# Plan: Remove Audio Features

## Goal

Remove audio recording and playback from the application. Participants will send typed messages, and the participant, human, and display clients will continue to show conversation text. Remove speech recognition, speech synthesis, audio file serving, and audio-specific setup requirements.

## Current audio paths

- Participant recording calls `POST /api/session/{session_id}/record/start` and `/record/stop`.
- `ConversationController` records microphone input, transcribes it with Whisper, and stores generated Piper audio for AI replies.
- Piper also generates speech for host messages and human replies received over WebSocket.
- FastAPI mounts the system temporary directory at `/audio`; participant and display clients play audio URLs, and the display requires an operator click to enable playback.
- The standalone conversation pipeline and several manual scripts exercise recording, transcription, and synthesis.

## Implementation steps

1. **Make typed messages the participant input.** Replace the recording controls and transcript-review flow in `frontend/participant/index.html` with a message input and send control. Simplify `frontend/participant/app.js` to submit text directly and display outgoing and incoming messages. Preserve the current distinction where Bob is a human text participant and Alice's text is sent to the LLM.
2. **Simplify conversation state and HTTP endpoints.** In `app/conversation/controller.py`, remove recorder/STT dependencies, recording and transcribing states, transcript editing, and audio-path state. Retain text validation, conversation calls, and any state/reset behavior still needed by the text flow. In `app/main.py`, remove recording endpoints and the `/audio` static mount, Piper initialization/synthesis, `audio_ready` WebSocket events, and audio response fields. Keep text WebSocket events and session state APIs that remain useful.
3. **Remove browser playback.** Remove the audio-enable button and `audio_ready` handling from `frontend/display/index.html` and `frontend/display/app.js`. Remove related audio and recording styles from `frontend/display/style.css` and `frontend/participant/style.css`. Update user-facing labels and empty-state copy to describe typing and text messages.
4. **Remove audio-only modules and scripts.** Delete `app/audio/`, `app/stt/`, and `app/tts/` after removing their imports. Delete `app/conversation/pipeline.py` if it has no remaining callers. Remove manual recorder, STT, TTS, voice, and audio pipeline scripts.
5. **Remove audio setup and dependencies.** Remove microphone, Whisper, and Piper settings from `app/config.py`. Remove audio-only packages from `pyproject.toml` (`faster-whisper`, `ctranslate2`, `av`, `sounddevice`, `scipy`, `piper-tts`, and CUDA packages if no remaining feature needs them). Update `scripts/check_setup.py`, `scripts/env.sh`, `scripts/start.sh`, and setup documentation so startup no longer requires a microphone, voice models, or audio-related CUDA libraries. Keep model files unless cleanup explicitly includes deleting stored assets.
6. **Update tests and documentation.** Remove tests that only cover recording, transcription, or synthesis. Replace them with coverage for typed participant messages, AI replies, human replies, WebSocket text events, and invalid/empty input. Review `tests/test_config.py`: it imports `PIPER_MODEL` and `SAMPLE_RATE`, which do not match the current config definitions, so update or remove its stale audio assertions. Update `README.html` and any other setup instructions to describe text-only operation.

## Behavior to preserve

- Alice's typed message reaches the conversation service and receives a text response.
- Bob's human text reply is broadcast and displayed as text.
- Host messages continue to reach both sessions and appear as text.
- The display continues to show both conversations and speaker labels.
- Session validation, conversation history, and reset behavior remain intact where used.

## Validation checklist

- Search the repository for remaining audio-related imports, routes, event names, UI strings, styles, scripts, dependencies, and setup checks.
- Confirm application startup and setup checks do not import or require audio packages, CUDA, microphone hardware, or Piper models.
- Run the relevant text-flow tests and then the full test suite after implementation.
- Manually verify Alice, Bob, host, and display text flows in the browser.

## Scope note

This plan treats “remove whole audio” as removing both audio input and audio output. Participants type messages; no recording, speech recognition, speech synthesis, generated audio files, or browser playback remain. Existing local model assets are not deleted by default.
