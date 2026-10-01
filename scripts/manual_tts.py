import subprocess

from app.tts.piper import PiperTTS


def main() -> None:
    tts = PiperTTS()

    text = "Cześć! To jest test syntezy mowy."

    print("Generowanie mowy...")
    audio_path = tts.synthesize(text)

    print(f"Wygenerowano: {audio_path}")

    subprocess.run(
        ["aplay", str(audio_path)],
        check=True,
    )

    audio_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
