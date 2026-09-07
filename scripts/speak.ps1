param(
    [Parameter(Mandatory=$true)]
    [string]$Text,
    [string]$AudioFile = ""
)

# 1. If an MP3/WAV file is provided (e.g. from Edge-TTS), play it via Media Player
if ($AudioFile -and (Test-Path $AudioFile)) {
    try {
        Add-Type -AssemblyName presentationCore
        $mediaPlayer = New-Object System.Windows.Media.MediaPlayer
        $mediaPlayer.Open([System.Uri]$AudioFile)
        $mediaPlayer.Play()
        
        # Wait until playback finishes or max 15 seconds
        $duration = 0
        while ($mediaPlayer.NaturalDuration.HasTimeSpan -eq $false -and $duration -lt 20) {
            Start-Sleep -Milliseconds 100
            $duration++
        }
        if ($mediaPlayer.NaturalDuration.HasTimeSpan) {
            $totalMs = $mediaPlayer.NaturalDuration.TimeSpan.TotalMilliseconds
            Start-Sleep -Milliseconds ([int]$totalMs)
        } else {
            Start-Sleep -Seconds 3
        }
        $mediaPlayer.Close()
        exit 0
    } catch {
        # Fallback to SAPI
    }
}

# 2. Universal Windows SAPI Speech Synthesis (Guaranteed audible output)
try {
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.Rate = 0
    $synth.Volume = 100
    $synth.Speak($Text)
} catch {
    Write-Error "Speech synthesis error: $_"
}
