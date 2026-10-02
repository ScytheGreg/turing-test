import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# =========================
# DeepSeek
# =========================

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-flash"


# =========================
# Audio
# =========================

SAMPLE_RATE = 48_000
MIC_DEVICE = 4


# =========================
# Whisper
# =========================

WHISPER_MODEL = "small"
WHISPER_LANGUAGE = "pl"


# =========================
# Piper
# =========================

PIPER_MODELS = {
    "host": BASE_DIR / "models" / "piper" / "pl_PL-bass-high.onnx",
    "alice": BASE_DIR / "models" / "piper" / "pl_PL-gosia-medium.onnx",
    "bob": BASE_DIR / "models" / "piper" / "pl_PL-darkman-medium.onnx",
}

PIPER_LENGTH_SCALE = 1.1

