# Time Tracker PWA

Eine installierbare Progressive Web App zur Arbeitszeiterfassung mit Projekten, Pausen, Monatsübersicht, Abwesenheiten und Statistik-Diagrammen.

## Funktionen

- Arbeitszeit starten/stoppen
- Projekt-Schnellauswahl mit den letzten 10 Projekten
- Pausenlogik mit Tagesregel
- Monatsübersicht mit Projektfilter
- Urlaub und Krankenstand als Abwesenheiten
- Statistik-Dashboard mit Diagrammen
- PDF- und CSV-Export
- Offlinefähig durch Service Worker
- Installierbar als PWA auf iOS, Android und Desktop

## PWA

Die App enthält:

- `manifest.webmanifest`
- `sw.js`
- App-Icons in 180, 192 und 512 px
- relativen Pfadaufbau für GitHub Pages
- Offline-Cache für App-Shell und lokale Vendor-Dateien

## Lokal testen

```bash
python3 -m http.server 8916
```

Dann öffnen:

```text
http://127.0.0.1:8916/
```

## Qualitätssicherung

```bash
python3 qa/verify_time_tracker.py
node --check sw.js
```

## GitHub Pages

Empfohlene Pages-Konfiguration:

```text
Source: Deploy from a branch
Branch: main
Folder: /root
```

Danach ist die PWA typischerweise unter folgender URL erreichbar:

```text
https://<github-user>.github.io/time-tracker-pwa/
```

## Version

Aktuelle App-Version: `3.0.0`
Service Worker Cache: `time-tracker`
