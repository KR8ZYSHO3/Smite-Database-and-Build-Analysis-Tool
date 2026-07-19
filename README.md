# SMITE 2 Database & Build Analysis Tool

**SMITE 2 only** — gods, abilities, items, patch notes, patch-weighted tier lists, and Conquest builds  
(**1 starter + 6 items**, max **3 Active** shop items; relics separate).

**Repo:** [github.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool](https://github.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool)

---

## Live web GUI (works now)

GitHub Pages on this account is broken (every Pages deploy dies with **`startup_failure`** / never runs jobs).  
So the site is served from the `docs/` folder on **jsDelivr** (pulls straight from GitHub — no Pages, no Actions).

### **[Open the web app →](https://cdn.jsdelivr.net/gh/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool@main/docs/index.html)**

Direct URL:

```
https://cdn.jsdelivr.net/gh/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool@main/docs/index.html
```

Backup mirror:

```
https://raw.githack.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool/main/docs/index.html
```

Tabs: **Tier List · Gods · Conquest Builds · Items**

> Use scope **`overall`** for the full S-tier list (~11).  
> Role scopes (Mid, Jungle, …) only show ~3 S-tier gods each.

After you push updates to `main`, CDN cache can lag a few minutes. Hard-refresh the tab if data looks old.

---

## Desktop GUI (Windows)

```powershell
cd path\to\Smite-Database-and-Build-Analysis-Tool
pip install -r requirements.txt
python -m smite2db.gui
```

Or double-click `launch_gui.bat`.

---

## Optional: your own free URL (Netlify Drop)

If you want a short link like `https://something.netlify.app` (still no GitHub Pages):

1. Open **[app.netlify.com/drop](https://app.netlify.com/drop)** (free account)
2. Drag the entire **`docs`** folder onto the page
3. Netlify gives you a live HTTPS URL immediately

Repo also has `netlify.toml` / `vercel.json` / `render.yaml` if you prefer “connect GitHub” on those hosts.

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

# Export JSON for the web GUI
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
| **Web GUI** | Static site in `docs/` (CDN / Netlify / any static host) |

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

## Why not GitHub Pages?

This repo’s Pages builds never start (`startup_failure`, 0 jobs) even with  
**Deploy from a branch → main → /docs**. That is a GitHub-side Actions/Pages issue, not missing files.  
CDN hosting avoids that path entirely.

---

## Notes

- Statistical model from public wiki data — **not** official win rates.
- Active items: SMITE 2 allows **at most 3** shop actives in inventory.
- Not affiliated with Hi-Rez / Titan Forge / SMITE 2.

## License

Personal / community project — use at your own risk. Game content belongs to Hi-Rez.
