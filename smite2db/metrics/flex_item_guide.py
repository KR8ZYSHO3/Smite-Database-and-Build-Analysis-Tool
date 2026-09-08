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
    # --- OB43 new / remade enchanter package (featured first in UI) ---
    "Lotus Sickle": {
        "tags": ["concept", "aura", "sustain"],
        "roles": ["Support", "Mid"],
        "simple": "Buff, heal, or shield an ally → gain Lotus stacks. When an ally basic-attacks an enemy, a stack pops for bonus magical damage.",
        "how": "You’re charging free damage onto your ADC’s autos. Needs an ally who actually basics (Carry). Same trigger as Soul Locket — they stack together.",
        "when": "Healer/buff supports (Aphrodite, Yemoja, Guan, Sylvanus, Ix Chel) pocketing a crit/AS carry.",
        "when_not": "No ally buffs/heals/shields in kit; team never basic-attacks.",
        "buy_as": "Support 2nd after Thebes (cheap CDR). New in OB43.",
        "featured": True,
        "patch": "OB43",
    },
    "Soul Locket": {
        "tags": ["concept", "active", "sustain"],
        "roles": ["Support", "Mid"],
        "simple": "+10% stronger heals/shields. Buff/heal/shield allies to charge Soul stacks. Active: ghost form — move speed, walk through walls/players, and damage reduction from your stacks.",
        "how": "Same trigger as Lotus Sickle. Build stacks while healing, then press the active when you’re dove or need to escape. Long cooldown — treat it like a save button, not spam.",
        "when": "Enchanter supports who stay in fights and get focused.",
        "when_not": "You never heal/buff allies; you already have 3 better actives.",
        "buy_as": "Support 2nd–3rd with Sickle. Pop when dove or escaping. New in OB43.",
        "featured": True,
        "patch": "OB43",
    },
    "Vital Amplifier": {
        "tags": ["concept", "sustain"],
        "roles": ["Carry", "Solo", "Support", "Jungle"],
        "simple": "Heal yourself with an ability → stacking attack speed and basic-attack damage (up to 3 stacks).",
        "how": "Self-heal ticks (e.g. Artemis Aspect of the Wild traps) can stack this fast. Adaptive STR or INT from your other items.",
        "when": "Self-heal kits that also basic-attack (Wild Artemis, some bruisers).",
        "when_not": "No self-heal in kit; pure ability mage who never autos.",
        "buy_as": "After a STR/INT core so adaptive lands correctly. Remade OB43.",
        "featured": True,
        "patch": "OB43",
    },
    "Rod Of Asclepius": {
        "tags": ["concept", "sustain"],
        "roles": ["Support"],
        "simple": "+10% heal/shield strength. When you heal an ally, you heal even more the lower their HP is.",
        "how": "Missing-HP heal amp. Stacks with Soul Locket / Heartwood / Chandra amp.",
        "when": "True healers (Aphrodite, Yemoja, Guan Yu).",
        "when_not": "No heal abilities — dead item.",
        "buy_as": "Support heal core 3rd–5th. Remade OB43.",
        "featured": True,
        "patch": "OB43",
    },
    "Lifebinder": {
        "tags": ["concept", "active", "sustain"],
        "roles": ["Support", "Mid"],
        "simple": "Active marks an enemy; the first ally to damage them gets a big heal and shield (amped by your heal/shield strength).",
        "how": "Mark → ally hits → heal bomb. Stronger if you already built heal amp.",
        "when": "Healers who group fight and can mark the dive target.",
        "when_not": "No heal identity; active slots full.",
        "buy_as": "Healer flex active. Remade OB43.",
        "featured": True,
        "patch": "OB43",
    },
    "Chandra's Grace": {
        "tags": ["aura", "sustain"],
        "roles": ["Support"],
        "simple": "+20% heal/shield strength. Every 15s, lowest-HP nearby ally gets regen and tiny cooldown shred.",
        "how": "Aura amp for healers plus a periodic “help the dying ally” buff.",
        "when": "Support heal/amp paths.",
        "when_not": "You’re full damage with no heals.",
        "buy_as": "Support aura after Thebes. Remade OB43.",
        "featured": True,
        "patch": "OB43",
    },
    "Serrated Edge": {
        "tags": ["concept", "sustain"],
        "roles": ["Jungle", "Solo"],
        "simple": "For each non-ult ability on cooldown you gain Strength and lifesteal (up to 3 stacks).",
        "how": "Ability-cycling junglers stay stacked mid-fight. High LS + free STR.",
        "when": "Jungle assassins/warriors with short ability cooldowns.",
        "when_not": "You never cast; pure AA with no ability loop.",
        "buy_as": "Jungle 1st–3rd on CD-heavy kits.",
        "featured": True,
        "patch": "OB43",
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
        "simple": "+20% heal/shield strength, faster heal cooldowns; heals you cast store a bank; active dumps that heal to nearby allies.",
        "how": "Spam heals to fill the bank → press active for a team heal bomb. Stacks with other heal-amp items.",
        "when": "Healer supports (Yemoja, Aphro, etc.).",
        "when_not": "No heal abilities; you already have 3 actives.",
        "buy_as": "Healer identity item 2nd–4th. Remade OB43.",
        "featured": True,
        "patch": "OB43",
    },
    "Daybreak Gavel": {
        "tags": ["concept"],
        "roles": ["Carry", "Solo", "Support", "Mid"],
        "simple": "Heal yourself with a healing ability to build stacks; your next non-heal ability spends them for a big STR or INT buff.",
        "how": "Self-heal → stacks → cast 2/3/ult to cash power. Adaptive STR/INT from your other items.",
        "when": "Self-heal kits (Wild Artemis traps, some bruisers) that also cast non-heals.",
        "when_not": "No self-heal; pure ally-heal support with no dump spell.",
        "buy_as": "Pair with Vital Amplifier on self-heal AA paths. Remade OB43.",
        "featured": True,
        "patch": "OB43",
    },
    "Eros' Bow": {
        "tags": ["concept", "active", "aura"],
        "roles": ["Support"],
        "simple": "Mark an ally as Beloved. Basic-attack to stack Devotion, then buff/heal/shield them to dump Passion (bonus STR and INT on that ally).",
        "how": "Same trigger family as Sickle/Locket. Fiddly — mark, auto, then heal. Strong pocket amp if you commit.",
        "when": "Enchanter supports who can AA safely next to the carry.",
        "when_not": "You hate actives / never basic-attack; prefer Sickle+Locket only.",
        "buy_as": "Optional 4th after Sickle/Locket — skip if too many actives. Remade OB43.",
        "featured": True,
        "patch": "OB43",
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
            "featured": bool(data.get("featured")),
            "patch": data.get("patch") or "",
        }
        by_name[name] = entry
        by_name[display] = entry
        by_name[display.lower()] = entry
        if display not in seen_display:
            seen_display.add(display)
            items.append(entry)

    # Featured (new / remade patch items) first, then A–Z
    items.sort(key=lambda x: (0 if x.get("featured") else 1, x["name"].lower()))
    featured = [it for it in items if it.get("featured")]
    tags = sorted({t for it in items for t in it["tags"]})
    return {
        "title": "Items explained — simple English",
        "disclaimer": (
            "Plain-language guides for new and situational items. "
            "Not live win rates. Primary builds come from this site’s kit + patch model — "
            "not copied from other build sites."
        ),
        "featured_title": "New / remade this patch (OB43)",
        "featured": featured,
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
