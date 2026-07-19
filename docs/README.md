# Web GUI (static)

Open **`index.html`** after a local server or any static host.

## Live links (no GitHub Pages required)

GitHub Pages is unreliable on this repo (Actions `startup_failure`). Use:

### Recommended (always current `@main`)

**https://cdn.jsdelivr.net/gh/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool@main/docs/index.html**

### Alternate

**https://raw.githack.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool/main/docs/index.html**

## Local

```powershell
cd docs
python -m http.server 8080
# http://localhost:8080
```

## Pretty custom URL (optional, free)

1. [Netlify Drop](https://app.netlify.com/drop) — drag this whole `docs` folder  
2. Or connect the GitHub repo in Netlify / Vercel / Render (configs in repo root)
