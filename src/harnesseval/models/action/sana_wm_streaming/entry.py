"""Launch official SANA-WM Streaming with a local Stage-1 text encoder."""

from __future__ import annotations

import os
import sys


def main() -> None:
    sana_root = os.environ["PYTHONPATH"].split(os.pathsep)[0]
    if sana_root not in sys.path:
        sys.path.insert(0, sana_root)

    import inference_video_scripts.wm.inference_sana_wm as official
    import torch
    from diffusion.model import builder
    from transformers import AutoModelForCausalLM, AutoTokenizer

    original = builder.get_tokenizer_and_text_encoder

    def load_local(name: str = "T5", device: str = "cuda"):
        requested = os.environ.get("SANA_WM_STAGE1_TEXT_ENCODER_NAME", "gemma-2-2b-it")
        root = os.environ.get("SANA_WM_STAGE1_TEXT_ENCODER_ROOT", "")
        if name != requested or not root:
            return original(name=name, device=device)
        tokenizer = AutoTokenizer.from_pretrained(root, local_files_only=True)
        tokenizer.padding_side = "right"
        encoder = AutoModelForCausalLM.from_pretrained(
            root, torch_dtype=torch.bfloat16, local_files_only=True
        ).get_decoder()
        return tokenizer, encoder.to(device)

    builder.get_tokenizer_and_text_encoder = load_local
    official.get_tokenizer_and_text_encoder = load_local

    import inference_video_scripts.wm.inference_sana_wm_streaming as streaming

    streaming.main()


if __name__ == "__main__":
    main()
