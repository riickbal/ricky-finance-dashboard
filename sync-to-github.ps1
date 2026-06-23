# sync-to-github.ps1
# Auto commit + push ke GitHub kalau ada perubahan file
# Dijalankan otomatis tiap 15 menit via Windows Task Scheduler

$repoPath = "D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard"
Set-Location $repoPath

# Cek ada perubahan ga
$status = git status --porcelain
if ($status) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    git add -A
    git commit -m "auto-sync: $timestamp"
    git push origin main
    Write-Host "[$timestamp] Pushed changes to GitHub"
} else {
    Write-Host "[$(Get-Date -Format 'HH:mm')] No changes to push"
}
