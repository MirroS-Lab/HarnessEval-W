"""WBench-style action conditioning for HarnessEval cases."""

from __future__ import annotations

from typing import Any

from ..navigation import navigation_turns
from ..text.prompt_builder import case_perspective


def case_to_actions(case: dict[str, Any]) -> dict[str, Any]:
    actions = []
    for turn in navigation_turns(case):
        motion = turn["motion"]
        keyboard = [0, 0, 0, 0]
        if motion["forward"] > 0:
            keyboard[0] = 1
        elif motion["forward"] < 0:
            keyboard[1] = 1
        if motion["right"] < 0:
            keyboard[2] = 1
        elif motion["right"] > 0:
            keyboard[3] = 1
        actions.append(
            {
                **turn,
                "tokens": turn["token"].split("+") if turn["token"] else [],
                "keyboard": keyboard,
                "mouse": [motion["pitch"], motion["yaw"]],
            }
        )
    return {
        "perspective": case_perspective(case),
        "actions": actions,
        "turn_count": len(actions),
    }
