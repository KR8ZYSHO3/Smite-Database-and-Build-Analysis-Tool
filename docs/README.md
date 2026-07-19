# Web GUI

## Open this (live)

**https://raw.githack.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool/main/docs/standalone.html**

`standalone.html` embeds CSS, JS, and all JSON data (~1 MB). No extra fetches.

## Do not use

`https://cdn.jsdelivr.net/gh/.../docs/index.html` — jsDelivr returns HTML as **plain text**.

## Local

```powershell
cd docs
python -m http.server 8080
# http://localhost:8080/standalone.html
```

Rebuild after data refresh: `python -m smite2db.export_web`
