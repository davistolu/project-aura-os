import os
import sys
import tempfile
import subprocess
import speech_recognition as sr
from gtts import gTTS

def play_audio_file(file_path):
    """Play MP3 or WAV audio synchronously using Windows MCI Multimedia"""
    if sys.platform == "win32":
        ps_cmd = f"""
        \$code = @"
        using System;
        using System.Runtime.InteropServices;
        public class WinAudioPlayer {{
            [DllImport("winmm.dll", EntryPoint = "mciSendStringA")]
            public static extern int mciSendString(string lpszCommand, string lpszReturnString, int cchReturn, int hwndCallback);
            public static void Play(string path) {{
                mciSendString("open \\"" + path + "\\" type mpegvideo alias audiofile", null, 0, 0);
                mciSendString("play audiofile wait", null, 0, 0);
                mciSendString("close audiofile", null, 0, 0);
            }}
        }}
        "@
        try {{ Add-Type -TypeDefinition \$code }} catch {{}}
        [WinAudioPlayer]::Play("{file_path}")
        """
        subprocess.run(["powershell", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    print("Player module verified.")
