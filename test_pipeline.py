import os
import wave
import tempfile

import httpx
import sounddevice as sd
from dotenv import load_dotenv
from faster_whisper import WhisperModel

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise RuntimeError("Brak DEEPSEEK_API_KEY w pliku .env")


# =========================
# KONFIGURACJA
# =========================

SAMPLE_RATE = 48000
RECORD_SECONDS = 5

MIC_DEVICE = 4

WHISPER_MODEL = "small"

PIPER_MODEL = (
    "models/piper/pl_PL-gosia-medium.onnx"
)

PIPER_LENGTH_SCALE = "1.1"


# =========================
# WHISPER
# =========================

print("Ładowanie Whisper...")

whisper = WhisperModel(
    WHISPER_MODEL,
    device="cuda",
    compute_type="float16",
)

print("Whisper gotowy.")


# =========================
# NAGRYWANIE
# =========================

print()
print(f"Mów przez {RECORD_SECONDS} sekund...")

audio = sd.rec(
    int(RECORD_SECONDS * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    device=MIC_DEVICE,
)

sd.wait()

print("Nagrywanie zakończone.")


# =========================
# ZAPIS WAV
# =========================

with tempfile.NamedTemporaryFile(
    suffix=".wav",
    delete=False,
) as f:
    wav_path = f.name

with wave.open(wav_path, "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(SAMPLE_RATE)

    pcm = (audio[:, 0] * 32767).astype("int16")
    wav.writeframes(pcm.tobytes())


# =========================
# STT
# =========================

print("Rozpoznawanie mowy...")

segments, info = whisper.transcribe(
    wav_path,
    language="pl",
)

text = " ".join(
    segment.text.strip()
    for segment in segments
).strip()

print()
print("TY:")
print(text)


if not text:
    raise RuntimeError("Whisper nie rozpoznał żadnej wypowiedzi.")


# =========================
# DEEPSEEK
# =========================

print()
print("Pytamy DeepSeek...")

response = httpx.post(
    "https://api.deepseek.com/chat/completions",
    headers={
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek-flash",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Jesteś uczestnikiem eksperymentu Turinga. "
                    "Rozmawiaj naturalnie po polsku. "
                    "Odpowiadaj krótko, maksymalnie 2-3 zdania. "
                    "Nie wspominaj, że jesteś modelem językowym."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        "stream": False,
    },
    timeout=60,
)

response.raise_for_status()

data = response.json()

answer = data["choices"][0]["message"]["content"].strip()

print()
print("DEEPSEEK:")
print(answer)


# =========================
# PIPER
# =========================

print()
print("Generowanie mowy...")

with tempfile.NamedTemporaryFile(
    suffix=".wav",
    delete=False,
) as f:
    output_wav = f.name

piper_command = [
    "piper",
    "-m",
    PIPER_MODEL,
    "--length-scale",
    PIPER_LENGTH_SCALE,
    "-f",
    output_wav,
]

import subprocess

subprocess.run(
    piper_command,
    input=answer,
    text=True,
    check=True,
)

print("Odtwarzanie...")

subprocess.run(
    ["aplay", output_wav],
    check=True,
)

print()
print("Gotowe.")
