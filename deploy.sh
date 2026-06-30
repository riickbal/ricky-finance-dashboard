#!/bin/bash
# deploy.sh — one-command sync + restart untuk Edith Finance Dashboard
set -e

cd "/Users/ricky/Edith AI (Project)/Personal Finance Dashboard"

echo "📦 Syncing with GitHub..."
git stash 2>/dev/null || true
rm -f .git/HEAD.lock .git/index.lock 2>/dev/null || true

if git pull origin main --rebase 2>&1; then
    git stash pop 2>/dev/null || true
else
    echo "❌ Git pull failed"
    git stash pop 2>/dev/null || true
    exit 1
fi

echo "🔄 Restarting Finance API..."
launchctl kickstart -k "gui/$(id -u)/com.edith.financeapi" 2>/dev/null || {
    launchctl unload ~/Library/LaunchAgents/com.edith.financeapi.plist 2>/dev/null
    sleep 1
    launchctl load ~/Library/LaunchAgents/com.edith.financeapi.plist
}

echo "🤖 Restarting Edith Telegram Bot..."
launchctl kickstart -k "gui/$(id -u)/com.edith.telegrambot" 2>/dev/null || {
    launchctl unload ~/Library/LaunchAgents/com.edith.telegrambot.plist 2>/dev/null
    sleep 1
    launchctl load ~/Library/LaunchAgents/com.edith.telegrambot.plist
}

sleep 2
echo "✅ Done! Checking health..."
curl -s http://localhost:3000/api/health && echo ""
