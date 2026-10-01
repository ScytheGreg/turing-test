from app.audio.recorder import record
from app.stt.whisper import WhisperSTT


def main() -> None:
    print("Ładowanie Whisper...")
    stt = WhisperSTT()
    print("Whisper gotowy.")

    print("Mów przez 5 sekund...")
    audio_path = record(5)

    print("Rozpoznawanie mowy...")
    text = stt.transcribe(audio_path)

    print(f"\nTY: {text}")

    audio_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
