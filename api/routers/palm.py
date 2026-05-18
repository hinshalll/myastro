"""
api/routers/palm.py — /api/v1/palm/*
======================================
Palm reading. Client uploads a palm photo + the user's birth profile;
backend runs math_engine.palm_vision (MediaPipe + quality gate +
landmark detection) then ai_engine.palm_vision_ai (Gemini Vision).

Mobile clients should upload the photo as multipart/form-data.
"""

import json
from fastapi import APIRouter, HTTPException, File, UploadFile, Form

from math_engine.dossier_builder import generate_astrology_dossier
from api.schemas import PalmReadingResponse, BirthProfile

router = APIRouter(prefix="/palm", tags=["palm"])


@router.post("/analyze", response_model=PalmReadingResponse)
async def palm_analyze(
    image: UploadFile  = File(..., description="JPEG/PNG of the dominant palm"),
    profile_json: str  = Form(..., description="JSON-encoded BirthProfile"),
):
    """Analyze a palm photo and return a kundli-aware reading.

    The endpoint accepts the profile as a JSON-encoded form field rather
    than a body — that lets mobile apps send the image + profile in one
    multipart request.
    """
    try:
        profile = BirthProfile(**json.loads(profile_json))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad profile_json: {e}")

    try:
        image_bytes = await image.read()
        from math_engine.palm_vision import analyze_palm
        from ai_engine.palm_vision_ai import generate_palm_reading
        from ai_engine.palm_knowledge_lookup import build_palm_knowledge_block

        analysis = analyze_palm(image_bytes)
        if not analysis["landmarks_found"]:
            raise HTTPException(
                status_code=400,
                detail="Could not detect a hand. Re-upload a clearer photo "
                       "with the full open palm visible.",
            )

        # Build chart dossier for kundli-aware reading
        dossier = generate_astrology_dossier(profile.dict())

        # RAG knowledge block
        knowledge_block = build_palm_knowledge_block(analysis)

        result = generate_palm_reading(
            enhanced_palm     = analysis["enhanced_palm"],
            mount_crops       = analysis["mount_crops"],
            hand_metrics      = analysis["hand_metrics"],
            vitality          = analysis["vitality"],
            quality_metrics   = analysis["quality_metrics"],
            dossier           = dossier,
            knowledge_context = knowledge_block,
        )
        return PalmReadingResponse(
            quality_metrics  = analysis["quality_metrics"],
            hand_metrics     = analysis["hand_metrics"],
            vitality         = analysis["vitality"],
            phase_a          = result.get("phase_a", {}),
            phase_b_markdown = result.get("phase_b", ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Palm reading failed: {e}")
