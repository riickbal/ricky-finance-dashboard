@echo off
title Git Push - Personal Finance Dashboard
color 0A
echo.
echo Pushing local commits to GitHub...
echo (Login browser mungkin terbuka - approve)
echo.
cd /d "D:\Edith (Claude Ai)\Projects\Personal Finance Dashboard"
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] Push berhasil! GitHub sudah sync.
) else (
    echo [INFO] Push gagal. Coba jalankan lagi atau cek koneksi.
)
echo.
pause
