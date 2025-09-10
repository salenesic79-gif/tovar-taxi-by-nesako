@echo off
echo ========================================
echo TOVAR TAXI - DEPLOY CHANGES TO RENDER
echo ========================================
echo.

echo Checking Git status...
git status

echo.
echo Adding all changes to Git...
git add .

echo.
echo Committing changes...
git commit -m "Update: Freight exchange sorting, carrier dashboard UI improvements, mobile optimization"

echo.
echo Pushing to Render...
git push origin main

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Changes deployed:
echo - Freight exchange shows only unaccepted offers
echo - Alphabetical sorting by pickup location
echo - Action buttons for route-based and all offers
echo - Username in carrier dashboard header
echo - Full vehicle brand names in license plates
echo - Mobile PWA optimization
echo.
echo Check your Render dashboard for deployment status.
echo.
pause
