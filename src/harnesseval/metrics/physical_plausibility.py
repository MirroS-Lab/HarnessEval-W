"""
Physical plausibility — PAVRM reward model scoring.

Method: PAVRM (qwen3vl_a3b) assigns a 0~5 physical plausibility score per video.
- raw_score: PAVRM raw score (0~5)
- score = raw_score / 5.0 (normalized to 0~1, higher = better)

Usage:
    from harnesseval.metrics.physical_plausibility import PhysicalPlausibilityEvaluator
    evaluator = PhysicalPlausibilityEvaluator(model_path="path/to/qwen3vl_a3b")
    results = evaluator.score_videos(["video1.mp4", "video2.mp4"])
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import numpy as np
import torch

from .weight_utils import get_weights_dir

METRIC_NAME = "visual_plausibility"

VIDEO_QUALITY_PROMPT = (
    "Suppose you are an expert in judging and evaluating the quality of AI-generated videos, "
    "please watch the above provided video and give scores for the video's truthfulness and "
    "rationality. i.e., whether the video's overall appreance and motion are consistent with "
    "our common-sense, physical principles.\n"
    "Your rating should be chosen from the following five catefories: Perfect, Good, Fair, Poor, "
    "and Bad. Now please rate this video:"
)

ANCHOR_TOKEN_IDS = [51041, 15216, 60795, 84103, 17082]
ANCHOR_WEIGHTS = torch.tensor([5.0, 4.0, 3.0, 2.0, 1.0])


class PhysicalPlausibilityEvaluator:
    """Local PAVRM inference using Qwen3-VL reward model (transformers backend)."""

    def __init__(self, model_path: str = None, device: str = "cuda"):
        from transformers import AutoModelForImageTextToText, AutoProcessor

        if model_path is None:
            model_path = os.environ.get("PAVRM_MODEL_PATH", "")
        if not model_path or not os.path.isdir(model_path):
            _default = os.path.join(
                get_weights_dir(), "qwen3vl-a3b-visual-plausibility"
            )
            if os.path.isdir(_default):
                model_path = _default
            else:
                raise RuntimeError(
                    f"PAVRM model path not found: {model_path}. "
                    "Set PAVRM_MODEL_PATH env var or pass model_path argument."
                )

        try:
            self.model = AutoModelForImageTextToText.from_pretrained(
                model_path, dtype=torch.bfloat16,
                attn_implementation="flash_attention_2",
                device_map="auto",
            )
        except (ImportError, ValueError):
            self.model = AutoModelForImageTextToText.from_pretrained(
                model_path, dtype=torch.bfloat16,
                device_map="auto",
            )
        self.processor = AutoProcessor.from_pretrained(model_path)
        self.device = device

    @torch.no_grad()
    def prepare_video(self, video_path: str, fps: float = 2.0):
        """Decode and tokenize a video on CPU before entering the GPU lane."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(video_path)
        messages = [{
            "role": "user",
            "content": [
                {"type": "video", "video": video_path,
                 "fps": fps, "max_pixels": 602112},
                {"type": "text", "text": VIDEO_QUALITY_PROMPT},
            ],
        }]
        return self.processor.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True,
            return_dict=True, return_tensors="pt"
        )

    @torch.no_grad()
    def score_prepared(self, inputs) -> Dict[str, Any]:
        """Run one already-prepared request through the resident GPU model."""
        inputs = inputs.to(self.model.device)
        outputs = self.model.generate(
            **inputs, max_new_tokens=1, do_sample=False,
            output_logits=True, return_dict_in_generate=True)

        logits = outputs.logits[0]
        token_ids = torch.tensor(ANCHOR_TOKEN_IDS, device=logits.device)
        logits_gathered = torch.gather(logits[0], dim=-1, index=token_ids)
        probs = torch.softmax(logits_gathered, dim=-1)
        raw_score = float(torch.sum(probs * ANCHOR_WEIGHTS.to(logits.device)))

        return {
            "raw_score": round(raw_score, 4),
            "score": round(raw_score / 5.0, 4),
            "error": None,
        }

    @torch.no_grad()
    def score_video(self, video_path: str, fps: float = 2.0) -> Dict[str, Any]:
        """Score a single video for physical plausibility."""
        try:
            return self.score_prepared(self.prepare_video(video_path, fps=fps))
        except Exception as e:
            return {"raw_score": None, "score": None, "error": str(e)}

    def score_videos(self, video_paths: List[str], fps: float = 2.0) -> List[Dict[str, Any]]:
        """Score multiple videos sequentially.

        Args:
            video_paths: List of video file paths
            fps: Frames per second to sample from videos

        Returns:
            List of dicts with raw_score (0-5), score (0-1), error
        """
        results = []
        for vp in video_paths:
            results.append(self.score_video(vp, fps))
        return results


def score_video_api(video_path: str, endpoint: str = None) -> Dict[str, Any]:
    """Score a video via PAVRM HTTP API endpoint (fallback)."""
    import requests

    endpoint = endpoint or os.environ.get("PAVRM_API_URL", "")
    if not endpoint:
        return {"raw_score": None, "score": None,
                "error": "PAVRM_API_URL not set. Set env var or pass endpoint."}

    abs_path = os.path.abspath(video_path)
    try:
        resp = requests.post(
            endpoint,
            json={"video_url": abs_path, "prompt": "", "dimension": "visual"},
            timeout=120,
        )
        data = resp.json()
        if "detail" in data:
            return {"raw_score": None, "score": None, "error": data["detail"]}
        raw = float(data["score"])
        return {"raw_score": round(raw, 4), "score": round(raw / 5.0, 4), "error": None}
    except Exception as e:
        return {"raw_score": None, "score": None, "error": str(e)}


def compute_case(video_path: str, model_path: str = None,
                 endpoint: str = None, device: str = "cuda") -> Dict[str, Any]:
    """Evaluate physical plausibility. Tries local model first, falls back to API."""
    model_path = model_path or os.environ.get("PAVRM_MODEL_PATH", "")
    if not model_path:
        _default = os.path.join(get_weights_dir(), "qwen3vl-a3b-visual-plausibility")
        if os.path.isdir(_default):
            model_path = _default
    endpoint = endpoint or os.environ.get("PAVRM_API_URL", "")

    if model_path and os.path.isdir(model_path):
        evaluator = PhysicalPlausibilityEvaluator(model_path=model_path, device=device)
        result = evaluator.score_video(video_path)
    elif endpoint:
        result = score_video_api(video_path, endpoint)
    else:
        return {"score": None, "error": "Neither PAVRM_MODEL_PATH nor PAVRM_API_URL is set"}

    return {
        "score": result["score"],
        "details": {"raw_score": result["raw_score"]},
        "params": {"method": "pavrm_qwen3vl_a3b", "scale": "raw/5"},
        "error": result["error"],
    }


def build_case_record(
    case_id: str,
    video_path: str,
    raw_score: Optional[float] = None,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    score = round(raw_score / 5.0, 4) if raw_score is not None and error is None else None
    return {
        "case_id": str(case_id),
        "video_path": str(video_path),
        "score": score,
        "details": {"raw_score": round(raw_score, 4) if raw_score is not None else None},
        "params": {"method": "pavrm_qwen3vl_a3b", "scale": "raw/5"},
        "error": error,
    }


def summarize_model_results(case_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    valid = [r for r in case_records if r.get("score") is not None]
    if not valid:
        return {"score": 0.0, "n_cases": 0}
    scores = [r["score"] for r in valid]
    raws = [r["details"]["raw_score"] for r in valid if r["details"].get("raw_score")]
    return {
        "score": round(float(np.mean(scores)), 4),
        "raw_mean": round(float(np.mean(raws)), 4) if raws else 0.0,
        "n_cases": len(valid),
    }
