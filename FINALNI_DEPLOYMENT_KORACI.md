# 🚀 TOVAR TAXI - FINALNI DEPLOYMENT KORACI

## ✅ PRIPREMA ZAVRŠENA
Sve sigurnosne postavke su konfigurisane:
- SESSION_COOKIE_SECURE = True
- SECURE_SSL_REDIRECT = True  
- CSRF_COOKIE_SECURE = True
- HSTS headers aktivirani
- render.yaml optimizovan

## 📋 SLEDEĆI KORACI ZA RENDER DEPLOYMENT

### 1. Git Commit & Push
```bash
git add .
git commit -m "Production ready: HTTPS security settings configured"
git push origin main
```

### 2. Render Setup
1. Idi na **https://render.com**
2. Klikni **"New +"** → **"Web Service"**
3. Konektuj GitHub/GitLab repository
4. Izaberi **tovar-taxi-by-nesako** repo

### 3. Render Konfiguracija
**Build Settings:**
- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command:** `gunicorn tovar_taxi.wsgi:application`
- **Environment:** Python 3

### 4. Environment Variables (OBAVEZNO!)
Dodaj u Render Dashboard → Environment:
```
DEBUG=False
SECRET_KEY=[Auto-generate ili kreiraj novi]
ALLOWED_HOSTS=your-app-name.onrender.com
PYTHON_VERSION=3.11.0
WEB_CONCURRENCY=4
```

### 5. Database Setup
1. U Render Dashboard: **"New +"** → **"PostgreSQL"**
2. Kreiraj database sa imenom: **tovar-taxi-db**
3. Konektuj sa Web Service
4. DATABASE_URL će biti automatski dodat

### 6. Deploy Process
1. Klikni **"Create Web Service"**
2. Čekaj build process (5-10 minuta)
3. Proveri logs za greške

### 7. Post-Deployment
**Admin pristup:**
- URL: `https://your-app.onrender.com/admin/`
- Kreiraj superuser preko Render Shell:
```bash
python manage.py createsuperuser
```

**Import korisnika:**
1. Eksportuj sa localhost: `/admin/auth/user/` → Action → "📤 Izvezi korisnike (JSON za Render)"
2. Importuj na produkciju: `/admin/auth/user/import-users/`

### 8. Testiranje
Testiraj sledeće funkcionalnosti:
- ✅ Login/Logout (30-dnevno pamćenje)
- ✅ Registracija naručilaca/prevoznika
- ✅ Dashboard-ovi
- ✅ Kreiranje pošiljki
- ✅ Admin panel
- ✅ Import/Export korisnika

### 9. SSL Verifikacija
Proveri da li su aktivni:
- 🔒 HTTPS redirect
- 🔒 Secure cookies
- 🔒 HSTS headers

### 10. Performance Monitoring
- Render automatski prati performance
- Proveri logs u Dashboard
- Konfiguriši alerts za downtime

## 🎯 FINALNI CHECKLIST
- [ ] Git push završen
- [ ] Render Web Service kreiran
- [ ] PostgreSQL database kreiran i konektovan
- [ ] Environment variables podešeni
- [ ] Deployment uspešan
- [ ] Admin panel dostupan
- [ ] Korisnici importovani
- [ ] SSL/HTTPS funkcioniše
- [ ] Login persistence radi (30 dana)
- [ ] Sve stranice se učitavaju

## 🆘 TROUBLESHOOTING
**Build fails:**
- Proveri requirements.txt
- Proveri Python version compatibility

**Database errors:**
- Proveri DATABASE_URL connection
- Pokreni migracije: `python manage.py migrate`

**Static files missing:**
- Proveri STATIC_ROOT settings
- Pokreni: `python manage.py collectstatic`

**HTTPS redirect loop:**
- Proveri SECURE_PROXY_SSL_HEADER settings
- Render automatski dodaje X-Forwarded-Proto header

## 📞 PODRŠKA
Za dodatnu pomoć:
- Render Documentation: https://render.com/docs
- Django Deployment Guide
- Kontakt NESAKO tim

---
**🎉 Uspešan deployment znači da je Tovar Taxi spreman za produkciju!**
