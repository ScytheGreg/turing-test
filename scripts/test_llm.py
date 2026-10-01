from app.llm.deepseek import DeepSeekClient


def main() -> None:
    llm = DeepSeekClient()

    answer = llm.chat(
        "Cześć! Napisz jedno krótkie zdanie na powitanie."
    )

    print("=== DEEPSEEK ===")
    print(answer)


if __name__ == "__main__":
    main()
