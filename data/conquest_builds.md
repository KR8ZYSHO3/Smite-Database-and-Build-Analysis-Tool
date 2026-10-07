# SMITE 2 Conquest Builds — Statistically Weighted

Multi-phase Conquest algorithm (docs/BUILD_ALGORITHM.md): hard gates → role job → buy-order spikes → kit archetype slots → ladder/patch → soft high-SR inspiration → light flex diversify. God kit (effects/tags/scaling) + items:overall ladder + optional data/tracker_inspiration.json (nudge only). Hard bans: damage type, god-only items, healer cores, removed shop. Shop actives ≤2 (hard max 3). Damage roles ≥20 matching pen. Order is first-class: Mid Book/Deso + % pen before luxury Echo; Carry Tyrfing → Exec/OBow → Titan before crit; Jungle Jotunn → Crusher/pen → Titan before toys. Damage roles must hurt tanks early (pen/shred in first 3–4 items). Carry: native Carry only on base kit; off-role flex only via aspects that convert basics to ranged (e.g. Geb Calamity, Kali Unbound).

> Not scraped from websites. Derived from wiki item stats, ability scaling, and patch-note item/god momentum in `smite2.db`.

## Carry

Conquest duo ADC (backline): sustained basic-attack DPS, crit, penetration, and lifesteal. Support peels so you can free-hit.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| str | 20% |
| pen | 18% |
| as | 16% |
| crit | 14% |
| ls | 10% |
| bap | 8% |
| hp | 5% |
| int | 4% |
| cdr | 3% |
| pprot | 1% |
| mprot | 1% |

### Role job (not a full build)

This is the Carry job description + common items — not a complete build. Open a god below for a kit-specific 1 starter + 6 buy order (actives ≤2, hard max 3).

**Typical starter:** Gilded Arrow
**Priority stats:** str, pen, as, crit, ls
**Common role items (not ordered as a build):** Gluttonous Grimoire, Damaru, Omen Drum, The Cosmic Horror, Oath-Sworn Spear, Stygian Anchor, Wyrmskin Hide, Toxic Blade

### God-specific kit builds (use these)

#### Princess Bari — S-tier (role rank #1, model 74.9)

*Magical · Intelligence scaling (STR 82.0% / INT 112.3%)*

Princess Bari · Carry · archetype «ability_mage_adc» (INT / magical). Kit effects: big ult spike, pet / deployable, hard crowd control, ally buffs / auras, lots of CC, burst combos. Tags: burst, hard_cc, high_cc, long_cd, pet_zone, team_buff, ult_nuke. Style burst 70%/dps 30%; patch rising (net +2.9, r5 +2.9). Patch axes (r5): attack_speed +1.5, cooldown +0.7, damage +0.6. Scale STR 82% / INT 112%. Path: Book of Thoth (mana stack → power scaling); The Cosmic Horror (penetration required for damage role); Spear of Desolation (flat pen + CDR for ability burst; patch rising — lean damage). Pen: Book of Thoth, The Cosmic Horror, Spear of Desolation, The World Stone. Actives 0/2 · pen ≈ 30.

- **Starter:** Sands Of Time
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Book of Thoth (power, 2300g)
  2. The Cosmic Horror (pen, pen 10.0, 2650g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Totem of Death (power, 2800g)
  5. The World Stone (pen, pen 10.0, 2800g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Cupid — S-tier (role rank #2, model 68.8)

*Physical · Strength scaling (STR 116.6% / INT 86.4%)*

Cupid · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, attack-speed steroid, heavy healing, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, gap_close, hard_cc, heal, heavy_heal, long_cd, pet_zone, sustained. Style burst 43%/dps 57%; patch stable (net +0.7, r5 +0.2). Patch axes (r5): heal +0.1, general +0.1. Scale STR 117% / INT 86%. Path: Devourer's Gauntlet (lifesteal stacking); Odysseus' Bow (Carry path fit for kit profile); Tyrfing (Carry path fit for kit profile). Pen: Devourer's Gauntlet. Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Odysseus' Bow (power, 2450g)
  3. Tyrfing (power, 2400g)
  4. The Executioner (power, 2550g)
  5. Eye of the Storm (power, 2600g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Nut — S-tier (role rank #3, model 67.3)

*Magical · Intelligence scaling (STR 80.3% / INT 130.9%)*

Nut · Carry · archetype «ability_mage_adc» (INT / magical). Kit effects: big ult spike, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, echo, gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 76%/dps 24%; patch stable (net -0.2, r5 +0.0). Patch axes (r5): damage -0.2, general +0.0. Scale STR 80% / INT 131%. Path: Book of Thoth (mana stack → power scaling); The Cosmic Horror (penetration required for damage role); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, The Cosmic Horror, Spear of Desolation, Spear Of The Magus. Actives 0/2 · pen ≈ 30. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Sands Of Time
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Book of Thoth (power, 2300g)
  2. The Cosmic Horror (pen, pen 10.0, 2650g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Totem of Death (power, 2800g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Cernunnos — A-tier (role rank #4, model 66.3)

*Physical · Strength scaling (STR 80.4% / INT 51.1%)*

Cernunnos · Carry · archetype «crit_adc» (STR / physical). Kit effects: protection shred, big ult spike, basic-attack kit, self heal / drain, hard crowd control, dash / leap engage. Tags: aa, dot, gap_close, hard_cc, heal, high_cc, long_cd, prot_shred. Style burst 31%/dps 69%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): general +0.0, damage +0.0, cooldown +0.0. Scale STR 80% / INT 51%. Path: Tyrfing (Carry path fit for kit profile); Devourer's Gauntlet (lifesteal stacking); Qin's Blade (Carry path fit for kit profile). Pen: Devourer's Gauntlet. Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Tyrfing (power, 2400g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Qin's Blade (power, 2600g)
  4. Eye of the Storm (power, 2600g)
  5. Odysseus' Bow (power, 2450g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Hachiman — A-tier (role rank #5, model 60.9)

*Physical · Strength scaling (STR 58.7% / INT 0%)*

Hachiman · Carry · archetype «crit_adc» (STR / physical). Kit effects: basic-attack kit, attack-speed steroid, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit. Tags: aa, anti_cc, as_steroid, gap_close, hard_cc, long_cd, sustained, team_buff. Style burst 28%/dps 72%; patch rising (net +5.4, r5 +5.4). Patch axes (r5): damage +5.6, general -1.5, utility +1.4. Scale STR 59% / INT 0%. Path: Tyrfing (Carry path fit for kit profile); Devourer's Gauntlet (lifesteal stacking); Tekko-Kagi (penetration required for damage role). Pen: Devourer's Gauntlet, Tekko-Kagi. Actives 0/2 · pen ≈ 10. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 10.0):
  1. Tyrfing (power, 2400g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Tekko-Kagi (pen, pen 10.0, 2650g)
  4. The Executioner (power, 2550g)
  5. Odysseus' Bow (power, 2450g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Chronos — A-tier (role rank #6, model 59.6)

*Magical · Intelligence scaling (STR 0% / INT 67.2%)*

Chronos · Carry · archetype «ability_mage_adc» (INT / magical). Kit effects: hard crowd control, dash / leap engage, CC immunity in kit, sustained DPS, multi-hit / ticks, healing in kit. Tags: anti_cc, gap_close, hard_cc, heal, long_cd. Style burst 0%/dps 100%; patch rising (net +2.6, r5 +4.7). Patch axes (r5): damage +3.8, general +0.9. Scale STR 0% / INT 67%. Path: Book of Thoth (penetration required for damage role); Divine Ruin (Carry path fit for kit profile); The Cosmic Horror (penetration required for damage role). Pen: Book of Thoth, The Cosmic Horror, Spear of Desolation. Actives 0/2 · pen ≈ 20.

- **Starter:** Sands Of Time
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Divine Ruin (counter, 2500g)
  3. The Cosmic Horror (pen, pen 10.0, 2650g)
  4. Spear of Desolation (pen, pen 10.0, 2650g)
  5. Totem of Death (power, 2800g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (33.0), Aegis of Acceleration (28.0)

#### Danzaburou — A-tier (role rank #7, model 58.4)

*Physical · Hybrid scaling (STR 113.4% / INT 119.3%)*

Danzaburou · Carry · archetype «crit_adc» (STR / physical). Kit effects: channel / cast time, big ult spike, basic-attack kit, hard crowd control, CC immunity in kit, lots of CC. Tags: aa, anti_cc, burst, channel, dot, hard_cc, heal, high_cc. Style burst 72%/dps 28%; patch new (net +0.1, r5 +0.0). Patch axes (r5): general +0.1, heal +0.0, attack_speed -0.0. Scale STR 113% / INT 119%. Path: Devourer's Gauntlet (lifesteal stacking); Odysseus' Bow (Carry path fit for kit profile); Riptalon (attack speed / crit carry core). Pen: Devourer's Gauntlet, Riptalon. Actives 0/2 · pen ≈ 10. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 10.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Odysseus' Bow (power, 2450g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. Tyrfing (power, 2400g)
  5. Eye of the Storm (power, 2600g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Sol — B-tier (role rank #8, model 58.2)

*Magical · Intelligence scaling (STR 21.8% / INT 50.7%)*

Sol · Carry · archetype «dot_mage_adc» (INT / magical). Kit effects: damage over time, big ult spike, self heal / drain, ally buffs / auras, CC immunity in kit, lots of CC. Tags: anti_cc, burst, dot, heal, heavy_dot, high_cc, long_cd, self_sustain. Style burst 62%/dps 38%; patch stable (net -0.0, r5 +0.0). Patch axes (r5): damage -0.0, general -0.0, attack_speed -0.0. Scale STR 22% / INT 51%. Path: Book of Thoth (mana stack → power scaling); Divine Ruin (anti-heal + pen for healing/sustain kits); The Cosmic Horror (penetration required for damage role). Pen: Book of Thoth, The Cosmic Horror, Spear of Desolation, Spear Of The Magus. Actives 0/2 · pen ≈ 30. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Sands Of Time
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Book of Thoth (power, 2300g)
  2. Divine Ruin (counter, 2500g)
  3. The Cosmic Horror (pen, pen 10.0, 2650g)
  4. Spear of Desolation (pen, pen 10.0, 2650g)
  5. Spear Of The Magus (pen, pen 10.0, 2700g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Anhur — B-tier (role rank #9, model 55.8)

*Physical · Strength scaling (STR 121.5% / INT 0%)*

Anhur · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, basic-attack kit, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 49%/dps 51%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): damage +0.1, general +0.0, pen +0.0. Scale STR 121% / INT 0%. Path: Devourer's Gauntlet (lifesteal stacking); Tyrfing (Carry path fit for kit profile); Odysseus' Bow (Carry path fit for kit profile). Pen: Devourer's Gauntlet. Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Tyrfing (power, 2400g)
  3. Odysseus' Bow (power, 2450g)
  4. The Executioner (power, 2550g)
  5. Eye of the Storm (power, 2600g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Neith — B-tier (role rank #10, model 54.8)

*Physical · Hybrid scaling (STR 63.3% / INT 76.7%)*

Neith · Carry · archetype «crit_adc» (STR / physical). Kit effects: channel / cast time, big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, lots of CC. Tags: as_steroid, burst, channel, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 68%/dps 32%; patch stable (net -0.0, r5 +0.0). Patch axes (r5): damage +0.0. Scale STR 63% / INT 77%. Path: Tyrfing (Carry path fit for kit profile); Eye of the Storm (Carry path fit for kit profile); Tekko-Kagi (penetration required for damage role). Pen: Tekko-Kagi. Actives 0/2 · pen ≈ 10. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 10.0):
  1. Tyrfing (power, 2400g)
  2. Eye of the Storm (power, 2600g)
  3. Tekko-Kagi (pen, pen 10.0, 2650g)
  4. The Executioner (power, 2550g)
  5. Odysseus' Bow (power, 2450g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Hou Yi — B-tier (role rank #11, model 54.7)

*Physical · Strength scaling (STR 50.0% / INT 36.8%)*

Hou Yi · Carry · archetype «power_adc» (STR / physical). Kit effects: big ult spike, hard crowd control, dash / leap engage, lots of CC, long cooldowns. Tags: gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 49%/dps 51%; patch stable (net -0.3, r5 +0.0). Patch axes (r5): general -0.2, cooldown -0.2, survivability +0.0. Scale STR 50% / INT 37%. Path: Tyrfing (Carry path fit for kit profile); Devourer's Gauntlet (lifesteal stacking); Odysseus' Bow (Carry path fit for kit profile). Pen: Devourer's Gauntlet, Pendulum Blade. Actives 1/2 · pen ≈ 10. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 10.0):
  1. Tyrfing (power, 2400g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Odysseus' Bow (power, 2450g)
  4. The Executioner (power, 2550g)
  5. Pendulum Blade (pen, active, pen 10.0, 2750g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Ishtar — B-tier (role rank #12, model 53.8)

*Physical · Strength scaling (STR 52.4% / INT 0%)*

Ishtar · Carry · archetype «crit_adc» (STR / physical). Kit effects: attack-speed steroid, execute / threshold, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, as_steroid, execute, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 1%/dps 99%; patch new (net +0.5, r5 +0.0). Patch axes (r5): survivability +0.5, damage -0.3, general +0.3. Scale STR 52% / INT 0%. Path: Tyrfing (Carry path fit for kit profile); Odysseus' Bow (Carry path fit for kit profile); Devourer's Gauntlet (lifesteal stacking). Pen: Devourer's Gauntlet. Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Tyrfing (power, 2400g)
  2. Odysseus' Bow (power, 2450g)
  3. Devourer's Gauntlet (power, 2500g)
  4. The Executioner (power, 2550g)
  5. Eye of the Storm (power, 2600g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Medusa — B-tier (role rank #13, model 53.0)

*Physical · Hybrid scaling (STR 64.2% / INT 63.9%)*

Medusa · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, as_steroid, burst, dot, gap_close, hard_cc, heal, long_cd. Style burst 76%/dps 24%; patch stable (net +0.6, r5 +0.0). Patch axes (r5): damage +0.2, cooldown +0.2, survivability +0.1. Scale STR 64% / INT 64%. Path: Tyrfing (Carry path fit for kit profile); Devourer's Gauntlet (lifesteal stacking); Odysseus' Bow (Carry path fit for kit profile). Pen: Devourer's Gauntlet. Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Tyrfing (power, 2400g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Odysseus' Bow (power, 2450g)
  4. The Executioner (power, 2550g)
  5. Eye of the Storm (power, 2600g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Xbalanque — C-tier (role rank #14, model 51.8)

*Physical · Strength scaling (STR 36.9% / INT 34.2%)*

Xbalanque · Carry · archetype «power_adc» (STR / physical). Kit effects: damage over time, dash / leap engage, CC immunity in kit, multi-hit / ticks, sustained DPS, zones / linger. Tags: anti_cc, dot, gap_close, heal, heavy_dot, long_cd, sustained, zone. Style burst 29%/dps 71%; patch stable (net +0.9, r5 +0.0). Patch axes (r5): damage +0.9, utility +0.0, attack_speed +0.0. Scale STR 37% / INT 34%. Path: Tyrfing (Carry path fit for kit profile); Transcendence (mana stack → power scaling); Odysseus' Bow (Carry path fit for kit profile). Pen: Transcendence, Pendulum Blade. Actives 1/2 · pen ≈ 10. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 10.0):
  1. Tyrfing (power, 2400g)
  2. Transcendence (power, 2400g)
  3. Odysseus' Bow (power, 2450g)
  4. The Executioner (power, 2550g)
  5. Pendulum Blade (pen, active, pen 10.0, 2750g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Apollo — C-tier (role rank #15, model 47.0)

*Physical · Strength scaling (STR 74.1% / INT 0%)*

Apollo · Carry · archetype «crit_adc» (STR / physical). Kit effects: basic-attack kit, attack-speed steroid, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit. Tags: aa, anti_cc, as_steroid, gap_close, hard_cc, long_cd, sustained, team_buff. Style burst 14%/dps 86%; patch volatile (net +0.6, r5 +0.6). Patch axes (r5): survivability +0.6. Scale STR 74% / INT 0%. Path: Tyrfing (Carry path fit for kit profile); Devourer's Gauntlet (lifesteal stacking); Tekko-Kagi (penetration required for damage role). Pen: Devourer's Gauntlet, Tekko-Kagi. Actives 1/2 · pen ≈ 10. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 10.0):
  1. Tyrfing (power, 2400g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Tekko-Kagi (pen, pen 10.0, 2650g)
  4. Qin's Blade (power, 2600g)
  5. Bloodforge (power, active, 2550g)
  6. Odysseus' Bow (power, 2450g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Jing Wei — C-tier (role rank #16, model 45.0)

*Physical · Strength scaling (STR 87.0% / INT 0%)*

Jing Wei · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, attack-speed steroid, pet / deployable, dash / leap engage, CC immunity in kit, high mobility. Tags: anti_cc, as_steroid, dot, gap_close, long_cd, mobile, pet_zone, sustained. Style burst 33%/dps 67%; patch stable (net -0.3, r5 +0.0). Patch axes (r5): general -0.3, damage -0.0, utility +0.0. Scale STR 87% / INT 0%. Path: Tyrfing (Carry path fit for kit profile); Qin's Blade (Carry path fit for kit profile); Eye of the Storm (Carry path fit for kit profile). Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Tyrfing (power, 2400g)
  2. Qin's Blade (power, 2600g)
  3. Eye of the Storm (power, 2600g)
  4. The Executioner (power, 2550g)
  5. Odysseus' Bow (power, 2450g)
  6. Demon Blade (power, 2750g)
- **Relics:** Purification Beads (33.0), Aegis of Acceleration (28.0)

#### Chiron — C-tier (role rank #17, model 44.4)

*Physical · Strength scaling (STR 99.9% / INT 0%)*

Chiron · Carry · archetype «power_adc» (STR / physical). Kit effects: protection shred, channel / cast time, big ult spike, pet / deployable, dash / leap engage, ally buffs / auras. Tags: burst, channel, dot, gap_close, heal, high_cc, long_cd, pet_zone. Style burst 71%/dps 29%; patch new (net +0.2, r5 +0.0). Patch axes (r5): general +0.2, utility +0.0. Scale STR 100% / INT 0%. Path: Devourer's Gauntlet (lifesteal stacking); Tyrfing (Carry path fit for kit profile); Pendulum Blade (penetration required for damage role). Pen: Devourer's Gauntlet, Pendulum Blade. Actives 1/2 · pen ≈ 10. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 10.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Tyrfing (power, 2400g)
  3. Pendulum Blade (pen, active, pen 10.0, 2750g)
  4. The Executioner (power, 2550g)
  5. Odysseus' Bow (power, 2450g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Rama — C-tier (role rank #18, model 41.3)

*Physical · Strength scaling (STR 64.6% / INT 0%)*

Rama · Carry · archetype «crit_adc» (STR / physical). Kit effects: attack-speed steroid, hard crowd control, sustained DPS, multi-hit / ticks, long cooldowns. Tags: as_steroid, hard_cc, long_cd, sustained. Style burst 0%/dps 100%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): general +0.1, survivability -0.0, attack_speed +0.0. Scale STR 65% / INT 0%. Path: Tyrfing (Carry path fit for kit profile); Odysseus' Bow (Carry path fit for kit profile); Riptalon (attack speed / crit carry core). Pen: Riptalon. Actives 0/2 · pen ≈ 10. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 10.0):
  1. Tyrfing (power, 2400g)
  2. Odysseus' Bow (power, 2450g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. Avenging Blade (power, 2650g)
  5. Eye of the Storm (power, 2600g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Izanami — D-tier (role rank #19, model 41.3)

*Physical · Hybrid scaling (STR 92.9% / INT 84.5%)*

Izanami · Carry · archetype «crit_adc» (STR / physical). Kit effects: protection shred, big ult spike, attack-speed steroid, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, dot, gap_close, hard_cc, heal, long_cd, pet_zone, prot_shred. Style burst 36%/dps 64%; patch falling (net -3.3, r5 -3.2). Patch axes (r5): attack_speed -2.4, utility -0.9. Scale STR 93% / INT 84%. Path: Tyrfing (Carry path fit for kit profile); Devourer's Gauntlet (lifesteal stacking); Qin's Blade (Carry path fit for kit profile). Pen: Devourer's Gauntlet. Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Tyrfing (power, 2400g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Qin's Blade (power, 2600g)
  4. Eye of the Storm (power, 2600g)
  5. Odysseus' Bow (power, 2450g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Ullr — D-tier (role rank #20, model 39.8)

*Physical · Strength scaling (STR 75.8% / INT 0%)*

Ullr · Carry · archetype «crit_adc» (STR / physical). Kit effects: attack-speed steroid, self heal / drain, pet / deployable, hard crowd control, dash / leap engage, sustained DPS. Tags: as_steroid, gap_close, hard_cc, heal, high_cc, pet_zone, self_sustain, sustained. Style burst 2%/dps 98%; patch stable (net -0.0, r5 +0.0). Patch axes (r5): general -0.0, attack_speed +0.0, cooldown +0.0. Scale STR 76% / INT 0%. Path: Tyrfing (Carry path fit for kit profile); Qin's Blade (Carry path fit for kit profile); Eye of the Storm (Carry path fit for kit profile). Pen: Tekko-Kagi. Actives 0/2 · pen ≈ 10. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 10.0):
  1. Tyrfing (power, 2400g)
  2. Qin's Blade (power, 2600g)
  3. Eye of the Storm (power, 2600g)
  4. Tekko-Kagi (pen, pen 10.0, 2650g)
  5. Odysseus' Bow (power, 2450g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Artemis — D-tier (role rank #22, model 24.4)

*Physical · Strength scaling (STR 67.1% / INT 0%)*

Artemis · Carry · archetype «crit_adc» (STR / physical). Kit effects: basic-attack kit, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: aa, anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 11%/dps 89%; patch falling (net -3.4, r5 -3.2). Patch axes (r5): utility -1.4, cooldown -0.9, attack_speed -0.9. Scale STR 67% / INT 0%. Path: Tyrfing (Carry path fit for kit profile); Eye of the Storm (Carry path fit for kit profile); Tekko-Kagi (penetration required for damage role). Pen: Tekko-Kagi. Actives 0/2 · pen ≈ 10. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 10.0):
  1. Tyrfing (power, 2400g)
  2. Eye of the Storm (power, 2600g)
  3. Tekko-Kagi (pen, pen 10.0, 2650g)
  4. The Executioner (power, 2550g)
  5. Odysseus' Bow (power, 2450g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Geb — ?-tier (role rank #9000, model None)

*Magical · Intelligence scaling (STR 0% / INT 36.3%)*

Geb · Carry · archetype «aa_mage» (INT / magical). ASPECT «Aspect of Calamity». Geb's attacks are ranged, travel slowly, and pierce with damage falloff. Shockwave deals circular damage, Crits, triggers on-hits, and grant Kit effects: basic-attack kit, attack-speed steroid, self heal / drain, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, as_steroid, burst, dot, gap_close, hard_cc, heal. Style burst 40%/dps 75%; patch stable (net -0.8, r5 +0.0). Patch axes (r5): damage -0.4, survivability -0.3, crit -0.1. Scale STR 0% / INT 36%. Path: Book of Thoth (mana stack → power scaling); The Cosmic Horror (penetration required for damage role); Chronos' Pendant (CDR core for spam / channel kits). Pen: Book of Thoth, The Cosmic Horror, Spear of Desolation. Actives 0/2 · pen ≈ 20.

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. The Cosmic Horror (pen, pen 10.0, 2650g)
  3. Chronos' Pendant (power, 2400g)
  4. Divine Ruin (counter, 2500g)
  5. Spear of Desolation (pen, pen 10.0, 2650g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Kali — ?-tier (role rank #9000, model None)

*Physical · Strength scaling (STR 54.5% / INT 17.1%)*

Kali · Carry · archetype «crit_adc» (STR / physical). ASPECT «Aspect of Unbound Destruction». Kali's Basics are ranged. Rupture procs at 5 stacks to deal damage & heal her. Incense doesn't stun or proc Rupture but knocks back & applie Kit effects: protection shred, basic-attack kit, attack-speed steroid, self heal / drain, heavy healing, execute / threshold. Tags: aa, anti_cc, as_steroid, burst, execute, gap_close, hard_cc, heal. Style burst 40%/dps 85%; patch volatile (net -2.9, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 54% / INT 17%. Path: Devourer's Gauntlet (lifesteal stacking); Tyrfing (Carry path fit for kit profile); The Reaper (penetration required for damage role). Pen: Devourer's Gauntlet, The Reaper, Riptalon. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Tyrfing (power, 2400g)
  3. The Reaper (pen, pen 10.0, 2600g)
  4. Odysseus' Bow (power, 2450g)
  5. Riptalon (pen, pen 10.0, 2700g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Tsukuyomi — ?-tier (role rank #9000, model None)

*Physical · Strength scaling (STR 157.1% / INT 112.5%)*

Tsukuyomi · Carry · archetype «crit_adc» (STR / physical). ASPECT «Aspect of Mangetsu». When gaining Shingetsu Ranged Attack, they become Mangetsu Ranged Attacks instead. Dark Moon Shuriken no longer sticks to gods. Piercing Moo Kit effects: big ult spike, basic-attack kit, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, as_steroid, burst, gap_close, hard_cc, heal, long_cd. Style burst 40%/dps 75%; patch stable (net -0.2, r5 +0.0). Patch axes (r5): damage -0.2, general +0.0, utility +0.0. Scale STR 157% / INT 112%. Path: Devourer's Gauntlet (lifesteal stacking); Tyrfing (Carry path fit for kit profile); Qin's Blade (Carry path fit for kit profile). Pen: Devourer's Gauntlet, Tekko-Kagi. Actives 0/2 · pen ≈ 10. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Gilded Arrow
- **Buy order** (actives 0/2, pen ≈ 10.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Tyrfing (power, 2400g)
  3. Qin's Blade (power, 2600g)
  4. Tekko-Kagi (pen, pen 10.0, 2650g)
  5. Odysseus' Bow (power, 2450g)
  6. Demon Blade (power, 2750g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

---

## Mid

Conquest mid (backline): ability burst, wave clear, INT power, penetration, CDR. Support peels so you can unload combos.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| int | 24% |
| pen | 22% |
| cdr | 14% |
| mp | 8% |
| hp | 7% |
| str | 6% |
| mpr | 5% |
| ls | 5% |
| as | 3% |
| pprot | 2% |
| mprot | 2% |

### Role job (not a full build)

This is the Mid job description + common items — not a complete build. Open a god below for a kit-specific 1 starter + 6 buy order (actives ≤2, hard max 3).

**Typical starter:** Conduit Gem
**Priority stats:** int, pen, cdr, mp, hp
**Common role items (not ordered as a build):** The Cosmic Horror, Gluttonous Grimoire, Damaru, Omen Drum, Helm of Darkness, Brawler’s Beat Stick, Stygian Anchor, Totem of Death

### God-specific kit builds (use these)

#### Princess Bari — S-tier (role rank #1, model 74.9)

*Magical · Intelligence scaling (STR 82.0% / INT 112.3%)*

Princess Bari · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, pet / deployable, hard crowd control, ally buffs / auras, lots of CC, burst combos. Tags: burst, hard_cc, high_cc, long_cd, pet_zone, team_buff, ult_nuke. Style burst 70%/dps 30%; patch rising (net +2.9, r5 +2.9). Patch axes (r5): attack_speed +1.5, cooldown +0.7, damage +0.6. Scale STR 82% / INT 112%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst; patch rising — lean damage). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Divine Ruin (counter, 2500g)
  6. Totem of Death (power, 2800g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Nut — S-tier (role rank #2, model 67.3)

*Magical · Intelligence scaling (STR 80.3% / INT 130.9%)*

Nut · Mid · archetype «burst_mage» (INT / magical). Kit effects: big ult spike, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, echo, gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 76%/dps 24%; patch stable (net -0.2, r5 +0.0). Patch axes (r5): damage -0.2, general +0.0. Scale STR 80% / INT 131%. Path: Spear Of The Magus (multi-hit / shred — stacks Magus passive); Spear of Desolation (flat pen + CDR for ability burst); Book of Thoth (mana stack → power scaling). Pen: Spear Of The Magus, Spear of Desolation, Book of Thoth, The Cosmic Horror. Actives 0/2 · pen ≈ 30. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Spear Of The Magus (pen, pen 10.0, 2700g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. Book of Thoth (power, 2300g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Divine Ruin (counter, 2500g)
  6. Totem of Death (power, 2800g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Scylla — S-tier (role rank #3, model 67.1)

*Magical · Intelligence scaling (STR 0% / INT 94.2%)*

Scylla · Mid · archetype «zone_mage» (INT / magical). Kit effects: protection shred, big ult spike, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, burst, gap_close, hard_cc, long_cd, pet_zone, prot_shred, ult_nuke. Style burst 66%/dps 34%; patch new (net +0.9, r5 +0.0). Patch axes (r5): general +0.5, damage +0.4, survivability -0.0. Scale STR 0% / INT 94%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst; damage buffed — power/pen). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror, Rod of Tahuti. Actives 0/2 · pen ≈ 25. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Rod of Tahuti (power, pen 5.0, 3000g)
  6. Gem of Isolation (mitigate, 2450g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Ah Puch — S-tier (role rank #4, model 62.6)

*Magical · Intelligence scaling (STR 0% / INT 53.0%)*

Ah Puch · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, heavy healing, hard crowd control, low mobility, multi-hit / ticks, burst combos. Tags: burst, dot, hard_cc, heal, heavy_dot, heavy_heal, immobile, long_cd. Style burst 55%/dps 45%; patch rising (net +2.1, r5 +3.1). Patch axes (r5): damage +2.1, heal +1.0, general +0.0. Scale STR 0% / INT 53%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst; patch rising — lean damage). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Ethereal Staff (mitigate, 2550g)
  6. Totem of Death (power, 2800g)
- **Relics:** Aegis of Acceleration (40.0), Purification Beads (38.0)

#### Chronos — A-tier (role rank #5, model 59.6)

*Magical · Intelligence scaling (STR 0% / INT 67.2%)*

Chronos · Mid · archetype «burst_mage» (INT / magical). Kit effects: hard crowd control, dash / leap engage, CC immunity in kit, sustained DPS, multi-hit / ticks, healing in kit. Tags: anti_cc, gap_close, hard_cc, heal, long_cd. Style burst 0%/dps 100%; patch rising (net +2.6, r5 +4.7). Patch axes (r5): damage +3.8, general +0.9. Scale STR 0% / INT 67%. Path: Book of Thoth (penetration required for damage role); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst; patch rising — lean damage). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Divine Ruin (counter, 2500g)
  6. Totem of Death (power, 2800g)
- **Relics:** Aegis of Acceleration (30.0), Purification Beads (30.0)

#### Sol — A-tier (role rank #6, model 58.2)

*Magical · Intelligence scaling (STR 21.8% / INT 50.7%)*

Sol · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, big ult spike, self heal / drain, ally buffs / auras, CC immunity in kit, lots of CC. Tags: anti_cc, burst, dot, heal, heavy_dot, high_cc, long_cd, self_sustain. Style burst 62%/dps 38%; patch stable (net -0.0, r5 +0.0). Patch axes (r5): damage -0.0, general -0.0, attack_speed -0.0. Scale STR 22% / INT 51%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror, Rod of Tahuti. Actives 0/2 · pen ≈ 25. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Divine Ruin (counter, 2500g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Eset — A-tier (role rank #7, model 58.0)

*Magical · Intelligence scaling (STR 0% / INT 52.7%)*

Eset · Mid · archetype «channel_mage» (INT / magical). Kit effects: channel / cast time, hard crowd control, ally buffs / auras, lots of CC, multi-hit / ticks, burst combos. Tags: burst, channel, hard_cc, heal, high_cc, long_cd, shield, team_buff. Style burst 86%/dps 14%; patch stable (net +0.5, r5 +0.1). Patch axes (r5): damage +0.1, survivability +0.1. Scale STR 0% / INT 53%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Divine Ruin (counter, 2500g)
  6. Totem of Death (power, 2800g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Discordia — A-tier (role rank #8, model 55.8)

*Magical · Intelligence scaling (STR 0% / INT 118.8%)*

Discordia · Mid · archetype «sustain_mage» (INT / magical). Kit effects: big ult spike, self heal / drain, hard crowd control, dash / leap engage, ally buffs / auras, burst combos. Tags: burst, gap_close, hard_cc, heal, long_cd, self_sustain, team_buff, ult_nuke. Style burst 70%/dps 30%; patch stable (net -0.3, r5 +0.0). Patch axes (r5): utility -0.6, cooldown +0.4, damage -0.2. Scale STR 0% / INT 119%. Path: Spear Of The Magus (multi-hit / shred — stacks Magus passive); Book of Thoth (mana stack → power scaling); Spear of Desolation (flat pen + CDR for ability burst). Pen: Spear Of The Magus, Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 30. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Spear Of The Magus (pen, pen 10.0, 2700g)
  2. Book of Thoth (power, 2300g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Typhon’s Heart (power, 2600g)
  6. Totem of Death (power, 2800g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Neith — A-tier (role rank #9, model 54.8)

*Physical · Hybrid scaling (STR 63.3% / INT 76.7%)*

Neith · Mid · archetype «channel_mage» (STR / physical). Kit effects: channel / cast time, big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, lots of CC. Tags: as_steroid, burst, channel, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 68%/dps 32%; patch stable (net -0.0, r5 +0.0). Patch axes (r5): damage +0.0. Scale STR 63% / INT 77%. Path: Transcendence (mana stack → power scaling); The Crusher (penetration required for damage role); Heartseeker (stacking pen power for assassins). Pen: Transcendence, The Crusher, Heartseeker, Jotunn's Revenge. Actives 2/2 · pen ≈ 25.

- **Starter:** Bluestone Pendant
- **Buy order** (actives 2/2, pen ≈ 25.0):
  1. Transcendence (power, 2400g)
  2. The Crusher (pen, pen 10.0, 2750g)
  3. Heartseeker (pen, pen 10.0, 3000g)
  4. Jotunn's Revenge (power, pen 5.0, 2400g)
  5. Bloodforge (power, active, 2550g)
  6. Arondight (power, active, 2550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Baron Samedi — B-tier (role rank #10, model 53.8)

*Magical · Intelligence scaling (STR 0% / INT 69.6%)*

Baron Samedi · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, channel / cast time, execute / threshold, pet / deployable, hard crowd control, ally buffs / auras. Tags: burst, channel, dot, execute, hard_cc, heal, heavy_dot, high_cc. Style burst 72%/dps 28%; patch volatile (net +1.1, r5 +0.7). Patch axes (r5): general +0.7. Scale STR 0% / INT 70%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 1/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Divine Ruin (counter, 2500g)
  6. Helm of Darkness (defense, active, 2700g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Ix Chel — B-tier (role rank #11, model 50.5)

*Magical · Intelligence scaling (STR 0% / INT 64.4%)*

Ix Chel · Mid · archetype «channel_mage» (INT / magical). Kit effects: channel / cast time, self heal / drain, heavy healing, pet / deployable, hard crowd control, ally buffs / auras. Tags: anti_cc, channel, dot, echo, hard_cc, heal, heavy_heal, high_cc. Style burst 49%/dps 51%; patch new (net -0.7, r5 -0.7). Patch axes (r5): damage -0.8, general +0.8, cooldown -0.7. Scale STR 0% / INT 64%. Path: Book of Thoth (mana stack → power scaling); Spear of Desolation (flat pen + CDR for ability burst); The Cosmic Horror (penetration required for damage role). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. The Cosmic Horror (pen, pen 10.0, 2650g)
  4. Divine Ruin (counter, 2500g)
  5. Gem of Isolation (mitigate, 2450g)
  6. Stygian Anchor (counter, 2550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Vulcan — B-tier (role rank #12, model 50.4)

*Magical · Intelligence scaling (STR 0% / INT 85.8%)*

Vulcan · Mid · archetype «burst_mage» (INT / magical). Kit effects: protection shred, big ult spike, dash / leap engage, multi-hit / ticks, burst combos, long cooldowns. Tags: burst, gap_close, long_cd, prot_shred, ult_nuke. Style burst 63%/dps 37%; patch stable (net -0.0, r5 +0.0). Patch axes (r5): damage -0.0, cooldown -0.0, general +0.0. Scale STR 0% / INT 86%. Path: Spear Of The Magus (multi-hit / shred — stacks Magus passive); Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits). Pen: Spear Of The Magus, Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 30. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Spear Of The Magus (pen, pen 10.0, 2700g)
  2. Book of Thoth (power, 2300g)
  3. Chronos' Pendant (power, 2400g)
  4. Spear of Desolation (pen, pen 10.0, 2650g)
  5. The Cosmic Horror (pen, pen 10.0, 2650g)
  6. Totem of Death (power, 2800g)
- **Relics:** Aegis of Acceleration (30.0), Purification Beads (30.0)

#### The Morrigan — B-tier (role rank #13, model 49.1)

*Magical · Intelligence scaling (STR 0% / INT 143.5%)*

The Morrigan · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, pet / deployable, hard crowd control, damage over time, long cooldowns, zones / linger. Tags: dot, hard_cc, long_cd, pet_zone, ult_nuke. Style burst 50%/dps 50%; patch stable (net -0.0, r5 +0.0). Patch axes (r5): general -0.0, utility +0.0, cooldown +0.0. Scale STR 0% / INT 143%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror, Rod of Tahuti. Actives 0/2 · pen ≈ 25. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Soul Reaver (power, 2950g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (30.0), Aegis of Acceleration (30.0)

#### Kukulkan — B-tier (role rank #14, model 47.5)

*Magical · Intelligence scaling (STR 0% / INT 85.4%)*

Kukulkan · Mid · archetype «mana_mage» (INT / magical). Kit effects: big ult spike, mana → power passive, pet / deployable, dash / leap engage, CC immunity in kit, lots of CC. Tags: anti_cc, burst, dot, gap_close, high_cc, long_cd, mana_stack, pet_zone. Style burst 66%/dps 34%; patch stable (net +0.7, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 0% / INT 85%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); The Cosmic Horror (penetration required for damage role). Pen: Book of Thoth, The Cosmic Horror, Rod of Tahuti, Spear of Desolation. Actives 0/2 · pen ≈ 25. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. The Cosmic Horror (pen, pen 10.0, 2650g)
  4. Rod of Tahuti (power, pen 5.0, 3000g)
  5. Spear of Desolation (pen, pen 10.0, 2650g)
  6. Gem of Isolation (mitigate, 2450g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Janus — B-tier (role rank #15, model 46.9)

*Magical · Intelligence scaling (STR 0% / INT 92.6%)*

Janus · Mid · archetype «burst_mage» (INT / magical). Kit effects: big ult spike, execute / threshold, ally buffs / auras, CC immunity in kit, multi-hit / ticks, burst combos. Tags: anti_cc, burst, execute, long_cd, team_buff, ult_nuke. Style burst 64%/dps 36%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): mana -0.1, damage +0.1, utility -0.0. Scale STR 0% / INT 93%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Divine Ruin (counter, 2500g)
  6. Totem of Death (power, 2800g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Poseidon — B-tier (role rank #16, model 44.8)

*Magical · Intelligence scaling (STR 0% / INT 111.2%)*

Poseidon · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, attack-speed steroid, pet / deployable, hard crowd control, burst combos, lots of CC. Tags: as_steroid, burst, dot, hard_cc, high_cc, long_cd, pet_zone, ult_nuke. Style burst 92%/dps 8%; patch volatile (net +1.3, r5 +0.7). Patch axes (r5): general +0.7. Scale STR 0% / INT 111%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Divine Ruin (counter, 2500g)
  6. Polynomicon (power, 2450g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Nu Wa — C-tier (role rank #17, model 43.4)

*Magical · Intelligence scaling (STR 0% / INT 78.2%)*

Nu Wa · Mid · archetype «zone_mage» (INT / magical). Kit effects: protection shred, big ult spike, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, burst, dot, gap_close, hard_cc, long_cd, pet_zone, prot_shred. Style burst 59%/dps 41%; patch volatile (net -2.1, r5 +0.0). Patch axes (r5): damage -2.3, survivability -1.7, attack_speed +1.1. Scale STR 0% / INT 78%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Soul Reaver (power, 2950g)
  6. Divine Ruin (counter, 2500g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Hel — C-tier (role rank #18, model 42.3)

*Magical · Intelligence scaling (STR 0% / INT 74.6%)*

Hel · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, attack-speed steroid, self heal / drain, ally buffs / auras, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, as_steroid, dot, heal, heavy_dot, self_sustain, team_buff. Style burst 42%/dps 58%; patch new (net +0.9, r5 +0.9). Patch axes (r5): general +0.9. Scale STR 0% / INT 75%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst; patch rising — lean damage). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Gem of Isolation (mitigate, 2450g)
  6. Totem of Death (power, 2800g)
- **Relics:** Aegis of Acceleration (30.0), Purification Beads (30.0)

#### Merlin — C-tier (role rank #19, model 38.2)

*Magical · Intelligence scaling (STR 0% / INT 47.4%)*

Merlin · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, channel / cast time, pet / deployable, dash / leap engage, lots of CC, multi-hit / ticks. Tags: channel, dot, gap_close, heal, heavy_dot, high_cc, pet_zone, zone. Style burst 46%/dps 54%; patch stable (net +0.6, r5 +0.0). Patch axes (r5): cooldown +0.6, general +0.0, damage -0.0. Scale STR 0% / INT 47%. Path: Book of Thoth (mana stack → power scaling); Spear of Desolation (flat pen + CDR for ability burst); The Cosmic Horror (penetration required for damage role). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror, Dreamer's Idol. Actives 1/2 · pen ≈ 30. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 30.0):
  1. Book of Thoth (power, 2300g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. The Cosmic Horror (pen, pen 10.0, 2650g)
  4. Gem of Isolation (mitigate, 2450g)
  5. Breastplate of Valor (defense, 2400g)
  6. Dreamer's Idol (pen, active, pen 10.0, 3500g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Hecate — C-tier (role rank #20, model 37.6)

*Magical · Intelligence scaling (STR 0% / INT 70.3%)*

Hecate · Mid · archetype «channel_mage» (INT / magical). Kit effects: channel / cast time, hard crowd control, dash / leap engage, ally buffs / auras, burst combos, shields. Tags: burst, channel, gap_close, hard_cc, heal, long_cd, shield, team_buff. Style burst 58%/dps 42%; patch falling (net -2.5, r5 -1.8). Patch axes (r5): damage -1.8. Scale STR 0% / INT 70%. Path: Book of Thoth (mana stack → power scaling); Spear Of The Magus (multi-hit / shred — stacks Magus passive); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear Of The Magus, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 30. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Book of Thoth (power, 2300g)
  2. Spear Of The Magus (pen, pen 10.0, 2700g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Chronos' Pendant (power, 2400g)
  5. The Cosmic Horror (pen, pen 10.0, 2650g)
  6. Totem of Death (power, 2800g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Morgan Le Fay — C-tier (role rank #21, model 36.4)

*Magical · Intelligence scaling (STR 0% / INT 76.5%)*

Morgan Le Fay · Mid · archetype «zone_mage» (INT / magical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit, multi-hit / ticks, burst combos. Tags: anti_cc, burst, dot, gap_close, hard_cc, heal, long_cd, pet_zone. Style burst 65%/dps 35%; patch falling (net -2.1, r5 -0.9). Patch axes (r5): damage -0.9. Scale STR 0% / INT 76%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror, Dreamer's Idol. Actives 1/2 · pen ≈ 30. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 30.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Soul Reaver (power, 2950g)
  6. Dreamer's Idol (pen, active, pen 10.0, 3500g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Aphrodite — C-tier (role rank #22, model 33.4)

*Magical · Intelligence scaling (STR 0% / INT 57.9%)*

Aphrodite · Mid · archetype «burst_mage» (INT / magical). Kit effects: big ult spike, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, burst, dot, gap_close, hard_cc, heal, long_cd, team_buff. Style burst 60%/dps 40%; patch falling (net -5.7, r5 -6.1). Patch axes (r5): damage -3.4, general -1.4, survivability -0.9. Scale STR 0% / INT 58%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Divine Ruin (counter, 2500g)
  6. Totem of Death (power, 2800g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Zeus — D-tier (role rank #23, model 31.9)

*Magical · Intelligence scaling (STR 0% / INT 62.1%)*

Zeus · Mid · archetype «burst_mage» (INT / magical). Kit effects: attack-speed steroid, hard crowd control, long cooldowns, burst combos. Tags: as_steroid, hard_cc, long_cd. Style burst 59%/dps 41%; patch volatile (net -1.1, r5 +0.0). Patch axes (r5): utility -0.7, damage -0.5, general +0.0. Scale STR 0% / INT 62%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror, Rod of Tahuti. Actives 0/2 · pen ≈ 25. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Rod of Tahuti (power, pen 5.0, 3000g)
  6. Totem of Death (power, 2800g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Ra — D-tier (role rank #24, model 31.5)

*Magical · Intelligence scaling (STR 0% / INT 106.2%)*

Ra · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, pet / deployable, ally buffs / auras, multi-hit / ticks, burst combos, damage over time. Tags: burst, dot, heal, long_cd, pet_zone, team_buff, ult_nuke. Style burst 70%/dps 30%; patch falling (net -2.8, r5 -2.8). Patch axes (r5): damage -2.5, general -0.4, heal +0.1. Scale STR 0% / INT 106%. Path: Book of Thoth (mana stack → power scaling); Spear of Desolation (flat pen + CDR for ability burst); The Cosmic Horror (penetration required for damage role). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. The Cosmic Horror (pen, pen 10.0, 2650g)
  4. Soul Reaver (power, 2950g)
  5. Divine Ruin (counter, 2500g)
  6. Polynomicon (power, 2450g)
- **Relics:** Purification Beads (30.0), Aegis of Acceleration (30.0)

#### Anubis — D-tier (role rank #25, model 31.4)

*Magical · Intelligence scaling (STR 0% / INT 59.8%)*

Anubis · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, channel / cast time, big ult spike, self heal / drain, pet / deployable, hard crowd control. Tags: anti_cc, channel, dot, hard_cc, heal, heavy_dot, high_cc, immobile. Style burst 98%/dps 2%; patch volatile (net -2.3, r5 +0.0). Patch axes (r5): survivability -1.0, damage -0.8, heal -0.5. Scale STR 0% / INT 60%. Path: Book of Thoth (mana stack → power scaling); Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror. Actives 0/2 · pen ≈ 20. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Book of Thoth (power, 2300g)
  2. Chronos' Pendant (power, 2400g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Typhon’s Heart (power, 2600g)
  6. Magi's Cloak (defense, 2400g)
- **Relics:** Aegis of Acceleration (40.0), Purification Beads (38.0)

#### Agni — D-tier (role rank #26, model 25.9)

*Magical · Intelligence scaling (STR 0% / INT 54.1%)*

Agni · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, pet / deployable, hard crowd control, dash / leap engage, multi-hit / ticks, healing in kit. Tags: dot, gap_close, hard_cc, heal, heavy_dot, long_cd, pet_zone. Style burst 0%/dps 0%; patch falling (net -2.5, r5 -2.0). Patch axes (r5): cooldown -1.1, utility -0.9. Scale STR 0% / INT 54%. Path: Book of Thoth (mana stack → power scaling); Spear of Desolation (flat pen + CDR for ability burst); The Cosmic Horror (penetration required for damage role). Pen: Book of Thoth, Spear of Desolation, The Cosmic Horror, Rod of Tahuti. Actives 0/2 · pen ≈ 25. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Book of Thoth (power, 2300g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. The Cosmic Horror (pen, pen 10.0, 2650g)
  4. Rod of Tahuti (power, pen 5.0, 3000g)
  5. Gem of Isolation (mitigate, 2450g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

---

## Jungle

Conquest jungle — ganks first: Bumba clear, Jotunn/Hydra (or stack) openers, then power + pen. Not a Solo shell — Shifter/BoV mid is wrong for most junglers.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| pen | 24% |
| cdr | 18% |
| str | 16% |
| int | 13% |
| hp | 8% |
| as | 8% |
| ls | 6% |
| crit | 3% |
| pprot | 2% |
| mprot | 2% |

### Role job (not a full build)

This is the Jungle job description + common items — not a complete build. Open a god below for a kit-specific 1 starter + 6 buy order (actives ≤2, hard max 3).

**Typical starter:** Bumba's Cudgel
**Priority stats:** pen, cdr, str, int, hp
**Common role items (not ordered as a build):** Gluttonous Grimoire, The Cosmic Horror, Damaru, Omen Drum, Oath-Sworn Spear, Stygian Anchor, Toxic Blade, Totem of Death

### God-specific kit builds (use these)

#### Cernunnos — S-tier (role rank #1, model 66.3)

*Physical · Strength scaling (STR 80.4% / INT 51.1%)*

Cernunnos · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: protection shred, big ult spike, basic-attack kit, self heal / drain, hard crowd control, dash / leap engage. Tags: aa, dot, gap_close, hard_cc, heal, high_cc, long_cd, prot_shred. Style burst 31%/dps 69%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): general +0.0, damage +0.0, cooldown +0.0. Scale STR 80% / INT 51%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Tekko-Kagi (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Tekko-Kagi, The Crusher, Heartseeker. Actives 0/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 0/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Tekko-Kagi (pen, pen 10.0, 2650g)
  3. Hydra's Lament (power, 2450g)
  4. The Crusher (pen, pen 10.0, 2750g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Tsukuyomi — S-tier (role rank #2, model 62.5)

*Physical · Strength scaling (STR 157.1% / INT 112.5%)*

Tsukuyomi · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: big ult spike, hard crowd control, dash / leap engage, CC immunity in kit, high mobility, burst combos. Tags: anti_cc, burst, gap_close, hard_cc, heal, long_cd, mobile, ult_nuke. Style burst 65%/dps 35%; patch stable (net -0.2, r5 +0.0). Patch axes (r5): damage -0.2, general +0.0, utility +0.0. Scale STR 157% / INT 112%. Path: The Crusher (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage); Jotunn's Revenge (CDR + pen for gank/engage). Pen: The Crusher, Jotunn's Revenge, Heartseeker, Avatar's Parashu. Actives 2/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 35.0):
  1. The Crusher (pen, pen 10.0, 2750g)
  2. Hydra's Lament (power, 2450g)
  3. Jotunn's Revenge (power, pen 5.0, 2400g)
  4. Arondight (power, active, 2550g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Ravana — S-tier (role rank #3, model 61.1)

*Physical · Strength scaling (STR 88.1% / INT 0%)*

Ravana · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: big ult spike, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit, high mobility. Tags: anti_cc, burst, gap_close, hard_cc, heal, long_cd, mobile, pet_zone. Style burst 70%/dps 30%; patch new (net +0.9, r5 +0.9). Patch axes (r5): general +0.7, heal +0.1, utility +0.0. Scale STR 88% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); The Crusher (penetration required for damage role). Pen: Jotunn's Revenge, The Crusher, Heartseeker. Actives 2/3 · pen ≈ 25. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. The Crusher (pen, pen 10.0, 2750g)
  4. Arondight (power, active, 2550g)
  5. Bloodforge (power, active, 2550g)
  6. Heartseeker (pen, pen 10.0, 3000g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Thor — A-tier (role rank #4, model 58.9)

*Physical · Strength scaling (STR 76.1% / INT 0%)*

Thor · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: channel / cast time, big ult spike, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, channel, gap_close, hard_cc, high_cc, long_cd, pet_zone, ult_nuke. Style burst 70%/dps 30%; patch rising (net +0.2, r5 +2.4). Patch axes (r5): general +1.6, attack_speed +0.8. Scale STR 76% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Tekko-Kagi (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Tekko-Kagi, The Crusher, Heartseeker. Actives 1/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Tekko-Kagi (pen, pen 10.0, 2650g)
  3. Hydra's Lament (power, 2450g)
  4. Arondight (power, active, 2550g)
  5. The Crusher (pen, pen 10.0, 2750g)
  6. Heartseeker (pen, pen 10.0, 3000g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Ratatoskr — A-tier (role rank #5, model 58.6)

*Physical · Strength scaling (STR 89.0% / INT 0%)*

Ratatoskr · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: big ult spike, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC, burst combos. Tags: anti_cc, burst, gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 75%/dps 25%; patch rising (net +3.2, r5 +2.1). Patch axes (r5): damage +1.9, cooldown +0.1, crit +0.1. Scale STR 89% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); The Crusher (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, The Crusher, Heartseeker, Avatar's Parashu. Actives 1/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. The Crusher (pen, pen 10.0, 2750g)
  3. Hydra's Lament (power, 2450g)
  4. Ashwhorl Acorn (mitigate, 2000g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Awilix — A-tier (role rank #6, model 55.3)

*Physical · Strength scaling (STR 64.0% / INT 0%)*

Awilix · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: attack-speed steroid, pet / deployable, hard crowd control, dash / leap engage, lots of CC, high mobility. Tags: as_steroid, gap_close, hard_cc, high_cc, long_cd, mobile, pet_zone, sustained. Style burst 23%/dps 77%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): attack_speed +0.0, damage +0.0, general -0.0. Scale STR 64% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Pendulum Blade (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Pendulum Blade, The Crusher. Actives 2/3 · pen ≈ 25. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Pendulum Blade (pen, active, pen 10.0, 2750g)
  3. Hydra's Lament (power, 2450g)
  4. Damaru (power, 2500g)
  5. Bloodforge (power, active, 2550g)
  6. The Crusher (pen, pen 10.0, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Gilgamesh — A-tier (role rank #7, model 53.1)

*Physical · Strength scaling (STR 72.8% / INT 0%)*

Gilgamesh · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, lots of CC, burst combos. Tags: burst, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, team_buff. Style burst 78%/dps 22%; patch new (net -0.0, r5 +0.0). Patch axes (r5): damage -0.4, general +0.2, survivability +0.1. Scale STR 73% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Tekko-Kagi (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Tekko-Kagi, The Crusher. Actives 2/3 · pen ≈ 25. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Tekko-Kagi (pen, pen 10.0, 2650g)
  3. Hydra's Lament (power, 2450g)
  4. Arondight (power, active, 2550g)
  5. Bloodforge (power, active, 2550g)
  6. The Crusher (pen, pen 10.0, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Thanatos — A-tier (role rank #8, model 52.8)

*Physical · Strength scaling (STR 56.1% / INT 0%)*

Thanatos · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: protection shred, self heal / drain, execute / threshold, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, burst, execute, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 63%/dps 37%; patch rising (net +1.3, r5 +1.2). Patch axes (r5): survivability +0.8, damage +0.2, heal +0.2. Scale STR 56% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Tekko-Kagi (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Tekko-Kagi, The Reaper, The Crusher. Actives 1/3 · pen ≈ 35. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Tekko-Kagi (pen, pen 10.0, 2650g)
  3. Hydra's Lament (power, 2450g)
  4. The Reaper (pen, pen 10.0, 2600g)
  5. Bloodforge (power, active, 2550g)
  6. The Crusher (pen, pen 10.0, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Mercury — B-tier (role rank #9, model 52.8)

*Physical · Strength scaling (STR 64.8% / INT 0%)*

Mercury · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: big ult spike, attack-speed steroid, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, as_steroid, gap_close, hard_cc, high_cc, long_cd, mobile, pet_zone. Style burst 16%/dps 84%; patch stable (net +0.4, r5 +0.1). Patch axes (r5): crit +0.1, damage +0.1. Scale STR 65% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Tekko-Kagi (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Tekko-Kagi, The Reaper, The Crusher. Actives 1/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Tekko-Kagi (pen, pen 10.0, 2650g)
  3. Hydra's Lament (power, 2450g)
  4. The Reaper (pen, pen 10.0, 2600g)
  5. Arondight (power, active, 2550g)
  6. The Crusher (pen, pen 10.0, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Fenrir — B-tier (role rank #10, model 50.9)

*Physical · Strength scaling (STR 97.4% / INT 0%)*

Fenrir · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: channel / cast time, big ult spike, basic-attack kit, self heal / drain, hard crowd control, dash / leap engage. Tags: aa, anti_cc, channel, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 20%/dps 80%; patch volatile (net +1.2, r5 +0.1). Patch axes (r5): crit +0.1, damage +0.1. Scale STR 97% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Tekko-Kagi (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Tekko-Kagi, The Crusher, Heartseeker. Actives 1/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Tekko-Kagi (pen, pen 10.0, 2650g)
  3. Hydra's Lament (power, 2450g)
  4. Arondight (power, active, 2550g)
  5. The Crusher (pen, pen 10.0, 2750g)
  6. Heartseeker (pen, pen 10.0, 3000g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Hun Batz — B-tier (role rank #11, model 50.7)

*Physical · Strength scaling (STR 62.6% / INT 0%)*

Hun Batz · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: channel / cast time, basic-attack kit, pet / deployable, hard crowd control, dash / leap engage, multi-hit / ticks. Tags: aa, channel, dot, gap_close, hard_cc, long_cd, pet_zone. Style burst 41%/dps 59%; patch rising (net +2.0, r5 +0.0). Patch axes (r5): damage +2.0, general +0.0, utility +0.0. Scale STR 63% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Pendulum Blade (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Pendulum Blade, The Reaper, The Crusher. Actives 2/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Pendulum Blade (pen, active, pen 10.0, 2750g)
  3. Hydra's Lament (power, 2450g)
  4. The Reaper (pen, pen 10.0, 2600g)
  5. Bloodforge (power, active, 2550g)
  6. The Crusher (pen, pen 10.0, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Aladdin — B-tier (role rank #12, model 49.2)

*Magical · Hybrid scaling (STR 113.8% / INT 109.8%)*

Aladdin · Jungle · archetype «mage_jungle» (INT / magical). Kit effects: big ult spike, execute / threshold, pet / deployable, hard crowd control, dash / leap engage, high mobility. Tags: burst, execute, gap_close, hard_cc, long_cd, mobile, pet_zone, shield. Style burst 59%/dps 41%; patch volatile (net -4.9, r5 +0.0). Patch axes (r5): damage -4.4, general -0.2, utility -0.2. Scale STR 114% / INT 110%. Path: Spear of Desolation (flat pen + CDR for ability burst); The Cosmic Horror (penetration required for damage role); Spear Of The Magus (multi-hit / shred — stacks Magus passive). Pen: Spear of Desolation, The Cosmic Horror, Spear Of The Magus, Book of Thoth, Rod of Tahuti, Soul Gem. Actives 0/2 · pen ≈ 40. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 0/2, pen ≈ 40.0):
  1. Spear of Desolation (pen, pen 10.0, 2650g)
  2. The Cosmic Horror (pen, pen 10.0, 2650g)
  3. Spear Of The Magus (pen, pen 10.0, 2700g)
  4. Book of Thoth (power, 2300g)
  5. Rod of Tahuti (power, pen 5.0, 3000g)
  6. Soul Gem (power, pen 5.0, 2500g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Ne Zha — B-tier (role rank #13, model 49.2)

*Physical · Strength scaling (STR 155.1% / INT 0%)*

Ne Zha · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: protection shred, big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, as_steroid, gap_close, hard_cc, heal, long_cd, mobile, prot_shred. Style burst 45%/dps 55%; patch falling (net -1.5, r5 -0.8). Patch axes (r5): survivability -2.0, damage +1.8, general -0.8. Scale STR 155% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Pendulum Blade (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Pendulum Blade, The Reaper, The Crusher, Heartseeker. Actives 1/3 · pen ≈ 45. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 45.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Pendulum Blade (pen, active, pen 10.0, 2750g)
  3. Hydra's Lament (power, 2450g)
  4. The Reaper (pen, pen 10.0, 2600g)
  5. The Crusher (pen, pen 10.0, 2750g)
  6. Heartseeker (pen, pen 10.0, 3000g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Mordred — B-tier (role rank #14, model 49.1)

*Physical · Strength scaling (STR 77.5% / INT 45.8%)*

Mordred · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: damage over time, channel / cast time, big ult spike, attack-speed steroid, self heal / drain, heavy healing. Tags: anti_cc, as_steroid, burst, channel, dot, gap_close, hard_cc, heal. Style burst 59%/dps 41%; patch stable (net -0.6, r5 +0.0). Patch axes (r5): damage -0.6, survivability +0.0, general -0.0. Scale STR 77% / INT 46%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Tekko-Kagi (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Tekko-Kagi, The Crusher, Heartseeker. Actives 1/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Tekko-Kagi (pen, pen 10.0, 2650g)
  3. Hydra's Lament (power, 2450g)
  4. Arondight (power, active, 2550g)
  5. The Crusher (pen, pen 10.0, 2750g)
  6. Heartseeker (pen, pen 10.0, 3000g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Odin — C-tier (role rank #15, model 48.5)

*Physical · Strength scaling (STR 53.9% / INT 21.0%)*

Odin · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: big ult spike, attack-speed steroid, shields, hard crowd control, dash / leap engage, ally buffs / auras. Tags: as_steroid, burst, dot, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 65%/dps 35%; patch stable (net +0.6, r5 +0.0). Patch axes (r5): cooldown +0.5, damage +0.0, survivability +0.0. Scale STR 54% / INT 21%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); The Reaper (penetration required for damage role). Pen: Jotunn's Revenge, The Reaper, The Crusher, Heartseeker, Avatar's Parashu. Actives 1/3 · pen ≈ 45. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 45.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. The Reaper (pen, pen 10.0, 2600g)
  4. The Crusher (pen, pen 10.0, 2750g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Achilles — C-tier (role rank #16, model 45.1)

*Physical · Strength scaling (STR 82.9% / INT 0%)*

Achilles · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: big ult spike, basic-attack kit, self heal / drain, execute / threshold, shields, hard crowd control. Tags: aa, anti_cc, execute, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 30%/dps 70%; patch volatile (net +0.6, r5 +0.6). Patch axes (r5): general +0.6. Scale STR 83% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); The Crusher (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, The Crusher, Heartseeker. Actives 2/3 · pen ≈ 25. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. The Crusher (pen, pen 10.0, 2750g)
  3. Hydra's Lament (power, 2450g)
  4. Bloodforge (power, active, 2550g)
  5. Arondight (power, active, 2550g)
  6. Heartseeker (pen, pen 10.0, 3000g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Loki — C-tier (role rank #17, model 42.9)

*Physical · Strength scaling (STR 62.6% / INT 0%)*

Loki · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: channel / cast time, big ult spike, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, channel, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 84%/dps 16%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): utility +0.1, damage +0.0, general +0.0. Scale STR 63% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); The Crusher (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, The Crusher, Heartseeker, Avatar's Parashu. Actives 1/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. The Crusher (pen, pen 10.0, 2750g)
  3. Hydra's Lament (power, 2450g)
  4. Damaru (power, 2500g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Nemesis — C-tier (role rank #18, model 41.6)

*Physical · Strength scaling (STR 102.2% / INT 70.4%)*

Nemesis · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: big ult spike, dash / leap engage, shields, healing in kit, long cooldowns. Tags: gap_close, heal, long_cd, shield, ult_nuke. Style burst 53%/dps 47%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): damage +0.0. Scale STR 102% / INT 70%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Toxic Blade (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Toxic Blade, The Reaper, The Crusher, Heartseeker. Actives 0/3 · pen ≈ 45. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 0/3, pen ≈ 45.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Toxic Blade (pen, pen 10.0, 2700g)
  3. Hydra's Lament (power, 2450g)
  4. The Reaper (pen, pen 10.0, 2600g)
  5. The Crusher (pen, pen 10.0, 2750g)
  6. Heartseeker (pen, pen 10.0, 3000g)
- **Relics:** Blink Rune (36.2), Sundering Arc (32.6)

#### Pele — C-tier (role rank #19, model 40.8)

*Physical · Strength scaling (STR 91.7% / INT 0%)*

Pele · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: big ult spike, self heal / drain, execute / threshold, dash / leap engage, CC immunity in kit, high mobility. Tags: anti_cc, burst, execute, gap_close, heal, long_cd, mobile, self_sustain. Style burst 77%/dps 23%; patch volatile (net -4.7, r5 +0.0). Patch axes (r5): damage -3.5, heal -0.8, survivability -0.3. Scale STR 92% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); The Reaper (penetration required for damage role). Pen: Jotunn's Revenge, The Reaper, The Crusher. Actives 1/3 · pen ≈ 25. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. The Reaper (pen, pen 10.0, 2600g)
  4. Damaru (power, 2500g)
  5. Bloodforge (power, active, 2550g)
  6. The Crusher (pen, pen 10.0, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Bastet — D-tier (role rank #20, model 32.8)

*Physical · Strength scaling (STR 73.0% / INT 8.8%)*

Bastet · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: big ult spike, self heal / drain, pet / deployable, hard crowd control, dash / leap engage, multi-hit / ticks. Tags: dot, gap_close, hard_cc, heal, long_cd, pet_zone, self_sustain, ult_nuke. Style burst 70%/dps 30%; patch falling (net -3.6, r5 +0.0). Patch axes (r5): damage -2.6, utility -1.3, general +0.4. Scale STR 73% / INT 9%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Pendulum Blade (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Pendulum Blade, The Crusher, Heartseeker. Actives 1/3 · pen ≈ 35. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Pendulum Blade (pen, active, pen 10.0, 2750g)
  3. Hydra's Lament (power, 2450g)
  4. Damaru (power, 2500g)
  5. The Crusher (pen, pen 10.0, 2750g)
  6. Heartseeker (pen, pen 10.0, 3000g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Da Ji — D-tier (role rank #21, model 31.5)

*Physical · Strength scaling (STR 48.8% / INT 0%)*

Da Ji · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: damage over time, channel / cast time, execute / threshold, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, channel, dot, execute, gap_close, hard_cc, heavy_dot, high_cc. Style burst 57%/dps 43%; patch volatile (net -1.7, r5 +0.0). Patch axes (r5): survivability -0.9, damage -0.4, utility -0.3. Scale STR 49% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); The Crusher (penetration required for damage role); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, The Crusher, Heartseeker, The Reaper. Actives 1/3 · pen ≈ 35. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. The Crusher (pen, pen 10.0, 2750g)
  3. Hydra's Lament (power, 2450g)
  4. Arondight (power, active, 2550g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. The Reaper (pen, pen 10.0, 2600g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Kali — D-tier (role rank #22, model 25.0)

*Physical · Strength scaling (STR 54.5% / INT 17.1%)*

Kali · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: protection shred, self heal / drain, heavy healing, execute / threshold, hard crowd control, dash / leap engage. Tags: anti_cc, execute, gap_close, hard_cc, heal, heavy_heal, long_cd, prot_shred. Style burst 0%/dps 100%; patch volatile (net -2.9, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 54% / INT 17%. Path: Tyrfing (Jungle path fit for kit profile); Jotunn's Revenge (CDR + pen for gank/engage); Pendulum Blade (penetration required for damage role). Pen: Jotunn's Revenge, Pendulum Blade, The Crusher. Actives 1/3 · pen ≈ 25. Soft high-SR inspiration on 5 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 25.0):
  1. Tyrfing (power, 2400g)
  2. Jotunn's Revenge (power, pen 5.0, 2400g)
  3. Pendulum Blade (pen, active, pen 10.0, 2750g)
  4. Hydra's Lament (power, 2450g)
  5. Hastened Fatalis (power, 2650g)
  6. The Crusher (pen, pen 10.0, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

#### Susano — D-tier (role rank #23, model 21.3)

*Physical · Strength scaling (STR 104.2% / INT 0%)*

Susano · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: damage over time, big ult spike, pet / deployable, dash / leap engage, multi-hit / ticks, burst combos. Tags: burst, dot, gap_close, heavy_dot, long_cd, pet_zone, ult_nuke, zone. Style burst 80%/dps 20%; patch falling (net -8.2, r5 -8.3). Patch axes (r5): damage -7.1, cooldown -0.8, utility -0.4. Scale STR 104% / INT 0%. Path: Tekko-Kagi (penetration required for damage role); Pendulum Blade (penetration required for damage role); Jotunn's Revenge (CDR + pen for gank/engage). Pen: Tekko-Kagi, Pendulum Blade, Jotunn's Revenge, The Crusher, Heartseeker. Actives 1/3 · pen ≈ 45. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 45.0):
  1. Tekko-Kagi (pen, pen 10.0, 2650g)
  2. Pendulum Blade (pen, active, pen 10.0, 2750g)
  3. Jotunn's Revenge (power, pen 5.0, 2400g)
  4. Hydra's Lament (power, 2450g)
  5. The Crusher (pen, pen 10.0, 2750g)
  6. Heartseeker (pen, pen 10.0, 3000g)
- **Relics:** Purification Beads (38.0), Blink Rune (36.2)

---

## Solo

Conquest solo — unkillable frontliner: dual prots, HP, Dampening/Plating/Tenacity, hybrid offline damage. Absorb pressure so mid/ADC free-hit.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| hp | 18% |
| pprot | 16% |
| mprot | 16% |
| damp | 10% |
| plat | 8% |
| ten | 8% |
| cdr | 8% |
| str | 6% |
| int | 5% |
| ls | 3% |
| pen | 2% |
| hpr | 0% |
| as | 0% |
| mp | 0% |

### Role job (not a full build)

This is the Solo job description + common items — not a complete build. Open a god below for a kit-specific 1 starter + 6 buy order (actives ≤2, hard max 3).

**Typical starter:** Warrior's Axe
**Priority stats:** hp, pprot, mprot, damp, plat
**Common role items (not ordered as a build):** Brawler’s Beat Stick, Wyrmskin Hide, Helm of Darkness, Regrowth Striders, Stygian Anchor, Alchemist Coat, Sphere of Negation, Stone of Binding

### God-specific kit builds (use these)

#### Sun Wukong — S-tier (role rank #1, model 79.5)

*Physical · Strength scaling (STR 113.9% / INT 45.7%)*

Sun Wukong · Solo · archetype «bruiser_solo» (STR / physical). Kit effects: big ult spike, execute / threshold, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: anti_cc, burst, dot, execute, gap_close, hard_cc, heal, high_cc. Style burst 65%/dps 35%; patch rising (net +3.3, r5 +3.3). Patch axes (r5): damage +1.7, survivability +1.6. Scale STR 114% / INT 46%. Path: Shifter's Shield (offline hybrid tank); Genji's Guard (magic prot + CDR for mages); Eye of the Storm (Solo path fit for kit profile). Actives 1/3 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Genji's Guard (defense, 2350g)
  3. Eye of the Storm (power, 2600g)
  4. Doublet of Binding (mitigate, active, 2700g)
  5. Oni Hunter's Garb (defense, 2500g)
  6. Kinetic Cuirass (mitigate, 2400g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Chaac — S-tier (role rank #2, model 71.1)

*Physical · Strength scaling (STR 97.1% / INT 44.1%)*

Chaac · Solo · archetype «sustain_solo» (STR / physical). Kit effects: channel / cast time, big ult spike, self heal / drain, pet / deployable, hard crowd control, dash / leap engage. Tags: anti_cc, channel, dot, gap_close, hard_cc, heal, long_cd, pet_zone. Style burst 40%/dps 60%; patch rising (net +2.1, r5 +1.9). Patch axes (r5): cooldown +1.0, attack_speed +0.4, utility +0.4. Scale STR 97% / INT 44%. Path: Shifter's Shield (offline hybrid tank); Genji's Guard (magic prot + CDR for mages); Phoenix Feather (shield / phoenix-style bulk). Actives 1/3 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Genji's Guard (defense, 2350g)
  3. Phoenix Feather (mitigate, active, 2350g)
  4. Eye of the Storm (power, 2600g)
  5. Wyrmskin Hide (mitigate, 2600g)
  6. Kinetic Cuirass (mitigate, 2400g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Cu Chulainn — S-tier (role rank #3, model 62.4)

*Physical · Strength scaling (STR 62.0% / INT 0%)*

Cu Chulainn · Solo · archetype «sustain_solo» (STR / physical). Kit effects: channel / cast time, self heal / drain, heavy healing, execute / threshold, pet / deployable, hard crowd control. Tags: anti_cc, channel, execute, gap_close, hard_cc, heal, heavy_heal, high_cc. Style burst 26%/dps 74%; patch rising (net +7.3, r5 +6.7). Patch axes (r5): general +3.9, damage +2.3, survivability +0.5. Scale STR 62% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Mystical Mail (Solo path fit for kit profile); Runeforged Hammer (Solo path fit for kit profile). Actives 0/3 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Mystical Mail (defense, 2550g)
  3. Runeforged Hammer (power, 2550g)
  4. Breastplate of Valor (defense, 2400g)
  5. Brawler’s Beat Stick (counter, 2500g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Amaterasu — A-tier (role rank #4, model 61.0)

*Physical · Hybrid scaling (STR 47.0% / INT 51.3%)*

Amaterasu · Solo · archetype «sustain_solo» (STR / physical). Kit effects: big ult spike, self heal / drain, hard crowd control, dash / leap engage, CC immunity in kit, sustained DPS. Tags: anti_cc, dot, gap_close, hard_cc, heal, long_cd, self_sustain, shield. Style burst 2%/dps 98%; patch rising (net +2.0, r5 +1.7). Patch axes (r5): general +1.7. Scale STR 47% / INT 51%. Path: Shifter's Shield (offline hybrid tank); Mystical Mail (Solo path fit for kit profile); Genji's Guard (magic prot + CDR for mages). Actives 0/3 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Mystical Mail (defense, 2550g)
  3. Genji's Guard (defense, 2350g)
  4. Shield of the Phoenix (mitigate, 2400g)
  5. Eye of the Storm (power, 2600g)
  6. Xibalban Effigy (defense, 2750g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Thor — A-tier (role rank #5, model 58.9)

*Physical · Strength scaling (STR 76.1% / INT 0%)*

Thor · Solo · archetype «tank_solo» (STR / physical). Kit effects: channel / cast time, big ult spike, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, channel, gap_close, hard_cc, high_cc, long_cd, pet_zone, ult_nuke. Style burst 70%/dps 30%; patch rising (net +0.2, r5 +2.4). Patch axes (r5): general +1.6, attack_speed +0.8. Scale STR 76% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Breastplate of Valor (physical CDR defense); Genji's Guard (magic prot + CDR for mages). Actives 0/3 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Breastplate of Valor (defense, 2400g)
  3. Genji's Guard (defense, 2350g)
  4. Regrowth Striders (defense, 2550g)
  5. Eye of the Storm (power, 2600g)
  6. Xibalban Effigy (defense, 2750g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Jormungandr — A-tier (role rank #6, model 58.3)

*Magical · Intelligence scaling (STR 27.9% / INT 51.4%)*

Jormungandr · Solo · archetype «mage_solo» (INT / magical). Kit effects: channel / cast time, big ult spike, hard crowd control, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, channel, dot, hard_cc, heal, high_cc, long_cd. Style burst 64%/dps 36%; patch stable (net +0.5, r5 +0.0). Patch axes (r5): survivability +0.2, utility +0.1, damage +0.1. Scale STR 28% / INT 51%. Path: Shifter's Shield (offline hybrid tank); Ethereal Staff (Solo path fit for kit profile); Breastplate of Valor (physical CDR defense). Actives 1/2 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Ethereal Staff (mitigate, 2550g)
  3. Breastplate of Valor (defense, 2400g)
  4. Alchemist Coat (mitigate, 2350g)
  5. Phoenix Feather (mitigate, active, 2350g)
  6. Xibalban Effigy (defense, 2750g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Osiris — A-tier (role rank #7, model 56.6)

*Physical · Strength scaling (STR 66.0% / INT 0%)*

Osiris · Solo · archetype «tank_solo» (STR / physical). Kit effects: attack-speed steroid, pet / deployable, hard crowd control, dash / leap engage, lots of CC, sustained DPS. Tags: as_steroid, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, sustained. Style burst 27%/dps 73%; patch stable (net -0.0, r5 +0.0). Patch axes (r5): attack_speed -0.0, damage -0.0, utility +0.0. Scale STR 66% / INT 0%. Path: Prophetic Cloak (Solo path fit for kit profile); Genji's Guard (Solo path fit for kit profile); Midgardian Mail (Solo path fit for kit profile). Actives 1/3 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Prophetic Cloak (defense, 2400g)
  2. Genji's Guard (defense, 2350g)
  3. Midgardian Mail (counter, 2400g)
  4. Shield Splitter (power, active, 2400g)
  5. Eye of the Storm (power, 2600g)
  6. Wyrmskin Hide (mitigate, 2600g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Gilgamesh — B-tier (role rank #8, model 53.1)

*Physical · Strength scaling (STR 72.8% / INT 0%)*

Gilgamesh · Solo · archetype «bruiser_solo» (STR / physical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, lots of CC, burst combos. Tags: burst, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, team_buff. Style burst 78%/dps 22%; patch new (net -0.0, r5 +0.0). Patch axes (r5): damage -0.4, general +0.2, survivability +0.1. Scale STR 73% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Genji's Guard (magic prot + CDR for mages); Spectral Armor (mitigate enemy crit (Spectral line)). Actives 1/3 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Genji's Guard (defense, 2350g)
  3. Spectral Armor (mitigate, 2300g)
  4. Phoenix Feather (mitigate, active, 2350g)
  5. Stone of Binding (mitigate, 2550g)
  6. Eye of the Storm (power, 2600g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Hercules — B-tier (role rank #9, model 51.5)

*Physical · Strength scaling (STR 84.8% / INT 0%)*

Hercules · Solo · archetype «sustain_solo» (STR / physical). Kit effects: big ult spike, attack-speed steroid, self heal / drain, hard crowd control, dash / leap engage, lots of CC. Tags: as_steroid, gap_close, hard_cc, heal, high_cc, long_cd, self_sustain, sustained. Style burst 38%/dps 62%; patch stable (net -0.4, r5 +0.2). Patch axes (r5): damage +0.1, survivability +0.1. Scale STR 85% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Genji's Guard (magic prot + CDR for mages); Shield Splitter (Solo path fit for kit profile). Actives 1/3 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Genji's Guard (defense, 2350g)
  3. Shield Splitter (power, active, 2400g)
  4. Shield of the Phoenix (mitigate, 2400g)
  5. Brawler’s Beat Stick (counter, 2500g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Bellona — B-tier (role rank #10, model 50.9)

*Physical · Strength scaling (STR 69.9% / INT 0%)*

Bellona · Solo · archetype «sustain_solo» (STR / physical). Kit effects: basic-attack kit, self heal / drain, shields, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, burst, gap_close, hard_cc, heal, heavy_shield, high_cc. Style burst 65%/dps 35%; patch stable (net +0.4, r5 +0.0). Patch axes (r5): damage +0.3, heal +0.0, general +0.0. Scale STR 70% / INT 0%. Path: Yogi's Necklace (Solo path fit for kit profile); Berserker's Shield (Solo path fit for kit profile); Phoenix Feather (shield / phoenix-style bulk). Actives 2/3 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 2/3, pen ≈ 0.0):
  1. Yogi's Necklace (defense, 2250g)
  2. Berserker's Shield (defense, 2400g)
  3. Phoenix Feather (mitigate, active, 2350g)
  4. Brawler’s Beat Stick (counter, 2500g)
  5. Wyrmskin Hide (mitigate, 2600g)
  6. Doublet of Binding (mitigate, active, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Mordred — B-tier (role rank #11, model 49.1)

*Physical · Strength scaling (STR 77.5% / INT 45.8%)*

Mordred · Solo · archetype «sustain_solo» (STR / physical). Kit effects: damage over time, channel / cast time, big ult spike, attack-speed steroid, self heal / drain, heavy healing. Tags: anti_cc, as_steroid, burst, channel, dot, gap_close, hard_cc, heal. Style burst 59%/dps 41%; patch stable (net -0.6, r5 +0.0). Patch axes (r5): damage -0.6, survivability +0.0, general -0.0. Scale STR 77% / INT 46%. Path: Shifter's Shield (offline hybrid tank); Shield of the Phoenix (shield / phoenix-style bulk); Brawler’s Beat Stick (healing reduction). Actives 1/3 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Shield of the Phoenix (mitigate, 2400g)
  3. Brawler’s Beat Stick (counter, 2500g)
  4. Stone of Binding (mitigate, 2550g)
  5. Eye of the Storm (power, 2600g)
  6. Doublet of Binding (mitigate, active, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Odin — B-tier (role rank #12, model 48.5)

*Physical · Strength scaling (STR 53.9% / INT 21.0%)*

Odin · Solo · archetype «shield_solo» (STR / physical). Kit effects: big ult spike, attack-speed steroid, shields, hard crowd control, dash / leap engage, ally buffs / auras. Tags: as_steroid, burst, dot, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 65%/dps 35%; patch stable (net +0.6, r5 +0.0). Patch axes (r5): cooldown +0.5, damage +0.0, survivability +0.0. Scale STR 54% / INT 21%. Path: Shifter's Shield (offline hybrid tank); Genji's Guard (magic prot + CDR for mages); Stygian Anchor (peel / anti-dive anchor). Actives 0/3 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Genji's Guard (defense, 2350g)
  3. Stygian Anchor (counter, 2550g)
  4. Regrowth Striders (defense, 2550g)
  5. Eye of the Storm (power, 2600g)
  6. Wyrmskin Hide (mitigate, 2600g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Hua Mulan — B-tier (role rank #13, model 48.4)

*Physical · Strength scaling (STR 94.0% / INT 0%)*

Hua Mulan · Solo · archetype «bruiser_solo» (STR / physical). Kit effects: big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: anti_cc, as_steroid, burst, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 81%/dps 19%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): damage +0.3, cooldown -0.1, survivability -0.1. Scale STR 94% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Breastplate of Valor (physical CDR defense); Genji's Guard (magic prot + CDR for mages). Actives 1/3 · pen ≈ 0. Soft high-SR inspiration on 4 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Breastplate of Valor (defense, 2400g)
  3. Genji's Guard (defense, 2350g)
  4. Eye of the Storm (power, 2600g)
  5. Doublet of Binding (mitigate, active, 2700g)
  6. Kinetic Cuirass (mitigate, 2400g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Artio — C-tier (role rank #14, model 45.8)

*Magical · Hybrid scaling (STR 60.4% / INT 50.1%)*

Artio · Solo · archetype «sustain_solo» (INT / magical). Kit effects: protection shred, channel / cast time, big ult spike, heavy healing, hard crowd control, ally buffs / auras. Tags: channel, hard_cc, heal, heavy_heal, high_cc, long_cd, prot_shred, team_buff. Style burst 59%/dps 41%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): general +0.1, damage +0.0, mana -0.0. Scale STR 60% / INT 50%. Path: Shifter's Shield (offline hybrid tank); Gauntlet of Thebes (team aura / support core); Phoenix Feather (shield / phoenix-style bulk). Actives 1/2 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Gauntlet of Thebes (defense, 2200g)
  3. Phoenix Feather (mitigate, active, 2350g)
  4. Alchemist Coat (mitigate, 2350g)
  5. Gem of Isolation (mitigate, 2450g)
  6. Rod Of Asclepius (power, 2350g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Achilles — C-tier (role rank #15, model 45.1)

*Physical · Strength scaling (STR 82.9% / INT 0%)*

Achilles · Solo · archetype «sustain_solo» (STR / physical). Kit effects: big ult spike, basic-attack kit, self heal / drain, execute / threshold, shields, hard crowd control. Tags: aa, anti_cc, execute, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 30%/dps 70%; patch volatile (net +0.6, r5 +0.6). Patch axes (r5): general +0.6. Scale STR 83% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Breastplate of Valor (physical CDR defense); Mystical Mail (Solo path fit for kit profile). Actives 0/3 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Breastplate of Valor (defense, 2400g)
  3. Mystical Mail (defense, 2550g)
  4. Genji's Guard (defense, 2350g)
  5. Shield of the Phoenix (mitigate, 2400g)
  6. Brawler’s Beat Stick (counter, 2500g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Nike — C-tier (role rank #16, model 43.6)

*Physical · Strength scaling (STR 56.9% / INT 0%)*

Nike · Solo · archetype «sustain_solo» (STR / physical). Kit effects: channel / cast time, self heal / drain, shields, hard crowd control, dash / leap engage, ally buffs / auras. Tags: anti_cc, channel, gap_close, hard_cc, heal, heavy_shield, high_cc, long_cd. Style burst 69%/dps 31%; patch rising (net +1.0, r5 +1.0). Patch axes (r5): general +1.0. Scale STR 57% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Mystical Mail (Solo path fit for kit profile); Genji's Guard (magic prot + CDR for mages). Actives 1/3 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Mystical Mail (defense, 2550g)
  3. Genji's Guard (defense, 2350g)
  4. Stygian Anchor (counter, 2550g)
  5. Eye of the Storm (power, 2600g)
  6. Doublet of Binding (mitigate, active, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Horus — C-tier (role rank #17, model 41.7)

*Physical · Strength scaling (STR 74.4% / INT 0%)*

Horus · Solo · archetype «sustain_solo» (STR / physical). Kit effects: channel / cast time, self heal / drain, heavy healing, hard crowd control, dash / leap engage, ally buffs / auras. Tags: anti_cc, channel, gap_close, hard_cc, heal, heavy_heal, high_cc, long_cd. Style burst 30%/dps 70%; patch falling (net -6.0, r5 -5.5). Patch axes (r5): survivability -2.9, heal -1.2, cooldown -1.0. Scale STR 74% / INT 0%. Path: Shifter's Shield (offline hybrid tank; patch falling — extra bulk/CDR); Genji's Guard (patch falling — extra bulk/CDR; kit CD nerfed — buy CDR); Phoenix Feather (shield / phoenix-style bulk). Actives 1/3 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Genji's Guard (defense, 2350g)
  3. Phoenix Feather (mitigate, active, 2350g)
  4. Brawler’s Beat Stick (counter, 2500g)
  5. Eye of the Storm (power, 2600g)
  6. Xibalban Effigy (defense, 2750g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Cabrakan — C-tier (role rank #18, model 39.1)

*Magical · Hybrid scaling (STR 75.1% / INT 51.1%)*

Cabrakan · Solo · archetype «shield_solo» (INT / magical). Kit effects: channel / cast time, big ult spike, hard crowd control, ally buffs / auras, lots of CC, multi-hit / ticks. Tags: channel, hard_cc, heal, high_cc, long_cd, shield, team_buff, ult_nuke. Style burst 55%/dps 45%; patch falling (net -2.8, r5 -1.2). Patch axes (r5): damage -0.7, general -0.6, heal +0.1. Scale STR 75% / INT 51%. Path: Shifter's Shield (offline hybrid tank; patch falling — extra bulk/CDR); Genji's Guard (magic prot + CDR for mages; patch falling — extra bulk/CDR); Spectral Armor (mitigate enemy crit (Spectral line)). Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Genji's Guard (defense, 2350g)
  3. Spectral Armor (mitigate, 2300g)
  4. Alchemist Coat (mitigate, 2350g)
  5. Leviathan's Hide (mitigate, 2400g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Guan Yu — D-tier (role rank #19, model 38.8)

*Physical · Strength scaling (STR 42.4% / INT 13.3%)*

Guan Yu · Solo · archetype «sustain_solo» (STR / physical). Kit effects: damage over time, attack-speed steroid, self heal / drain, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, dot, gap_close, hard_cc, heal, heavy_dot, long_cd, pet_zone. Style burst 16%/dps 84%; patch volatile (net -1.6, r5 -0.1). Patch axes (r5): cooldown -1.7, attack_speed +1.6. Scale STR 42% / INT 13%. Path: Shifter's Shield (offline hybrid tank); Genji's Guard (magic prot + CDR for mages; kit CD nerfed — buy CDR); Stygian Anchor (peel / anti-dive anchor). Actives 0/3 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Genji's Guard (defense, 2350g)
  3. Stygian Anchor (counter, 2550g)
  4. Eye of the Storm (power, 2600g)
  5. Wyrmskin Hide (mitigate, 2600g)
  6. Xibalban Effigy (defense, 2750g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Hades — D-tier (role rank #20, model 37.6)

*Magical · Intelligence scaling (STR 0% / INT 85.1%)*

Hades · Solo · archetype «sustain_solo» (INT / magical). Kit effects: damage over time, channel / cast time, big ult spike, self heal / drain, hard crowd control, dash / leap engage. Tags: anti_cc, channel, dot, gap_close, hard_cc, heal, heavy_dot, high_cc. Style burst 47%/dps 53%; patch falling (net -1.5, r5 -1.5). Patch axes (r5): cooldown -1.3, survivability -1.2, general +1.0. Scale STR 0% / INT 85%. Path: Shifter's Shield (offline hybrid tank; patch falling — extra bulk/CDR); Genji's Guard (magic prot + CDR for mages; patch falling — extra bulk/CDR); Contagion (team anti-heal aura). Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Genji's Guard (defense, 2350g)
  3. Contagion (defense, 2400g)
  4. Midgardian Mail (counter, 2400g)
  5. Brawler’s Beat Stick (counter, 2500g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Cerberus — D-tier (role rank #21, model 17.8)

*Magical · Intelligence scaling (STR 0% / INT 42.6%)*

Cerberus · Solo · archetype «sustain_solo» (INT / magical). Kit effects: self heal / drain, pet / deployable, hard crowd control, dash / leap engage, burst combos, lots of CC. Tags: dot, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, self_sustain. Style burst 100%/dps 0%; patch falling (net -3.9, r5 -2.9). Patch axes (r5): cooldown -2.0, damage -0.9. Scale STR 0% / INT 43%. Path: Shifter's Shield (offline hybrid tank; patch falling — extra bulk/CDR); Mystical Mail (Solo path fit for kit profile); Genji's Guard (magic prot + CDR for mages; patch falling — extra bulk/CDR). Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2750g)
  2. Mystical Mail (defense, 2550g)
  3. Genji's Guard (defense, 2350g)
  4. Stone of Binding (mitigate, 2550g)
  5. Regrowth Striders (defense, 2550g)
  6. Wyrmskin Hide (mitigate, 2600g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

---

## Support

Conquest support — peel for ADC & mid: dual prots, Damp/Plat/Ten, anti-AS, anti-crit, aura/team utility. Body-block & counter, not personal DPS.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| hp | 16% |
| pprot | 15% |
| mprot | 15% |
| damp | 12% |
| plat | 10% |
| cdr | 10% |
| ten | 8% |
| int | 4% |
| mp | 3% |
| str | 2% |
| hpr | 2% |
| pen | 2% |
| mpr | 1% |
| as | 0% |
| ls | 0% |

### Role job (not a full build)

This is the Support job description + common items — not a complete build. Open a god below for a kit-specific 1 starter + 6 buy order (actives ≤2, hard max 3).

**Typical starter:** Selflessness
**Priority stats:** hp, pprot, mprot, damp, plat
**Common role items (not ordered as a build):** Stygian Anchor, Wyrmskin Hide, Helm of Darkness, Regrowth Striders, Alchemist Coat, Stone of Binding, Umbral Link, Sphere of Negation

### God-specific kit builds (use these)

#### Ganesha — S-tier (role rank #1, model 71.4)

*Magical · Intelligence scaling (STR 0% / INT 75.0%)*

Ganesha · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, big ult spike, execute / threshold, pet / deployable, hard crowd control, dash / leap engage. Tags: burst, channel, dot, execute, gap_close, hard_cc, high_cc, long_cd. Style burst 83%/dps 17%; patch rising (net +4.2, r5 +4.3). Patch axes (r5): damage +2.1, general +1.5, cooldown +0.7. Scale STR 0% / INT 75%. Path: Gauntlet of Thebes (team aura / support core); Gem of Isolation (zones & CC — Isolation slow/shred value); Stygian Anchor (peel / anti-dive anchor). Actives 1/2 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Gem of Isolation (mitigate, 2450g)
  3. Stygian Anchor (counter, 2550g)
  4. Regrowth Striders (defense, 2550g)
  5. Helm of Darkness (defense, active, 2700g)
  6. Xibalban Effigy (defense, 2750g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Ymir — S-tier (role rank #2, model 62.5)

*Magical · Intelligence scaling (STR 12.3% / INT 117.7%)*

Ymir · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, big ult spike, pet / deployable, hard crowd control, low mobility, CC immunity in kit. Tags: anti_cc, burst, channel, hard_cc, high_cc, immobile, long_cd, pet_zone. Style burst 61%/dps 39%; patch stable (net +0.9, r5 +0.0). Patch axes (r5): damage +0.5, survivability +0.3, cooldown +0.0. Scale STR 12% / INT 118%. Path: Alchemist Coat (tenacity / anti-CC bulk); Gem of Isolation (zones & CC — Isolation slow/shred value); Doublet of Binding (Stone of Binding — CC setup shred). Actives 1/2 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Alchemist Coat (mitigate, 2350g)
  2. Gem of Isolation (mitigate, 2450g)
  3. Doublet of Binding (mitigate, active, 2700g)
  4. Draconic Scale (defense, 2700g)
  5. Triton's Conch (power, 2700g)
  6. Resolute Mantle (mitigate, 2750g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (42.0)

#### Jormungandr — S-tier (role rank #3, model 58.3)

*Magical · Intelligence scaling (STR 27.9% / INT 51.4%)*

Jormungandr · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, big ult spike, hard crowd control, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, channel, dot, hard_cc, heal, high_cc, long_cd. Style burst 64%/dps 36%; patch stable (net +0.5, r5 +0.0). Patch axes (r5): survivability +0.2, utility +0.1, damage +0.1. Scale STR 28% / INT 51%. Path: Gauntlet of Thebes (team aura / support core); Gem of Isolation (zones & CC — Isolation slow/shred value); Damaru (Support path fit for kit profile). Actives 1/2 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Gem of Isolation (mitigate, 2450g)
  3. Damaru (power, 2500g)
  4. Stygian Anchor (counter, 2550g)
  5. Doublet of Binding (mitigate, active, 2700g)
  6. Spectral Armor (mitigate, 2300g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Baron Samedi — A-tier (role rank #4, model 53.8)

*Magical · Intelligence scaling (STR 0% / INT 69.6%)*

Baron Samedi · Support · archetype «lockdown_support» (INT / magical). Kit effects: damage over time, channel / cast time, execute / threshold, pet / deployable, hard crowd control, ally buffs / auras. Tags: burst, channel, dot, execute, hard_cc, heal, heavy_dot, high_cc. Style burst 72%/dps 28%; patch volatile (net +1.1, r5 +0.7). Patch axes (r5): general +0.7. Scale STR 0% / INT 70%. Path: Gauntlet of Thebes (team aura / support core); Gem of Isolation (zones & CC — Isolation slow/shred value); Damaru (Support path fit for kit profile). Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Gem of Isolation (mitigate, 2450g)
  3. Damaru (power, 2500g)
  4. Stone of Binding (mitigate, 2550g)
  5. Regrowth Striders (defense, 2550g)
  6. Midgardian Mail (counter, 2400g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Athena — A-tier (role rank #5, model 51.4)

*Magical · Intelligence scaling (STR 12.0% / INT 66.9%)*

Athena · Support · archetype «shield_support» (INT / magical). Kit effects: channel / cast time, big ult spike, dash / leap engage, ally buffs / auras, CC immunity in kit, lots of CC. Tags: anti_cc, burst, channel, gap_close, high_cc, long_cd, shield, team_buff. Style burst 72%/dps 28%; patch volatile (net -0.5, r5 -0.5). Patch axes (r5): general -0.6, damage +0.1. Scale STR 12% / INT 67%. Path: Prophetic Cloak (tenacity / anti-CC bulk); Amanita Charm (Support path fit for kit profile); Alchemist Coat (tenacity / anti-CC bulk). Actives 2/2 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Prophetic Cloak (defense, 2400g)
  2. Amanita Charm (defense, active, 2350g)
  3. Alchemist Coat (mitigate, 2350g)
  4. Phoenix Feather (mitigate, active, 2350g)
  5. Stone of Binding (mitigate, 2550g)
  6. Wyrmskin Hide (mitigate, 2600g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Ix Chel — A-tier (role rank #6, model 50.5)

*Magical · Intelligence scaling (STR 0% / INT 64.4%)*

Ix Chel · Support · archetype «heal_support» (INT / magical). Kit effects: channel / cast time, self heal / drain, heavy healing, pet / deployable, hard crowd control, ally buffs / auras. Tags: anti_cc, channel, dot, echo, hard_cc, heal, heavy_heal, high_cc. Style burst 49%/dps 51%; patch new (net -0.7, r5 -0.7). Patch axes (r5): damage -0.8, general +0.8, cooldown -0.7. Scale STR 0% / INT 64%. Path: Lotus Sickle (heal amp / team sustain); Gauntlet of Thebes (team aura / support core); Phoenix Feather (shield / phoenix-style bulk). Actives 1/1 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 1/1, pen ≈ 0.0):
  1. Lotus Sickle (power, 2150g)
  2. Gauntlet of Thebes (defense, 2200g)
  3. Phoenix Feather (mitigate, active, 2350g)
  4. Gem of Isolation (mitigate, 2450g)
  5. Stygian Anchor (counter, 2550g)
  6. Rod Of Asclepius (power, 2350g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Yemoja — A-tier (role rank #7, model 50.0)

*Magical · Intelligence scaling (STR 0% / INT 56.5%)*

Yemoja · Support · archetype «heal_support» (INT / magical). Kit effects: attack-speed steroid, heavy healing, hard crowd control, ally buffs / auras, lots of CC, multi-hit / ticks. Tags: as_steroid, burst, dot, hard_cc, heal, heavy_heal, high_cc, long_cd. Style burst 71%/dps 29%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): general +0.1, damage +0.0, survivability -0.0. Scale STR 0% / INT 56%. Path: Gauntlet of Thebes (team aura / support core); Lotus Sickle (heal amp / team sustain); Gem of Isolation (zones & CC — Isolation slow/shred value). Actives 0/1 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 0/1, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Lotus Sickle (power, 2150g)
  3. Gem of Isolation (mitigate, 2450g)
  4. Stygian Anchor (counter, 2550g)
  5. Midgardian Mail (counter, 2400g)
  6. Rod Of Asclepius (power, 2350g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Ares — B-tier (role rank #8, model 49.2)

*Magical · Intelligence scaling (STR 33.6% / INT 29.6%)*

Ares · Support · archetype «shield_support» (INT / magical). Kit effects: damage over time, channel / cast time, big ult spike, pet / deployable, hard crowd control, ally buffs / auras. Tags: anti_cc, burst, channel, dot, hard_cc, heal, heavy_dot, long_cd. Style burst 84%/dps 16%; patch volatile (net -0.5, r5 -0.5). Patch axes (r5): general -0.9, survivability +0.4, damage -0.3. Scale STR 34% / INT 30%. Path: Gauntlet of Thebes (team aura / support core); Shifter's Shield (offline hybrid tank); Alchemist Coat (tenacity / anti-CC bulk). Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Shifter's Shield (defense, 2750g)
  3. Alchemist Coat (mitigate, 2350g)
  4. Contagion (defense, 2400g)
  5. Gem of Isolation (mitigate, 2450g)
  6. Damaru (power, 2500g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Charon — B-tier (role rank #9, model 47.8)

*Magical · Intelligence scaling (STR 0% / INT 45.0%)*

Charon · Support · archetype «shield_support» (INT / magical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, burst combos. Tags: anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, mobile, pet_zone. Style burst 96%/dps 4%; patch rising (net +1.1, r5 +0.0). Patch axes (r5): damage +0.7, general +0.4. Scale STR 0% / INT 45%. Path: Gauntlet of Thebes (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk); Phoenix Feather (shield / phoenix-style bulk). Actives 1/2 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Alchemist Coat (mitigate, 2350g)
  3. Phoenix Feather (mitigate, active, 2350g)
  4. Magi's Cloak (defense, 2400g)
  5. Gem of Isolation (mitigate, 2450g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Sylvanus — B-tier (role rank #10, model 47.6)

*Magical · Intelligence scaling (STR 0% / INT 41.7%)*

Sylvanus · Support · archetype «heal_support» (INT / magical). Kit effects: damage over time, protection shred, execute / threshold, pet / deployable, hard crowd control, low mobility. Tags: dot, execute, hard_cc, heal, heavy_dot, high_cc, immobile, long_cd. Style burst 0%/dps 0%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): cooldown +0.0. Scale STR 0% / INT 42%. Path: Lotus Sickle (heal amp / team sustain); Gauntlet of Thebes (team aura / support core); Gem of Isolation (zones & CC — Isolation slow/shred value). Actives 0/1 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 0/1, pen ≈ 0.0):
  1. Lotus Sickle (power, 2150g)
  2. Gauntlet of Thebes (defense, 2200g)
  3. Gem of Isolation (mitigate, 2450g)
  4. Stone of Binding (mitigate, 2550g)
  5. Stygian Anchor (counter, 2550g)
  6. Rod Of Asclepius (power, 2350g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (42.0)

#### Bacchus — B-tier (role rank #11, model 47.2)

*Magical · Intelligence scaling (STR 30.6% / INT 24.7%)*

Bacchus · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, hard crowd control, dash / leap engage, burst combos, lots of CC, healing in kit. Tags: channel, gap_close, hard_cc, heal, high_cc, long_cd, utility. Style burst 100%/dps 0%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): general +0.0, damage +0.0, survivability +0.0. Scale STR 31% / INT 25%. Path: Amanita Charm (Support path fit for kit profile); Gauntlet of Thebes (team aura / support core); Prophetic Cloak (tenacity / anti-CC bulk). Actives 2/2 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Amanita Charm (defense, active, 2350g)
  2. Gauntlet of Thebes (defense, 2200g)
  3. Prophetic Cloak (defense, 2400g)
  4. Gem of Isolation (mitigate, 2450g)
  5. Stone of Binding (mitigate, 2550g)
  6. Doublet of Binding (mitigate, active, 2700g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Artio — B-tier (role rank #12, model 45.8)

*Magical · Hybrid scaling (STR 60.4% / INT 50.1%)*

Artio · Support · archetype «heal_support» (INT / magical). Kit effects: protection shred, channel / cast time, big ult spike, heavy healing, hard crowd control, ally buffs / auras. Tags: channel, hard_cc, heal, heavy_heal, high_cc, long_cd, prot_shred, team_buff. Style burst 59%/dps 41%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): general +0.1, damage +0.0, mana -0.0. Scale STR 60% / INT 50%. Path: Lotus Sickle (heal amp / team sustain); Gem of Isolation (zones & CC — Isolation slow/shred value); Stone of Binding (Stone of Binding — CC setup shred). Actives 1/1 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 1/1, pen ≈ 0.0):
  1. Lotus Sickle (power, 2150g)
  2. Gem of Isolation (mitigate, 2450g)
  3. Stone of Binding (mitigate, 2550g)
  4. Void Shield (defense, 2550g)
  5. Doublet of Binding (mitigate, active, 2700g)
  6. Rod Of Asclepius (power, 2350g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Khepri — B-tier (role rank #13, model 44.0)

*Magical · Intelligence scaling (STR 0% / INT 30.5%)*

Khepri · Support · archetype «shield_support» (INT / magical). Kit effects: execute / threshold, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, lots of CC. Tags: anti_cc, dot, execute, gap_close, hard_cc, high_cc, long_cd, shield. Style burst 0%/dps 0%; patch new (net +0.3, r5 +0.0). Patch axes (r5): utility +0.5, damage -0.3, general +0.0. Scale STR 0% / INT 30%. Path: Gauntlet of Thebes (team aura / support core); Shifter's Shield (offline hybrid tank); Phoenix Feather (shield / phoenix-style bulk). Actives 2/2 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Shifter's Shield (defense, 2750g)
  3. Phoenix Feather (mitigate, active, 2350g)
  4. Gem of Isolation (mitigate, 2450g)
  5. Stygian Anchor (counter, 2550g)
  6. Helm of Darkness (defense, active, 2700g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Atlas — C-tier (role rank #14, model 42.4)

*Magical · Intelligence scaling (STR 0% / INT 51.4%)*

Atlas · Support · archetype «lockdown_support» (INT / magical). Kit effects: protection shred, basic-attack kit, pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras. Tags: aa, burst, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 79%/dps 21%; patch falling (net -1.4, r5 -1.0). Patch axes (r5): mana -1.0. Scale STR 0% / INT 51%. Path: Gauntlet of Thebes (team aura / support core); Shifter's Shield (offline hybrid tank; patch falling — extra bulk/CDR); Gem of Isolation (zones & CC — Isolation slow/shred value). Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 2 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Shifter's Shield (defense, 2750g)
  3. Gem of Isolation (mitigate, 2450g)
  4. Stygian Anchor (counter, 2550g)
  5. Wyrmskin Hide (mitigate, 2600g)
  6. Midgardian Mail (counter, 2400g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Hel — C-tier (role rank #15, model 42.3)

*Magical · Intelligence scaling (STR 0% / INT 74.6%)*

Hel · Support · archetype «heal_support» (INT / magical). Kit effects: damage over time, attack-speed steroid, self heal / drain, ally buffs / auras, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, as_steroid, dot, heal, heavy_dot, self_sustain, team_buff. Style burst 42%/dps 58%; patch new (net +0.9, r5 +0.9). Patch axes (r5): general +0.9. Scale STR 0% / INT 75%. Path: Lotus Sickle (heal amp / team sustain); Gauntlet of Thebes (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk). Actives 0/1 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 0/1, pen ≈ 0.0):
  1. Lotus Sickle (power, 2150g)
  2. Gauntlet of Thebes (defense, 2200g)
  3. Alchemist Coat (mitigate, 2350g)
  4. Gem of Isolation (mitigate, 2450g)
  5. Midgardian Mail (counter, 2400g)
  6. Rod Of Asclepius (power, 2350g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (32.0)

#### Horus — C-tier (role rank #16, model 41.7)

*Physical · Strength scaling (STR 74.4% / INT 0%)*

Horus · Support · archetype «heal_support» (STR / physical). Kit effects: channel / cast time, self heal / drain, heavy healing, hard crowd control, dash / leap engage, ally buffs / auras. Tags: anti_cc, channel, gap_close, hard_cc, heal, heavy_heal, high_cc, long_cd. Style burst 30%/dps 70%; patch falling (net -6.0, r5 -5.5). Patch axes (r5): survivability -2.9, heal -1.2, cooldown -1.0. Scale STR 74% / INT 0%. Path: Gauntlet of Thebes (team aura / support core); Yogi's Necklace (Support path fit for kit profile); Shifter's Shield (offline hybrid tank; patch falling — extra bulk/CDR). Actives 0/1 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 0/1, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Yogi's Necklace (defense, 2250g)
  3. Shifter's Shield (defense, 2750g)
  4. Shield of the Phoenix (mitigate, 2400g)
  5. Stygian Anchor (counter, 2550g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Sobek — C-tier (role rank #17, model 39.7)

*Magical · Intelligence scaling (STR 0% / INT 50.0%)*

Sobek · Support · archetype «lockdown_support» (INT / magical). Kit effects: self heal / drain, execute / threshold, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, burst, dot, execute, gap_close, hard_cc, heal, high_cc. Style burst 81%/dps 19%; patch stable (net -0.4, r5 -0.3). Patch axes (r5): damage -0.5, utility +0.1. Scale STR 0% / INT 50%. Path: Gauntlet of Thebes (team aura / support core); Shifter's Shield (offline hybrid tank); Phoenix Feather (shield / phoenix-style bulk). Actives 1/2 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Shifter's Shield (defense, 2750g)
  3. Phoenix Feather (mitigate, active, 2350g)
  4. Gem of Isolation (mitigate, 2450g)
  5. Stone of Binding (mitigate, 2550g)
  6. Contagion (defense, 2400g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Cabrakan — C-tier (role rank #18, model 39.1)

*Magical · Hybrid scaling (STR 75.1% / INT 51.1%)*

Cabrakan · Support · archetype «shield_support» (INT / magical). Kit effects: channel / cast time, big ult spike, hard crowd control, ally buffs / auras, lots of CC, multi-hit / ticks. Tags: channel, hard_cc, heal, high_cc, long_cd, shield, team_buff, ult_nuke. Style burst 55%/dps 45%; patch falling (net -2.8, r5 -1.2). Patch axes (r5): damage -0.7, general -0.6, heal +0.1. Scale STR 75% / INT 51%. Path: Gauntlet of Thebes (team aura / support core); Shifter's Shield (offline hybrid tank; patch falling — extra bulk/CDR); Stampede (Support path fit for kit profile). Actives 2/2 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Shifter's Shield (defense, 2750g)
  3. Stampede (defense, active, 2400g)
  4. Gem of Isolation (mitigate, 2450g)
  5. Stone of Binding (mitigate, 2550g)
  6. Helm of Darkness (defense, active, 2700g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Guan Yu — D-tier (role rank #19, model 38.8)

*Physical · Strength scaling (STR 42.4% / INT 13.3%)*

Guan Yu · Support · archetype «heal_support» (STR / physical). Kit effects: damage over time, attack-speed steroid, self heal / drain, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, dot, gap_close, hard_cc, heal, heavy_dot, long_cd, pet_zone. Style burst 16%/dps 84%; patch volatile (net -1.6, r5 -0.1). Patch axes (r5): cooldown -1.7, attack_speed +1.6. Scale STR 42% / INT 13%. Path: Gauntlet of Thebes (team aura / support core); Phoenix Feather (shield / phoenix-style bulk); Gladiator's Shield (Support path fit for kit profile). Actives 1/1 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 1/1, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Phoenix Feather (mitigate, active, 2350g)
  3. Gladiator's Shield (defense, 2450g)
  4. Stygian Anchor (counter, 2550g)
  5. Stone of Binding (mitigate, 2550g)
  6. Mystical Mail (defense, 2550g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Geb — D-tier (role rank #20, model 35.2)

*Magical · Intelligence scaling (STR 0% / INT 36.3%)*

Geb · Support · archetype «shield_support» (INT / magical). Kit effects: hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, lots of CC, shields. Tags: anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, shield, team_buff. Style burst 67%/dps 33%; patch stable (net -0.8, r5 +0.0). Patch axes (r5): damage -0.4, survivability -0.3, crit -0.1. Scale STR 0% / INT 36%. Path: Gauntlet of Thebes (team aura / support core); Shifter's Shield (offline hybrid tank); Gem of Isolation (zones & CC — Isolation slow/shred value). Actives 1/2 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Shifter's Shield (defense, 2750g)
  3. Gem of Isolation (mitigate, 2450g)
  4. Stone of Binding (mitigate, 2550g)
  5. Helm of Darkness (defense, active, 2700g)
  6. Ethereal Staff (mitigate, 2550g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Aphrodite — D-tier (role rank #21, model 33.4)

*Magical · Intelligence scaling (STR 0% / INT 57.9%)*

Aphrodite · Support · archetype «heal_support» (INT / magical). Kit effects: big ult spike, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, burst, dot, gap_close, hard_cc, heal, long_cd, team_buff. Style burst 60%/dps 40%; patch falling (net -5.7, r5 -6.1). Patch axes (r5): damage -3.4, general -1.4, survivability -0.9. Scale STR 0% / INT 58%. Path: Lotus Sickle (heal amp / team sustain); Rod Of Asclepius (heal amp / team sustain); Shogun's Ofuda (Support path fit for kit profile). Actives 0/1 · pen ≈ 0. Soft high-SR inspiration on 3 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 0/1, pen ≈ 0.0):
  1. Lotus Sickle (power, 2150g)
  2. Rod Of Asclepius (power, 2350g)
  3. Shogun's Ofuda (mitigate, 2500g)
  4. Stygian Anchor (counter, 2550g)
  5. Stone of Binding (mitigate, 2550g)
  6. Genji's Guard (defense, 2350g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Cerberus — D-tier (role rank #22, model 17.8)

*Magical · Intelligence scaling (STR 0% / INT 42.6%)*

Cerberus · Support · archetype «lockdown_support» (INT / magical). Kit effects: self heal / drain, pet / deployable, hard crowd control, dash / leap engage, burst combos, lots of CC. Tags: dot, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, self_sustain. Style burst 100%/dps 0%; patch falling (net -3.9, r5 -2.9). Patch axes (r5): cooldown -2.0, damage -0.9. Scale STR 0% / INT 43%. Path: Gauntlet of Thebes (team aura / support core); Gem of Isolation (zones & CC — Isolation slow/shred value); Stone of Binding (Stone of Binding — CC setup shred). Actives 0/2 · pen ≈ 0. Soft high-SR inspiration on 1 item(s) (tracker.gg — not a meta copy).

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Gem of Isolation (mitigate, 2450g)
  3. Stone of Binding (mitigate, 2550g)
  4. Regrowth Striders (defense, 2550g)
  5. Xibalban Effigy (defense, 2750g)
  6. Spectral Armor (mitigate, 2300g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

---
