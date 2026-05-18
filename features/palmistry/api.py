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
        from features.palmistry.service import (
            analyze_palm, read_palm, get_palm_context, query_palmistry,
        )
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

        dossier = generate_astrology_dossier(req.profile)
        knowledge_ctx = ""
        if get_palm_context:
            try:
                kctx = get_palm_context(palm, palm.get("mount_elevations") or {}, dossier=dossier)
                knowledge_ctx = kctx.get("formatted_block", "")
            except Exception:
                pass
        qctx = ""
        if query_palmistry:
            try:
                qctx = query_palmistry(palm, palm.get("mount_elevations") or {}, k=6)
            except Exception:
                pass

        result = read_palm(
            enhanced_palm=palm["enhanced_palm"],
            mount_crops=palm.get("mount_crops") or {},
            hand_metrics=palm.get("hand_metrics") or {},
            vitality=palm.get("vitality") or {},
            quality_metrics=palm.get("quality_metrics") or {},
            dossier=dossier,
            knowledge_context=knowledge_ctx,
            qdrant_context=qctx,
        )
        return PalmReadingResponse(
            phase_a=result.get("phase_a") or {},
            phase_b=result.get("phase_b") or "",
            error=result.get("error") or "",
        )
