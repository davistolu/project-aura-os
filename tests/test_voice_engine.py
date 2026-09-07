import unittest

class MockVoiceEngine:
    def __init__(self):
        self.wake_words = ["hey davis", "davis", "hey jarvis", "aura", "jarvis"]
        self.mic_enabled = True
        self.tts_enabled = True
        self.state = "IDLE_LISTENING_WAKE_WORD"
        self.held_capabilities = {"audio.capture", "audio.playback"}

    def detect_wake_word(self, phrase):
        if not self.mic_enabled:
            return None
        lower = phrase.lower()
        for w in self.wake_words:
            if w in lower:
                return w
        return None

    def toggle_mic(self):
        self.mic_enabled = not self.mic_enabled
        self.state = "MUTED" if not self.mic_enabled else "IDLE_LISTENING_WAKE_WORD"
        return self.mic_enabled

    def synthesize(self, text):
        if not self.tts_enabled or "audio.playback" not in self.held_capabilities:
            return None
        return f"[Audio PCM Stream: '{text}']"

class TestVoiceEngine(unittest.TestCase):
    def setUp(self):
        self.voice = MockVoiceEngine()

    def test_wake_word_trigger(self):
        detected = self.voice.detect_wake_word("Hey Jarvis, check my battery level")
        self.assertEqual(detected, "hey jarvis")

    def test_alternate_wake_word(self):
        detected = self.voice.detect_wake_word("Aura, switch to gaming workspace")
        self.assertEqual(detected, "aura")

    def test_unrelated_audio_no_trigger(self):
        detected = self.voice.detect_wake_word("What time is it right now?")
        self.assertIsNone(detected)

    def test_privacy_mic_mute(self):
        self.voice.toggle_mic()
        self.assertEqual(self.voice.state, "MUTED")
        # When muted, wake words must never trigger
        detected = self.voice.detect_wake_word("Hey Jarvis, are you there?")
        self.assertIsNone(detected)

    def test_tts_synthesis(self):
        audio_stream = self.voice.synthesize("Welcome to Project Aura. All systems nominal.")
        self.assertIsNotNone(audio_stream)
        self.assertIn("Audio PCM Stream", audio_stream)

if __name__ == "__main__":
    unittest.main()
