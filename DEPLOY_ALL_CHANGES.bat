@echo off
echo ========================================
echo TOVAR TAXI - DEPLOY ALL CHANGES
echo ========================================
echo.

echo Checking current directory...
cd /d "c:\Users\PC\Desktop\tovar-taxi-by-nesako"
echo Current directory: %CD%

echo.
echo Checking Git status...
git status

echo.
echo Adding ALL files to Git...
git add .

echo.
echo Committing all changes...
git commit -m "Complete UI overhaul: unified roles, improved license plates, simplified dashboard, mobile optimization"

echo.
echo Pushing to Render deployment...
git push origin main

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo All changes deployed:
echo - Unified prevoznik/vozac roles
echo - Improved license plate design (wider, bold numbers)
echo - Simplified carrier dashboard (removed duplicate buttons)
echo - Username dropdown with arrow instead of truck icon
echo - White border on action buttons
echo - Freight exchange sorting by pickup location
echo - Mobile PWA optimizations
echo - Removed duplicate quick actions
echo.
echo Check your Render dashboard for deployment status.
echo Your app will be available at: https://tovar-taxi-by-nesako-web.onrender.com
echo.
pause
