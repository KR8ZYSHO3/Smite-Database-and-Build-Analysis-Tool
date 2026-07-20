# SMITE 2 Conquest Builds — Statistically Weighted

God-first Conquest builds: each path is assembled from that god's ability kit (structured effects + tags + metrics + patch axes), archetype slot recipes, item-family matching, and per-item why lines. Optional data/kit_overrides.json force tags / prefer / ban items. Role cards explain the job only — they are NOT a full build. Carry/Mid backline + pen; Jungle ganks; Solo frontline bulk; Support peels. Shop actives ≤2 default (hard max 3). Damage roles enforce ≥10 matching pen.

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
**Common role items (not ordered as a build):** Titan's Bane, The Executioner, Avenging Blade, Jotunn's Revenge, Musashi's Dual Swords, Shifter's Shield, Freya's Tears, The Crusher

### God-specific kit builds (use these)

#### Xbalanque — S-tier (role rank #1, model 76.1)

*Physical · Strength scaling (STR 38.2% / INT 35.4%)*

Xbalanque · Carry · archetype «crit_adc» (STR / physical). Kit effects: damage over time, basic-attack kit, dash / leap engage, CC immunity in kit, multi-hit / ticks, sustained DPS. Tags: aa, anti_cc, dot, gap_close, heal, heavy_dot, long_cd, sustained. Style burst 23%/dps 77%; patch rising (net +1.9, r5 +1.7). Patch axes (r5): damage +1.7. Scale STR 38% / INT 35%. Path: Titan's Bane (% pen for physical tanks / late fights; patch rising — lean damage); Arondight (CDR + pen for gank/engage); Musashi's Dual Swords (attack speed / crit carry core; patch rising — lean damage). Pen: Titan's Bane. Actives 1/2 · pen ≈ 20.

- **Starter:** Death's Toll
- **Buy order** (actives 1/2, pen ≈ 20.0):
  1. Titan's Bane (pen, pen 20.0, 3100g)
  2. Arondight (power, active, 2650g)
  3. Musashi's Dual Swords (power, 2700g)
  4. Demon Blade (power, 2750g)
  5. Damaru (power, 2750g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Cupid — S-tier (role rank #2, model 75.6)

*Physical · Strength scaling (STR 116.6% / INT 83.6%)*

Cupid · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, attack-speed steroid, heavy healing, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, gap_close, hard_cc, heal, heavy_heal, long_cd, pet_zone, sustained. Style burst 42%/dps 58%; patch volatile (net +1.0, r5 +0.0). Patch axes (r5): damage +1.0, attack_speed +0.1, general -0.1. Scale STR 117% / INT 84%. Path: Jotunn's Revenge (CDR + pen for gank/engage); The Reaper (penetration required for damage role); Titan's Bane (% pen for physical tanks / late fights; damage buffed — power/pen). Pen: Jotunn's Revenge, The Reaper, Titan's Bane. Actives 0/2 · pen ≈ 35.

- **Starter:** Death's Toll
- **Buy order** (actives 0/2, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. The Reaper (pen, pen 10.0, 2600g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. Avenging Blade (power, 2650g)
  5. Deathbringer (power, 2900g)
  6. Gauntlet of Thebes (defense, 2200g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Danzaburou — S-tier (role rank #3, model 72.5)

*Physical · Hybrid scaling (STR 113.4% / INT 119.3%)*

Danzaburou · Carry · archetype «crit_adc» (STR / physical). Kit effects: channel / cast time, big ult spike, basic-attack kit, hard crowd control, CC immunity in kit, lots of CC. Tags: aa, anti_cc, burst, channel, dot, hard_cc, heal, high_cc. Style burst 72%/dps 28%; patch new (net +0.1, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 113% / INT 119%. Path: Heartseeker (stacking pen power for assassins); Titan's Bane (% pen for physical tanks / late fights); Bloodforge (lifesteal + power for execute/bruiser). Pen: Heartseeker, Titan's Bane, Avatar's Parashu. Actives 2/2 · pen ≈ 40.

- **Starter:** Death's Toll
- **Buy order** (actives 2/2, pen ≈ 40.0):
  1. Heartseeker (pen, pen 10.0, 3000g)
  2. Titan's Bane (pen, pen 20.0, 3100g)
  3. Bloodforge (power, active, 2550g)
  4. Avenging Blade (power, 2650g)
  5. Demon Blade (power, 2750g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Princess Bari — A-tier (role rank #4, model 70.3)

*Magical · Intelligence scaling (STR 80.1% / INT 110.3%)*

Princess Bari · Carry · archetype «ability_mage_adc» (INT / magical). Kit effects: big ult spike, pet / deployable, hard crowd control, ally buffs / auras, lots of CC, burst combos. Tags: burst, hard_cc, high_cc, long_cd, pet_zone, team_buff, ult_nuke. Style burst 69%/dps 31%; patch new (net +0.2, r5 +0.0). Patch axes (r5): general +0.3, cooldown -0.0, attack_speed -0.0. Scale STR 80% / INT 110%. Path: Chronos' Pendant (CDR core for spam / channel kits); Soul Gem (ability heal/proc for mages); Gem of Isolation (zones & CC — Isolation slow/shred value). Pen: Soul Gem, Gluttonous Grimoire, Spear of Desolation, Spear Of The Magus. Actives 0/2 · pen ≈ 35.

- **Starter:** Vampiric Shroud
- **Buy order** (actives 0/2, pen ≈ 35.0):
  1. Chronos' Pendant (power, 2400g)
  2. Soul Gem (power, pen 5.0, 2500g)
  3. Gem of Isolation (power, 2500g)
  4. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  5. Spear of Desolation (pen, pen 10.0, 2650g)
  6. Spear Of The Magus (pen, pen 10.0, 2700g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Cernunnos — A-tier (role rank #5, model 69.3)

*Physical · Strength scaling (STR 80.4% / INT 51.1%)*

Cernunnos · Carry · archetype «crit_adc» (STR / physical). Kit effects: protection shred, big ult spike, basic-attack kit, self heal / drain, hard crowd control, dash / leap engage. Tags: aa, dot, gap_close, hard_cc, heal, high_cc, long_cd, prot_shred. Style burst 30%/dps 70%; patch stable (net +0.5, r5 +0.0). Patch axes (r5): general +0.5, damage +0.0, cooldown +0.0. Scale STR 80% / INT 51%. Path: Hydra's Lament (CDR + pen for gank/engage); Devourer's Gauntlet (lifesteal stacking); Riptalon (attack speed / crit carry core). Pen: Riptalon, Titan's Bane. Actives 0/2 · pen ≈ 30.

- **Starter:** Death's Toll
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Hydra's Lament (power, 2450g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Musashi's Dual Swords (power, 2700g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Sol — A-tier (role rank #6, model 68.2)

*Magical · Intelligence scaling (STR 21.8% / INT 50.7%)*

Sol · Carry · archetype «dot_mage_adc» (INT / magical). Kit effects: damage over time, big ult spike, basic-attack kit, self heal / drain, ally buffs / auras, CC immunity in kit. Tags: aa, anti_cc, burst, dot, heal, heavy_dot, high_cc, long_cd. Style burst 61%/dps 39%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): damage -0.0, general -0.0, attack_speed -0.0. Scale STR 22% / INT 51%. Path: Rod Of Asclepius (heal amp / team sustain); Spear Of The Magus (multi-hit / shred — stacks Magus passive); Doom Orb (mana stack → power scaling). Pen: Spear Of The Magus, Doom Orb, The World Stone. Actives 1/2 · pen ≈ 30.

- **Starter:** Vampiric Shroud
- **Buy order** (actives 1/2, pen ≈ 30.0):
  1. Rod Of Asclepius (power, active, 2350g)
  2. Spear Of The Magus (pen, pen 10.0, 2700g)
  3. Doom Orb (pen, pen 10.0, 2700g)
  4. The World Stone (pen, pen 10.0, 2800g)
  5. Soul Reaver (power, 2950g)
  6. Magi's Cloak (defense, 2400g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Anhur — A-tier (role rank #7, model 68.1)

*Physical · Strength scaling (STR 121.5% / INT 0%)*

Anhur · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, basic-attack kit, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 49%/dps 51%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, pen +0.0, survivability +0.0. Scale STR 121% / INT 0%. Path: Pendulum Blade (penetration required for damage role); Titan's Bane (% pen for physical tanks / late fights); Runeforged Hammer (Carry path fit for kit profile). Pen: Pendulum Blade, Titan's Bane. Actives 1/2 · pen ≈ 30.

- **Starter:** Death's Toll
- **Buy order** (actives 1/2, pen ≈ 30.0):
  1. Pendulum Blade (pen, active, pen 10.0, 2750g)
  2. Titan's Bane (pen, pen 20.0, 3100g)
  3. Runeforged Hammer (power, 2550g)
  4. Avenging Blade (power, 2650g)
  5. Musashi's Dual Swords (power, 2700g)
  6. Demon Blade (power, 2750g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Neith — B-tier (role rank #8, model 66.4)

*Physical · Hybrid scaling (STR 63.3% / INT 76.7%)*

Neith · Carry · archetype «crit_adc» (STR / physical). Kit effects: channel / cast time, big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, lots of CC. Tags: as_steroid, burst, channel, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 67%/dps 33%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): general +0.1, utility -0.0, attack_speed -0.0. Scale STR 63% / INT 77%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); Riptalon (attack speed / crit carry core). Pen: Jotunn's Revenge, Riptalon, The Crusher. Actives 1/2 · pen ≈ 25.

- **Starter:** Death's Toll
- **Buy order** (actives 1/2, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. The Crusher (pen, pen 10.0, 2800g)
  5. Death Metal (power, active, 2600g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Chiron — B-tier (role rank #9, model 65.0)

*Physical · Strength scaling (STR 99.9% / INT 0%)*

Chiron · Carry · archetype «crit_adc» (STR / physical). Kit effects: protection shred, channel / cast time, big ult spike, basic-attack kit, pet / deployable, dash / leap engage. Tags: aa, burst, channel, dot, gap_close, heal, high_cc, long_cd. Style burst 70%/dps 30%; patch new (net -0.3, r5 +0.0). Patch axes (r5): general -0.3, utility +0.0. Scale STR 100% / INT 0%. Path: Chandra's Grace (team aura / support core); Riptalon (attack speed / crit carry core); Titan's Bane (% pen for physical tanks / late fights). Pen: Riptalon, Titan's Bane. Actives 0/2 · pen ≈ 30.

- **Starter:** Death's Toll
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Riptalon (pen, pen 10.0, 2700g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. The Executioner (power, 2550g)
  5. Musashi's Dual Swords (power, 2700g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Nut — B-tier (role rank #10, model 64.4)

*Magical · Intelligence scaling (STR 80.3% / INT 130.9%)*

Nut · Carry · archetype «aa_mage_adc» (INT / magical). Kit effects: big ult spike, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: aa, anti_cc, burst, gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 75%/dps 25%; patch falling (net -1.4, r5 +0.0). Patch axes (r5): general -0.9, damage -0.5. Scale STR 80% / INT 131%. Path: Soul Gem (ability heal/proc for mages); Bracer of The Abyss (Carry path fit for kit profile); Gluttonous Grimoire (sustain / omnivamp line). Pen: Soul Gem, Gluttonous Grimoire, Obsidian Shard, Rod of Tahuti. Actives 0/2 · pen ≈ 40.

- **Starter:** Vampiric Shroud
- **Buy order** (actives 0/2, pen ≈ 40.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Bracer of The Abyss (power, 2500g)
  3. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Soul Reaver (power, 2950g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Izanami — B-tier (role rank #11, model 60.1)

*Physical · Hybrid scaling (STR 92.9% / INT 84.5%)*

Izanami · Carry · archetype «crit_adc» (STR / physical). Kit effects: protection shred, big ult spike, basic-attack kit, attack-speed steroid, pet / deployable, hard crowd control. Tags: aa, as_steroid, dot, gap_close, hard_cc, heal, long_cd, pet_zone. Style burst 35%/dps 65%; patch new (net -0.2, r5 -0.2). Patch axes (r5): general -0.2. Scale STR 93% / INT 84%. Path: Heartseeker (stacking pen power for assassins); Titan's Bane (% pen for physical tanks / late fights); Runeforged Hammer (Carry path fit for kit profile). Pen: Heartseeker, Titan's Bane. Actives 0/2 · pen ≈ 30.

- **Starter:** Death's Toll
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Heartseeker (pen, pen 10.0, 3000g)
  2. Titan's Bane (pen, pen 20.0, 3100g)
  3. Runeforged Hammer (power, 2550g)
  4. Musashi's Dual Swords (power, 2700g)
  5. Demon Blade (power, 2750g)
  6. Void Shield (defense, 2550g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Medusa — B-tier (role rank #12, model 58.0)

*Physical · Hybrid scaling (STR 64.2% / INT 63.9%)*

Medusa · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, as_steroid, burst, dot, gap_close, hard_cc, heal, long_cd. Style burst 76%/dps 24%; patch volatile (net +1.4, r5 +0.0). Patch axes (r5): cooldown +0.5, damage +0.5, survivability +0.3. Scale STR 64% / INT 64%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); Heartseeker (stacking pen power for assassins). Pen: Jotunn's Revenge, Heartseeker. Actives 1/2 · pen ≈ 15.

- **Starter:** Death's Toll
- **Buy order** (actives 1/2, pen ≈ 15.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. Heartseeker (pen, pen 10.0, 3000g)
  4. Death Metal (power, active, 2600g)
  5. Musashi's Dual Swords (power, 2700g)
  6. Prophetic Cloak (defense, 2400g)
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
**Common role items (not ordered as a build):** Obsidian Shard, Gluttonous Grimoire, The Executioner, Jotunn's Revenge, Shifter's Shield, Freya's Tears, Spear Of The Magus, Jade Scepter

### God-specific kit builds (use these)

#### Princess Bari — S-tier (role rank #1, model 70.3)

*Magical · Intelligence scaling (STR 80.1% / INT 110.3%)*

Princess Bari · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, pet / deployable, hard crowd control, ally buffs / auras, lots of CC, burst combos. Tags: burst, hard_cc, high_cc, long_cd, pet_zone, team_buff, ult_nuke. Style burst 69%/dps 31%; patch new (net +0.2, r5 +0.0). Patch axes (r5): general +0.3, cooldown -0.0, attack_speed -0.0. Scale STR 80% / INT 110%. Path: Chronos' Pendant (CDR core for spam / channel kits); Spear of Desolation (flat pen + CDR for ability burst); Spear Of The Magus (multi-hit / shred — stacks Magus passive). Pen: Spear of Desolation, Spear Of The Magus, The World Stone, Obsidian Shard. Actives 0/2 · pen ≈ 50.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 50.0):
  1. Chronos' Pendant (power, 2400g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. Spear Of The Magus (pen, pen 10.0, 2700g)
  4. The World Stone (pen, pen 10.0, 2800g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Ra — S-tier (role rank #2, model 69.0)

*Magical · Intelligence scaling (STR 0% / INT 106.2%)*

Ra · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, pet / deployable, ally buffs / auras, multi-hit / ticks, burst combos, damage over time. Tags: burst, dot, heal, long_cd, pet_zone, team_buff, ult_nuke. Style burst 69%/dps 31%; patch stable (net +0.7, r5 +0.0). Patch axes (r5): general +0.6, damage +0.1, survivability +0.0. Scale STR 0% / INT 106%. Path: Divine Ruin (anti-heal + pen for healing/sustain kits); Soul Gem (ability heal/proc for mages); Gluttonous Grimoire (sustain / omnivamp line). Pen: Soul Gem, Gluttonous Grimoire, Spear of Desolation, The Cosmic Horror, Obsidian Shard. Actives 0/2 · pen ≈ 55.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 55.0):
  1. Divine Ruin (counter, 2500g)
  2. Soul Gem (power, pen 5.0, 2500g)
  3. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  4. Spear of Desolation (pen, pen 10.0, 2650g)
  5. The Cosmic Horror (pen, pen 10.0, 2650g)
  6. Obsidian Shard (pen, pen 20.0, 3050g)
- **Relics:** Purification Beads (30.0), Aegis of Acceleration (30.0)

#### Kukulkan — S-tier (role rank #3, model 68.3)

*Magical · Intelligence scaling (STR 0% / INT 85.4%)*

Kukulkan · Mid · archetype «mana_mage» (INT / magical). Kit effects: big ult spike, mana → power passive, pet / deployable, dash / leap engage, CC immunity in kit, lots of CC. Tags: anti_cc, burst, dot, gap_close, high_cc, long_cd, mana_stack, pet_zone. Style burst 66%/dps 34%; patch rising (net +0.9, r5 +1.4). Patch axes (r5): damage +1.4. Scale STR 0% / INT 85%. Path: Soul Gem (ability heal/proc for mages); Spear of Desolation (flat pen + CDR for ability burst; patch rising — lean damage); The World Stone (penetration required for damage role). Pen: Soul Gem, Spear of Desolation, The World Stone, Obsidian Shard, Rod of Tahuti. Actives 0/2 · pen ≈ 50.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 50.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. The World Stone (pen, pen 10.0, 2800g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Soul Reaver (power, 2950g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Sol — A-tier (role rank #4, model 68.2)

*Magical · Intelligence scaling (STR 21.8% / INT 50.7%)*

Sol · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, big ult spike, basic-attack kit, self heal / drain, ally buffs / auras, CC immunity in kit. Tags: aa, anti_cc, burst, dot, heal, heavy_dot, high_cc, long_cd. Style burst 61%/dps 39%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): damage -0.0, general -0.0, attack_speed -0.0. Scale STR 22% / INT 51%. Path: Chronos' Pendant (CDR core for spam / channel kits); Gluttonous Grimoire (sustain / omnivamp line); Spear of Desolation (flat pen + CDR for ability burst). Pen: Gluttonous Grimoire, Spear of Desolation, Obsidian Shard. Actives 0/2 · pen ≈ 40.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 40.0):
  1. Chronos' Pendant (power, 2400g)
  2. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Soul Reaver (power, 2950g)
  6. Genji's Guard (defense, 2350g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Aphrodite — A-tier (role rank #5, model 67.3)

*Magical · Intelligence scaling (STR 0% / INT 102.0%)*

Aphrodite · Mid · archetype «burst_mage» (INT / magical). Kit effects: big ult spike, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, burst, dot, gap_close, hard_cc, heal, long_cd, team_buff. Style burst 60%/dps 40%; patch volatile (net +1.1, r5 +0.1). Patch axes (r5): heal +0.1. Scale STR 0% / INT 102%. Path: Chronos' Pendant (CDR core for spam / channel kits); Lifebinder (heal amp / team sustain); Gluttonous Grimoire (sustain / omnivamp line). Pen: Gluttonous Grimoire, Spear of Desolation, Spear Of The Magus, Rod of Tahuti. Actives 1/2 · pen ≈ 35.

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 35.0):
  1. Chronos' Pendant (power, 2400g)
  2. Lifebinder (power, active, 2400g)
  3. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  4. Spear of Desolation (pen, pen 10.0, 2650g)
  5. Spear Of The Magus (pen, pen 10.0, 2700g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Neith — A-tier (role rank #6, model 66.4)

*Physical · Hybrid scaling (STR 63.3% / INT 76.7%)*

Neith · Mid · archetype «channel_mage» (STR / physical). Kit effects: channel / cast time, big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, lots of CC. Tags: as_steroid, burst, channel, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 67%/dps 33%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): general +0.1, utility -0.0, attack_speed -0.0. Scale STR 63% / INT 77%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); Riptalon (attack speed / crit carry core). Pen: Jotunn's Revenge, Riptalon, The Crusher, Titan's Bane. Actives 1/2 · pen ≈ 45.

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 45.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. The Crusher (pen, pen 10.0, 2800g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Arondight (power, active, 2650g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Nut — A-tier (role rank #7, model 64.4)

*Magical · Intelligence scaling (STR 80.3% / INT 130.9%)*

Nut · Mid · archetype «burst_mage» (INT / magical). Kit effects: big ult spike, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: aa, anti_cc, burst, gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 75%/dps 25%; patch falling (net -1.4, r5 +0.0). Patch axes (r5): general -0.9, damage -0.5. Scale STR 80% / INT 131%. Path: Soul Gem (ability heal/proc for mages); Gem of Isolation (zones & CC — Isolation slow/shred value); The World Stone (penetration required for damage role). Pen: Soul Gem, The World Stone, Obsidian Shard. Actives 0/2 · pen ≈ 35.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 35.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Gem of Isolation (power, 2500g)
  3. The World Stone (pen, pen 10.0, 2800g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Soul Reaver (power, 2950g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Baron Samedi — A-tier (role rank #8, model 64.3)

*Magical · Intelligence scaling (STR 0% / INT 69.6%)*

Baron Samedi · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, channel / cast time, execute / threshold, pet / deployable, hard crowd control, ally buffs / auras. Tags: burst, channel, dot, execute, hard_cc, heal, heavy_dot, high_cc. Style burst 71%/dps 29%; patch volatile (net +1.1, r5 +0.0). Patch axes (r5): heal +0.9, general +0.3, damage -0.1. Scale STR 0% / INT 70%. Path: Bancroft's Talon (self-sustain power (missing HP)); Soul Gem (ability heal/proc for mages); Gluttonous Grimoire (sustain / omnivamp line). Pen: Soul Gem, Gluttonous Grimoire, Spear Of The Magus, Obsidian Shard. Actives 0/2 · pen ≈ 45.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 45.0):
  1. Bancroft's Talon (power, 2300g)
  2. Soul Gem (power, pen 5.0, 2500g)
  3. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### The Morrigan — B-tier (role rank #9, model 63.8)

*Magical · Intelligence scaling (STR 0% / INT 142.6%)*

The Morrigan · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, pet / deployable, hard crowd control, damage over time, long cooldowns, zones / linger. Tags: dot, hard_cc, long_cd, pet_zone, ult_nuke. Style burst 48%/dps 52%; patch stable (net +0.4, r5 +0.0). Patch axes (r5): utility +0.0. Scale STR 0% / INT 143%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Divine Ruin (anti-heal + pen for healing/sustain kits); Soul Gem (ability heal/proc for mages). Pen: Soul Gem, Gluttonous Grimoire, Spear Of The Magus, Obsidian Shard. Actives 0/2 · pen ≈ 45.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 45.0):
  1. Gem of Isolation (power, 2500g)
  2. Divine Ruin (counter, 2500g)
  3. Soul Gem (power, pen 5.0, 2500g)
  4. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  5. Spear Of The Magus (pen, pen 10.0, 2700g)
  6. Obsidian Shard (pen, pen 20.0, 3050g)
- **Relics:** Purification Beads (30.0), Aegis of Acceleration (30.0)

#### Eset — B-tier (role rank #10, model 63.4)

*Magical · Intelligence scaling (STR 0% / INT 52.7%)*

Eset · Mid · archetype «channel_mage» (INT / magical). Kit effects: channel / cast time, basic-attack kit, hard crowd control, ally buffs / auras, lots of CC, multi-hit / ticks. Tags: aa, burst, channel, hard_cc, heal, high_cc, long_cd, shield. Style burst 86%/dps 14%; patch volatile (net +0.0, r5 +0.7). Patch axes (r5): damage +0.7. Scale STR 0% / INT 53%. Path: Bancroft's Talon (self-sustain power (missing HP)); Rod Of Asclepius (heal amp / team sustain); Chronos' Pendant (CDR core for spam / channel kits). Pen: Gluttonous Grimoire, Spear Of The Magus, The World Stone. Actives 1/2 · pen ≈ 30.

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 30.0):
  1. Bancroft's Talon (power, 2300g)
  2. Rod Of Asclepius (power, active, 2350g)
  3. Chronos' Pendant (power, 2400g)
  4. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  5. Spear Of The Magus (pen, pen 10.0, 2700g)
  6. The World Stone (pen, pen 10.0, 2800g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Hecate — B-tier (role rank #11, model 60.5)

*Magical · Intelligence scaling (STR 0% / INT 70.3%)*

Hecate · Mid · archetype «channel_mage» (INT / magical). Kit effects: channel / cast time, hard crowd control, dash / leap engage, ally buffs / auras, burst combos, shields. Tags: burst, channel, gap_close, hard_cc, heal, long_cd, shield, team_buff. Style burst 57%/dps 43%; patch stable (net -0.4, r5 +0.0). Patch axes (r5): general -0.5, damage +0.0, survivability +0.0. Scale STR 0% / INT 70%. Path: Soul Gem (ability heal/proc for mages); Gem of Isolation (zones & CC — Isolation slow/shred value); Gluttonous Grimoire (sustain / omnivamp line). Pen: Soul Gem, Gluttonous Grimoire, Obsidian Shard, Rod of Tahuti. Actives 0/2 · pen ≈ 40.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 40.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Gem of Isolation (power, 2500g)
  3. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Typhon’s Heart (power, 2600g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Poseidon — B-tier (role rank #12, model 59.1)

*Magical · Intelligence scaling (STR 0% / INT 100.4%)*

Poseidon · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, basic-attack kit, attack-speed steroid, pet / deployable, hard crowd control, burst combos. Tags: aa, as_steroid, burst, dot, hard_cc, high_cc, long_cd, pet_zone. Style burst 92%/dps 8%; patch volatile (net +1.3, r5 +0.0). Patch axes (r5): damage +1.3, cooldown -0.0, general +0.0. Scale STR 0% / INT 100%. Path: Divine Ruin (anti-heal + pen for healing/sustain kits); Gluttonous Grimoire (sustain / omnivamp line); Spear of Desolation (flat pen + CDR for ability burst; damage buffed — power/pen). Pen: Gluttonous Grimoire, Spear of Desolation, Obsidian Shard, Rod of Tahuti. Actives 0/2 · pen ≈ 45.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 45.0):
  1. Divine Ruin (counter, 2500g)
  2. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Soul Reaver (power, 2950g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

---

## Jungle

Conquest jungle — job is ganks: Bumba clear, burst pen, CDR, Blink/mobility relics, enough HP to invade. Not a full-tank solo.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| pen | 22% |
| cdr | 16% |
| str | 14% |
| int | 12% |
| hp | 10% |
| as | 8% |
| ls | 6% |
| crit | 4% |
| pprot | 4% |
| mprot | 4% |

### Role job (not a full build)

This is the Jungle job description + common items — not a complete build. Open a god below for a kit-specific 1 starter + 6 buy order (actives ≤2, hard max 3).

**Typical starter:** Bumba's Cudgel
**Priority stats:** pen, cdr, str, int, hp
**Common role items (not ordered as a build):** Obsidian Shard, Gluttonous Grimoire, The Executioner, Titan's Bane, Jotunn's Revenge, Shifter's Shield, Soul Gem

### God-specific kit builds (use these)

#### Ne Zha — S-tier (role rank #1, model 75.1)

*Physical · Strength scaling (STR 147.9% / INT 0%)*

Ne Zha · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: protection shred, big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, as_steroid, gap_close, hard_cc, heal, long_cd, mobile, prot_shred. Style burst 44%/dps 56%; patch new (net -0.7, r5 +0.0). Patch axes (r5): damage -1.0, general +0.3, utility +0.0. Scale STR 148% / INT 0%. Path: Devourer's Gauntlet (lifesteal stacking); Heartseeker (stacking pen power for assassins); Titan's Bane (% pen for physical tanks / late fights). Pen: Heartseeker, Titan's Bane. Actives 1/3 · pen ≈ 30.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 1/3, pen ≈ 30.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Heartseeker (pen, pen 10.0, 3000g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. Bloodforge (power, active, 2550g)
  5. Avenging Blade (power, 2650g)
  6. Prophetic Cloak (defense, 2400g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Tsukuyomi — S-tier (role rank #2, model 73.6)

*Physical · Strength scaling (STR 158.7% / INT 119.2%)*

Tsukuyomi · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: big ult spike, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit, high mobility. Tags: aa, anti_cc, burst, gap_close, hard_cc, heal, long_cd, mobile. Style burst 65%/dps 35%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): general +0.2, damage -0.2, utility +0.0. Scale STR 159% / INT 119%. Path: Hydra's Lament (CDR + pen for gank/engage); Riptalon (attack speed / crit carry core); Heartseeker (stacking pen power for assassins). Pen: Riptalon, Heartseeker, Titan's Bane. Actives 0/3 · pen ≈ 40.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 0/3, pen ≈ 40.0):
  1. Hydra's Lament (power, 2450g)
  2. Riptalon (pen, pen 10.0, 2700g)
  3. Heartseeker (pen, pen 10.0, 3000g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Mantle Of Discord (mitigate, 2600g)
  6. Demon Blade (power, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Mordred — S-tier (role rank #3, model 73.3)

*Physical · Strength scaling (STR 77.5% / INT 45.8%)*

Mordred · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: damage over time, channel / cast time, big ult spike, attack-speed steroid, self heal / drain, heavy healing. Tags: anti_cc, as_steroid, burst, channel, dot, gap_close, hard_cc, heal. Style burst 58%/dps 42%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): survivability +0.0, general -0.0, heal +0.0. Scale STR 77% / INT 46%. Path: Jotunn's Revenge (CDR + pen for gank/engage); The Reaper (penetration required for damage role); Titan's Bane (% pen for physical tanks / late fights). Pen: Jotunn's Revenge, The Reaper, Titan's Bane. Actives 1/3 · pen ≈ 35.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. The Reaper (pen, pen 10.0, 2600g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. Arondight (power, active, 2650g)
  5. Avenging Blade (power, 2650g)
  6. Genji's Guard (defense, 2350g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Cernunnos — A-tier (role rank #4, model 69.3)

*Physical · Strength scaling (STR 80.4% / INT 51.1%)*

Cernunnos · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: protection shred, big ult spike, basic-attack kit, self heal / drain, hard crowd control, dash / leap engage. Tags: aa, dot, gap_close, hard_cc, heal, high_cc, long_cd, prot_shred. Style burst 30%/dps 70%; patch stable (net +0.5, r5 +0.0). Patch axes (r5): general +0.5, damage +0.0, cooldown +0.0. Scale STR 80% / INT 51%. Path: Devourer's Gauntlet (lifesteal stacking); The Reaper (penetration required for damage role); The Executioner (AA prot shred). Pen: The Reaper, Avatar's Parashu. Actives 2/3 · pen ≈ 20.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 2/3, pen ≈ 20.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. The Reaper (pen, pen 10.0, 2600g)
  3. The Executioner (power, 2550g)
  4. Bloodforge (power, active, 2550g)
  5. Breastplate of Valor (defense, 2400g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Ratatoskr — A-tier (role rank #5, model 68.6)

*Physical · Strength scaling (STR 89.7% / INT 0%)*

Ratatoskr · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: big ult spike, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC, burst combos. Tags: anti_cc, burst, gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 75%/dps 25%; patch rising (net +2.2, r5 +1.5). Patch axes (r5): survivability +2.2, general -0.9, cooldown -0.7. Scale STR 90% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Pendulum Blade (penetration required for damage role); Heartseeker (stacking pen power for assassins). Pen: Jotunn's Revenge, Pendulum Blade, Heartseeker, Titan's Bane. Actives 2/3 · pen ≈ 45.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 2/3, pen ≈ 45.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Pendulum Blade (pen, active, pen 10.0, 2750g)
  3. Heartseeker (pen, pen 10.0, 3000g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Stone of Binding (mitigate, 2550g)
  6. Arondight (power, active, 2650g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Awilix — A-tier (role rank #6, model 67.9)

*Physical · Strength scaling (STR 64.0% / INT 0%)*

Awilix · Jungle · archetype «bruiser_jungle» (STR / physical). Kit effects: attack-speed steroid, pet / deployable, hard crowd control, dash / leap engage, lots of CC, high mobility. Tags: as_steroid, gap_close, hard_cc, high_cc, long_cd, mobile, pet_zone, sustained. Style burst 22%/dps 78%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, utility +0.0, cooldown +0.0. Scale STR 64% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Pendulum Blade (penetration required for damage role); Heartseeker (penetration required for damage role). Pen: Jotunn's Revenge, Pendulum Blade, Heartseeker, Titan's Bane. Actives 2/3 · pen ≈ 45.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 45.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Pendulum Blade (pen, active, pen 10.0, 2750g)
  3. Heartseeker (pen, pen 10.0, 3000g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Arondight (power, active, 2650g)
  6. Avenging Blade (power, 2650g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Thanatos — A-tier (role rank #7, model 67.5)

*Physical · Strength scaling (STR 56.1% / INT 0%)*

Thanatos · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: protection shred, self heal / drain, execute / threshold, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, burst, execute, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 62%/dps 38%; patch rising (net +1.2, r5 +1.0). Patch axes (r5): general +1.0. Scale STR 56% / INT 0%. Path: Devourer's Gauntlet (lifesteal stacking); The Crusher (penetration required for damage role); Bloodforge (lifesteal + power for execute/bruiser). Pen: The Crusher, Avatar's Parashu. Actives 3/3 · pen ≈ 20.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 3/3, pen ≈ 20.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. The Crusher (pen, pen 10.0, 2800g)
  3. Bloodforge (power, active, 2550g)
  4. The Executioner (power, 2550g)
  5. Eye of Erebus (defense, active, 2600g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Gilgamesh — B-tier (role rank #8, model 65.7)

*Physical · Strength scaling (STR 72.8% / INT 0%)*

Gilgamesh · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, lots of CC, burst combos. Tags: burst, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, team_buff. Style burst 77%/dps 23%; patch new (net -0.3, r5 +0.0). Patch axes (r5): damage -1.3, general +0.9, mana +0.1. Scale STR 73% / INT 0%. Path: Chandra's Grace (team aura / support core); Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Titan's Bane. Actives 1/3 · pen ≈ 25.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 25.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Jotunn's Revenge (power, pen 5.0, 2400g)
  3. Hydra's Lament (power, 2450g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Bloodforge (power, active, 2550g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Odin — B-tier (role rank #9, model 65.4)

*Physical · Strength scaling (STR 65.2% / INT 34.1%)*

Odin · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: big ult spike, basic-attack kit, attack-speed steroid, shields, hard crowd control, dash / leap engage. Tags: aa, as_steroid, burst, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 64%/dps 36%; patch volatile (net +1.1, r5 +0.1). Patch axes (r5): damage +0.1, survivability +0.1. Scale STR 65% / INT 34%. Path: The Crusher (penetration required for damage role); Heartseeker (stacking pen power for assassins); Titan's Bane (% pen for physical tanks / late fights). Pen: The Crusher, Heartseeker, Titan's Bane. Actives 2/3 · pen ≈ 40.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 2/3, pen ≈ 40.0):
  1. The Crusher (pen, pen 10.0, 2800g)
  2. Heartseeker (pen, pen 10.0, 3000g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. Arondight (power, active, 2650g)
  5. Sanguine Lash (power, active, 2650g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Fenrir — B-tier (role rank #10, model 64.8)

*Physical · Strength scaling (STR 97.4% / INT 0%)*

Fenrir · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: channel / cast time, big ult spike, basic-attack kit, self heal / drain, hard crowd control, dash / leap engage. Tags: aa, anti_cc, channel, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 20%/dps 80%; patch volatile (net -0.3, r5 +0.8). Patch axes (r5): damage +0.8. Scale STR 97% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); Tekko-Kagi (penetration required for damage role). Pen: Jotunn's Revenge, Tekko-Kagi, The Crusher, Titan's Bane. Actives 0/3 · pen ≈ 45.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 0/3, pen ≈ 45.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. Tekko-Kagi (pen, pen 10.0, 2700g)
  4. The Crusher (pen, pen 10.0, 2800g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Avenging Blade (power, 2650g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Achilles — B-tier (role rank #11, model 62.7)

*Physical · Strength scaling (STR 82.9% / INT 0%)*

Achilles · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: big ult spike, basic-attack kit, self heal / drain, execute / threshold, shields, hard crowd control. Tags: aa, anti_cc, execute, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 30%/dps 70%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, attack_speed +0.0, survivability +0.0. Scale STR 83% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); Heartseeker (stacking pen power for assassins). Pen: Jotunn's Revenge, Heartseeker, Titan's Bane. Actives 2/3 · pen ≈ 35.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. Heartseeker (pen, pen 10.0, 3000g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Arondight (power, active, 2650g)
  6. Eye of Erebus (defense, active, 2600g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Nemesis — B-tier (role rank #12, model 58.8)

*Physical · Strength scaling (STR 102.2% / INT 70.3%)*

Nemesis · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: big ult spike, dash / leap engage, shields, healing in kit, long cooldowns. Tags: gap_close, heal, long_cd, shield, ult_nuke. Style burst 52%/dps 48%; patch stable (net +0.2, r5 +0.0). Patch axes (r5): general +0.1, damage +0.0, survivability +0.0. Scale STR 102% / INT 70%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Hydra's Lament (CDR + pen for gank/engage); Tekko-Kagi (penetration required for damage role). Pen: Tekko-Kagi. Actives 1/3 · pen ≈ 10.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 1/3, pen ≈ 10.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Hydra's Lament (power, 2450g)
  3. Tekko-Kagi (pen, pen 10.0, 2700g)
  4. Bloodforge (power, active, 2550g)
  5. Avenging Blade (power, 2650g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Blink Rune (32.4), Purification Beads (30.0)

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
**Common role items (not ordered as a build):** Shifter's Shield, Freya's Tears, Genji's Guard, Breastplate of Valor, Sphere of Negation, Draconic Scale, Stone of Binding, Berserker's Shield

### God-specific kit builds (use these)

#### Sun Wukong — S-tier (role rank #1, model 78.4)

*Physical · Strength scaling (STR 113.9% / INT 45.7%)*

Sun Wukong · Solo · archetype «bruiser_solo» (STR / physical). Kit effects: big ult spike, execute / threshold, hard crowd control, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, dot, execute, hard_cc, heal, high_cc, long_cd. Style burst 65%/dps 35%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 114% / INT 46%. Path: Chandra's Grace (team aura / support core); Stygian Anchor (peel / anti-dive anchor); Avenging Blade (attack speed / crit carry core). Actives 0/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Stygian Anchor (counter, 2550g)
  3. Avenging Blade (power, 2650g)
  4. Breastplate of Valor (defense, 2400g)
  5. Prophetic Cloak (defense, 2400g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Jormungandr — S-tier (role rank #2, model 73.4)

*Magical · Intelligence scaling (STR 27.9% / INT 51.4%)*

Jormungandr · Solo · archetype «mage_solo» (INT / magical). Kit effects: channel / cast time, big ult spike, hard crowd control, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, channel, dot, hard_cc, heal, high_cc, long_cd. Style burst 63%/dps 37%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): general -0.2, utility +0.1, damage +0.0. Scale STR 28% / INT 51%. Path: Rod Of Asclepius (heal amp / team sustain); Gluttonous Grimoire (sustain / omnivamp line); Stone of Binding (Stone of Binding — CC setup shred). Pen: Gluttonous Grimoire. Actives 2/2 · pen ≈ 10.

- **Starter:** Warrior's Axe
- **Buy order** (actives 2/2, pen ≈ 10.0):
  1. Rod Of Asclepius (power, active, 2350g)
  2. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  3. Stone of Binding (mitigate, 2550g)
  4. Amanita Charm (defense, active, 2350g)
  5. Shifter's Shield (defense, 2650g)
  6. Draconic Scale (defense, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Mordred — S-tier (role rank #3, model 73.3)

*Physical · Strength scaling (STR 77.5% / INT 45.8%)*

Mordred · Solo · archetype «sustain_solo» (STR / physical). Kit effects: damage over time, channel / cast time, big ult spike, attack-speed steroid, self heal / drain, heavy healing. Tags: anti_cc, as_steroid, burst, channel, dot, gap_close, hard_cc, heal. Style burst 58%/dps 42%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): survivability +0.0, general -0.0, heal +0.0. Scale STR 77% / INT 46%. Path: Chandra's Grace (team aura / support core); Phoenix Feather (shield / phoenix-style bulk); Leviathan's Hide (Solo path fit for kit profile). Actives 1/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Phoenix Feather (mitigate, active, 2400g)
  3. Leviathan's Hide (mitigate, 2500g)
  4. Wyrmskin Hide (mitigate, 2600g)
  5. Contagion (defense, 2400g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Osiris — A-tier (role rank #4, model 72.8)

*Physical · Strength scaling (STR 65.9% / INT 0%)*

Osiris · Solo · archetype «tank_solo» (STR / physical). Kit effects: basic-attack kit, attack-speed steroid, pet / deployable, hard crowd control, dash / leap engage, lots of CC. Tags: aa, as_steroid, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone. Style burst 26%/dps 74%; patch stable (net -0.3, r5 +0.0). Patch axes (r5): general -0.2, attack_speed -0.1, damage -0.0. Scale STR 66% / INT 0%. Path: Chandra's Grace (team aura / support core); Stone of Binding (Stone of Binding — CC setup shred); Stygian Anchor (peel / anti-dive anchor). Actives 1/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Stone of Binding (mitigate, 2550g)
  3. Stygian Anchor (counter, 2550g)
  4. Doublet of Binding (mitigate, active, 2700g)
  5. Eye of Providence (defense, 2300g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Chaac — A-tier (role rank #5, model 71.3)

*Physical · Strength scaling (STR 97.1% / INT 44.1%)*

Chaac · Solo · archetype «sustain_solo» (STR / physical). Kit effects: channel / cast time, big ult spike, self heal / drain, pet / deployable, hard crowd control, dash / leap engage. Tags: anti_cc, channel, dot, gap_close, hard_cc, heal, long_cd, pet_zone. Style burst 39%/dps 61%; patch stable (net +0.8, r5 +0.0). Patch axes (r5): damage +0.4, general +0.4, utility -0.0. Scale STR 97% / INT 44%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Stone of Binding (Stone of Binding — CC setup shred); Wyrmskin Hide (Solo path fit for kit profile). Actives 0/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Gem of Isolation (power, 2500g)
  2. Stone of Binding (mitigate, 2550g)
  3. Wyrmskin Hide (mitigate, 2600g)
  4. Gauntlet of Thebes (defense, 2200g)
  5. Magi's Cloak (defense, 2400g)
  6. Draconic Scale (defense, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Hua Mulan — A-tier (role rank #6, model 70.4)

*Physical · Strength scaling (STR 94.0% / INT 0%)*

Hua Mulan · Solo · archetype «bruiser_solo» (STR / physical). Kit effects: big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: anti_cc, as_steroid, burst, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 80%/dps 20%; patch stable (net -0.2, r5 +0.0). Patch axes (r5): general -0.2, cooldown -0.0, attack_speed +0.0. Scale STR 94% / INT 0%. Path: Wyrmskin Hide (Solo path fit for kit profile); Genji's Guard (magic prot + CDR for mages); Prophetic Cloak (tenacity / anti-CC bulk). Actives 0/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Wyrmskin Hide (mitigate, 2600g)
  2. Genji's Guard (defense, 2350g)
  3. Prophetic Cloak (defense, 2400g)
  4. Contagion (defense, 2400g)
  5. Regrowth Striders (defense, 2550g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Bellona — B-tier (role rank #7, model 67.6)

*Physical · Strength scaling (STR 69.9% / INT 0%)*

Bellona · Solo · archetype «sustain_solo» (STR / physical). Kit effects: basic-attack kit, self heal / drain, shields, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, burst, gap_close, hard_cc, heal, heavy_shield, high_cc. Style burst 64%/dps 36%; patch volatile (net +0.4, r5 +0.6). Patch axes (r5): damage +0.6. Scale STR 70% / INT 0%. Path: Chandra's Grace (team aura / support core); Shield of the Phoenix (shield / phoenix-style bulk); Sanguine Lash (Solo path fit for kit profile). Actives 1/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Shield of the Phoenix (mitigate, 2400g)
  3. Sanguine Lash (power, active, 2650g)
  4. Breastplate of Valor (defense, 2400g)
  5. Magi's Cloak (defense, 2400g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Gilgamesh — B-tier (role rank #8, model 65.7)

*Physical · Strength scaling (STR 72.8% / INT 0%)*

Gilgamesh · Solo · archetype «bruiser_solo» (STR / physical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, lots of CC, burst combos. Tags: burst, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, team_buff. Style burst 77%/dps 23%; patch new (net -0.3, r5 +0.0). Patch axes (r5): damage -1.3, general +0.9, mana +0.1. Scale STR 73% / INT 0%. Path: Shield of the Phoenix (shield / phoenix-style bulk); Runeforged Hammer (Solo path fit for kit profile); Doublet of Binding (Stone of Binding — CC setup shred). Actives 3/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 3/3, pen ≈ 0.0):
  1. Shield of the Phoenix (mitigate, 2400g)
  2. Runeforged Hammer (power, 2550g)
  3. Doublet of Binding (mitigate, active, 2700g)
  4. Freya's Tears (defense, 2600g)
  5. Eye of Erebus (defense, active, 2600g)
  6. Heartwood Charm (defense, active, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Amaterasu — B-tier (role rank #9, model 65.6)

*Physical · Hybrid scaling (STR 47.0% / INT 51.3%)*

Amaterasu · Solo · archetype «sustain_solo» (STR / physical). Kit effects: big ult spike, self heal / drain, hard crowd control, dash / leap engage, CC immunity in kit, sustained DPS. Tags: anti_cc, dot, gap_close, hard_cc, heal, long_cd, self_sustain, shield. Style burst 2%/dps 98%; patch volatile (net +1.3, r5 +0.6). Patch axes (r5): damage +0.6. Scale STR 47% / INT 51%. Path: Kinetic Cuirass (Solo path fit for kit profile); Contagion (team anti-heal aura); Gladiator's Shield (Solo path fit for kit profile). Actives 1/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Kinetic Cuirass (mitigate, 2400g)
  2. Contagion (defense, 2400g)
  3. Gladiator's Shield (defense, 2450g)
  4. Freya's Tears (defense, 2600g)
  5. Heartwood Charm (defense, active, 2650g)
  6. Draconic Scale (defense, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Odin — B-tier (role rank #10, model 65.4)

*Physical · Strength scaling (STR 65.2% / INT 34.1%)*

Odin · Solo · archetype «shield_solo» (STR / physical). Kit effects: big ult spike, basic-attack kit, attack-speed steroid, shields, hard crowd control, dash / leap engage. Tags: aa, as_steroid, burst, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 64%/dps 36%; patch volatile (net +1.1, r5 +0.1). Patch axes (r5): damage +0.1, survivability +0.1. Scale STR 65% / INT 34%. Path: Shield of the Phoenix (shield / phoenix-style bulk); Eye of the Storm (Solo path fit for kit profile); Doublet of Binding (Stone of Binding — CC setup shred). Actives 3/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 3/3, pen ≈ 0.0):
  1. Shield of the Phoenix (mitigate, 2400g)
  2. Eye of the Storm (power, active, 2500g)
  3. Doublet of Binding (mitigate, active, 2700g)
  4. Gauntlet of Thebes (defense, 2200g)
  5. Glorious Pridwen (defense, active, 2550g)
  6. Freya's Tears (defense, 2600g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Xing Tian — B-tier (role rank #11, model 64.3)

*Magical · Intelligence scaling (STR 0% / INT 57.1%)*

Xing Tian · Solo · archetype «mage_solo» (INT / magical). Kit effects: damage over time, channel / cast time, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, channel, dot, gap_close, hard_cc, heal, heavy_dot. Style burst 65%/dps 35%; patch rising (net +1.0, r5 +1.0). Patch axes (r5): general +1.0. Scale STR 0% / INT 57%. Path: Shield of the Phoenix (shield / phoenix-style bulk); Gem of Isolation (zones & CC — Isolation slow/shred value); Gluttonous Grimoire (sustain / omnivamp line). Pen: Gluttonous Grimoire. Actives 1/2 · pen ≈ 10.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/2, pen ≈ 10.0):
  1. Shield of the Phoenix (mitigate, 2400g)
  2. Gem of Isolation (power, 2500g)
  3. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  4. Doublet of Binding (mitigate, active, 2700g)
  5. Contagion (defense, 2400g)
  6. Magi's Cloak (defense, 2400g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Achilles — C-tier (role rank #12, model 62.7)

*Physical · Strength scaling (STR 82.9% / INT 0%)*

Achilles · Solo · archetype «sustain_solo» (STR / physical). Kit effects: big ult spike, basic-attack kit, self heal / drain, execute / threshold, shields, hard crowd control. Tags: aa, anti_cc, execute, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 30%/dps 70%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, attack_speed +0.0, survivability +0.0. Scale STR 83% / INT 0%. Path: Shield of the Phoenix (shield / phoenix-style bulk); Kinetic Cuirass (Solo path fit for kit profile); Phoenix Feather (shield / phoenix-style bulk). Actives 2/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 2/3, pen ≈ 0.0):
  1. Shield of the Phoenix (mitigate, 2400g)
  2. Kinetic Cuirass (mitigate, 2400g)
  3. Phoenix Feather (mitigate, active, 2400g)
  4. Stone of Binding (mitigate, 2550g)
  5. Gauntlet of Thebes (defense, 2200g)
  6. Eye of Erebus (defense, active, 2600g)
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
**Common role items (not ordered as a build):** Spectral Armor, Freya's Tears, Genji's Guard, Breastplate of Valor, Sphere of Negation, Shifter's Shield, Stone of Binding, Umbral Link

### God-specific kit builds (use these)

#### Jormungandr — S-tier (role rank #1, model 73.4)

*Magical · Intelligence scaling (STR 27.9% / INT 51.4%)*

Jormungandr · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, big ult spike, hard crowd control, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, channel, dot, hard_cc, heal, high_cc, long_cd. Style burst 63%/dps 37%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): general -0.2, utility +0.1, damage +0.0. Scale STR 28% / INT 51%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Alchemist Coat (tenacity / anti-CC bulk); Rod Of Asclepius (heal amp / team sustain). Actives 2/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Alchemist Coat (mitigate, 2350g)
  3. Rod Of Asclepius (power, active, 2350g)
  4. Lifebinder (power, active, 2400g)
  5. Spirit Robe (mitigate, 2500g)
  6. Draconic Scale (defense, 2700g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Charon — S-tier (role rank #2, model 70.5)

*Magical · Intelligence scaling (STR 0% / INT 45.0%)*

Charon · Support · archetype «shield_support» (INT / magical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, burst combos. Tags: anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, mobile, pet_zone. Style burst 96%/dps 4%; patch rising (net +2.6, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 0% / INT 45%. Path: Chandra's Grace (team aura / support core); Shield of the Phoenix (shield / phoenix-style bulk); Gem of Isolation (zones & CC — Isolation slow/shred value). Pen: Spear Of The Magus. Actives 1/2 · pen ≈ 10.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 10.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Shield of the Phoenix (mitigate, 2400g)
  3. Gem of Isolation (power, 2500g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Stone of Binding (mitigate, 2550g)
  6. Heartwood Charm (defense, active, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Aphrodite — S-tier (role rank #3, model 67.3)

*Magical · Intelligence scaling (STR 0% / INT 102.0%)*

Aphrodite · Support · archetype «heal_support» (INT / magical). Kit effects: big ult spike, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, burst, dot, gap_close, hard_cc, heal, long_cd, team_buff. Style burst 60%/dps 40%; patch volatile (net +1.1, r5 +0.1). Patch axes (r5): heal +0.1. Scale STR 0% / INT 102%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Gem of Isolation (zones & CC — Isolation slow/shred value); Leviathan's Hide (Support path fit for kit profile). Pen: Obsidian Shard. Actives 1/2 · pen ≈ 20.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 20.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Gem of Isolation (power, 2500g)
  3. Leviathan's Hide (mitigate, 2500g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Doublet of Binding (mitigate, active, 2700g)
  6. Freya's Tears (defense, 2600g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Yemoja — A-tier (role rank #4, model 65.3)

*Magical · Intelligence scaling (STR 0% / INT 56.5%)*

Yemoja · Support · archetype «heal_support» (INT / magical). Kit effects: basic-attack kit, attack-speed steroid, heavy healing, hard crowd control, ally buffs / auras, lots of CC. Tags: aa, as_steroid, burst, dot, hard_cc, heal, heavy_heal, high_cc. Style burst 70%/dps 30%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): damage -0.1, general +0.1, survivability -0.0. Scale STR 0% / INT 56%. Path: Rod Of Asclepius (heal amp / team sustain); Shield of the Phoenix (shield / phoenix-style bulk); Doublet of Binding (Stone of Binding — CC setup shred). Actives 2/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Rod Of Asclepius (power, active, 2350g)
  2. Shield of the Phoenix (mitigate, 2400g)
  3. Doublet of Binding (mitigate, active, 2700g)
  4. Genji's Guard (defense, 2350g)
  5. Contagion (defense, 2400g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Ares — A-tier (role rank #5, model 64.4)

*Magical · Intelligence scaling (STR 33.6% / INT 29.6%)*

Ares · Support · archetype «heal_support» (INT / magical). Kit effects: damage over time, channel / cast time, big ult spike, pet / deployable, hard crowd control, ally buffs / auras. Tags: anti_cc, burst, channel, dot, hard_cc, heal, heavy_dot, long_cd. Style burst 84%/dps 16%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.2, damage +0.0, survivability -0.0. Scale STR 34% / INT 30%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Chandra's Grace (team aura / support core); Obsidian Shard (% pen for magical tanks / late fights). Pen: Obsidian Shard. Actives 1/2 · pen ≈ 20.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 20.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Obsidian Shard (pen, pen 20.0, 3050g)
  4. Mantle Of Discord (mitigate, 2600g)
  5. Gauntlet of Thebes (defense, 2200g)
  6. Heartwood Charm (defense, active, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Xing Tian — A-tier (role rank #6, model 64.3)

*Magical · Intelligence scaling (STR 0% / INT 57.1%)*

Xing Tian · Support · archetype «lockdown_support» (INT / magical). Kit effects: damage over time, channel / cast time, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, channel, dot, gap_close, hard_cc, heal, heavy_dot. Style burst 65%/dps 35%; patch rising (net +1.0, r5 +1.0). Patch axes (r5): general +1.0. Scale STR 0% / INT 57%. Path: Alchemist Coat (tenacity / anti-CC bulk); Rod Of Asclepius (heal amp / team sustain); Stone of Binding (Stone of Binding — CC setup shred). Actives 2/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Alchemist Coat (mitigate, 2350g)
  2. Rod Of Asclepius (power, active, 2350g)
  3. Stone of Binding (mitigate, 2550g)
  4. Staff of Myrddin (power, active, 2900g)
  5. Genji's Guard (defense, 2350g)
  6. Magi's Cloak (defense, 2400g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Baron Samedi — A-tier (role rank #7, model 64.3)

*Magical · Intelligence scaling (STR 0% / INT 69.6%)*

Baron Samedi · Support · archetype «heal_support» (INT / magical). Kit effects: damage over time, channel / cast time, execute / threshold, pet / deployable, hard crowd control, ally buffs / auras. Tags: burst, channel, dot, execute, hard_cc, heal, heavy_dot, high_cc. Style burst 71%/dps 29%; patch volatile (net +1.1, r5 +0.0). Patch axes (r5): heal +0.9, general +0.3, damage -0.1. Scale STR 0% / INT 70%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Rod Of Asclepius (heal amp / team sustain); Alchemist Coat (tenacity / anti-CC bulk). Actives 2/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Rod Of Asclepius (power, active, 2350g)
  3. Alchemist Coat (mitigate, 2350g)
  4. Gauntlet of Thebes (defense, 2200g)
  5. Breastplate of Valor (defense, 2400g)
  6. Heartwood Charm (defense, active, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Ymir — B-tier (role rank #8, model 64.0)

*Magical · Intelligence scaling (STR 12.3% / INT 117.7%)*

Ymir · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, big ult spike, basic-attack kit, pet / deployable, hard crowd control, low mobility. Tags: aa, anti_cc, burst, channel, hard_cc, high_cc, immobile, long_cd. Style burst 60%/dps 40%; patch volatile (net +1.8, r5 +0.0). Patch axes (r5): damage +1.0, survivability +0.4, general +0.3. Scale STR 12% / INT 118%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Gem of Focus (ability CDR / focus passive); Doublet of Binding (Stone of Binding — CC setup shred). Actives 2/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Gem of Isolation (power, 2500g)
  2. Gem of Focus (power, 2550g)
  3. Doublet of Binding (mitigate, active, 2700g)
  4. Resolute Mantle (mitigate, 2750g)
  5. Breastplate of Valor (defense, 2400g)
  6. Heartwood Charm (defense, active, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (42.0)

#### Atlas — B-tier (role rank #9, model 64.0)

*Magical · Intelligence scaling (STR 0% / INT 51.4%)*

Atlas · Support · archetype «lockdown_support» (INT / magical). Kit effects: protection shred, pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, lots of CC. Tags: burst, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone, prot_shred. Style burst 79%/dps 21%; patch new (net -0.8, r5 -0.4). Patch axes (r5): utility -0.8, general +0.7, attack_speed -0.5. Scale STR 0% / INT 51%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Gem of Isolation (zones & CC — Isolation slow/shred value); Spirit Robe (Support path fit for kit profile). Pen: Spear Of The Magus. Actives 0/2 · pen ≈ 10.

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 10.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Gem of Isolation (power, 2500g)
  3. Spirit Robe (mitigate, 2500g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Freya's Tears (defense, 2600g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Athena — B-tier (role rank #10, model 62.9)

*Magical · Intelligence scaling (STR 12.0% / INT 66.9%)*

Athena · Support · archetype «shield_support» (INT / magical). Kit effects: channel / cast time, big ult spike, basic-attack kit, dash / leap engage, ally buffs / auras, CC immunity in kit. Tags: aa, anti_cc, burst, channel, gap_close, high_cc, long_cd, shield. Style burst 72%/dps 28%; patch stable (net +0.2, r5 +0.0). Patch axes (r5): general +0.2, cooldown +0.0, damage +0.0. Scale STR 12% / INT 67%. Path: Chandra's Grace (team aura / support core); Rod Of Asclepius (heal amp / team sustain); Lifebinder (heal amp / team sustain). Actives 2/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Rod Of Asclepius (power, active, 2350g)
  3. Lifebinder (power, active, 2400g)
  4. Gem of Isolation (power, 2500g)
  5. Stone of Binding (mitigate, 2550g)
  6. Mantle Of Discord (mitigate, 2600g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Cabrakan — B-tier (role rank #11, model 61.6)

*Magical · Hybrid scaling (STR 75.1% / INT 51.2%)*

Cabrakan · Support · archetype «heal_support» (INT / magical). Kit effects: channel / cast time, big ult spike, basic-attack kit, hard crowd control, ally buffs / auras, lots of CC. Tags: aa, channel, hard_cc, heal, high_cc, long_cd, shield, team_buff. Style burst 54%/dps 46%; patch falling (net -2.2, r5 -2.3). Patch axes (r5): survivability -1.0, damage -0.9, heal -0.3. Scale STR 75% / INT 51%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Chandra's Grace (team aura / support core); Doublet of Binding (Stone of Binding — CC setup shred). Pen: Rod of Tahuti. Actives 2/2 · pen ≈ 5.

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 5.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Doublet of Binding (mitigate, active, 2700g)
  4. Rod of Tahuti (power, pen 5.0, 3000g)
  5. Prophetic Cloak (defense, 2400g)
  6. Heartwood Charm (defense, active, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Guan Yu — B-tier (role rank #12, model 61.4)

*Physical · Strength scaling (STR 42.4% / INT 13.3%)*

Guan Yu · Support · archetype «heal_support» (STR / physical). Kit effects: damage over time, attack-speed steroid, self heal / drain, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, dot, gap_close, hard_cc, heal, heavy_dot, long_cd, pet_zone. Style burst 15%/dps 85%; patch stable (net +0.2, r5 +0.0). Patch axes (r5): general +0.3, survivability -0.1, cooldown -0.1. Scale STR 42% / INT 13%. Path: Chandra's Grace (team aura / support core); Spectral Armor (mitigate enemy crit (Spectral line)); Stone of Binding (Stone of Binding — CC setup shred). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Spectral Armor (mitigate, 2300g)
  3. Stone of Binding (mitigate, 2550g)
  4. Breastplate of Valor (defense, 2400g)
  5. Contagion (defense, 2400g)
  6. Heartwood Charm (defense, active, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

---
