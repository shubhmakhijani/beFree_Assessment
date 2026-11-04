@echo off
echo ===================================================
echo   Befree Platform - Push to GitHub Utility
echo ===================================================
echo.

set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/shubhmakhijani/befree-bank-statement-parser.git): "

if "%REPO_URL%"=="" (
    echo Error: No repository URL provided!
    pause
    exit /b
)

echo.
echo Setting remote origin to: %REPO_URL%
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo Pushing 'main' branch to GitHub...
git push -u origin main

echo.
echo ===================================================
echo   Done! Check your GitHub repository.
echo ===================================================
pause
