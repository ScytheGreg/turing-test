# Project Overview

## Main idea

This project is a Polish-language Turing test demonstration. A host runs two
conversations, one with an AI persona and one with a human participant. Both are
shown side by side on a display so an audience can compare them and decide
which conversation involves the AI.

## How it works

- The host uses the `/participant` interface to manage the AI conversation.
  The host enters prompts as text.
- The backend sends each prompt and its conversation history to DeepSeek. The
  AI is prompted to respond as a person named Ola in short, natural Polish
  messages.
- The human participant uses `/human` to send text replies.
- `/display` presents both sessions side by side. WebSockets deliver messages
  to connected browser clients in real time.

## Architecture

- `app/main.py` serves the FastAPI API, static browser interfaces, and per-session
  WebSocket connections.
- `app/conversation/` coordinates LLM conversation history and text responses.
- `app/llm/` contains the DeepSeek integration.
- `frontend/participant/`, `frontend/human/`, and `frontend/display/` are the
  host, human participant, and audience browser clients.
- Alice and Bob are the two built-in sessions: Alice is the AI conversation;
  Bob is the human conversation.

## Runtime requirements

The intended setup uses Python 3.12, a `DEEPSEEK_API_KEY` in `.env`, and the
Cloudflare Tunnel described in `README.html`. Start the configured application
with `./scripts/start.sh`; the repository guide also documents setup checks and
manual service smoke tests.
