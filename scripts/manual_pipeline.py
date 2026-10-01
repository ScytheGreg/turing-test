import subprocess

from app.conversation.pipeline import ConversationPipeline


def main() -> None:
    print("Ładowanie pipeline'u...")
    pipeline = ConversationPipeline()

    print("Pipeline gotowy.")
    print("Mów przez 5 sekund...")

    user_text, answer, audio_path = pipeline.run_once()

    print(f"\nTY: {user_text}")
    print(f"AI: {answer}")
    print(f"\nAudio: {audio_path}")

    subprocess.run(
        ["aplay", str(audio_path)],
        check=True,
    )

    audio_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
