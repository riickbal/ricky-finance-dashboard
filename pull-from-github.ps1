# pull-from-github.ps1
# Auto pull update dari GitHub (harga VOO/BBRI/FX dari GitHub Actions)
# Dijalankan otomatis tiap 6 jam via Windows Task Scheduler

$repoPath = "D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard"
Set-Location $repoPath

git pull origin main
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm')] Pulled latest from GitHub"
