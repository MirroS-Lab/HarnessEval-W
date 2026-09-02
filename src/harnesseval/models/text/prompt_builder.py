"""Build Seedance prompts from HarnessEval actions."""

from __future__ import annotations

from typing import Any


FIRST_PERSON_ACTIONS = {
    "W": "The camera pushes forward.",
    "S": "The camera pulls back.",
    "A": "The camera moves to the left.",
    "D": "The camera moves to the right.",
    "left": "The camera pans to the left.",
    "right": "The camera pans to the right.",
    "up": "The camera tilts up.",
    "down": "The camera tilts down.",
    "W+A": "The camera moves diagonally forward-left.",
    "W+D": "The camera moves diagonally forward-right.",
    "S+A": "The camera moves diagonally backward-left.",
    "S+D": "The camera moves diagonally backward-right.",
    "W+left": "The camera pushes forward while panning to the left.",
    "W+right": "The camera pushes forward while panning to the right.",
    "W+up": "The camera pushes forward while tilting up.",
    "W+down": "The camera pushes forward while tilting down.",
}

THIRD_PERSON_ACTIONS = {
    "W": "The subject moves forward while the camera follows.",
    "S": "The subject moves backward while the camera follows.",
    "A": "The subject moves left while the camera tracks left.",
    "D": "The subject moves right while the camera tracks right.",
    "left": "The camera orbits counterclockwise around the subject.",
    "right": "The camera orbits clockwise around the subject.",
    "up": "The camera cranes upward while keeping the subject framed.",
    "down": "The camera cranes downward while keeping the subject framed.",
    "W+A": "The subject moves diagonally forward-left while the camera follows.",
    "W+D": "The subject moves diagonally forward-right while the camera follows.",
    "S+A": "The subject moves diagonally backward-left while the camera follows.",
    "S+D": "The subject moves diagonally backward-right while the camera follows.",
    "W+left": "The subject moves forward while the camera arcs counterclockwise.",
    "W+right": "The subject moves forward while the camera arcs clockwise.",
    "W+up": "The subject moves forward while the camera cranes upward.",
    "W+down": "The subject moves forward while the camera cranes downward.",
}

NAVIGATION_TOKEN_ALIASES = {
    "W": "W",
    "A": "A",
    "S": "S",
    "D": "D",
    "w": "W",
    "a": "A",
    "s": "S",
    "d": "D",
    "forward": "W",
    "backward": "S",
    "strafe_left": "A",
    "strafe_right": "D",
    "turn_left": "left",
    "look_left": "left",
    "turn_right": "right",
    "look_right": "right",
    "look_up": "up",
    "look_down": "down",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "ArrowUp": "up",
    "ArrowDown": "down",
    "ArrowLeft": "left",
    "ArrowRight": "right",
}


def clean_spaces(text: str) -> str:
    return " ".join((text or "").replace("..", ".").split()).strip()


def normalize_navigation_token(token: Any) -> str:
    text = str(token).strip()
    if "+" in text:
        return "+".join(normalize_navigation_token(part) for part in text.split("+"))
    normalized = NAVIGATION_TOKEN_ALIASES.get(text, text)
    if normalized not in FIRST_PERSON_ACTIONS:
        raise ValueError(f"unknown navigation action: {token}")
    return normalized


def navigation_action_tokens(action: dict[str, Any]) -> list[str]:
    chunks = action.get("chunks") or []
    if chunks:
        tokens = []
        for chunk in chunks:
            actions = None
            chunk_action = chunk.get("action")
            if isinstance(chunk_action, dict):
                actions = chunk_action.get("controls")
                if actions is None and chunk_action.get("type") == "navigation":
                    actions = [chunk_action]
            if actions is None:
                actions = chunk.get("controls")
            if actions is None:
                actions = chunk.get("actions")
            if actions is None:
                continue
            if not isinstance(actions, list) or len(actions) != 1:
                raise ValueError(f"expected one navigation action per chunk: {chunk}")
            action_item = actions[0]
            if (
                not isinstance(action_item, dict)
                or action_item.get("type") != "navigation"
            ):
                raise ValueError(f"unexpected chunk action: {action_item}")
            tokens.append(normalize_navigation_token(action_item.get("action")))
        return tokens
    for key in ("actions", "control_sequence"):
        if action.get(key):
            return [normalize_navigation_token(token) for token in action[key]]
    if action.get("action"):
        return [normalize_navigation_token(action["action"])]
    return []


def navigation_sequence_prompt(tokens: list[Any], perspective: str) -> str:
    action_map = (
        THIRD_PERSON_ACTIONS if perspective == "third_person" else FIRST_PERSON_ACTIONS
    )
    normalized = [normalize_navigation_token(token) for token in tokens]
    return clean_spaces(" ".join(action_map[token] for token in normalized))


def chunk_text(action: dict[str, Any]) -> str:
    parts = []
    for index, chunk in enumerate(action.get("chunks") or []):
        text = ""
        chunk_action = chunk.get("action")
        if isinstance(chunk_action, dict):
            text = clean_spaces(str(chunk_action.get("text", "")))
        if not text:
            text = clean_spaces(str(chunk.get("text", "")))
        if text:
            parts.append(f"Chunk {index + 1}: {text}")
    return " ".join(parts)


def case_perspective(case: dict[str, Any]) -> str:
    return str(
        case.get("world", {}).get("source_tags", {}).get("perspective", "first_person")
    )


def navigation_prompt(action: dict[str, Any], case: dict[str, Any]) -> str:
    perspective = case_perspective(case)
    tokens = navigation_action_tokens(action)
    motion = (
        navigation_sequence_prompt(tokens, perspective)
        if tokens
        else clean_spaces(str(action.get("text", "")))
    )
    action_text = clean_spaces(str(action.get("text", "")))
    perspective_clause = (
        "Keep a third-person following view with the route visible ahead."
        if perspective == "third_person"
        else "Keep a first-person navigation viewpoint."
    )
    return clean_spaces(
        "Navigation video in the same scene. "
        f"{motion} {action_text} {perspective_clause} "
        "Make the motion smooth and continuous. Preserve route landmarks, spatial "
        "layout, scene identity, and visual style. Do not teleport, cut to the "
        "destination, or introduce unrelated events."
    )


def intentional_prompt(action: dict[str, Any]) -> str:
    action_text = clean_spaces(str(action.get("text", "")))
    if not action_text:
        return "Locked-off video in the same scene."
    return clean_spaces(
        "Locked-off video in the same scene. "
        f"{action_text} "
        "Show the requested state change clearly through a short, natural transition. "
        "Keep the camera, scene identity, background layout, lighting, and all unrelated "
        "objects unchanged. Do not introduce unrelated people, objects, camera cuts, or "
        "extra events."
    )


def offscreen_prompt(action: dict[str, Any]) -> str:
    action_text = clean_spaces(str(action.get("text", "")))
    chunks = chunk_text(action)
    return clean_spaces(
        "Offscreen evolution video in the same scene. "
        f"{action_text} {chunks} "
        "Keep the interaction continuous across all chunks. Stable landmarks, layout, "
        "object identities, lighting style, and camera perspective should remain traceable. "
        "If the route leaves a region and later returns, show the same evolving world rather "
        "than a reset or a new scene."
    )


def physical_prompt(action: dict[str, Any]) -> str:
    action_text = clean_spaces(str(action.get("text", "")))
    parameters = action.get("parameters") or {}
    parameter_text = " ".join(
        f"{key}={value}" for key, value in sorted(parameters.items())
    )
    return clean_spaces(
        "Fixed measurement-camera video of the same physical setup. "
        f"{action_text} {parameter_text} "
        "Show the physical evolution caused by the specified condition through the full "
        "rollout. Keep the camera, scale markers, apparatus, background, and all unspecified "
        "physical parameters unchanged. Do not introduce extra forces, camera cuts, new "
        "objects, or unrelated events."
    )


def turns_for_case(case: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand one HarnessEval action into ordered generation turns."""

    action = (case.get("interaction") or {}).get("action") or {}
    if not isinstance(action, dict):
        raise ValueError(f"invalid action for case {case.get('case_id')}")
    chunks = action.get("chunks")
    if chunks is None or chunks == []:
        return [
            {
                "turn_index": 1,
                "turn_id": "turn_001",
                "action_chunk": None,
                "action": dict(action),
            }
        ]
    if not isinstance(chunks, list):
        raise ValueError(f"action chunks must be an array for case {case.get('case_id')}")

    turns = []
    seen_ids = set()
    for index, chunk in enumerate(chunks, start=1):
        if not isinstance(chunk, dict):
            raise ValueError(
                f"invalid action chunk {index} for case {case.get('case_id')}"
            )
        turn_id = str(chunk.get("chunk_id") or f"c{index:02d}")
        if turn_id in seen_ids:
            raise ValueError(
                f"duplicate action chunk id {turn_id} for case {case.get('case_id')}"
            )
        seen_ids.add(turn_id)
        turns.append(
            {
                "turn_index": index,
                "turn_id": turn_id,
                "action_chunk": dict(chunk),
                # Expose only this chunk to the per-turn prompt builder.
                "action": {**action, "chunks": [dict(chunk)]},
            }
        )
    return turns


def _prompt_for_action(case: dict[str, Any], action: dict[str, Any]) -> str:
    probe_family = str(case.get("taxonomy", {}).get("probe_family", ""))
    action_type = str(action.get("type") or "")
    if probe_family in {
        "exploratory_transition",
        "drift_resistance",
        "return_revisit_consistency",
    } or action_type in {
        "long_navigation_sequence",
        "navigation_control",
        "navigation",
        "closed_loop_navigation",
    }:
        return navigation_prompt(action, case)
    if (
        probe_family == "intentional_transition"
        or action_type == "text_based_state_change"
    ):
        return intentional_prompt(action)
    if probe_family == "offscreen_evolution" or action_type in {
        "offscreen_evolution",
        "offscreen_evolution_sequence",
    }:
        return offscreen_prompt(action)
    if probe_family == "physical_transition" or action_type in {
        "apply_physical_control",
        "physical_parameter_condition",
    }:
        return physical_prompt(action)
    text = clean_spaces(str(action.get("text", "")))
    if text:
        return text
    chunks = chunk_text(action)
    if chunks:
        return chunks
    raise ValueError(f"missing prompt text for case {case.get('case_id')}")


def prompt_for_turn(case: dict[str, Any], turn: dict[str, Any]) -> str:
    """Build a prompt from one turn without exposing later action chunks."""

    action = turn.get("action")
    if not isinstance(action, dict):
        raise ValueError(f"invalid generation turn for case {case.get('case_id')}")
    return _prompt_for_action(case, action)


def prompt_for_case(case: dict[str, Any]) -> str:
    """Build the legacy whole-case prompt for callers that need a summary."""

    action = (case.get("interaction") or {}).get("action") or {}
    if not isinstance(action, dict):
        raise ValueError(f"invalid action for case {case.get('case_id')}")
    return _prompt_for_action(case, action)
