"""Attribute patch note lines to gods/items and score buff/nerf momentum."""

from __future__ import annotations

import re
import sqlite3
from collections import defaultdict
from typing import Any

from .stat_parse import extract_from_to


BUFF_RE = re.compile(
    r"\b(increased|increase|buff(?:ed|s)?|improved|raised|higher|added|now (?:also )?deals|"
    r"reduced cooldown|cooldown reduced|cost reduced|lower(?:ed)? cooldown)\b",
    re.I,
)
NERF_RE = re.compile(
    r"\b(decreased|decrease|reduced|reduce|nerf(?:ed|s)?|lower(?:ed)?|weaker|removed|"
    r"increased cooldown|cooldown increased|cost increased|no longer)\b",
    re.I,
)
SHIFT_RE = re.compile(r"\b(shift(?:ed)?|rework(?:ed|s)?|adjusted|changed|now\b|instead)\b", re.I)
FIX_RE = re.compile(r"\b(fix(?:ed|es)?|bug|issue|correct(?:ed)?)\b", re.I)
NEW_RE = re.compile(r"\b(new|added to the game|released|introduc)\b", re.I)

# Strong direction from explicit "from X to Y" with context keywords
INCREASE_CTX = re.compile(
    r"\b(damage|scaling|heal|shield|range|radius|duration|protections?|movement|attack speed|"
    r"lifesteal|penetration|strength|intelligence|health|mana)\b.*\bfrom\b|\bfrom\b.*\bto\b",
    re.I,
)


def _clean_entity(name: str) -> str:
    name = re.sub(r"\[\[File:[^\]]+\]\]", "", name, flags=re.I)
    name = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", name)
    name = re.sub(r"\[\[([^\]]+)\]\]", r"\1", name)
    name = re.sub(r"'{2,}", "", name)
    name = re.sub(r"^\d+px\s*", "", name.strip())
    name = re.sub(r"\s+", " ", name).strip()
    return name


def build_name_index(conn: sqlite3.Connection) -> tuple[dict[str, str], dict[str, str]]:
    """Map lowercase name -> canonical name for gods and items."""
    gods = {
        r["name"].lower(): r["name"]
        for r in conn.execute("SELECT name FROM gods")
    }
    # also slug-like variants
    for r in conn.execute("SELECT name, slug FROM gods"):
        if r["slug"]:
            gods[r["slug"].lower().replace("-", " ")] = r["name"]
        gods[r["name"].lower().replace("'", "")] = r["name"]
    items = {
        r["name"].lower(): r["name"]
        for r in conn.execute("SELECT name FROM items")
    }
    for r in conn.execute("SELECT name FROM items"):
        items[r["name"].lower().replace("'", "")] = r["name"]
        items[r["name"].lower().replace("'", "’")] = r["name"]
    return gods, items


COSMETIC_RE = re.compile(
    r"\b(skin|ward skin|tracker|prism|badge|announcer|voice pack|emote|recall|"
    r"loading frame|fountain|level[- ]up|global emote|cross[- ]gen)\b",
    re.I,
)


def classify_direction(text: str, section: str = "") -> str:
    t = text or ""
    sec = (section or "").lower()
    # Cosmetics / store lines are noise for balance tiers
    if COSMETIC_RE.search(t) and not (BUFF_RE.search(t) or NERF_RE.search(t)):
        return "neutral"
    if re.search(r"\bnew classic god\b|\bnew god\b", sec, re.I) or re.search(
        r"has been added to the game", t, re.I
    ):
        # Kit reveal bullets under a new-god section are not 20 separate buffs
        if re.search(r"\b(passive|ability|ultimate|aspect)\b", t, re.I) or len(t) > 40:
            return "new"
        return "new"
    if FIX_RE.search(t) and not (BUFF_RE.search(t) or NERF_RE.search(t)):
        return "fix"

    # Explicit buff/nerf words win
    has_buff = bool(BUFF_RE.search(t))
    has_nerf = bool(NERF_RE.search(t))

    # from-to with increased/decreased
    ft = extract_from_to(t)
    if ft:
        a, b = ft
        # if cooldown/cost: up = nerf, down = buff
        if re.search(r"cooldown|cost|mana", t, re.I):
            if b < a:
                return "buff"
            if b > a:
                return "nerf"
        else:
            # damage/scaling/etc: up = buff
            if b > a:
                return "buff"
            if b < a:
                return "nerf"

    if has_buff and not has_nerf:
        return "buff"
    if has_nerf and not has_buff:
        return "nerf"
    if has_buff and has_nerf:
        return "shift"
    if SHIFT_RE.search(t):
        return "shift"
    if "buff" in sec and "nerf" not in sec:
        return "buff"
    if "nerf" in sec and "buff" not in sec:
        return "nerf"
    return "neutral"


def change_magnitude(text: str, direction: str) -> float:
    """Estimate change strength 0.5–3.0."""
    if direction in ("new",):
        return 2.5
    if direction == "fix":
        return 0.3
    if direction == "neutral":
        return 0.2
    ft = extract_from_to(text)
    if ft:
        a, b = ft
        if a == 0:
            base = 1.5
        else:
            pct = abs(b - a) / abs(a)
            base = 0.75 + min(pct * 3.0, 2.0)
        return min(base, 3.0)
    # keyword intensity
    if re.search(r"\bsignificant|major|massive|huge\b", text, re.I):
        return 2.2
    if re.search(r"\bslight(?:ly)?|minor|small\b", text, re.I):
        return 0.7
    return 1.0


def direction_sign(direction: str) -> float:
    return {
        "buff": 1.0,
        "nerf": -1.0,
        "new": 0.85,  # new gods get attention, not auto-S
        "shift": 0.15,
        "fix": 0.05,
        "neutral": 0.0,
    }.get(direction, 0.0)


def recency_weights(patch_ids_newest_first: list[int], half_life: float = 6.0) -> dict[int, float]:
    """Exponential decay by rank (0 = newest). half_life patches → weight 0.5."""
    weights = {}
    for rank, pid in enumerate(patch_ids_newest_first):
        weights[pid] = 0.5 ** (rank / half_life)
    return weights


def parse_patch_wikitext_entities(
    wikitext: str,
    god_index: dict[str, str],
    item_index: dict[str, str],
) -> list[dict[str, Any]]:
    """
    Walk patch wikitext and emit attributed change lines.
    Gods/items often appear as: [[File:...]] '''[[Aladdin]]'''
    """
    events: list[dict[str, Any]] = []
    section = "General"
    entity_name: str | None = None
    entity_type: str | None = None

    # Pre-sorted names for longest-match scanning
    god_names = sorted(set(god_index.values()), key=len, reverse=True)
    item_names = sorted(set(item_index.values()), key=len, reverse=True)

    for raw_line in wikitext.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        hm = re.match(r"^(={1,6})\s*(.+?)\s*\1\s*$", line)
        if hm:
            level = len(hm.group(1))
            title = _clean_entity(hm.group(2))
            if level <= 2:
                section = title
                entity_name = None
                entity_type = None
            else:
                resolved = _resolve_name(title, god_index, item_index)
                if resolved:
                    entity_type, entity_name = resolved
            continue

        # Inline god/item header: '''[[Name]]''' or '''Name'''
        header = re.search(r"'{2,3}\s*\[\[([^\]|]+)(?:\|[^\]]*)?\]\]\s*'{2,3}", line)
        if not header:
            header = re.search(r"\[\[File:[^\]]+\]\].*?\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", line)
        if header:
            resolved = _resolve_name(header.group(1), god_index, item_index)
            if resolved:
                entity_type, entity_name = resolved
                continue

        # Bold-only name line
        bold = re.match(r"^'{2,3}([^']+)'{2,3}\s*$", line)
        if bold:
            resolved = _resolve_name(bold.group(1), god_index, item_index)
            if resolved:
                entity_type, entity_name = resolved
                continue

        # Bullet changes
        bm = re.match(r"^\*+\s*(.+)$", line)
        if not bm:
            continue
        text = _clean_entity(bm.group(1))
        if not text or len(text) < 3:
            continue

        # If no current entity, try to find a name inside the line
        et, en = entity_type, entity_name
        if not en:
            found = _find_name_in_text(text, god_names, item_names, god_index, item_index)
            if found:
                et, en = found
        # Section BUFFS/NERFS sometimes only lists god name as the bullet
        if not en:
            resolved = _resolve_name(text, god_index, item_index)
            if resolved:
                entity_type, entity_name = resolved
                continue

        if not en:
            continue

        direction = classify_direction(text, section)
        # Section-level buff/nerf override when text is short ability name only
        if direction == "neutral":
            if re.search(r"\bbuff", section, re.I):
                direction = "buff"
            elif re.search(r"\bnerf", section, re.I):
                direction = "nerf"

        mag = change_magnitude(text, direction)
        events.append(
            {
                "section": section,
                "entity_type": et,
                "entity_name": en,
                "direction": direction,
                "magnitude": mag,
                "change_text": text,
            }
        )
    return events


def _resolve_name(
    raw: str,
    god_index: dict[str, str],
    item_index: dict[str, str],
) -> tuple[str, str] | None:
    name = _clean_entity(raw)
    key = name.lower().strip()
    key2 = key.replace("'", "").replace("’", "")
    if key in god_index:
        return "god", god_index[key]
    if key2 in god_index:
        return "god", god_index[key2]
    if key in item_index:
        return "item", item_index[key]
    if key2 in item_index:
        return "item", item_index[key2]
    # strip trailing Buff/Nerf labels from structured logs
    for suffix in (" buff", " nerf", " shift"):
        if key.endswith(suffix):
            base = key[: -len(suffix)]
            if base in god_index:
                return "god", god_index[base]
            if base in item_index:
                return "item", item_index[base]
    return None


def _find_name_in_text(
    text: str,
    god_names: list[str],
    item_names: list[str],
    god_index: dict[str, str],
    item_index: dict[str, str],
) -> tuple[str, str] | None:
    tl = text.lower()
    for g in god_names:
        if g.lower() in tl:
            return "god", g
    for it in item_names:
        if len(it) < 4:
            continue
        if it.lower() in tl:
            return "item", it
    return None


def compute_patch_impacts(conn: sqlite3.Connection) -> dict[str, int]:
    god_index, item_index = build_name_index(conn)
    patches = conn.execute(
        """
        SELECT id, name, release_date, number_label, content_wikitext, content_json, phase
        FROM patch_notes
        ORDER BY id ASC
        """
    ).fetchall()
    # ids are newest-first from scrape order (OB39=1)
    patch_ids = [p["id"] for p in patches]
    weights = recency_weights(patch_ids, half_life=6.0)

    conn.execute("DELETE FROM patch_impacts")
    conn.execute("DELETE FROM entity_patch_summary")

    # Aggregate (patch, entity, direction) -> stats
    agg: dict[tuple, dict[str, Any]] = {}

    for p in patches:
        w = weights[p["id"]]
        events: list[dict[str, Any]] = []
        if p["content_wikitext"]:
            events.extend(
                parse_patch_wikitext_entities(p["content_wikitext"], god_index, item_index)
            )
        # Merge sparse structured JSON when present
        if p["content_json"]:
            import json

            try:
                blob = json.loads(p["content_json"])
            except json.JSONDecodeError:
                blob = None
            if isinstance(blob, dict):
                for key, val in blob.items():
                    resolved = _resolve_name(key, god_index, item_index)
                    text = val if isinstance(val, str) else str(val)
                    if not resolved:
                        # key might be "Zeus Nerf"
                        resolved = _resolve_name(key, god_index, item_index)
                    if not resolved:
                        found = _find_name_in_text(
                            key + " " + text,
                            sorted(set(god_index.values()), key=len, reverse=True),
                            sorted(set(item_index.values()), key=len, reverse=True),
                            god_index,
                            item_index,
                        )
                        resolved = found
                    if not resolved:
                        continue
                    et, en = resolved
                    direction = classify_direction(key + " " + text)
                    events.append(
                        {
                            "section": "StructuredLog",
                            "entity_type": et,
                            "entity_name": en,
                            "direction": direction,
                            "magnitude": change_magnitude(text, direction),
                            "change_text": text[:500],
                        }
                    )

        for ev in events:
            # Skip pure cosmetic/noise neutrals
            if ev["direction"] == "neutral" and COSMETIC_RE.search(ev["change_text"] or ""):
                continue
            key = (p["id"], ev["entity_type"], ev["entity_name"], ev["direction"])
            slot = agg.get(key)
            # Cap "new" kit dumps: one new-event credit per entity per patch
            if ev["direction"] == "new" and slot:
                slot["change_count"] += 1
                continue
            signed = direction_sign(ev["direction"]) * ev["magnitude"] * w
            if ev["direction"] == "new":
                # Single modest novelty bump, not sum of every kit bullet
                signed = direction_sign("new") * 1.2 * w
            if not slot:
                agg[key] = {
                    "patch_id": p["id"],
                    "entity_type": ev["entity_type"],
                    "entity_name": ev["entity_name"],
                    "direction": ev["direction"],
                    "magnitude": ev["magnitude"] if ev["direction"] != "new" else 1.2,
                    "weighted_score": signed,
                    "recency_weight": w,
                    "change_count": 1,
                    "sample_text": ev["change_text"][:400],
                    "patch_name": p["name"],
                    "release_date": p["release_date"],
                    "patch_rank": patch_ids.index(p["id"]),
                }
            else:
                slot["magnitude"] = max(slot["magnitude"], ev["magnitude"])
                # Soft-cap stacking of many tiny same-direction lines in one patch
                stack_factor = 1.0 / (1.0 + 0.15 * slot["change_count"])
                slot["weighted_score"] += signed * stack_factor
                slot["change_count"] += 1
                if len(ev["change_text"]) > 20 and ev["direction"] in ("buff", "nerf", "shift"):
                    slot["sample_text"] = ev["change_text"][:400]

    for slot in agg.values():
        conn.execute(
            """
            INSERT INTO patch_impacts (
                patch_id, entity_type, entity_name, direction, magnitude,
                weighted_score, recency_weight, change_count, sample_text
            ) VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(patch_id, entity_type, entity_name, direction) DO UPDATE SET
                magnitude=excluded.magnitude,
                weighted_score=excluded.weighted_score,
                change_count=excluded.change_count,
                sample_text=excluded.sample_text
            """,
            (
                slot["patch_id"],
                slot["entity_type"],
                slot["entity_name"],
                slot["direction"],
                slot["magnitude"],
                slot["weighted_score"],
                slot["recency_weight"],
                slot["change_count"],
                slot["sample_text"],
            ),
        )

    # Entity summaries
    by_entity: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for slot in agg.values():
        by_entity[(slot["entity_type"], slot["entity_name"])].append(slot)

    for (et, en), slots in by_entity.items():
        slots_sorted = sorted(slots, key=lambda s: s["patch_rank"])  # newest first ranks low
        buff_events = sum(s["change_count"] for s in slots if s["direction"] == "buff")
        nerf_events = sum(s["change_count"] for s in slots if s["direction"] == "nerf")
        shift_events = sum(s["change_count"] for s in slots if s["direction"] == "shift")
        new_events = sum(s["change_count"] for s in slots if s["direction"] == "new")
        net_weighted = sum(s["weighted_score"] for s in slots)
        net_raw = sum(direction_sign(s["direction"]) * s["magnitude"] * s["change_count"] for s in slots)

        recent_5 = sum(s["weighted_score"] for s in slots if s["patch_rank"] < 5)
        recent_10 = sum(s["weighted_score"] for s in slots if s["patch_rank"] < 10)

        last = slots_sorted[0]
        # trajectory
        r5 = recent_5
        if new_events and abs(net_weighted) < 1:
            trajectory = "new"
        elif abs(r5) < 0.35 and abs(net_weighted) < 1:
            trajectory = "stable"
        elif r5 >= 0.8:
            trajectory = "rising"
        elif r5 <= -0.8:
            trajectory = "falling"
        elif buff_events > 0 and nerf_events > 0:
            trajectory = "volatile"
        elif net_weighted > 0:
            trajectory = "rising"
        elif net_weighted < 0:
            trajectory = "falling"
        else:
            trajectory = "stable"

        patches_touched = len({s["patch_id"] for s in slots})
        conn.execute(
            """
            INSERT INTO entity_patch_summary (
                entity_type, entity_name, patches_touched, buff_events, nerf_events,
                shift_events, new_events, net_raw_score, net_weighted_score,
                recent_5_score, recent_10_score, last_direction, last_patch,
                last_patch_date, trajectory
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                et,
                en,
                patches_touched,
                buff_events,
                nerf_events,
                shift_events,
                new_events,
                net_raw,
                net_weighted,
                recent_5,
                recent_10,
                last["direction"],
                last["patch_name"],
                last["release_date"],
                trajectory,
            ),
        )

    conn.commit()
    return {
        "patch_impact_rows": len(agg),
        "entities_scored": len(by_entity),
    }
