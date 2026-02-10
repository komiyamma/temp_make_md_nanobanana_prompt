cd /d "%~dp0"
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0generate_list.ps1"
if errorlevel 1 exit /b %errorlevel%
git add -A
git commit -m "addition"
git push
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0auto_jules.ps1" %*
