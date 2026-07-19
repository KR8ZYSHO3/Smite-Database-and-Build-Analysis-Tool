# Web GUI (GitHub Pages)

This folder is the **clickable browser UI**.

After enabling GitHub Pages (Settings → Pages → Deploy from branch → `/docs`):

**https://kr8zysho3.github.io/Smite-Database-and-Build-Analysis-Tool/**

Local preview (required — `file://` cannot fetch JSON):

```powershell
cd docs
python -m http.server 8080
# open http://localhost:8080
```

Refresh exported data from the SQLite DB:

```powershell
python -m smite2db.export_web
```
