$SourceRoot = "c:\Operation Greenfield\neural-chromium\src"
$OverlayRoot = "c:\Operation Greenfield\neural-chromium-overlay\src"

Write-Host "Applying Neural-Chromium overlay to source tree..."

$files = Get-ChildItem -Path $OverlayRoot -Recurse -File
foreach ($file in $files) {
    $relativePath = $file.FullName.Substring($OverlayRoot.Length + 1)
    $targetPath = Join-Path $SourceRoot $relativePath
    
    Write-Host " Applying: $relativePath"
    Copy-Item $file.FullName $targetPath -Force
}

# Apply build args if the output dir exists
if (Test-Path "c:\Operation Greenfield\neural-chromium\src\out\AgentDebug") {
    Copy-Item "c:\Operation Greenfield\neural-chromium-overlay\args.gn" "c:\Operation Greenfield\neural-chromium\src\out\AgentDebug\args.gn" -Force
    Write-Host " Applied: args.gn"
}

Write-Host "Overlay applied successfully."
