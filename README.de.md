# Bild-Studio DE/EN (Homelab-Kompass)

Vorlage für [Runpod](https://runpod.io), gebaut von Michael Weidinger / Homelab-Kompass. Sie startet ComfyUI im Browser und lädt **Krea 2** und **MOSS-Image** erst auf Anfrage. Im Image stecken **keine Modellgewichte**.

English: [README.en.md](README.en.md)

## Was enthalten ist

- Offizielles Runpod-ComfyUI-Image `2.4.1-comfyuiv0.44.0-cuda12.8` (Digest im `Dockerfile`), ComfyUI **0.44.0**. Das reicht für die MOSS-Image-Bearbeitung, die ComfyUI **0.43** oder neuer braucht.
- CUDA **12.8**, weil die empfohlene Karte eine **RTX 3090** ist. Runpod ordnet Karten vor Blackwell der CUDA-12.8-Linie zu. CUDA-13-Varianten desselben ComfyUI-Stands gibt es, sind hier aber nicht die Vorgabe.
- Automatische Passwörter für ComfyUI (Port 8188), FileBrowser (8080) und Jupyter (8888), wenn du keine eigenen setzt. Sie stehen **ganz am Anfang der Pod-Logs**.
- Offizielle ComfyUI-Workflows (MIT, Comfy Org) für **Krea 2 Turbo Text-to-Image**, **MOSS-Image Text-to-Image** und **MOSS-Image Image Edit**.
- Ein Prompt-Filter (keine Gewichte) als Grundschutz gemäß der **Krea 2 Community License**.
- Downloader über `MODELS` bzw. `download_models.sh`. Standard: es wird nichts geladen.

Nicht enthalten: Qwen Image 2.1 (nur Forschungslizenz) und jedes FLUX.1-Modell. Die VAE von MOSS-Image ist die **FLUX.2**-VAE unter Apache 2.0, nicht FLUX.1.

## Schnellstart

1. Pod mit einer **RTX 3090** (24 GB) oder einer vergleichbaren 24-GB-Karte starten. Empfohlenes Volume: etwa **150 GB**.
2. Logs öffnen und ganz nach oben scrollen: ComfyUI-, FileBrowser- und Jupyter-Passwort notieren.
3. **Connect → Port 8188**, Passwort eingeben. Den Proxy-Link nicht teilen.
4. Gewichte laden, zum Beispiel:

```bash
# Krea 2 Turbo (braucht die Lizenzbestätigung)
ACCEPT_KREA_LICENSE=yes /workspace/homelab-kompass/download_models.sh krea2-turbo

# Optional zusätzlich Krea 2 RAW
ACCEPT_KREA_LICENSE=yes /workspace/homelab-kompass/download_models.sh krea2-raw

# MOSS-Image SFT inkl. Edit-LoRA
/workspace/homelab-kompass/download_models.sh moss-edit
```

Oder vor dem Start setzen: `MODELS=krea2-turbo,moss-edit` und für Krea 2 zusätzlich `ACCEPT_KREA_LICENSE=yes`.

5. In ComfyUI die Workflows unter `user/default/workflows/homelab-kompass/` oder `/workspace/homelab-kompass/workflows/` öffnen.
6. Ergebnisse sichern, dann den Pod **stoppen**. Ohne Netzwerk-Volume für eine längere Pause **beenden**. Gestoppter Volume-Speicher kostet weiter, und zwar mehr als im Lauf.

Begleitartikel: https://homelab-kompass.pages.dev/ki-gpu-cloud/comfyui-runpod-einsteiger-anleitung/

## Modelle und Speicher

Größen laut Hugging-Face-LFS, geprüft am 22. November 2026, gerundet:

| Alias | Inhalt | Ungefähre Größe |
| --- | --- | --- |
| `krea2-turbo` | `krea2_turbo_fp8_scaled`, `qwen3vl_4b_fp8_scaled`, `qwen_image_vae` | 18,6 GB |
| `krea2-raw` | `krea2_raw_fp8_scaled` plus dieselben Text-Encoder und VAE | 18,6 GB (Encoder/VAE werden nicht doppelt geladen) |
| `moss` | `moss_image_sft_int8_convrot`, `qwen3.5_9b_w4a8_gptq`, `flux2-vae_small` | 13,0 GB |
| `moss-edit` | wie `moss`, plus `moss_image_edit_lora_rank_64_bf16` | 13,3 GB |

Alles zusammen liegt bei etwa 45 GB, plus Spielraum. Deshalb das 150-GB-Volume. Quellen: [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) und [Comfy-Org/MOSS-Image](https://huggingface.co/Comfy-Org/MOSS-Image).

Für **Krea 2 RAW** gibt es keine offizielle eigene Text-to-Image-Vorlage. Nimm den offiziellen Turbo-Workflow, tausche den Checkpoint gegen `krea2_raw_fp8_scaled.safetensors`, stelle 52 Schritte und CFG 4,5 ein und ersetze `ConditioningZeroOut` durch eine negative Prompt-Kodierung (darf leer bleiben). Das folgt der Beschreibung in der [Krea-2-RAW-Diskussion](https://huggingface.co/krea/Krea-2-Raw/discussions/2).

## Lizenzen — bitte lesen

**Krea 2** steht unter der [Krea 2 Community License](https://huggingface.co/krea/Krea-2-Turbo/blob/main/LICENSE.pdf). Kurz (kein Ersatz für den Vertragstext):

- Weltweite Nutzung, auch kommerziell, nur wenn der unternehmensweite Umsatz der letzten 12 Monate unter **1.000.000 USD** liegt.
- Darüber brauchst du vor jeder kommerziellen Nutzung eine Enterprise-Lizenz von Krea (`opensource@krea.ai`).
- Wer die Modelle bereitstellt, muss **Content-Filter** oder ein gleichwertiges Prüfverfahren einsetzen.
- Den Namen **Krea 2** beibehalten. Diese Vorlage ist kein Produkt von Krea.

Der Downloader lädt Krea-2-Pakete erst nach `ACCEPT_KREA_LICENSE=yes` (oder `ACCEPT_LICENSE=yes`). Ein Prompt-Filter ist standardmäßig aktiv. Er ist ein Grundschutz, kein vollständiger Bildprüfer. Abschalten geht nur mit `HK_DISABLE_CONTENT_FILTER=yes` und kann die Lizenz verletzen.

**MOSS-Image** (SFT und Edit-LoRA) steht unter **Apache 2.0**. Die FLUX.2-Small-VAE ebenfalls unter Apache 2.0.

Ausführlicher: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Umgebungsvariablen

| Variable | Wirkung |
| --- | --- |
| `COMFYUI_PASSWORD` | ComfyUI-Login, mindestens 12 Zeichen. Sonst wird eines erzeugt. |
| `FILEBROWSER_PASSWORD` / `JUPYTER_PASSWORD` | Sonst jeweils erzeugt und nur in die Logs geschrieben. |
| `MODELS` oder `HK_DOWNLOAD_MODELS` | Komma-getrennte Aliase, Download nach dem ersten Start. |
| `ACCEPT_KREA_LICENSE` | `yes`, bevor Krea-2-Pakete geladen werden. |
| `HF_TOKEN` | Nur nötig, wenn Hugging Face eine Anmeldung verlangt. Die genannten Dateien waren am 22.11.2026 frei ladbar. |
| `HK_DISABLE_CONTENT_FILTER` | Filter aus. Für Krea 2 lizenzkritisch. |
| `HK_AUTO_STOP_MINUTES` / `HK_IDLE_STOP_MINUTES` | Optionaler Auto-Stopp, braucht `RUNPOD_API_KEY` als Secret. |

## Sicherheit

Port 8188 verlangt ein Passwort im Browser. Die Zugangsdaten stehen ganz am Anfang der Logs; eine später geöffnete Log-Ansicht kann diese Zeilen verpassen. Den Proxy-Link nicht öffentlich teilen. Geheimnisse gehören in Runpod Secrets, nicht in sichtbare Umgebungsvariablen eines öffentlichen Templates.

## Image

`ghcr.io/homelab-kompass/runpod-comfyui-bild-studio:v0.1.0`

Autor: Michael Weidinger / Homelab-Kompass.
