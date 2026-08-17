"""MegaSAM pipeline with immutable networks resident across video requests."""

from __future__ import annotations

import gc
import glob
import os
import runpy
import sys
import tempfile
import time
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

import cv2
import numpy as np

from . import unidepth


SCHEMA_VERSION = "harnesseval.resident_megasam_pipeline"
DEFAULT_DROID_BUFFER_SIZE = 1024


def droid_buffer_size(frame_count: int) -> int:
    if frame_count < 1:
        raise ValueError("frame_count must be positive")
    return max(DEFAULT_DROID_BUFFER_SIZE, frame_count)


@contextmanager
def working_directory(path: Path) -> Iterable[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def prepend_sys_path(paths: Iterable[Path]) -> None:
    for path in reversed([str(path) for path in paths]):
        if path not in sys.path:
            sys.path.insert(0, path)


def batches(items: list[Path], batch_size: int) -> Iterable[list[Path]]:
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def compute_stride(video_path: Path, target_fps: float) -> tuple[int, float, float]:
    cap = cv2.VideoCapture(str(video_path))
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 24.0)
    cap.release()
    stride = max(1, int(fps / target_fps))
    return stride, fps, fps / stride


def extract_frames(video_path: Path, frames_dir: Path, stride: int) -> int:
    frames_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    index = 0
    saved = 0
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        if index % stride == 0:
            cv2.imwrite(str(frames_dir / f"{saved:05d}.jpg"), frame)
            saved += 1
        index += 1
    cap.release()
    return saved


def atomic_save_pose(source: Path, destination: Path, metadata: dict[str, Any]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.stem}.{os.getpid()}.{time.time_ns()}.tmp.npz")
    try:
        with np.load(source) as data:
            cam_c2w = data["cam_c2w"]
            np.savez(
                temporary,
                cam_c2w=cam_c2w,
                camera_centers=cam_c2w[:, :3, 3],
                intrinsic=data["intrinsic"],
                stride=metadata["stride"],
                original_fps=metadata["original_fps"],
                effective_fps=metadata["effective_fps"],
            )
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def valid_pose_cache(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path) as data:
            poses = data["cam_c2w"]
            return poses.ndim == 3 and poses.shape[1:] == (4, 4) and poses.shape[0] >= 2
    except Exception:  # noqa: BLE001
        return False


class ResidentMegaSamPipeline:
    """Load all three MegaSAM networks once while recreating scene state per request."""

    def __init__(
        self,
        dependencies_root: Path,
        weights_root: Path | None = None,
        device: str = "cuda",
        target_fps: float = 15.0,
        frame_batch_size: int = 1,
    ) -> None:
        self.dependencies_root = dependencies_root.resolve()
        self.megasam_root = self.dependencies_root / "mega-sam"
        self.depth_anything_root = self.megasam_root / "Depth-Anything"
        self.unidepth_root = self.megasam_root / "UniDepth"
        self.weights_root = (
            weights_root.resolve() if weights_root else Path("weights/megasam").resolve()
        )
        self.device_name = device
        self.target_fps = target_fps
        if frame_batch_size < 1:
            raise ValueError("frame_batch_size must be positive")
        self.frame_batch_size = frame_batch_size
        configured_tmp_root = os.environ.get("HARNESSEVAL_MEGASAM_TMPDIR")
        self.tmp_root = (
            Path(configured_tmp_root).resolve()
            if configured_tmp_root
            else self.megasam_root / "_megasam_tmp"
        )
        self.tmp_root.mkdir(parents=True, exist_ok=True)
        self.load_started = time.time()
        self._configure_imports()

        import torch
        import torch.nn.functional as torch_functional
        from torchvision.transforms import Compose
        from depth_anything.dpt import DPT_DINOv2
        from depth_anything.util.transform import NormalizeImage, PrepareForNet, Resize

        self.torch = torch
        self.torch_functional = torch_functional
        self.device = torch.device(device)
        with working_directory(self.megasam_root):
            self.depth_anything = DPT_DINOv2(
                encoder="vitl",
                features=256,
                out_channels=[256, 512, 1024, 1024],
                localhub=True,
            ).to(self.device)
        depth_weights = self.weights_root / "depth_anything_vitl14.pth"
        self.depth_anything.load_state_dict(
            torch.load(depth_weights, map_location="cpu"),
            strict=True,
        )
        self.depth_anything.eval()
        self.depth_transform = Compose(
            [
                Resize(
                    width=768,
                    height=768,
                    resize_target=False,
                    keep_aspect_ratio=True,
                    ensure_multiple_of=14,
                    resize_method="upper_bound",
                    image_interpolation_method=cv2.INTER_CUBIC,
                ),
                NormalizeImage(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                PrepareForNet(),
            ]
        )

        self.unidepth = unidepth.load_unidepth_model(
            self.unidepth_root,
            self.weights_root,
            self.device,
        )
        self.droid_class, self.droid_net = self._load_droid_net()
        self.loaded_at = time.time()
        print(
            f"[MEGASAM] resident Depth Anything, UniDepth, and DROIDNet loaded in "
            f"{self.loaded_at - self.load_started:.1f}s "
            f"(frame_batch_size={self.frame_batch_size}, tmp_root={self.tmp_root})",
            flush=True,
        )

    def _configure_imports(self) -> None:
        prepend_sys_path(
            [
                self.depth_anything_root,
                self.unidepth_root,
                self.megasam_root / "base",
                self.megasam_root / "base" / "droid_slam",
                self.megasam_root / "base" / "thirdparty" / "lietorch",
            ]
        )
        os.environ.setdefault("HF_HOME", str(self.weights_root / "huggingface"))
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        os.environ.setdefault("TORCH_HOME", str(self.weights_root / "torch_home"))

    def _load_droid_net(self) -> tuple[Any, Any]:
        from droid import Droid
        from droid_net import DroidNet

        checkpoint = self.weights_root / "megasam_final.pth"
        net = DroidNet()
        state_dict = OrderedDict(
            (key.replace("module.", ""), value)
            for key, value in self.torch.load(checkpoint).items()
        )
        for key in (
            "update.weight.2.weight",
            "update.weight.2.bias",
            "update.delta.2.weight",
            "update.delta.2.bias",
        ):
            state_dict[key] = state_dict[key][:2]
        net.load_state_dict(state_dict, strict=True)
        return Droid, net.to(self.device).eval()

    @staticmethod
    def frame_paths(image_root: Path) -> list[Path]:
        return [Path(path) for path in sorted(glob.glob(str(image_root / "*.jpg")))] + [
            Path(path) for path in sorted(glob.glob(str(image_root / "*.png")))
        ]

    def run_depth_anything(self, image_root: Path, output_root: Path) -> int:
        images = self.frame_paths(image_root)
        if not images:
            raise FileNotFoundError(f"no input frames found under {image_root}")
        output_root.mkdir(parents=True, exist_ok=True)
        with self.torch.no_grad():
            for image_paths in batches(images, self.frame_batch_size):
                transformed = []
                dimensions = []
                for image_path in image_paths:
                    raw_image = cv2.imread(str(image_path))[..., :3]
                    image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB) / 255.0
                    dimensions.append(image.shape[:2])
                    transformed.append(self.depth_transform({"image": image})["image"])
                if len(set(dimensions)) != 1:
                    raise RuntimeError("MegaSAM extracted frames changed dimensions within one video")
                image_tensor = self.torch.from_numpy(np.stack(transformed)).to(self.device)
                depth = self.depth_anything(image_tensor).unsqueeze(1)
                depth = self.torch_functional.interpolate(
                    depth,
                    dimensions[0],
                    mode="bilinear",
                    align_corners=False,
                )[:, 0]
                depth_values = np.float32(depth.cpu().numpy())
                for image_path, depth_value in zip(image_paths, depth_values, strict=True):
                    np.save(output_root / f"{image_path.stem}.npy", depth_value)
        return len(images)

    def run_unidepth(self, image_root: Path, output_root: Path, scene_name: str) -> int:
        from PIL import Image

        images = self.frame_paths(image_root)
        if not images:
            raise FileNotFoundError(f"no input frames found under {image_root}")
        output_scene = output_root / scene_name
        output_scene.mkdir(parents=True, exist_ok=True)
        with self.torch.no_grad():
            for image_paths in batches(images, self.frame_batch_size):
                rgb_values = []
                for image_path in image_paths:
                    with Image.open(image_path) as image:
                        rgb = np.array(image)[..., :3]
                    rgb_values.append(unidepth.resize_rgb(rgb))
                rgb_tensor = self.torch.from_numpy(np.stack(rgb_values)).permute(0, 3, 1, 2).to(self.device)
                predictions = self.unidepth.infer(rgb_tensor)
                depth_values = predictions["depth"][:, 0].detach().cpu().numpy()
                intrinsics_values = predictions["intrinsics"].detach().cpu().numpy()
                prediction_width = predictions["depth"].shape[-1]
                for image_path, depth, intrinsics in zip(
                    image_paths,
                    depth_values,
                    intrinsics_values,
                    strict=True,
                ):
                    fov = np.rad2deg(2 * np.arctan(prediction_width / (2 * intrinsics[0, 0])))
                    np.savez(
                        output_scene / f"{image_path.stem}.npz",
                        depth=np.float32(depth),
                        fov=np.float32(fov),
                    )
        return len(images)

    def run_camera_tracking(
        self,
        frames_dir: Path,
        mono_root: Path,
        metric_root: Path,
        scene_name: str,
        runtime_root: Path,
        buffer_size: int,
    ) -> Path:
        runtime_root.mkdir(parents=True, exist_ok=True)
        output = runtime_root / "outputs" / f"{scene_name}_droid.npz"
        output.unlink(missing_ok=True)
        original_load_weights = self.droid_class.load_weights
        original_argv = sys.argv

        def use_resident_net(instance: Any, _weights: str) -> None:
            instance.net = self.droid_net

        self.droid_class.load_weights = use_resident_net
        sys.argv = [
            "camera_tracking_scripts/test_demo.py",
            "--datapath",
            str(frames_dir),
            "--weights",
            str(self.weights_root / "megasam_final.pth"),
            "--buffer",
            str(buffer_size),
            "--scene_name",
            scene_name,
            "--mono_depth_path",
            str(mono_root),
            "--metric_depth_path",
            str(metric_root),
            "--disable_vis",
        ]
        namespace: dict[str, Any] | None = None
        try:
            with working_directory(runtime_root):
                namespace = runpy.run_path(
                    str(self.megasam_root / "camera_tracking_scripts" / "test_demo.py"),
                    run_name="__main__",
                )
        finally:
            self.droid_class.load_weights = original_load_weights
            sys.argv = original_argv
            if namespace is not None:
                namespace.clear()
            gc.collect()
            self.torch.cuda.empty_cache()
        if not output.is_file():
            raise FileNotFoundError(f"MegaSAM output not found: {output}")
        return output

    def evaluate(self, video: Path, output: Path, target_fps: float | None = None) -> dict[str, Any]:
        target_fps = float(target_fps or self.target_fps)
        scene_name = video.stem
        stride, original_fps, effective_fps = compute_stride(video, target_fps)
        stage_times: dict[str, float] = {}
        started = time.time()
        with tempfile.TemporaryDirectory(
            prefix=f"harnesseval_resident_megasam_{scene_name}_",
            dir=str(self.tmp_root),
        ) as temporary:
            temporary_root = Path(temporary)
            frames_dir = temporary_root / "frames" / scene_name
            mono_root = temporary_root / "mono"
            mono_dir = mono_root / scene_name
            metric_root = temporary_root / "metric"

            stage = time.time()
            frame_count = extract_frames(video, frames_dir, stride)
            tracking_buffer_size = droid_buffer_size(frame_count)
            stage_times["extract_frames"] = round(time.time() - stage, 2)
            stage = time.time()
            self.run_depth_anything(frames_dir, mono_dir)
            stage_times["depth_anything"] = round(time.time() - stage, 2)
            stage = time.time()
            self.run_unidepth(frames_dir, metric_root, scene_name)
            stage_times["unidepth"] = round(time.time() - stage, 2)
            stage = time.time()
            source_pose = self.run_camera_tracking(
                frames_dir,
                mono_root,
                metric_root,
                scene_name,
                temporary_root / "tracking_runtime",
                tracking_buffer_size,
            )
            stage_times["camera_tracking"] = round(time.time() - stage, 2)
            atomic_save_pose(
                source_pose,
                output,
                {
                    "stride": stride,
                    "original_fps": original_fps,
                    "effective_fps": effective_fps,
                },
            )
            source_pose.unlink(missing_ok=True)
        if not valid_pose_cache(output):
            raise RuntimeError(f"resident MegaSAM produced an invalid pose cache: {output}")
        return {
            "schema_version": SCHEMA_VERSION,
            "video_path": str(video),
            "output_path": str(output),
            "frame_count": frame_count,
            "droid_buffer_size": tracking_buffer_size,
            "stride": stride,
            "original_fps": original_fps,
            "effective_fps": effective_fps,
            "frame_batch_size": self.frame_batch_size,
            "tmp_root": str(self.tmp_root),
            "stage_times": stage_times,
            "elapsed_seconds": round(time.time() - started, 2),
            "model_load_scope": "resident_worker_process",
            "model_load_count": {
                "depth_anything": 1,
                "unidepth": 1,
                "droid_net": 1,
            },
        }
