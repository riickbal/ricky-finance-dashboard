@echo off
title Git Setup - Personal Finance Dashboard
color 0A
echo.
echo ======================================
echo  Git Setup - Personal Finance Dashboard
echo ======================================
echo.

:: Cek git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git tidak terinstall!
    echo.
    echo Install dulu dari: https://git-scm.com/download/win
    echo Setelah install, jalankan file ini lagi.
    echo.
    pause
    exit /b 1
)

echo [OK] Git ditemukan:
git --version
echo.

:: Masuk ke folder project
cd /d "D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard"
echo [OK] Folder: %CD%
echo.

:: Init git jika belum
if not exist ".git" (
    echo [SETUP] Inisialisasi git repository...
    git init
    git checkout -b main 2>nul || git branch -m master main 2>nul
    echo [OK] Git repo initialized
) else (
    echo [OK] Git repo sudah ada
)
echo.

:: Set user config
git config user.email "mrq.scm@gmail.com"
git config user.name "Ricky"
echo [OK] Git user: mrq.scm@gmail.com
echo.

:: Set remote
git remote remove origin 2>nul
git remote add origin https://github.com/riickbal/ricky-finance-dashboard.git
echo [OK] Remote: https://github.com/riickbal/ricky-finance-dashboard.git
echo.

:: Stage semua file
echo [SETUP] Stage semua file...
git add -A
git status --short
echo.

:: Initial commit
echo [SETUP] Commit...
git commit -m "init: setup git sync for Personal Finance Dashboard" 2>nul
if %errorlevel% equ 0 (
    echo [OK] Commit done
) else (
    echo [OK] Tidak ada yang perlu di-commit
)
echo.

:: Fetch dan merge dari GitHub agar history match
echo [SETUP] Ambil history dari GitHub...
echo (Browser mungkin terbuka untuk login GitHub - approve aja)
echo.
git fetch origin
git merge origin/main --allow-unrelated-histories -m "merge: sync with GitHub" 2>nul

:: Push ke GitHub
echo.
echo [SETUP] Push ke GitHub...
git push -u origin main
echo.

if %errorlevel% equ 0 (
    echo ============================================
    echo  [SUCCESS] Git sync berhasil!
    echo.
    echo  Sekarang setiap Claude update data.js,
    echo  file watcher langsung push ke GitHub.
    echo.
    echo  Lo tidak perlu klik apa-apa lagi!
    echo ============================================
) else (
    echo ============================================
    echo  [INFO] Push gagal - kemungkinan perlu login
    echo.
    echo  Coba jalankan di CMD:
    echo    git -C "D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard" push -u origin main
    echo.
    echo  Kalau diminta password, masukkan GitHub
    echo  Personal Access Token (bukan password biasa)
    echo  Buat PAT di: github.com/settings/tokens
    echo ============================================
)
echo.

:: Setup Task Scheduler untuk live sync
echo [SETUP] Daftarkan Live Sync ke Task Scheduler...
powershell -ExecutionPolicy Bypass -Command "^
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File \"D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard\watch-and-sync.ps1\"';^
    $trigger = New-ScheduledTaskTrigger -AtLogOn;^
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -StartWhenAvailable -RunOnlyIfNetworkAvailable;^
    Register-ScheduledTask -TaskName 'RickyDashboard-LiveSync' -Action $action -Trigger $trigger -Settings $settings -Description 'Live sync dashboard to GitHub' -RunLevel Limited -Force | Out-Null;^
    Write-Host '[OK] Task Scheduler: RickyDashboard-LiveSync registered'"

:: Start watcher sekarang
echo [SETUP] Start file watcher sekarang (background)...
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard\watch-and-sync.ps1"
echo [OK] Watcher jalan di background!
echo.
echo Tekan Enter untuk tutup...
pause >nul
