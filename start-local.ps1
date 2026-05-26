# Starts port-forward and keeps it alive automatically.
# Run this script after Docker Desktop is up.

Write-Host "Starting port-forward loop for cv-fit-score -> http://localhost:8080"
Write-Host "Press Ctrl+C to stop."

while ($true) {
    kubectl port-forward service/cv-fit-score 8080:80 2>$null
    Write-Host "Port-forward dropped, restarting in 2s..."
    Start-Sleep -Seconds 2
}
