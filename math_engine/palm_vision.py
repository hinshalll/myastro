import io
import cv2
import numpy as np
import PIL.Image
from skimage.filters import frangi
from skimage.color import rgb2gray
from skimage.morphology import skeletonize
from scipy.ndimage import convolve

import mediapipe as mp
mp_hands = mp.solutions.hands

hands_detector = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

# ─── FEATURE FLAGS ────────────────────────────────────────────────────────────
# Flip to True on localhost (8 GB RAM) or FastAPI server.
# Requires: pip install transformers torch
USE_DEPTH_MODEL = False

def _load_depth_model():
    try:
        import streamlit as st
        @st.cache_resource(show_spinner=False)
        def _inner():
            from transformers import pipeline as hf_pipeline
            return hf_pipeline("depth-estimation",
                                model="depth-anything/Depth-Anything-V2-Small-hf",
                                device=-1)
        return _inner()
    except Exception:
        return None

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
LINE_LABELS = {
    "heart_line": "Heart Line",
    "head_line":  "Head Line",
    "life_line":  "Life Line",
    "fate_line":  "Fate Line",
    "sun_line":   "Sun / Apollo Line",
}

HAND_TYPES = {
    "square_short": ("Earth Hand", "Prithvi Hasta — Practical, grounded, reliable"),
    "square_long":  ("Air Hand",   "Vayu Hasta — Intellectual, communicative, restless"),
    "oblong_short": ("Fire Hand",  "Agni Hasta — Passionate, impulsive, creative"),
    "oblong_long":  ("Water Hand", "Jal Hasta — Intuitive, emotional, empathetic"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — IMAGE PREPARATION
# ═══════════════════════════════════════════════════════════════════════════════

def enhance_and_resize(image_array, target_width=900):
    h, w = image_array.shape[:2]
    resized = cv2.resize(image_array, (target_width, int(target_width*(h/w))),
                         interpolation=cv2.INTER_AREA)
    kernel  = np.array([[0,-0.5,0],[-0.5,3,-0.5],[0,-0.5,0]])
    return cv2.filter2D(resized, -1, kernel)


def pad_to_square(crop_rgb, size=300, bg=(12, 8, 20)):
    """Pad any crop to a fixed square with dark background. Fixes UI alignment."""
    if crop_rgb is None or crop_rgb.size == 0:
        return np.full((size, size, 3), bg, dtype=np.uint8)
    h, w   = crop_rgb.shape[:2]
    scale  = min(size/max(h,1), size/max(w,1))
    nw, nh = int(w*scale), int(h*scale)
    res    = cv2.resize(crop_rgb, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.full((size, size, 3), bg, dtype=np.uint8)
    yo     = (size-nh)//2;  xo = (size-nw)//2
    canvas[yo:yo+nh, xo:xo+nw] = res
    return canvas


def get_safe_box(x, y, w, h, img_w, img_h, pad=0.35):
    pw = int(w*pad); ph = int(h*pad)
    return (max(0,x-pw), max(0,y-ph), min(img_w,x+w+pw), min(img_h,y+h+ph))


def remove_background(frame_rgb):
    """GrabCut background removal — skin-tone agnostic."""
    try:
        mask = np.zeros(frame_rgb.shape[:2], np.uint8)
        bgd  = np.zeros((1,65), np.float64)
        fgd  = np.zeros((1,65), np.float64)
        h, w = frame_rgb.shape[:2]
        mg   = max(5, int(min(h,w)*0.03))
        cv2.grabCut(cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR),
                    mask, (mg,mg,w-mg*2,h-mg*2), bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask==2)|(mask==0), 0, 1).astype("uint8")
        ctrs, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if ctrs:
            c = max(ctrs, key=cv2.contourArea)
            x,y,bw,bh = cv2.boundingRect(c)
            p=20; x=max(0,x-p); y=max(0,y-p)
            return frame_rgb[y:y+min(h-y,bh+p*2), x:x+min(w-x,bw+p*2)]
    except Exception:
        pass
    # Fallback
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    _,th = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    ctrs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if ctrs:
        c=max(ctrs,key=cv2.contourArea); x,y,bw,bh=cv2.boundingRect(c); p=20
        x=max(0,x-p); y=max(0,y-p)
        return frame_rgb[y:y+min(frame_rgb.shape[0]-y,bh+p*2),
                         x:x+min(frame_rgb.shape[1]-x,bw+p*2)]
    return frame_rgb


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ACCURACY-CRITICAL PREPROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def apply_clahe_lab(frame_rgb):
    """
    CLAHE in LAB colour space — THE critical accuracy fix.
    Enhances local contrast so palm lines pop before Frangi sees the image.
    Works on all skin tones (operates on Lightness channel only).
    Returns: enhanced_rgb, enhanced_gray (normalised 0-255, ready for Frangi).
    """
    lab = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l_enh = clahe.apply(l)
    enh_rgb  = cv2.cvtColor(cv2.merge([l_enh,a,b]), cv2.COLOR_LAB2RGB)
    enh_gray = cv2.normalize(cv2.cvtColor(enh_rgb, cv2.COLOR_RGB2GRAY),
                             None, 0, 255, cv2.NORM_MINMAX)
    return enh_rgb, enh_gray


def enhance_crop_for_ai(crop_rgb):
    """
    Stronger CLAHE for crops sent to Gemini Vision.
    Gemini needs to SEE the lines — not flat skin tones.
    """
    if crop_rgb is None or crop_rgb.size == 0:
        return crop_rgb
    lab = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2LAB)
    l,a,b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4,4))
    return cv2.cvtColor(cv2.merge([clahe.apply(l),a,b]), cv2.COLOR_LAB2RGB)


def get_skin_mask(frame_rgb):
    """
    HSV skin detection covering all ethnicities.
    Applied to Frangi output to zero background noise.
    This is why we got 152 fake endpoints before — background
    noise was flooding topology with false line terminations.
    """
    hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)
    m1  = cv2.inRange(hsv, np.array([0,15,50],np.uint8),
                          np.array([25,255,255],np.uint8))
    m2  = cv2.inRange(hsv, np.array([160,15,50],np.uint8),
                          np.array([180,255,255],np.uint8))
    mask = cv2.bitwise_or(m1, m2)
    kn   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15))
    return cv2.dilate(mask, kn, iterations=3)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — ORIENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_palm_orientation(frame_rgb, lm):
    w_pt = np.array(lm[0], float); m_pt = np.array(lm[9], float)
    d    = m_pt - w_pt
    angle= np.degrees(np.arctan2(d[0], -d[1]))
    h,w  = frame_rgb.shape[:2]; c=(w//2,h//2)
    M    = cv2.getRotationMatrix2D(c, angle, 1.0)
    return cv2.warpAffine(frame_rgb, M, (w,h),
                          flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE), M


def rotate_landmarks(lm, M, iw, ih):
    out = {}
    for idx,(x,y) in lm.items():
        r = cv2.transform(np.array([[[float(x),float(y)]]],np.float32), M)
        out[idx] = (int(np.clip(r[0][0][0],0,iw-1)),
                    int(np.clip(r[0][0][1],0,ih-1)))
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — FRANGI + PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════

def run_dual_frangi(enhanced_gray):
    """
    Run Frangi for BOTH dark ridges AND bright ridges, take pixel-wise max.
    Dark ridges  = normal palm lines on lighter skin (the common case).
    Bright ridges= handles overexposed images or reverse-contrast scenarios.
    This alone prevents the 'all lines faint' result from a single-direction pass.
    Also applies a mild Gaussian denoise before Frangi so sensor noise isn't amplified.
    """
    blurred   = cv2.GaussianBlur(enhanced_gray, (3,3), 0)
    g_norm    = blurred.astype(np.float64) / 255.0
    r_dark    = frangi(g_norm, sigmas=range(1,9), black_ridges=True)
    r_bright  = frangi(g_norm, sigmas=range(1,9), black_ridges=False)
    combined  = np.maximum(r_dark, r_bright)
    return cv2.normalize(combined, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)


def build_persistence_map(frangi_norm):
    """
    8-threshold voting. Genuine lines survive many thresholds; noise survives few.
    Seed threshold lowered to 4 (was 6) to handle moderate-signal images post-CLAHE.
    """
    thresholds  = [15,25,35,45,55,65,75,85]
    persistence = np.zeros_like(frangi_norm, dtype=np.uint8)
    for t in thresholds:
        persistence += (frangi_norm > t).astype(np.uint8)
    total = np.sum(persistence >= 1)
    strong= np.sum(persistence >= 4)
    return persistence, float(strong/max(total,1))


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — LINE ISOLATION & TOPOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

def isolate_lines_watershed(frangi_norm, persistence, skin_mask=None):
    """
    Watershed-lite: seeds (persistence ≥ 4) flood through terrain (frangi > 15).
    Skin mask zeroes out background noise before seeding.
    Small blobs (< 1% image height) pruned as noise.
    """
    fn = cv2.bitwise_and(frangi_norm, frangi_norm, mask=skin_mask) \
         if skin_mask is not None else frangi_norm
    ps = cv2.bitwise_and(persistence, persistence, mask=skin_mask) \
         if skin_mask is not None else persistence

    seeds   = (ps >= 4).astype(np.uint8)
    terrain = (fn > 15).astype(np.uint8)

    if seeds.sum() == 0:
        return (fn > 35).astype(np.uint8) * 255

    kn    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    grown = seeds.copy()
    for _ in range(12):
        grown = cv2.bitwise_and(cv2.dilate(grown,kn,iterations=1), terrain)

    min_area = max(40, int(frangi_norm.shape[0]*0.01))
    n,labels,stats,_ = cv2.connectedComponentsWithStats(grown)
    clean = np.zeros_like(grown, dtype=np.uint8)
    for lid in range(1,n):
        if stats[lid, cv2.CC_STAT_AREA] >= min_area:
            clean[labels==lid] = 255
    return clean


def extract_topology(clean_mask, img_h, img_w):
    binary = (clean_mask>0).astype(np.uint8)
    kn = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    binary = cv2.morphologyEx(cv2.morphologyEx(binary, cv2.MORPH_OPEN, kn),
                               cv2.MORPH_CLOSE, kn)
    skel = skeletonize(binary.astype(bool)).astype(np.uint8)
    nbrs = convolve(skel.astype(int), np.ones((3,3),int)) - skel.astype(int)

    endpoints    = int(np.sum((skel==1)&(nbrs==1)))
    branchpoints = int(np.sum((skel==1)&(nbrs>=3)))

    simian = False
    for row in skel[int(img_h*0.20):int(img_h*0.55)]:
        run=mx=0
        for px in row:
            if px: run+=1; mx=max(mx,run)
            else: run=0
        if mx > img_w*0.50: simian=True; break

    return {
        "line_endpoints":  endpoints,
        "line_forks":      branchpoints,
        "simian_line":     simian,
        "line_complexity": int(branchpoints/max(endpoints,1)*100),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — ZONE SCORES (coverage-weighted)
# ═══════════════════════════════════════════════════════════════════════════════

def extract_zone_scores(frangi_norm, lm, img_h, img_w):
    """
    Coverage-weighted scoring formula:
      score = (fraction_of_zone_covered × 0.6 + mean_intensity × 0.4) × 100

    OLD formula (mean/255×100) produced 14 even when lines existed
    because 35/255×100 = 13.7.

    NEW formula: a line covering 50% of zone at moderate intensity → scores ~40.
    Adaptive threshold (40th percentile, min 12) instead of fixed 30.
    """
    def sc(zone):
        if zone.size == 0: return 0
        thr = max(12, int(np.percentile(zone, 40)))
        px  = zone[zone > thr]
        if len(px) == 0: return 0
        cov = len(px)/zone.size
        itn = float(np.mean(px))/255.0
        return min(100, int((cov*0.6 + itn*0.4)*100))

    wy=lm[0][1]; my=lm[5][1]; lx=min(lm[17][0],lm[5][0]); rx=max(lm[17][0],lm[5][0])
    ph=max(wy-my,1); tx=lm[2][0]; fx=lm[9][0]; sx=lm[13][0]; iw=img_w

    hy1=my;      hy2=my+int(ph*0.22)
    hd1=hy2;     hd2=hd1+int(ph*0.22)
    lx1=max(0,tx-int(iw*0.13)); lx2=min(iw,tx+int(iw*0.10))
    fx1=max(0,fx-int(iw*0.07)); fx2=min(iw,fx+int(iw*0.07))
    sx1=max(0,sx-int(iw*0.06)); sx2=min(iw,sx+int(iw*0.06))

    return {
        "heart_line": sc(frangi_norm[hy1:hy2, lx:rx]),
        "head_line":  sc(frangi_norm[hd1:hd2, lx:rx]),
        "life_line":  sc(frangi_norm[hd2:wy,  lx1:lx2]),
        "fate_line":  sc(frangi_norm[hd2:wy,  fx1:fx2]),
        "sun_line":   sc(frangi_norm[hd2:wy,  sx1:sx2]),
    }


def _fallback_zone_scores(frangi_norm, img_h, img_w):
    def sc(zone):
        if zone.size==0: return 0
        thr=max(12,int(np.percentile(zone,40))); px=zone[zone>thr]
        if len(px)==0: return 0
        return min(100,int((len(px)/zone.size*0.6+float(np.mean(px))/255*0.4)*100))
    t=img_h//3
    return {
        "heart_line": sc(frangi_norm[0:int(t*.7),  img_w//4:img_w*3//4]),
        "head_line":  sc(frangi_norm[int(t*.7):t,  img_w//4:img_w*3//4]),
        "life_line":  sc(frangi_norm[t:t*2,         0:img_w//3]),
        "fate_line":  sc(frangi_norm[t:t*2, img_w//3:img_w*2//3]),
        "sun_line":   sc(frangi_norm[t:t*2, img_w*2//3:img_w]),
    }


def score_to_label(s):
    if s>=65: return "Deep & Prominent"
    if s>=45: return "Clear & Defined"
    if s>=25: return "Moderate"
    if s>=10: return "Faint"
    return "Absent / Not Detected"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — GEOMETRY & VITALITY
# ═══════════════════════════════════════════════════════════════════════════════

def compute_finger_ratios(lm):
    def fl(t,p): return float(np.linalg.norm(np.array(lm[t])-np.array(lm[p])))
    il=fl(8,5); rl=fl(16,13); ml=fl(12,9); pl=fl(20,17)
    r244=il/max(rl,1)
    pw=abs(lm[17][0]-lm[5][0]); ph=fl(9,0)
    pr=float(pw/max(ph,1)); fr=float(ml/max(ph,1))
    shape="square" if pr>=0.85 else "oblong"
    length="short" if fr<0.75 else "long"
    western,vedic=HAND_TYPES.get(f"{shape}_{length}",
                                  ("Mixed Hand","Mishra Hasta — Complex, adaptable"))
    rr=("Longer ring finger — strong Mars/Sun energy" if r244<0.95 else
        "Longer index finger — strong Jupiter energy"  if r244>1.05 else
        "Balanced index-ring ratio — harmonised energies")
    dom=max({"Index":il,"Ring":rl,"Middle":ml,"Pinky":pl},
            key=lambda k:{"Index":il,"Ring":rl,"Middle":ml,"Pinky":pl}[k])
    return {"ratio_2d4d":round(r244,3),"ratio_reading":rr,
            "hand_type":western,"hand_type_vedic":vedic,
            "dominant_finger":dom,"palm_ratio":round(pr,3)}


def get_vitality_hsv(frame_rgb, lm, iw, ih):
    vx,vy=lm[2]; box=max(40,int(iw*.07))
    crop=frame_rgb[max(0,vy):min(ih,vy+box*2), max(0,vx-box):min(iw,vx+box)]
    if crop.size==0: return "Balanced Kapha (Steady vitality)","Balanced & Steady Energy"
    hsv=cv2.cvtColor(crop,cv2.COLOR_RGB2HSV)
    s=float(cv2.mean(hsv)[1]); v=float(cv2.mean(hsv)[2])
    if s>95 and v>100: return "Active Pitta (High vitality — strong Venus mount)","Warm, Passionate & High Energy"
    if s<45 or v<80:  return "Cool Vata (Variable vitality)","Cool, Sensitive & Variable Energy"
    return "Balanced Kapha (Steady vitality)","Balanced & Steady Energy"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — MOUNT ELEVATION
# ═══════════════════════════════════════════════════════════════════════════════

def _normalize_elevations(raw):
    """Relative normalization — prevents all mounts showing 'Highly Developed'."""
    if not raw: return {}
    mn=min(raw.values()); mx=max(raw.values()); sp=max(mx-mn,1e-6)
    out={}
    for m,s in raw.items():
        r=int((s-mn)/sp*100)
        lb=("Highly Developed" if r>=70 else "Moderately Developed" if r>=45
            else "Slightly Developed" if r>=25 else "Flat / Underdeveloped")
        out[m]={"elevation":lb,"score":r}
    return out


def estimate_mount_elevations_relative(orig_crops_raw):
    """Brightness+sharpness heuristic with relative normalization (Streamlit Cloud)."""
    raw={}
    for m,c in orig_crops_raw.items():
        if c is None or c.size==0: continue
        hsv=cv2.cvtColor(c,cv2.COLOR_RGB2HSV)
        v=float(cv2.mean(hsv)[2])
        g=cv2.cvtColor(c,cv2.COLOR_RGB2GRAY)
        lap=float(cv2.Laplacian(g,cv2.CV_64F).var())
        raw[m]=min(100,v/2.55)*0.5 + min(100,float(np.log1p(lap))*12)*0.5
    return _normalize_elevations(raw)


def get_mount_elevations_depth(frame_rgb, lm):
    if not USE_DEPTH_MODEL or not lm: return None
    estimator=_load_depth_model()
    if not estimator: return None
    try:
        dep=np.array(estimator(PIL.Image.fromarray(frame_rgb))["depth"],np.float32)
        mn,mx=dep.min(),dep.max()
        if mx-mn<1e-6: return None
        dep=(dep-mn)/(mx-mn)*100
        ih,iw=frame_rgb.shape[:2]
        box=int(np.sqrt((lm[5][0]-lm[9][0])**2+(lm[5][1]-lm[9][1])**2))*2
        anch={"Jupiter":lm[5],"Saturn":lm[9],"Sun":lm[13],"Mercury":lm[17],
              "Venus":lm[2],
              "Mars_Upper":(lm[17][0],int((lm[17][1]+lm[0][1])/2)),
              "Luna":(lm[17][0],int(lm[17][1]*.4+lm[0][1]*.6))}
        raw={}
        for m,(ax,ay) in anch.items():
            bs=int(box*1.4) if m in ("Venus","Mars_Upper","Luna") else box
            r=dep[max(0,ay-bs//2):min(ih,ay+bs//2),
                  max(0,ax-bs//2):min(iw,ax+bs//2)]
            if r.size>0: raw[m]=float(np.mean(r))
        return _normalize_elevations(raw)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_palm_hybrid(image_bytes):
    img        = PIL.Image.open(io.BytesIO(image_bytes)).convert("RGB")
    best_frame = enhance_and_resize(np.array(img))
    best_frame = remove_background(best_frame)
    ih, iw     = best_frame.shape[:2]
    data       = {"landmarks_found": False}

    # MediaPipe
    results = hands_detector.process(best_frame)
    lm_dict = None
    if results.multi_hand_landmarks:
        lm_raw  = results.multi_hand_landmarks[0]
        lm_dict = {i:(int(p.x*iw),int(p.y*ih)) for i,p in enumerate(lm_raw.landmark)}
        data["landmarks_found"] = True
        best_frame, M = normalize_palm_orientation(best_frame, lm_dict)
        ih, iw = best_frame.shape[:2]
        lm_dict = rotate_landmarks(lm_dict, M, iw, ih)
        vitality_hsv, ui_vitality = get_vitality_hsv(best_frame, lm_dict, iw, ih)
        finger_data = compute_finger_ratios(lm_dict)
    else:
        vitality_hsv = "Unknown (no landmarks detected)"
        ui_vitality  = "Upload a clearer image for vitality reading"
        finger_data  = {}

    # CLAHE — THE accuracy fix
    enhanced_rgb, enhanced_gray = apply_clahe_lab(best_frame)

    # Skin mask — kills fake endpoints
    skin_mask = get_skin_mask(best_frame)

    # Dual-ridge Frangi + mask
    frangi_norm = run_dual_frangi(enhanced_gray)
    frangi_norm = cv2.bitwise_and(frangi_norm, frangi_norm, mask=skin_mask)

    # Persistence
    persistence, persistence_ratio = build_persistence_map(frangi_norm)

    # Watershed-lite
    clean_mask = isolate_lines_watershed(frangi_norm, persistence, skin_mask)

    # Topology on clean mask
    topology = extract_topology(clean_mask, ih, iw)

    # Zone scores
    zone_scores = (extract_zone_scores(frangi_norm, lm_dict, ih, iw)
                   if lm_dict else _fallback_zone_scores(frangi_norm, ih, iw))

    # Global score
    px = frangi_norm[frangi_norm>35]
    gs = int((np.mean(px)/255)*100) if len(px)>0 else 0
    ui_line = ("Deep & Prominent" if gs>35 else
               "Clear & Defined"  if gs>20 else "Delicate & Fine")

    # Depth elevation
    depth_elev = get_mount_elevations_depth(best_frame, lm_dict)

    data.update({
        "vitality_hsv":      vitality_hsv,
        "ui_vitality":       ui_vitality,
        "line_clarity_score": gs,
        "ui_line":           ui_line,
        "zone_scores":       zone_scores,
        "topology":          topology,
        "persistence_ratio": persistence_ratio,
        "finger_data":       finger_data,
        "depth_elevations":  depth_elev,
        "used_depth_model":  depth_elev is not None,
        "enhanced_rgb":      enhanced_rgb,
    })

    # Diagnostic xray (display only)
    hm  = cv2.applyColorMap(frangi_norm, cv2.COLORMAP_BONE)
    pv  = cv2.normalize(persistence, None, 0,255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    pc  = cv2.applyColorMap(pv, cv2.COLORMAP_JET)
    xr  = cv2.addWeighted(hm, 0.55, pc, 0.45, 0)
    cy  = np.zeros_like(xr); cy[clean_mask>0]=(255,200,0)
    xray = cv2.addWeighted(xr, 0.80, cy, 0.20, 0)
    if lm_dict: _draw_lm(xray, lm_dict)

    return data, xray, best_frame, lm_dict


def _draw_lm(bgr, lm):
    conns = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),
             (10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),
             (18,19),(19,20),(0,17),(5,9),(9,13),(13,17)]
    for a,b in conns:
        if a in lm and b in lm:
            cv2.line(bgr, lm[a], lm[b], (80,180,80), 1, cv2.LINE_AA)
    for (x,y) in lm.values():
        cv2.circle(bgr, (x,y), 2, (120,220,120), -1)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — MOUNT SLICER
# ═══════════════════════════════════════════════════════════════════════════════

def slice_xray_mounts(best_frame_rgb, diagnostic_xray, lm_dict, enhanced_rgb=None):
    """
    Returns three dicts (all crops square-padded for alignment):
      xray_crops     — heatmap crops (UI display)
      orig_crops     — CLAHE-enhanced crops padded to square (UI 'what AI sees')
      orig_crops_raw — unpadded CLAHE-enhanced crops (for Gemini Vision API)
    """
    ih, iw = best_frame_rgb.shape[:2]
    src    = enhanced_rgb if enhanced_rgb is not None else best_frame_rgb
    xc={};  oc={};  ocr={}

    if not lm_dict:
        th=ih//3; tw=iw//3
        for nm,(y1,y2,x1,x2) in {"Jupiter":(0,th,0,tw),
                                   "Venus":(th*2,ih,0,tw),
                                   "Luna":(th*2,ih,tw*2,iw)}.items():
            _xc=diagnostic_xray[y1:y2,x1:x2]
            _oc=src[y1:y2,x1:x2]
            xr=cv2.cvtColor(_xc,cv2.COLOR_BGR2RGB) if _xc.ndim==3 else _xc
            xc[nm]=pad_to_square(xr); oc[nm]=pad_to_square(_oc); ocr[nm]=_oc
        return xc, oc, ocr

    box =int(np.sqrt((lm_dict[5][0]-lm_dict[9][0])**2+
                     (lm_dict[5][1]-lm_dict[9][1])**2))*2
    vbox=int(box*1.4)
    defs={"Jupiter":(lm_dict[5],box),"Saturn":(lm_dict[9],box),
          "Sun":(lm_dict[13],box),"Mercury":(lm_dict[17],box),
          "Venus":(lm_dict[2],vbox),
          "Mars_Upper":((lm_dict[17][0],int((lm_dict[17][1]+lm_dict[0][1])/2)),vbox),
          "Luna":((lm_dict[17][0],int(lm_dict[17][1]*.4+lm_dict[0][1]*.6)),vbox)}

    for nm,((ax,ay),bs) in defs.items():
        if nm in ("Jupiter","Saturn","Sun","Mercury"): ay-=int(bs*.1)
        x1,y1,x2,y2=get_safe_box(ax-bs//2,ay-bs//2,bs,bs,iw,ih,0.30)
        _xc=diagnostic_xray[y1:y2,x1:x2]; _oc=src[y1:y2,x1:x2]
        if _xc.size==0: continue
        xr=cv2.cvtColor(_xc,cv2.COLOR_BGR2RGB)
        lbl=xr.copy(); cv2.putText(lbl,nm,(5,18),cv2.FONT_HERSHEY_SIMPLEX,
                                   .45,(255,255,255),1,cv2.LINE_AA)
        xc[nm]=pad_to_square(lbl); oc[nm]=pad_to_square(_oc); ocr[nm]=_oc

    return xc, oc, ocr
