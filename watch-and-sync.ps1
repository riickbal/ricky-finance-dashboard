# watch-and-sync.ps1
# Real-time file watcher — deteksi perubahan data.js / index.html → langsung push ke GitHub
# Jalan terus di background selama PC nyala

$repoPath = "D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard"
Set-Location $repoPath

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Watcher aktif — monitoring $repoPath"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $repoPath
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite

# Debounce — jangan push berkali-kali dalam 3 detik
$lastPush = [DateTime]::MinValue

$action = {
    $now = Get-Date
    $elapsed = ($now - $lastPush).TotalSeconds
    if ($elapsed -lt 3) { return }
    $script:lastPush = $now

    $file = $Event.SourceEventArgs.Name
    # Hanya sync kalau file yang relevan berubah
    if ($file -notmatch "data\.js|index\.html|prices\.json") { return }

    Start-Sleep -Seconds 1  # tunggu file selesai ditulis
    Set-Location $repoPath

    $status = git status --porcelain
    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git add -A
        git commit -m "live-sync: $file updated at $timestamp"
        git push origin main 2>&1
        Write-Host "[$timestamp] PUSHED: $file"
    }
}

Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null
Register-ObjectEvent $watcher "Created" -Action $action | Out-Null

# Keep alive
while ($true) { Start-Sleep -Seconds 10 }
