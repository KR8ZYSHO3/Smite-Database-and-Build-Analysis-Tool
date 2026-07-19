"""Parsers for SMITE 2 wiki content (gods, abilities, items, patches)."""

from __future__ import annotations

import json
import re
from typing import Any

from .parse_util import (
    bullets_to_text,
    clean_text,
    extract_section,
    extract_templates,
    parse_stat_lines,
    parse_stat_templates,
    parse_template_fields,
    strip_html,
)

SLOT_ORDER = {
    "basic attack": 0,
    "passive": 1,
    "1st ability": 2,
    "2nd ability": 3,
    "3rd ability": 4,
    "ultimate": 5,
}


def parse_god_infobox(wikitext: str) -> dict[str, str]:
    blocks = extract_templates(wikitext, "God infoboxS2")
    if not blocks:
        blocks = extract_templates(wikitext, "God infobox")
    if not blocks:
        return {}
    # Drop outer {{Name and closing }}
    body = blocks[0]
    body = re.sub(r"^\{\{\s*God infoboxS?2?\s*", "", body, flags=re.I)
    body = re.sub(r"\}\}\s*$", "", body)
    return parse_template_fields(body)


def parse_abilities(wikitext: str) -> list[dict[str, Any]]:
    abilities: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for block in extract_templates(wikitext, "Ability"):
        body = re.sub(r"^\{\{\s*Ability\s*", "", block, flags=re.I)
        body = re.sub(r"\}\}\s*$", "", body)
        fields = parse_template_fields(body)
        slot = fields.get("slot", "").strip()
        name = clean_text(fields.get("name", ""))
        # Stance / aspect pages sometimes repeat the same Ability block
        key = (slot.lower(), name.lower())
        if key in seen:
            continue
        seen.add(key)
        stats_raw = fields.get("stats", "")
        notes_raw = fields.get("notes", "")
        # Keep natural order for stance variants that share a slot name
        # (e.g. Ullr bow vs axes) by appending occurrence index for order only
        base_order = SLOT_ORDER.get(slot.lower(), 99)
        same_slot = sum(1 for a in abilities if a["slot"].lower() == slot.lower())
        abilities.append(
            {
                "slot": slot,
                "slot_order": base_order * 10 + same_slot,
                "name": name,
                "short_label": clean_text(fields.get("short", "")),
                "icon": fields.get("icon", "").strip(),
                "description": clean_text(fields.get("description", "")),
                "stats_text": bullets_to_text(stats_raw.replace("{{!}}", "|")),
                "notes_text": bullets_to_text(notes_raw),
                "stats_json": parse_stat_lines(stats_raw),
            }
        )
    return abilities


def parse_lore(wikitext: str) -> str:
    section = extract_section(wikitext, "Lore")
    if not section:
        return ""
    # Lore is usually italicized paragraph
    text = clean_text(section)
    text = re.sub(r"^'+|" + r"'+$", "", text)
    return text.strip(" '\"")


def parse_item_infobox(wikitext: str) -> dict[str, Any]:
    blocks = extract_templates(wikitext, "Item infobox")
    if not blocks:
        return {}
    body = re.sub(r"^\{\{\s*Item infobox\s*", "", blocks[0], flags=re.I)
    body = re.sub(r"\}\}\s*$", "", body)
    fields = parse_template_fields(body)

    stats: list[dict[str, str]] = []
    for key, val in fields.items():
        if key.startswith("stat"):
            stats.extend(parse_stat_templates(val))

    passive = fields.get("passive", "") or ""
    active = fields.get("active", "") or ""
    # Some items put effect text only in active/passive; clean HTML
    result = {
        "name": fields.get("name", "").strip(),
        "image": fields.get("image", "").strip(),
        "tier": fields.get("tier", "").strip(),
        "item_type": fields.get("type", "").strip(),
        "cost": _to_int(fields.get("cost")),
        "total_cost": _to_int(fields.get("totalcost") or fields.get("total cost")),
        "stats_json": stats,
        "stats_text": _format_item_stats(stats),
        "passive": clean_text(passive),
        "active": clean_text(active),
        "raw": fields,
    }
    return result


def parse_item_recipe(wikitext: str) -> list[str] | None:
    blocks = extract_templates(wikitext, "Recipe")
    if not blocks:
        return None
    # Collect all item= names in recipe tree
    items = re.findall(r"\|\s*item\s*=\s*([^\n|}]+)", blocks[0])
    return [clean_text(i) for i in items if i.strip()]


def parse_item_categories(wikitext: str) -> list[str]:
    return re.findall(r"\[\[Category:([^\]]+)\]\]", wikitext)


def parse_item_notes(wikitext: str) -> str:
    section = extract_section(wikitext, "Notes")
    return clean_text(section)


def parse_patch_infobox(wikitext: str) -> dict[str, str]:
    for name in ("Patch infobox2", "Patch infobox"):
        blocks = extract_templates(wikitext, name)
        if blocks:
            body = re.sub(rf"^\{{{{\s*{re.escape(name)}\s*", "", blocks[0], flags=re.I)
            body = re.sub(r"\}\}\s*$", "", body)
            return parse_template_fields(body)
    return {}


def parse_patch_list(wikitext: str) -> list[dict[str, str]]:
    """Parse the Patch_notes index page into patch entries.

    Handles both single-line rows:
      |[[SMITE 2 Closed Alpha 8]]||December 10, 2024
    and multi-line rows:
      |[[SMITE 2 Open Beta 39]]
      |July 14th, 2026
    """
    patches: list[dict[str, str]] = []
    current_phase = ""
    pending_name: str | None = None

    for line in wikitext.splitlines():
        hm = re.match(r"^==\s*(.+?)\s*==\s*$", line)
        if hm:
            heading = hm.group(1).lower()
            if "open beta" in heading:
                current_phase = "Open Beta"
            elif "closed alpha" in heading:
                current_phase = "Closed Alpha"
            elif "alpha weekend" in heading:
                current_phase = "Alpha Weekend"
            pending_name = None
            continue

        # Single-line: |[[Name]]||Date
        m = re.search(
            r"\[\[(SMITE 2 [^|\]]+)(?:\|[^\]]*)?\]\]\s*\|\|\s*(.+?)\s*$",
            line,
        )
        if m:
            patches.append(
                {
                    "name": m.group(1).strip(),
                    "release_date": clean_text(m.group(2)),
                    "phase": current_phase,
                }
            )
            pending_name = None
            continue

        # Multi-line name cell: |[[Name]]
        m = re.match(r"^\|\s*\[\[(SMITE 2 [^|\]]+)(?:\|[^\]]*)?\]\]\s*$", line)
        if m:
            pending_name = m.group(1).strip()
            continue

        # Multi-line date cell after a name
        if pending_name:
            m = re.match(r"^\|\s*(.+?)\s*$", line)
            if m and not m.group(1).startswith("[["):
                patches.append(
                    {
                        "name": pending_name,
                        "release_date": clean_text(m.group(1)),
                        "phase": current_phase,
                    }
                )
                pending_name = None

    return patches


def split_patch_changes(wikitext: str) -> list[dict[str, Any]]:
    """
    Heuristically split patch wikitext into change rows.
    Looks for god/item headings and bullet lines.
    """
    changes: list[dict[str, Any]] = []
    section = "General"
    entity_name = None
    entity_type = "other"
    order = 0

    # Remove infobox
    text = re.sub(r"\{\{Patch infobox2?.*?\}\}", "", wikitext, count=1, flags=re.S | re.I)

    for line in text.splitlines():
        heading = re.match(r"^(={1,6})\s*(.+?)\s*\1\s*$", line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2)
            title = re.sub(r"\[\[File:[^\]]+\]\]", "", title, flags=re.I)
            title = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", title)
            title = re.sub(r"\[\[([^\]]+)\]\]", r"\1", title)
            # leftover image size tokens like "30px Name"
            title = re.sub(r"^\d+px\s*", "", title.strip())
            title = clean_text(title)
            if level <= 2:
                section = title
                entity_name = None
                entity_type = "other"
                if re.search(r"god", section, re.I):
                    entity_type = "god"
                elif re.search(r"item", section, re.I):
                    entity_type = "item"
            else:
                # Likely a god or item name
                entity_name = title
                if re.search(r"god|balance", section, re.I):
                    entity_type = "god"
                elif re.search(r"item", section, re.I):
                    entity_type = "item"
                else:
                    entity_type = "other"
            continue

        bullet = re.match(r"^\*+\s*(.+)$", line)
        if bullet:
            change_text = clean_text(bullet.group(1))
            if not change_text:
                continue
            changes.append(
                {
                    "section": section,
                    "entity_name": entity_name,
                    "entity_type": entity_type,
                    "change_text": change_text,
                    "change_order": order,
                }
            )
            order += 1

    return changes


def wikitext_to_plain(wikitext: str) -> str:
    text = re.sub(r"\{\{[^}]+\}\}", "", wikitext)
    text = re.sub(r"\[\[File:[^\]]+\]\]", "", text, flags=re.I)
    text = clean_text(text)
    return text


def _to_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    value = str(value).strip().replace(",", "")
    try:
        return int(float(value))
    except ValueError:
        return None


def _format_item_stats(stats: list[dict[str, str]]) -> str:
    return "\n".join(f"{s['stat']}: {s['value']}" for s in stats)


def unwrap_json_data(obj: Any) -> Any:
    if isinstance(obj, dict) and "json" in obj and len(obj) <= 2:
        return obj["json"]
    return obj
