# Conquest Build Algorithm

**Purpose:** Produce ranked-viable Conquest paths (1 starter + 6 items) that are  
**kit-true**, **role-correct**, **spike-ordered**, and **softly informed by high-SR play** —  
without becoming a frozen meta photocopier.

**Inventory model (SMITE 2):** starter slot separate · 6 shop items · ≤2–3 On-Use actives · relics separate.

---

## Design principles (priority order)

When two signals conflict, **higher wins**:

| Rank | Layer | Rule |
|-----:|--------|------|
| 1 | **Hard gates** | Illegal items never appear (damage type, god-only, removed shop, healer-only, etc.) |
| 2 | **Role job** | Carry shreds/crits, Mid online pen, Jungle ganks (no Omen-as-core), Solo offline+bulk, Support aura/peel (**no Jotunn/Titan/Hydra damage cores**) |
| 3 | **Buy order / spikes** | Item *sequence* matters as much as the set; early online before late % pen / luxury |
| 4 | **Kit identity** | Tags, effects, scaling (STR/INT), archetype slot recipe |
| 5 | **Ladder + patch** | S/A item momentum; C/D soft penalty; role-gated so tank S doesn’t invade Mid |
| 6 | **High-SR inspiration** | Soft frequency + average inventory slot from tracker.gg — **nudge, never override 1–3** |
| 7 | **Light diversify** | Only shell / last flex so gods aren’t clones; **never scramble pen/opener cores** |

Troll / meme and counter paths are **separate pipelines** (same gates, different objective).

---

## Inputs

```
god          → kit metrics, abilities, scaling, tags, optional aspect, overrides
role         → Carry | Mid | Jungle | Solo | Support
items        → wiki catalog (stats, cost, tier, passive, ladder, patch axes)
inspiration  → optional data/tracker_inspiration.json (high-SR Ranked Conquest)
kit_overrides→ optional force tags / prefer / ban
```

---

## Pipeline overview

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 0  Context                                               │
│  Kit bias, tags, effects, damage type, aspect, role profile     │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1  Score universe                                        │
│  Role base score × ladder × patch for every T3 shop item        │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2  Hard gates (filter pool)                              │
│  Type bans · god-specific · heal/LS · removed · role toys       │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3  God rescore                                           │
│  Kit affinity + tag signatures + soft high-SR boost (capped)    │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4  Archetype + slot recipe                               │
│  e.g. burst_mage, crit_adc, burst_assassin, sustain_solo…       │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 5  Assemble 6 slots                                      │
│  Ranked cores = argmax; flex = mild diversify among near-peers  │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 6  Structural repair                                     │
│  Pen floor · jungle openers · inject high-SR staples · actives  │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 7  Buy order (critical)                                  │
│  high-SR avg_slot ⊕ role spike phases ⊕ cost tie-break          │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 8  Explain + quality gate                                │
│  Per-item why · inspired flags · uniqueness/pen checks          │
└─────────────────────────────────────────────────────────────────┘
```

Implementation entry: `smite2db.build_pipeline.run_build_pipeline` → used by `build_god_build`.

---

## Phase 0 — Context

1. Load god kit metrics (`god_scaling_bias`).
2. Optional aspect merge (`build_aspect_bias`).
3. Derive:
   - `primary` scaling (STR / INT / Mixed)
   - `mage` / `physical`
   - `tags` (burst, aa, gap_close, mana_stack, self_sustain, heal, …)
   - structured `effects` for explanations
4. Apply `data/kit_overrides.json` (force tags / prefer / ban).
5. Select `ROLE_PROFILES[role]` (stat weights, starter prefs, job blurb).

---

## Phase 1 — Score universe

For each catalog item:

```
role_base = Σ_axis weight[axis] × normalize(stat[axis])
          + type/tag bonuses
          + ladder_boost(S/A/B/C/D, rank, role-gated)
          + patch_axis affinity
```

Ladder is **strong but not supreme**: S/A beat mediocre peers; kit + gates still win.

---

## Phase 2 — Hard gates

**Remove** from the pool (not “downrank”):

| Gate | Rule |
|------|------|
| Damage type | No mage pen/power cores on physical; no hunter STR toys on pure mages |
| God-specific | Acorns **Ratatoskr only**; Vulcan mods / Baron’s Brew / etc. never shared shop |
| Removed shop | e.g. Eye of Providence |
| Heal cores | Asclepius / Lifebinder only true healers (Aphrodite, Guan Yu, Yemoja + kit) |
| Mage LS | Bancroft / Typhon / Gluttonous only self-sustain kits |
| Role toys | ADC crit toys off ability jungle; Jotunn/Crusher off AA Carry; etc. |
| Overrides | `ban_items` always |

Starter selection uses the same spirit (no god-only starters on wrong gods).

---

## Phase 3 — God rescore

```
score = 0.55 × role_base
      + kit_alignment(scaling, tags, effects)
      + tag_signature_boost(item, tags)
      + tracker_inspire(item, god, role)   # capped ~+32 god×role, ~+16 role
      + prefer_overrides
```

**Inspiration is soft:** high-SR frequency and early `avg_slot` raise pick chance;  
they cannot reintroduce gated items or skip pen/role identity.

---

## Phase 4 — Archetype

`detect_archetype(bias, role, mage, physical)` maps kit × role → recipe id.

Examples:

| Role | Archetypes (examples) |
|------|------------------------|
| Mid | burst_mage, mana_mage, dot_mage, zone_mage, spam_mage, sustain_mage |
| Carry | crit_adc, onhit_adc, power_adc, mage ADC variants |
| Jungle | burst_assassin, sustain_assassin, aa_assassin, mage_jungle |
| Solo | tank_solo, sustain_solo, bruiser_solo, mage_solo, shield_solo |
| Support | peel / lockdown / shield / heal / aura_support |

Each maps to ordered **slots** (identity of the 6-item grid), e.g.:

```
burst_mage:     flat_pen → pct_pen → power → cdr → defense → luxury
crit_adc:       as_core → ls_core → pct_pen → crit_core → power → defense
burst_assassin: gap → flat_pen → pct_pen → power → cdr → defense
sustain_solo:   hybrid_bulk → power_bruiser → defense → …
peel_support:   aura → mitigate → defense → …
```

Slot order is **assembly priority**, not final buy order (Phase 7 reorders).

---

## Phase 5 — Assemble six slots

For each slot in the recipe:

1. Filter pool with `_item_matches_slot` (role-aware: e.g. jungle `gap` = Jotunn/Hydra/stack only).
2. Rank candidates: role score + **meta core boosts** + signatures.
3. **Ranked core slots** (`flat_pen`, `pct_pen`, `gap`, `as_core`, `aura`, …): take **#1**.
4. **Flex slots** (defense, luxury, some power): mild diversify among **near-best** peers only.

Then signature inject (kit keys) and fill empties.

**Do not** salt Jotunn vs Arondight; that was how openers broke.

---

## Phase 6 — Structural repair

Applied in order:

1. **`_ensure_pen_in_path`** — damage roles need matching pen. Soft coverage is enough:
   - matching pen total ≥ `MIN_BUILD_PEN` (20), **or**
   - flat pen piece + (light % pen ≥10 *or* role shred: Exec/OBow/Qin / Magus/Void/Grimoire).
   Do **not** force Obsidian Shard / Titan's Bane when soft coverage already holds. Those stay on **`tanks_hp` flex chips** for fat fronts.
2. **Jungle normalize** — standard openers; cap opener-family ≤2; strip ADC toys on ability kits; skip second pen inject when soft coverage is met.
3. **`_ensure_inspired_cores`** — if high-SR openers/staples missing (Deso, Book, Tyrfing, Jotunn, Thebes, Shifter…), inject 1–2 legal ones by replacing weakest non-core. Shard/Titan are **not** role staples.
4. **Trim excess defense** on Carry/Mid/Jungle (max 1 pure shell).
5. **Active budget** — default ≤2 shop actives (≤3 melee physical Solo/Jungle).

---

## Phase 7 — Buy order (spike timing)

Order is half the build. Sort key:

```
primary:  tracker avg_slot(god×role) if sample enough
else:     role heuristic phase (0 = open … 5 = luxury)
then:     cost / sub-priority / score
```

### High-SR role openers (empirical, Ranked Conquest)

| Role | Open early (phase 0–1) | Mid | Late (never open) |
|------|------------------------|-----|-------------------|
| **Mid** | Book of Thoth, Deso, Chronos Pendant, Doom Orb | Magus / flat pen | Obsidian, Tahuti, Soul Reaver, Soul Gem |
| **Carry** | Tyrfing, DG, Transcendence, AS shred | power / on-hit | Titan’s, Deathbringer |
| **Jungle** | Jotunn’s, Hydra’s, Trans/HS/DG | Crusher / Pendulum | Titan’s, luxury actives |
| **Solo** | Shifter’s | Genji / BP / hybrid | pure aura shell spam |
| **Support** | Thebes, Shifter’s, Stampede, Prophetic | Genji / BP / Shell | Spectral as counter, not item 1 |

Wrong order (Obsidian/Titan first, stacks last) fails even if the six names look “meta.”

---

## Phase 8 — Explain & gate

- Per-item `why` from kit effects + optional `inspired: high-SR …`
- Build blurb: archetype, tags, pen total, actives, inspiration count
- Quality gate: uniqueness soft-warn; pen fail list; no hard block on mild clones for spike roles

---

## Scoring formula (single item, conceptual)

```
if hard_gate_fail(item):  score = −∞  (excluded)

score = 0.55 · RoleScore(item, role)
      + KitAlign(item, god_kit)
      + LadderBoost(item, role)          # S/A up, C/D down; tank S muted on Mid/Carry
      + TagSignature(item, tags)
      + min(GOD_ROLE_CAP, InspireGodRole) + min(ROLE_CAP, InspireRole)
      + PreferOverride − BanOverride

# early high-SR items get slight inspire multiplier when avg_slot ≤ 1.5
```

Path score is **not** sum of item scores alone — structure (pen, opener, order) is enforced after.

---

## Role job cards (what “correct” means)

| Role | Job | Path identity |
|------|-----|----------------|
| **Carry** | Backline sustained DPS | Online AS/LS/stack → shred/pen → crit finisher |
| **Mid** | Clear + burst/zone | Online power/flat pen → % pen → luxury |
| **Jungle** | Gank spike | Jotunn/Hydra/stack → pen → power |
| **Solo** | Hold + offline | Shifter/hybrid → bulk + residual damage |
| **Support** | Aura + peel | Thebes/Shifter/Stampede → team shell → counters |

---

## Explicit non-goals

- **Not** pure copy of one ladder week’s most common 6 items.
- **Not** max random uniqueness (that scrambled Jotunn → Bloodforge openers).
- **Not** “every god unique 6” if that means illegal or off-role cores.
- **Not** troll builds (separate: kit-true annoyance / max-stat greed).
- **Not** match-outcome ML yet (no per-build WR model); high-SR is a prior, not proof.

---

## Refresh loop (ops)

```text
1. python -m smite2db.scrape / refresh     # wiki + metrics
2. python -m smite2db.analyze run         # tiers
3. python -m smite2db.tracker_inspire     # high-SR soft prior + avg_slot
4. python -m smite2db.export_web          # docs/data + standalone
```

Empty inspiration scrapes **must not** overwrite a good snapshot (guard in `save_inspiration`).

---

## Conflict resolution examples

| Situation | Winner |
|-----------|--------|
| High-SR loves Soul Gem first mid | Order phase: Soul Gem late; may appear item 4–5 if kit allows |
| Tag wants ADC crit on ability Susano | Gate: crit toys banned; Jotunn path wins |
| Ladder S tank item on Mid | Ladder muted on defensive for Mid; pen cores win |
| Two gods same archetype | Same cores OK; diversify defense/luxury only |
| Acorn on non-Rat | Gate: never |
| Asclepius on Zeus | Gate: never |

---

## Mental model (one sentence)

> **Filter the illegal shop, score what’s left by role + kit + ladder, fill a role archetype grid with ranked cores, repair structure (pen/openers), then sort by real spike order using high-SR timing as a soft teacher.**

That is the whole algorithm.
