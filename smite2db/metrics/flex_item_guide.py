"""
Plain-English guide for situational / concept items.

Game tooltips are dense. These blurbs answer:
  - what it actually does (simple)
  - when to buy
  - when to skip
"""

from __future__ import annotations

from typing import Any

# Categories for UI filters
# answer | concept | active | aura | sustain | shred | anti_cc | vision

FLEX_ITEM_GUIDE: dict[str, dict[str, Any]] = {
    # --- Answer / every-game flex ---
    "Spectral Armor": {
        "tags": ["answer", "aura"],
        "roles": ["Support", "Solo"],
        "simple": "You and nearby allies take less damage from critical hits.",
        "how": "Passive aura. Stand near your carry — they get part of the anti-crit too.",
        "when": "Enemy has a crit Carry (or anyone building crit). Default Support flex almost every game.",
        "when_not": "No crit threat at all (full ability damage lobby).",
        "buy_as": "2nd–4th item on Support after Thebes/Shifter’s.",
    },
    "Midgardian Mail": {
        "tags": ["answer"],
        "roles": ["Support", "Solo"],
        "simple": "When they basic-attack you, their attack speed drops (stacks).",
        "how": "They freefire you → they get slower. You want them hitting you (frontline).",
        "when": "ADC or AA jungler is freefiring your face.",
        "when_not": "Nobody basics you (pure mage poke from range).",
        "buy_as": "Support/Solo tank path when AA is the problem.",
    },
    "Stygian Anchor": {
        "tags": ["answer", "shred"],
        "roles": ["Support", "Solo"],
        "simple": "Your damage cuts enemy healing 25% and slows their attack speed in stacks.",
        "how": "Real anti-heal on ability damage (not Contagion). Also shreds AS.",
        "when": "Aphro, Yogi’s, Cu sustain, heavy lifesteal, heal comps.",
        "when_not": "Zero healing on the enemy team.",
        "buy_as": "Support/Solo whenever heals are real — don’t wait until item 6.",
    },
    "Brawler's Beat Stick": {
        "tags": ["answer", "shred"],
        "roles": ["Solo", "Jungle", "Carry", "Mid"],
        "simple": "Hitting gods applies 25% healing reduction + you stack combat stats.",
        "how": "Anti-heal for bruisers/hybrids. Adaptive STR or INT from your build.",
        "when": "Enemy heals/lifesteals and you’re a damage or hybrid role.",
        "when_not": "No heals; pure tank with no damage to apply it.",
        "buy_as": "Solo/Jungle/Carry into sustain; sometimes Mid hybrid.",
    },
    "Brawler’s Beat Stick": {
        "tags": ["answer", "shred"],
        "roles": ["Solo", "Jungle", "Carry", "Mid"],
        "simple": "Hitting gods applies 25% healing reduction + you stack combat stats.",
        "how": "Anti-heal for bruisers/hybrids. Adaptive STR or INT from your build.",
        "when": "Enemy heals/lifesteals and you’re a damage or hybrid role.",
        "when_not": "No heals; pure tank with no damage to apply it.",
        "buy_as": "Solo/Jungle/Carry into sustain; sometimes Mid hybrid.",
    },
    "Divine Ruin": {
        "tags": ["answer", "shred"],
        "roles": ["Mid"],
        "simple": "Mage anti-heal: your god damage cuts healing 25% + lightning proc.",
        "how": "The mid-lane answer to Aphro/Yogi’s/sustain. Also INT power.",
        "when": "Any real healing on the enemy (or you’re not sure — safe default mid).",
        "when_not": "Full glass lobby with zero sustain and you need pure burst sooner.",
        "buy_as": "Mid 2nd–4th item into heal comps.",
    },
    "Toxic Blade": {
        "tags": ["answer"],
        "roles": ["Carry", "Jungle"],
        "simple": "Your basics apply healing reduction and attack-speed slow.",
        "how": "AA-based anti-heal. You must basic-attack them.",
        "when": "You’re Carry/AA jungle into heals.",
        "when_not": "Ability-only mage; you never auto.",
        "buy_as": "Carry flex vs heal / high AS.",
    },
    "Genji's Guard": {
        "tags": ["answer"],
        "roles": ["Support", "Solo", "Jungle"],
        "simple": "Big magical protection; getting hit by magic shortens your cooldowns.",
        "how": "Mage damage answer. They hit you with magic → you get CDs back.",
        "when": "Fed mid mage or magical damage everywhere.",
        "when_not": "All physical lobby (ADC + phys jungle only).",
        "buy_as": "Support/Solo default into magic.",
    },
    "Phoenix Feather": {
        "tags": ["answer", "active"],
        "roles": ["Support", "Solo"],
        "simple": "Magic bulk + active pulses that heal you and true-damage nearby enemies.",
        "how": "Tank mprot item with a panic heal/true damage button.",
        "when": "Magic damage + you want a self-peel active.",
        "when_not": "You need pure aura peel and never press actives.",
        "buy_as": "Solo/Support into mages.",
    },
    "Magi's Cloak": {
        "tags": ["answer", "anti_cc"],
        "roles": ["Support", "Solo", "Mid", "Carry", "Jungle"],
        "simple": "Every so often, the next hard CC on you is blocked (short CC immunity).",
        "how": "Anti-lockdown bubble on a cooldown. Saves you from root/stun openers.",
        "when": "Heavy hard CC / dive (Bastet, Fenrir, Ymir lock, etc.).",
        "when_not": "Soft poke only, no real CC threat.",
        "buy_as": "Anyone getting locked before they can act.",
    },
    "Spirit Robe": {
        "tags": ["answer", "anti_cc"],
        "roles": ["Support", "Solo"],
        "simple": "When hard CC’d, you gain a big dual-prot buff and a small heal.",
        "how": "CC makes you tankier briefly. Note: enemies can ‘proc’ this on purpose.",
        "when": "Lots of hard CC and you’re frontline.",
        "when_not": "You want to avoid giving them free value; Magi’s is cleaner for ‘don’t get CC’d’.",
        "buy_as": "Tank flex into CC-heavy lobbies.",
    },
    "Mantle Of Discord": {
        "tags": ["answer", "anti_cc", "active"],
        "roles": ["Support", "Solo"],
        "simple": "When you drop low, you stun nearby enemies and get CC immune briefly.",
        "how": "Panic button passive at low HP. Long cooldown.",
        "when": "You’re the dive target and need a last-stand peel.",
        "when_not": "You never drop low / never frontline.",
        "buy_as": "Late tank slot.",
    },
    "Mantle of Discord": {
        "tags": ["answer", "anti_cc"],
        "roles": ["Support", "Solo"],
        "simple": "When you drop low, you stun nearby enemies and get CC immune briefly.",
        "how": "Panic button passive at low HP. Long cooldown.",
        "when": "You’re the dive target and need a last-stand peel.",
        "when_not": "You never drop low / never frontline.",
        "buy_as": "Late tank slot.",
    },

    # --- Concept / underpicked ---
    "Xibalban Effigy": {
        "tags": ["concept", "active"],
        "roles": ["Support", "Solo"],
        "simple": "For 4s you only take half damage, then you pay back what you blocked (as physical). Can’t kill yourself below 5% HP.",
        "how": "Press when a big burst is landing. You delay death, not become immortal. Moonlight = half the payback.",
        "when": "You’re a frontline tank and enemy has big ult combos.",
        "when_not": "Glass builds; long AA freefire with no spike; pressing it with nobody hitting you.",
        "buy_as": "2nd–3rd item on Ymir/Atlas/Xing-style tanks after some bulk.",
    },
    "Vital Amplifier": {
        "tags": ["concept", "aura"],
        "roles": ["Support", "Mid"],
        "simple": "When you heal yourself or an ally with an ability, they get attack speed and attack damage (stacks 3×).",
        "how": "Heals = AA steroids for your team. Needs a healing kit and allies who basic-attack.",
        "when": "You’re Yemoja/Aphro/Ra/Baron-style healer with an ADC who autos.",
        "when_not": "No heals in kit; team is all ability mages who never AA.",
        "buy_as": "Healer Support/Mid 2nd–3rd after aura/core.",
    },
    "Umbral Link": {
        "tags": ["concept", "aura", "sustain"],
        "roles": ["Solo", "Jungle", "Support"],
        "simple": "Above 50% HP, your lifesteal healing is shared with nearby allies (and gives them small prots).",
        "how": "You’re a mobile vamp aura. Must build lifesteal and stay healthy next to teammates.",
        "when": "Physical LS bruisers (Fenrir, Kali, Chaac paths) who group fight.",
        "when_not": "No LS; always under 50% HP; you never stand near allies.",
        "buy_as": "After or with Bloodforge/DG-style LS cores.",
    },
    "Contagion": {
        "tags": ["concept"],
        "roles": ["Support", "Solo"],
        "simple": "Enemies who hit you or lifesteal off you get stacks. You AA or hard CC them to explode stacks for % of YOUR max HP damage.",
        "how": "Not real anti-heal. Soft punish freefire/LS. You must detonate with AA or hard CC.",
        "when": "You’re the freefire tank into LS ADC/bruisers.",
        "when_not": "You need 25% heal cut (buy Stygian/Brawler’s/Divine instead); you’re mid glass.",
        "buy_as": "Tank flex; never your only anti-heal into Aphro.",
    },
    "Erosion": {
        "tags": ["answer", "shred"],
        "roles": ["Support", "Solo", "Jungle"],
        "simple": "Enemy shields near you are much weaker; you gain prots when that happens.",
        "how": "Anti-shield aura. Great into shield-heavy kits/items.",
        "when": "Lots of shields (Berserk shields, item shields, kit shields).",
        "when_not": "Nobody shields — wasted slot.",
        "buy_as": "Situational tank/bruiser.",
    },
    "Yogi's Necklace": {
        "tags": ["sustain", "concept"],
        "roles": ["Solo", "Support"],
        "simple": "Fat HP/mana + constant heal for 0.5% of your max HP every second.",
        "how": "Regen brick. On Cu, mana also becomes more HP via his passive. Wins long fights, not burst.",
        "when": "You want to outlast lane and never die to chip.",
        "when_not": "You need damage spike or real anti-heal answer on you.",
        "buy_as": "Solo sustain first item (turtle style).",
    },
    "Soul Reaver": {
        "tags": ["shred", "concept"],
        "roles": ["Mid", "Solo"],
        "simple": "Ability hits deal extra damage based on the target’s health (base + item HP).",
        "how": "Tank shred for mages. Still goes through prots — buy pen too.",
        "when": "Fat tanks, Thebes stacks, Yogi’s bricks.",
        "when_not": "All glass enemies and you need pure burst/CDR sooner.",
        "buy_as": "Mid/offline mage with Obsidian/Deso.",
    },
    "Ethereal Staff": {
        "tags": ["shred", "concept"],
        "roles": ["Mid", "Solo"],
        "simple": "Ability hits steal max HP (and mana) from the target over time stacks.",
        "how": "You get thicker, they get thinner across the fight. Needs multiple ability hits.",
        "when": "Long fights vs HP stackers.",
        "when_not": "You cast once and die; no multi-hit kit.",
        "buy_as": "With Reaver/pen on shred mages.",
    },
    "Stone of Binding": {
        "tags": ["shred"],
        "roles": ["Support", "Solo", "Jungle", "Mid"],
        "simple": "Your hard CC shreds their physical and magical protections (stacks).",
        "how": "Only works if you land hard CC (stun/root/knockup/etc.).",
        "when": "You have reliable hard CC (Ymir, Atlas, Hades, etc.).",
        "when_not": "Soft CC only / no CC in kit.",
        "buy_as": "CC gods — synergy item, not random bulk.",
    },
    "Void Stone": {
        "tags": ["shred", "aura"],
        "roles": ["Solo", "Support", "Jungle"],
        "simple": "Nearby enemies have less magical protection (stronger up close).",
        "how": "Aura shred for magical damage dealers on your team (or you).",
        "when": "You’re frontline with mage allies, or magical bruiser.",
        "when_not": "All physical team and you’re not magical.",
        "buy_as": "Frontline aura slot.",
    },
    "Void Shield": {
        "tags": ["shred", "aura"],
        "roles": ["Solo", "Support", "Jungle"],
        "simple": "Nearby enemies have less physical protection (stronger up close).",
        "how": "Aura shred for physical carries/junglers.",
        "when": "You’re peeling in front of a physical ADC/jungle.",
        "when_not": "Full magical team.",
        "buy_as": "Frontline aura slot.",
    },
    "Obsidian Shard": {
        "tags": ["shred"],
        "roles": ["Mid"],
        "simple": "% magical penetration + first ability cast gets bonus pen (Shattering).",
        "how": "Makes mage damage actually land on tanks. First cast of the cycle is juicier.",
        "when": "Any mid that needs to kill tanks / bulk.",
        "when_not": "Never finishing pen into triple tank (you’ll bounce).",
        "buy_as": "Mid core, often 4th–6th.",
    },
    "Titan's Bane": {
        "tags": ["shred"],
        "roles": ["Carry", "Jungle", "Solo"],
        "simple": "% physical penetration + first ability cast bonus pen (Shattering).",
        "how": "Same idea as Obsidian for physical. Don’t skip into bulk.",
        "when": "Physical damage roles mid/late.",
        "when_not": "You only AA and never cast (still usually good).",
        "buy_as": "Carry/Jungle pen slot.",
    },

    # --- Actives / toys ---
    "Heartwood Charm": {
        "tags": ["concept", "active", "sustain"],
        "roles": ["Support", "Mid"],
        "simple": "Healing abilities cool down faster; heals you cast store a bank; active dumps that heal to nearby allies.",
        "how": "Spam heals to fill the bank → press active for a team heal bomb.",
        "when": "Healer supports (Yemoja, Aphro, etc.).",
        "when_not": "No heal abilities.",
        "buy_as": "Healer identity item 2nd–4th.",
    },
    "Daybreak Gavel": {
        "tags": ["concept"],
        "roles": ["Support", "Mid"],
        "simple": "Healing different gods builds stacks; your next non-heal ability spends stacks for a big STR/INT buff.",
        "how": "Heal unique allies → cast damage/utility spell to cash power.",
        "when": "Team healers who also cast non-heal abilities.",
        "when_not": "You only damage and never heal.",
        "buy_as": "Baron/Aphro/Yemoja-style paths.",
    },
    "Eros' Bow": {
        "tags": ["concept", "active", "aura"],
        "roles": ["Support", "Carry"],
        "simple": "Mark an ally; your basic attacks heal that ally for a % of your max HP.",
        "how": "You’re an AA battery for the carry. Mark them and auto anything.",
        "when": "You basic-attack a lot and peel with the ADC.",
        "when_not": "Ability-only support who never autos.",
        "buy_as": "Hybrid support / weird duo.",
    },
    "Gluttonous Grimoire": {
        "tags": ["concept", "sustain"],
        "roles": ["Mid", "Solo"],
        "simple": "Part of your lifesteal is stored as bonus damage on your next basic attack.",
        "how": "Cast/LS → bank → AA to dump a chunk. Stores more at full HP.",
        "when": "INT + lifesteal mages (Hades, Anubis-style).",
        "when_not": "No LS; you never basic attack.",
        "buy_as": "With Bancroft/Blood-Bound + pen.",
    },
    "Sanguine Lash": {
        "tags": ["concept", "active"],
        "roles": ["Jungle", "Solo"],
        "simple": "Nearby enemies take % HP damage over time; scales with your lifesteal. Active makes ticks faster.",
        "how": "Melee sit-on-them item. Build LS and stay in range.",
        "when": "Melee LS assassins/bruisers.",
        "when_not": "Ranged poke; no LS.",
        "buy_as": "Fenrir/Kali-style after LS core.",
    },
    "Doublet of Binding": {
        "tags": ["concept", "active"],
        "roles": ["Support"],
        "simple": "Active links an ally: you take 20% of their damage (mitigated by your dampening).",
        "how": "Bodyguard button. Stack damp/prots so the redirected damage is soft.",
        "when": "You peel one carry hard (Athena/Geb/Ymir).",
        "when_not": "You’re the one dying first with no bulk.",
        "buy_as": "Support peel path.",
    },
    "Eye of Erebus": {
        "tags": ["concept", "active"],
        "roles": ["Support", "Solo", "Jungle"],
        "simple": "Active drops an eye that blasts % max HP, reveals, and slows the first enemy in range.",
        "how": "Trap/zone tool + adaptive power. Place on chokes or objectives.",
        "when": "Roam/setup tanks and bruisers.",
        "when_not": "You never use actives or set vision traps.",
        "buy_as": "Fun roam identity item.",
    },
    "Eye of Providence": {
        "tags": ["vision", "answer"],
        "roles": ["Support"],
        "simple": "Dual prot + free sentry wards over time; gold for killing wards.",
        "how": "Vision item. Keeps wards in your inventory loop.",
        "when": "Enemy wards everything / you want free sentry uptime.",
        "when_not": "You already have perfect vision and need combat stats more.",
        "buy_as": "Support flex for vision games.",
    },
    "Alchemist Coat": {
        "tags": ["concept", "sustain"],
        "roles": ["Solo", "Support", "Mid"],
        "simple": "Using consumables gives dampening; free Multi Potion over time if you have a slot.",
        "how": "Potion engine + tankiness when you chug.",
        "when": "You buy pots and want free value.",
        "when_not": "Never use consumables.",
        "buy_as": "Niche sustain tank.",
    },
    "Prophetic Cloak": {
        "tags": ["concept"],
        "roles": ["Support", "Solo"],
        "simple": "Damaging gods stacks protections vs their damage type; evolves into stronger dual prot + mitigation.",
        "how": "Adaptive tank: fight people → stack the right prots → evolve.",
        "when": "Frontliners in long games who hit a lot of gods.",
        "when_not": "You need an immediate answer (Spectral/Genji’s) this fight.",
        "buy_as": "Early tank scaler; evolve is the payoff.",
    },
    "Omen Drum": {
        "tags": ["concept", "active"],
        "roles": ["Mid", "Jungle", "Solo"],
        "simple": "Active: abilities mark enemies for 5s, then a % of the damage you dealt is echoed to all marked.",
        "how": "Multi-hit ability combos shine. Press before full rotation.",
        "when": "Ability spam kits in teamfights.",
        "when_not": "One-spell pokes; you forget actives.",
        "buy_as": "Identity active on multi-cast gods.",
    },
    "Staff of Myrddin": {
        "tags": ["concept", "active"],
        "roles": ["Mid"],
        "simple": "Active: your next non-ult ability has no cooldown.",
        "how": "Double-cast button. Huge on burst mages with a key spell.",
        "when": "Your combo is one ability twice (or reset a big CD).",
        "when_not": "Low impact abilities; you need pen/heal cut first.",
        "buy_as": "Late mid luxury active.",
    },
    "Circe's Hexstone": {
        "tags": ["concept", "active"],
        "roles": ["Solo", "Support", "Jungle"],
        "simple": "Active: poly dash with CC immune and prots; hitting a god knocks up and deals % current HP.",
        "how": "Engage/peel dash toy. Build so you can afford the active slot.",
        "when": "You want a displacement engage on a tank.",
        "when_not": "Active slots already full of better tools.",
        "buy_as": "Fun tank active.",
    },
    "Bloodforge": {
        "tags": ["sustain", "active"],
        "roles": ["Jungle", "Carry", "Solo"],
        "simple": "STR + lifesteal; active gives a big health shield that also buffs LS.",
        "how": "All-in vamp. Press shield when you dive.",
        "when": "Physical divers who auto/spell vamp.",
        "when_not": "Pure tank with no damage; mage INT path.",
        "buy_as": "Jungle/Carry all-in slot.",
    },
    "Bancroft's Talon": {
        "tags": ["sustain", "concept"],
        "roles": ["Mid"],
        "simple": "The lower your HP, the more INT and lifesteal you get.",
        "how": "Comeback / low-HP fighter mage. Risky: rewards being hurt.",
        "when": "Aggressive LS mages who fight in the red.",
        "when_not": "You play full HP safe poke only (still usable, less ideal).",
        "buy_as": "With Grimoire / LS mage paths.",
    },
    "Amanita Charm": {
        "tags": ["concept", "active", "sustain"],
        "roles": ["Support", "Solo"],
        "simple": "Active drops a healing mushroom zone that heals and stacks damage reduction.",
        "how": "Place for team heal + DR in a pit or under tower.",
        "when": "Teamfight support who holds ground.",
        "when_not": "You never group or use actives.",
        "buy_as": "Support active heal toy.",
    },
    "Stampede": {
        "tags": ["active", "answer"],
        "roles": ["Support"],
        "simple": "Active: you and nearby allies get slow immunity and a huge decaying speed boost.",
        "how": "Engage or disengage button for the whole team.",
        "when": "You need team move for fights/rotates (classic support).",
        "when_not": "Rarely — it’s a standard support tool when speed wins fights.",
        "buy_as": "Support 3rd–5th often.",
    },
    "Gauntlet of Thebes": {
        "tags": ["aura"],
        "roles": ["Support"],
        "simple": "Stacks max HP from assists; fully stacked gives more HP and dual prots for the team aura fantasy.",
        "how": "Support farm item. Stack on minions/gods → evolve power.",
        "when": "Almost every Support game as core.",
        "when_not": "You’re not actually supporting (full damage mid).",
        "buy_as": "Support item 1–2.",
    },
    "Shifter's Shield": {
        "tags": ["answer"],
        "roles": ["Solo", "Support", "Jungle"],
        "simple": "High HP: free STR or INT. Low HP: free dual protections.",
        "how": "Hybrid tank/damage. Healthy = offline damage; hurt = tank mode.",
        "when": "Solo/Support default bulk almost always.",
        "when_not": "Full glass ADC/mid who never wants prots.",
        "buy_as": "Universal frontline core.",
    },
}


def build_flex_item_guide() -> dict[str, Any]:
    """Export-ready guide: list + by_name + tag index."""
    # Prefer straight apostrophe keys for display; merge curly duplicates in by_name only
    items: list[dict[str, Any]] = []
    by_name: dict[str, dict[str, Any]] = {}
    seen_display: set[str] = set()

    for name, data in FLEX_ITEM_GUIDE.items():
        # Normalize display name (straight apostrophe)
        display = name.replace("’", "'").replace("'", "'")
        entry = {
            "name": display,
            "tags": list(data.get("tags") or []),
            "roles": list(data.get("roles") or []),
            "simple": data.get("simple") or "",
            "how": data.get("how") or "",
            "when": data.get("when") or "",
            "when_not": data.get("when_not") or "",
            "buy_as": data.get("buy_as") or "",
        }
        by_name[name] = entry
        by_name[display] = entry
        by_name[display.lower()] = entry
        if display not in seen_display:
            seen_display.add(display)
            items.append(entry)

    items.sort(key=lambda x: x["name"].lower())
    tags = sorted({t for it in items for t in it["tags"]})
    return {
        "title": "Flex & weird items — simple English",
        "disclaimer": (
            "Plain-language guides for situational and concept items. "
            "Not live win rates. When in doubt: answer the lobby (heal/crit/AS/magic/CC) before toys."
        ),
        "items": items,
        "by_name": {k: v for k, v in by_name.items() if isinstance(k, str)},
        "tags": tags,
        "tag_labels": {
            "answer": "Lobby answers",
            "concept": "Concept / underpicked",
            "active": "Has an active",
            "aura": "Aura / team",
            "sustain": "Healing / LS",
            "shred": "Pen / anti-tank",
            "anti_cc": "Anti-CC",
            "vision": "Vision",
        },
    }


def lookup_item_guide(name: str) -> dict[str, Any] | None:
    if not name:
        return None
    guide = build_flex_item_guide()
    by = guide["by_name"]
    if name in by:
        return by[name]
    return by.get(name.replace("’", "'")) or by.get(name.lower())
