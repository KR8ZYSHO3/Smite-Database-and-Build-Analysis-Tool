"""Shared wikitext parsing helpers."""

from __future__ import annotations

import re
from html import unescape


def strip_html(text: str | None) -> str:
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("{{!}}", "|")
    text = re.sub(r"\s+\n", "\n", text)
    return text.strip()


def strip_wikilinks(text: str) -> str:
    """[[Foo|Bar]] -> Bar, [[Foo]] -> Foo."""
    text = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"'''+|''+", "", text)
    return text


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    text = strip_html(text)
    text = strip_wikilinks(text)
    text = re.sub(r"\{\{[^}]+\}\}", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_template_fields(block: str) -> dict[str, str]:
    """
    Parse top-level |key=value fields from a template body (without outer braces).
    Handles multi-line values; does not fully recurse nested templates.
    """
    fields: dict[str, str] = {}
    # Split on |key= at the start of a line or after newline, careful with nested {{}}
    # Simpler approach: find |name= patterns at depth 0 relative to the block.
    current_key: str | None = None
    current_val: list[str] = []
    depth = 0
    i = 0
    # Normalize: ensure leading newline for consistent matching
    block = "\n" + block.strip()

    # Walk character by character tracking template depth and field starts
    # Field start: | at depth 0 followed by key=
    lines = block.split("\n")
    field_re = re.compile(r"^\|([^=\n|]+)=(.*)$")

    for line in lines:
        # Track depth changes from this line
        opens = line.count("{{")
        closes = line.count("}}")

        m = field_re.match(line) if depth == 0 else None
        if m:
            if current_key is not None:
                fields[current_key.strip()] = "\n".join(current_val).strip()
            current_key = m.group(1).strip()
            current_val = [m.group(2)]
            # depth for nested templates on the value part
            depth += opens - closes
            if depth < 0:
                depth = 0
            continue

        if current_key is not None:
            current_val.append(line)
            depth += opens - closes
            if depth < 0:
                depth = 0

    if current_key is not None:
        fields[current_key.strip()] = "\n".join(current_val).strip()
    return fields


def extract_templates(wikitext: str, name: str) -> list[str]:
    """Extract full {{Name ...}} blocks including nested templates."""
    results: list[str] = []
    # Case-insensitive name match
    pattern = re.compile(r"\{\{\s*" + re.escape(name) + r"\b", re.I)
    for m in pattern.finditer(wikitext):
        start = m.start()
        depth = 0
        i = start
        while i < len(wikitext) - 1:
            if wikitext[i : i + 2] == "{{":
                depth += 1
                i += 2
                continue
            if wikitext[i : i + 2] == "}}":
                depth -= 1
                i += 2
                if depth == 0:
                    results.append(wikitext[start:i])
                    break
                continue
            i += 1
    return results


def extract_section(wikitext: str, heading: str) -> str:
    """Return text under ==Heading== until next same-or-higher heading."""
    start_re = re.compile(
        rf"^(={{2,6}})\s*{re.escape(heading)}\s*\1\s*$",
        re.I | re.M,
    )
    m = start_re.search(wikitext)
    if not m:
        return ""
    level = len(m.group(1))
    rest = wikitext[m.end() :]
    end_re = re.compile(rf"^(={{{1},{level}}})[^=\n].*?\1\s*$", re.M)
    em = end_re.search(rest)
    if em:
        return rest[: em.start()].strip()
    return rest.strip()


def bullets_to_text(stats: str) -> str:
    lines = []
    for line in stats.splitlines():
        line = line.strip()
        if line.startswith("*"):
            line = line[1:].strip()
        line = clean_text(line)
        if line:
            lines.append(line)
    return "\n".join(lines)


def parse_stat_lines(stats: str) -> dict[str, str]:
    """Parse '* Key: Value' lines into a dict."""
    out: dict[str, str] = {}
    for line in bullets_to_text(stats).splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            out[key.strip()] = val.strip().replace("{{!}}", "|")
        else:
            out[line] = ""
    return out


def parse_stat_templates(value: str) -> list[dict[str, str]]:
    """Parse {{Str|45}} style item stat templates into [{name, value}]."""
    results = []
    for m in re.finditer(r"\{\{\s*([A-Za-z][A-Za-z0-9_ ']+)\|([^}]+)\}\}", value):
        results.append({"stat": m.group(1).strip(), "value": m.group(2).strip()})
    return results
