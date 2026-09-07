param (
    [string]$OutputFile = "$env:TEMP\aura_mic_input.wav",
    [int]$DurationSeconds = 5
)

# Use Windows Multimedia API (winmm.dll) for direct hardware audio recording
$code = @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public class WinAudioRecorder {
    [DllImport("winmm.dll", EntryPoint = "mciSendStringA", CharSet = CharSet.Ansi)]
    public static extern int mciSendString(string lpszCommand, StringBuilder lpszReturnString, int cchReturn, int hwndCallback);

    public static void Record(string outputPath, int durationSeconds) {
        mciSendString("open new Type waveaudio Alias recsound", null, 0, 0);
        // 16000 Hz, 16-bit, Mono PCM (Ideal for Google Speech Recognition)
        mciSendString("set recsound format tag pcm bitspersample 16 channels 1 samplespersec 16000", null, 0, 0);
        mciSendString("record recsound", null, 0, 0);
        System.Threading.Thread.Sleep(durationSeconds * 1000);
        mciSendString("save recsound \"" + outputPath + "\"", null, 0, 0);
        mciSendString("close recsound", null, 0, 0);
    }
}
"@

try {
    Add-Type -TypeDefinition $code
} catch {}

try {
    if (Test-Path $OutputFile) {
        Remove-Item $OutputFile -Force
    }
    [WinAudioRecorder]::Record($OutputFile, $DurationSeconds)
    if (Test-Path $OutputFile) {
        Write-Output $OutputFile
    } else {
        Write-Output "__NO_AUDIO_CAPTURED__"
    }
} catch {
    Write-Output "__REC_ERROR__: $($_.Exception.Message)"
}
