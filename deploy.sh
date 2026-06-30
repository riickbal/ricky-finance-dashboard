#!/bin/bash
# deploy.sh — one-command sync + restart untuk Edith Finance Dashboard
set -e

cd "/Users/ricky/Edith AI (Project)/Personal Finance Dashboard"

echo "📦 Syncing with GitHub..."
rm -f .git/HEAD.lock .git/index.lock 2>/dev/null || true
# Discard local noise (.DS_Store, fuse files, dll) biar pull tidak blocked
git checkout -- . 2>/dev/null || true
git clean -fd backend/.fuse_hidden* 2>/dev/null || true
git pull origin main --rebase || {
    echo "❌ Git pull failed"
    exit 1
}

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
