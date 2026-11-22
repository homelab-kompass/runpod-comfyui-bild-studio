# Third-party notices

This repository's own scripts, documentation, configuration, and the content-safety node are licensed under the MIT License (see `LICENSE`), Copyright (c) 2026 Michael Weidinger / Homelab-Kompass.

## Official Runpod ComfyUI image

The container image is based on `runpod/comfyui:2.4.1-comfyuiv0.44.0-cuda12.8` (digest pinned in the `Dockerfile`). ComfyUI, ComfyUI-Manager, JupyterLab, FileBrowser, and other software shipped in that base image remain under their own licenses. We do not relicense them.

## Official workflows

The JSON files in `workflows/` are official ComfyUI workflow templates from [Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates), licensed under the MIT License, Copyright (c) 2023-present Comfy Org, copied from commit `8a665db5f05cea82ab8e77a8be70e8c71d536837` (22 November 2026). A copy of that license:

```
MIT License

Copyright (c) 2023-present Comfy Org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Sources are listed in `workflows/README.md`.

## Optional model weights (not included in the image)

The downloader can fetch third-party weights at runtime. Those files are not part of this image. You must follow the license of each model you download.

### Krea 2 Turbo and Krea 2 RAW

Repackaged files come from [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2). Upstream models: [krea/Krea-2-Turbo](https://huggingface.co/krea/Krea-2-Turbo) and [krea/Krea-2-Raw](https://huggingface.co/krea/Krea-2-Raw).

License: [Krea 2 Community License](https://huggingface.co/krea/Krea-2-Turbo/blob/main/LICENSE.pdf). Commercial use is limited to organisations with trailing-12-month company-wide revenue under USD 1,000,000; above that, an Enterprise License from Krea is required before commercial use. Deployments must implement content filters or an equivalent review process. Keep the name "Krea 2" when referring to the model. This template is not a Krea product.

The text encoder (`qwen3vl_4b_fp8_scaled`) and VAE (`qwen_image_vae`) in that pack are dependencies of the official Krea 2 ComfyUI templates, not Qwen Image 2.1 (which is not offered here).

### MOSS-Image SFT and edit LoRA

Repackaged files come from [Comfy-Org/MOSS-Image](https://huggingface.co/Comfy-Org/MOSS-Image) (Apache License 2.0). Upstream includes [OpenMOSS-Team/MOSS-Image-SFT](https://huggingface.co/OpenMOSS-Team/MOSS-Image-SFT) and the edit LoRA rehosted from [chinoll/Moss-Image-Edit](https://huggingface.co/chinoll/Moss-Image-Edit).

The VAE `flux2-vae_small` is the FLUX.2 small autoencoder (Apache License 2.0, Black Forest Labs). It is not FLUX.1.

## Content filter

The node pack `custom_nodes/ComfyUI-HomelabKompass-Safety` is written for this template (MIT, Michael Weidinger / Homelab-Kompass). It is a prompt-side baseline filter. It does not implement Krea's hosted input/output classifiers and does not inspect generated pixels.
