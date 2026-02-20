#!/bin/bash
#
# Download open-source Piper voice models from Hugging Face.
# All models are MIT/Apache-2.0 licensed via the rhasspy/piper-voices repo.
#
# Usage: ./download-voices.sh [voice_name ...]
#   No args = download the recommended starter set
#   With args = download only the specified voices
#
# Models are saved to ./voices/

set -euo pipefail

VOICE_DIR="${VOICE_DIR:-./voices}"
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

mkdir -p "$VOICE_DIR"

# Available voices: name -> path under BASE_URL
declare -A VOICES=(
  # --- Recommended starter set ---
  # Amy (US female, medium quality) — clear, natural, great default
  ["en_US-amy-medium"]="en/en_US/amy/medium"
  # Lessac (US female, medium) — expressive, popular in AI demos
  ["en_US-lessac-medium"]="en/en_US/lessac/medium"
  # Ryan (US male, medium) — solid male voice
  ["en_US-ryan-medium"]="en/en_US/ryan/medium"
  # Arctic (US, medium) — multi-speaker research corpus voice
  ["en_US-arctic-medium"]="en/en_US/arctic/medium"

  # --- Additional quality voices ---
  # Lessac high quality (larger model, slower, better)
  ["en_US-lessac-high"]="en/en_US/lessac/high"
  # Ryan high quality
  ["en_US-ryan-high"]="en/en_US/ryan/high"
  # Joe (US male, medium)
  ["en_US-joe-medium"]="en/en_US/joe/medium"
  # Kristin (US female, medium)
  ["en_US-kristin-medium"]="en/en_US/kristin/medium"
  # Danny (US male, low) — lightweight
  ["en_US-danny-low"]="en/en_US/danny/low"
  # LJSpeech (US female, medium) — classic TTS training dataset voice
  ["en_US-ljspeech-medium"]="en/en_US/ljspeech/medium"
  # HFC Female (US, medium)
  ["en_US-hfc_female-medium"]="en/en_US/hfc_female/medium"
  # HFC Male (US, medium)
  ["en_US-hfc_male-medium"]="en/en_US/hfc_male/medium"

  # --- British English ---
  # Alan (GB male, medium)
  ["en_GB-alan-medium"]="en/en_GB/alan/medium"
  # Jenny DioCo (GB female, medium)
  ["en_GB-jenny_dioco-medium"]="en/en_GB/jenny_dioco/medium"
  # Northern English Male (GB, medium)
  ["en_GB-northern_english_male-medium"]="en/en_GB/northern_english_male/medium"
)

# Default starter set if no args given
DEFAULT_VOICES=(
  "en_US-amy-medium"
  "en_US-lessac-medium"
  "en_US-ryan-medium"
  "en_US-joe-medium"
)

download_voice() {
  local name="$1"
  local url_path="${VOICES[$name]}"

  if [[ -z "$url_path" ]]; then
    echo "Unknown voice: $name"
    echo "Available: ${!VOICES[*]}"
    return 1
  fi

  local model_url="${BASE_URL}/${url_path}/${name}.onnx?download=true"
  local config_url="${BASE_URL}/${url_path}/${name}.onnx.json?download=true"
  local model_file="${VOICE_DIR}/${name}.onnx"
  local config_file="${VOICE_DIR}/${name}.onnx.json"

  if [[ -f "$model_file" ]]; then
    echo "  ✓ ${name} (already downloaded)"
    return 0
  fi

  echo "  ↓ ${name}..."
  curl -sL "$model_url" -o "$model_file"
  curl -sL "$config_url" -o "$config_file"
  echo "  ✓ ${name}"
}

# Determine which voices to download
if [[ $# -gt 0 ]]; then
  TARGETS=("$@")
else
  TARGETS=("${DEFAULT_VOICES[@]}")
fi

echo "Downloading ${#TARGETS[@]} voice(s) to ${VOICE_DIR}/"
echo ""

for voice in "${TARGETS[@]}"; do
  download_voice "$voice"
done

echo ""
echo "Done. Restart Speechy to pick up new voices."
