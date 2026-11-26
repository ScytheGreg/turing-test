import sys

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
