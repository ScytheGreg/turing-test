# Project Overview

## Main idea

This project is a Polish-language Turing test demonstration. A host runs two
conversations, one with an AI persona and one with a human participant. Both are
shown side by side on a display so an audience can compare them and decide
which conversation involves the AI.

## How it works

- The host uses the `/participant` interface to manage the AI conversation.
  Spoken prompts are recorded, transcribed in Polish with Whisper, and can be
  reviewed or edited before they are sent.
- The backend sends each prompt and its conversation history to DeepSeek. The
  AI is prompted to respond as a person named Ola in short, natural Polish
  messages.
- Responses are spoken using Piper text-to-speech. Host prompts and the human
  participant's messages are also voiced for the display.
- The human participant uses `/human` to send text replies. That interface is
  currently text-based; the backend generates speech for those replies.
- `/display` presents both sessions side by side. WebSockets deliver messages
  and audio notifications to connected browser clients in real time.

## Architecture

- `app/main.py` serves the FastAPI API, static browser interfaces, audio files,
  and per-session WebSocket connections.
- `app/conversation/` coordinates session state, recording, transcription,
  LLM conversation history, and response audio generation.
- `app/audio/`, `app/stt/`, `app/llm/`, and `app/tts/` contain the microphone,
  Whisper, DeepSeek, and Piper integrations.
- `frontend/participant/`, `frontend/human/`, and `frontend/display/` are the
  host, human participant, and audience browser clients.
- Alice and Bob are the two built-in sessions: Alice is the AI conversation;
  Bob is the human conversation.

## Runtime requirements

The intended setup uses Python 3.12, a configured microphone and CUDA-capable
GPU, local Piper voice models, a `DEEPSEEK_API_KEY` in `.env`, and the
Cloudflare Tunnel described in `README.html`. Start the configured application
with `./scripts/start.sh`; the repository guide also documents setup checks and
manual service smoke tests.
