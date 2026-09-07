param (
    [int]$TimeoutSeconds = 6
)

Add-Type -AssemblyName System.Speech

try {
    $engine = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    $engine.SetInputToDefaultAudioDevice()
    $grammar = New-Object System.Speech.Recognition.DictationGrammar
    $engine.LoadGrammar($grammar)
    
    $timeout = [TimeSpan]::FromSeconds($TimeoutSeconds)
    $result = $engine.Recognize($timeout)
    
    if ($result -and $result.Text) {
        Write-Output $result.Text
    } else {
        Write-Output "__NO_SPEECH_DETECTED__"
    }
} catch {
    Write-Output "__MIC_ERROR__: $($_.Exception.Message)"
} finally {
    if ($engine) {
        $engine.Dispose()
    }
}
