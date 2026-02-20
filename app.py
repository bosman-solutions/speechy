"""
Speechy — A simple HTTP API that turns text into speech on your speakers.

How it works:
  1. You send text + a voice name via HTTP
  2. Speechy runs the piper CLI to generate a WAV file
  3. Speechy plays the WAV through PipeWire
  4. The temp file gets cleaned up

That's it. No protocols, no streaming, no magic.
"""

from flask import Flask, request, jsonify
import subprocess
import tempfile
import glob
import json
import os
import threading

app = Flask(__name__)

# --- Config (all from environment, with sane defaults) ---
VOICE_DIR = os.environ.get("VOICE_DIR", "/data")
DEFAULT_VOICE = os.environ.get("DEFAULT_VOICE", "en_US-amy-medium")

# Only one thing talks through the speakers at a time
play_lock = threading.Lock()


# --- Routes ---

@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/voices")
def voices():
    """List every .onnx voice model in the voice directory."""
    found = []
    for onnx_file in sorted(glob.glob(os.path.join(VOICE_DIR, "*.onnx"))):
        name = os.path.basename(onnx_file).replace(".onnx", "")
        found.append(name)
    return jsonify(voices=found)


@app.route("/speak", methods=["GET", "POST"])
def speak():
    """
    Synthesize text and play it on the speakers.

    GET  /speak?text=Hello&voice=mssam
    POST /speak {"text": "Hello", "voice": "mssam"}
    """
    # Get text and voice from either GET params or POST JSON
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        text = data.get("text", "")
        voice = data.get("voice", DEFAULT_VOICE)
    else:
        text = request.args.get("text", "")
        voice = request.args.get("voice", DEFAULT_VOICE)

    if not text:
        return jsonify(error="No text provided"), 400

    # Make sure the voice model exists
    model_path = os.path.join(VOICE_DIR, f"{voice}.onnx")
    if not os.path.exists(model_path):
        available = [
            f.replace(".onnx", "")
            for f in os.listdir(VOICE_DIR)
            if f.endswith(".onnx")
        ]
        return jsonify(error=f"Voice '{voice}' not found", available=available), 404

    # Only one request plays at a time (no overlapping audio)
    with play_lock:
        wav_path = None
        try:
            # Step 1: Generate WAV with piper
            wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            wav_path = wav_file.name
            wav_file.close()

            result = subprocess.run(
                ["piper", "--model", model_path, "--output_file", wav_path],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )

            if result.returncode != 0:
                return jsonify(error="Piper failed", details=result.stderr.decode()), 500

            # Step 2: Play it through the speakers
            subprocess.run(["pw-play", wav_path], check=True, timeout=30)

            return jsonify(status="played", voice=voice, text=text)

        except Exception as e:
            return jsonify(error=str(e)), 500

        finally:
            # Step 3: Clean up the temp file
            if wav_path and os.path.exists(wav_path):
                os.unlink(wav_path)


# --- Start ---

if __name__ == "__main__":
    print(f"Speechy starting up")
    print(f"  Voice dir:     {VOICE_DIR}")
    print(f"  Default voice: {DEFAULT_VOICE}")
    print(
        f"  Voices found:  {sorted(f.replace('.onnx','') for f in os.listdir(VOICE_DIR) if f.endswith('.onnx'))}"
    )
    app.run(host="0.0.0.0", port=int(os.environ.get("LISTEN_PORT", "5050")))
