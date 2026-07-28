"""Scrape SMITE 2 data from the official wiki into SQLite."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import DEFAULT_DB, connect, init_db, reset_content_tables, set_meta
from .parsers import (
    parse_abilities,
    parse_god_aspect,
    parse_god_infobox,
    parse_item_categories,
    parse_item_infobox,
    parse_item_notes,
    parse_item_recipe,
    parse_lore,
    parse_patch_infobox,
    parse_patch_list,
    split_patch_changes,
    unwrap_json_data,
    wikitext_to_plain,
)
from .wiki import WikiClient

# Wiki categories → default tier / type labels for the catalog
# (page infobox overrides these when present)
ITEM_CATEGORY_META: list[tuple[str, str, str]] = [
    # (category title, tier, item_type)
    ("Relics", "Relic", "Relic"),
    ("Curios", "Curio", "Curio"),
    ("Consumable items", "Consumable", "Consumable"),
    ("Starter items", "Starter", "Starter"),
    ("Tier 1 items", "1", ""),
    ("Tier 2 items", "2", ""),
    ("Tier 3 items", "3", ""),
    ("Offensive items", "3", "Offensive"),
    ("Defensive items", "3", "Defensive"),
    ("Hybrid items", "3", "Hybrid"),
    ("God Specific items", "God Specific", "God Specific"),
]


def _discover_gods_from_latest_patches(
    wiki: WikiClient,
    known_names: set[str],
    *,
    look_ahead_ob: int = 3,
    verbose: bool = True,
) -> list[str]:
    """
    Data:Gods.json often lags a day after a new classic god ships.
    Pull god page titles from recent Open Beta 'New Classic God' sections.
    """
    # Highest OB we know from index + look-ahead
    try:
        index_wt = wiki.get_wikitext("Patch notes")
        patches = parse_patch_list(index_wt)
    except Exception:
        patches = []
    max_n = 0
    for p in patches:
        m = re.search(r"Open Beta\s+(\d+)", p.get("name") or "", re.I)
        if m:
            max_n = max(max_n, int(m.group(1)))
    candidates = [f"SMITE 2 Open Beta {n}" for n in range(max(1, max_n - 1), max_n + 1 + look_ahead_ob)]
    found: list[str] = []
    skip_prefixes = (
        "file:",
        "category:",
        "smite 2 ",
        "template:",
        "ob",
    )
    for patch_name in candidates:
        try:
            wt = wiki.get_wikitext(patch_name)
        except Exception:
            continue
        if not wt or len(wt) < 200:
            continue
        # Prefer New Classic God section; fall back to full page links under === [[God]] ===
        sections = re.findall(
            r"==\s*New Classic Gods?\s*==(.+?)(?:\n==\s[^=]|\Z)",
            wt,
            flags=re.S | re.I,
        )
        blob = "\n".join(sections) if sections else wt
        for link in re.findall(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", blob):
            name = link.strip()
            if not name or name.lower().startswith(skip_prefixes):
                continue
            # Skip patch-nav style links
            if re.search(r"open beta|closed alpha|patch notes", name, re.I):
                continue
            if name in known_names or name in found:
                continue
            # Must look like a real god page (has God infobox)
            try:
                gwt = wiki.get_wikitext(name)
            except Exception:
                continue
            if not gwt or "God infobox" not in gwt:
                continue
            found.append(name)
            if verbose:
                print(f"  Discovered god not in Gods.json: {name} (from {patch_name})")
    return found


def _upsert_god_from_wiki(
    conn,
    wiki: WikiClient,
    name: str,
    g: dict[str, Any] | None = None,
    *,
    verbose: bool = True,
) -> bool:
    """Insert/update one god from wiki (+ optional Gods.json row)."""
    g = g or {}
    if verbose:
        print(f"  God: {name}")
    try:
        wikitext = wiki.get_wikitext(name)
    except Exception as exc:  # noqa: BLE001
        print(f"    WARN: could not load page for {name}: {exc}", file=sys.stderr)
        wikitext = ""

    infobox = parse_god_infobox(wikitext) if wikitext else {}
    base_wt = wikitext
    if wikitext:
        m = re.search(r"^={2,6}\s*God Aspect\s*={2,6}", wikitext, re.I | re.M)
        if m:
            base_wt = wikitext[: m.start()]
    abilities = parse_abilities(base_wt) if base_wt else []
    aspect = parse_god_aspect(wikitext) if wikitext else None
    lore = parse_lore(wikitext) if wikitext else ""

    roles = g.get("roleTags") or []
    wiki_roles = [infobox.get("role1"), infobox.get("role2")]
    wiki_roles = [r for r in wiki_roles if r]
    role_list = wiki_roles or roles

    release = None
    if infobox.get("day") and infobox.get("month") and infobox.get("year"):
        release = f"{infobox['year']}-{infobox['month'].zfill(2)}-{infobox['day'].zfill(2)}"

    # Damage type: JSON or infobox "attack damage" / "attack type"
    dtype = (
        g.get("primaryDamageType")
        or infobox.get("attack damage")
        or infobox.get("attackdamage")
        or ""
    )
    if dtype and dtype.lower() in ("physical", "magical"):
        dtype = dtype.title()

    slug = g.get("slug") or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    conn.execute(
        """
        INSERT INTO gods (
            name, slug, title, pantheon, primary_damage_type, roles, character_tags,
            type_label, release_date, diamonds, voice_actor, wiki_url, icon_path, card_path,
            lore, game_id, master_id, patch_version, base_stats_json, raw_infobox_json
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(name) DO UPDATE SET
            slug=excluded.slug,
            title=excluded.title,
            pantheon=excluded.pantheon,
            primary_damage_type=excluded.primary_damage_type,
            roles=excluded.roles,
            character_tags=excluded.character_tags,
            type_label=excluded.type_label,
            release_date=excluded.release_date,
            diamonds=excluded.diamonds,
            voice_actor=excluded.voice_actor,
            wiki_url=excluded.wiki_url,
            icon_path=excluded.icon_path,
            card_path=excluded.card_path,
            lore=excluded.lore,
            game_id=excluded.game_id,
            master_id=excluded.master_id,
            patch_version=excluded.patch_version,
            base_stats_json=excluded.base_stats_json,
            raw_infobox_json=excluded.raw_infobox_json,
            scraped_at=datetime('now')
        """,
        (
            name,
            slug,
            g.get("title") or infobox.get("title"),
            g.get("pantheon") or infobox.get("pantheon"),
            dtype,
            json.dumps(role_list),
            json.dumps(g.get("characterTags") or []),
            g.get("type") or infobox.get("spec1"),
            release,
            _safe_int(infobox.get("diamonds")),
            infobox.get("voice actor"),
            wiki.page_url(name),
            g.get("smallIconPath"),
            g.get("godCardPath"),
            lore,
            str(g.get("id") or ""),
            g.get("masterId"),
            g.get("patchVersion"),
            json.dumps(g.get("baseStats") or {}),
            json.dumps(infobox),
        ),
    )
    god_id = conn.execute("SELECT id FROM gods WHERE name = ?", (name,)).fetchone()["id"]
    conn.execute("DELETE FROM abilities WHERE god_id = ?", (god_id,))

    for ab in abilities:
        conn.execute(
            """
            INSERT OR IGNORE INTO abilities (
                god_id, slot, slot_order, name, short_label, icon,
                description, stats_text, notes_text, stats_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                god_id,
                ab["slot"],
                ab["slot_order"],
                ab["name"],
                ab["short_label"],
                ab["icon"],
                ab["description"],
                ab["stats_text"],
                ab["notes_text"],
                json.dumps(ab["stats_json"]),
            ),
        )

    try:
        old_aspects = conn.execute(
            "SELECT id FROM god_aspects WHERE god_id = ?", (god_id,)
        ).fetchall()
        for oa in old_aspects:
            conn.execute(
                "DELETE FROM god_aspect_abilities WHERE aspect_id = ?", (oa["id"],)
            )
        conn.execute("DELETE FROM god_aspects WHERE god_id = ?", (god_id,))
    except sqlite3.OperationalError:
        pass
    if aspect and (aspect.get("name") or aspect.get("description")):
        conn.execute(
            """
            INSERT INTO god_aspects (god_id, name, description, image, raw_json)
            VALUES (?,?,?,?,?)
            """,
            (
                god_id,
                aspect.get("name") or "God Aspect",
                aspect.get("description") or "",
                aspect.get("image") or "",
                json.dumps(aspect),
            ),
        )
        aspect_id = conn.execute(
            "SELECT id FROM god_aspects WHERE god_id = ? ORDER BY id DESC LIMIT 1",
            (god_id,),
        ).fetchone()["id"]
        for ab in aspect.get("abilities") or []:
            conn.execute(
                """
                INSERT INTO god_aspect_abilities (
                    aspect_id, slot, slot_order, name, short_label, icon,
                    description, stats_text, notes_text, stats_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    aspect_id,
                    ab.get("slot") or "",
                    ab.get("slot_order") or 0,
                    ab.get("name") or "",
                    ab.get("short_label") or "",
                    ab.get("icon") or "",
                    ab.get("description") or "",
                    ab.get("stats_text") or "",
                    ab.get("notes_text") or "",
                    json.dumps(ab.get("stats_json") or {}),
                ),
            )
        if verbose:
            print(f"    Aspect: {aspect.get('name')}")

    conn.commit()
    return True


def scrape_gods(conn, wiki: WikiClient, verbose: bool = True) -> int:
    if verbose:
        print("Fetching Data:Gods.json …")
    raw = wiki.get_page_json("Data:Gods.json")
    gods_data = unwrap_json_data(raw)
    if not isinstance(gods_data, list):
        raise RuntimeError("Unexpected Gods.json shape")

    # Dedupe JSON rows (Bastet has appeared twice)
    by_name: dict[str, dict] = {}
    for g in gods_data:
        name = g.get("name")
        if name:
            by_name[name] = g

    count = 0
    for name, g in by_name.items():
        if _upsert_god_from_wiki(conn, wiki, name, g, verbose=verbose):
            count += 1

    # Gods.json lag: pull new classics from latest patch pages (e.g. Cu Chulainn on OB40 day-1)
    extras = _discover_gods_from_latest_patches(
        wiki, set(by_name.keys()), verbose=verbose
    )
    for name in extras:
        if _upsert_god_from_wiki(conn, wiki, name, None, verbose=verbose):
            count += 1
    return count


def collect_item_catalog(wiki: WikiClient, verbose: bool = True) -> dict[str, dict[str, str]]:
    """Build item page title → {tier, item_type} from wiki categories."""
    catalog: dict[str, dict[str, str]] = {}
    for cat, tier, item_type in ITEM_CATEGORY_META:
        try:
            titles = wiki.category_members(cat)
        except Exception as exc:  # noqa: BLE001
            print(f"  WARN category {cat}: {exc}", file=sys.stderr)
            continue
        if verbose:
            print(f"  Category {cat}: {len(titles)} pages")
        for title in titles:
            if title.startswith("Category:") or title in ("Items",):
                continue
            existing = catalog.get(title, {})
            # Prefer more specific type labels when we see them
            merged_type = item_type or existing.get("item_type", "")
            # Starter override: if also in Starter items, keep Starter tier unless tier 2 upgrade
            merged_tier = existing.get("tier") or tier
            if cat == "Starter items":
                # Distinguish upgraded starters: they are also Tier 2
                if existing.get("tier") == "2":
                    merged_tier = "Upgraded Starter"
                else:
                    merged_tier = "Starter"
            elif cat == "Tier 2 items" and existing.get("tier") == "Starter":
                merged_tier = "Upgraded Starter"
            elif not existing.get("tier"):
                merged_tier = tier
            elif item_type in ("Offensive", "Defensive", "Hybrid"):
                merged_tier = existing.get("tier") or "3"
            catalog[title] = {
                "tier": merged_tier,
                "item_type": merged_type or existing.get("item_type", ""),
            }
    return catalog


def scrape_items(conn, wiki: WikiClient, verbose: bool = True) -> int:
    if verbose:
        print("Collecting items from wiki categories …")
    catalog = collect_item_catalog(wiki, verbose=verbose)
    if verbose:
        print(f"  Unique item pages: {len(catalog)}")

    count = 0
    for name, meta in sorted(catalog.items()):
        if verbose:
            print(f"  Item: {name}")
        try:
            wikitext = wiki.get_wikitext(name)
        except Exception as exc:  # noqa: BLE001
            print(f"    WARN: skip {name}: {exc}", file=sys.stderr)
            continue

        if not re.search(r"\{\{\s*Item infobox", wikitext, re.I):
            if verbose:
                print(f"    skip (not an item page): {name}")
            continue

        info = parse_item_infobox(wikitext)
        recipe = parse_item_recipe(wikitext)
        cats = parse_item_categories(wikitext)
        notes = parse_item_notes(wikitext)

        tier = str(info.get("tier") or meta.get("tier") or "")
        # Normalize numeric / word tiers
        tier_l = tier.lower().strip()
        if tier_l in ("1", "tier 1", "i", "tier i"):
            tier = "1"
        elif tier_l in ("2", "tier 2", "ii", "tier ii"):
            tier = "2"
        elif tier_l in ("3", "tier 3", "iii", "tier iii"):
            tier = "3"
        elif meta.get("tier") in ("Starter", "Upgraded Starter", "Relic", "Curio", "Consumable", "God Specific"):
            # Prefer catalog classification for special slots when infobox only has a number
            if tier in ("1", "2", "3") and meta["tier"] in ("Starter", "Upgraded Starter", "Relic", "Curio", "Consumable", "God Specific"):
                tier = meta["tier"]

        # Category-based type for specials
        item_type = info.get("item_type") or meta.get("item_type") or ""
        if not item_type:
            for c in cats:
                cl = c.lower()
                if "offensive" in cl:
                    item_type = "Offensive"
                elif "defensive" in cl:
                    item_type = "Defensive"
                elif "hybrid" in cl:
                    item_type = "Hybrid"
                elif "relic" in cl:
                    item_type = "Relic"
                elif "curio" in cl:
                    item_type = "Curio"
                elif "consumable" in cl:
                    item_type = "Consumable"
                elif "starter" in cl:
                    item_type = "Starter"

        total_cost = info.get("total_cost")
        cost = info.get("cost")
        display_name = info.get("name") or name

        # God-specific hint
        god_specific = None
        for c in cats:
            if "god specific" in c.lower():
                god_specific = "god-specific"
                break

        try:
            conn.execute(
                """
                INSERT INTO items (
                    name, tier, item_type, cost, total_cost, stats_text, stats_json,
                    passive, active, recipe_json, categories, god_specific, wiki_url,
                    image, notes, raw_infobox_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(name) DO UPDATE SET
                    tier=excluded.tier,
                    item_type=excluded.item_type,
                    cost=excluded.cost,
                    total_cost=excluded.total_cost,
                    stats_text=excluded.stats_text,
                    stats_json=excluded.stats_json,
                    passive=excluded.passive,
                    active=excluded.active,
                    recipe_json=excluded.recipe_json,
                    categories=excluded.categories,
                    god_specific=excluded.god_specific,
                    wiki_url=excluded.wiki_url,
                    image=excluded.image,
                    notes=excluded.notes,
                    raw_infobox_json=excluded.raw_infobox_json,
                    scraped_at=datetime('now')
                """,
                (
                    display_name,
                    tier,
                    item_type,
                    cost,
                    total_cost,
                    info.get("stats_text"),
                    json.dumps(info.get("stats_json") or []),
                    info.get("passive"),
                    info.get("active"),
                    json.dumps(recipe) if recipe else None,
                    json.dumps(cats),
                    god_specific,
                    wiki.page_url(name),
                    info.get("image"),
                    notes,
                    json.dumps(info.get("raw") or {}),
                ),
            )
            count += 1
            conn.commit()
        except Exception as exc:  # noqa: BLE001
            print(f"    ERROR inserting {name}: {exc}", file=sys.stderr)
    return count


def _discover_newer_open_beta_patches(
    wiki: WikiClient,
    patches: list[dict[str, str]],
    *,
    look_ahead: int = 3,
    verbose: bool = True,
) -> list[dict[str, str]]:
    """
    Wiki Patch_notes index sometimes lags a day after launch.
    If Open Beta N is listed, try Open Beta N+1…N+look_ahead and prepend any live pages.
    """
    max_n = 0
    for p in patches:
        m = re.search(r"Open Beta\s+(\d+)", p.get("name") or "", re.I)
        if m:
            max_n = max(max_n, int(m.group(1)))
    if max_n <= 0:
        return patches
    known = {p["name"] for p in patches}
    extra: list[dict[str, str]] = []
    for n in range(max_n + 1, max_n + 1 + look_ahead):
        name = f"SMITE 2 Open Beta {n}"
        if name in known:
            continue
        try:
            wt = wiki.get_wikitext(name)
        except Exception:
            continue
        if not wt or len(wt) < 200:
            continue
        # Prefer infobox release date when present
        info = parse_patch_infobox(wt)
        release = info.get("release date") or info.get("releasedate") or ""
        if not release:
            # common first heading / table cell
            dm = re.search(
                r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}",
                wt,
            )
            release = dm.group(0) if dm else ""
        extra.append(
            {
                "name": name,
                "release_date": release,
                "phase": "Open Beta",
            }
        )
        if verbose:
            print(f"  Discovered unlisted patch page: {name} ({release or 'date TBD'})")
    if not extra:
        return patches
    # Newest first to match index order
    return extra[::-1] + patches


def scrape_patches(conn, wiki: WikiClient, verbose: bool = True) -> int:
    if verbose:
        print("Fetching patch notes index …")
    index_wt = wiki.get_wikitext("Patch notes")
    patches = parse_patch_list(index_wt)
    patches = _discover_newer_open_beta_patches(wiki, patches, verbose=verbose)
    if verbose:
        print(f"  Found {len(patches)} patches")

    # Optional structured patch log data
    structured: dict[str, Any] = {}
    try:
        structured = unwrap_json_data(wiki.get_page_json("Data:PatchLogs.json"))
        if not isinstance(structured, dict):
            structured = {}
    except Exception as exc:  # noqa: BLE001
        print(f"  WARN: PatchLogs.json unavailable: {exc}", file=sys.stderr)

    count = 0
    for p in patches:
        name = p["name"]
        if verbose:
            print(f"  Patch: {name}")
        try:
            wikitext = wiki.get_wikitext(name)
        except Exception as exc:  # noqa: BLE001
            print(f"    WARN: skip {name}: {exc}", file=sys.stderr)
            continue

        info = parse_patch_infobox(wikitext)
        changes = split_patch_changes(wikitext)
        plain = wikitext_to_plain(wikitext)

        # Match structured log entries
        content_json = None
        if name in structured:
            content_json = structured[name]
        else:
            # try without "SMITE 2 " prefix variants
            for key in structured:
                if key.lower() == name.lower():
                    content_json = structured[key]
                    break

        # Title from first = heading =
        title_m = re.search(r"^=\s*(.+?)\s*=\s*$", wikitext, re.M)
        title = clean_title(title_m.group(1)) if title_m else info.get("name", name)

        number_label = info.get("currentnum") or info.get("current num") or ""
        phase = p.get("phase") or ""
        if not phase:
            if "Open Beta" in name:
                phase = "Open Beta"
            elif "Closed Alpha" in name:
                phase = "Closed Alpha"
            elif "Alpha Weekend" in name:
                phase = "Alpha Weekend"

        cur = conn.execute(
            """
            INSERT INTO patch_notes (
                name, phase, number_label, release_date, title, wiki_url,
                previous_patch, next_patch, content_wikitext, content_text, content_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(name) DO UPDATE SET
                phase=excluded.phase,
                number_label=excluded.number_label,
                release_date=excluded.release_date,
                title=excluded.title,
                wiki_url=excluded.wiki_url,
                previous_patch=excluded.previous_patch,
                next_patch=excluded.next_patch,
                content_wikitext=excluded.content_wikitext,
                content_text=excluded.content_text,
                content_json=excluded.content_json,
                scraped_at=datetime('now')
            """,
            (
                name,
                phase,
                number_label,
                p.get("release_date") or info.get("release date"),
                title,
                wiki.page_url(name),
                info.get("previousupdate") or info.get("previous update"),
                info.get("nextupdate") or info.get("next update"),
                wikitext,
                plain,
                json.dumps(content_json) if content_json else None,
            ),
        )
        # Get id (works for insert; for conflict need select)
        row = conn.execute("SELECT id FROM patch_notes WHERE name = ?", (name,)).fetchone()
        patch_id = row["id"]

        conn.execute("DELETE FROM patch_changes WHERE patch_id = ?", (patch_id,))
        for ch in changes:
            conn.execute(
                """
                INSERT INTO patch_changes (
                    patch_id, section, entity_name, entity_type, change_text, change_order
                ) VALUES (?,?,?,?,?,?)
                """,
                (
                    patch_id,
                    ch["section"],
                    ch["entity_name"],
                    ch["entity_type"],
                    ch["change_text"],
                    ch["change_order"],
                ),
            )
        count += 1
        conn.commit()
    return count


def clean_title(s: str) -> str:
    s = re.sub(r"\[\[File:[^\]]+\]\]", "", s)
    s = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    return s.strip()


def scrape_aspects_only(conn, wiki: WikiClient, verbose: bool = True) -> int:
    """Re-fetch God Aspect sections for gods already in the DB (faster than full god scrape)."""
    init_db(conn)
    gods = conn.execute("SELECT id, name FROM gods ORDER BY name").fetchall()
    count = 0
    for g in gods:
        name = g["name"]
        god_id = g["id"]
        if verbose:
            print(f"  Aspect: {name}")
        try:
            wikitext = wiki.get_wikitext(name)
        except Exception as exc:  # noqa: BLE001
            print(f"    WARN: {name}: {exc}", file=sys.stderr)
            continue
        aspect = parse_god_aspect(wikitext) if wikitext else None
        try:
            old = conn.execute(
                "SELECT id FROM god_aspects WHERE god_id = ?", (god_id,)
            ).fetchall()
            for oa in old:
                conn.execute(
                    "DELETE FROM god_aspect_abilities WHERE aspect_id = ?", (oa["id"],)
                )
            conn.execute("DELETE FROM god_aspects WHERE god_id = ?", (god_id,))
        except sqlite3.OperationalError:
            init_db(conn)
        if not aspect or not (aspect.get("name") or aspect.get("description")):
            conn.commit()
            continue
        conn.execute(
            """
            INSERT INTO god_aspects (god_id, name, description, image, raw_json)
            VALUES (?,?,?,?,?)
            """,
            (
                god_id,
                aspect.get("name") or "God Aspect",
                aspect.get("description") or "",
                aspect.get("image") or "",
                json.dumps(aspect),
            ),
        )
        aspect_id = conn.execute(
            "SELECT id FROM god_aspects WHERE god_id = ? ORDER BY id DESC LIMIT 1",
            (god_id,),
        ).fetchone()["id"]
        for ab in aspect.get("abilities") or []:
            conn.execute(
                """
                INSERT INTO god_aspect_abilities (
                    aspect_id, slot, slot_order, name, short_label, icon,
                    description, stats_text, notes_text, stats_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    aspect_id,
                    ab.get("slot") or "",
                    ab.get("slot_order") or 0,
                    ab.get("name") or "",
                    ab.get("short_label") or "",
                    ab.get("icon") or "",
                    ab.get("description") or "",
                    ab.get("stats_text") or "",
                    ab.get("notes_text") or "",
                    json.dumps(ab.get("stats_json") or {}),
                ),
            )
        if verbose:
            print(f"    → {aspect.get('name')} ({len(aspect.get('abilities') or [])} abilities)")
        count += 1
        conn.commit()
    return count


def _safe_int(v) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(str(v).strip().replace(",", ""))
    except ValueError:
        return None


def run_scrape(
    db_path: Path | str | None = None,
    targets: set[str] | None = None,
    reset: bool = True,
    delay: float = 0.35,
    verbose: bool = True,
) -> dict[str, int]:
    targets = targets or {"gods", "items", "patches"}
    conn = connect(db_path)
    init_db(conn)
    if reset:
        reset_content_tables(conn)

    wiki = WikiClient(delay=delay)
    results: dict[str, int] = {}

    set_meta(conn, "game", "SMITE 2")
    set_meta(conn, "source", "https://wiki.smite2.com")
    set_meta(conn, "scraped_at", datetime.now(timezone.utc).isoformat())
    conn.commit()

    if "gods" in targets:
        results["gods"] = scrape_gods(conn, wiki, verbose=verbose)
        results["abilities"] = conn.execute("SELECT COUNT(*) AS c FROM abilities").fetchone()["c"]
        try:
            results["aspects"] = conn.execute("SELECT COUNT(*) AS c FROM god_aspects").fetchone()["c"]
        except sqlite3.OperationalError:
            results["aspects"] = 0
    if "aspects" in targets and "gods" not in targets:
        # Aspects-only refresh (keeps existing gods/abilities)
        results["aspects"] = scrape_aspects_only(conn, wiki, verbose=verbose)
    if "items" in targets:
        results["items"] = scrape_items(conn, wiki, verbose=verbose)
    if "patches" in targets:
        results["patches"] = scrape_patches(conn, wiki, verbose=verbose)
        results["patch_changes"] = conn.execute("SELECT COUNT(*) AS c FROM patch_changes").fetchone()["c"]

    set_meta(conn, "last_results", json.dumps(results))
    conn.commit()
    conn.close()
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scrape SMITE 2 gods, abilities, items, and patch notes into SQLite."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"SQLite path (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--only",
        choices=["gods", "items", "patches", "aspects"],
        action="append",
        help="Scrape only these targets (repeatable). Default: all.",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Do not wipe existing tables before scrape.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.35,
        help="Seconds between wiki requests (default 0.35).",
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args(argv)

    targets = set(args.only) if args.only else {"gods", "items", "patches"}
    # aspects-only must never wipe the DB
    reset = not args.no_reset
    if targets == {"aspects"}:
        reset = False
    print(f"SMITE 2 scrape → {args.db}")
    print(f"Targets: {', '.join(sorted(targets))}")
    results = run_scrape(
        db_path=args.db,
        targets=targets,
        reset=reset,
        delay=args.delay,
        verbose=not args.quiet,
    )
    print("Done:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
