"""Cheap palmistry accuracy guardrails; no Gemini or Qdrant calls."""

import base64
import io
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from features.palmistry.api import read as read_api, scan as scan_api
from features.palmistry.schemas import PalmCapture, PalmReadingRequest, PalmScanRequest
from features.palmistry import vlm_reader
from features.palmistry.prompts import build_phase_a_prompt


class _FakeResponse:
    def __init__(self, text):
        self.text = text


class _InvalidPhaseAModel:
    def __init__(self):
        self.calls = 0

    def generate_content(self, _contents):
        self.calls += 1
        return _FakeResponse("phase a did not return json")


class _ValidPhaseAModel:
    def __init__(self):
        self.calls = 0
        self.last_contents = None

    def generate_content(self, contents):
        self.calls += 1
        self.last_contents = contents
        return _FakeResponse("""{
          "image_quality": "acceptable",
          "image_issues": "",
          "lines": {
            "heart": {"visibility": "clear", "path": "curved", "endpoint": "Jupiter"},
            "head": {"visibility": "clear", "path": "slight slope", "joined_to_life": "yes", "slope": "gentle_downward"},
            "life": {"visibility": "clear", "path": "wide arc", "curve": "wide"},
            "fate": {"visibility": "faint", "path": "central", "starts_at": "center"},
            "sun": {"visibility": "faint", "path": "under ring finger"},
            "marriage_lines": {"count_visible": "1", "description": "one clear line"},
            "simian": {"present": false, "confidence": "high"}
          },
          "mounts": {
            "Jupiter": {"fullness": "moderate", "marks": "no notable marks"},
            "Saturn": {"fullness": "moderate", "marks": "no notable marks"},
            "Sun": {"fullness": "moderate", "marks": "no notable marks"},
            "Mercury": {"fullness": "moderate", "marks": "no notable marks"},
            "Venus": {"fullness": "prominent", "marks": "no notable marks"},
            "Mars": {"fullness": "moderate", "marks": "no notable marks"},
            "Luna": {"fullness": "moderate", "marks": "no notable marks"}
          },
          "special_marks": {
            "mystic_cross": "not_visible",
            "ring_of_solomon": "not_visible",
            "ring_of_saturn": "not_visible"
          },
          "fingers": {
            "tip_shape_dominant": "rounded",
            "knotted_joints": "no",
            "spacing": "moderate",
            "index_vs_ring_length": "ring_longer"
          },
          "thumb": {
            "set": "medium",
            "tip_shape": "conic",
            "flexibility_estimate": "flexible"
          },
          "vitality_visual_class": "Balanced",
          "capture_guidance": {
            "general_reading_ready": true,
            "required_for_general": [],
            "optional_for_detail": []
          }
        }""")


class _PhaseBModel:
    def __init__(self):
        self.calls = 0
        self.last_contents = None

    def generate_content(self, contents):
        self.calls += 1
        self.last_contents = contents
        return _FakeResponse("## First Glance\nA grounded reading.")


def _smoke_phase_a_prompt_limits():
    prompt = build_phase_a_prompt({}, {}, {}, n_mount_crops=0)
    assert "kundli_palm_agreement" not in prompt
    assert "Marriage/relationship lines sit on the side edge" in prompt
    assert "neutral open-palm photo does not prove thumb flexibility" in prompt
    assert '"capture_guidance"' in prompt
    assert "Do not wrap it in markdown fences" in prompt


def _smoke_invalid_scan_stops_before_phase_b():
    fake_model = _InvalidPhaseAModel()
    old_get_json_model = vlm_reader.get_ai_model_for_json
    old_get_model = vlm_reader.get_ai_model_by_name
    old_mount_ref = vlm_reader._fetch_mounts_ref
    old_line_ref = vlm_reader._fetch_lines_ref

    try:
        vlm_reader.get_ai_model_for_json = lambda *_args, **_kwargs: fake_model
        vlm_reader.get_ai_model_by_name = lambda _name: fake_model
        vlm_reader._fetch_mounts_ref = lambda: None
        vlm_reader._fetch_lines_ref = lambda: None

        result = vlm_reader.read_palm(
            enhanced_palm=np.zeros((96, 96, 3), dtype=np.uint8),
            mount_crops={},
            hand_metrics={},
            vitality={},
            quality_metrics={"is_usable": True},
        )
    finally:
        vlm_reader.get_ai_model_for_json = old_get_json_model
        vlm_reader.get_ai_model_by_name = old_get_model
        vlm_reader._fetch_mounts_ref = old_mount_ref
        vlm_reader._fetch_lines_ref = old_line_ref

    assert fake_model.calls == 1
    assert result["phase_b"] == ""
    assert "usable observations" in result["error"]


def _smoke_phase_b_is_text_only_and_role_gated():
    scan_model = _ValidPhaseAModel()
    phase_b_model = _PhaseBModel()
    old_get_json_model = vlm_reader.get_ai_model_for_json
    old_get_model = vlm_reader.get_ai_model_by_name
    old_mount_ref = vlm_reader._fetch_mounts_ref
    old_line_ref = vlm_reader._fetch_lines_ref

    try:
        vlm_reader.get_ai_model_for_json = lambda *_args, **_kwargs: scan_model
        vlm_reader.get_ai_model_by_name = lambda _name: phase_b_model
        vlm_reader._fetch_mounts_ref = lambda: None
        vlm_reader._fetch_lines_ref = lambda: None

        result = vlm_reader.read_palm(
            enhanced_palm=np.zeros((96, 96, 3), dtype=np.uint8),
            mount_crops={},
            hand_metrics={},
            vitality={},
            quality_metrics={"is_usable": True},
            knowledge_context="static knowledge context supplied for smoke test",
            qdrant_context="classical passage context supplied for smoke test",
        )
    finally:
        vlm_reader.get_ai_model_for_json = old_get_json_model
        vlm_reader.get_ai_model_by_name = old_get_model
        vlm_reader._fetch_mounts_ref = old_mount_ref
        vlm_reader._fetch_lines_ref = old_line_ref

    assert scan_model.calls == 1
    assert phase_b_model.calls == 1
    assert len(phase_b_model.last_contents) == 1
    assert isinstance(phase_b_model.last_contents[0], str)
    assert result["phase_a"]["lines"]["marriage_lines"]["count_visible"] == "not_assessable"
    assert result["phase_a"]["thumb"]["flexibility_estimate"] == "not_assessable"
    optional_roles = {
        item["role"]
        for item in result["capture_guidance"]["optional_for_detail"]
    }
    assert {"mercury_edge", "thumb_flex"} <= optional_roles


def _smoke_api_rejects_non_hand_before_ai():
    image_bytes = io.BytesIO()
    Image.new("RGB", (640, 640), color=(120, 120, 120)).save(image_bytes, format="JPEG")
    request = PalmReadingRequest(
        image_base64=base64.b64encode(image_bytes.getvalue()).decode("ascii")
    )

    result = read_api(request)

    assert result.phase_b == ""
    assert "No palm landmarks found" in result.error


def _smoke_scan_accepts_role_labelled_captures():
    image_bytes = io.BytesIO()
    Image.new("RGB", (640, 640), color=(120, 120, 120)).save(image_bytes, format="JPEG")
    encoded = base64.b64encode(image_bytes.getvalue()).decode("ascii")
    request = PalmScanRequest(captures=[
        PalmCapture(role="dominant_full", image_base64=encoded),
        PalmCapture(role="dominant_line_closeup", image_base64=encoded),
    ])

    result = scan_api(request)

    assert result.capture_guidance["general_reading_ready"] is False
    assert result.capture_guidance["required_for_general"] == ["dominant_full"]
    assert "No palm landmarks found" in result.error


if __name__ == "__main__":
    _smoke_phase_a_prompt_limits()
    _smoke_invalid_scan_stops_before_phase_b()
    _smoke_phase_b_is_text_only_and_role_gated()
    _smoke_api_rejects_non_hand_before_ai()
    _smoke_scan_accepts_role_labelled_captures()
    print("palmistry accuracy smoke checks passed")
