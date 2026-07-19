# SMITE 2 Conquest Builds — Statistically Weighted

Local statistical weighting: item flat stats (normalized) × role priority vector + passive/active utility tags + cost band + item patch momentum; per-god paths re-scored by kit STR/INT scaling from ability metrics. No external build sites.

> Not scraped from websites. Derived from wiki item stats, ability scaling, and patch-note item/god momentum in `smite2.db`.

## Carry

Conquest duo ADC: sustained basic-attack DPS, crit windows, penetration, and self-heal to stay in lane/fights.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| str | 22% |
| as | 18% |
| crit | 14% |
| pen | 14% |
| ls | 10% |
| bap | 8% |
| hp | 5% |
| int | 4% |
| cdr | 3% |
| pprot | 1% |
| mprot | 1% |

### Role template (best-in-role item scores)

**Starter:** Gilded Arrow (score 27.9, cost 650)
**Starter alts:** Death's Toll (24.2), Leather Cowl (22.4), Selflessness (15.4)
**Upgrade path:** Sharpshooter's Arrow (score 62.2)

**Inventory: 1 starter + 6 items** (starter is separate)

| Starter | **Gilded Arrow** | `27.9` | 650g |

| # | Item | Score | Cost | Stats |
|--:|------|------:|-----:|-------|
| 1 | **Lernaean Bow** | `82.9` | 2500g | str 40.0, as 30.0 |
| 2 | **Musashi's Dual Swords** | `81.1` | 2700g | str 35.0, crit 30.0 |
| 3 | **Death Metal** | `75.0` | 2600g | int 40.0, str 35.0, crit 20.0 |
| 4 | **Avatar's Parashu** | `67.1` | 3700g | str 90.0, pen 10.0 |
| 5 | **Runeforged Hammer** | `46.5` | 2550g | hp 350.0, str 45.0, hpr 3.0 |
| 6 | **Freya's Tears** | `31.9` | 2600g | mprot 35.0, pprot 30.0, cdr 20.0 |

**Relics (scored):** Purification Beads (33.0), Aegis of Acceleration (28.0), Sundering Arc (22.7)

### Top gods in this role (model) + tailored paths

#### Xbalanque — S-tier (role rank #1, model 72.3)

*Physical · Hybrid scaling (STR 37.5% / INT 35.0%)*

Xbalanque as Carry: primary scaling Hybrid (STR 38% / INT 35% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #1).

- **Starter:** Gilded Arrow (`35.8`)
- **6 items:**
  1. Death Metal (`113.7` · 2600g)
  2. Avatar's Parashu (`103.1` · 3700g)
  3. Avenging Blade (`102.7` · 2650g)
  4. Lernaean Bow (`98.9` · 2500g)
  5. Triton's Conch (`66.6` · 2700g)
  6. Freya's Tears (`53.9` · 2600g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Neith — S-tier (role rank #2, model 68.6)

*Physical · Hybrid scaling (STR 67.5% / INT 66.0%)*

Neith as Carry: primary scaling Hybrid (STR 68% / INT 66% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #2).

- **Starter:** Gilded Arrow (`35.8`)
- **6 items:**
  1. Death Metal (`113.7` · 2600g)
  2. Avatar's Parashu (`103.1` · 3700g)
  3. Avenging Blade (`102.7` · 2650g)
  4. Lernaean Bow (`98.9` · 2500g)
  5. Triton's Conch (`66.6` · 2700g)
  6. Freya's Tears (`53.9` · 2600g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Danzaburou — S-tier (role rank #3, model 67.9)

*Physical · Hybrid scaling (STR 78.8% / INT 61.0%)*

Danzaburou as Carry: primary scaling Hybrid (STR 79% / INT 61% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #3).

- **Starter:** Gilded Arrow (`35.8`)
- **6 items:**
  1. Death Metal (`113.7` · 2600g)
  2. Avatar's Parashu (`103.1` · 3700g)
  3. Avenging Blade (`102.7` · 2650g)
  4. Lernaean Bow (`98.9` · 2500g)
  5. Triton's Conch (`66.6` · 2700g)
  6. Freya's Tears (`53.9` · 2600g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

#### Princess Bari — A-tier (role rank #4, model 65.8)

*Magical · Hybrid scaling (STR 43.8% / INT 62.5%)*

Princess Bari as Carry: primary scaling Hybrid (STR 44% / INT 62% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Role model tier A (rank #4).

- **Starter:** Gilded Arrow (`31.0`)
- **6 items:**
  1. Death Metal (`113.7` · 2600g)
  2. Avatar's Parashu (`78.1` · 3700g)
  3. Lernaean Bow (`73.9` · 2500g)
  4. Musashi's Dual Swords (`70.1` · 2700g)
  5. Triton's Conch (`66.6` · 2700g)
  6. Freya's Tears (`41.9` · 2600g)
- **Relics:** Purification Beads (41.0), Aegis of Acceleration (28.0)

---

## Mid

Conquest mid: ability burst and wave clear, intelligence or hybrid power, penetration, cooldown, and mana sustain.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| int | 26% |
| pen | 16% |
| cdr | 14% |
| str | 8% |
| mp | 8% |
| hp | 8% |
| mpr | 6% |
| ls | 6% |
| as | 4% |
| pprot | 2% |
| mprot | 2% |

### Role template (best-in-role item scores)

**Starter:** Conduit Gem (score 31.2, cost 650)
**Starter alts:** Sands Of Time (23.9), Vampiric Shroud (22.1), Bluestone Pendant (19.0)
**Upgrade path:** Heroism (score 23.1)

**Inventory: 1 starter + 6 items** (starter is separate)

| Starter | **Conduit Gem** | `31.2` | 650g |

| # | Item | Score | Cost | Stats |
|--:|------|------:|-----:|-------|
| 1 | **Jade Scepter** | `106.5` | 2750g | hp 250.0, int 100.0 |
| 2 | **Dreamer's Idol** | `103.6` | 3500g | int 130.0, pen 10.0 |
| 3 | **Death Metal** | `62.3` | 2600g | int 40.0, str 35.0, crit 20.0 |
| 4 | **Jotunn's Revenge** | `56.4` | 2400g | mp 250.0, str 35.0, cdr 25.0, pen 5.0 |
| 5 | **Helm of Darkness** | `53.4` | 2700g | int 40.0, mprot 25.0, pprot 20.0 |
| 6 | **Spear Of The Magus** | `102.3` | 2700g | int 95.0, pen 10.0 |

**Relics (scored):** Purification Beads (30.0), Aegis of Acceleration (30.0), Sundering Arc (21.7)

### Top gods in this role (model) + tailored paths

#### Kukulkan — S-tier (role rank #1, model 75.2)

*Magical · Intelligence scaling (STR 0% / INT 77.5%)*

Kukulkan as Mid: primary scaling Intelligence (STR 0% / INT 78% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Role model tier S (rank #1).

- **Starter:** Conduit Gem (`33.6`)
- **6 items:**
  1. Dreamer's Idol (`214.1` · 3500g)
  2. Wish-Granting Pearl (`192.6` · 3550g)
  3. Helm of Darkness (`87.4` · 2700g)
  4. Death Metal (`77.1` · 2600g)
  5. Jade Scepter (`191.5` · 2750g)
  6. Freya's Tears (`59.6` · 2600g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Neith — S-tier (role rank #2, model 68.6)

*Physical · Hybrid scaling (STR 67.5% / INT 66.0%)*

Neith as Mid: primary scaling Hybrid (STR 68% / INT 66% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #2).

- **Starter:** Conduit Gem (`33.6`)
- **6 items:**
  1. Dreamer's Idol (`130.6` · 3500g)
  2. Jade Scepter (`121.5` · 2750g)
  3. Death Metal (`101.1` · 2600g)
  4. Jotunn's Revenge (`80.4` · 2400g)
  5. Wish-Granting Pearl (`113.6` · 3550g)
  6. Freya's Tears (`71.6` · 2600g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Scylla — S-tier (role rank #3, model 67.3)

*Magical · Intelligence scaling (STR 0% / INT 83.8%)*

Scylla as Mid: primary scaling Intelligence (STR 0% / INT 84% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Role model tier S (rank #3).

- **Starter:** Conduit Gem (`33.6`)
- **6 items:**
  1. Dreamer's Idol (`214.1` · 3500g)
  2. Wish-Granting Pearl (`192.6` · 3550g)
  3. Helm of Darkness (`87.4` · 2700g)
  4. Death Metal (`77.1` · 2600g)
  5. Jade Scepter (`191.5` · 2750g)
  6. Freya's Tears (`59.6` · 2600g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

#### Hecate — A-tier (role rank #4, model 66.9)

*Magical · Intelligence scaling (STR 0% / INT 70.0%)*

Hecate as Mid: primary scaling Intelligence (STR 0% / INT 70% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier A (rank #4).

- **Starter:** Conduit Gem (`33.6`)
- **6 items:**
  1. Dreamer's Idol (`214.1` · 3500g)
  2. Wish-Granting Pearl (`192.6` · 3550g)
  3. Helm of Darkness (`99.4` · 2700g)
  4. Death Metal (`77.1` · 2600g)
  5. Jade Scepter (`191.5` · 2750g)
  6. Freya's Tears (`71.6` · 2600g)
- **Relics:** Purification Beads (38.0), Aegis of Acceleration (30.0)

---

## Jungle

Conquest jungle: early clear, gank threat, mobility/CDR, burst penetration, and enough HP to invade.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| str | 16% |
| pen | 16% |
| int | 12% |
| cdr | 12% |
| hp | 12% |
| as | 10% |
| ls | 8% |
| pprot | 5% |
| mprot | 5% |
| crit | 4% |

### Role template (best-in-role item scores)

**Starter:** Bumba's Cudgel (score 39.9, cost 650)
**Starter alts:** Bumba's Golden Dagger (36.4), Selflessness (16.0), Death's Toll (14.8)
**Upgrade path:** War Banner (score 29.6)

**Inventory: 1 starter + 6 items** (starter is separate)

| Starter | **Bumba's Cudgel** | `39.9` | 650g |

| # | Item | Score | Cost | Stats |
|--:|------|------:|-----:|-------|
| 1 | **Transcendence** | `54.2` | 2400g | mp 250.0, str 35.0, mpr 4.0 |
| 2 | **Gluttonous Grimoire** | `51.5` | 2600g | hp 150.0, int 55.0, pen 10.0, ls 7.5 |
| 3 | **Jotunn's Revenge** | `49.2` | 2400g | mp 250.0, str 35.0, cdr 25.0, pen 5.0 |
| 4 | **Soul Gem** | `48.9` | 2500g | int 60.0, cdr 10.0, ls 7.5, pen 5.0 |
| 5 | **Jade Scepter** | `47.0` | 2750g | hp 250.0, int 100.0 |
| 6 | **Freya's Tears** | `42.6` | 2600g | mprot 35.0, pprot 30.0, cdr 20.0 |

**Relics (scored):** Purification Beads (28.0), Sundering Arc (25.7), Agility Relic (22.5)

### Top gods in this role (model) + tailored paths

#### Mordred — S-tier (role rank #1, model 69.0)

*Physical · Hybrid scaling (STR 65.0% / INT 61.7%)*

Mordred as Jungle: primary scaling Hybrid (STR 65% / INT 62% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #1).

- **Starter:** Bumba's Cudgel (`42.6`)
- **6 items:**
  1. Avenging Blade (`84.5` · 2650g)
  2. Death Metal (`81.0` · 2600g)
  3. Arondight (`75.4` · 2650g)
  4. Soul Gem (`69.9` · 2500g)
  5. Freya's Tears (`64.6` · 2600g)
  6. Triton's Conch (`63.0` · 2700g)
- **Relics:** Purification Beads (36.0), Sundering Arc (25.7)

#### Tsukuyomi — S-tier (role rank #2, model 65.7)

*Physical · Hybrid scaling (STR 32.5% / INT 36.0%)*

Tsukuyomi as Jungle: primary scaling Hybrid (STR 32% / INT 36% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #2).

- **Starter:** Bumba's Cudgel (`42.6`)
- **6 items:**
  1. Avenging Blade (`84.5` · 2650g)
  2. Death Metal (`81.0` · 2600g)
  3. Arondight (`75.4` · 2650g)
  4. Soul Gem (`69.9` · 2500g)
  5. Freya's Tears (`64.6` · 2600g)
  6. Triton's Conch (`63.0` · 2700g)
- **Relics:** Purification Beads (36.0), Sundering Arc (25.7)

#### Thanatos — S-tier (role rank #3, model 62.4)

*Physical · Strength scaling (STR 81.7% / INT 0%)*

Thanatos as Jungle: primary scaling Strength (STR 82% / INT 0% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #3).

- **Starter:** Bumba's Cudgel (`42.6`)
- **6 items:**
  1. Avenging Blade (`111.5` · 2650g)
  2. Avatar's Parashu (`103.1` · 3700g)
  3. Jotunn's Revenge (`88.9` · 2400g)
  4. Lernaean Bow (`82.2` · 2500g)
  5. Runeforged Hammer (`69.7` · 2550g)
  6. Freya's Tears (`64.6` · 2600g)
- **Relics:** Purification Beads (36.0), Sundering Arc (25.7)

#### Ratatoskr — A-tier (role rank #4, model 60.0)

*Physical · Strength scaling (STR 60.0% / INT 0%)*

Ratatoskr as Jungle: primary scaling Strength (STR 60% / INT 0% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Role model tier A (rank #4).

- **Starter:** Bumba's Cudgel (`42.6`)
- **6 items:**
  1. Avatar's Parashu (`103.1` · 3700g)
  2. Avenging Blade (`99.5` · 2650g)
  3. Jotunn's Revenge (`88.9` · 2400g)
  4. Lernaean Bow (`82.2` · 2500g)
  5. Runeforged Hammer (`69.7` · 2550g)
  6. Freya's Tears (`52.6` · 2600g)
- **Relics:** Purification Beads (36.0), Sundering Arc (25.7)

---

## Solo

Conquest solo: lane sustain, hybrid damage, protections, HP, and items that win extended trades / rotate first.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| hp | 16% |
| pprot | 14% |
| mprot | 14% |
| str | 12% |
| int | 10% |
| cdr | 10% |
| ls | 8% |
| pen | 8% |
| hpr | 4% |
| as | 2% |
| mp | 2% |

### Role template (best-in-role item scores)

**Starter:** Warrior's Axe (score 37.8, cost 650)
**Starter alts:** Bluestone Pendant (36.8), Selflessness (26.9), Vampiric Shroud (18.6)
**Upgrade path:** Heroism (score 46.1)

**Inventory: 1 starter + 6 items** (starter is separate)

| Starter | **Warrior's Axe** | `37.8` | 650g |

| # | Item | Score | Cost | Stats |
|--:|------|------:|-----:|-------|
| 1 | **Runeforged Hammer** | `63.4` | 2550g | hp 350.0, str 45.0, hpr 3.0 |
| 2 | **Soul Gem** | `53.9` | 2500g | int 60.0, cdr 10.0, ls 7.5, pen 5.0 |
| 3 | **Shield Splitter** | `43.8` | 2400g | str 40.0, pprot 15.0, mprot 15.0 |
| 4 | **Jotunn's Revenge** | `42.6` | 2400g | mp 250.0, str 35.0, cdr 25.0, pen 5.0 |
| 5 | **Shifter's Shield** | `80.6` | 2650g | hp 300.0, pprot 25.0, mprot 25.0, hpr 4.0 |
| 6 | **Freya's Tears** | `71.9` | 2600g | mprot 35.0, pprot 30.0, cdr 20.0 |

**Relics (scored):** Purification Beads (32.0), Aegis of Acceleration (26.0), Sundering Arc (21.7)

### Top gods in this role (model) + tailored paths

#### Chaac — S-tier (role rank #1, model 69.9)

*Physical · Hybrid scaling (STR 88.3% / INT 43.8%)*

Chaac as Solo: primary scaling Hybrid (STR 88% / INT 44% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #1).

- **Starter:** Warrior's Axe (`46.1`)
- **6 items:**
  1. Shifter's Shield (`92.6` · 2650g)
  2. Soul Gem (`74.9` · 2500g)
  3. The Reaper (`67.8` · 2600g)
  4. Sanguine Lash (`67.7` · 2650g)
  5. Freya's Tears (`93.9` · 2600g)
  6. Shield of the Phoenix (`84.8` · 2400g)
- **Relics:** Purification Beads (40.0), Aegis of Acceleration (26.0)

#### Mordred — S-tier (role rank #2, model 69.0)

*Physical · Hybrid scaling (STR 65.0% / INT 61.7%)*

Mordred as Solo: primary scaling Hybrid (STR 65% / INT 62% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #2).

- **Starter:** Warrior's Axe (`46.1`)
- **6 items:**
  1. Shifter's Shield (`92.6` · 2650g)
  2. Soul Gem (`74.9` · 2500g)
  3. The Reaper (`67.8` · 2600g)
  4. Sanguine Lash (`67.7` · 2650g)
  5. Freya's Tears (`93.9` · 2600g)
  6. Shield of the Phoenix (`84.8` · 2400g)
- **Relics:** Purification Beads (40.0), Aegis of Acceleration (26.0)

#### Xing Tian — S-tier (role rank #3, model 66.6)

*Magical · Intelligence scaling (STR 0% / INT 37.5%)*

Xing Tian as Solo: primary scaling Intelligence (STR 0% / INT 38% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #3).

- **Starter:** Warrior's Axe (`46.1`)
- **6 items:**
  1. Jade Scepter (`134.7` · 2750g)
  2. Soul Gem (`126.9` · 2500g)
  3. Sphere of Negation (`96.1` · 2750g)
  4. Brawler’s Beat Stick (`57.1` · 2550g)
  5. Wish-Granting Pearl (`133.4` · 3550g)
  6. Freya's Tears (`93.9` · 2600g)
- **Relics:** Purification Beads (40.0), Aegis of Acceleration (26.0)

#### Jormungandr — A-tier (role rank #4, model 65.9)

*Magical · Hybrid scaling (STR 53.8% / INT 42.5%)*

Jormungandr as Solo: primary scaling Hybrid (STR 54% / INT 42% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier A (rank #4).

- **Starter:** Warrior's Axe (`46.1`)
- **6 items:**
  1. Soul Gem (`99.9` · 2500g)
  2. Shifter's Shield (`92.6` · 2650g)
  3. Sphere of Negation (`78.1` · 2750g)
  4. Death Metal (`65.5` · 2600g)
  5. Freya's Tears (`93.9` · 2600g)
  6. Jade Scepter (`89.7` · 2750g)
- **Relics:** Purification Beads (40.0), Aegis of Acceleration (26.0)

---

## Support

Conquest support: peel, aura/team utility, dual prots, HP, CDR, and active/defensive cores over pure personal DPS.

### Role stat priority vector

| Stat | Weight |
|------|-------:|
| hp | 18% |
| pprot | 16% |
| mprot | 16% |
| cdr | 12% |
| int | 8% |
| mp | 6% |
| hpr | 6% |
| mpr | 6% |
| str | 4% |
| pen | 4% |
| as | 2% |
| ls | 2% |

### Role template (best-in-role item scores)

**Starter:** Selflessness (score 44.7, cost 550)
**Starter alts:** War Flag (32.5), Warrior's Axe (29.5), Bumba's Cudgel (5.6)
**Upgrade path:** Heroism (score 72.8)

**Inventory: 1 starter + 6 items** (starter is separate)

| Starter | **Selflessness** | `44.7` | 550g |

| # | Item | Score | Cost | Stats |
|--:|------|------:|-----:|-------|
| 1 | **Shifter's Shield** | `78.8` | 2650g | hp 300.0, pprot 25.0, mprot 25.0, hpr 4.0 |
| 2 | **Sphere of Negation** | `53.8` | 2750g | mprot 50.0, int 40.0 |
| 3 | **Sanguine Lash** | `46.0` | 2650g | mprot 30.0, str 25.0, ls 5.0 |
| 4 | **Shield Splitter** | `44.8` | 2400g | str 40.0, pprot 15.0, mprot 15.0 |
| 5 | **Heartwood Charm** | `81.3` | 2650g | hp 400.0, mp 250.0, cdr 10.0 |
| 6 | **Freya's Tears** | `76.0` | 2600g | mprot 35.0, pprot 30.0, cdr 20.0 |

**Relics (scored):** Purification Beads (36.0), Aegis of Acceleration (30.0), Phantom Shell (24.0)

### Top gods in this role (model) + tailored paths

#### Ymir — S-tier (role rank #1, model 79.4)

*Magical · Hybrid scaling (STR 110.0% / INT 80.0%)*

Ymir as Support: primary scaling Hybrid (STR 110% / INT 80% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Role model tier S (rank #1).

- **Starter:** Selflessness (`55.3`)
- **6 items:**
  1. Jade Scepter (`90.5` · 2750g)
  2. Soul Gem (`88.0` · 2500g)
  3. Sphere of Negation (`69.8` · 2750g)
  4. Death Metal (`65.5` · 2600g)
  5. Heartwood Charm (`91.3` · 2650g)
  6. Freya's Tears (`86.0` · 2600g)
- **Relics:** Purification Beads (44.0), Aegis of Acceleration (30.0)

#### Charon — S-tier (role rank #2, model 77.0)

*Magical · Intelligence scaling (STR 0% / INT 43.8%)*

Charon as Support: primary scaling Intelligence (STR 0% / INT 44% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #2).

- **Starter:** Selflessness (`60.1`)
- **6 items:**
  1. Jade Scepter (`135.5` · 2750g)
  2. Soul Gem (`127.0` · 2500g)
  3. Sphere of Negation (`99.8` · 2750g)
  4. Brawler’s Beat Stick (`52.7` · 2550g)
  5. Wish-Granting Pearl (`133.3` · 3550g)
  6. Freya's Tears (`98.0` · 2600g)
- **Relics:** Purification Beads (44.0), Aegis of Acceleration (30.0)

#### Xing Tian — S-tier (role rank #3, model 66.6)

*Magical · Intelligence scaling (STR 0% / INT 37.5%)*

Xing Tian as Support: primary scaling Intelligence (STR 0% / INT 38% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier S (rank #3).

- **Starter:** Selflessness (`60.1`)
- **6 items:**
  1. Jade Scepter (`135.5` · 2750g)
  2. Soul Gem (`127.0` · 2500g)
  3. Sphere of Negation (`99.8` · 2750g)
  4. Brawler’s Beat Stick (`52.7` · 2550g)
  5. Wish-Granting Pearl (`133.3` · 3550g)
  6. Freya's Tears (`98.0` · 2600g)
- **Relics:** Purification Beads (44.0), Aegis of Acceleration (30.0)

#### Sobek — A-tier (role rank #4, model 66.4)

*Magical · Intelligence scaling (STR 0% / INT 50.0%)*

Sobek as Support: primary scaling Intelligence (STR 0% / INT 50% kit avg). Path ordered by combined role-stat score × god scaling bias × patch momentum. High CC kit → CDR and defensive/peel options weighted up. Self-heal in kit → lifesteal / heal-amp items favored. Role model tier A (rank #4).

- **Starter:** Selflessness (`60.1`)
- **6 items:**
  1. Jade Scepter (`135.5` · 2750g)
  2. Soul Gem (`127.0` · 2500g)
  3. Sphere of Negation (`99.8` · 2750g)
  4. Brawler’s Beat Stick (`52.7` · 2550g)
  5. Wish-Granting Pearl (`133.3` · 3550g)
  6. Freya's Tears (`98.0` · 2600g)
- **Relics:** Purification Beads (44.0), Aegis of Acceleration (30.0)

---
