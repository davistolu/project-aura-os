use serde::{Deserialize, Serialize};
use std::sync::{Arc, RwLock};
use aura_core::error::{AuraError, AuraResult};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VoiceState {
    Muted,
    IdleListeningWakeWord,
    ActiveCapturingSpeech,
    ProcessingIntent,
    SpeakingResponse,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VoiceConfig {
    pub wake_words: Vec<String>,
    pub voice_name: String,
    pub speech_rate: f32,
    pub mic_enabled: bool,
    pub tts_enabled: bool,
    pub language: String,
}

impl Default for VoiceConfig {
    fn default() -> Self {
        Self {
            wake_words: vec!["hey jarvis".to_string(), "aura".to_string(), "jarvis".to_string()],
            voice_name: "aura-neural-male".to_string(),
            speech_rate: 1.0,
            mic_enabled: true,
            tts_enabled: true,
            language: "en-US".to_string(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct VoiceEngine {
    config: Arc<RwLock<VoiceConfig>>,
    state: Arc<RwLock<VoiceState>>,
}

impl Default for VoiceEngine {
    fn default() -> Self {
        Self::new(VoiceConfig::default())
    }
}

impl VoiceEngine {
    pub fn new(config: VoiceConfig) -> Self {
        Self {
            config: Arc::new(RwLock::new(config)),
            state: Arc::new(RwLock::new(VoiceState::IdleListeningWakeWord)),
        }
    }

    pub fn get_state(&self) -> VoiceState {
        *self.state.read().unwrap()
    }

    pub fn set_state(&self, state: VoiceState) {
        let mut s = self.state.write().unwrap();
        *s = state;
    }

    pub fn toggle_mic_mute(&self) -> bool {
        let mut cfg = self.config.write().unwrap();
        cfg.mic_enabled = !cfg.mic_enabled;
        let mut state = self.state.write().unwrap();
        if !cfg.mic_enabled {
            *state = VoiceState::Muted;
        } else {
            *state = VoiceState::IdleListeningWakeWord;
        }
        cfg.mic_enabled
    }

    /// Check audio transcript against wake words
    pub fn detect_wake_word(&self, transcript: &str) -> Option<String> {
        let cfg = self.config.read().unwrap();
        if !cfg.mic_enabled {
            return None;
        }

        let lower = transcript.to_lowercase();
        for word in &cfg.wake_words {
            if lower.contains(word) {
                return Some(word.clone());
            }
        }
        None
    }

    /// Convert input audio waveform buffer to text (Whisper / local STT)
    pub fn transcribe_speech(&self, _audio_pcm_samples: &[f32]) -> AuraResult<String> {
        let state = self.get_state();
        if state == VoiceState::Muted {
            return Err(AuraError::System("Microphone is currently hardware/software muted".to_string()));
        }
        // STT inference (e.g. whisper.cpp / onnx)
        Ok("Sample transcribed speech".to_string())
    }

    /// Synthesize speech audio from text response (Piper / local TTS)
    pub fn synthesize_speech(&self, text: &str) -> AuraResult<Vec<u8>> {
        let cfg = self.config.read().unwrap();
        if !cfg.tts_enabled {
            return Ok(Vec::new());
        }

        // TTS inference returning PCM audio buffer for PipeWire playback
        Ok(format!("[PCM Audio Stream for '{}' using voice '{}']", text, cfg.voice_name).into_bytes())
    }
}
