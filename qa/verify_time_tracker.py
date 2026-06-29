#!/usr/bin/env python3
"""Regression checks for the Time Tracker 2.0 hardening work."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text(encoding="utf-8")
sw = (ROOT / "sw.js").read_text(encoding="utf-8")

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


# Storage must be fault-tolerant.
check("function LS(key, fallback = null)" in html, "safe LS(key, fallback) helper missing")
check("const LS=k=>JSON.parse" not in html, "unsafe localStorage JSON.parse shortcut still present")
check("function SS(key, value)" in html, "safe SS(key, value) helper missing")
check("function removeLS(key)" in html, "safe removeLS(key) helper missing")
check(html.count("localStorage.removeItem") <= 1, "direct localStorage.removeItem calls outside helper remain")

# Dates must be local dates, not UTC slices.
check("function localDateISO" in html, "localDateISO helper missing")
check("toISOString().slice(0,10)" not in html, "UTC date slice still present")

# Rendering must not inject user-controlled entry values with innerHTML.
check("content.innerHTML = `" not in html, "month entry rendering still uses template innerHTML")
check("appendTextLine" in html or "appendLine" in html, "safe text rendering helper missing")

# Validation must be centralized.
check("function clampNumber" in html, "clampNumber helper missing")
check("function isValidTimeHHMM" in html, "isValidTimeHHMM helper missing")
check("function normalizeEntry" in html, "backup/entry normalization missing")
check("function normalizeSettings" in html, "settings normalization missing")
check("TIME_RE" in html or "/^([01]" in html, "strict HH:MM validation regex missing")

# Running session should snapshot values at start.
check(re.search(r"const\s+run\s*=\s*\{[\s\S]*?project[\s\S]*?pause[\s\S]*?extraMin[\s\S]*?\};[\s\S]*?SS\('running',\s*run\)", html) is not None,
      "running session does not snapshot project/pause/extraMin")
check("if(!SS('entries', normalizeEntriesForStorage(entries)))" in html or "if(!SS('entries', entries))" in html, "stopWork does not abort when entries save fails")

# Backup import should whitelist/normalize, not write arbitrary settings/entries.
check("function normalizeBackupData" in html, "normalizeBackupData helper missing")
check("function getEntries" in html and "Array.isArray(entries)" in html, "safe getEntries Array.isArray helper missing")
check("cdn.jsdelivr.net" not in html, "PDF libraries still load from external CDN")
check("Object.keys(s).forEach(k=> SS(k, s[k]))" not in html, "backup import still writes arbitrary settings keys")
check("SS('entries', json.data.entries || [])" not in html, "backup import still stores raw entries")
check("SS('entries', normalized.entries)" in html, "backup import does not store normalized entries")
check("nur, wenn die App geöffnet ist" in html, "backup UI does not explain auto-backup limitation")
check("localStorage.setItem(BACKUP_KEY" not in html, "fake persistent backup handle still written to localStorage")

# Accessibility basics.
check('aria-label="Einstellungen öffnen"' in html, "settings button aria-label missing")
check('aria-label="Info öffnen"' in html, "info button aria-label missing")
check('role="dialog"' in html, "modal dialog role missing")
check('aria-modal="true"' in html, "modal aria-modal missing")
check("Escape" in html and "closeTopModal" in html, "Escape modal close handler missing")

# V2.1 UI and export improvements.
check('id="todayHero"' in html, "modern timer hero section missing")
check('id="startStopBtn"' in html and "function toggleWork" in html, "single Start/Stop action missing")
check('id="recentProjects"' in html and "function renderProjectChips" in html, "project quick-select chips missing")
check('function exportMonthCsv' in html and "CSV Export" in html, "CSV export missing")
check("CSV formula injection" in html, "CSV export formula-injection guard missing")
check('month-entry-card' in html and 'entry-badge' in html, "modern monthly entry cards missing")
check('id="targetProgressFill"' in html and "function updateDashboard" in html, "daily progress dashboard missing")

# V2.2 workflow changes: app version visible, Zusatz only editable in month entry modal.
check('APP_VERSION' in html and 'id="appVersion"' in html and 'Version' in html, "Info modal version number missing")
check('for="extra"' not in html and 'id="extra"' not in html, "dashboard Zusatz input still present")
check('id="editExtra"' in html and 'for="editExtra"' in html, "edit modal Zusatz input missing")
check("extraMin: 0" in html, "new running sessions should start with Zusatz 0")
check(re.search(r"const\s+extraMin\s*=\s*clampNumber\(editExtra\.value", html) is not None,
      "saveEdit does not read Zusatz from edit modal")

# V2.3 Mac edit-time regression: visible start/stop fields must be manually editable.
check('time-text-input' in html and 'time-picker-wrap' in html, "Mac-editable time input classes missing")
check(re.search(r'id="editStartDisplay"[^>]*readonly', html) is None, "Start display time field is still readonly")
check(re.search(r'id="editEndDisplay"[^>]*readonly', html) is None, "Stop display time field is still readonly")
check('function readEditableTime' in html, "saveEdit does not read editable visible time fields")
check('time-picker-wrap .native-picker' in html, "native time picker still covers the whole editable field")

# V2.4 daily pause rule: the 4-hour threshold is per calendar day, not per single Start/Stop entry.
check('function getShiftSpanMinutes' in html, "gross shift-duration helper missing")
check('const DAILY_PAUSE_THRESHOLD_MINUTES = 4 * 60' in html, "daily pause threshold constant missing")
check('function getRequestedPauseMinutes' in html, "requested pause helper missing")
check('pauseRequested' in html, "entered/requested pause is not preserved for later daily recalculation")
check('function applyDailyPauseRules' in html, "daily pause aggregation helper missing")
check('function normalizeEntriesForStorage' in html, "storage normalization helper missing")
check(re.search(r'const\s+dailyGrossByDate\s*=\s*new\s+Map\(', html) is not None,
      "daily pause rule does not group gross work minutes by date")
check(re.search(r'dayGross\s*<\s*DAILY_PAUSE_THRESHOLD_MINUTES\s*\?\s*0\s*:', html) is not None,
      "pause is not zeroed based on total daily gross work under 4 hours")
check(re.search(r'getNormalizedEntries\(\)[\s\S]*?return\s+applyDailyPauseRules\(rows\)', html) is not None,
      "getNormalizedEntries does not apply daily pause rules")
check('normalizePauseMinutes(startHM, endHM, raw.pause)' not in html,
      "normalizeEntry still applies the old per-shift pause rule")
check(re.search(r"SS\('entries',\s*normalizeEntriesForStorage\(entries\)\)", html) is not None,
      "entry saves do not recalculate day-level pauses before storage")

# V2.5 Bottom Toolbar / Variante A navigation.
check('id="bottomToolbar"' in html and 'role="tablist"' in html, "bottom toolbar tablist missing")
check('data-app-tab="today"' in html and 'data-app-tab="month"' in html and 'data-app-tab="stats"' in html and 'data-app-tab="more"' in html,
      "toolbar does not expose Heute/Monat/Statistik/Mehr tabs")
check('id="tabToday"' in html and 'id="tabMonth"' in html and 'id="tabStats"' in html and 'id="tabMore"' in html,
      "tab panels for Variante A missing")
check('function selectAppTab' in html, "tab switching helper missing")
check('function isMonthTabActive' in html, "month tab active helper missing")
check(re.search(r'function\s+selectAppTab[\s\S]*?safe\s*===\s*[\'\"]month[\'\"][\s\S]*?renderSelectedMonth\(', html) is not None,
      "month tab selection does not render the monthly overview")
check('aria-selected="true"' in html and 'aria-controls="tabToday"' in html, "toolbar accessibility attributes missing")
check('id="moreActions"' in html and 'Export' in html and 'Backup' in html, "Mehr tab action hub missing")

# V2.6 UX upgrade: polished Today, grouped/filterable Month, sectioned More hub.
check('id="heroProgressPercent"' in html and 'id="heroRemaining"' in html and 'id="heroSession"' in html,
      "Today hero does not expose prominent percent/remaining/session metrics")
check('id="todayInsightCard"' in html and 'id="todayEntryCount"' in html and 'id="todayPauseTotal"' in html,
      "Today quick insight card missing")
check('function updateTodayInsights' in html and 'todayInsightCard' in html,
      "Today dashboard insights are not updated from JS")
check('id="monthSummary"' in html and 'id="monthProjectFilter"' in html,
      "Month summary and project filter controls missing")
check('function getSelectedMonthProjectFilter' in html and 'function populateMonthProjectFilter' in html,
      "Month project filtering helpers missing")
check('month-day-group' in html and 'month-day-header' in html,
      "Month entries are not grouped by day")
check('function buildMonthSummary' in html and 'month-summary-grid' in html,
      "Month summary KPI cards missing")
check('more-section' in html and 'more-section-title' in html and 'danger-zone' in html,
      "Mehr tab is not organized into professional sections")
check('moreExportContext' in html and 'function updateMoreExportContext' in html,
      "Mehr export context indicator missing")
check('function ensureYearOption' in html and 'ensureYearOption(y)' in html,
      "Month year navigation does not handle years outside the initial select range")

# V2.7 cleanup: no legacy duplicate controls or unused styling/function leftovers.
check('class="export-actions"' not in html, "duplicate month export buttons still present; export belongs in More hub")
check('Backup jetzt erstellen' not in html and 'Alles löschen</button>' not in html,
      "duplicate settings action buttons still present")
check('class="info-btn"' not in html and 'class="gear-btn"' not in html,
      "duplicate topbar Settings/Info buttons still present")
check('function toggleMonth' not in html and 'function openNativePicker' not in html,
      "unused legacy JS helpers still present")
check('.more-actions' not in html and '.form-grid' not in html and '.footer-btn' not in html,
      "unused legacy CSS selectors still present")

# V2.6.1 Today ordering and project-card polish.
check('id="projectCard"' in html and 'project-card-head' in html and 'input-shell project-input-shell' in html,
      "polished project card structure missing")
check(html.find('id="projectCard"') != -1 and html.find('id="todayInsightCard"') != -1 and html.find('id="projectCard"') < html.find('id="todayInsightCard"'),
      "Heute im Überblick card must sit below the project card")
check('pause-row' in html and 'project-note' in html and 'pause-input-shell' in html,
      "project card pause layout missing")
check('project-recent-dropdown' in html and 'project-recent-list' in html and 'recentProjectsSummary' in html,
      "recent projects must be an expandable list in project card")
check('slice(0,10)' in html and 'Letzte Projekte öffnen' in html,
      "recent project list must show up to 10 saved projects")
check('project-recent-item' in html and 'role = \'option\'' in html,
      "recent project list items are not rendered as selectable list options")

# V2.7.0 Vacation feature and running-pause editing.
check('id="vacationModal"' in html and 'id="vacationFrom"' in html and 'id="vacationTo"' in html,
      "vacation add modal with from/to date fields missing")
check('function addVacationRange' in html and 'function buildVacationEntry' in html and 'const VACATION_TYPE' in html,
      "vacation entry creation helpers missing")
check('function isConfiguredWorkday' in html and 'vacationIncludeWeekends' in html,
      "vacation workday/weekend selection logic missing")
check('vacation-entry-card' in html and 'Ganztägiger Urlaub' in html,
      "month overview does not render vacation entries as dedicated cards")
check('function updateRunningPause' in html and 'pause.oninput' in html and 'getRunningSessionTotals' in html,
      "pause cannot be updated while a timer is running")
check('[project].forEach' in html and '[project, pause].forEach' not in html,
      "running state still disables pause input")

# V2.8.0 Absence feature: vacation + sick leave share one safe flow.
check('id="absenceType"' in html and 'value="vacation"' in html and 'value="sick"' in html,
      "absence type selector with vacation/sick options missing")
check('const SICK_TYPE' in html and 'function buildSickEntry' in html and 'function buildAbsenceEntry' in html,
      "sick leave entry creation helpers missing")
check('function isAbsenceEntry' in html and '!isAbsenceEntry(row.entry)' in html,
      "absence entries are not excluded from work pause rules")
check('sick-entry-card' in html and 'Ganztägiger Krankenstand' in html and '🤒 Krankenstand' in html,
      "month overview does not render sick leave entries as dedicated cards")
check('Abwesenheit hinzufügen' in html and 'Krankenstandstag(e)' in html,
      "absence UI copy for sick leave missing")

# V3.0.0 Statistics dashboard with charts.
check('id="statsRange"' in html and 'function updateStatsDashboard' in html,
      "statistics period selector/update helper missing")
check('id="statsTotalWork"' in html and 'id="statsAvgDay"' in html and 'id="statsTargetBalance"' in html,
      "statistics KPI cards missing")
check('id="statsDailyChart"' in html and 'id="statsProjectChart"' in html and 'id="statsWeekdayChart"' in html,
      "statistics chart containers missing")
check('id="statsAbsenceChart"' in html and 'id="statsVacationDays"' in html and 'id="statsSickDays"' in html,
      "statistics absence metrics/chart missing")
check('stats-chart-bar' in html and 'stats-progress-bar' in html and 'function renderStatsBarChart' in html,
      "statistics bar chart renderer/CSS missing")
check('function getStatsRangeInfo' in html and 'function buildStatsBuckets' in html and 'function renderStatsInsights' in html,
      "statistics aggregation helpers missing")

# Service worker must clean up old caches and version assets.
check(re.search(r'time-tracker-v\d+', sw) is not None, "service worker cache version not bumped")
check('skipWaiting' in sw, "service worker skipWaiting missing")
check('caches.keys' in sw and 'caches.delete' in sw, "service worker does not delete old caches")
check('icon-180.png' in sw, "apple touch icon missing from cache assets")

if failures:
    print("FAIL: Time Tracker hardening checks failed:")
    for idx, failure in enumerate(failures, start=1):
        print(f"{idx:02d}. {failure}")
    sys.exit(1)

print("PASS: Time Tracker hardening checks passed.")
