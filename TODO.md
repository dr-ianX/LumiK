# TODO - Fix audio autoplay, music controls, and event preview metadata

- [ ] 1. assistant.html
  - [x] Remove intrusive autoplay alert and blocking click flow
  - [x] Add robust autoplay unlock logic without breaking visuals
  - [ ] Add random playlist/autoplay on load
  - [x] Add WebSocket handlers for AUDIO_PLAY / AUDIO_PAUSE / AUDIO_STOP / AUDIO_SEEK_START / AUDIO_RANDOM

- [ ] 2. control.html
  - [x] Fix music source to local `/music/...` instead of external GitHub raw URL
  - [x] Ensure Play resets to start and controls assistant via WS
  - [x] Ensure Pause/Stop send proper WS commands and work in assistant
  - [ ] Add upload control for audio files
  - [ ] Add command/history integration for new audio actions

- [ ] 3. server.py
  - [x] Fix EVENT_INFO parsing for OpenGraph injection
  - [x] Keep OG values dynamic from control event fields
  - [ ] Add endpoint for audio upload (if needed for control uploader)
  - [x] Add endpoint to list uploaded audio files
  - [x] Ensure `/music` and `/uploads` are served correctly for playback and preview image

- [ ] 4. Verification
  - [ ] Validate no regressions in visual/chat behavior
  - [ ] Validate autoplay behavior (best effort browser policy compliant)
  - [ ] Validate OG tags and event image/title/description flow
  - [ ] Prepare git commands for commit and push to Render-connected repo
