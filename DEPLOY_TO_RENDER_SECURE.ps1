# PowerShell skripta za deployment na Render sa HTTPS konfiguracijama
# Autor: NESAKO - Tovar Taxi Deployment Script

Write-Host "=== TOVAR TAXI - RENDER DEPLOYMENT SCRIPT ===" -ForegroundColor Green
Write-Host "Priprema za deployment sa HTTPS sigurnosnim postavkama..." -ForegroundColor Yellow

# 1. Backup trenutnih settings
Write-Host "`n[1/8] Kreiranje backup-a settings.py..." -ForegroundColor Cyan
$backupPath = "tovar_taxi\settings_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').py"
Copy-Item "tovar_taxi\settings.py" $backupPath
Write-Host "Backup kreiran: $backupPath" -ForegroundColor Green

# 2. Modifikacija settings.py za produkciju
Write-Host "`n[2/8] Modifikacija settings.py za HTTPS produkciju..." -ForegroundColor Cyan
$settingsContent = Get-Content "tovar_taxi\settings.py" -Raw

# Zameni SESSION_COOKIE_SECURE
$settingsContent = $settingsContent -replace "SESSION_COOKIE_SECURE = False  # True za HTTPS u produkciji", "SESSION_COOKIE_SECURE = True  # HTTPS produkcija"

# Dodaj dodatne sigurnosne postavke za produkciju
$securitySettings = @"

# Sigurnosne postavke za HTTPS produkciju
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 godina
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CSRF postavke za produkciju
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://tovar-taxi.onrender.com'
]
"@

# Dodaj sigurnosne postavke na kraj fajla
$settingsContent += $securitySettings
Set-Content "tovar_taxi\settings.py" $settingsContent
Write-Host "Settings.py modifikovan za HTTPS produkciju" -ForegroundColor Green

# 3. Kreiranje .env fajla za produkciju
Write-Host "`n[3/8] Kreiranje .env fajla za produkciju..." -ForegroundColor Cyan
$envContent = @"
# Tovar Taxi - Production Environment Variables
DEBUG=False
SECRET_KEY=your-super-secret-key-here-change-this-in-production
DATABASE_URL=postgresql://user:password@host:port/database
ALLOWED_HOSTS=tovar-taxi.onrender.com,*.onrender.com
RENDER_EXTERNAL_HOSTNAME=tovar-taxi.onrender.com

# Session Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email settings (opciono)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
"@

Set-Content ".env.production" $envContent
Write-Host ".env.production kreiran" -ForegroundColor Green

# 4. Kreiranje render.yaml za deployment
Write-Host "`n[4/8] Kreiranje render.yaml konfiguracije..." -ForegroundColor Cyan
$renderYaml = @"
services:
  - type: web
    name: tovar-taxi
    env: python
    buildCommand: |
      pip install -r requirements.txt
      python manage.py collectstatic --noinput
      python manage.py migrate
    startCommand: gunicorn tovar_taxi.wsgi:application
    envVars:
      - key: DEBUG
        value: False
      - key: SECRET_KEY
        generateValue: true
      - key: WEB_CONCURRENCY
        value: 4
      - key: PYTHON_VERSION
        value: 3.11.0
    autoDeploy: false
    healthCheckPath: /
"@

Set-Content "render.yaml" $renderYaml
Write-Host "render.yaml kreiran" -ForegroundColor Green

# 5. Ažuriranje requirements.txt
Write-Host "`n[5/8] Ažuriranje requirements.txt..." -ForegroundColor Cyan
$requirements = @"
Django>=4.2.0
channels>=4.0.0
whitenoise>=6.5.0
gunicorn>=21.2.0
psycopg2-binary>=2.9.7
python-decouple>=3.8
dj-database-url>=2.1.0
"@

Set-Content "requirements.txt" $requirements
Write-Host "requirements.txt ažuriran" -ForegroundColor Green

# 6. Kreiranje gunicorn konfiguracije
Write-Host "`n[6/8] Kreiranje gunicorn.conf.py..." -ForegroundColor Cyan
$gunicornConf = @"
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + str(os.environ.get("PORT", "8000"))
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "tovar_taxi"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
"@

Set-Content "gunicorn.conf.py" $gunicornConf
Write-Host "gunicorn.conf.py kreiran" -ForegroundColor Green

# 7. Kreiranje deployment skripte
Write-Host "`n[7/8] Kreiranje build.sh skripte..." -ForegroundColor Cyan
$buildScript = @"
#!/bin/bash
# Build script za Render deployment

echo "=== Tovar Taxi Build Script ==="

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@tovartaxi.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

echo "Build completed successfully!"
"@

Set-Content "build.sh" $buildScript -Encoding UTF8
Write-Host "build.sh kreiran" -ForegroundColor Green

# 8. Kreiranje deployment instrukcija
Write-Host "`n[8/8] Kreiranje deployment instrukcija..." -ForegroundColor Cyan
$instructions = @"
# TOVAR TAXI - RENDER DEPLOYMENT INSTRUKCIJE

## Korak 1: Priprema
1. Commituj sve promene u Git
2. Push na GitHub/GitLab

## Korak 2: Render Setup
1. Idi na https://render.com
2. Kreiraj novi Web Service
3. Konektuj GitHub/GitLab repo
4. Podesi sledeće:
   - Build Command: `chmod +x build.sh && ./build.sh`
   - Start Command: `gunicorn tovar_taxi.wsgi:application`
   - Environment: Python 3

## Korak 3: Environment Variables
Dodaj sledeće environment variables u Render:
- DEBUG=False
- SECRET_KEY=[generiši novi]
- ALLOWED_HOSTS=your-app-name.onrender.com
- DATABASE_URL=[Render će automatski kreirati]

## Korak 4: Domain Setup
1. U Render dashboard, idi na Settings
2. Dodaj custom domain (opciono)
3. SSL će biti automatski konfigurisan

## Korak 5: Database
1. Kreiraj PostgreSQL database u Render
2. Konektuj sa web service
3. Migracije će se pokrenuti automatski

## Korak 6: Admin Access
- URL: https://your-app.onrender.com/admin/
- Username: admin
- Password: admin123 (PROMENI ODMAH!)

## Korak 7: Import korisnika
1. Eksportuj korisnike sa localhost: /admin/auth/user/
2. Importuj na produkciju: /admin/auth/user/import-users/

## Sigurnosne postavke aktivirane:
✅ HTTPS redirect
✅ Secure cookies
✅ HSTS headers
✅ XSS protection
✅ CSRF protection
✅ Content type sniffing protection

## Backup fajlovi kreirani:
- settings_backup_*.py (originalni settings)
- .env.production (environment variables)

## Podrška:
Za pomoć kontaktiraj NESAKO tim.
"@

Set-Content "RENDER_DEPLOYMENT_INSTRUCTIONS.md" $instructions -Encoding UTF8
Write-Host "Deployment instrukcije kreirane" -ForegroundColor Green

# Završetak
Write-Host "`n=== DEPLOYMENT PRIPREMA ZAVRŠENA ===" -ForegroundColor Green
Write-Host "Kreirani fajlovi:" -ForegroundColor Yellow
Write-Host "  ✅ settings.py (modifikovan za HTTPS)" -ForegroundColor White
Write-Host "  ✅ .env.production" -ForegroundColor White
Write-Host "  ✅ render.yaml" -ForegroundColor White
Write-Host "  ✅ requirements.txt (ažuriran)" -ForegroundColor White
Write-Host "  ✅ gunicorn.conf.py" -ForegroundColor White
Write-Host "  ✅ build.sh" -ForegroundColor White
Write-Host "  ✅ RENDER_DEPLOYMENT_INSTRUCTIONS.md" -ForegroundColor White
Write-Host "  ✅ $backupPath (backup)" -ForegroundColor White

Write-Host "`nSledeći koraci:" -ForegroundColor Cyan
Write-Host "1. Pregledaj RENDER_DEPLOYMENT_INSTRUCTIONS.md" -ForegroundColor White
Write-Host "2. Commituj promene u Git" -ForegroundColor White
Write-Host "3. Kreiraj Render Web Service" -ForegroundColor White
Write-Host "4. Konfiguriši environment variables" -ForegroundColor White
Write-Host "5. Deploy aplikaciju" -ForegroundColor White

Write-Host "`n🚀 Spremno za deployment na Render!" -ForegroundColor Green
