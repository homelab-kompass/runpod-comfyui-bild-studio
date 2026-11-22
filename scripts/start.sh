#!/usr/bin/env bash
# Homelab-Kompass wrapper around the official Runpod ComfyUI /start.sh.
# Sets secure password defaults, copies docs, workflows and the content-safety
# node, then execs the official entrypoint so base-image updates keep working.
set -euo pipefail

HK_ROOT="/opt/homelab-kompass"
HK_WS="/workspace/homelab-kompass"
COMFYUI_DIR="${COMFYUI_DIR:-/workspace/runpod-slim/ComfyUI}"
OFFICIAL_START="/start.sh"
FB_DB="/workspace/runpod-slim/filebrowser.db"
SAFETY_SRC="${HK_ROOT}/custom_nodes/ComfyUI-HomelabKompass-Safety"
SAFETY_NAME="ComfyUI-HomelabKompass-Safety"

log() { echo "[homelab-kompass] $*"; }

generate_secret() {
    # Official ComfyUI start requires COMFYUI_PASSWORD of at least 12 characters.
    local len="${1:-20}"
    local secret=""
    if command -v openssl >/dev/null 2>&1; then
        secret="$(openssl rand -base64 48 | tr -d '/+=' | tr -d '\n' | cut -c1-"${len}")"
    else
        secret="$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c "${len}" || true)"
    fi
    printf '%s' "${secret}"
}

# --- Passwords: never write these to a file under /workspace (FileBrowser root).
GENERATED_FB=0
GENERATED_JP=0
GENERATED_CU=0
if [[ -z "${FILEBROWSER_PASSWORD:-}" ]]; then
    FILEBROWSER_PASSWORD="$(generate_secret)"
    export FILEBROWSER_PASSWORD
    GENERATED_FB=1
fi
if [[ -z "${JUPYTER_PASSWORD:-}" ]]; then
    JUPYTER_PASSWORD="$(generate_secret)"
    export JUPYTER_PASSWORD
    GENERATED_JP=1
fi
if [[ -z "${COMFYUI_PASSWORD:-}" ]]; then
    COMFYUI_PASSWORD="$(generate_secret)"
    export COMFYUI_PASSWORD
    GENERATED_CU=1
elif [[ ${#COMFYUI_PASSWORD} -lt 12 ]]; then
    log "COMFYUI_PASSWORD is shorter than 12 characters; the official start script would not start ComfyUI. Generating a new password."
    COMFYUI_PASSWORD="$(generate_secret)"
    export COMFYUI_PASSWORD
    GENERATED_CU=1
else
    export COMFYUI_PASSWORD
fi

mkdir -p "${HK_WS}" /workspace

cp -f "${HK_ROOT}/README.de.md" "${HK_ROOT}/README.en.md" "${HK_ROOT}/README.md" \
      "${HK_ROOT}/LICENSE" "${HK_ROOT}/THIRD_PARTY_NOTICES.md" \
      "${HK_ROOT}/welcome/welcome.md" "${HK_WS}/" 2>/dev/null || true
ln -sfn "${HK_ROOT}/scripts/download_models.sh" "${HK_WS}/download_models.sh"
if [[ ! -e "${HK_WS}/scripts" ]]; then
    ln -sfn "${HK_ROOT}/scripts" "${HK_WS}/scripts"
fi
mkdir -p "${HK_WS}/workflows"
for src in "${HK_ROOT}/workflows/"*.json "${HK_ROOT}/workflows/README.md"; do
    [[ -e "${src}" ]] || continue
    dest="${HK_WS}/workflows/$(basename "${src}")"
    if [[ ! -e "${dest}" ]]; then
        cp "${src}" "${dest}"
    fi
done

# --- Banner (also the only place generated passwords are printed).
echo "================================================================"
echo " Homelab-Kompass Bild-Studio DE/EN"
echo " Author: Michael Weidinger  |  https://homelab-kompass.pages.dev"
echo "----------------------------------------------------------------"
echo " Ports:"
echo "   8188  ComfyUI     — browser login, password below. Do not share the link."
echo "   8080  FileBrowser — user: admin"
echo "   8888  JupyterLab  — token/password below"
echo "   22    SSH         — set PUBLIC_KEY if you need it"
if [[ "${GENERATED_FB}" -eq 1 ]]; then
    echo " FileBrowser password (generated for this start): ${FILEBROWSER_PASSWORD}"
else
    echo " FileBrowser password: using FILEBROWSER_PASSWORD from the environment"
fi
if [[ -f "${FB_DB}" ]]; then
    echo " Note: an existing FileBrowser database was found at ${FB_DB}."
    echo "       The official start script keeps that database; a newly"
    echo "       generated password applies only on a first-time volume."
fi
if [[ "${GENERATED_JP}" -eq 1 ]]; then
    echo " JupyterLab token (generated for this start): ${JUPYTER_PASSWORD}"
else
    echo " JupyterLab token: using JUPYTER_PASSWORD from the environment"
fi
if [[ "${GENERATED_CU}" -eq 1 ]]; then
    echo " ComfyUI password (generated for this start): ${COMFYUI_PASSWORD}"
else
    echo " ComfyUI password: using COMFYUI_PASSWORD from the environment"
fi
echo " Workspace docs: ${HK_WS}"
echo " Models dir:     ${COMFYUI_DIR}/models"
echo " MODELS aliases: krea2-turbo, krea2-raw, moss, moss-edit (none downloaded by default)."
echo " Krea 2 downloads also need ACCEPT_KREA_LICENSE=yes. Weights are never baked into the image."
echo " A prompt filter is enabled (Krea 2 Community License). See THIRD_PARTY_NOTICES.md."
echo " Stop the pod when you are done — a running GPU keeps billing."
echo " A stopped volume disk still incurs storage charges (higher than while running)."
echo " Guide: https://homelab-kompass.pages.dev/ki-gpu-cloud/comfyui-runpod-einsteiger-anleitung/"
echo "================================================================"

install_safety_node() {
    # Refresh on every boot so the license-required filter cannot be left deleted
    # on the volume from a previous session.
    local dest_parent="${COMFYUI_DIR}/custom_nodes"
    local dest="${dest_parent}/${SAFETY_NAME}"
    mkdir -p "${dest_parent}"
    rm -rf "${dest}"
    cp -a "${SAFETY_SRC}" "${dest}"
    log "Installed content-safety node at ${dest}"
}

watch_safety_node() {
    local i
    for i in $(seq 1 900); do
        if [[ -d "${COMFYUI_DIR}/custom_nodes" || -d "${COMFYUI_DIR}/models" ]]; then
            install_safety_node || log "Could not install the content-safety node."
            return 0
        fi
        sleep 0.2
    done
    log "Timed out waiting for ${COMFYUI_DIR}; content-safety node was not installed."
    return 1
}

install_comfy_workflows() {
    local dest="${COMFYUI_DIR}/user/default/workflows/homelab-kompass"
    local i
    for i in $(seq 1 180); do
        if [[ -d "${COMFYUI_DIR}/models" ]]; then
            mkdir -p "${dest}"
            for src in "${HK_ROOT}/workflows/"*.json; do
                [[ -e "${src}" ]] || continue
                local name
                name="$(basename "${src}")"
                if [[ ! -e "${dest}/${name}" ]]; then
                    cp "${src}" "${dest}/${name}"
                fi
            done
            log "Starter workflows available in ${dest}"
            return 0
        fi
        sleep 5
    done
    log "Timed out waiting for ${COMFYUI_DIR}; starter workflows were not copied into ComfyUI."
    return 1
}

run_model_download() {
    local models="${MODELS:-${HK_DOWNLOAD_MODELS:-}}"
    models="$(echo "${models}" | tr -d '[:space:]')"
    if [[ -z "${models}" ]]; then
        log "MODELS / HK_DOWNLOAD_MODELS is empty — no automatic download. Use ${HK_WS}/download_models.sh when you are ready."
        return 0
    fi
    local i
    for i in $(seq 1 180); do
        if [[ -d "${COMFYUI_DIR}/models" ]]; then
            log "Starting model download for: ${models}"
            "${HK_ROOT}/scripts/download_models.sh" || log "Model download finished with errors. Check the logs above."
            return 0
        fi
        sleep 5
    done
    log "Timed out waiting for ${COMFYUI_DIR}; skipped automatic model download."
    return 1
}

run_auto_stop() {
    if [[ -n "${HK_AUTO_STOP_MINUTES:-}" || -n "${HK_IDLE_STOP_MINUTES:-}" ]]; then
        "${HK_ROOT}/scripts/idle_stop.sh" &
        log "Auto-stop watcher started (HK_AUTO_STOP_MINUTES=${HK_AUTO_STOP_MINUTES:-unset}, HK_IDLE_STOP_MINUTES=${HK_IDLE_STOP_MINUTES:-unset})."
    fi
}

# If this volume already has ComfyUI, install the filter before the official start.
if [[ -d "${COMFYUI_DIR}/custom_nodes" || -d "${COMFYUI_DIR}/models" ]]; then
    install_safety_node || true
fi

watch_safety_node &
install_comfy_workflows &
run_model_download &
run_auto_stop

if [[ ! -x "${OFFICIAL_START}" && ! -f "${OFFICIAL_START}" ]]; then
    log "ERROR: official ${OFFICIAL_START} is missing. Cannot start ComfyUI."
    exit 1
fi

exec "${OFFICIAL_START}"
