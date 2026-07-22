# SMITE 2 Conquest Builds — Statistically Weighted

God-first Conquest builds: each path is assembled from that god's ability kit (structured effects + tags + metrics + patch axes), the items:overall tier ladder (S/A preferred, C/D soft-penalized, role-gated so tank S-tiers don't invade Mid), archetype slot recipes, item-family matching, and per-item why lines. Hard damage-type bans (no mage toys on physical / no hunter toys on mages). Optional data/kit_overrides.json force tags / prefer / ban items. Role cards explain the job only — they are NOT a full build. Carry/Mid backline + pen; Jungle ganks; Solo frontline bulk; Support peels. Shop actives ≤2 default (hard max 3). Damage roles enforce ≥10 matching pen.

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
**Common role items (not ordered as a build):** The Executioner, Jotunn's Revenge, Titan's Bane, Avenging Blade, Musashi's Dual Swords, Shifter's Shield, Freya's Tears, Tyrfing

### God-specific kit builds (use these)

#### Xbalanque — S-tier (role rank #1, model 72.8)

*Physical · Strength scaling (STR 38.2% / INT 35.4%)*

Xbalanque · Carry · archetype «crit_adc» (STR / physical). Kit effects: damage over time, basic-attack kit, dash / leap engage, CC immunity in kit, multi-hit / ticks, sustained DPS. Tags: aa, anti_cc, dot, gap_close, heal, heavy_dot, long_cd, sustained. Style burst 23%/dps 77%; patch rising (net +1.9, r5 +1.7). Patch axes (r5): damage +1.7. Scale STR 38% / INT 35%. Path: Odysseus' Bow (Carry path fit for kit profile); Avenging Blade (attack speed / crit carry core; patch rising — lean damage); Riptalon (attack speed / crit carry core; patch rising — lean damage). Pen: Riptalon, Titan's Bane. Actives 0/2 · pen ≈ 30.

- **Starter:** Death's Toll
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Odysseus' Bow (power, 2450g)
  2. Avenging Blade (power, 2650g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Demon Blade (power, 2750g)
  6. Prophetic Cloak (defense, 2400g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Cupid — S-tier (role rank #2, model 70.6)

*Physical · Strength scaling (STR 116.6% / INT 83.6%)*

Cupid · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, attack-speed steroid, heavy healing, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, gap_close, hard_cc, heal, heavy_heal, long_cd, pet_zone, sustained. Style burst 42%/dps 58%; patch volatile (net +1.0, r5 +0.0). Patch axes (r5): damage +1.0, attack_speed +0.1, general -0.1. Scale STR 117% / INT 84%. Path: Death Metal (Carry path fit for kit profile); Arondight (CDR + pen for gank/engage); Titan's Bane (% pen for physical tanks / late fights; damage buffed — power/pen). Pen: Titan's Bane. Actives 2/2 · pen ≈ 20.

- **Starter:** Gilded Arrow
- **Buy order** (actives 2/2, pen ≈ 20.0):
  1. Death Metal (power, active, 2600g)
  2. Arondight (power, active, 2650g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. Demon Blade (power, 2750g)
  5. Deathbringer (power, 2900g)
  6. Chandra's Grace (mitigate, 2300g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Danzaburou — S-tier (role rank #3, model 70.0)

*Physical · Hybrid scaling (STR 113.4% / INT 119.3%)*

Danzaburou · Carry · archetype «crit_adc» (STR / physical). Kit effects: channel / cast time, big ult spike, basic-attack kit, hard crowd control, CC immunity in kit, lots of CC. Tags: aa, anti_cc, burst, channel, dot, hard_cc, heal, high_cc. Style burst 72%/dps 28%; patch new (net +0.1, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 113% / INT 119%. Path: Devourer's Gauntlet (lifesteal stacking); Death Metal (Carry path fit for kit profile); Riptalon (attack speed / crit carry core). Pen: Riptalon, Heartseeker, Titan's Bane, Avatar's Parashu. Actives 2/2 · pen ≈ 50.

- **Starter:** Gilded Arrow
- **Buy order** (actives 2/2, pen ≈ 50.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Death Metal (power, active, 2600g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. Heartseeker (pen, pen 10.0, 3000g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Cernunnos — A-tier (role rank #4, model 66.4)

*Physical · Strength scaling (STR 80.4% / INT 51.1%)*

Cernunnos · Carry · archetype «crit_adc» (STR / physical). Kit effects: protection shred, big ult spike, basic-attack kit, self heal / drain, hard crowd control, dash / leap engage. Tags: aa, dot, gap_close, hard_cc, heal, high_cc, long_cd, prot_shred. Style burst 30%/dps 70%; patch stable (net +0.5, r5 +0.0). Patch axes (r5): general +0.5, damage +0.0, cooldown +0.0. Scale STR 80% / INT 51%. Path: Bloodforge (lifesteal + power for execute/bruiser); Arondight (CDR + pen for gank/engage); Riptalon (attack speed / crit carry core). Pen: Riptalon, Heartseeker, Titan's Bane. Actives 2/2 · pen ≈ 40.

- **Starter:** Gilded Arrow
- **Buy order** (actives 2/2, pen ≈ 40.0):
  1. Bloodforge (power, active, 2550g)
  2. Arondight (power, active, 2650g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. Heartseeker (pen, pen 10.0, 3000g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Princess Bari — A-tier (role rank #5, model 66.2)

*Magical · Intelligence scaling (STR 80.1% / INT 110.3%)*

Princess Bari · Carry · archetype «ability_mage_adc» (INT / magical). Kit effects: big ult spike, pet / deployable, hard crowd control, ally buffs / auras, lots of CC, burst combos. Tags: burst, hard_cc, high_cc, long_cd, pet_zone, team_buff, ult_nuke. Style burst 69%/dps 31%; patch new (net +0.2, r5 +0.0). Patch axes (r5): general +0.3, cooldown -0.0, attack_speed -0.0. Scale STR 80% / INT 110%. Path: Soul Gem (ability heal/proc for mages); Gem of Isolation (zones & CC — Isolation slow/shred value); Spear of Desolation (flat pen + CDR for ability burst). Pen: Soul Gem, Spear of Desolation, Spear Of The Magus. Actives 0/2 · pen ≈ 25.

- **Starter:** Sands Of Time
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Gem of Isolation (power, 2500g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Genji's Guard (defense, 2350g)
  6. Wish-Granting Pearl (power, 3550g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Anhur — A-tier (role rank #6, model 65.8)

*Physical · Strength scaling (STR 121.5% / INT 0%)*

Anhur · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, basic-attack kit, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 49%/dps 51%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, pen +0.0, survivability +0.0. Scale STR 121% / INT 0%. Path: Lernaean Bow (Carry path fit for kit profile); Avenging Blade (attack speed / crit carry core); Arondight (CDR + pen for gank/engage). Pen: Titan's Bane. Actives 2/2 · pen ≈ 20.

- **Starter:** Death's Toll
- **Buy order** (actives 2/2, pen ≈ 20.0):
  1. Lernaean Bow (power, active, 2500g)
  2. Avenging Blade (power, 2650g)
  3. Arondight (power, active, 2650g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Demon Blade (power, 2750g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Sol — A-tier (role rank #7, model 64.0)

*Magical · Intelligence scaling (STR 21.8% / INT 50.7%)*

Sol · Carry · archetype «dot_mage_adc» (INT / magical). Kit effects: damage over time, big ult spike, basic-attack kit, self heal / drain, ally buffs / auras, CC immunity in kit. Tags: aa, anti_cc, burst, dot, heal, heavy_dot, high_cc, long_cd. Style burst 61%/dps 39%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): damage -0.0, general -0.0, attack_speed -0.0. Scale STR 22% / INT 51%. Path: Bancroft's Talon (self-sustain power (missing HP)); Soul Gem (ability heal/proc for mages); Gluttonous Grimoire (sustain / omnivamp line). Pen: Soul Gem, Gluttonous Grimoire, Spear Of The Magus. Actives 0/2 · pen ≈ 25.

- **Starter:** Vampiric Shroud
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Bancroft's Talon (power, 2300g)
  2. Soul Gem (power, pen 5.0, 2500g)
  3. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Soul Reaver (power, 2950g)
  6. Chandra's Grace (mitigate, 2300g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Chiron — B-tier (role rank #8, model 62.9)

*Physical · Strength scaling (STR 99.9% / INT 0%)*

Chiron · Carry · archetype «crit_adc» (STR / physical). Kit effects: protection shred, channel / cast time, big ult spike, basic-attack kit, pet / deployable, dash / leap engage. Tags: aa, burst, channel, dot, gap_close, heal, high_cc, long_cd. Style burst 70%/dps 30%; patch new (net -0.3, r5 +0.0). Patch axes (r5): general -0.3, utility +0.0. Scale STR 100% / INT 0%. Path: The Executioner (AA prot shred); Runeforged Hammer (Carry path fit for kit profile); Titan's Bane (% pen for physical tanks / late fights). Pen: Titan's Bane, Avatar's Parashu. Actives 1/2 · pen ≈ 30.

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 30.0):
  1. The Executioner (power, 2550g)
  2. Runeforged Hammer (power, 2550g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. Deathbringer (power, 2900g)
  5. Void Shield (defense, 2550g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Neith — B-tier (role rank #9, model 62.9)

*Physical · Hybrid scaling (STR 63.3% / INT 76.7%)*

Neith · Carry · archetype «crit_adc» (STR / physical). Kit effects: channel / cast time, big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, lots of CC. Tags: as_steroid, burst, channel, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 67%/dps 33%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): general +0.1, utility -0.0, attack_speed -0.0. Scale STR 63% / INT 77%. Path: Arondight (CDR + pen for gank/engage); Musashi's Dual Swords (attack speed / crit carry core); Riptalon (attack speed / crit carry core). Pen: Riptalon, Heartseeker. Actives 1/2 · pen ≈ 20.

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 20.0):
  1. Arondight (power, active, 2650g)
  2. Musashi's Dual Swords (power, 2700g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. Heartseeker (pen, pen 10.0, 3000g)
  5. Demon Blade (power, 2750g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Nut — B-tier (role rank #10, model 61.8)

*Magical · Intelligence scaling (STR 80.3% / INT 130.9%)*

Nut · Carry · archetype «aa_mage_adc» (INT / magical). Kit effects: big ult spike, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: aa, anti_cc, burst, gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 75%/dps 25%; patch falling (net -1.4, r5 +0.0). Patch axes (r5): general -0.9, damage -0.5. Scale STR 80% / INT 131%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Bracer of The Abyss (Carry path fit for kit profile); Spear Of The Magus (multi-hit / shred — stacks Magus passive). Pen: Spear Of The Magus, Obsidian Shard, Dreamer's Idol. Actives 1/2 · pen ≈ 40.

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 40.0):
  1. Gem of Isolation (power, 2500g)
  2. Bracer of The Abyss (power, 2500g)
  3. Spear Of The Magus (pen, pen 10.0, 2700g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Stone of Binding (mitigate, 2550g)
  6. Dreamer's Idol (pen, active, pen 10.0, 3500g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Izanami — B-tier (role rank #11, model 59.8)

*Physical · Hybrid scaling (STR 92.9% / INT 84.5%)*

Izanami · Carry · archetype «crit_adc» (STR / physical). Kit effects: protection shred, big ult spike, basic-attack kit, attack-speed steroid, pet / deployable, hard crowd control. Tags: aa, as_steroid, dot, gap_close, hard_cc, heal, long_cd, pet_zone. Style burst 35%/dps 65%; patch new (net -0.2, r5 -0.2). Patch axes (r5): general -0.2. Scale STR 93% / INT 84%. Path: Musashi's Dual Swords (attack speed / crit carry core); Riptalon (attack speed / crit carry core); The Crusher (penetration required for damage role). Pen: Riptalon, The Crusher, Titan's Bane, Avatar's Parashu. Actives 1/2 · pen ≈ 50.

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 50.0):
  1. Musashi's Dual Swords (power, 2700g)
  2. Riptalon (pen, pen 10.0, 2700g)
  3. The Crusher (pen, pen 10.0, 2800g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Freya's Tears (defense, 2600g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Artemis — B-tier (role rank #12, model 58.6)

*Physical · Strength scaling (STR 67.1% / INT 0%)*

Artemis · Carry · archetype «crit_adc» (STR / physical). Kit effects: basic-attack kit, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: aa, anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 10%/dps 90%; patch stable (net -0.2, r5 +0.0). Patch axes (r5): general -0.2, heal -0.0, attack_speed +0.0. Scale STR 67% / INT 0%. Path: Rage (Carry path fit for kit profile); Arondight (CDR + pen for gank/engage); Titan's Bane (% pen for physical tanks / late fights). Pen: Titan's Bane. Actives 1/2 · pen ≈ 20.

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 20.0):
  1. Rage (power, 2450g)
  2. Arondight (power, active, 2650g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. Demon Blade (power, 2750g)
  5. Deathbringer (power, 2900g)
  6. Magi's Cloak (defense, 2400g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Medusa — C-tier (role rank #13, model 56.3)

*Physical · Hybrid scaling (STR 64.2% / INT 63.9%)*

Medusa · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, as_steroid, burst, dot, gap_close, hard_cc, heal, long_cd. Style burst 76%/dps 24%; patch volatile (net +1.4, r5 +0.0). Patch axes (r5): cooldown +0.5, damage +0.5, survivability +0.3. Scale STR 64% / INT 64%. Path: Runeforged Hammer (Carry path fit for kit profile); Death Metal (Carry path fit for kit profile); Arondight (CDR + pen for gank/engage). Pen: Tekko-Kagi, Heartseeker. Actives 2/2 · pen ≈ 20.

- **Starter:** Gilded Arrow
- **Buy order** (actives 2/2, pen ≈ 20.0):
  1. Runeforged Hammer (power, 2550g)
  2. Death Metal (power, active, 2600g)
  3. Arondight (power, active, 2650g)
  4. Tekko-Kagi (pen, pen 10.0, 2700g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Demon Blade (power, 2750g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Ishtar — C-tier (role rank #14, model 53.7)

*Physical · Strength scaling (STR 50.7% / INT 0%)*

Ishtar · Carry · archetype «crit_adc» (STR / physical). Kit effects: attack-speed steroid, execute / threshold, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, as_steroid, execute, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 14%/dps 86%; patch volatile (net -1.6, r5 -0.8). Patch axes (r5): damage -0.8, general +0.0. Scale STR 51% / INT 0%. Path: Odysseus' Bow (Carry path fit for kit profile); Bloodforge (lifesteal + power for execute/bruiser); Musashi's Dual Swords (attack speed / crit carry core). Pen: Titan's Bane. Actives 1/2 · pen ≈ 20.

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 20.0):
  1. Odysseus' Bow (power, 2450g)
  2. Bloodforge (power, active, 2550g)
  3. Musashi's Dual Swords (power, 2700g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Deathbringer (power, 2900g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Ullr — C-tier (role rank #15, model 51.8)

*Physical · Strength scaling (STR 80.1% / INT 0%)*

Ullr · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, attack-speed steroid, self heal / drain, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, gap_close, hard_cc, heal, high_cc, pet_zone, self_sustain, sustained. Style burst 3%/dps 97%; patch stable (net -0.6, r5 +0.0). Patch axes (r5): general -0.6, attack_speed +0.0, cooldown +0.0. Scale STR 80% / INT 0%. Path: Bloodforge (lifesteal + power for execute/bruiser); Titan's Bane (% pen for physical tanks / late fights); Shifter's Shield (offline hybrid tank). Pen: Titan's Bane. Actives 1/2 · pen ≈ 20.

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 20.0):
  1. Bloodforge (power, active, 2550g)
  2. Titan's Bane (pen, pen 20.0, 3100g)
  3. Shifter's Shield (defense, 2650g)
  4. Demon Blade (power, 2750g)
  5. Deathbringer (power, 2900g)
  6. Stygian Anchor (counter, 2550g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Apollo — C-tier (role rank #16, model 51.7)

*Physical · Strength scaling (STR 74.1% / INT 0%)*

Apollo · Carry · archetype «crit_adc» (STR / physical). Kit effects: basic-attack kit, attack-speed steroid, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit. Tags: aa, anti_cc, as_steroid, gap_close, hard_cc, long_cd, sustained, team_buff. Style burst 14%/dps 86%; patch volatile (net +0.6, r5 +0.8). Patch axes (r5): general +0.8. Scale STR 74% / INT 0%. Path: Odysseus' Bow (Carry path fit for kit profile); Runeforged Hammer (Carry path fit for kit profile); Avenging Blade (attack speed / crit carry core). Pen: Titan's Bane. Actives 1/2 · pen ≈ 20.

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 20.0):
  1. Odysseus' Bow (power, 2450g)
  2. Runeforged Hammer (power, 2550g)
  3. Avenging Blade (power, 2650g)
  4. Arondight (power, active, 2650g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Jing Wei — C-tier (role rank #17, model 49.9)

*Physical · Strength scaling (STR 87.0% / INT 0%)*

Jing Wei · Carry · archetype «crit_adc» (STR / physical). Kit effects: big ult spike, attack-speed steroid, pet / deployable, dash / leap engage, CC immunity in kit, high mobility. Tags: anti_cc, as_steroid, dot, gap_close, long_cd, mobile, pet_zone, sustained. Style burst 32%/dps 68%; patch volatile (net -0.6, r5 -0.6). Patch axes (r5): general -0.6. Scale STR 87% / INT 0%. Path: Devourer's Gauntlet (lifesteal stacking); Bloodforge (lifesteal + power for execute/bruiser); Avenging Blade (attack speed / crit carry core). Pen: Heartseeker, Titan's Bane. Actives 1/2 · pen ≈ 30.

- **Starter:** Gilded Arrow
- **Buy order** (actives 1/2, pen ≈ 30.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Bloodforge (power, active, 2550g)
  3. Avenging Blade (power, 2650g)
  4. Musashi's Dual Swords (power, 2700g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Titan's Bane (pen, pen 20.0, 3100g)
- **Relics:** Purification Beads (33.0), Aegis of Acceleration (28.0)

#### Hou Yi — D-tier (role rank #18, model 48.8)

*Physical · Strength scaling (STR 50.0% / INT 36.8%)*

Hou Yi · Carry · archetype «power_adc» (STR / physical). Kit effects: big ult spike, hard crowd control, dash / leap engage, lots of CC, long cooldowns. Tags: gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 49%/dps 51%; patch falling (net -1.0, r5 +0.0). Patch axes (r5): general -0.7, cooldown -0.3, damage +0.0. Scale STR 50% / INT 37%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); Bloodforge (lifesteal + power for execute/bruiser). Pen: Jotunn's Revenge, Tekko-Kagi, Titan's Bane. Actives 2/2 · pen ≈ 35.

- **Starter:** Gilded Arrow
- **Buy order** (actives 2/2, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. Bloodforge (power, active, 2550g)
  4. Death Metal (power, active, 2600g)
  5. Tekko-Kagi (pen, pen 10.0, 2700g)
  6. Titan's Bane (pen, pen 20.0, 3100g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Rama — D-tier (role rank #19, model 48.4)

*Physical · Strength scaling (STR 64.6% / INT 0%)*

Rama · Carry · archetype «crit_adc» (STR / physical). Kit effects: basic-attack kit, attack-speed steroid, hard crowd control, sustained DPS, multi-hit / ticks, long cooldowns. Tags: aa, as_steroid, hard_cc, long_cd, sustained. Style burst 0%/dps 100%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): general +0.1, survivability -0.0, attack_speed +0.0. Scale STR 65% / INT 0%. Path: Tyrfing (Carry path fit for kit profile); Lernaean Bow (Carry path fit for kit profile); Bloodforge (lifesteal + power for execute/bruiser). Pen: Titan's Bane. Actives 2/2 · pen ≈ 20.

- **Starter:** Gilded Arrow
- **Buy order** (actives 2/2, pen ≈ 20.0):
  1. Tyrfing (power, 2400g)
  2. Lernaean Bow (power, active, 2500g)
  3. Bloodforge (power, active, 2550g)
  4. Avenging Blade (power, 2650g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Deathbringer (power, 2900g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Chronos — D-tier (role rank #20, model 28.0)

*Magical · Intelligence scaling (STR 0% / INT 67.2%)*

Chronos · Carry · archetype «ability_mage_adc» (INT / magical). Kit effects: hard crowd control, dash / leap engage, CC immunity in kit, sustained DPS, multi-hit / ticks, healing in kit. Tags: anti_cc, gap_close, hard_cc, heal, long_cd. Style burst 0%/dps 100%; patch falling (net -4.2, r5 -4.2). Patch axes (r5): utility -2.1, damage -1.5, general -0.5. Scale STR 0% / INT 67%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Spear of Desolation (flat pen + CDR for ability burst); The World Stone (penetration required for damage role). Pen: Spear of Desolation, The World Stone, Obsidian Shard. Actives 0/2 · pen ≈ 40.

- **Starter:** Sands Of Time
- **Buy order** (actives 0/2, pen ≈ 40.0):
  1. Gem of Isolation (power, 2500g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. The World Stone (pen, pen 10.0, 2800g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Genji's Guard (defense, 2350g)
  6. Wish-Granting Pearl (power, 3550g)
- **Relics:** Purification Beads (33.0), Aegis of Acceleration (28.0)

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

#### Princess Bari — S-tier (role rank #1, model 66.2)

*Magical · Intelligence scaling (STR 80.1% / INT 110.3%)*

Princess Bari · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, pet / deployable, hard crowd control, ally buffs / auras, lots of CC, burst combos. Tags: burst, hard_cc, high_cc, long_cd, pet_zone, team_buff, ult_nuke. Style burst 69%/dps 31%; patch new (net +0.2, r5 +0.0). Patch axes (r5): general +0.3, cooldown -0.0, attack_speed -0.0. Scale STR 80% / INT 110%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Divine Ruin (anti-heal + pen for healing/sustain kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Spear of Desolation, The World Stone, Obsidian Shard. Actives 1/2 · pen ≈ 40.

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 40.0):
  1. Gem of Isolation (power, 2500g)
  2. Divine Ruin (counter, 2500g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The World Stone (pen, pen 10.0, 2800g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Staff of Myrddin (power, active, 2900g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Kukulkan — S-tier (role rank #2, model 65.9)

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

#### Ra — S-tier (role rank #3, model 65.3)

*Magical · Intelligence scaling (STR 0% / INT 106.2%)*

Ra · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, pet / deployable, ally buffs / auras, multi-hit / ticks, burst combos, damage over time. Tags: burst, dot, heal, long_cd, pet_zone, team_buff, ult_nuke. Style burst 69%/dps 31%; patch stable (net +0.7, r5 +0.0). Patch axes (r5): general +0.6, damage +0.1, survivability +0.0. Scale STR 0% / INT 106%. Path: Soul Gem (ability heal/proc for mages); Divine Ruin (anti-heal + pen for healing/sustain kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Soul Gem, Spear of Desolation, The Cosmic Horror, Obsidian Shard, Rod of Tahuti. Actives 0/2 · pen ≈ 50.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 50.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Divine Ruin (counter, 2500g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (30.0), Aegis of Acceleration (30.0)

#### Eset — A-tier (role rank #4, model 64.7)

*Magical · Intelligence scaling (STR 0% / INT 52.7%)*

Eset · Mid · archetype «channel_mage» (INT / magical). Kit effects: channel / cast time, basic-attack kit, hard crowd control, ally buffs / auras, lots of CC, multi-hit / ticks. Tags: aa, burst, channel, hard_cc, heal, high_cc, long_cd, shield. Style burst 86%/dps 14%; patch volatile (net +0.0, r5 +0.7). Patch axes (r5): damage +0.7. Scale STR 0% / INT 53%. Path: Chronos' Pendant (CDR core for spam / channel kits); Soul Gem (ability heal/proc for mages); Gem of Isolation (zones & CC — Isolation slow/shred value). Pen: Soul Gem, The Cosmic Horror, Spear Of The Magus. Actives 0/2 · pen ≈ 25.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Chronos' Pendant (power, 2400g)
  2. Soul Gem (power, pen 5.0, 2500g)
  3. Gem of Isolation (power, 2500g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Spear Of The Magus (pen, pen 10.0, 2700g)
  6. Stygian Anchor (counter, 2550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Aphrodite — A-tier (role rank #5, model 64.5)

*Magical · Intelligence scaling (STR 0% / INT 102.0%)*

Aphrodite · Mid · archetype «burst_mage» (INT / magical). Kit effects: big ult spike, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, burst, dot, gap_close, hard_cc, heal, long_cd, team_buff. Style burst 60%/dps 40%; patch volatile (net +1.1, r5 +0.1). Patch axes (r5): heal +0.1. Scale STR 0% / INT 102%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Spear of Desolation (flat pen + CDR for ability burst); Spear Of The Magus (multi-hit / shred — stacks Magus passive). Pen: Spear of Desolation, Spear Of The Magus. Actives 0/2 · pen ≈ 20.

- **Starter:** Vampiric Shroud
- **Buy order** (actives 0/2, pen ≈ 20.0):
  1. Gem of Isolation (power, 2500g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. Spear Of The Magus (pen, pen 10.0, 2700g)
  4. Soul Reaver (power, 2950g)
  5. Alchemist Coat (mitigate, 2350g)
  6. Wish-Granting Pearl (power, 3550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Sol — A-tier (role rank #6, model 64.0)

*Magical · Intelligence scaling (STR 21.8% / INT 50.7%)*

Sol · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, big ult spike, basic-attack kit, self heal / drain, ally buffs / auras, CC immunity in kit. Tags: aa, anti_cc, burst, dot, heal, heavy_dot, high_cc, long_cd. Style burst 61%/dps 39%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): damage -0.0, general -0.0, attack_speed -0.0. Scale STR 22% / INT 51%. Path: Chronos' Pendant (CDR core for spam / channel kits); Gluttonous Grimoire (sustain / omnivamp line); Spear of Desolation (flat pen + CDR for ability burst). Pen: Gluttonous Grimoire, Spear of Desolation, Obsidian Shard. Actives 0/2 · pen ≈ 40.

- **Starter:** Vampiric Shroud
- **Buy order** (actives 0/2, pen ≈ 40.0):
  1. Chronos' Pendant (power, 2400g)
  2. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Soul Reaver (power, 2950g)
  6. Resolute Mantle (mitigate, 2750g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Neith — A-tier (role rank #7, model 62.9)

*Physical · Hybrid scaling (STR 63.3% / INT 76.7%)*

Neith · Mid · archetype «channel_mage» (STR / physical). Kit effects: channel / cast time, big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, lots of CC. Tags: as_steroid, burst, channel, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 67%/dps 33%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): general +0.1, utility -0.0, attack_speed -0.0. Scale STR 63% / INT 77%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Transcendence (mana stack → power scaling); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Transcendence, The Crusher, Titan's Bane. Actives 1/2 · pen ≈ 35.

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Transcendence (power, 2400g)
  3. Hydra's Lament (power, 2450g)
  4. Arondight (power, active, 2650g)
  5. The Crusher (pen, pen 10.0, 2800g)
  6. Titan's Bane (pen, pen 20.0, 3100g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Baron Samedi — A-tier (role rank #8, model 62.1)

*Magical · Intelligence scaling (STR 0% / INT 69.6%)*

Baron Samedi · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, channel / cast time, execute / threshold, pet / deployable, hard crowd control, ally buffs / auras. Tags: burst, channel, dot, execute, hard_cc, heal, heavy_dot, high_cc. Style burst 71%/dps 29%; patch volatile (net +1.1, r5 +0.0). Patch axes (r5): heal +0.9, general +0.3, damage -0.1. Scale STR 0% / INT 70%. Path: Chronos' Pendant (CDR core for spam / channel kits); Soul Gem (ability heal/proc for mages); Gem of Isolation (zones & CC — Isolation slow/shred value). Pen: Soul Gem, The World Stone, Obsidian Shard. Actives 0/2 · pen ≈ 35.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 35.0):
  1. Chronos' Pendant (power, 2400g)
  2. Soul Gem (power, pen 5.0, 2500g)
  3. Gem of Isolation (power, 2500g)
  4. The World Stone (pen, pen 10.0, 2800g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Nut — B-tier (role rank #9, model 61.8)

*Magical · Intelligence scaling (STR 80.3% / INT 130.9%)*

Nut · Mid · archetype «burst_mage» (INT / magical). Kit effects: big ult spike, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: aa, anti_cc, burst, gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 75%/dps 25%; patch falling (net -1.4, r5 +0.0). Patch axes (r5): general -0.9, damage -0.5. Scale STR 80% / INT 131%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Spear of Desolation (flat pen + CDR for ability burst); The World Stone (penetration required for damage role). Pen: Spear of Desolation, The World Stone, Obsidian Shard. Actives 1/2 · pen ≈ 40.

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 40.0):
  1. Gem of Isolation (power, 2500g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. The World Stone (pen, pen 10.0, 2800g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Staff of Myrddin (power, active, 2900g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### The Morrigan — B-tier (role rank #10, model 61.6)

*Magical · Intelligence scaling (STR 0% / INT 142.6%)*

The Morrigan · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, pet / deployable, hard crowd control, damage over time, long cooldowns, zones / linger. Tags: dot, hard_cc, long_cd, pet_zone, ult_nuke. Style burst 48%/dps 52%; patch stable (net +0.4, r5 +0.0). Patch axes (r5): utility +0.0. Scale STR 0% / INT 143%. Path: Soul Gem (ability heal/proc for mages); Gem of Isolation (zones & CC — Isolation slow/shred value); Divine Ruin (anti-heal + pen for healing/sustain kits). Pen: Soul Gem, Spear Of The Magus, Doom Orb, Obsidian Shard. Actives 0/2 · pen ≈ 45.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 45.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Gem of Isolation (power, 2500g)
  3. Divine Ruin (counter, 2500g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Doom Orb (pen, pen 10.0, 2700g)
  6. Obsidian Shard (pen, pen 20.0, 3050g)
- **Relics:** Purification Beads (30.0), Aegis of Acceleration (30.0)

#### Hecate — B-tier (role rank #11, model 59.9)

*Magical · Intelligence scaling (STR 0% / INT 70.3%)*

Hecate · Mid · archetype «channel_mage» (INT / magical). Kit effects: channel / cast time, hard crowd control, dash / leap engage, ally buffs / auras, burst combos, shields. Tags: burst, channel, gap_close, hard_cc, heal, long_cd, shield, team_buff. Style burst 57%/dps 43%; patch stable (net -0.4, r5 +0.0). Patch axes (r5): general -0.5, damage +0.0, survivability +0.0. Scale STR 0% / INT 70%. Path: The World Stone (penetration required for damage role); Obsidian Shard (% pen for magical tanks / late fights); Shifter's Shield (offline hybrid tank). Pen: The World Stone, Obsidian Shard, Rod of Tahuti. Actives 1/2 · pen ≈ 35.

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 35.0):
  1. The World Stone (pen, pen 10.0, 2800g)
  2. Obsidian Shard (pen, pen 20.0, 3050g)
  3. Shifter's Shield (defense, 2650g)
  4. Staff of Myrddin (power, active, 2900g)
  5. Rod of Tahuti (power, pen 5.0, 3000g)
  6. Stygian Anchor (counter, 2550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Poseidon — B-tier (role rank #12, model 56.5)

*Magical · Intelligence scaling (STR 0% / INT 100.4%)*

Poseidon · Mid · archetype «zone_mage» (INT / magical). Kit effects: big ult spike, basic-attack kit, attack-speed steroid, pet / deployable, hard crowd control, burst combos. Tags: aa, as_steroid, burst, dot, hard_cc, high_cc, long_cd, pet_zone. Style burst 92%/dps 8%; patch volatile (net +1.3, r5 +0.0). Patch axes (r5): damage +1.3, cooldown -0.0, general +0.0. Scale STR 0% / INT 100%. Path: Divine Ruin (anti-heal + pen for healing/sustain kits); Spear of Desolation (flat pen + CDR for ability burst; damage buffed — power/pen); The Cosmic Horror (penetration required for damage role). Pen: Spear of Desolation, The Cosmic Horror, Obsidian Shard, Rod of Tahuti. Actives 0/2 · pen ≈ 45.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 45.0):
  1. Divine Ruin (counter, 2500g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. The Cosmic Horror (pen, pen 10.0, 2650g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Soul Reaver (power, 2950g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Scylla — B-tier (role rank #13, model 56.5)

*Magical · Intelligence scaling (STR 0% / INT 96.2%)*

Scylla · Mid · archetype «zone_mage» (INT / magical). Kit effects: protection shred, big ult spike, basic-attack kit, pet / deployable, hard crowd control, dash / leap engage. Tags: aa, anti_cc, burst, gap_close, hard_cc, long_cd, pet_zone, prot_shred. Style burst 89%/dps 11%; patch volatile (net +1.5, r5 +0.7). Patch axes (r5): damage +0.7. Scale STR 0% / INT 96%. Path: Divine Ruin (anti-heal + pen for healing/sustain kits); Gem of Isolation (zones & CC — Isolation slow/shred value); Spear of Desolation (flat pen + CDR for ability burst; damage buffed — power/pen). Pen: Spear of Desolation, Spear Of The Magus, Obsidian Shard. Actives 0/2 · pen ≈ 40.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 40.0):
  1. Divine Ruin (counter, 2500g)
  2. Gem of Isolation (power, 2500g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Wish-Granting Pearl (power, 3550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Discordia — B-tier (role rank #14, model 56.3)

*Magical · Intelligence scaling (STR 0% / INT 118.8%)*

Discordia · Mid · archetype «sustain_mage» (INT / magical). Kit effects: big ult spike, self heal / drain, hard crowd control, dash / leap engage, ally buffs / auras, burst combos. Tags: burst, gap_close, hard_cc, heal, long_cd, self_sustain, team_buff, ult_nuke. Style burst 69%/dps 31%; patch volatile (net -1.6, r5 -0.1). Patch axes (r5): utility -0.9, cooldown +0.8. Scale STR 0% / INT 119%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Spear of Desolation (flat pen + CDR for ability burst); Obsidian Shard (% pen for magical tanks / late fights). Pen: Spear of Desolation, Obsidian Shard. Actives 0/2 · pen ≈ 30.

- **Starter:** Vampiric Shroud
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Gem of Isolation (power, 2500g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. Obsidian Shard (pen, pen 20.0, 3050g)
  4. Soul Reaver (power, 2950g)
  5. Chandra's Grace (mitigate, 2300g)
  6. Wish-Granting Pearl (power, 3550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Vulcan — C-tier (role rank #15, model 55.8)

*Magical · Intelligence scaling (STR 0% / INT 86.6%)*

Vulcan · Mid · archetype «burst_mage» (INT / magical). Kit effects: protection shred, big ult spike, dash / leap engage, multi-hit / ticks, burst combos, long cooldowns. Tags: burst, gap_close, long_cd, prot_shred, ult_nuke. Style burst 62%/dps 38%; patch stable (net -0.2, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 0% / INT 87%. Path: Soul Gem (ability heal/proc for mages); Ethereal Staff (Mid path fit for kit profile); Spear of Desolation (flat pen + CDR for ability burst). Pen: Soul Gem, Spear of Desolation, Spear Of The Magus, The World Stone. Actives 1/2 · pen ≈ 35.

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 35.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Ethereal Staff (mitigate, 2550g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. The World Stone (pen, pen 10.0, 2800g)
  6. Staff of Myrddin (power, active, 2900g)
- **Relics:** Aegis of Acceleration (30.0), Purification Beads (30.0)

#### Janus — C-tier (role rank #16, model 55.4)

*Magical · Intelligence scaling (STR 0% / INT 92.6%)*

Janus · Mid · archetype «burst_mage» (INT / magical). Kit effects: big ult spike, execute / threshold, ally buffs / auras, CC immunity in kit, multi-hit / ticks, burst combos. Tags: anti_cc, burst, execute, long_cd, team_buff, ult_nuke. Style burst 64%/dps 36%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): utility -0.1, damage -0.0, survivability -0.0. Scale STR 0% / INT 93%. Path: Ethereal Staff (Mid path fit for kit profile); Spear of Desolation (flat pen + CDR for ability burst); Spear Of The Magus (multi-hit / shred — stacks Magus passive). Pen: Spear of Desolation, Spear Of The Magus, The World Stone, Rod of Tahuti. Actives 0/2 · pen ≈ 35.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 35.0):
  1. Ethereal Staff (mitigate, 2550g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. Spear Of The Magus (pen, pen 10.0, 2700g)
  4. The World Stone (pen, pen 10.0, 2800g)
  5. Soul Reaver (power, 2950g)
  6. Rod of Tahuti (power, pen 5.0, 3000g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Merlin — C-tier (role rank #17, model 52.9)

*Magical · Intelligence scaling (STR 0% / INT 47.4%)*

Merlin · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, channel / cast time, pet / deployable, dash / leap engage, lots of CC, multi-hit / ticks. Tags: channel, dot, gap_close, heal, heavy_dot, high_cc, pet_zone, zone. Style burst 46%/dps 54%; patch stable (net +0.7, r5 +0.0). Patch axes (r5): cooldown +1.2, damage -0.6, general +0.3. Scale STR 0% / INT 47%. Path: Chronos' Pendant (CDR core for spam / channel kits); Gem of Isolation (zones & CC — Isolation slow/shred value); Gem of Focus (ability CDR / focus passive). Pen: Spear Of The Magus, Obsidian Shard. Actives 0/2 · pen ≈ 30.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 30.0):
  1. Chronos' Pendant (power, 2400g)
  2. Gem of Isolation (power, 2500g)
  3. Gem of Focus (power, 2550g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Zeus — C-tier (role rank #18, model 48.3)

*Magical · Intelligence scaling (STR 0% / INT 62.3%)*

Zeus · Mid · archetype «burst_mage» (INT / magical). Kit effects: attack-speed steroid, hard crowd control, long cooldowns, burst combos. Tags: as_steroid, hard_cc, long_cd. Style burst 58%/dps 42%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, utility -0.0, damage -0.0. Scale STR 0% / INT 62%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Spear Of The Magus (multi-hit / shred — stacks Magus passive); The World Stone (penetration required for damage role). Pen: Spear Of The Magus, The World Stone, Obsidian Shard. Actives 1/2 · pen ≈ 40.

- **Starter:** Conduit Gem
- **Buy order** (actives 1/2, pen ≈ 40.0):
  1. Gem of Isolation (power, 2500g)
  2. Spear Of The Magus (pen, pen 10.0, 2700g)
  3. The World Stone (pen, pen 10.0, 2800g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Jade Scepter (power, active, 2750g)
  6. Wish-Granting Pearl (power, 3550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Morgan Le Fay — C-tier (role rank #19, model 46.8)

*Magical · Intelligence scaling (STR 0% / INT 76.5%)*

Morgan Le Fay · Mid · archetype «zone_mage» (INT / magical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit, multi-hit / ticks, burst combos. Tags: anti_cc, burst, dot, gap_close, hard_cc, heal, long_cd, pet_zone. Style burst 64%/dps 36%; patch falling (net -2.5, r5 -2.9). Patch axes (r5): damage -1.5, utility -0.8, survivability -0.6. Scale STR 0% / INT 76%. Path: Soul Gem (ability heal/proc for mages); Spear of Desolation (flat pen + CDR for ability burst); Spear Of The Magus (multi-hit / shred — stacks Magus passive). Pen: Soul Gem, Spear of Desolation, Spear Of The Magus, The World Stone, Obsidian Shard. Actives 0/2 · pen ≈ 55.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 55.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. Spear Of The Magus (pen, pen 10.0, 2700g)
  4. The World Stone (pen, pen 10.0, 2800g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Wish-Granting Pearl (power, 3550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Ah Puch — C-tier (role rank #20, model 45.4)

*Magical · Intelligence scaling (STR 0% / INT 46.9%)*

Ah Puch · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, heavy healing, hard crowd control, low mobility, multi-hit / ticks, zones / linger. Tags: dot, hard_cc, heal, heavy_dot, heavy_heal, immobile, long_cd, zone. Style burst 54%/dps 46%; patch falling (net -2.0, r5 -2.0). Patch axes (r5): damage -1.0, survivability -0.8, general +0.7. Scale STR 0% / INT 47%. Path: Chronos' Pendant (CDR core for spam / channel kits); Gem of Isolation (zones & CC — Isolation slow/shred value); Soul Gem (ability heal/proc for mages). Pen: Soul Gem, Obsidian Shard. Actives 0/2 · pen ≈ 25.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Chronos' Pendant (power, 2400g)
  2. Gem of Isolation (power, 2500g)
  3. Soul Gem (power, pen 5.0, 2500g)
  4. Divine Ruin (counter, 2500g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Alchemist Coat (mitigate, 2350g)
- **Relics:** Aegis of Acceleration (40.0), Purification Beads (38.0)

#### Agni — D-tier (role rank #21, model 38.9)

*Magical · Intelligence scaling (STR 0% / INT 54.1%)*

Agni · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, pet / deployable, hard crowd control, dash / leap engage, multi-hit / ticks, healing in kit. Tags: dot, gap_close, hard_cc, heal, heavy_dot, long_cd, pet_zone. Style burst 0%/dps 0%; patch volatile (net -1.0, r5 -0.6). Patch axes (r5): damage -0.6, general +0.0. Scale STR 0% / INT 54%. Path: Soul Gem (ability heal/proc for mages); Divine Ruin (anti-heal + pen for healing/sustain kits); Spear of Desolation (flat pen + CDR for ability burst). Pen: Soul Gem, Spear of Desolation, Spear Of The Magus. Actives 0/2 · pen ≈ 25.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 25.0):
  1. Soul Gem (power, pen 5.0, 2500g)
  2. Divine Ruin (counter, 2500g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Stone of Binding (mitigate, 2550g)
  6. Wish-Granting Pearl (power, 3550g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Nu Wa — D-tier (role rank #22, model 38.0)

*Magical · Intelligence scaling (STR 0% / INT 76.1%)*

Nu Wa · Mid · archetype «aa_mage» (INT / magical). Kit effects: protection shred, big ult spike, basic-attack kit, pet / deployable, hard crowd control, dash / leap engage. Tags: aa, anti_cc, burst, dot, gap_close, hard_cc, long_cd, pet_zone. Style burst 60%/dps 40%; patch falling (net -4.2, r5 -1.5). Patch axes (r5): damage -1.5. Scale STR 0% / INT 76%. Path: Divine Ruin (anti-heal + pen for healing/sustain kits); Bracer of The Abyss (Mid path fit for kit profile); Spear of Desolation (flat pen + CDR for ability burst). Pen: Spear of Desolation, The Cosmic Horror, Obsidian Shard. Actives 0/2 · pen ≈ 40.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 40.0):
  1. Divine Ruin (counter, 2500g)
  2. Bracer of The Abyss (power, 2500g)
  3. Spear of Desolation (pen, pen 10.0, 2650g)
  4. The Cosmic Horror (pen, pen 10.0, 2650g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Soul Reaver (power, 2950g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Anubis — D-tier (role rank #23, model 28.2)

*Magical · Intelligence scaling (STR 0% / INT 59.8%)*

Anubis · Mid · archetype «dot_mage» (INT / magical). Kit effects: damage over time, channel / cast time, big ult spike, self heal / drain, pet / deployable, hard crowd control. Tags: anti_cc, channel, dot, hard_cc, heal, heavy_dot, high_cc, immobile. Style burst 98%/dps 2%; patch falling (net -4.4, r5 -4.5). Patch axes (r5): survivability -2.1, damage -1.5, heal -1.0. Scale STR 0% / INT 60%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Soul Gem (ability heal/proc for mages); Gluttonous Grimoire (sustain / omnivamp line). Pen: Soul Gem, Gluttonous Grimoire, Spear Of The Magus, Obsidian Shard. Actives 0/2 · pen ≈ 45.

- **Starter:** Vampiric Shroud
- **Buy order** (actives 0/2, pen ≈ 45.0):
  1. Gem of Isolation (power, 2500g)
  2. Soul Gem (power, pen 5.0, 2500g)
  3. Gluttonous Grimoire (pen, pen 10.0, 2600g)
  4. Spear Of The Magus (pen, pen 10.0, 2700g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Chandra's Grace (mitigate, 2300g)
- **Relics:** Aegis of Acceleration (40.0), Purification Beads (38.0)

#### Chronos — D-tier (role rank #24, model 28.0)

*Magical · Intelligence scaling (STR 0% / INT 67.2%)*

Chronos · Mid · archetype «burst_mage» (INT / magical). Kit effects: hard crowd control, dash / leap engage, CC immunity in kit, sustained DPS, multi-hit / ticks, healing in kit. Tags: anti_cc, gap_close, hard_cc, heal, long_cd. Style burst 0%/dps 100%; patch falling (net -4.2, r5 -4.2). Patch axes (r5): utility -2.1, damage -1.5, general -0.5. Scale STR 0% / INT 67%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Spear of Desolation (flat pen + CDR for ability burst); Spear Of The Magus (multi-hit / shred — stacks Magus passive). Pen: Spear of Desolation, Spear Of The Magus, Obsidian Shard. Actives 0/2 · pen ≈ 40.

- **Starter:** Conduit Gem
- **Buy order** (actives 0/2, pen ≈ 40.0):
  1. Gem of Isolation (power, 2500g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. Spear Of The Magus (pen, pen 10.0, 2700g)
  4. Obsidian Shard (pen, pen 20.0, 3050g)
  5. Chandra's Grace (mitigate, 2300g)
  6. Alchemist Coat (mitigate, 2350g)
- **Relics:** Aegis of Acceleration (30.0), Purification Beads (30.0)

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
**Common role items (not ordered as a build):** Gluttonous Grimoire, The Executioner, Soul Gem, Jotunn's Revenge, Shifter's Shield, Obsidian Shard, Avenging Blade

### God-specific kit builds (use these)

#### Ne Zha — S-tier (role rank #1, model 70.5)

*Physical · Strength scaling (STR 147.9% / INT 0%)*

Ne Zha · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: protection shred, big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, as_steroid, gap_close, hard_cc, heal, long_cd, mobile, prot_shred. Style burst 44%/dps 56%; patch new (net -0.7, r5 +0.0). Patch axes (r5): damage -1.0, general +0.3, utility +0.0. Scale STR 148% / INT 0%. Path: Hydra's Lament (CDR + pen for gank/engage); Devourer's Gauntlet (lifesteal stacking); The Executioner (AA prot shred). Pen: Titan's Bane. Actives 1/3 · pen ≈ 20.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 1/3, pen ≈ 20.0):
  1. Hydra's Lament (power, 2450g)
  2. Devourer's Gauntlet (power, 2500g)
  3. The Executioner (power, 2550g)
  4. Bloodforge (power, active, 2550g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Freya's Tears (defense, 2600g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Mordred — S-tier (role rank #2, model 67.9)

*Physical · Strength scaling (STR 77.5% / INT 45.8%)*

Mordred · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: damage over time, channel / cast time, big ult spike, attack-speed steroid, self heal / drain, heavy healing. Tags: anti_cc, as_steroid, burst, channel, dot, gap_close, hard_cc, heal. Style burst 58%/dps 42%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): survivability +0.0, general -0.0, heal +0.0. Scale STR 77% / INT 46%. Path: Hydra's Lament (CDR + pen for gank/engage); The Executioner (AA prot shred); Bloodforge (lifesteal + power for execute/bruiser). Pen: Heartseeker, Titan's Bane. Actives 1/3 · pen ≈ 30.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 30.0):
  1. Hydra's Lament (power, 2450g)
  2. The Executioner (power, 2550g)
  3. Bloodforge (power, active, 2550g)
  4. Avenging Blade (power, 2650g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Titan's Bane (pen, pen 20.0, 3100g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Tsukuyomi — S-tier (role rank #3, model 67.0)

*Physical · Strength scaling (STR 158.7% / INT 119.2%)*

Tsukuyomi · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: big ult spike, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit, high mobility. Tags: aa, anti_cc, burst, gap_close, hard_cc, heal, long_cd, mobile. Style burst 65%/dps 35%; patch stable (net +0.1, r5 +0.0). Patch axes (r5): general +0.2, damage -0.2, utility +0.0. Scale STR 159% / INT 119%. Path: Avenging Blade (attack speed / crit carry core); Riptalon (attack speed / crit carry core); Heartseeker (stacking pen power for assassins). Pen: Riptalon, Heartseeker, Titan's Bane. Actives 1/3 · pen ≈ 40.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 1/3, pen ≈ 40.0):
  1. Avenging Blade (power, 2650g)
  2. Riptalon (pen, pen 10.0, 2700g)
  3. Heartseeker (pen, pen 10.0, 3000g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Eye of Erebus (defense, active, 2600g)
  6. Demon Blade (power, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Cernunnos — A-tier (role rank #4, model 66.4)

*Physical · Strength scaling (STR 80.4% / INT 51.1%)*

Cernunnos · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: protection shred, big ult spike, basic-attack kit, self heal / drain, hard crowd control, dash / leap engage. Tags: aa, dot, gap_close, hard_cc, heal, high_cc, long_cd, prot_shred. Style burst 30%/dps 70%; patch stable (net +0.5, r5 +0.0). Patch axes (r5): general +0.5, damage +0.0, cooldown +0.0. Scale STR 80% / INT 51%. Path: Jotunn's Revenge (CDR + pen for gank/engage); The Executioner (AA prot shred); Avenging Blade (attack speed / crit carry core). Pen: Jotunn's Revenge, Pendulum Blade. Actives 2/3 · pen ≈ 15.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 2/3, pen ≈ 15.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. The Executioner (power, 2550g)
  3. Avenging Blade (power, 2650g)
  4. Arondight (power, active, 2650g)
  5. Pendulum Blade (pen, active, pen 10.0, 2750g)
  6. Gladiator's Shield (defense, 2450g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Thanatos — A-tier (role rank #5, model 65.5)

*Physical · Strength scaling (STR 56.1% / INT 0%)*

Thanatos · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: protection shred, self heal / drain, execute / threshold, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, burst, execute, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 62%/dps 38%; patch rising (net +1.2, r5 +1.0). Patch axes (r5): general +1.0. Scale STR 56% / INT 0%. Path: Devourer's Gauntlet (lifesteal stacking); Arondight (CDR + pen for gank/engage); Titan's Bane (% pen for physical tanks / late fights; patch rising — lean damage). Pen: Titan's Bane, Avatar's Parashu. Actives 2/3 · pen ≈ 30.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 2/3, pen ≈ 30.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Arondight (power, active, 2650g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. Deathbringer (power, 2900g)
  5. Prophetic Cloak (defense, 2400g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Odin — A-tier (role rank #6, model 65.4)

*Physical · Strength scaling (STR 65.2% / INT 34.1%)*

Odin · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: big ult spike, basic-attack kit, attack-speed steroid, shields, hard crowd control, dash / leap engage. Tags: aa, as_steroid, burst, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 64%/dps 36%; patch volatile (net +1.1, r5 +0.1). Patch axes (r5): damage +0.1, survivability +0.1. Scale STR 65% / INT 34%. Path: Hydra's Lament (CDR + pen for gank/engage); Bloodforge (lifesteal + power for execute/bruiser); Arondight (CDR + pen for gank/engage). Pen: Riptalon, Titan's Bane. Actives 2/3 · pen ≈ 30.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 2/3, pen ≈ 30.0):
  1. Hydra's Lament (power, 2450g)
  2. Bloodforge (power, active, 2550g)
  3. Arondight (power, active, 2650g)
  4. Riptalon (pen, pen 10.0, 2700g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Ratatoskr — A-tier (role rank #7, model 65.4)

*Physical · Strength scaling (STR 89.7% / INT 0%)*

Ratatoskr · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: big ult spike, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC, burst combos. Tags: anti_cc, burst, gap_close, hard_cc, high_cc, long_cd, ult_nuke. Style burst 75%/dps 25%; patch rising (net +2.2, r5 +1.5). Patch axes (r5): survivability +2.2, general -0.9, cooldown -0.7. Scale STR 90% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Transcendence (mana stack → power scaling); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Transcendence, Pendulum Blade, Heartseeker, Titan's Bane. Actives 1/3 · pen ≈ 45.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 1/3, pen ≈ 45.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Transcendence (power, 2400g)
  3. Hydra's Lament (power, 2450g)
  4. Pendulum Blade (pen, active, pen 10.0, 2750g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Titan's Bane (pen, pen 20.0, 3100g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Awilix — B-tier (role rank #8, model 64.1)

*Physical · Strength scaling (STR 64.0% / INT 0%)*

Awilix · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: attack-speed steroid, pet / deployable, hard crowd control, dash / leap engage, lots of CC, high mobility. Tags: as_steroid, gap_close, hard_cc, high_cc, long_cd, mobile, pet_zone, sustained. Style burst 22%/dps 78%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, utility +0.0, cooldown +0.0. Scale STR 64% / INT 0%. Path: Bloodforge (Jungle path fit for kit profile); Arondight (CDR + pen for gank/engage); Musashi's Dual Swords (attack speed / crit carry core). Pen: Heartseeker, Titan's Bane. Actives 2/3 · pen ≈ 30.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 30.0):
  1. Bloodforge (power, active, 2550g)
  2. Arondight (power, active, 2650g)
  3. Musashi's Dual Swords (power, 2700g)
  4. Heartseeker (pen, pen 10.0, 3000g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Fenrir — B-tier (role rank #9, model 61.1)

*Physical · Strength scaling (STR 97.4% / INT 0%)*

Fenrir · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: channel / cast time, big ult spike, basic-attack kit, self heal / drain, hard crowd control, dash / leap engage. Tags: aa, anti_cc, channel, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 20%/dps 80%; patch volatile (net -0.3, r5 +0.8). Patch axes (r5): damage +0.8. Scale STR 97% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Devourer's Gauntlet (lifesteal stacking); Avenging Blade (attack speed / crit carry core). Pen: Jotunn's Revenge, The Crusher, Titan's Bane. Actives 0/3 · pen ≈ 35.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 0/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Avenging Blade (power, 2650g)
  4. The Crusher (pen, pen 10.0, 2800g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Gilgamesh — B-tier (role rank #10, model 61.0)

*Physical · Strength scaling (STR 72.8% / INT 0%)*

Gilgamesh · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, lots of CC, burst combos. Tags: burst, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, team_buff. Style burst 77%/dps 23%; patch new (net -0.3, r5 +0.0). Patch axes (r5): damage -1.3, general +0.9, mana +0.1. Scale STR 73% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Transcendence (mana stack → power scaling); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Transcendence, Titan's Bane. Actives 1/3 · pen ≈ 25.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Transcendence (power, 2400g)
  3. Hydra's Lament (power, 2450g)
  4. Arondight (power, active, 2650g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Nemesis — B-tier (role rank #11, model 58.1)

*Physical · Strength scaling (STR 102.2% / INT 70.3%)*

Nemesis · Jungle · archetype «bruiser_jungle» (STR / physical). Kit effects: big ult spike, dash / leap engage, shields, healing in kit, long cooldowns. Tags: gap_close, heal, long_cd, shield, ult_nuke. Style burst 52%/dps 48%; patch stable (net +0.2, r5 +0.0). Patch axes (r5): general +0.1, damage +0.0, survivability +0.0. Scale STR 102% / INT 70%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Runeforged Hammer (Jungle path fit for kit profile); Avenging Blade (attack speed / crit carry core). Pen: Jotunn's Revenge, The Crusher, Avatar's Parashu. Actives 1/3 · pen ≈ 25.

- **Starter:** Bumba's Golden Dagger
- **Buy order** (actives 1/3, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Runeforged Hammer (power, 2550g)
  3. Avenging Blade (power, 2650g)
  4. The Crusher (pen, pen 10.0, 2800g)
  5. Shifter's Shield (defense, 2650g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Blink Rune (32.4), Purification Beads (30.0)

#### Achilles — B-tier (role rank #12, model 57.7)

*Physical · Strength scaling (STR 82.9% / INT 0%)*

Achilles · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: big ult spike, basic-attack kit, self heal / drain, execute / threshold, shields, hard crowd control. Tags: aa, anti_cc, execute, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 30%/dps 70%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, attack_speed +0.0, survivability +0.0. Scale STR 83% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Hydra's Lament (CDR + pen for gank/engage); Sanguine Lash (Jungle path fit for kit profile). Pen: Jotunn's Revenge, Riptalon, The Crusher. Actives 2/3 · pen ≈ 25.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. Sanguine Lash (power, active, 2650g)
  4. Riptalon (pen, pen 10.0, 2700g)
  5. The Crusher (pen, pen 10.0, 2800g)
  6. Eye of Erebus (defense, active, 2600g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Loki — B-tier (role rank #13, model 54.9)

*Physical · Strength scaling (STR 62.6% / INT 0%)*

Loki · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: channel / cast time, big ult spike, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, channel, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone. Style burst 84%/dps 16%; patch stable (net +0.4, r5 +0.1). Patch axes (r5): utility +0.1. Scale STR 63% / INT 0%. Path: Transcendence (mana stack → power scaling); Hydra's Lament (CDR + pen for gank/engage); Arondight (CDR + pen for gank/engage). Pen: Transcendence, Titan's Bane, Avatar's Parashu. Actives 3/3 · pen ≈ 30.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 3/3, pen ≈ 30.0):
  1. Transcendence (power, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. Arondight (power, active, 2650g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Eye of Erebus (defense, active, 2600g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Mercury — C-tier (role rank #14, model 54.8)

*Physical · Strength scaling (STR 64.8% / INT 0%)*

Mercury · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: big ult spike, attack-speed steroid, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, as_steroid, gap_close, hard_cc, high_cc, long_cd, mobile, pet_zone. Style burst 20%/dps 80%; patch falling (net -1.3, r5 +0.0). Patch axes (r5): general -1.3, utility +0.0, attack_speed +0.0. Scale STR 65% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Devourer's Gauntlet (lifesteal stacking); Riptalon (attack speed / crit carry core). Pen: Jotunn's Revenge, Riptalon, Heartseeker, Titan's Bane. Actives 0/3 · pen ≈ 45.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 0/3, pen ≈ 45.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Riptalon (pen, pen 10.0, 2700g)
  4. Heartseeker (pen, pen 10.0, 3000g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Demon Blade (power, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Susano — C-tier (role rank #15, model 53.7)

*Physical · Strength scaling (STR 109.8% / INT 0%)*

Susano · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: damage over time, big ult spike, basic-attack kit, pet / deployable, dash / leap engage, multi-hit / ticks. Tags: aa, burst, dot, gap_close, heavy_dot, long_cd, pet_zone, ult_nuke. Style burst 73%/dps 27%; patch stable (net +0.2, r5 +0.0). Patch axes (r5): damage +0.1, utility +0.1, general +0.1. Scale STR 110% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Transcendence (mana stack → power scaling); Hydra's Lament (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Transcendence, Titan's Bane. Actives 0/3 · pen ≈ 25.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 0/3, pen ≈ 25.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Transcendence (power, 2400g)
  3. Hydra's Lament (power, 2450g)
  4. Devourer's Gauntlet (power, 2500g)
  5. Musashi's Dual Swords (power, 2700g)
  6. Titan's Bane (pen, pen 20.0, 3100g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Hun Batz — C-tier (role rank #16, model 47.3)

*Physical · Strength scaling (STR 62.4% / INT 0%)*

Hun Batz · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: channel / cast time, basic-attack kit, pet / deployable, hard crowd control, dash / leap engage, multi-hit / ticks. Tags: aa, channel, dot, gap_close, hard_cc, long_cd, pet_zone. Style burst 40%/dps 60%; patch stable (net -0.2, r5 +0.0). Patch axes (r5): general -0.3, damage +0.1, utility +0.0. Scale STR 62% / INT 0%. Path: Bloodforge (lifesteal + power for execute/bruiser); Riptalon (attack speed / crit carry core); The Crusher (penetration required for damage role). Pen: Riptalon, The Crusher, Titan's Bane. Actives 1/3 · pen ≈ 40.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 40.0):
  1. Bloodforge (power, active, 2550g)
  2. Riptalon (pen, pen 10.0, 2700g)
  3. The Crusher (pen, pen 10.0, 2800g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Demon Blade (power, 2750g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Bastet — C-tier (role rank #17, model 37.4)

*Physical · Strength scaling (STR 71.7% / INT 8.5%)*

Bastet · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: big ult spike, self heal / drain, pet / deployable, hard crowd control, dash / leap engage, multi-hit / ticks. Tags: dot, gap_close, hard_cc, heal, long_cd, pet_zone, self_sustain, ult_nuke. Style burst 69%/dps 31%; patch falling (net -3.3, r5 -3.3). Patch axes (r5): utility -2.1, damage -1.8, general +0.8. Scale STR 72% / INT 8%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Devourer's Gauntlet (lifesteal stacking); Arondight (CDR + pen for gank/engage). Pen: Jotunn's Revenge, Titan's Bane, Avatar's Parashu. Actives 3/3 · pen ≈ 35.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 3/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Devourer's Gauntlet (power, 2500g)
  3. Arondight (power, active, 2650g)
  4. Titan's Bane (pen, pen 20.0, 3100g)
  5. Eye of Erebus (defense, active, 2600g)
  6. Avatar's Parashu (pen, active, pen 10.0, 3700g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Da Ji — C-tier (role rank #18, model 35.3)

*Physical · Strength scaling (STR 48.8% / INT 0%)*

Da Ji · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: damage over time, channel / cast time, execute / threshold, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, channel, dot, execute, gap_close, hard_cc, heavy_dot, high_cc. Style burst 56%/dps 44%; patch falling (net -3.4, r5 -1.7). Patch axes (r5): survivability -1.8, damage +0.0. Scale STR 49% / INT 0%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Heartseeker (stacking pen power for assassins); Titan's Bane (% pen for physical tanks / late fights). Pen: Jotunn's Revenge, Heartseeker, Titan's Bane. Actives 0/3 · pen ≈ 35.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 0/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Heartseeker (pen, pen 10.0, 3000g)
  3. Titan's Bane (pen, pen 20.0, 3100g)
  4. Deathbringer (power, 2900g)
  5. Breastplate of Valor (defense, 2400g)
  6. Resolute Mantle (mitigate, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Thor — D-tier (role rank #19, model 32.1)

*Physical · Strength scaling (STR 79.1% / INT 0%)*

Thor · Jungle · archetype «burst_assassin» (STR / physical). Kit effects: channel / cast time, big ult spike, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, channel, gap_close, hard_cc, high_cc, long_cd, pet_zone, ult_nuke. Style burst 69%/dps 31%; patch falling (net -3.8, r5 -3.5). Patch axes (r5): damage -2.7, heal -0.4, survivability -0.4. Scale STR 79% / INT 0%. Path: Transcendence (mana stack → power scaling); Hydra's Lament (CDR + pen for gank/engage); Runeforged Hammer (Jungle path fit for kit profile). Pen: Transcendence, Pendulum Blade, Heartseeker, Titan's Bane. Actives 1/3 · pen ≈ 40.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 40.0):
  1. Transcendence (power, 2400g)
  2. Hydra's Lament (power, 2450g)
  3. Runeforged Hammer (power, 2550g)
  4. Pendulum Blade (pen, active, pen 10.0, 2750g)
  5. Heartseeker (pen, pen 10.0, 3000g)
  6. Titan's Bane (pen, pen 20.0, 3100g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Aladdin — D-tier (role rank #20, model 31.5)

*Magical · Hybrid scaling (STR 113.8% / INT 109.8%)*

Aladdin · Jungle · archetype «mage_jungle» (INT / magical). Kit effects: big ult spike, execute / threshold, pet / deployable, hard crowd control, dash / leap engage, high mobility. Tags: burst, execute, gap_close, hard_cc, long_cd, mobile, pet_zone, shield. Style burst 59%/dps 41%; patch falling (net -9.1, r5 -8.2). Patch axes (r5): damage -8.2. Scale STR 114% / INT 110%. Path: Gem of Isolation (zones & CC — Isolation slow/shred value); Spear of Desolation (flat pen + CDR for ability burst); Spear Of The Magus (multi-hit / shred — stacks Magus passive). Pen: Spear of Desolation, Spear Of The Magus, The World Stone, Obsidian Shard. Actives 1/2 · pen ≈ 50.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/2, pen ≈ 50.0):
  1. Gem of Isolation (power, 2500g)
  2. Spear of Desolation (pen, pen 10.0, 2650g)
  3. Spear Of The Magus (pen, pen 10.0, 2700g)
  4. The World Stone (pen, pen 10.0, 2800g)
  5. Obsidian Shard (pen, pen 20.0, 3050g)
  6. Eye of Erebus (defense, active, 2600g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Pele — D-tier (role rank #21, model 23.0)

*Physical · Strength scaling (STR 91.4% / INT 0%)*

Pele · Jungle · archetype «aa_assassin» (STR / physical). Kit effects: big ult spike, basic-attack kit, self heal / drain, execute / threshold, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, burst, execute, gap_close, heal, long_cd, mobile. Style burst 77%/dps 23%; patch falling (net -7.7, r5 -4.3). Patch axes (r5): damage -4.3. Scale STR 91% / INT 0%. Path: Devourer's Gauntlet (lifesteal stacking); Bloodforge (lifesteal + power for execute/bruiser); Musashi's Dual Swords (attack speed / crit carry core). Pen: The Reaper, Titan's Bane. Actives 1/3 · pen ≈ 30.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 1/3, pen ≈ 30.0):
  1. Devourer's Gauntlet (power, 2500g)
  2. Bloodforge (power, active, 2550g)
  3. Musashi's Dual Swords (power, 2700g)
  4. The Reaper (pen, pen 10.0, 2600g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Demon Blade (power, 2750g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

#### Kali — D-tier (role rank #22, model 16.5)

*Physical · Strength scaling (STR 54.5% / INT 17.1%)*

Kali · Jungle · archetype «sustain_assassin» (STR / physical). Kit effects: protection shred, self heal / drain, heavy healing, execute / threshold, hard crowd control, dash / leap engage. Tags: anti_cc, execute, gap_close, hard_cc, heal, heavy_heal, long_cd, prot_shred. Style burst 0%/dps 100%; patch falling (net -5.6, r5 -5.9). Patch axes (r5): damage -5.9. Scale STR 54% / INT 17%. Path: Jotunn's Revenge (CDR + pen for gank/engage); Transcendence (penetration required for damage role); Bloodforge (lifesteal + power for execute/bruiser). Pen: Jotunn's Revenge, Transcendence, Pendulum Blade, Titan's Bane. Actives 2/3 · pen ≈ 35.

- **Starter:** Bumba's Cudgel
- **Buy order** (actives 2/3, pen ≈ 35.0):
  1. Jotunn's Revenge (power, pen 5.0, 2400g)
  2. Transcendence (power, 2400g)
  3. Bloodforge (power, active, 2550g)
  4. Pendulum Blade (pen, active, pen 10.0, 2750g)
  5. Titan's Bane (pen, pen 20.0, 3100g)
  6. Breastplate of Valor (defense, 2400g)
- **Relics:** Purification Beads (38.0), Blink Rune (32.4)

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
**Common role items (not ordered as a build):** Shifter's Shield, Freya's Tears, Genji's Guard, Breastplate of Valor, Draconic Scale, Stone of Binding, Umbral Link, Berserker's Shield

### God-specific kit builds (use these)

#### Sun Wukong — S-tier (role rank #1, model 81.3)

*Physical · Strength scaling (STR 113.9% / INT 45.7%)*

Sun Wukong · Solo · archetype «bruiser_solo» (STR / physical). Kit effects: big ult spike, execute / threshold, hard crowd control, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, dot, execute, hard_cc, heal, high_cc, long_cd. Style burst 65%/dps 35%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 114% / INT 46%. Path: Chandra's Grace (team aura / support core); Amanita Charm (Solo path fit for kit profile); Runeforged Hammer (Solo path fit for kit profile). Actives 1/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Amanita Charm (defense, active, 2350g)
  3. Runeforged Hammer (power, 2550g)
  4. Stygian Anchor (counter, 2550g)
  5. Draconic Scale (defense, 2700g)
  6. Hussar's Wings (defense, 3500g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Chaac — S-tier (role rank #2, model 77.0)

*Physical · Strength scaling (STR 97.1% / INT 44.1%)*

Chaac · Solo · archetype «sustain_solo» (STR / physical). Kit effects: channel / cast time, big ult spike, self heal / drain, pet / deployable, hard crowd control, dash / leap engage. Tags: anti_cc, channel, dot, gap_close, hard_cc, heal, long_cd, pet_zone. Style burst 39%/dps 61%; patch stable (net +0.8, r5 +0.0). Patch axes (r5): damage +0.4, general +0.4, utility -0.0. Scale STR 97% / INT 44%. Path: Shifter's Shield (offline hybrid tank); Chandra's Grace (team aura / support core); Spectral Armor (mitigate enemy crit (Spectral line)). Actives 1/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2650g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Spectral Armor (mitigate, 2300g)
  4. Shield of the Phoenix (mitigate, 2400g)
  5. Sanguine Lash (power, active, 2650g)
  6. Draconic Scale (defense, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Osiris — S-tier (role rank #3, model 73.6)

*Physical · Strength scaling (STR 65.9% / INT 0%)*

Osiris · Solo · archetype «tank_solo» (STR / physical). Kit effects: basic-attack kit, attack-speed steroid, pet / deployable, hard crowd control, dash / leap engage, lots of CC. Tags: aa, as_steroid, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone. Style burst 26%/dps 74%; patch stable (net -0.3, r5 +0.0). Patch axes (r5): general -0.2, attack_speed -0.1, damage -0.0. Scale STR 66% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Chandra's Grace (team aura / support core); Breastplate of Valor (physical CDR defense). Actives 0/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2650g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Breastplate of Valor (defense, 2400g)
  4. Gladiator's Shield (defense, 2450g)
  5. Stone of Binding (mitigate, 2550g)
  6. Stygian Anchor (counter, 2550g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Jormungandr — A-tier (role rank #4, model 73.4)

*Magical · Intelligence scaling (STR 27.9% / INT 51.4%)*

Jormungandr · Solo · archetype «mage_solo» (INT / magical). Kit effects: channel / cast time, big ult spike, hard crowd control, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, channel, dot, hard_cc, heal, high_cc, long_cd. Style burst 63%/dps 37%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): general -0.2, utility +0.1, damage +0.0. Scale STR 28% / INT 51%. Path: Shifter's Shield (offline hybrid tank); Prophetic Cloak (tenacity / anti-CC bulk); Gem of Isolation (zones & CC — Isolation slow/shred value). Actives 1/2 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2650g)
  2. Prophetic Cloak (defense, 2400g)
  3. Gem of Isolation (power, 2500g)
  4. Stone of Binding (mitigate, 2550g)
  5. Stygian Anchor (counter, 2550g)
  6. Doublet of Binding (mitigate, active, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Bellona — A-tier (role rank #5, model 69.0)

*Physical · Strength scaling (STR 69.9% / INT 0%)*

Bellona · Solo · archetype «sustain_solo» (STR / physical). Kit effects: basic-attack kit, self heal / drain, shields, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, burst, gap_close, hard_cc, heal, heavy_shield, high_cc. Style burst 64%/dps 36%; patch volatile (net +0.4, r5 +0.6). Patch axes (r5): damage +0.6. Scale STR 70% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Gauntlet of Thebes (team aura / support core); Leviathan's Hide (Solo path fit for kit profile). Actives 0/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2650g)
  2. Gauntlet of Thebes (defense, 2200g)
  3. Leviathan's Hide (mitigate, 2500g)
  4. Stone of Binding (mitigate, 2550g)
  5. Wyrmskin Hide (mitigate, 2600g)
  6. Avenging Blade (power, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Hua Mulan — A-tier (role rank #6, model 68.5)

*Physical · Strength scaling (STR 94.0% / INT 0%)*

Hua Mulan · Solo · archetype «bruiser_solo» (STR / physical). Kit effects: big ult spike, attack-speed steroid, hard crowd control, dash / leap engage, CC immunity in kit, lots of CC. Tags: anti_cc, as_steroid, burst, gap_close, hard_cc, heal, high_cc, long_cd. Style burst 80%/dps 20%; patch stable (net -0.2, r5 +0.0). Patch axes (r5): general -0.2, cooldown -0.0, attack_speed +0.0. Scale STR 94% / INT 0%. Path: Shield of the Phoenix (shield / phoenix-style bulk); Prophetic Cloak (tenacity / anti-CC bulk); Stone of Binding (Stone of Binding — CC setup shred). Actives 0/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shield of the Phoenix (mitigate, 2400g)
  2. Prophetic Cloak (defense, 2400g)
  3. Stone of Binding (mitigate, 2550g)
  4. Stygian Anchor (counter, 2550g)
  5. Brawler’s Beat Stick (counter, 2550g)
  6. Hussar's Wings (defense, 3500g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Mordred — B-tier (role rank #7, model 67.9)

*Physical · Strength scaling (STR 77.5% / INT 45.8%)*

Mordred · Solo · archetype «sustain_solo» (STR / physical). Kit effects: damage over time, channel / cast time, big ult spike, attack-speed steroid, self heal / drain, heavy healing. Tags: anti_cc, as_steroid, burst, channel, dot, gap_close, hard_cc, heal. Style burst 58%/dps 42%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): survivability +0.0, general -0.0, heal +0.0. Scale STR 77% / INT 46%. Path: Chandra's Grace (team aura / support core); Shield of the Phoenix (shield / phoenix-style bulk); Contagion (team anti-heal aura). Actives 1/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Shield of the Phoenix (mitigate, 2400g)
  3. Contagion (defense, 2400g)
  4. Gladiator's Shield (defense, 2450g)
  5. Mantle Of Discord (mitigate, 2600g)
  6. Sanguine Lash (power, active, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Odin — B-tier (role rank #8, model 65.4)

*Physical · Strength scaling (STR 65.2% / INT 34.1%)*

Odin · Solo · archetype «shield_solo» (STR / physical). Kit effects: big ult spike, basic-attack kit, attack-speed steroid, shields, hard crowd control, dash / leap engage. Tags: aa, as_steroid, burst, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 64%/dps 36%; patch volatile (net +1.1, r5 +0.1). Patch axes (r5): damage +0.1, survivability +0.1. Scale STR 65% / INT 34%. Path: Eye of Erebus (Solo path fit for kit profile); Chandra's Grace (team aura / support core); Shield of the Phoenix (shield / phoenix-style bulk). Actives 3/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 3/3, pen ≈ 0.0):
  1. Eye of Erebus (defense, active, 2600g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Shield of the Phoenix (mitigate, 2400g)
  4. Phoenix Feather (mitigate, active, 2400g)
  5. Mystical Mail (defense, 2550g)
  6. Heartwood Charm (defense, active, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Amaterasu — B-tier (role rank #9, model 62.1)

*Physical · Hybrid scaling (STR 47.0% / INT 51.3%)*

Amaterasu · Solo · archetype «sustain_solo» (STR / physical). Kit effects: big ult spike, self heal / drain, hard crowd control, dash / leap engage, CC immunity in kit, sustained DPS. Tags: anti_cc, dot, gap_close, hard_cc, heal, long_cd, self_sustain, shield. Style burst 2%/dps 98%; patch volatile (net +1.3, r5 +0.6). Patch axes (r5): damage +0.6. Scale STR 47% / INT 51%. Path: Amanita Charm (Solo path fit for kit profile); Contagion (team anti-heal aura); Gladiator's Shield (Solo path fit for kit profile). Actives 3/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 3/3, pen ≈ 0.0):
  1. Amanita Charm (defense, active, 2350g)
  2. Contagion (defense, 2400g)
  3. Gladiator's Shield (defense, 2450g)
  4. Leviathan's Hide (mitigate, 2500g)
  5. Glorious Pridwen (defense, active, 2550g)
  6. Sanguine Lash (power, active, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Xing Tian — B-tier (role rank #10, model 61.9)

*Magical · Intelligence scaling (STR 0% / INT 57.1%)*

Xing Tian · Solo · archetype «mage_solo» (INT / magical). Kit effects: damage over time, channel / cast time, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, channel, dot, gap_close, hard_cc, heal, heavy_dot. Style burst 65%/dps 35%; patch rising (net +1.0, r5 +1.0). Patch axes (r5): general +1.0. Scale STR 0% / INT 57%. Path: Shifter's Shield (offline hybrid tank); Chandra's Grace (team aura / support core); Shield of the Phoenix (shield / phoenix-style bulk). Actives 0/2 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2650g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Shield of the Phoenix (mitigate, 2400g)
  4. Contagion (defense, 2400g)
  5. Gem of Isolation (power, 2500g)
  6. Freya's Tears (defense, 2600g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Cabrakan — B-tier (role rank #11, model 61.2)

*Magical · Hybrid scaling (STR 75.1% / INT 51.2%)*

Cabrakan · Solo · archetype «shield_solo» (INT / magical). Kit effects: channel / cast time, big ult spike, basic-attack kit, hard crowd control, ally buffs / auras, lots of CC. Tags: aa, channel, hard_cc, heal, high_cc, long_cd, shield, team_buff. Style burst 54%/dps 46%; patch falling (net -2.2, r5 -2.3). Patch axes (r5): survivability -1.0, damage -0.9, heal -0.3. Scale STR 75% / INT 51%. Path: Chandra's Grace (team aura / support core); Amanita Charm (Solo path fit for kit profile); Shield of the Phoenix (shield / phoenix-style bulk). Actives 1/2 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Amanita Charm (defense, active, 2350g)
  3. Shield of the Phoenix (mitigate, 2400g)
  4. Breastplate of Valor (defense, 2400g)
  5. Stone of Binding (mitigate, 2550g)
  6. Mystical Mail (defense, 2550g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Gilgamesh — C-tier (role rank #12, model 61.0)

*Physical · Strength scaling (STR 72.8% / INT 0%)*

Gilgamesh · Solo · archetype «bruiser_solo» (STR / physical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, lots of CC, burst combos. Tags: burst, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, team_buff. Style burst 77%/dps 23%; patch new (net -0.3, r5 +0.0). Patch axes (r5): damage -1.3, general +0.9, mana +0.1. Scale STR 73% / INT 0%. Path: Gauntlet of Thebes (team aura / support core); Breastplate of Valor (physical CDR defense); Kinetic Cuirass (Solo path fit for kit profile). Actives 0/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Breastplate of Valor (defense, 2400g)
  3. Kinetic Cuirass (mitigate, 2400g)
  4. Runeforged Hammer (power, 2550g)
  5. Freya's Tears (defense, 2600g)
  6. Hussar's Wings (defense, 3500g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Hercules — C-tier (role rank #13, model 58.8)

*Physical · Strength scaling (STR 84.8% / INT 0%)*

Hercules · Solo · archetype «sustain_solo» (STR / physical). Kit effects: big ult spike, attack-speed steroid, self heal / drain, hard crowd control, dash / leap engage, lots of CC. Tags: as_steroid, gap_close, hard_cc, heal, high_cc, long_cd, self_sustain, sustained. Style burst 37%/dps 63%; patch volatile (net -1.1, r5 +0.0). Patch axes (r5): damage -0.7, survivability -0.4, general -0.2. Scale STR 85% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Spectral Armor (mitigate enemy crit (Spectral line)); Shield of the Phoenix (shield / phoenix-style bulk). Actives 0/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2650g)
  2. Spectral Armor (mitigate, 2300g)
  3. Shield of the Phoenix (mitigate, 2400g)
  4. Contagion (defense, 2400g)
  5. Freya's Tears (defense, 2600g)
  6. Avenging Blade (power, 2650g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Guan Yu — C-tier (role rank #14, model 57.7)

*Physical · Strength scaling (STR 42.4% / INT 13.3%)*

Guan Yu · Solo · archetype «sustain_solo» (STR / physical). Kit effects: damage over time, attack-speed steroid, self heal / drain, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, dot, gap_close, hard_cc, heal, heavy_dot, long_cd, pet_zone. Style burst 15%/dps 85%; patch stable (net +0.2, r5 +0.0). Patch axes (r5): general +0.3, survivability -0.1, cooldown -0.1. Scale STR 42% / INT 13%. Path: Eye of Erebus (Solo path fit for kit profile); Chandra's Grace (team aura / support core); Berserker's Shield (Solo path fit for kit profile). Actives 1/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Eye of Erebus (defense, active, 2600g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Berserker's Shield (defense, 2400g)
  4. Gladiator's Shield (defense, 2450g)
  5. Stone of Binding (mitigate, 2550g)
  6. Draconic Scale (defense, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Achilles — C-tier (role rank #15, model 57.7)

*Physical · Strength scaling (STR 82.9% / INT 0%)*

Achilles · Solo · archetype «sustain_solo» (STR / physical). Kit effects: big ult spike, basic-attack kit, self heal / drain, execute / threshold, shields, hard crowd control. Tags: aa, anti_cc, execute, gap_close, hard_cc, heal, heavy_shield, long_cd. Style burst 30%/dps 70%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, attack_speed +0.0, survivability +0.0. Scale STR 83% / INT 0%. Path: Shifter's Shield (offline hybrid tank); Chandra's Grace (team aura / support core); Amanita Charm (Solo path fit for kit profile). Actives 2/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 2/3, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2650g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Amanita Charm (defense, active, 2350g)
  4. Phoenix Feather (mitigate, active, 2400g)
  5. Contagion (defense, 2400g)
  6. Hussar's Wings (defense, 3500g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Hades — C-tier (role rank #16, model 57.3)

*Magical · Intelligence scaling (STR 0% / INT 83.3%)*

Hades · Solo · archetype «sustain_solo» (INT / magical). Kit effects: damage over time, channel / cast time, big ult spike, self heal / drain, hard crowd control, dash / leap engage. Tags: anti_cc, channel, dot, gap_close, hard_cc, heal, heavy_dot, high_cc. Style burst 45%/dps 55%; patch stable (net +0.4, r5 +0.0). Patch axes (r5): general +0.4, survivability -0.0, heal -0.0. Scale STR 0% / INT 83%. Path: Shifter's Shield (offline hybrid tank); Chandra's Grace (team aura / support core); Contagion (team anti-heal aura). Actives 0/2 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2650g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Contagion (defense, 2400g)
  4. Prophetic Cloak (defense, 2400g)
  5. Gladiator's Shield (defense, 2450g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Artio — D-tier (role rank #17, model 51.7)

*Magical · Hybrid scaling (STR 52.4% / INT 36.2%)*

Artio · Solo · archetype «sustain_solo» (INT / magical). Kit effects: protection shred, channel / cast time, big ult spike, heavy healing, pet / deployable, hard crowd control. Tags: channel, hard_cc, heal, heavy_heal, high_cc, long_cd, mobile, pet_zone. Style burst 83%/dps 17%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): general -0.1, damage +0.1, mana -0.1. Scale STR 52% / INT 36%. Path: Shifter's Shield (offline hybrid tank); Breastplate of Valor (physical CDR defense); Gem of Isolation (zones & CC — Isolation slow/shred value). Actives 0/2 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Shifter's Shield (defense, 2650g)
  2. Breastplate of Valor (defense, 2400g)
  3. Gem of Isolation (power, 2500g)
  4. Stone of Binding (mitigate, 2550g)
  5. Stygian Anchor (counter, 2550g)
  6. Draconic Scale (defense, 2700g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Cerberus — D-tier (role rank #18, model 39.3)

*Magical · Intelligence scaling (STR 0% / INT 42.4%)*

Cerberus · Solo · archetype «sustain_solo» (INT / magical). Kit effects: self heal / drain, pet / deployable, hard crowd control, dash / leap engage, burst combos, lots of CC. Tags: dot, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, self_sustain. Style burst 100%/dps 0%; patch falling (net -1.8, r5 -1.8). Patch axes (r5): survivability -1.2, general -0.6. Scale STR 0% / INT 42%. Path: Eye of Erebus (Solo path fit for kit profile); Chandra's Grace (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk). Actives 1/2 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Eye of Erebus (defense, active, 2600g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Alchemist Coat (mitigate, 2350g)
  4. Kinetic Cuirass (mitigate, 2400g)
  5. Contagion (defense, 2400g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (42.0), Aegis of Acceleration (32.0)

#### Thor — D-tier (role rank #19, model 32.1)

*Physical · Strength scaling (STR 79.1% / INT 0%)*

Thor · Solo · archetype «tank_solo» (STR / physical). Kit effects: channel / cast time, big ult spike, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, channel, gap_close, hard_cc, high_cc, long_cd, pet_zone, ult_nuke. Style burst 69%/dps 31%; patch falling (net -3.8, r5 -3.5). Patch axes (r5): damage -2.7, heal -0.4, survivability -0.4. Scale STR 79% / INT 0%. Path: Chandra's Grace (team aura / support core); Breastplate of Valor (physical CDR defense; patch falling — extra bulk/CDR); Stone of Binding (Stone of Binding — CC setup shred). Actives 1/3 · pen ≈ 0.

- **Starter:** Warrior's Axe
- **Buy order** (actives 1/3, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Breastplate of Valor (defense, 2400g)
  3. Stone of Binding (mitigate, 2550g)
  4. Glorious Pridwen (defense, active, 2550g)
  5. Freya's Tears (defense, 2600g)
  6. Mantle Of Discord (mitigate, 2600g)
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
**Common role items (not ordered as a build):** Spectral Armor, Freya's Tears, Genji's Guard, Breastplate of Valor, Shifter's Shield, Stone of Binding, Umbral Link, Screeching Gargoyle

### God-specific kit builds (use these)

#### Jormungandr — S-tier (role rank #1, model 73.4)

*Magical · Intelligence scaling (STR 27.9% / INT 51.4%)*

Jormungandr · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, big ult spike, hard crowd control, CC immunity in kit, lots of CC, multi-hit / ticks. Tags: anti_cc, burst, channel, dot, hard_cc, heal, high_cc, long_cd. Style burst 63%/dps 37%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): general -0.2, utility +0.1, damage +0.0. Scale STR 28% / INT 51%. Path: Gauntlet of Thebes (team aura / support core); Spectral Armor (mitigate enemy crit (Spectral line)); Chandra's Grace (team aura / support core). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Spectral Armor (mitigate, 2300g)
  3. Chandra's Grace (mitigate, 2300g)
  4. Alchemist Coat (mitigate, 2350g)
  5. Draconic Scale (defense, 2700g)
  6. Doublet of Binding (mitigate, active, 2700g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Charon — S-tier (role rank #2, model 71.5)

*Magical · Intelligence scaling (STR 0% / INT 45.0%)*

Charon · Support · archetype «shield_support» (INT / magical). Kit effects: pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, burst combos. Tags: anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, mobile, pet_zone. Style burst 96%/dps 4%; patch rising (net +2.6, r5 +0.0). Patch axes (r5): general +0.0. Scale STR 0% / INT 45%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Chandra's Grace (team aura / support core); Shield of the Phoenix (shield / phoenix-style bulk). Actives 0/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Shield of the Phoenix (mitigate, 2400g)
  4. Breastplate of Valor (defense, 2400g)
  5. Gem of Isolation (power, 2500g)
  6. Shogun's Ofuda (mitigate, 2500g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Athena — S-tier (role rank #3, model 66.3)

*Magical · Intelligence scaling (STR 12.0% / INT 66.9%)*

Athena · Support · archetype «shield_support» (INT / magical). Kit effects: channel / cast time, big ult spike, basic-attack kit, dash / leap engage, ally buffs / auras, CC immunity in kit. Tags: aa, anti_cc, burst, channel, gap_close, high_cc, long_cd, shield. Style burst 72%/dps 28%; patch stable (net +0.2, r5 +0.0). Patch axes (r5): general +0.2, cooldown +0.0, damage +0.0. Scale STR 12% / INT 67%. Path: Chandra's Grace (team aura / support core); Genji's Guard (magic prot + CDR for mages); Kinetic Cuirass (Support path fit for kit profile). Actives 2/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Genji's Guard (defense, 2350g)
  3. Kinetic Cuirass (mitigate, 2400g)
  4. Phoenix Feather (mitigate, active, 2400g)
  5. Heartwood Charm (defense, active, 2650g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Ares — A-tier (role rank #4, model 65.4)

*Magical · Intelligence scaling (STR 33.6% / INT 29.6%)*

Ares · Support · archetype «shield_support» (INT / magical). Kit effects: damage over time, channel / cast time, big ult spike, pet / deployable, hard crowd control, ally buffs / auras. Tags: anti_cc, burst, channel, dot, hard_cc, heal, heavy_dot, long_cd. Style burst 84%/dps 16%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.2, damage +0.0, survivability -0.0. Scale STR 34% / INT 30%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Shield of the Phoenix (shield / phoenix-style bulk); Contagion (team anti-heal aura). Actives 0/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Shield of the Phoenix (mitigate, 2400g)
  3. Contagion (defense, 2400g)
  4. Mystical Mail (defense, 2550g)
  5. Freya's Tears (defense, 2600g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Aphrodite — A-tier (role rank #5, model 64.5)

*Magical · Intelligence scaling (STR 0% / INT 102.0%)*

Aphrodite · Support · archetype «heal_support» (INT / magical). Kit effects: big ult spike, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, multi-hit / ticks. Tags: anti_cc, burst, dot, gap_close, hard_cc, heal, long_cd, team_buff. Style burst 60%/dps 40%; patch volatile (net +1.1, r5 +0.1). Patch axes (r5): heal +0.1. Scale STR 0% / INT 102%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Chandra's Grace (team aura / support core); Shield of the Phoenix (shield / phoenix-style bulk). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Shield of the Phoenix (mitigate, 2400g)
  4. Magi's Cloak (defense, 2400g)
  5. Heartwood Charm (defense, active, 2650g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Yemoja — A-tier (role rank #6, model 63.8)

*Magical · Intelligence scaling (STR 0% / INT 56.5%)*

Yemoja · Support · archetype «heal_support» (INT / magical). Kit effects: basic-attack kit, attack-speed steroid, heavy healing, hard crowd control, ally buffs / auras, lots of CC. Tags: aa, as_steroid, burst, dot, hard_cc, heal, heavy_heal, high_cc. Style burst 70%/dps 30%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): damage -0.1, general +0.1, survivability -0.0. Scale STR 0% / INT 56%. Path: Gauntlet of Thebes (team aura / support core); Spectral Armor (mitigate enemy crit (Spectral line)); Rod Of Asclepius (heal amp / team sustain). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Spectral Armor (mitigate, 2300g)
  3. Rod Of Asclepius (power, active, 2350g)
  4. Shield of the Phoenix (mitigate, 2400g)
  5. Shogun's Ofuda (mitigate, 2500g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Ymir — A-tier (role rank #7, model 62.5)

*Magical · Intelligence scaling (STR 12.3% / INT 117.7%)*

Ymir · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, big ult spike, basic-attack kit, pet / deployable, hard crowd control, low mobility. Tags: aa, anti_cc, burst, channel, hard_cc, high_cc, immobile, long_cd. Style burst 60%/dps 40%; patch volatile (net +1.8, r5 +0.0). Patch axes (r5): damage +1.0, survivability +0.4, general +0.3. Scale STR 12% / INT 118%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Chandra's Grace (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Alchemist Coat (mitigate, 2350g)
  4. Gem of Isolation (power, 2500g)
  5. Doublet of Binding (mitigate, active, 2700g)
  6. Resolute Mantle (mitigate, 2750g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (42.0)

#### Baron Samedi — B-tier (role rank #8, model 62.1)

*Magical · Intelligence scaling (STR 0% / INT 69.6%)*

Baron Samedi · Support · archetype «lockdown_support» (INT / magical). Kit effects: damage over time, channel / cast time, execute / threshold, pet / deployable, hard crowd control, ally buffs / auras. Tags: burst, channel, dot, execute, hard_cc, heal, heavy_dot, high_cc. Style burst 71%/dps 29%; patch volatile (net +1.1, r5 +0.0). Patch axes (r5): heal +0.9, general +0.3, damage -0.1. Scale STR 0% / INT 70%. Path: Kinetic Cuirass (Support path fit for kit profile); Contagion (team anti-heal aura); Gem of Isolation (zones & CC — Isolation slow/shred value). Actives 0/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Kinetic Cuirass (mitigate, 2400g)
  2. Contagion (defense, 2400g)
  3. Gem of Isolation (power, 2500g)
  4. Stone of Binding (mitigate, 2550g)
  5. Ethereal Staff (mitigate, 2550g)
  6. Freya's Tears (defense, 2600g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Xing Tian — B-tier (role rank #9, model 61.9)

*Magical · Intelligence scaling (STR 0% / INT 57.1%)*

Xing Tian · Support · archetype «lockdown_support» (INT / magical). Kit effects: damage over time, channel / cast time, basic-attack kit, hard crowd control, dash / leap engage, CC immunity in kit. Tags: aa, anti_cc, channel, dot, gap_close, hard_cc, heal, heavy_dot. Style burst 65%/dps 35%; patch rising (net +1.0, r5 +1.0). Patch axes (r5): general +1.0. Scale STR 0% / INT 57%. Path: Chandra's Grace (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk); Amanita Charm (Support path fit for kit profile). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Alchemist Coat (mitigate, 2350g)
  3. Amanita Charm (defense, active, 2350g)
  4. Genji's Guard (defense, 2350g)
  5. Contagion (defense, 2400g)
  6. Magi's Cloak (defense, 2400g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Atlas — B-tier (role rank #10, model 61.4)

*Magical · Intelligence scaling (STR 0% / INT 51.4%)*

Atlas · Support · archetype «lockdown_support» (INT / magical). Kit effects: protection shred, pet / deployable, hard crowd control, dash / leap engage, ally buffs / auras, lots of CC. Tags: burst, dot, gap_close, hard_cc, high_cc, long_cd, pet_zone, prot_shred. Style burst 79%/dps 21%; patch new (net -0.8, r5 -0.4). Patch axes (r5): utility -0.8, general +0.7, attack_speed -0.5. Scale STR 0% / INT 51%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Shield of the Phoenix (shield / phoenix-style bulk); Gem of Isolation (zones & CC — Isolation slow/shred value). Actives 0/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Shield of the Phoenix (mitigate, 2400g)
  3. Gem of Isolation (power, 2500g)
  4. Spirit Robe (mitigate, 2500g)
  5. Void Stone (defense, 2550g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Cabrakan — B-tier (role rank #11, model 61.2)

*Magical · Hybrid scaling (STR 75.1% / INT 51.2%)*

Cabrakan · Support · archetype «shield_support» (INT / magical). Kit effects: channel / cast time, big ult spike, basic-attack kit, hard crowd control, ally buffs / auras, lots of CC. Tags: aa, channel, hard_cc, heal, high_cc, long_cd, shield, team_buff. Style burst 54%/dps 46%; patch falling (net -2.2, r5 -2.3). Patch axes (r5): survivability -1.0, damage -0.9, heal -0.3. Scale STR 75% / INT 51%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Chandra's Grace (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk). Actives 0/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Alchemist Coat (mitigate, 2350g)
  4. Breastplate of Valor (defense, 2400g)
  5. Prophetic Cloak (defense, 2400g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Sobek — B-tier (role rank #12, model 59.3)

*Magical · Intelligence scaling (STR 0% / INT 50.0%)*

Sobek · Support · archetype «lockdown_support» (INT / magical). Kit effects: self heal / drain, execute / threshold, pet / deployable, hard crowd control, dash / leap engage, CC immunity in kit. Tags: anti_cc, burst, dot, execute, gap_close, hard_cc, heal, high_cc. Style burst 81%/dps 19%; patch stable (net +0.4, r5 +0.0). Patch axes (r5): general +0.4, cooldown -0.0, damage +0.0. Scale STR 0% / INT 50%. Path: Chandra's Grace (team aura / support core); Shield of the Phoenix (shield / phoenix-style bulk); Freya's Tears (raw protections / HP). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Shield of the Phoenix (mitigate, 2400g)
  3. Freya's Tears (defense, 2600g)
  4. Doublet of Binding (mitigate, active, 2700g)
  5. Resolute Mantle (mitigate, 2750g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Ganesha — B-tier (role rank #13, model 59.1)

*Magical · Intelligence scaling (STR 0% / INT 75.1%)*

Ganesha · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, big ult spike, execute / threshold, pet / deployable, hard crowd control, dash / leap engage. Tags: burst, channel, dot, execute, gap_close, hard_cc, high_cc, long_cd. Style burst 84%/dps 16%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): damage -0.1, utility -0.1, survivability +0.0. Scale STR 0% / INT 75%. Path: Gauntlet of Thebes (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk); Shield of the Phoenix (shield / phoenix-style bulk). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Alchemist Coat (mitigate, 2350g)
  3. Shield of the Phoenix (mitigate, 2400g)
  4. Contagion (defense, 2400g)
  5. Stygian Anchor (counter, 2550g)
  6. Doublet of Binding (mitigate, active, 2700g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Guan Yu — C-tier (role rank #14, model 57.7)

*Physical · Strength scaling (STR 42.4% / INT 13.3%)*

Guan Yu · Support · archetype «heal_support» (STR / physical). Kit effects: damage over time, attack-speed steroid, self heal / drain, pet / deployable, hard crowd control, dash / leap engage. Tags: as_steroid, dot, gap_close, hard_cc, heal, heavy_dot, long_cd, pet_zone. Style burst 15%/dps 85%; patch stable (net +0.2, r5 +0.0). Patch axes (r5): general +0.3, survivability -0.1, cooldown -0.1. Scale STR 42% / INT 13%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Breastplate of Valor (physical CDR defense); Jotunn's Revenge (CDR + pen for gank/engage). Pen: Jotunn's Revenge. Actives 1/2 · pen ≈ 5.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 5.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Breastplate of Valor (defense, 2400g)
  3. Jotunn's Revenge (power, pen 5.0, 2400g)
  4. Stone of Binding (mitigate, 2550g)
  5. Doublet of Binding (mitigate, active, 2700g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Horus — C-tier (role rank #15, model 57.4)

*Physical · Strength scaling (STR 74.4% / INT 0%)*

Horus · Support · archetype «shield_support» (STR / physical). Kit effects: channel / cast time, self heal / drain, heavy healing, hard crowd control, dash / leap engage, ally buffs / auras. Tags: anti_cc, channel, gap_close, hard_cc, heal, heavy_heal, high_cc, long_cd. Style burst 30%/dps 70%; patch falling (net -3.0, r5 -3.0). Patch axes (r5): damage -1.6, cooldown -0.8, heal -0.7. Scale STR 74% / INT 0%. Path: Spectral Armor (Support path fit for kit profile); Alchemist Coat (tenacity / anti-CC bulk); Shield of the Phoenix (shield / phoenix-style bulk). Actives 0/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Alchemist Coat (mitigate, 2350g)
  3. Shield of the Phoenix (mitigate, 2400g)
  4. Gladiator's Shield (defense, 2450g)
  5. Freya's Tears (defense, 2600g)
  6. Shifter's Shield (defense, 2650g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Bacchus — C-tier (role rank #16, model 56.4)

*Magical · Intelligence scaling (STR 30.6% / INT 24.7%)*

Bacchus · Support · archetype «lockdown_support» (INT / magical). Kit effects: channel / cast time, basic-attack kit, hard crowd control, dash / leap engage, burst combos, lots of CC. Tags: aa, channel, gap_close, hard_cc, heal, high_cc, long_cd, utility. Style burst 100%/dps 0%; patch stable (net +0.3, r5 +0.0). Patch axes (r5): general +0.3, damage +0.0, survivability +0.0. Scale STR 31% / INT 25%. Path: Chandra's Grace (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk); Shield of the Phoenix (shield / phoenix-style bulk). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Alchemist Coat (mitigate, 2350g)
  3. Shield of the Phoenix (mitigate, 2400g)
  4. Breastplate of Valor (defense, 2400g)
  5. Heartwood Charm (defense, active, 2650g)
  6. Draconic Scale (defense, 2700g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Khepri — C-tier (role rank #17, model 55.8)

*Magical · Intelligence scaling (STR 0% / INT 30.5%)*

Khepri · Support · archetype «shield_support» (INT / magical). Kit effects: execute / threshold, hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, lots of CC. Tags: anti_cc, dot, execute, gap_close, hard_cc, high_cc, long_cd, shield. Style burst 0%/dps 0%; patch new (net +0.6, r5 +0.0). Patch axes (r5): utility +1.0, damage -0.5, general +0.1. Scale STR 0% / INT 30%. Path: Gauntlet of Thebes (team aura / support core); Chandra's Grace (team aura / support core); Genji's Guard (magic prot + CDR for mages). Actives 0/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 0/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Chandra's Grace (mitigate, 2300g)
  3. Genji's Guard (defense, 2350g)
  4. Shield of the Phoenix (mitigate, 2400g)
  5. Gem of Isolation (power, 2500g)
  6. Hussar's Wings (defense, 3500g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Artio — C-tier (role rank #18, model 51.7)

*Magical · Hybrid scaling (STR 52.4% / INT 36.2%)*

Artio · Support · archetype «shield_support» (INT / magical). Kit effects: protection shred, channel / cast time, big ult spike, heavy healing, pet / deployable, hard crowd control. Tags: channel, hard_cc, heal, heavy_heal, high_cc, long_cd, mobile, pet_zone. Style burst 83%/dps 17%; patch stable (net -0.1, r5 +0.0). Patch axes (r5): general -0.1, damage +0.1, mana -0.1. Scale STR 52% / INT 36%. Path: Chandra's Grace (team aura / support core); Shield of the Phoenix (shield / phoenix-style bulk); Phoenix Feather (shield / phoenix-style bulk). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Shield of the Phoenix (mitigate, 2400g)
  3. Phoenix Feather (mitigate, active, 2400g)
  4. Stygian Anchor (counter, 2550g)
  5. Void Stone (defense, 2550g)
  6. Freya's Tears (defense, 2600g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Sylvanus — D-tier (role rank #19, model 51.5)

*Magical · Intelligence scaling (STR 0% / INT 41.4%)*

Sylvanus · Support · archetype «lockdown_support» (INT / magical). Kit effects: damage over time, protection shred, execute / threshold, pet / deployable, hard crowd control, low mobility. Tags: dot, execute, hard_cc, heal, heavy_dot, high_cc, immobile, long_cd. Style burst 0%/dps 0%; patch stable (net +0.0, r5 +0.0). Patch axes (r5): general +0.1, heal -0.1, survivability -0.1. Scale STR 0% / INT 41%. Path: Gauntlet of Thebes (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk); Gem of Isolation (zones & CC — Isolation slow/shred value). Actives 2/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 2/2, pen ≈ 0.0):
  1. Gauntlet of Thebes (defense, 2200g)
  2. Alchemist Coat (mitigate, 2350g)
  3. Gem of Isolation (power, 2500g)
  4. Stygian Anchor (counter, 2550g)
  5. Heartwood Charm (defense, active, 2650g)
  6. Doublet of Binding (mitigate, active, 2700g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (42.0)

#### Geb — D-tier (role rank #20, model 46.0)

*Magical · Intelligence scaling (STR 0% / INT 36.3%)*

Geb · Support · archetype «shield_support» (INT / magical). Kit effects: hard crowd control, dash / leap engage, ally buffs / auras, CC immunity in kit, lots of CC, shields. Tags: anti_cc, dot, gap_close, hard_cc, high_cc, long_cd, shield, team_buff. Style burst 66%/dps 34%; patch volatile (net -2.4, r5 +0.0). Patch axes (r5): general -0.9, damage -0.7, survivability -0.6. Scale STR 0% / INT 36%. Path: Spectral Armor (mitigate enemy crit (Spectral line)); Alchemist Coat (tenacity / anti-CC bulk); Breastplate of Valor (physical CDR defense). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Spectral Armor (mitigate, 2300g)
  2. Alchemist Coat (mitigate, 2350g)
  3. Breastplate of Valor (defense, 2400g)
  4. Contagion (defense, 2400g)
  5. Phoenix Feather (mitigate, active, 2400g)
  6. Stone of Binding (mitigate, 2550g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

#### Cerberus — D-tier (role rank #21, model 39.3)

*Magical · Intelligence scaling (STR 0% / INT 42.4%)*

Cerberus · Support · archetype «lockdown_support» (INT / magical). Kit effects: self heal / drain, pet / deployable, hard crowd control, dash / leap engage, burst combos, lots of CC. Tags: dot, gap_close, hard_cc, heal, high_cc, long_cd, pet_zone, self_sustain. Style burst 100%/dps 0%; patch falling (net -1.8, r5 -1.8). Patch axes (r5): survivability -1.2, general -0.6. Scale STR 0% / INT 42%. Path: Chandra's Grace (team aura / support core); Alchemist Coat (tenacity / anti-CC bulk); Stone of Binding (Stone of Binding — CC setup shred). Actives 1/2 · pen ≈ 0.

- **Starter:** Selflessness
- **Buy order** (actives 1/2, pen ≈ 0.0):
  1. Chandra's Grace (mitigate, 2300g)
  2. Alchemist Coat (mitigate, 2350g)
  3. Stone of Binding (mitigate, 2550g)
  4. Stygian Anchor (counter, 2550g)
  5. Heartwood Charm (defense, active, 2650g)
  6. Hussar's Wings (defense, 3500g)
- **Relics:** Purification Beads (46.0), Aegis of Acceleration (32.0)

---
