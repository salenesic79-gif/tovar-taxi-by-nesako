# TOVAR TAXI - RENDER DEPLOYMENT INSTRUKCIJE

## Korak 1: Priprema
1. Commituj sve promene u Git
2. Push na GitHub/GitLab

## Korak 2: Render Setup
1. Idi na https://render.com
2. Kreiraj novi Web Service
3. Konektuj GitHub/GitLab repo
4. Podesi sledeÄ‡e:
   - Build Command: chmod +x build.sh && ./build.sh
   - Start Command: gunicorn tovar_taxi.wsgi:application
   - Environment: Python 3

## Korak 3: Environment Variables
Dodaj sledeÄ‡e environment variables u Render:
- DEBUG=False
- SECRET_KEY=[generiÅ¡i novi]
- ALLOWED_HOSTS=your-app-name.onrender.com
- DATABASE_URL=[Render Ä‡e automatski kreirati]

## Korak 4: Domain Setup
1. U Render dashboard, idi na Settings
2. Dodaj custom domain (opciono)
3. SSL Ä‡e biti automatski konfigurisan

## Korak 5: Database
1. Kreiraj PostgreSQL database u Render
2. Konektuj sa web service
3. Migracije Ä‡e se pokrenuti automatski

## Korak 6: Admin Access
- URL: https://your-app.onrender.com/admin/
- Username: admin
- Password: admin123 (PROMENI ODMAH!)

## Korak 7: Import korisnika
1. Eksportuj korisnike sa localhost: /admin/auth/user/
2. Importuj na produkciju: /admin/auth/user/import-users/

## Sigurnosne postavke aktivirane:
âœ… HTTPS redirect
âœ… Secure cookies
âœ… HSTS headers
âœ… XSS protection
âœ… CSRF protection
âœ… Content type sniffing protection

## Backup fajlovi kreirani:
- settings_backup_*.py (originalni settings)
- .env.production (environment variables)

## PodrÅ¡ka:
Za pomoÄ‡ kontaktiraj NESAKO tim.
