@echo off
cd /d "d:\icu telegram bot\last version\coding"
:: Start the bot in the background
start "" /B "C:\Python313\python.exe" telegram_bot.py
:: Start the dashboard in the foreground (since this bat is often called by a hidden VBS)
"C:\Python313\python.exe" dashboard.py
