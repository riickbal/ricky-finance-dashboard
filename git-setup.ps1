# git-setup.ps1
# Setup git di project folder Personal Finance Dashboard
# Jalanin SEKALI: klik kanan -> Run with PowerShell

$repoPath = "D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard"
$remoteUrl = "https://github.com/riickbal/ricky-finance-dashboard.git"

Write-Host "======================================"
Write-Host " Git Setup - Personal Finance Dashboard"
Write-Host "======================================"
Write-Host ""

# 1. Cek git installed
$gitVersion = git --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Git tidak ditemukan!" -ForegroundColor Red
    Write-Host "Download dan install dulu: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "Tekan Enter untuk keluar"
    exit 1
}
Write-Host "[OK] Git ditemukan: $gitVersion" -ForegroundColor Green

# 2. Masuk ke folder project
Set-Location $repoPath
Write-Host "[OK] Folder: $repoPath" -ForegroundColor Green

# 3. Init git jika belum ada
if (!(Test-Path ".git")) {
    Write-Host ""
    Write-Host "[SETUP] Inisialisasi git repository..." -ForegroundColor Cyan
    git init
    git checkout -b main
    Write-Host "[OK] Git repo initialized" -ForegroundColor Green
} else {
    Write-Host "[OK] Git repo sudah ada, skip init" -ForegroundColor Green
}

# 4. Set user config (global)
$currentEmail = git config --global user.email 2>&1
if (!$currentEmail) {
    git config --global user.email "mrq.scm@gmail.com"
    git config --global user.name "Ricky"
    Write-Host "[OK] Git user configured" -ForegroundColor Green
} else {
    Write-Host "[OK] Git user: $currentEmail" -ForegroundColor Green
}

# 5. Set remote origin
$existingRemote = git remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    git remote add origin $remoteUrl
    Write-Host "[OK] Remote origin added: $remoteUrl" -ForegroundColor Green
} else {
    git remote set-url origin $remoteUrl
    Write-Host "[OK] Remote origin updated: $remoteUrl" -ForegroundColor Green
}

# 6. Stage semua file & commit awal
Write-Host ""
Write-Host "[SETUP] Commit semua file lokal..." -ForegroundColor Cyan
git add -A
$status = git status --porcelain
if ($status) {
    git commit -m "init: setup git sync for Personal Finance Dashboard"
    Write-Host "[OK] Initial commit done" -ForegroundColor Green
} else {
    Write-Host "[OK] Tidak ada perubahan untuk di-commit" -ForegroundColor Yellow
}

# 7. Pull dari GitHub (agar history match) lalu push
Write-Host ""
Write-Host "[SETUP] Sync dengan GitHub..." -ForegroundColor Cyan
Write-Host "Browser mungkin akan terbuka untuk login GitHub - approve aja." -ForegroundColor Yellow
Write-Host ""

git pull origin main --allow-unrelated-histories --no-edit 2>&1
git push -u origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Git sync berhasil!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[INFO] Kalau ada error auth, login dulu ke GitHub via:" -ForegroundColor Yellow
    Write-Host "  gh auth login" -ForegroundColor White
    Write-Host "Atau masukkan Personal Access Token (PAT) saat diminta password." -ForegroundColor Yellow
}

# 8. Setup watch-and-sync task
Write-Host ""
Write-Host "[SETUP] Daftarkan Live Sync task ke Task Scheduler..." -ForegroundColor Cyan
$action1 = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$repoPath\watch-and-sync.ps1`""
$trigger1 = New-ScheduledTaskTrigger -AtLogOn
$settings1 = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

Register-ScheduledTask `
    -TaskName "RickyDashboard-LiveSync" `
    -Action $action1 -Trigger $trigger1 -Settings $settings1 `
    -Description "Live sync: deteksi perubahan file -> langsung push ke GitHub" `
    -RunLevel Limited -Force | Out-Null

Write-Host "[OK] Task Scheduler: RickyDashboard-LiveSync aktif (jalan saat login)" -ForegroundColor Green

# 9. Langsung start watcher sekarang (background)
Write-Host ""
Write-Host "[SETUP] Memulai file watcher sekarang..." -ForegroundColor Cyan
Start-Process powershell.exe -ArgumentList "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$repoPath\watch-and-sync.ps1`"" -WindowStyle Hidden
Write-Host "[OK] File watcher sudah jalan di background!" -ForegroundColor Green

Write-Host ""
Write-Host "============================================"
Write-Host " SELESAI! Full auto sync aktif."
Write-Host ""
Write-Host " Trigger: Claude update data.js"
Write-Host " -> watch-and-sync.ps1 deteksi perubahan"
Write-Host " -> langsung push ke GitHub (<5 detik)"
Write-Host " -> GitHub Pages update otomatis"
Write-Host ""
Write-Host " Lo ga perlu klik apa-apa lagi!"
Write-Host "============================================"
Write-Host ""
Read-Host "Tekan Enter untuk tutup"
