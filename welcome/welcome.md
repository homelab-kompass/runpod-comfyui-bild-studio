# Homelab-Kompass Bild-Studio — checklist

**DE**

1. Logs öffnen und ganz nach oben scrollen. ComfyUI-, FileBrowser- und Jupyter-Zugangsdaten notieren (wenn du keine eigenen gesetzt hast).
2. **Connect → Port 8188** und das ComfyUI-Passwort aus den Logs eingeben. Den Link nicht öffentlich teilen.
3. Workflows: `/workspace/homelab-kompass/workflows/` und in ComfyUI unter `user/default/workflows/homelab-kompass/`.
4. Modelle bewusst laden, z. B. `ACCEPT_KREA_LICENSE=yes /workspace/homelab-kompass/download_models.sh krea2-turbo` oder `/workspace/homelab-kompass/download_models.sh moss-edit`.
5. Ergebnisse sichern, danach den Pod **stoppen**. Ohne Netzwerk-Volume für eine längere Pause **beenden**.

Begleitartikel: https://homelab-kompass.pages.dev/ki-gpu-cloud/comfyui-runpod-einsteiger-anleitung/

**EN**

1. Open the logs and scroll to the very top. Copy the ComfyUI, FileBrowser and Jupyter secrets (unless you set your own).
2. **Connect → port 8188** and enter the ComfyUI password from the logs. Do not share that link.
3. Workflows: `/workspace/homelab-kompass/workflows/` and in ComfyUI under `user/default/workflows/homelab-kompass/`.
4. Download weights on purpose, e.g. `ACCEPT_KREA_LICENSE=yes /workspace/homelab-kompass/download_models.sh krea2-turbo` or `/workspace/homelab-kompass/download_models.sh moss-edit`.
5. Save your outputs, then **stop** the pod. For a longer pause without a network volume, **terminate** it.

Guide: https://homelab-kompass.pages.dev/ki-gpu-cloud/comfyui-runpod-einsteiger-anleitung/

Author: Michael Weidinger / Homelab-Kompass
