"""Verify OB45 refresh outputs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
meta = json.loads((ROOT / "docs/data/meta.json").read_text(encoding="utf-8"))
gods = json.loads((ROOT / "docs/data/gods.json").read_text(encoding="utf-8"))
by = {g["name"]: g for g in gods}

print("latest_patch:", meta.get("latest_patch"), meta.get("latest_patch_date"))
print("algo:", (meta.get("build_algorithm") or {}).get("version"))
print("gods:", len(gods), "Nike" in by, "Hel" in by)

for name in ("Aphrodite", "Hel", "Nike", "Yemoja", "Hachiman"):
    g = by[name]
    cbr = g.get("conquest_by_role") or {}
    print(f"\n=== {name} roles={g.get('native_roles')} ===")
    for role, path in cbr.items():
        items = [i["name"] for i in (path.get("items") or [])]
        actives = sum(1 for i in (path.get("items") or []) if i.get("is_active"))
        print(f"  {role}: {items} actives={actives} starter={path.get('starter')}")

# Serrated must be gone
blob = json.dumps(gods).lower()
print("\nserrated hits:", blob.count("serrated"))
print("sickle supports:", sum(
    1 for g in gods
    for i in ((g.get("conquest_by_role") or {}).get("Support") or {}).get("items") or []
    if "sickle" in i["name"].lower()
))
