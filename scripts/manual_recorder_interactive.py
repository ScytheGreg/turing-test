from app.audio.recorder import AudioRecorder


def main() -> None:
    recorder = AudioRecorder()

    input("Naciśnij ENTER, żeby rozpocząć nagrywanie...")

    recorder.start()

    print("🔴 Nagrywanie...")
    input("Naciśnij ENTER, żeby zatrzymać...")

    audio_path = recorder.stop()

    print(f"Nagranie zapisane: {audio_path}")
    print("Plik pozostawiono na dysku do ręcznego sprawdzenia.")


if __name__ == "__main__":
    main()