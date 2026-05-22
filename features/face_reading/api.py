"""features.face_reading.api — FastAPI router.

Single endpoint, single AI call. Works WITHOUT a chart (read any face); pass
use_kundli=true + profile to add the birth-chart cross-reference.

Wire up in fastapi_main.py:
    ("face_reading", "features.face_reading.api")
"""

import base64

from features.face_reading.schemas import FaceReadingRequest, FaceReadingResponse

try:
    from fastapi import APIRouter, HTTPException
    router = APIRouter()
except ImportError:
    router = None


if router is not None:

    @router.post("/read", response_model=FaceReadingResponse)
    def read(req: FaceReadingRequest) -> FaceReadingResponse:
        from features.face_reading.service import analyze_face, read_face, get_face_context

        try:
            img_bytes = base64.b64decode(req.image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"image_base64 invalid: {e}")

        face = analyze_face(img_bytes)
        if not face.get("face_found"):
            return FaceReadingResponse(
                phase_a={}, phase_b="", metrics={},
                error="No face detected — use a clear, front-facing photo.",
            )

        dossier = ""
        use_kundli = bool(req.use_kundli and req.profile)
        if use_kundli:
            try:
                from shared.astro.dossier_builder import generate_astrology_dossier
                dossier = generate_astrology_dossier(req.profile) or ""
            except Exception:
                dossier = ""

        knowledge_ctx = ""
        if get_face_context:
            try:
                knowledge_ctx = get_face_context(
                    face["metrics"], use_kundli=use_kundli, dossier=dossier
                ).get("formatted_block", "")
            except Exception:
                knowledge_ctx = ""

        result = read_face(
            enhanced_face=face["enhanced_face"],
            region_crops=face.get("region_crops") or {},
            metrics=face.get("metrics") or {},
            quality_metrics=face.get("quality_metrics") or {},
            pose_metrics=face.get("pose_metrics") or {},
            knowledge_context=knowledge_ctx,
            dossier=dossier,
            use_kundli=use_kundli,
        )
        return FaceReadingResponse(
            phase_a=result.get("phase_a") or {},
            phase_b=result.get("phase_b") or "",
            metrics=face.get("metrics") or {},
            error=result.get("error") or "",
        )
