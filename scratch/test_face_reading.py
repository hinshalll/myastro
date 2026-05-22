import os
import sys
import json

# Add workspace to path
sys.path.append(r"C:\Users\hinsh\Desktop\myastro")

from shared.astro.face_vision import analyze_face
from features.face_reading.vlm_reader import read_face
from features.face_reading.knowledge_lookup import get_face_context

def test_pipeline():
    print("=== STARTING VEDIC FACE READING INTEGRATION TEST ===")
    
    # Load Gemini API key from .streamlit/secrets.toml
    secrets_path = r"C:\Users\hinsh\Desktop\myastro\.streamlit\secrets.toml"
    api_key = None
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as sf:
            for line in sf:
                if "GEMINI_API_KEY" in line:
                    api_key = line.split("=")[1].strip().strip('"').strip("'")
                    break
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in secrets.toml.")
        return
        
    from shared.ai.gemini_client import init_gemini
    init_gemini(api_key)
    print("Gemini client successfully initialized!")
    
    # Scan all image files in the downloads folder to find one with a detectable face
    downloads = r"C:\Users\hinsh\Downloads"
    selected_image = None
    face_analysis = None
    
    print("Scanning Downloads folder for an image with a detectable face...")
    for f in os.listdir(downloads):
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
            p = os.path.join(downloads, f)
            try:
                with open(p, "rb") as img_f:
                    img_bytes = img_f.read()
                analysis = analyze_face(img_bytes)
                if analysis.get("face_found"):
                    selected_image = p
                    face_analysis = analysis
                    break
            except Exception:
                continue
                
    if not selected_image:
        print("ERROR: No face image found in downloads (or no face could be detected in any available image).")
        return
        
    print(f"Selected test image: {selected_image}")
    
    # 1. Run face vision analysis
    print("\nRunning face vision math analysis...")
    
    if not face_analysis.get("face_found"):
        print("FAIL: No face detected in the image.")
        return
        
    print("SUCCESS: Face detected!")
    print(f"Pose Metrics: {face_analysis.get('pose_metrics')}")
    print(f"Pose Issues: {face_analysis.get('pose_issues')}")
    print(f"Initial Landmark Metrics:")
    print(json.dumps(face_analysis.get("metrics"), indent=2))
    
    # Check if pose checks or quality checks blocked it
    pose_issues = face_analysis.get("pose_issues", [])
    if pose_issues:
        print(f"WARNING: Pose issues detected (pitch check may have triggered!): {pose_issues}")
    
    # 2. Build knowledge lookup
    print("\nBuilding Vedic/Patwari knowledge context...")
    # Mocking birth chart info for full cross-reference
    use_kundli = True
    mock_dossier = "Virgo Ascendant (Lagna), Ascendant Lord Mercury in the 1st House in Virgo. Moon in Rohini Nakshatra in the 9th House."
    
    context = get_face_context(face_analysis["metrics"], use_kundli=use_kundli, dossier=mock_dossier)
    print("Vedic knowledge formatted block built successfully!")
    print(context["formatted_block"][:600] + "...\n")
    
    # 3. Run VLM Face Reading (Pass 1 & Pass 2 combined)
    print("Running VLM reading call (with high-availability fallbacks & visual self-corrections)...")
    result = read_face(
        enhanced_face=face_analysis["enhanced_face"],
        region_crops=face_analysis.get("region_crops") or {},
        metrics=face_analysis.get("metrics") or {},
        quality_metrics=face_analysis.get("quality_metrics") or {},
        pose_metrics=face_analysis.get("pose_metrics") or {},
        knowledge_context=context["formatted_block"],
        dossier=mock_dossier,
        use_kundli=use_kundli
    )
    
    if result.get("error"):
        print(f"FAIL: VLM run failed with error: {result['error']}")
        return
        
    print("\nSUCCESS: VLM read complete!")
    print("\n--- PHASE A OBSERVATIONS (VLM) ---")
    print(json.dumps(result.get("phase_a"), indent=2))
    
    print("\n--- SELF-CORRECTED METRICS ---")
    print(json.dumps(result.get("metrics"), indent=2))
    
    print("\n--- PHASE B READING SNIPPET ---")
    print(result.get("phase_b", "")[:1200] + "...\n")
    
    print("=== INTEGRATION TEST COMPLETE WITH ZERO ERRORS ===")

if __name__ == "__main__":
    test_pipeline()
