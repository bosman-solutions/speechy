# Speechy — text in, speech out, on your speakers.
#
# Pure Python. No Wyoming. No rhasspy base image.
# Just Flask, piper-tts, and PipeWire client tools.

FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        pipewire \
        libspa-0.2-modules \
    && pip install --no-cache-dir \
        flask \
        piper-tts \
        pathvalidate \
        onnxruntime \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app.py .

EXPOSE 5050

CMD ["python3", "app.py"]
