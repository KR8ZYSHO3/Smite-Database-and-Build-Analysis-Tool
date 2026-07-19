# SMITE 2 Database & Build Analysis Tool

**SMITE 2 only** — gods, abilities, items, patch notes, patch-weighted tier lists, and Conquest builds  
(**1 starter + 6 items**, max **3 Active** shop items; relics separate).

**Repo:** [github.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool](https://github.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool)

---

## Clickable web GUI (recommended)

After GitHub Pages is enabled on this repo (`Settings → Pages → Branch: main → /docs`):

### **https://kr8zysho3.github.io/Smite-Database-and-Build-Analysis-Tool/**

Tabs: **Tier List · Gods · Conquest Builds · Items**

> Use scope **`overall`** for the full S-tier list (~11).  
> Role scopes (Mid, Jungle, …) only show ~3 S-tier gods each (top ~12% of that role).

---

## Desktop GUI (Windows)

```powershell
cd path\to\Smite-Database-and-Build-Analysis-Tool
pip install -r requirements.txt
python -m smite2db.gui
```

Or double-click `launch_gui.bat`.

---

## Install & refresh data

```powershell
git clone https://github.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool.git
cd Smite-Database-and-Build-Analysis-Tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt

# Pull latest from wiki.smite2.com
python -m smite2db.scrape

# Metrics + tier lists
python -m smite2db.analyze run

# Conquest builds (enforces ≤3 actives)
python -m smite2db.conquest_builds

# Export JSON for the web GUI / GitHub Pages
python -m smite2db.export_web
```

Local web preview:

```powershell
cd docs
python -m http.server 8080
# open http://localhost:8080
```

---

## What’s inside

| Feature | Description |
|--------|-------------|
| **Scrape** | Official [wiki.smite2.com](https://wiki.smite2.com) only (not Smite 1) |
| **Tier lists** | Patch momentum 48% · kit 28% · build 14% · novelty/stability |
| **Conquest builds** | Statistical role builds: 1 starter + 6 items · **≤3 actives** |
| **Desktop GUI** | tkinter app (`python -m smite2db.gui`) |
| **Web GUI** | Static site in `docs/` for GitHub Pages |

Database: `data/smite2.db`  
Web data: `docs/data/*.json`

---

## CLI cheatsheet

```powershell
python -m smite2db.analyze tiers --scope overall -v
python -m smite2db.analyze god Kukulkan -v
python -m smite2db.analyze momentum --entity-type god --limit 15
python -m smite2db.conquest_builds
python -m smite2db.export_web
```

---

## Notes

- Statistical model from public wiki data — **not** official win rates.
- Active items: SMITE 2 allows **at most 3** shop actives in inventory.
- Not affiliated with Hi-Rez / Titan Forge / SMITE 2.

## License

Personal / community project — use at your own risk. Game content belongs to Hi-Rez.
