# syntax=docker/dockerfile:1
# Homelab-Kompass Bild-Studio DE/EN
# Wrapper around the official Runpod ComfyUI image. No model weights are baked in.
#
# CUDA 12.8 (not 13.x): default GPU for this template is an RTX 3090. Official
# Runpod guidance maps pre-Blackwell cards to the CUDA 12.8 image. CUDA 13
# tags exist (2.4.1-comfyuiv0.44.0-cuda13.0 / cuda13.2) but were not verified
# on a 3090 in this pass (no test pod). ComfyUI 0.44.0 meets the >=0.43
# requirement for the MOSS-Image edit template.
# Pin is the latest CUDA 12.8 versioned tag as of 2026-11-17, not the stale
# :cuda12.8 alias (last updated 2026-08-27).
FROM runpod/comfyui:2.4.1-comfyuiv0.44.0-cuda12.8@sha256:1375617a2352d50a5409638fdba7761d33fae7fd6b0ab757ef80beb2e7092769

LABEL org.opencontainers.image.title="Homelab-Kompass Bild-Studio DE/EN" \
      org.opencontainers.image.description="Official Runpod ComfyUI (0.44.0, CUDA 12.8) with Krea 2 and MOSS-Image download-on-start, official workflows, a Krea-license content filter, and secure password defaults. No model weights are included." \
      org.opencontainers.image.source="https://github.com/homelab-kompass/runpod-comfyui-bild-studio" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.authors="Michael Weidinger / Homelab-Kompass" \
      org.opencontainers.image.version="0.1.0"

USER root

COPY scripts/ /opt/homelab-kompass/scripts/
COPY workflows/ /opt/homelab-kompass/workflows/
COPY welcome/ /opt/homelab-kompass/welcome/
COPY custom_nodes/ /opt/homelab-kompass/custom_nodes/
COPY README.md README.de.md README.en.md LICENSE THIRD_PARTY_NOTICES.md VERSION /opt/homelab-kompass/

RUN chmod +x /opt/homelab-kompass/scripts/*.sh \
    && ln -sf /opt/homelab-kompass/scripts/download_models.sh /opt/homelab-kompass/download_models.sh \
    && ln -sf /opt/homelab-kompass/scripts/start.sh /opt/homelab-kompass/start.sh

ENTRYPOINT ["/opt/homelab-kompass/scripts/start.sh"]

EXPOSE 8188 8080 8888 22
