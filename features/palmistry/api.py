"""features.palmistry.api — FastAPI router."""

import base64

from features.palmistry.schemas import PalmReadingRequest, PalmReadingResponse

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:
    router = None


if router is not None:

    @router.post("/read", response_model=PalmReadingResponse)
    def read(req: PalmReadingRequest) -> PalmReadingResponse:
        from features.palmistry.service import analyze_palm, read_palm
        from shared.astro.dossier_builder import generate_astrology_dossier

        try:
            img_bytes = base64.b64decode(req.image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"image_base64 invalid: {e}")

        palm = analyze_palm(img_bytes)
        if not palm.get("enhanced_palm") is not None:
            return PalmReadingResponse(
                phase_a={}, phase_b="", error="palm-vision pipeline failed",
            )
        if not palm.get("landmarks_found"):
            return PalmReadingResponse(
                phase_a={},
                phase_b="",
                error="No palm landmarks found. Use a clear photo of the full open palm.",
            )

        dossier = generate_astrology_dossier(req.profile) if req.profile else ""

        result = read_palm(
            enhanced_palm=palm["enhanced_palm"],
            mount_crops=palm.get("mount_crops") or {},
            hand_metrics=palm.get("hand_metrics") or {},
            vitality=palm.get("vitality") or {},
            quality_metrics=palm.get("quality_metrics") or {},
            dossier=dossier,
        )
        return PalmReadingResponse(
            phase_a=result.get("phase_a") or {},
            phase_b=result.get("phase_b") or "",
            error=result.get("error") or "",
        )
