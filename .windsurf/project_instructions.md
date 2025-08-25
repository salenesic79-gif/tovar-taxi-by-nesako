[PROJECT_INSTRUCTIONS]
Naslov: Windsurf Cascade — GLAVNI OPERATIVNI PRAVILNIK (B2B, Stabilnost, UX, Regresija, Mape, Bezbednost)

Kontekst:
- Projekat je Django + PWA, B2B orijentisan. Cilj je maksimalna jednostavnost korišćenja, uz kompleksnu logiku u pozadini.
- Svaka izmena mora biti izuzetno obazriva, posebno na delovima sa kojima je vlasnik zadovoljan.
- Uvek daj prioritet stabilnosti, poslovnom izgledu, funkcionalnoj logici i čitljivosti.

OPŠTA PRAVILA
1) STABILNOST I REGRESIJA PRE SVEGA
- Nikada ne uvoditi izmenu bez: (a) statičke analize, (b) testova, (c) provere uticaja na sve povezane delove (rute, kanali, template-ovi, signal-i, celery taskovi, websockets).
- Uvek pokreni regresioni set testova. Ako nešto pukne → automatski predloži i primeni popravku, pa pokreni testove ponovo.
- Ako je deo označen kao “zadovoljan sam” (SAFE AREA), NIKAD ne menjati bez eksplicitne dozvole. Ako je neophodno, predloži minimalno invazivno rešenje i traži potvrdu.

2) DIZAJN I UX (B2B STANDARD)
- Vizuelno: poslovno, čisto, bez suvišnih ukrasa. Tipografija: Inter / Roboto / Open Sans; bazna veličina 14–16px; visina reda ≥ 1.45.
- Raspored: grid/flex, jasna hijerarhija (H1–H3, podnaslovi), čitljivi razmaci (8/12/16/24 px scale).
- Komponente: primarno dugme (solid), sekundarno (outline), destruktivno (danger), neutralna (link). Uvek konzistentna stanja (hover/active/disabled).
- Forme: label iznad inputa, obavezna polja označena, inline greške, jasne poruke validacije, jednoznačni placeholder-i, “Save/Cancel” na istom mestu.
- Navigacija: levo/sidebar za B2B module, gore/topbar za globalne radnje; breadcrumb za duboke stranice; dosledni nazivi menija.
- Responsive: breakpointi (sm/md/lg/xl); na mobilnom prioritet primarnih akcija; nikad “skrivena” kritična radnja iza 3 klika.
- Pristupačnost: ARIA role, kontrast AA, fokus obrisi, pristupačnost tastaturom (Tab/Enter/Esc), alt tekst za ikone/ilustracije.

3) PERFORMANSE I BUDŽETI
- Front: LCP < 2.5s (mobilno), interaktivnost < 200ms gde je moguće; bundle minimizovan; lazy-load mapa i teških modula.
- Back/API: p95 < 300ms za ključne rute; p99 < 800ms; paginacija obavezna; N+1 upiti eliminisani.
- PWA: manifest + service worker; offline fallback; Add to Home Screen; caching strategije (stale-while-revalidate za list-e, network-first za kritične API).

4) MAPE I GEOLOKACIJA — TAJMING I GATE-OVI
- Uvodi tek nakon stabilizacije: (a) auth/roles, (b) entiteta (order/driver/route), (c) osnovnog UI layouta.
- Preduslovi (obavezni “ready” signali):
  - API za lokacije definisan i dokumentovan
  - Event kanal za real-time (Django Channels/WebSocket) radi stabilno
  - Feature flag MAPS_ENABLED postoji (default: false u produkciji)
- Integracija redosledom:
  1) statička mapa + marker,
  2) geokodiranje i rutiranje,
  3) real-time praćenje i re-route,
  4) notifikacije i edge-cases (GPS off, permissions).
- Ako neki preduslov fali → NE uvoditi mape; umesto toga predložiti korake i ček-liste.

5) BEZBEDNOST I TAJNE
- NIKAD ne hardkodovati kredencijale; sve kroz ENV (Cascade/Render sekreti).
- Obavezno: HTTPS, CSRF, XSS zaštita (escape), validacija inputa, rate-limit kritičnih ruta, audit log za finansijske radnje.
- Payment provajder (Stripe/PayPal/Adyen): koristiti zvanične SDK; kartice NE dodirivati server-side; webhook validacija; idempotency.
- Dependecy sigurnost: bandit/safety/snyk; lock fajl; redovna ažuriranja.

6) MIGRACIJE, PODACI I ROLLBACK
- Svaka DB migracija mora biti (a) bezbedna za online deploy, (b) idempotentna, (c) sa planom rollback-a.
- Pre migracije: “makemigrations --check” i “migrate --plan”; nakon migracije: smoke test ključnih modela.
- Backfill i data-migration u zasebnim fajlovima; izbegavati dugotrajne lock-ove (chunk batch).

7) GRANANJE, COMMITS I REVIEW
- Strategija: main (stabilno), develop (integraciona), feature/*, hotfix/*.
- Commit stil: Conventional Commits (feat:, fix:, perf:, refactor:, docs:, chore:, test:).
- Svaka funkcionalnost preko PR; automatski testovi + security + UI snapshot pre merg-a.
- Auto-fix dozvoljen za lint/style/low-risk; za high-risk (auth, payments, migrations) — obavezno traži potvrdu.

8) OBSERVABILNOST I KVALITET
- Logovi bez PII; strukturisani; error budget definisan.
- Health: /healthz i /readiness; SLO: uptime 99.9% za ključne rute.
- Monitoring: hvataj greške klijenta (PWA) i servera; predloži remedijaciju.

9) PROCES NADOGRADNJE
- Pre svake izmene: plan uticaja; posle izmene: regresija, UI review, A/B (ako potrebno), rollout strategija (canary 10% → 100%).
- Uvek pripremi fallback (feature flag OFF, brzi rollback).

10) INTEGRACIJA NAJBOLJIH PRAKSI IZ SRODNIH APLIKACIJA
- Poredi tokove sa najboljim B2B aplikacijama i relevantnim logističkim/dostavnim servisima.
- Uzimaj inspiraciju za: tok naručivanja, praćenje, notifikacije, pretragu, filtere, batch operacije, exporte.
- Uvek navedi izvor inspiracije i obrazloženje.

11) KONKRETNE SMERNICE ZA MAP/ROUTING UI
- Panel sa kontrolama desno ili levo (dosledno); mapa zauzima preostali prostor; fiksna visina header-a.
- Jasna dugmad: “Start tracking”, “Pause”, “Re-center”, “Route to…”.
- State indikatori permissions: GPS off, no signal, stale data (<timestamp).
- Nemoj blokirati aplikaciju ako mapa zakaže — degradiraj graciozno.

12) KADA KORISNIK KAŽE “ZADOVOLJAN SAM”
- Obeleži taj kod/komponentu u SAFE_AREAS.md (sa opisom).
- Svaka naredna izmena u SAFE delu — prvo simuliraj uticaj, prikaži diff i traži eksplicitnu dozvolu.

13) DODATNI PREDLOZI ZA UNAPREĐENJE
- Uvesti feature flags (MAPS_ENABLED, NEW_CHECKOUT, FAST_TABLES).
- Uvesti precommit hookove (lint/test) i format automatiku.
- Uvesti vizuelnu regresiju (screenshot diff) za ključne ekrane.
- Uvesti “design tokens” (spacing, font-size, radius) radi doslednosti.

KRAJNJI CILJ
- Aplikacija mora biti jednostavna za korisnike, stabilna pod opterećenjem, vizuelno profesionalna i logična, sa automatizovanom regresijom i pažljivim uvođenjem mapa/geolokacije. Svaka promena se planira, proverava i objavljuje bez lomljenja postojećeg.


[END_PROJECT_INSTRUCTIONS]

## APPLICATION FLOW SPECIFICATION

### Core User Flows

#### 1. Authentication Flow
```
Landing Page → Register/Login → Profile Setup → Dashboard
```

#### 2. Order Creation Flow  
```
Dashboard → Create Order → Select Vehicle Type → Enter Route Details → Confirm & Submit
```

#### 3. Order Management Flow
```
Dashboard → Order List → View Details → Update Status → Track Progress
```

#### 4. Driver/Vehicle Flow
```
Dashboard → Vehicle Management → Add/Edit Vehicle → Assign to Orders
```

#### 5. Payment Flow
```
Order Confirmation → Payment Method Selection → Process Payment → Payment Confirmation → Receipt
```

#### 6. Notification Flow
```
Order Status Change → Generate Notification → Send to User/Driver → Update UI
```

### Implementation Priority (Following Project Rules)
1. **Phase 1**: Stabilize auth system (rules 1, 12)
2. **Phase 2**: Core order entities (rules 6, 11) 
3. **Phase 3**: Basic UI flows (rules 2, 3)
4. **Phase 4**: Maps integration (rules 4 - only after prerequisites)
5. **Phase 5**: Payment integration (rules 5 - security first)
6. **Phase 6**: Real-time notifications

flow:
  name: B2B Master Pipeline (Stable+UX+Maps-Gated)
  triggers:
    - on_push
    - on_pull_request
    - manual

  env:
    PYTHONUNBUFFERED: "1"
    PYTHONUTF8: "1"
    DJANGO_SETTINGS_MODULE: "project.settings"
    CI: "true"
    MAPS_ENABLED: "false"   # promeni na true tek kad preduslovi budu ispunjeni
    SAFE_AREAS_FILE: "SAFE_AREAS.md"

  steps:
    - name: Checkout
      run: |
        git clone ${{ env.REPO_URL }} repo
        cd repo
        echo "✅ Repo povučen"

    - name: Detect stack & install deps
      run: |
        cd repo
        if [ -f "requirements.txt" ]; then
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest bandit safety black isort
        fi
        if [ -f "package.json" ]; then
          npm ci || npm install
          # lighthouse i playwright za opcioni UI test
          npx --yes playwright install --with-deps || true
          npm i -D @lhci/cli || true
        fi
        echo "✅ Zavisnosti instalirane"

    - name: Django checks (no side-effects)
      run: |
        cd repo
        python manage.py check --deploy
        python - <<'PY'
from django.conf import settings
print("ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)
PY
        echo "✅ Basic Django check OK"

    - name: DB migrations (plan & apply)
      run: |
        cd repo
        python manage.py makemigrations --check || true
        python manage.py migrate --plan || true
        python manage.py migrate
        echo "✅ Migracije OK"

    - name: Static & PWA sanity
      run: |
        cd repo
        # PWA fajlovi potrebno: manifest + service worker
        test -f app/static/manifest.webmanifest || echo "::warning::manifest.webmanifest nedostaje"
        test -f app/static/service-worker.js || echo "::warning::service-worker.js nedostaje"
        # Odrađujemo dry run za collectstatic
        python manage.py collectstatic --dry-run --noinput || true
        echo "✅ Static/PWA sanity završeno"

    - name: Lint & format (non-blocking fix attempt)
      run: |
        cd repo
        set +e
        black --check . || echo "black-fail" >> ../errors.log
        isort --check-only . || echo "isort-fail" >> ../errors.log
        # (opciono) flake8 ako postoji u projektu
        if command -v flake8 >/dev/null 2>&1; then flake8 || echo "flake8-fail" >> ../errors.log; fi
        set -e
        echo "✅ Lint/format provereno"

    - name: Security scan
      run: |
        cd repo
        set +e
        bandit -r . -lll || echo "bandit-fail" >> ../errors.log
        safety check --full-report || echo "safety-fail" >> ../errors.log
        set -e
        echo "✅ Security sken završen"

    - name: Tests (backend + optional e2e)
      run: |
        cd repo
        set +e
        if [ -f "pytest.ini" ] || [ -d "tests" ]; then
          pytest || echo "pytest-fail" >> ../errors.log
        else
          echo "::notice::Nema pytest testova, preskačem"
        fi
        # (opciono) e2e ili vizuelna regresija ako postoji Playwright config
        if [ -f "playwright.config.ts" ] || [ -f "playwright.config.js" ]; then
          npx playwright test || echo "playwright-fail" >> ../errors.log
        fi
        set -e
        echo "✅ Test korak završen"

    - name: UI/Lighthouse check (soft gate)
      run: |
        cd repo
        if [ -f "package.json" ] && [ -f "scripts/start" ] || [ -f "scripts:dev" ]; then
          echo "::notice::Može se dodati LHCI ako je definisan start skript"
          # Primer (lokalni audit u CI je težak bez servera); ostavljamo kao budući korak
        else
          echo "::notice::Preskačem Lighthouse (nema front build/start skripta)"
        fi

    - name: Soft gate for MAPS integration
      run: |
        cd repo
        if [ "${MAPS_ENABLED}" != "true" ]; then
          echo "::notice::MAPS_ENABLED=false — mapa/geolokacija su trenutno zaključani dok se ne ispune preduslovi."
          echo "::notice::Preduslovi: stabilan auth/roles, definisani entiteti (orders/drivers/routes), stabilan realtime kanal."
        else
          echo "✅ MAPS_ENABLED=true — dozvoljena integracija mapa."
        fi

    - name: Policy: SAFE AREAS protection
      run: |
        cd repo
        if [ -f "${SAFE_AREAS_FILE}" ]; then
          echo "SAFE areas postoje:"
          cat ${SAFE_AREAS_FILE} || true
          echo "::notice::Nemoj menjati SAFE delove bez eksplicitne dozvole vlasnika."
        else
          echo "::notice::SAFE_AREAS.md nije nađen; preporuka je da se kreira i popuni."
        fi

    - name: AI — Analyze & Repair (conservative)
      uses: ai/repair@security_backend_frontend
      with:
        repo_path: ./repo
        errors_file: ./errors.log
        strategy: "conservative"         # minimalne, bezbedne izmene
        respect_safe_areas: true          # NE diraj SAFE delove bez dozvole
        b2b_ux_guidelines: true
        maps_feature_flag: MAPS_ENABLED
        requests:
          - "Prođi kroz sve prijavljene greške i predloži fix bez narušavanja postojećeg toka."
          - "Ako UI poravnavanje i semantika nisu konzistentni, predloži minimalne korekcije (grid/flex, spacing, label/inputs)."
          - "Ukloni N+1 upite, uvedi select_related/prefetch_related gde je potrebno."
          - "Za forms & validaciju, uvedi jednoznačne poruke i inline error state."
          - "Za mape: NEMOJ uvoditi ništa dok MAPS_ENABLED != true i dok preduslovi nisu ispunjeni."
          - "Ako je deo označen kao SAFE, samo predloži komentar; ne menjaj kod."
        commit: true

    - name: Re-run critical checks after AI fixes
      run: |
        cd repo
        rm -f ../errors.log
        set +e
        black --check . || echo "black-fail" >> ../errors.log
        isort --check-only . || echo "isort-fail" >> ../errors.log
        bandit -r . -lll || echo "bandit-fail" >> ../errors.log
        safety check --full-report || echo "safety-fail" >> ../errors.log
        if [ -f "pytest.ini" ] || [ -d "tests" ]; then
          pytest || echo "pytest-fail" >> ../errors.log
        fi
        set -e
        if [ -s ../errors.log ]; then
          echo "::warning::Još uvek ima problema nakon AI ispravki."
        else
          echo "✅ AI ispravke prošle sve proverke."
        fi

    - name: Deploy gate (only if clean)
      run: |
        cd repo
        if [ -s ../errors.log ]; then
          echo "::warning::Preskačem deploy jer postoje problemi."
          exit 0
        fi
        echo "✅ Spreman za deploy; pokreni Render deploy step ako je konfigurisan."

    # (opciono) ovde može ići Render deploy korak ako koristiš CLI ili API

  artifacts:
    - path: repo
      name: source_after_fixes

DODATNE SMERNICE (AI pomoćniku i pipeline-u):
- Ako detektuješ “razbacana” dugmad ili nelogične rute: predloži mapu navigacije, konsoliduj akcije, uvedi jasne CTA.
- Ako PWA datoteke nedostaju, generiši minimalno ispravan manifest.webmanifest i service-worker.js (bez agresivnog cache-a) i traži potvrdu pre uključivanja.
- Uvek koristi feature flagove za nove veće funkcije (ex: NEW_CHECKOUT, MAPS_ENABLED).
- Ako korisnik izjavi “zadovoljan sam ovim delom”, dodaj opis u SAFE_AREAS.md sa datim commit hash-om i komponentama; sve buduće izmene samo uz eksplicitnu potvrdu.
- Pre svake DB migracije sa promenom šeme, pripremi plan rollback-a i test backfill skriptu (mala batch obrada).
- Za B2B tabele: uvedi sortiranje, filtere, eksport (CSV/Excel), jasne status badge-ve i prazna stanja sa uputstvom.
- Za forme: prikaži validacije pre submit-a; za duge forme koristi stepper/wizard; za kritične akcije potvrdu (confirm dialog).
- Za performanse: obavezno memoizuj teške izračune na frontu; na backendu koristi select_related/prefetch_related; za liste paginaciju i “query param sync” u URL.
- Za mape: kada MAPS_ENABLED postane true, uvedi modularno (map component izolovan), sa jasnim props/state, bez side-effecta na ostali UI; fallback (tekstualne koordinate) kada mapa nije dostupna.
- Za release-e: koristi semantic versioning; generiši CHANGELOG; canary deploy kada je moguće; prebacivanje na 100% samo ako health-check i error rate izgledaju dobro.