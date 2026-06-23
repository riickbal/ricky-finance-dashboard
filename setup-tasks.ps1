# setup-tasks.ps1
# Jalanin sekali — klik kanan -> Run with PowerShell
# Setup: live sync watcher + auto pull harga tiap 6 jam

$repoPath = "D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard"

# -------------------------------------------------------
# Task 1: Live Watcher — push ke GitHub real-time
# -------------------------------------------------------
$action1 = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$repoPath\watch-and-sync.ps1`""

# Trigger: langsung jalan saat login, jalan terus
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
    -Description "Live sync: deteksi perubahan file → langsung push ke GitHub" `
    -RunLevel Limited -Force

Write-Host "OK: RickyDashboard-LiveSync (real-time, jalan saat login)"

# -------------------------------------------------------
# Task 2: Auto Pull harga dari GitHub tiap 6 jam
# -------------------------------------------------------
$action2 = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$repoPath\pull-from-github.ps1`""

$trigger2 = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Hours 6) -Once -At (Get-Date)

$settings2 = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 2) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

Register-ScheduledTask `
    -TaskName "RickyDashboard-AutoPull" `
    -Action $action2 -Trigger $trigger2 -Settings $settings2 `
    -Description "Auto pull harga VOO/BBRI dari GitHub tiap 6 jam" `
    -RunLevel Limited -Force

Write-Host "OK: RickyDashboard-AutoPull (tiap 6 jam)"

# -------------------------------------------------------
# Hapus task lama kalau ada
# -------------------------------------------------------
Unregister-ScheduledTask -TaskName "RickyDashboard-AutoPush" -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Removed: RickyDashboard-AutoPush (diganti LiveSync)"

Write-Host ""
Write-Host "=============================="
Write-Host " SELESAI! Live sync aktif."
Write-Host " Setiap data.js / index.html"
Write-Host " berubah -> langsung ke GitHub"
Write-Host "=============================="
Read-Host "Tekan Enter untuk tutup"
