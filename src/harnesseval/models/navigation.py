"""Convert HarnessEval action chunks into model-agnostic navigation turns."""

from __future__ import annotations

from typing import Any

from .text.prompt_builder import (
    navigation_action_tokens,
    normalize_navigation_token,
)


OFFSCREEN_TOKENS: tuple[str | None, ...] = (
    "left",
    "left",
    "W",
    None,
    "S",
    "right",
    "right",
    None,
)


def _chunk_token(chunk: dict[str, Any]) -> str | None:
    actions: Any = chunk.get("actions")
    chunk_action = chunk.get("action")
    if actions is None and isinstance(chunk_action, dict):
        actions = (
            [chunk_action] if chunk_action.get("type") == "navigation" else None
        )
    if actions is None:
        actions = chunk.get("controls")
    if actions is None:
        return None
    if not isinstance(actions, list) or len(actions) != 1:
        raise ValueError(f"expected one navigation action per chunk: {chunk}")
    item = actions[0]
    if not isinstance(item, dict) or item.get("type") != "navigation":
        raise ValueError(f"unexpected chunk action: {item}")
    return normalize_navigation_token(item.get("action"))


def motion_for_token(token: str | None) -> dict[str, int]:
    motion = {"forward": 0, "right": 0, "yaw": 0, "pitch": 0}
    if token is None:
        return motion
    for part in normalize_navigation_token(token).split("+"):
        if part == "W":
            motion["forward"] = 1
        elif part == "S":
            motion["forward"] = -1
        elif part == "A":
            motion["right"] = -1
        elif part == "D":
            motion["right"] = 1
        elif part == "left":
            motion["yaw"] = -1
        elif part == "right":
            motion["yaw"] = 1
        elif part == "up":
            motion["pitch"] = 1
        elif part == "down":
            motion["pitch"] = -1
    return motion


def navigation_turns(case: dict[str, Any]) -> list[dict[str, Any]]:
    action = (case.get("interaction") or {}).get("action") or {}
    if not isinstance(action, dict):
        raise ValueError(f"invalid action for case {case.get('case_id')}")
    chunks = action.get("chunks")
    if chunks is not None and not isinstance(chunks, list):
        raise ValueError(f"action chunks must be an array for case {case.get('case_id')}")

    if chunks:
        tokens = [_chunk_token(chunk) for chunk in chunks]
        family = str(case.get("taxonomy", {}).get("probe_family", ""))
        if family == "offscreen_evolution" and not any(tokens):
            if len(chunks) != len(OFFSCREEN_TOKENS):
                raise ValueError("offscreen action must contain eight chunks")
            tokens = list(OFFSCREEN_TOKENS)
        return [
            {
                "turn_index": index,
                "turn_id": str(chunk.get("chunk_id") or f"c{index:02d}"),
                "token": token,
                "motion": motion_for_token(token),
                "action_chunk": dict(chunk),
            }
            for index, (chunk, token) in enumerate(zip(chunks, tokens), start=1)
        ]

    tokens = navigation_action_tokens(action)
    if not tokens:
        tokens = [None]
    return [
        {
            "turn_index": index,
            "turn_id": f"turn_{index:03d}",
            "token": token,
            "motion": motion_for_token(token),
            "action_chunk": None,
        }
        for index, token in enumerate(tokens, start=1)
    ]
