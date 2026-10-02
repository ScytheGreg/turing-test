import subprocess

from app.tts.piper import PiperTTS


tts = PiperTTS()

text = "Cześć. To jest test głosu."

for voice in ("host", "alice", "bob"):
    print(f"Testuję głos: {voice}")

    audio_path = tts.synthesize(
        text,
        voice=voice,
    )

    subprocess.run(
        ["aplay", str(audio_path)],
        check=True,
    )

    audio_path.unlink(missing_ok=True)