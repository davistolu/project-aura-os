import asyncio
import os
import sys
import tempfile
import time
import subprocess
import threading
import ctypes
import hashlib

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

class NeuralVoiceSynthesizer:
    """
    High-Fidelity Neural Voice Synthesizer for DAVIS.
    Features:
    - Zero-latency pre-cached wake acknowledgements.
    - Direct Windows MCI (winmm.dll) playback (0ms subprocess overhead).
    - Fast async Edge-TTS with instant Windows SAPI fallback.
    - True synchronous audio-locking to prevent microphone feedback loops.
    """
    DEFAULT_VOICE = "en-US-ChristopherNeural"  # Natural, articulate human voice
    _is_speaking = False
    _lock = threading.Lock()
    _cache_dir = os.path.join(tempfile.gettempdir(), "aura_voice_cache")

    @classmethod
    def _ensure_cache_dir(cls):
        os.makedirs(cls._cache_dir, exist_ok=True)

    @classmethod
    def _get_cache_path(cls, text: str) -> str:
        cls._ensure_cache_dir()
        text_hash = hashlib.md5(text.strip().lower().encode('utf-8')).hexdigest()
        return os.path.join(cls._cache_dir, f"voice_{text_hash}.mp3")

    @classmethod
    async def _generate_audio_async(cls, text: str, output_mp3: str):
        voice = cls.DEFAULT_VOICE
        communicate = edge_tts.Communicate(text, voice, rate="+5%", pitch="+0Hz")
        await asyncio.wait_for(communicate.save(output_mp3), timeout=5.0)

    @classmethod
    def prewarm_cache(cls, phrases=None):
        """Pre-generates common phrases in background so voice playback is instant (0ms delay)"""
        if phrases is None:
            phrases = [
                "Yeah?",
                "What can I do for you?",
                "Yes? I'm listening.",
                "Right here. What's on your mind?",
                "Yeah, what do you need?",
                "Listening...",
                "Standing by."
            ]

        def _prewarm_worker():
            for phrase in phrases:
                cached_file = cls._get_cache_path(phrase)
                if not os.path.exists(cached_file) or os.path.getsize(cached_file) < 500:
                    try:
                        if HAS_EDGE_TTS:
                            asyncio.run(cls._generate_audio_async(phrase, cached_file))
                    except Exception:
                        pass

        t = threading.Thread(target=_prewarm_worker, daemon=True)
        t.start()

    @classmethod
    def _play_audio_mci(cls, audio_path: str, fallback_text: str = "") -> bool:
        """Plays MP3/WAV audio using native Windows Media Control Interface with duration-bounded sleep (Deadlock-Free)"""
        if not sys.platform.startswith("win"):
            return False
        alias = f"davis_audio_{int(time.time() * 1000) % 100000}"
        winmm = ctypes.windll.winmm
        try:
            # Clean any old alias
            winmm.mciSendStringW(f'close {alias}', None, 0, 0)
            
            # Open audio file
            open_cmd = f'open "{audio_path}" type mpegvideo alias {alias}'
            ret = winmm.mciSendStringW(open_cmd, None, 0, 0)
            if ret != 0:
                ret = winmm.mciSendStringW(f'open "{audio_path}" alias {alias}', None, 0, 0)
                if ret != 0:
                    return False

            # Query duration in milliseconds
            buf = ctypes.create_unicode_buffer(64)
            winmm.mciSendStringW(f'status {alias} length', buf, 64, 0)
            try:
                val = buf.value.strip()
                ms = int(val) if val.isdigit() else 0
                dur = max(0.6, min(ms / 1000.0, 12.0))
            except Exception:
                dur = max(0.8, min(len(fallback_text) * 0.08, 8.0))

            # Play without freezing thread on MCI driver wait
            winmm.mciSendStringW(f'play {alias}', None, 0, 0)
            time.sleep(dur + 0.15)
            return True
        except Exception:
            return False
        finally:
            try:
                winmm.mciSendStringW(f'stop {alias}', None, 0, 0)
                winmm.mciSendStringW(f'close {alias}', None, 0, 0)
            except Exception:
                pass

    @classmethod
    def _speak_sapi_native(cls, text: str):
        """Fast fallback to Windows SAPI via PowerShell or COM"""
        clean_text = text.replace('"', '').replace("'", "").replace('\n', ' ')
        ps_cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{clean_text}')"
        try:
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=6)
        except Exception:
            pass

    @classmethod
    def speak_sync(cls, text: str):
        """
        Speaks text synchronously with audio mutex lock.
        Guarantees release of audio lock so system never hangs.
        """
        if not text:
            return

        with cls._lock:
            cls._is_speaking = True
            try:
                cached_file = cls._get_cache_path(text)
                audio_ready = False

                # 1. Check pre-warmed cache
                if os.path.exists(cached_file) and os.path.getsize(cached_file) > 500:
                    played = cls._play_audio_mci(cached_file, fallback_text=text)
                    if played:
                        return

                # 2. Synthesize with Edge-TTS if not cached
                if HAS_EDGE_TTS:
                    try:
                        asyncio.run(cls._generate_audio_async(text, cached_file))
                        if os.path.exists(cached_file) and os.path.getsize(cached_file) > 500:
                            played = cls._play_audio_mci(cached_file, fallback_text=text)
                            if played:
                                return
                    except Exception:
                        pass

                # 3. Native SAPI Fallback (Guaranteed immediate voice)
                cls._speak_sapi_native(text)

            finally:
                time.sleep(0.15)  # Acoustic decay buffer
                cls._is_speaking = False

    @classmethod
    def speak(cls, text: str):
        """Speaks asynchronously in a background thread"""
        t = threading.Thread(target=cls.speak_sync, args=(text,), daemon=True)
        t.start()

# Automatically pre-warm common phrases on import
NeuralVoiceSynthesizer.prewarm_cache()

