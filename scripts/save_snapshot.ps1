$SourceRoot = "c:\Operation Greenfield\neural-chromium\src"
$OverlayRoot = "c:\Operation Greenfield\neural-chromium-overlay\src"

# List of files we are tracking (Add new files here as we modify them)
$TrackedFiles = @(
    "chrome/browser/ui/views/frame/browser_view.cc",
    "content/browser/browser_main_loop.cc",
    "components/viz/service/display/display.cc",
    "third_party/blink/renderer/core/events/event.cc"
)

Write-Host "Snapshotting modified files from Monster to Overlay..."

foreach ($file in $TrackedFiles) {
    $src = Join-Path $SourceRoot $file
    $dst = Join-Path $OverlayRoot $file
    
    if (Test-Path $src) {
        $parent = Split-Path $dst -Parent
        if (-not (Test-Path $parent)) {
            New-Item -Path $parent -ItemType Directory -Force | Out-Null
        }
        Copy-Item $src $dst -Force
        Write-Host "Saved: $file"
    }
    else {
        Write-Warning "File not found in source (skipping): $file"
    }
}

# Also save the build config
Copy-Item "c:\Operation Greenfield\neural-chromium\src\out\AgentDebug\args.gn" "c:\Operation Greenfield\neural-chromium-overlay\args.gn" -Force
Write-Host "Saved: args.gn"

Write-Host "Snapshot complete."
