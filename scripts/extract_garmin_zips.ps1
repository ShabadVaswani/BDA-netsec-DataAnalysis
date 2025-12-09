# Extract all Garmin zip files into organized folders

$zipFiles = Get-ChildItem -Path "." -Filter "*.zip"

Write-Host "Found $($zipFiles.Count) zip files to extract..."
Write-Host ""

foreach ($zip in $zipFiles) {
    $folderName = $zip.BaseName
    
    # Create folder if it doesn't exist
    if (-not (Test-Path $folderName)) {
        New-Item -ItemType Directory -Path $folderName -Force | Out-Null
    }
    
    # Extract zip file
    Write-Host "Extracting: $folderName..."
    Expand-Archive -Path $zip.FullName -DestinationPath $folderName -Force
}

Write-Host ""
Write-Host "Extraction complete! All files organized by date."
