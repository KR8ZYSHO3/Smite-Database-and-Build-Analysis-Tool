# SMITE 2 Database & Build Analysis Tool

**SMITE 2 only** — gods, abilities, items, patch notes, patch-weighted tier lists, and Conquest builds  
(**1 starter + 6 items**, max **3 Active** shop items; relics separate).

**Repo:** [github.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool](https://github.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool)

---

## Live web GUI (use this link)

**Do not use jsDelivr for the HTML page** — it serves `.html` as `text/plain`, so the browser shows source code instead of the app.

### **[Open the web app (standalone.html)](https://raw.githack.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool/main/docs/standalone.html)**

```
https://raw.githack.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool/main/docs/standalone.html
```

That file is **self-contained** (CSS + JS + all data embedded). One request, no multi-file CDN path issues.

Production CDN mirror (cached):

```
https://rawcdn.githack.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool/main/docs/standalone.html
```

Tabs: **Tier List · Gods · Conquest Builds · Items**

> Use scope **`overall`** for the full S-tier list (~11).  
> Role scopes (Mid, Jungle, …) only show ~3 S-tier gods each.

---

## Desktop GUI (Windows) — always works offline

```powershell
cd path\to\Smite-Database-and-Build-Analysis-Tool
pip install -r requirements.txt
python -m smite2db.gui
```

Or double-click `launch_gui.bat`.

---

## Local web preview

```powershell
cd docs
python -m http.server 8080
# open http://localhost:8080/standalone.html
# or http://localhost:8080/  (multi-file index.html)
```

---

## Optional pretty URL (Netlify Drop)

1. Open **[app.netlify.com/drop](https://app.netlify.com/drop)**
2. Drag the **`docs`** folder (or just `standalone.html`)
3. Get a `*.netlify.app` link

### Tomorrow’s deploy checklist (after Drop limit resets)

```powershell
cd path\to\Smite-Database-and-Build-Analysis-Tool
git pull
python -m smite2db.refresh          # optional: freshen data
# Local preview first:
cd docs
python -m http.server 8080
# open http://localhost:8080/
```

Then drag **`docs`** (or `docs/standalone.html`) onto Netlify Drop again.

### Local preview (no Netlify)

```powershell
python -m smite2db.refresh
cd docs
python -m http.server 8080
```

Open http://localhost:8080/ — full multi-file app. Or open `standalone.html` the same way.

---

## Install & refresh data

```powershell
git clone https://github.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool.git
cd Smite-Database-and-Build-Analysis-Tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# One command: analyze metrics + rebuild builds + export docs/
python -m smite2db.refresh

# Full wiki re-scrape then refresh:
python -m smite2db.refresh --scrape

# Or step by step:
python -m smite2db.scrape
python -m smite2db.analyze run
python -m smite2db.export_web
```

**How it thinks:** patch notes (48%) + kit metrics (28%) + Conquest build fit (14%).  
Builds and tier “build fit” share one engine. Patch **r5 axes** (damage/CD/pen/…) steer item picks.

---

## What’s inside

| Feature | Description |
|--------|-------------|
| **Scrape** | Official [wiki.smite2.com](https://wiki.smite2.com) only (not Smite 1) |
| **Tier lists** | Patch momentum 48% · kit 28% · build 14% · novelty/stability |
| **Conquest builds** | 1 starter + 6 items · **≤3 actives** |
| **Desktop GUI** | `python -m smite2db.gui` |
| **Web GUI** | `docs/standalone.html` (embedded) + multi-file `docs/` |

---

## Why GitHub Pages / jsDelivr failed

| Host | Problem |
|------|---------|
| **GitHub Pages** | Deploy workflows never start (`startup_failure`, 0 jobs) on this repo |
| **jsDelivr `…/index.html`** | Serves HTML as **`text/plain`** → you see source, not the app |
| **raw.githack standalone** | Serves **`text/html`** + data is embedded → works |

---

## Notes

- Statistical model from public wiki data — **not** official win rates.
- Active items: SMITE 2 allows **at most 3** shop actives in inventory.
- Not affiliated with Hi-Rez / Titan Forge / SMITE 2.

## License

Personal / community project — use at your own risk. Game content belongs to Hi-Rez.
