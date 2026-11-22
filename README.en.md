# Bild-Studio DE/EN (Homelab-Kompass)

A [Runpod](https://runpod.io) template by Michael Weidinger / Homelab-Kompass. It starts ComfyUI in the browser and downloads **Krea 2** and **MOSS-Image** only when you ask for them. The image ships **no model weights**.

Deutsch: [README.de.md](README.de.md)

## What is included

- Official Runpod ComfyUI image `2.4.1-comfyuiv0.44.0-cuda12.8` (digest pinned in the `Dockerfile`), ComfyUI **0.44.0**. That meets the **0.43+** requirement for MOSS-Image edit.
- CUDA **12.8**, because the recommended GPU is an **RTX 3090**. Runpod maps pre-Blackwell cards to the CUDA 12.8 line. CUDA 13 builds of the same ComfyUI version exist but are not the default here.
- Auto-generated passwords for ComfyUI (port 8188), FileBrowser (8080) and Jupyter (8888) when you do not set your own. They are printed **at the very start of the pod logs**.
- Official ComfyUI workflows (MIT, Comfy Org) for **Krea 2 Turbo text-to-image**, **MOSS-Image text-to-image** and **MOSS-Image image edit**.
- A prompt filter (no weights) as a baseline safeguard required by the **Krea 2 Community License**.
- A downloader via `MODELS` or `download_models.sh`. By default nothing is fetched.

Not included: Qwen Image 2.1 (research licence only) and any FLUX.1 model. The VAE used by MOSS-Image is the Apache-2.0 **FLUX.2** VAE, not FLUX.1.

## Quick start

1. Start a pod on an **RTX 3090** (24 GB) or a similar 24 GB card. Recommended volume size: about **150 GB**.
2. Open the logs and scroll to the very top. Copy the ComfyUI, FileBrowser and Jupyter secrets.
3. **Connect → port 8188** and enter the ComfyUI password. Do not share the proxy link.
4. Download weights, for example:

```bash
# Krea 2 Turbo (requires the licence acknowledgement)
ACCEPT_KREA_LICENSE=yes /workspace/homelab-kompass/download_models.sh krea2-turbo

# Optionally also Krea 2 RAW
ACCEPT_KREA_LICENSE=yes /workspace/homelab-kompass/download_models.sh krea2-raw

# MOSS-Image SFT including the edit LoRA
/workspace/homelab-kompass/download_models.sh moss-edit
```

Or set `MODELS=krea2-turbo,moss-edit` before start, plus `ACCEPT_KREA_LICENSE=yes` for Krea 2.

5. In ComfyUI, open the workflows under `user/default/workflows/homelab-kompass/` or `/workspace/homelab-kompass/workflows/`.
6. Save your outputs, then **stop** the pod. For a longer pause without a network volume, **terminate** it. A stopped volume disk still incurs storage charges, at a higher rate than while running.

Guide: https://homelab-kompass.pages.dev/ki-gpu-cloud/comfyui-runpod-einsteiger-anleitung/

## Models and disk

Sizes from Hugging Face LFS metadata, retrieved 22 November 2026, rounded:

| Alias | Contents | Approx. size |
| --- | --- | --- |
| `krea2-turbo` | `krea2_turbo_fp8_scaled`, `qwen3vl_4b_fp8_scaled`, `qwen_image_vae` | 18.6 GB |
| `krea2-raw` | `krea2_raw_fp8_scaled` plus the same text encoder and VAE | 18.6 GB (encoder/VAE are not fetched twice) |
| `moss` | `moss_image_sft_int8_convrot`, `qwen3.5_9b_w4a8_gptq`, `flux2-vae_small` | 13.0 GB |
| `moss-edit` | same as `moss`, plus `moss_image_edit_lora_rank_64_bf16` | 13.3 GB |

All packs together are about 45 GB, plus headroom, which is why the volume is 150 GB. Sources: [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) and [Comfy-Org/MOSS-Image](https://huggingface.co/Comfy-Org/MOSS-Image).

There is no official dedicated text-to-image template for **Krea 2 RAW**. Use the official Turbo workflow, switch the checkpoint to `krea2_raw_fp8_scaled.safetensors`, set 52 steps and CFG 4.5, and replace `ConditioningZeroOut` with a negative prompt encode (it may be empty). That follows the note in the [Krea 2 RAW discussion](https://huggingface.co/krea/Krea-2-Raw/discussions/2).

## Licences — please read

**Krea 2** is under the [Krea 2 Community License](https://huggingface.co/krea/Krea-2-Turbo/blob/main/LICENSE.pdf). In short (not a substitute for the agreement):

- Worldwide use, including commercial use, only if trailing-12-month company-wide revenue is under **USD 1,000,000**.
- At or above that threshold you must obtain an Enterprise License from Krea (`opensource@krea.ai`) before any commercial use.
- Deployments must implement **content filters** or an equivalent review process.
- Keep the name **Krea 2** when referring to the model. This template is not a Krea product.

The downloader fetches Krea 2 packs only after `ACCEPT_KREA_LICENSE=yes` (or `ACCEPT_LICENSE=yes`). A prompt filter is on by default. It is a baseline, not a full image moderator. Disabling it (`HK_DISABLE_CONTENT_FILTER=yes`) may breach the licence.

**MOSS-Image** (SFT and the edit LoRA) is **Apache 2.0**. The FLUX.2 small VAE is also Apache 2.0.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

## Environment variables

| Variable | Effect |
| --- | --- |
| `COMFYUI_PASSWORD` | ComfyUI login, at least 12 characters. Generated if unset. |
| `FILEBROWSER_PASSWORD` / `JUPYTER_PASSWORD` | Generated if unset; printed only in the logs. |
| `MODELS` or `HK_DOWNLOAD_MODELS` | Comma-separated aliases, downloaded after first boot. |
| `ACCEPT_KREA_LICENSE` | `yes` before any Krea 2 pack is downloaded. |
| `HF_TOKEN` | Only if Hugging Face requires login. The listed files were freely downloadable on 22 Nov 2026. |
| `HK_DISABLE_CONTENT_FILTER` | Turns the filter off. Licence-sensitive for Krea 2. |
| `HK_AUTO_STOP_MINUTES` / `HK_IDLE_STOP_MINUTES` | Optional auto-stop; needs `RUNPOD_API_KEY` as a secret. |

## Security

Port 8188 asks for a password in the browser. Secrets are printed at the very start of the logs; a later log view can miss those lines. Do not share the proxy link. Put secrets in Runpod Secrets, not in visible environment variables of a public template.

## Image

`ghcr.io/homelab-kompass/runpod-comfyui-bild-studio:v0.1.0`

Author: Michael Weidinger / Homelab-Kompass.
