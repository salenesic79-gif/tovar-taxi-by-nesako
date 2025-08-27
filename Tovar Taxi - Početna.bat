@echo off
cd /d "c:\Users\PC\Desktop\tovar-taxi-by-nesako"
start http://localhost:8000
python manage.py runserver
pause
