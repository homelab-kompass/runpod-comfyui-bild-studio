#!/usr/bin/env python3
"""Download selected model weights for the Homelab-Kompass Bild-Studio.
No weights are bundled in the image.

Aliases (comma-separated in MODELS or HK_DOWNLOAD_MODELS, or argv):
  krea2-turbo, krea2-raw, moss, moss-edit

Krea 2 packs require ACCEPT_KREA_LICENSE=yes (or ACCEPT_LICENSE=yes).
Qwen Image 2.1 and FLUX.1 are intentionally not offered.
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from pathlib import Path

COMFYUI_DIR = Path(os.environ.get("COMFYUI_DIR", "/workspace/runpod-slim/ComfyUI"))
MODELS_ROOT = COMFYUI_DIR / "models"
LICENSE_DIR = Path("/workspace/homelab-kompass/licenses")
RESERVE_BYTES = 2 * 1024 * 1024 * 1024  # keep 2 GiB free after planned downloads

# Hugging Face LFS sha256 and sizes, retrieved 2026-11-22.
KREA_TE = {
    "repo": "Comfy-Org/Krea-2",
    "filename": "text_encoders/qwen3vl_4b_fp8_scaled.safetensors",
    "dest": "text_encoders/qwen3vl_4b_fp8_scaled.safetensors",
    "sha256": "54bd5144df0bbc25dd6ccadfcb826b521445a1b06ae5a42570bdd2974ca87094",
    "size": 5242467968,
}
KREA_VAE = {
    "repo": "Comfy-Org/Krea-2",
    "filename": "vae/qwen_image_vae.safetensors",
    "dest": "vae/qwen_image_vae.safetensors",
    "sha256": "a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f",
    "size": 253806246,
}
MOSS_SFT = {
    "repo": "Comfy-Org/MOSS-Image",
    "filename": "diffusion_models/moss_image_sft_int8_convrot.safetensors",
    "dest": "diffusion_models/moss_image_sft_int8_convrot.safetensors",
    "sha256": "b4d1475bc7eeffd7b809e82ea13a1fba1fb85c4e18365af3813722faa5c0fe4f",
    "size": 5413698958,
}
MOSS_TE = {
    "repo": "Comfy-Org/MOSS-Image",
    "filename": "text_encoders/qwen3.5_9b_w4a8_gptq.safetensors",
    "dest": "text_encoders/qwen3.5_9b_w4a8_gptq.safetensors",
    "sha256": "4cc6a1543ad2061806da46f35f90cadb4801dcba246c44782cf42ec0feb6407c",
    "size": 7343591088,
}
MOSS_VAE = {
    "repo": "Comfy-Org/MOSS-Image",
    "filename": "vae/flux2-vae_small.safetensors",
    "dest": "vae/flux2-vae_small.safetensors",
    "sha256": "d8d52ba036475f5fb07c8b435e176d3d97ebfa82f0d1a1c317f9cc1e25bd013b",
    "size": 249521340,
}


def log(msg: str) -> None:
    print(f"[homelab-kompass-downloader] {msg}", flush=True)


def wait_for_models_dir(timeout_s: int = 900) -> Path:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if MODELS_ROOT.is_dir():
            return MODELS_ROOT
        time.sleep(5)
    raise SystemExit(
        f"Timed out waiting for {MODELS_ROOT}. Is the official ComfyUI first-boot copy still running?"
    )


def free_bytes(path: Path) -> int:
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize


def sha256_file(path: Path, expected: str | None) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    digest = h.hexdigest()
    if expected and digest != expected:
        raise SystemExit(f"Checksum mismatch for {path.name}: got {digest}, expected {expected}")
    return digest


def truthy(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on", "accept"}


def accepted_krea_license() -> bool:
    return truthy(os.environ.get("ACCEPT_KREA_LICENSE")) or truthy(os.environ.get("ACCEPT_LICENSE"))


def write_license_note(name: str, text: str) -> None:
    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    (LICENSE_DIR / name).write_text(text, encoding="utf-8")


def download_hf(repo: str, filename: str, dest: Path, expected_sha256: str | None, size: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size == size:
        if expected_sha256:
            log(f"Already present, verifying checksum: {dest}")
            sha256_file(dest, expected_sha256)
        else:
            log(f"Already present: {dest}")
        return
    if dest.exists() and dest.stat().st_size != size:
        log(f"Incomplete file {dest} ({dest.stat().st_size} bytes), re-downloading.")
        dest.unlink()

    available = free_bytes(dest.parent)
    if available < size + RESERVE_BYTES:
        need = (size + RESERVE_BYTES) / (1024**3)
        have = available / (1024**3)
        raise SystemExit(
            f"Not enough free space on /workspace for {filename}: "
            f"need about {need:.1f} GiB including reserve, have {have:.1f} GiB. "
            "Attach a larger volume or a network volume and retry."
        )

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        log("huggingface_hub is missing; installing it with pip...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "huggingface_hub"])
        from huggingface_hub import hf_hub_download  # type: ignore

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN") or None
    log(f"Downloading {repo}/{filename} -> {dest}")
    tmp_name = hf_hub_download(
        repo_id=repo,
        filename=filename,
        token=token,
        resume_download=True,
    )
    src = Path(tmp_name)
    if dest.exists():
        dest.unlink()
    try:
        os.link(src, dest)
    except OSError:
        import shutil

        shutil.copy2(src, dest)
    if expected_sha256:
        sha256_file(dest, expected_sha256)
        log(f"Checksum OK: {dest.name}")
    else:
        log(f"Downloaded (no published checksum to verify): {dest}")


KREA_LICENSE_SUMMARY = """Krea 2 Community License (summary, not a substitute for the full text):
- Worldwide use of Krea 2 Raw and Krea 2 Turbo, including commercial use, only if
  your company-wide trailing-12-month revenue is under USD 1,000,000.
- At or above that threshold you must obtain an Enterprise License from Krea
  (opensource@krea.ai) before any commercial use.
- Deployments must implement content filters or an equivalent review process.
- Keep the name "Krea 2" when referring to the model. This template is not a Krea product.
Full agreement: https://huggingface.co/krea/Krea-2-Turbo/blob/main/LICENSE.pdf
"""

PACKS: dict[str, dict] = {
    "krea2-turbo": {
        "title": "Krea 2 Turbo FP8 (Comfy-Org/Krea-2, originally krea/Krea-2-Turbo)",
        "license": KREA_LICENSE_SUMMARY,
        "requires_krea_license": True,
        "files": [
            {
                "repo": "Comfy-Org/Krea-2",
                "filename": "diffusion_models/krea2_turbo_fp8_scaled.safetensors",
                "dest": "diffusion_models/krea2_turbo_fp8_scaled.safetensors",
                "sha256": "eb4dd8c612cfd10f64f25b057e6e6bbcb5737c94a7372177e456dbf7579502f1",
                "size": 13141730784,
            },
            KREA_TE,
            KREA_VAE,
        ],
    },
    "krea2-raw": {
        "title": "Krea 2 RAW FP8 (Comfy-Org/Krea-2, originally krea/Krea-2-Raw)",
        "license": KREA_LICENSE_SUMMARY,
        "requires_krea_license": True,
        "files": [
            {
                "repo": "Comfy-Org/Krea-2",
                "filename": "diffusion_models/krea2_raw_fp8_scaled.safetensors",
                "dest": "diffusion_models/krea2_raw_fp8_scaled.safetensors",
                "sha256": "48cd5d6c100297968349b41a8e77c6591d1dac18a215807f5f25f59e5c54cd61",
                "size": 13141730784,
            },
            KREA_TE,
            KREA_VAE,
        ],
    },
    "moss": {
        "title": "MOSS-Image SFT int8 (Comfy-Org/MOSS-Image, Apache-2.0)",
        "license": (
            "MOSS-Image is Apache License 2.0. The FLUX.2 small VAE used by the "
            "official templates is also Apache-2.0 (Black Forest Labs). "
            "This is not FLUX.1. Upstream: https://huggingface.co/Comfy-Org/MOSS-Image"
        ),
        "files": [MOSS_SFT, MOSS_TE, MOSS_VAE],
    },
    "moss-edit": {
        "title": "MOSS-Image SFT int8 + edit LoRA (Comfy-Org/MOSS-Image, Apache-2.0)",
        "license": (
            "MOSS-Image is Apache License 2.0. The edit LoRA is the official "
            "Comfy-Org rehost of chinoll/Moss-Image-Edit. Needs ComfyUI 0.43 or later. "
            "Upstream: https://huggingface.co/Comfy-Org/MOSS-Image"
        ),
        "files": [
            MOSS_SFT,
            MOSS_TE,
            MOSS_VAE,
            {
                "repo": "Comfy-Org/MOSS-Image",
                "filename": "loras/moss_image_edit_lora_rank_64_bf16.safetensors",
                "dest": "loras/moss_image_edit_lora_rank_64_bf16.safetensors",
                "sha256": "17a48b8c605dcffdedb92a2b887d18cf316505be90802717669fb6556098dcdf",
                "size": 297382216,
            },
        ],
    },
}


def requested_aliases() -> list[str]:
    raw = os.environ.get("MODELS") or os.environ.get("HK_DOWNLOAD_MODELS") or ""
    if len(sys.argv) > 1 and not raw:
        raw = ",".join(sys.argv[1:])
    parts = [p.strip().lower() for p in raw.replace(";", ",").split(",") if p.strip()]
    return parts


def main() -> int:
    wait_for_models_dir()
    items = requested_aliases()
    if not items:
        log("No MODELS aliases given. Nothing to download.")
        log("Known: krea2-turbo, krea2-raw, moss, moss-edit.")
        return 0

    errors = 0
    unknown: list[str] = []
    seen_files: set[str] = set()

    for item in items:
        if item not in PACKS:
            unknown.append(item)
            continue
        pack = PACKS[item]
        if pack.get("requires_krea_license") and not accepted_krea_license():
            log(
                f"Skipping {item}: set ACCEPT_KREA_LICENSE=yes (or ACCEPT_LICENSE=yes) "
                "to confirm you agree to the Krea 2 Community License. "
                "See https://huggingface.co/krea/Krea-2-Turbo/blob/main/LICENSE.pdf"
            )
            errors += 1
            continue
        write_license_note(f"{item}.txt", pack["title"] + "\n\n" + pack["license"] + "\n")
        log(f"=== {pack['title']} ===")
        log(pack["license"])
        needed = 0
        pending = []
        for f in pack["files"]:
            dest = MODELS_ROOT / f["dest"]
            key = f["dest"]
            if key in seen_files or (dest.exists() and dest.stat().st_size == f["size"]):
                continue
            pending.append(f)
            needed += f["size"]
        if needed and free_bytes(MODELS_ROOT) < needed + RESERVE_BYTES:
            have = free_bytes(MODELS_ROOT) / (1024**3)
            need = (needed + RESERVE_BYTES) / (1024**3)
            log(
                f"Not enough free space for {item}: need about {need:.1f} GiB including reserve, have {have:.1f} GiB."
            )
            errors += 1
            continue
        try:
            for f in pack["files"]:
                dest = MODELS_ROOT / f["dest"]
                download_hf(f["repo"], f["filename"], dest, f.get("sha256"), f["size"])
                seen_files.add(f["dest"])
        except SystemExit as exc:
            log(str(exc))
            errors += 1
        except Exception as exc:  # noqa: BLE001
            log(f"Download failed for {item}: {exc}")
            errors += 1

    if unknown:
        log("Unknown alias(es): " + ", ".join(unknown))
        log("Known: krea2-turbo, krea2-raw, moss, moss-edit.")
        log("Not offered: Qwen Image 2.1 (research license) or any FLUX.1 pack.")
        errors += 1

    if errors:
        log(f"Finished with {errors} error(s).")
        return 1
    log("All requested downloads finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
