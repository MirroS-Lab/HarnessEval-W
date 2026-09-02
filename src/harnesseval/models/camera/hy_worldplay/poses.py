"""Camera trajectories for HY-WorldPlay."""

from __future__ import annotations

from typing import Any

import numpy as np

from ...navigation import navigation_turns
from ...text.prompt_builder import case_perspective

LATENTS_PER_TURN = 12
TEMPORAL_COMPRESSION = 4
FORWARD_STEP = 0.08
YAW_STEP = np.deg2rad(3.0)
PITCH_STEP = np.deg2rad(3.0)
ORBIT_RADIUS = FORWARD_STEP / YAW_STEP
ORBIT_HEIGHT = 0.3
DEFAULT_INTRINSIC = [
    [969.6969696969696, 0.0, 960.0],
    [0.0, 969.6969696969696, 540.0],
    [0.0, 0.0, 1.0],
]


def _rot_x(angle: float) -> np.ndarray:
    cosine, sine = np.cos(angle), np.sin(angle)
    return np.asarray(
        [[1, 0, 0], [0, cosine, -sine], [0, sine, cosine]], dtype=np.float64
    )


def _rot_y(angle: float) -> np.ndarray:
    cosine, sine = np.cos(angle), np.sin(angle)
    return np.asarray(
        [[cosine, 0, sine], [0, 1, 0], [-sine, 0, cosine]], dtype=np.float64
    )


def _motions(turns: list[dict[str, Any]]) -> list[dict[str, float]]:
    motions = []
    for index, turn in enumerate(turns):
        motion = turn["motion"]
        delta = {}
        if motion["forward"]:
            delta["forward"] = FORWARD_STEP * np.sign(motion["forward"])
        if motion["right"]:
            delta["right"] = FORWARD_STEP * np.sign(motion["right"])
        if motion["yaw"]:
            delta["yaw"] = YAW_STEP * np.sign(motion["yaw"])
        if motion["pitch"]:
            delta["pitch"] = PITCH_STEP * np.sign(motion["pitch"])
        count = LATENTS_PER_TURN - 1 if index == 0 else LATENTS_PER_TURN
        motions.extend(dict(delta) for _ in range(count))
    return motions


def _first_person(motions: list[dict[str, float]]) -> list[np.ndarray]:
    transform = np.eye(4)
    poses = [transform.copy()]
    for motion in motions:
        if "yaw" in motion:
            transform[:3, :3] = transform[:3, :3] @ _rot_y(motion["yaw"])
        if "pitch" in motion:
            transform[:3, :3] = transform[:3, :3] @ _rot_x(motion["pitch"])
        transform[:3, 3] += transform[:3, :3] @ np.asarray(
            [motion.get("right", 0.0), 0.0, motion.get("forward", 0.0)]
        )
        poses.append(transform.copy())
    return poses


def _third_person(motions: list[dict[str, float]]) -> list[np.ndarray]:
    azimuth = np.pi
    elevation = 0.0
    character = np.zeros(3)

    def camera_pose() -> np.ndarray:
        camera = character + np.asarray(
            [
                ORBIT_RADIUS * np.cos(elevation) * np.sin(azimuth),
                ORBIT_HEIGHT + ORBIT_RADIUS * np.sin(elevation),
                ORBIT_RADIUS * np.cos(elevation) * np.cos(azimuth),
            ]
        )
        forward = character + np.asarray([0.0, ORBIT_HEIGHT * 0.5, 0.0]) - camera
        forward /= np.linalg.norm(forward) + 1e-8
        right = np.cross(forward, np.asarray([0.0, 1.0, 0.0]))
        right /= np.linalg.norm(right) + 1e-8
        transform = np.eye(4)
        transform[:3, 0] = right
        transform[:3, 1] = np.cross(right, forward)
        transform[:3, 2] = forward
        transform[:3, 3] = camera
        return transform

    poses = [camera_pose()]
    for motion in motions:
        azimuth -= motion.get("yaw", 0.0)
        elevation = float(
            np.clip(
                elevation - motion.get("pitch", 0.0),
                np.deg2rad(-60),
                np.deg2rad(60),
            )
        )
        character += np.asarray(
            [motion.get("right", 0.0), 0.0, motion.get("forward", 0.0)]
        )
        poses.append(camera_pose())
    return poses


def case_to_poses(case: dict[str, Any]) -> dict[str, Any]:
    """Convert every case turn into one complete HY camera trajectory."""

    turns = navigation_turns(case)
    motions = _motions(turns)
    perspective = case_perspective(case)
    matrices = (
        _first_person(motions)
        if perspective == "first_person"
        else _third_person(motions)
    )
    total_latents = len(turns) * LATENTS_PER_TURN
    if len(matrices) != total_latents:
        raise RuntimeError(f"pose count mismatch: {len(matrices)} != {total_latents}")
    poses = {
        str(index): {"extrinsic": matrix.tolist(), "K": DEFAULT_INTRINSIC}
        for index, matrix in enumerate(matrices)
    }
    return {
        "perspective": perspective,
        "poses": poses,
        "turn_count": len(turns),
        "latents_per_turn": LATENTS_PER_TURN,
        "total_latents": total_latents,
        "video_length": (total_latents - 1) * TEMPORAL_COMPRESSION + 1,
    }
