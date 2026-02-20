# Speechy 🔊

A dead-simple HTTP API that turns text into speech on your speakers.

## What it is

One container. Text goes in, speech comes out of your speakers. No Wyoming protocol, no rhasspy dependencies, no black boxes. Just Flask, piper-tts, and PipeWire.

## Setup

1. Download some voices: `./download-voices.sh`
2. `docker compose up -d`
3. That's it.

## Usage

```bash
# Say something
curl http://localhost:5050/speak -d '{"text": "Hello world", "voice": "mssam"}'

# Use the default voice
curl http://localhost:5050/speak -d '{"text": "Hello world"}'

# Use GET if you prefer
curl "http://localhost:5050/speak?text=Hello&voice=hal"

# List available voices
curl http://localhost:5050/voices

# Health check
curl http://localhost:5050/health
```

## Voices

Use the included download script to grab open-source Piper voices from Hugging Face:

```bash
# Download the starter set (amy, lessac, ryan, joe)
./download-voices.sh

# Download specific voices
./download-voices.sh en_US-amy-medium en_GB-alan-medium

# Download all available voices
./download-voices.sh $(grep -oP 'en_\w+-\w+-\w+' download-voices.sh | sort -u)
```

### Recommended voices

| Voice | Quality | Description |
|-------|---------|-------------|
| `en_US-amy-medium` | Medium | US female, clear and natural — great default |
| `en_US-lessac-medium` | Medium | US female, expressive — popular in AI demos |
| `en_US-ryan-medium` | Medium | US male, solid general-purpose |
| `en_US-joe-medium` | Medium | US male, warm tone |
| `en_US-lessac-high` | High | US female, best quality (larger model) |
| `en_US-ryan-high` | High | US male, best quality (larger model) |
| `en_GB-alan-medium` | Medium | British male |
| `en_GB-jenny_dioco-medium` | Medium | British female |

All voices are MIT/Apache-2.0 licensed from the [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices) repository.

You can also drop any Piper `.onnx` + `.onnx.json` pair into `./voices/` manually. Custom voices can be trained with [piper-recording-studio](https://github.com/rhasspy/piper-recording-studio).

## How it works

```
You → HTTP POST /speak → Speechy → piper CLI → WAV file → pw-play → Your speakers
```

1. Speechy receives your text via HTTP
2. Runs `piper --model <voice>.onnx --output_file temp.wav` with your text on stdin
3. Plays the WAV through PipeWire (`pw-play`)
4. Deletes the temp file
5. Returns JSON confirmation

## Requirements

- Docker + Docker Compose
- PipeWire running on the host (for audio playback)
- Host user UID 1000 (or adjust `user:` in docker-compose.yml)

## Environment variables

| Variable | Default | What it does |
|----------------|---------|----------------------------------|
| `VOICE_DIR` | `/data` | Where voice models live |
| `DEFAULT_VOICE`| `en_US-amy-medium` | Voice used when none specified |
| `LISTEN_HOST` | `0.0.0.0` | Bind address (`127.0.0.1` for localhost only) |
| `LISTEN_PORT` | `5050` | HTTP server port |

## Notes

- Only one request plays at a time (requests queue up, no overlapping audio)
- Speechy runs the piper CLI directly — no protocols, no middleware
- The full stack: Python 3.12, Flask, piper-tts, PipeWire client. That's it.

## License

MIT
