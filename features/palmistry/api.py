"""features.palmistry.api - FastAPI router."""

import base64
import io

import PIL.Image
import PIL.ImageOps

from features.palmistry.schemas import (
    PalmReadingRequest,
    PalmReadingResponse,
    PalmScanRequest,
    PalmScanResponse,
)

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:
    router = None


if router is not None:

    def _decode_image_base64(image_base64: str, label: str) -> bytes:
        try:
            return base64.b64decode(image_base64, validate=True)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"{label} image_base64 invalid: {e}")

    def _supplemental_image(image_bytes: bytes, label: str):
        try:
            image = PIL.Image.open(io.BytesIO(image_bytes))
            return PIL.ImageOps.exif_transpose(image).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"{label} is not a readable image: {e}")

    def _capture_inputs(req) -> tuple[bytes, list[dict]]:
        """Return dominant full-palm bytes plus AI-owned role-labelled extra views."""
        captures = list(req.captures or [])
        primary_capture = next((c for c in captures if c.role == "dominant_full"), None)

        if primary_capture is not None:
            primary_bytes = _decode_image_base64(primary_capture.image_base64, "dominant_full")
        elif req.image_base64:
            primary_bytes = _decode_image_base64(req.image_base64, "dominant_full")
        else:
            raise HTTPException(
                status_code=400,
                detail="A dominant_full capture or legacy image_base64 palm photo is required.",
            )

        supplemental = []
        for capture in captures:
            if capture is primary_capture or capture.role == "dominant_full":
                continue
            capture_bytes = _decode_image_base64(capture.image_base64, capture.role)
            supplemental.append({
                "role": capture.role,
                "image": _supplemental_image(capture_bytes, capture.role),
            })
        return primary_bytes, supplemental

    def _vision_error_response(palm: dict) -> tuple[dict, dict, str]:
        if not palm.get("enhanced_palm") is not None:
            return {}, {}, "palm-vision pipeline failed"
        if not palm.get("landmarks_found"):
            guidance = {
                "general_reading_ready": False,
                "required_for_general": ["dominant_full"],
                "optional_for_detail": [],
            }
            return {}, guidance, "No palm landmarks found. Use a clear photo of the full open palm."
        return {}, {}, ""

    @router.post("/scan", response_model=PalmScanResponse)
    def scan(req: PalmScanRequest) -> PalmScanResponse:
        from features.palmistry.service import analyze_palm, scan_palm

        primary_bytes, supplemental = _capture_inputs(req)
        palm = analyze_palm(primary_bytes)
        _, capture_guidance, vision_error = _vision_error_response(palm)
        if vision_error:
            return PalmScanResponse(
                phase_a={},
                capture_guidance=capture_guidance,
                hand_metrics={},
                palm_tone={},
                error=vision_error,
            )

        result = scan_palm(
            enhanced_palm=palm["enhanced_palm"],
            mount_crops=palm.get("mount_crops") or {},
            hand_metrics=palm.get("hand_metrics") or {},
            vitality=palm.get("vitality") or {},
            quality_metrics=palm.get("quality_metrics") or {},
            supplemental_captures=supplemental,
        )
        return PalmScanResponse(
            phase_a=result.get("phase_a") or {},
            capture_guidance=result.get("capture_guidance") or {},
            hand_metrics=result.get("hand_metrics") or {},
            palm_tone=result.get("vitality") or {},
            error=result.get("error") or "",
        )

    @router.post("/read", response_model=PalmReadingResponse)
    def read(req: PalmReadingRequest) -> PalmReadingResponse:
        from features.palmistry.service import analyze_palm, read_palm
        from shared.astro.dossier_builder import generate_astrology_dossier

        primary_bytes, supplemental = _capture_inputs(req)
        palm = analyze_palm(primary_bytes)
        _, capture_guidance, vision_error = _vision_error_response(palm)
        if vision_error:
            return PalmReadingResponse(
                phase_a={},
                phase_b="",
                capture_guidance=capture_guidance,
                error=vision_error,
            )

        dossier = generate_astrology_dossier(req.profile) if req.profile else ""
        result = read_palm(
            enhanced_palm=palm["enhanced_palm"],
            mount_crops=palm.get("mount_crops") or {},
            hand_metrics=palm.get("hand_metrics") or {},
            vitality=palm.get("vitality") or {},
            quality_metrics=palm.get("quality_metrics") or {},
            dossier=dossier,
            supplemental_captures=supplemental,
        )
        return PalmReadingResponse(
            phase_a=result.get("phase_a") or {},
            phase_b=result.get("phase_b") or "",
            capture_guidance=result.get("capture_guidance") or {},
            error=result.get("error") or "",
        )
