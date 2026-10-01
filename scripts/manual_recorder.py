from app.audio.recorder import record


def main() -> None:
    print("Mów przez 5 sekund...")

    output_path = record(5)

    print(f"Nagranie zapisane: {output_path}")


if __name__ == "__main__":
    main()
