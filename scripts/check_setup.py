from pathlib import Path
import os
import sys


BASE_DIR = Path(__file__).resolve().parent.parent

OK = "✓"
FAIL = "✗"


def check(name: str, func) -> bool:
    try:
        result = func()
        print(f"{OK} {name}: {result}")
        return True
    except Exception as exc:
        print(f"{FAIL} {name}: {exc}")
        return False


def check_python():
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def check_cuda():
    import ctranslate2

    count = ctranslate2.get_cuda_device_count()
    if count < 1:
        raise RuntimeError("CTranslate2 nie wykrywa GPU CUDA.")
    return f"wykryto {count} GPU"


def check_microphone():
    import sounddevice as sd
    from app.config import MIC_CHANNELS, MIC_DEVICE_NAME

    device = sd.query_devices(MIC_DEVICE_NAME, kind="input")

    if device["max_input_channels"] < MIC_CHANNELS:
        raise RuntimeError(
            f"mikrofon ma {device['max_input_channels']} kanałów wejściowych, "
            f"wymagane {MIC_CHANNELS}"
        )

    return (
        f"{device['name']} "
        f"(input channels: {device['max_input_channels']})"
    )


def check_piper():
    from app.config import PIPER_MODELS

    missing = []

    for voice, path in PIPER_MODELS.items():
        if not path.exists():
            missing.append(f"{voice}: {path}")

    if missing:
        raise RuntimeError(
            "brak modeli:\n" + "\n".join(missing)
        )

    return ", ".join(PIPER_MODELS.keys())


def check_deepseek():
    from app.config import DEEPSEEK_API_KEY

    if not DEEPSEEK_API_KEY:
        raise RuntimeError("brak DEEPSEEK_API_KEY w .env")

    return "klucz ustawiony"


def check_app_import():
    import app.main

    return "app.main zaimportowany poprawnie"


def main():
    print()
    print("=== TURING TEST — CHECK SETUP ===")
    print()

    checks = [
        ("Python", check_python),
        ("CUDA / GPU", check_cuda),
        ("Mikrofon", check_microphone),
        ("Modele Piper", check_piper),
        ("DeepSeek API", check_deepseek),
        ("Aplikacja FastAPI", check_app_import),
    ]

    results = []

    for name, func in checks:
        results.append(check(name, func))

    print()
    print("=================================")

    if all(results):
        print(f"{OK} Wszystko wygląda poprawnie.")
        print()
        print("Możesz uruchomić aplikację:")
        print("uv run uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return 0

    print(f"{FAIL} Wykryto problemy. Nie uruchamiaj jeszcze aplikacji.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())