# Time Tracker PWA

Eine installierbare Progressive Web App zur Arbeitszeiterfassung mit Kunden, Projekten, Pausen, Kalender-Monatsübersicht, Abwesenheiten, Statistik-Dashboard und professionellen Monatsberichten.

## Funktionen

- Arbeitszeit starten/stoppen
- Kunden- und Projektfelder für bessere Nachweise
- Projekt-Schnellauswahl mit den letzten 10 Projekten
- Pausenlogik mit Tagesregel
- Kalenderbasierte Monatsübersicht mit antippbaren Tagen und Detailansicht
- Kompakter Kalender ohne Überdeckung durch die mobile Bottom-Navigation
- Kunden- und Projektfilter in der Monatsübersicht
- Urlaub und Krankenstand als Abwesenheiten
- Aufgeräumtes Statistik-Dashboard mit Bereichen für Überblick, Projekte, Zeiten und Abwesenheiten
- Separater Spenden-Button im Mehr-Bereich unter Einstellungen & Info
- Kunden-/Projektverteilung in der Statistik
- Professioneller PDF-Monatsbericht mit Kunde, Projekt, Firmenprofil und optionalem Logo
- CSV-Export
- Offlinefähig durch Service Worker
- Installierbar als PWA auf iOS, Android und Desktop

## PWA

Die App enthält:

- `manifest.webmanifest`
- `sw.js`
- App-Icons in 180, 192 und 512 px
- relativen Pfadaufbau für GitHub Pages
- iPhone Safe-Area-Hardening mit `viewport-fit=cover`
- Offline-Cache für App-Shell und lokale Vendor-Dateien

## Lokal testen

```bash
python3 -m http.server 8917
```

Dann öffnen:

```text
http://127.0.0.1:8917/
```

## Qualitätssicherung

```bash
python3 qa/verify_time_tracker.py
node --check sw.js
```

Zusätzlich empfiehlt sich nach UI-Änderungen:

```bash
node --check /tmp/time-tracker-phase12-scripts.js
python3 -m json.tool manifest.webmanifest
```

## GitHub Pages

Empfohlene Pages-Konfiguration:

```text
Source: Deploy from a branch
Branch: main
Folder: /root
```

Live-PWA:

```text
https://simon-psycho.github.io/time-tracker-pwa/
```

Repository:

```text
https://github.com/Simon-psycho/time-tracker-pwa
```

## Version

Aktuelle App-Version: `3.2.2`
Service Worker Cache: `time-tracker-v22`
