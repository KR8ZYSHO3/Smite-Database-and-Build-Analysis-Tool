/**
 * Variety probe for troll Annoy paths.
 * Run: node scripts/_troll_variety_probe.js
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.join(__dirname, "..");
const gods = JSON.parse(fs.readFileSync(path.join(root, "docs/data/gods.json"), "utf8"));
const items = JSON.parse(fs.readFileSync(path.join(root, "docs/data/items.json"), "utf8"));
const appSrc = fs.readFileSync(path.join(root, "docs/app.js"), "utf8");

function sliceFn(src, name) {
  const needle = "function " + name + "(";
  const start = src.indexOf(needle);
  if (start < 0) return null;
  // Skip parameter list (may contain default `opts = {}`) before body brace
  let i = start + needle.length - 1; // at '('
  let depthParen = 0;
  let inStr = null;
  let esc = false;
  for (; i < src.length; i++) {
    const c = src[i];
    if (inStr) {
      if (esc) {
        esc = false;
        continue;
      }
      if (c === "\\") {
        esc = true;
        continue;
      }
      if (c === inStr) inStr = null;
      continue;
    }
    if (c === '"' || c === "'" || c === "`") {
      inStr = c;
      continue;
    }
    if (c === "(") depthParen++;
    else if (c === ")") {
      depthParen--;
      if (depthParen === 0) {
        i++;
        break;
      }
    }
  }
  while (i < src.length && /\s/.test(src[i])) i++;
  if (src[i] !== "{") return null;
  let depth = 0;
  inStr = null;
  esc = false;
  for (; i < src.length; i++) {
    const c = src[i];
    if (inStr) {
      if (esc) {
        esc = false;
        continue;
      }
      if (c === "\\") {
        esc = true;
        continue;
      }
      if (c === inStr) inStr = null;
      continue;
    }
    if (c === '"' || c === "'" || c === "`") {
      inStr = c;
      continue;
    }
    if (c === "{") depth++;
    else if (c === "}") {
      depth--;
      if (depth === 0) return src.slice(start, i + 1);
    }
  }
  return null;
}

function sliceConst(src, name) {
  const needle = "const " + name + " =";
  const start = src.indexOf(needle);
  if (start < 0) return null;
  let i = start + needle.length;
  let depthBrace = 0;
  let depthBrack = 0;
  let depthParen = 0;
  let inStr = null;
  let esc = false;
  for (; i < src.length; i++) {
    const c = src[i];
    if (inStr) {
      if (esc) {
        esc = false;
        continue;
      }
      if (c === "\\") {
        esc = true;
        continue;
      }
      if (c === inStr) inStr = null;
      continue;
    }
    if (c === '"' || c === "'" || c === "`") {
      inStr = c;
      continue;
    }
    if (c === "{") depthBrace++;
    else if (c === "}") depthBrace--;
    else if (c === "[") depthBrack++;
    else if (c === "]") depthBrack--;
    else if (c === "(") depthParen++;
    else if (c === ")") depthParen--;
    else if (c === ";" && !depthBrace && !depthBrack && !depthParen) {
      return src.slice(start, i + 1);
    }
  }
  return null;
}

// Minimal shop stubs — variety test cares about axis pick logic, not every catalog edge case
const stubs = `
function itemCategoriesBlob(it){ return String((it&&it.categories)||''); }
function isRemovedOrUnavailableItem(it){
  const n=String((it&&it.name)||'').toLowerCase();
  return !it || n.includes('providence');
}
function isGodSpecificItem(it){
  const tier=String((it&&it.tier)||'');
  const n=String((it&&it.name)||'').toLowerCase();
  return tier==='God Specific' || n.includes('acorn');
}
function itemAllowedForGod(it, godName){
  if(!isGodSpecificItem(it)) return true;
  const g=String(godName||'').toLowerCase();
  if(String((it&&it.name)||'').toLowerCase().includes('acorn')) return g.includes('ratatoskr');
  return true;
}
function isT3Item(it){
  if(isGodSpecificItem(it)) return false;
  const tier=String((it&&it.tier)||'').trim();
  const cost=Number(it.total_cost??it.cost??0);
  if(['1','2','T1','T2','Starter','Relic','Curio','Consumable'].includes(tier)) return false;
  if(tier==='3'||tier==='T3') return true;
  return !tier && cost>=2200;
}
function itemStat(it,key){
  const t=String((it&&it.stats_text)||'');
  const map={str:/(?:^|\\n)\\s*str(?:ength)?\\s*[:=]?\\s*(\\d+)/im,int:/(?:^|\\n)\\s*int(?:elligence)?\\s*[:=]?\\s*(\\d+)/im,
    hp:/(?:^|\\n)\\s*(?:hp|health)\\s*[:=]?\\s*(\\d+)/im,as:/(?:^|\\n)\\s*(?:attack\\s*speed|as)\\s*[:=]?\\s*(\\d+)/im,
    pprot:/(?:^|\\n)\\s*(?:physical\\s*protection|pprot)\\s*[:=]?\\s*(\\d+)/im,
    mprot:/(?:^|\\n)\\s*(?:magical\\s*protection|mprot)\\s*[:=]?\\s*(\\d+)/im,
    pen:/(?:^|\\n)\\s*(?:penetration|pen)\\s*[:=]?\\s*(\\d+)/im,
    crit:/(?:^|\\n)\\s*crit(?:ical)?\\s*[:=]?\\s*(\\d+)/im,
    cdr:/(?:^|\\n)\\s*(?:cooldown|cdr)\\s*[:=]?\\s*(\\d+)/im,
    ls:/(?:^|\\n)\\s*(?:lifesteal|ls)\\s*[:=]?\\s*(\\d+)/im};
  const m=t.match(map[key]||/$^/);
  return m?+m[1]:0;
}
function fmt(v,d){ const n=Number(v); return Number.isFinite(n)?n.toFixed(d??1):String(v); }
function mulberry32(a){ return function(){ let t=a+=0x6d2b79f5; t=Math.imul(t^t>>>15,t|1); t^=t+Math.imul(t^t>>>7,t|61); return ((t^t>>>14)>>>0)/4294967296; }; }
function getBaselinePath(){ return []; }
function getStarter(god, role){
  return (god&&god.conquest_by_role&&god.conquest_by_role[role]&&god.conquest_by_role[role].starter) || {name:'Starter'};
}
const TROLL_SUPPORT_POWER_BAN=['tahuti','soul reaver','dreamer','wish-granting','parashu','deathbringer','doom orb','book of thoth','heartseeker','bloodforge','arondight','soul gem','obsidian shard',"titan's bane"];
const TRUE_HEALER_NAMES=new Set(['aphrodite','guan yu','yemoja']);
function trollPoolItemOk(it,god,role,primaryAxis){
  if(!it||isRemovedOrUnavailableItem(it)) return false;
  if(!itemAllowedForGod(it,god&&god.name)) return false;
  if(isGodSpecificItem(it)){ if(!itemAllowedForGod(it,god&&god.name)) return false; }
  else if(!isT3Item(it)) return false;
  const dtype=String((god&&god.primary_damage_type)||'').toLowerCase();
  const str=itemStat(it,'str'), int=itemStat(it,'int');
  const n=String(it.name||'').toLowerCase();
  const mageNames=['bancroft','typhon','soul gem','soul reaver','gluttonous','tahuti','obsidian shard','spear of the magus','spear of desolation','book of thoth','doom orb',"chronos' pendant",'gem of focus','divine ruin','jade scepter'];
  const physNames=["titan's bane",'bloodforge','deathbringer','demon blade','riptalon','musashi','avenging blade','executioner','heartseeker','jotunn',"hydra's",'tyrfing','devourer',"qin's",'odysseus','the crusher','the reaper','pendulum blade'];
  if(dtype==='physical' && primaryAxis!=='aa_clown'){
    if(int>=40 && str<20) return false;
    if(mageNames.some(k=>n.includes(k))) return false;
  }
  if(dtype==='magical' && primaryAxis!=='aa_clown'){
    if(str>=40 && int<20) return false;
    if(physNames.some(k=>n.includes(k))) return false;
  }
  if(role==='Support' && primaryAxis!=='active_toybox' && primaryAxis!=='aa_clown' && primaryAxis!=='infinite_poke'){
    if(TROLL_SUPPORT_POWER_BAN.some(k=>n.includes(k))) return false;
  }
  return true;
}
function shopPoolForGod(godName, opts){
  const god = typeof godName==='object'?godName:{name:godName};
  const role=(opts&&opts.role)||'Support';
  const axis=(opts&&opts.primaryAxis)||null;
  return (state.items||[]).filter(it => opts&&opts.troll ? trollPoolItemOk(it,god,role,axis) : isT3Item(it));
}
`;

let bundle = stubs;
const trollStart = appSrc.indexOf("/* -------------------- Troll builds");
const trollEnd = appSrc.indexOf("function randomGodFromPool");
if (trollStart < 0 || trollEnd < 0) {
  console.error("troll section markers missing", trollStart, trollEnd);
  process.exit(1);
}
bundle += appSrc.slice(trollStart, trollEnd);

const sandbox = {
  console,
  Math,
  Set,
  Map,
  Object,
  Array,
  String,
  Number,
  JSON,
  RegExp,
  parseInt,
  parseFloat,
  isNaN,
  Infinity,
  undefined,
  Error,
  TypeError,
  Date,
  Promise,
  state: { gods, items, meta: {}, tiers: {}, builds: {} },
};
sandbox.globalThis = sandbox;

try {
  vm.runInNewContext(bundle, sandbox, { filename: "troll-bundle.js", timeout: 10000 });
} catch (e) {
  console.error("Bundle load failed:", e.message);
  process.exit(1);
}

if (typeof sandbox.buildAnnoyPathJS !== "function") {
  console.error("buildAnnoyPathJS missing");
  process.exit(1);
}
if (typeof sandbox.shopPoolForGod !== "function" || sandbox.shopPoolForGod.length < 1) {
  // length check weak; ensure body exists
  console.log("shopPoolForGod typeof", typeof sandbox.shopPoolForGod);
}

function findGod(name) {
  return gods.find((g) => g.name.toLowerCase() === name.toLowerCase());
}

function uniqueSets(rolls) {
  return new Set(
    rolls.map((r) =>
      (r.items || [])
        .map((i) => i.name)
        .sort()
        .join("|")
    )
  ).size;
}

function stapleFreq(rolls) {
  const staples = [
    "Gem of Isolation",
    "Stone of Binding",
    "Gauntlet of Thebes",
    "Shifter's Shield",
    "Chronos' Pendant",
    "Spectral Armor",
    "Doublet of Binding",
  ];
  const freq = Object.fromEntries(staples.map((s) => [s, 0]));
  for (const r of rolls) {
    const names = new Set((r.items || []).map((i) => i.name));
    for (const s of staples) if (names.has(s)) freq[s]++;
  }
  return freq;
}

const cases = [
  ["Geb", "Support"],
  ["Ah Puch", "Mid"],
  ["Susano", "Jungle"],
  ["Cupid", "Carry"],
  ["Horus", "Solo"],
];

let failed = false;
for (const [god, role] of cases) {
  const rolls = [];
  for (let i = 0; i < 5; i++) {
    const seed = 1000 + i * 97 + god.length * 13 + role.length * 3;
    const rng = sandbox.mulberry32(seed);
    rolls.push(sandbox.buildAnnoyPathJS(findGod(god), role, false, false, rng));
  }
  const uniq = uniqueSets(rolls);
  const axes = [...new Set(rolls.map((r) => r.primary))];
  const freq = stapleFreq(rolls);
  console.log(`\n=== ${god} ${role} ===`);
  console.log("unique item-sets:", uniq, "/5");
  console.log("axes rolled:", axes.join(", "));
  for (const r of rolls) {
    console.log(`  [${r.primary}]`, (r.items || []).map((i) => i.name).join(" → "));
  }
  console.log("staple hits /5:", JSON.stringify(freq));
  if (uniq < 3) {
    console.log("FAIL: need ≥3 distinct sets");
    failed = true;
  }
  if (rolls.some((r) => (r.items || []).length < 6)) {
    console.log(
      "WARN: short path",
      rolls.map((r) => (r.items || []).length)
    );
  }
}

{
  const god = findGod("Tsukuyomi") || findGod("Susano");
  const ms = sandbox.buildMaxStatPathJS(god, "Jungle", false, "max_str", sandbox.mulberry32(42));
  const names = (ms.items || []).map((i) => i.name);
  console.log("\n=== max STR", god.name, "===");
  console.log(names.join(", "), "total", ms.stat_total);
  if (names.some((n) => /archmage|chandra|binding|thebes/i.test(n))) {
    console.log("FAIL: max STR has shell");
    failed = true;
  }
}

if (failed) {
  console.error("\nVariety probe FAILED");
  process.exit(1);
}
console.log("\nVariety probe OK");
