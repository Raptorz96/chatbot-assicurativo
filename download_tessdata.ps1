# Script per scaricare i file linguistici di Tesseract
$tessdata_path = "C:\Programmi\Tesseract-OCR\tessdata"
$base_url = "https://github.com/tesseract-ocr/tessdata/raw/main"

# Lista dei file da scaricare
$files = @(
    "ita.traineddata",  # Italiano
    "eng.traineddata",  # Inglese
    "osd.traineddata"   # Orientation/Script Detection
)

# Verifica che la directory esista
if (-not (Test-Path $tessdata_path)) {
    Write-Host "Creazione directory tessdata..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $tessdata_path -Force
}

# Scarica ogni file
foreach ($file in $files) {
    $url = "$base_url/$file"
    $output = Join-Path $tessdata_path $file
    
    Write-Host "Download di $file..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
        $size = [math]::Round((Get-Item $output).Length / 1MB, 2)
        Write-Host "✅ $file scaricato con successo ($size MB)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Errore nel download di $file : $_" -ForegroundColor Red
    }
}

Write-Host "`n✅ Download completato!" -ForegroundColor Green