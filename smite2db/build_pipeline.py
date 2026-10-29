"""
Conquest build pipeline — formal multi-phase algorithm.

Full design: docs/BUILD_ALGORITHM.md

Priority (high → low):
  1. Hard gates
  2. Role job identity
  3. Buy order / spike timing
  4. Kit identity
  5. Ladder + patch
  6. Soft high-SR inspiration (tracker.gg)
  7. Light diversify (shell/flex only)

Production assembly lives in conquest_builds.build_god_build (implements these phases).
This module is the stable API + phase labels for exports, UI, and audits.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Phase registry (human + machine readable)
# ---------------------------------------------------------------------------

ALGORITHM_VERSION = "1.6.0"
ALGORITHM_DOC = "docs/BUILD_ALGORITHM.md"

PHASES: list[dict[str, str]] = [
    {
        "id": "P0_context",
        "name": "Context",
        "summary": "Kit bias, tags, effects, damage type, aspect, role profile",
    },
    {
        "id": "P1_score_universe",
        "name": "Score universe",
        "summary": "Role base × ladder × patch for every T3 shop item",
    },
    {
        "id": "P2_hard_gates",
        "name": "Hard gates",
        "summary": "Illegal items out: type, god-only, heal/LS, removed, aspect hard-bans, role toys",
    },
    {
        "id": "P3_god_rescore",
        "name": "God rescore",
        "summary": "Kit affinity + signatures + sample-weighted ladder/inspire (capped)",
    },
    {
        "id": "P4_archetype",
        "name": "Archetype",
        "summary": "Map kit × role → slot recipe (burst_mage, crit_adc, …)",
    },
    {
        "id": "P5_assemble",
        "name": "Assemble slots",
        "summary": "Fill 6 slots; ranked cores = #1; flex = mild near-peer diversify",
    },
    {
        "id": "P6_repair",
        "name": "Structural repair",
        "summary": "Pen floor, jungle openers, inject high-SR staples, actives, trim shells",
    },
    {
        "id": "P7_buy_order",
        "name": "Buy order",
        "summary": "high-SR avg_slot ⊕ role spike phases (order = half the build)",
    },
    {
        "id": "P8_explain",
        "name": "Explain + gate",
        "summary": "Why lines, inspired flags, quality checks",
    },
]

PRIORITY_LAYERS: list[dict[str, str]] = [
    {"rank": "1", "layer": "hard_gates", "rule": "Illegal items never appear"},
    {"rank": "2", "layer": "kit_identity", "rule": "Hooks + stat elasticity amplify unique scaling; identity_lock beats staples"},
    {"rank": "3", "layer": "role_job", "rule": "Role constraints (soft under lock); meta staples × staple_soft_factor"},
    {"rank": "4", "layer": "buy_order", "rule": "Spike timing before late % pen / luxury"},
    {"rank": "5", "layer": "ladder_patch", "rule": "S/A momentum × sample weight × identity mute"},
    {"rank": "6", "layer": "high_sr_inspire", "rule": "Flex only under lock; skip fighting staples; scaled by n"},
    {"rank": "7", "layer": "diversify", "rule": "Shell/flex only — never scramble openers/pen"},
]

# Empirical high-SR openers (Ranked Conquest Skill Rating — soft teacher)
ROLE_SPIKE_OPENERS: dict[str, tuple[str, ...]] = {
    "Mid": ("Book of Thoth", "Spear of Desolation", "Chronos' Pendant", "Doom Orb"),
    "Carry": ("Tyrfing", "Devourer's Gauntlet", "Transcendence", "Lernaean Bow", "The Executioner"),
    "Jungle": ("Jotunn's Revenge", "Hydra's Lament", "Transcendence", "Heartseeker", "Devourer's Gauntlet"),
    "Solo": ("Shifter's Shield", "Genji's Guard", "Breastplate of Valor", "Runeforged Hammer"),
    "Support": ("Gauntlet of Thebes", "Shifter's Shield", "Stampede", "Prophetic Cloak"),
}

ROLE_LATE_ITEMS: dict[str, tuple[str, ...]] = {
    "Mid": ("Obsidian Shard", "Rod of Tahuti", "Soul Reaver", "Soul Gem"),
    "Carry": ("Titan's Bane", "Deathbringer", "Demon Blade"),
    "Jungle": ("Titan's Bane", "Avatar's Parashu"),
    "Solo": ("Draconic Scale", "Hussar's Wings"),
    "Support": ("Spectral Armor", "Mantle Of Discord"),
}


def algorithm_card() -> dict[str, Any]:
    """Metadata embedded in exports / UI about how builds are made."""
    return {
        "version": ALGORITHM_VERSION,
        "doc": ALGORITHM_DOC,
        "phases": PHASES,
        "priority": PRIORITY_LAYERS,
        "role_spike_openers": {k: list(v) for k, v in ROLE_SPIKE_OPENERS.items()},
        "role_late_items": {k: list(v) for k, v in ROLE_LATE_ITEMS.items()},
        "philosophy": (
            "Kit payoff first (stat elasticity + identity hooks), role as constraints. "
            "Ladder/inspire weight scales with god×role n (n/n0); identity_strength mutes "
            "role staples and flex-only inspire under lock. "
            "Aspect hard-bans drop removed-mechanic families. "
            "Each build exports confidence + score_breakdown. "
            "Hard gates and soft pen floors always win — "
            "Obsidian/Titan are tank flex, not mandatory cores."
        ),
        "blend": {
            "ladder_n0": 100,
            "module": "smite2db.build_blend",
            "eval": "python -m smite2db.eval_builds",
        },
    }


def run_build_pipeline(
    conn,
    items: list[dict],
    role: str,
    god: dict,
    *,
    use_aspect: bool = False,
    aspect_id: int | None = None,
) -> dict[str, Any]:
    """
    Produce one Conquest build via the formal pipeline.

    Delegates to conquest_builds.build_god_build (implements P0–P8),
    then attaches algorithm metadata for transparency.
    """
    from .conquest_builds import build_god_build

    result = build_god_build(
        conn,
        items,
        role,
        god,
        use_aspect=use_aspect,
        aspect_id=aspect_id,
    )
    if result is None:
        return {
            "god": god.get("entity_name") or god.get("name"),
            "role": role,
            "invalid_role": True,
            "why": (
                f"{role} is not valid for this kit "
                f"(melee basics need a ranged-enabling aspect for Carry)."
            ),
            "algorithm": algorithm_card(),
            "algorithm_phases": [f"{p['id']}: {p['summary']}" for p in PHASES],
        }
    result["algorithm"] = algorithm_card()
    # Compact phase trail for debugging / UI
    result["algorithm_phases"] = [
        f"{p['id']}: {p['summary']}" for p in PHASES
    ]
    return result
