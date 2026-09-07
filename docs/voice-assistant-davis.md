# DAVIS Voice & Intelligence Runtime Documentation

**DAVIS** (Dynamic Autonomous Virtual Intelligence System) is the built-in conversational AI assistant and runtime engine for **PROJECT AURA**.

---

## 1. Architecture Overview

```
+-------------------------------------------------------------------------+
|                  Microphone Audio Input (16kHz PCM WAV)                 |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|     Acoustic Echo Guard & VoiceIO Sync Mutex (_is_speaking Lock)        |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|             Google Web Speech Recognition Engine (STT)                  |
|     - Continuous Background Wake-Word Detection ("Davis" / "Hey Davis") |
|     - Bounded 4-Second High-Accuracy Command Capture Window             |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                DAVIS Natural Dialogue & Intent Engine                   |
|     - Pleasantries & Context-Aware Intent Classifier                    |
|     - Live Public APIs (Weather, Currency, Math, Wikipedia, Songs)       |
|     - Real Hardware Controls (Wi-Fi, Bluetooth, Powercfg, RAM, Volume)  |
|     - Multi-Turn Persistent Memory Engine (~/.aura_memory.json)         |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|             Neural Voice Synthesizer & Zero-Latency Audio               |
|     - Pre-Warmed Response Cache (~/.aura_voice_cache)                   |
|     - High-Fidelity Edge Neural Voice (en-US-ChristopherNeural)         |
|     - Native Windows MCI (winmm.dll) Direct In-Process Playback         |
|     - Instant Universal SAPI Fallback                                   |
+-------------------------------------------------------------------------+
```

---

## 2. Wake-Word Detection & Acoustic Echo Cancellation

### Continuous Background Monitoring
- DAVIS runs a dedicated background daemon thread listening for its wake-words: **"Davis"** or **"Hey Davis"**.
- Recording uses native Windows Multimedia (`winmm.dll`) PCM audio capture (16,000 Hz, 16-bit Mono), eliminating external process spawn overhead.

### Acoustic Echo Guard (`_is_speaking` Mutex)
- **Problem**: When a voice assistant speaks out loud through laptop speakers, the microphone records its own voice, creating an endless acoustic feedback loop.
- **Solution**: AURA implements a strict synchronous audio mutex lock (`VoiceIO._is_speaking`). While Davis speaks, microphone capture is completely ducked. Once Davis finishes speaking, the audio decay buffer (150ms) elapses, the mutex is unlocked, and the microphone re-opens cleanly.

---

## 3. Zero-Latency Pre-Warmed Audio Cache

When Davis hears its wake-word, users expect an immediate human-like response without network buffering delay:
- During OS startup, common acknowledgements (*"Yeah?"*, *"What can I do for you?"*, *"Yes? I'm listening."*, *"Standing by."*) are pre-synthesized into `~/.aura_voice_cache/`.
- Playback occurs in **under 10 milliseconds** via Windows MCI (`mciSendStringW`), ensuring immediate verbal feedback.

---

## 4. Live External APIs & System Services

DAVIS connects to free, public, authenticated APIs to provide real-time intelligence:

| Service | Provider | Example Spoken Query |
| :--- | :--- | :--- |
| **Live Weather** | Open-Meteo / wttr.in | *"What is the weather in London?"* |
| **Forex & Currency** | open.er-api.com | *"Convert 50 USD to EUR"* |
| **Math & Science** | Local SymPy / AST Solver | *"What is 15 * 6 + 45?"* / *"Square root of 256"* |
| **Web Knowledge** | Wikipedia & DuckDuckGo | *"Who is Alan Turing?"* / *"Tell me about quantum computing"* |
| **Music Discovery** | iTunes Search API | *"Who sings Bohemian Rhapsody?"* |
| **Hardware & Settings**| Real Windows Subsystem | *"Connect to Wi-Fi Aura-5G"*, *"Set power mode to Performance"* |

---

## 5. Multi-Turn Persistent Memory Engine

DAVIS maintains conversational memory across sessions in `~/.aura_memory.json`:
- **User Identity**: Remembers your name (*"My name is Alex"* &rarr; *"You are Alex!"*).
- **Session History**: Records multi-turn interactions (*"What did we talk about?"*).
- **Privacy Reset**: Instantly wipes conversation logs upon request (*"Davis, clear memory"*).
