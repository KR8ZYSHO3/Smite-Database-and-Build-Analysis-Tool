/* SMITE 2 Database — static web GUI (GitHub Pages) */

const state = {
  meta: null,
  tiers: null,
  builds: null,
  gods: null,
  items: null,
  selectedGod: null,
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];

function fmt(v, d = 1) {
  if (v === null || v === undefined || v === "") return "—";
  const n = Number(v);
  if (Number.isNaN(n)) return String(v);
  return n.toFixed(d);
}

async function loadData() {
  const base = new URL("./data/", window.location.href);
  const [meta, tiers, builds, gods, items] = await Promise.all([
    fetch(new URL("meta.json", base)).then((r) => r.json()),
    fetch(new URL("tiers.json", base)).then((r) => r.json()),
    fetch(new URL("builds.json", base)).then((r) => r.json()),
    fetch(new URL("gods.json", base)).then((r) => r.json()),
    fetch(new URL("items.json", base)).then((r) => r.json()),
  ]);
  state.meta = meta;
  state.tiers = tiers;
  state.builds = builds;
  state.gods = gods;
  state.items = items;
}

function setupTabs() {
  $$(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      $$(".tab-btn").forEach((b) => b.classList.remove("active"));
      $$(".panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      $(`#panel-${btn.dataset.tab}`).classList.add("active");
    });
  });
}

/* -------------------- Tiers -------------------- */
function setupTiers() {
  const scopeSel = $("#tier-scope");
  const filterSel = $("#tier-filter");
  const scopes = Object.keys(state.tiers || {}).sort();
  // Prefer overall first
  scopes.sort((a, b) => {
    if (a === "overall") return -1;
    if (b === "overall") return 1;
    return a.localeCompare(b);
  });
  scopeSel.innerHTML = scopes
    .map((s) => `<option value="${s}">${s}</option>`)
    .join("");
  if (scopes.includes("overall")) scopeSel.value = "overall";

  const render = () => {
    const scope = scopeSel.value;
    const filt = filterSel.value;
    let rows = state.tiers[scope] || [];
    rows = rows.filter((r) => r.entity_type === "god" || scope.startsWith("items"));
    if (filt !== "All") rows = rows.filter((r) => r.tier === filt);

    const tbody = $("#tier-body");
    tbody.innerHTML = rows
      .map(
        (r, i) => `
      <tr data-name="${escapeAttr(r.entity_name)}" data-type="${r.entity_type}">
        <td>${r.rank_in_scope ?? i + 1}</td>
        <td class="tier-${r.tier}">${r.tier}</td>
        <td>${escapeHtml(r.entity_name)}</td>
        <td>${fmt(r.score)}</td>
        <td>${fmt(r.patch_score)}</td>
        <td>${fmt(r.kit_score)}</td>
        <td>${fmt(r.build_score)}</td>
      </tr>`
      )
      .join("");

    tbody.querySelectorAll("tr").forEach((tr) => {
      tr.addEventListener("click", () => {
        tbody.querySelectorAll("tr").forEach((x) => x.classList.remove("selected"));
        tr.classList.add("selected");
        const name = tr.dataset.name;
        const type = tr.dataset.type;
        const row = rows.find((r) => r.entity_name === name && r.entity_type === type);
        showTierDetail(row);
        if (type === "god") selectGod(name, false);
      });
      tr.addEventListener("dblclick", () => {
        if (tr.dataset.type === "god") {
          selectGod(tr.dataset.name, true);
          $$(".tab-btn").find((b) => b.dataset.tab === "gods")?.click();
        }
      });
    });

    $("#tier-count").textContent = `${rows.length} entries · scope ${scope}`;
  };

  scopeSel.addEventListener("change", render);
  filterSel.addEventListener("change", render);
  render();
}

function showTierDetail(row) {
  const el = $("#tier-detail");
  if (!row) {
    el.textContent = "Select a row.";
    return;
  }
  el.textContent = [
    `${row.entity_name}`,
    `${"=".repeat(Math.min(row.entity_name.length, 40))}`,
    `Type: ${row.entity_type}  ·  Tier ${row.tier}  ·  Rank #${row.rank_in_scope}`,
    `Score ${fmt(row.score)}  Patch ${fmt(row.patch_score)}  Kit ${fmt(row.kit_score)}  Build ${fmt(row.build_score)}`,
    `Confidence: ${row.confidence != null ? (row.confidence * 100).toFixed(0) + "%" : "—"}`,
    "",
    "Rationale",
    "---------",
    row.rationale || "—",
    "",
    "Double-click a god to open the Gods tab.",
  ].join("\n");
}

/* -------------------- Gods -------------------- */
function setupGods() {
  const search = $("#god-search");
  const renderList = () => {
    const q = (search.value || "").toLowerCase().trim();
    let list = state.gods || [];
    if (q) {
      list = list.filter(
        (g) =>
          g.name.toLowerCase().includes(q) ||
          (g.pantheon || "").toLowerCase().includes(q) ||
          (g.primary_damage_type || "").toLowerCase().includes(q)
      );
    }
    const tbody = $("#god-list-body");
    tbody.innerHTML = list
      .map(
        (g) => `
      <tr data-name="${escapeAttr(g.name)}">
        <td>${escapeHtml(g.name)}</td>
        <td>${escapeHtml(g.pantheon || "")}</td>
        <td>${escapeHtml(g.primary_damage_type || "")}</td>
        <td class="tier-${g.tier || ""}">${g.tier || "—"}</td>
        <td>${g.rank_in_scope ?? "—"}</td>
      </tr>`
      )
      .join("");
    tbody.querySelectorAll("tr").forEach((tr) => {
      tr.addEventListener("click", () => {
        tbody.querySelectorAll("tr").forEach((x) => x.classList.remove("selected"));
        tr.classList.add("selected");
        selectGod(tr.dataset.name, false);
      });
    });
  };
  search.addEventListener("input", renderList);
  renderList();
}

function selectGod(name, switchTab) {
  const g = (state.gods || []).find((x) => x.name === name);
  if (!g) return;
  state.selectedGod = g;
  if (switchTab) {
    $$(".tab-btn").find((b) => b.dataset.tab === "gods")?.click();
  }

  $("#god-title").textContent = g.name;
  $("#god-sub").textContent = [
    g.title || "",
    g.pantheon || "",
    g.primary_damage_type || "",
    g.primary_scaling ? `scaling ${g.primary_scaling}` : "",
  ]
    .filter(Boolean)
    .join(" · ");

  $("#god-metrics").innerHTML = [
    pill(`Tier ${g.tier || "—"} #${g.rank_in_scope ?? "—"}`),
    pill(`Score ${fmt(g.score)}`),
    pill(`Patch ${fmt(g.patch_score)}`),
    pill(`Kit ${fmt(g.kit_score)}`),
    pill(`Build ${fmt(g.build_score)}`),
    pill(`STR% ${fmt(g.avg_scaling_str, 0)} / INT% ${fmt(g.avg_scaling_int, 0)}`),
    pill(`Trajectory ${g.trajectory || "—"}`),
  ].join(" ");

  const ab = $("#god-abilities");
  ab.innerHTML = (g.abilities || [])
    .map(
      (a) => `
    <tr>
      <td>${escapeHtml(a.slot || "")}</td>
      <td>${escapeHtml(a.name || "")}</td>
      <td>${fmt(a.damage_rank5)}</td>
      <td>${fmt(a.scaling_str_pct)}</td>
      <td>${fmt(a.scaling_int_pct)}</td>
      <td>${fmt(a.cooldown_rank5)}</td>
      <td>${fmt(a.power_score)}</td>
    </tr>`
    )
    .join("");

  const cores = g.core_items || safeJson(g.core_items_json) || [];
  const defs = g.defense_items || safeJson(g.defense_items_json) || [];
  const relics = g.relic_suggestions || safeJson(g.relic_suggestions) || [];

  let buildText = [
    `Scaling: ${g.primary_scaling || "—"} (${g.primary_damage_type || ""})`,
    `Starter: ${g.recommended_starter || "—"}`,
    "",
    "Cores:",
    ...cores.map((x) => `  · ${x}`),
    "",
    "Defense:",
    ...defs.map((x) => `  · ${x}`),
    "",
    "Relics:",
    ...relics.map((x) => `  · ${x}`),
    "",
    g.build_notes || "",
  ];

  // Conquest tailored if present
  const roles = state.builds?.roles || {};
  for (const [role, data] of Object.entries(roles)) {
    for (const gb of data.recommended_gods || []) {
      if (gb.god === g.name) {
        const items = gb.items || gb.full_path || [];
        const nAct = items.filter((i) => i.is_active).length;
        buildText.push(
          "",
          `--- Conquest ${role} (1 starter + 6 · actives ${nAct}/3) ---`,
          `Starter: ${gb.starter?.name || "—"}`,
          ...items.map(
            (it, i) =>
              `  ${i + 1}. ${it.is_active ? "*" : " "} ${it.name} (${it.cost}g)`
          )
        );
      }
    }
  }
  $("#god-build").textContent = buildText.join("\n");

  $("#god-patch").textContent = [
    `Trajectory: ${g.trajectory || "—"}`,
    `Net weighted: ${fmt(g.net_weighted_score, 2)}`,
    `Last 5 patches: ${fmt(g.recent_5_score, 2)}`,
    `Buff / Nerf events: ${g.buff_events ?? "—"} / ${g.nerf_events ?? "—"}`,
    "",
    "Tier rationale:",
    g.rationale || "—",
  ].join("\n");
}

/* -------------------- Builds -------------------- */
function setupBuilds() {
  const roleSel = $("#build-role");
  const roles = Object.keys(state.builds?.roles || {});
  roleSel.innerHTML = roles.map((r) => `<option value="${r}">${r}</option>`).join("");

  const render = () => {
    const role = roleSel.value;
    const data = state.builds?.roles?.[role];
    if (!data) {
      $("#build-template").textContent = "No build data.";
      $("#build-gods").textContent = "";
      return;
    }
    const t = data.template;
    const items = t.items || t.full_path || [];
    const nAct = items.filter((i) => i.is_active).length;
    $("#build-desc").textContent = t.description || "";

    $("#build-template").innerHTML = `
      <div class="muted">1 starter + 6 items · actives ${nAct}/3 · * = Active item</div>
      <h3>Starter</h3>
      <div class="build-line">
        ${chip(t.starter, "S")}
      </div>
      <h3>Six items</h3>
      <div class="build-line">
        ${items.map((it, i) => chip(it, String(i + 1))).join("")}
      </div>
      <h3>Relics (separate slot)</h3>
      <div class="build-line">
        ${(t.relics || []).map((it) => chip(it, "R")).join("")}
      </div>
      <h3>Starter alts</h3>
      <div class="build-line">
        ${(t.starter_alternatives || []).map((it) => chip(it, "A")).join("")}
      </div>
    `;

    $("#build-gods").innerHTML = (data.recommended_gods || [])
      .map((gb) => {
        const itemsG = gb.items || gb.full_path || [];
        const ga = itemsG.filter((i) => i.is_active).length;
        return `
        <div class="card" style="margin-bottom:10px">
          <h3>
            <span class="tier-${gb.tier || ""}">[${gb.tier || "?"}]</span>
            ${escapeHtml(gb.god)}
            <span class="muted"> · ${escapeHtml(gb.damage_type || "")} · ${escapeHtml(gb.scaling || "")}
            · actives ${ga}/3</span>
          </h3>
          <div class="muted" style="margin-bottom:6px">${escapeHtml(gb.why || "")}</div>
          <div><strong>Starter:</strong> ${escapeHtml(gb.starter?.name || "—")}</div>
          <div class="build-line">
            ${itemsG.map((it, i) => chip(it, String(i + 1))).join("")}
          </div>
          <div class="muted">Relics: ${(gb.relics || []).map((r) => r.name).join(", ")}</div>
        </div>`;
      })
      .join("");
  };

  roleSel.addEventListener("change", render);
  render();
}

function chip(it, n) {
  if (!it) return "";
  const active = it.is_active;
  return `<span class="item-chip ${active ? "active" : ""}" title="${escapeAttr(
    it.effect || ""
  )}">
    <span class="n">${n}${active ? "*" : ""}</span>${escapeHtml(it.name)}
    <span class="muted"> ${it.cost != null ? it.cost + "g" : ""}</span>
  </span>`;
}

/* -------------------- Items -------------------- */
function setupItems() {
  const search = $("#item-search");
  const tier = $("#item-tier");
  const render = () => {
    const q = (search.value || "").toLowerCase().trim();
    const t = tier.value;
    let list = state.items || [];
    if (t !== "All") {
      list = list.filter((it) => String(it.tier || "") === t || (t === "Starter" && (it.categories || "").includes("Starter")));
    }
    if (q) list = list.filter((it) => it.name.toLowerCase().includes(q));
    const tbody = $("#item-body");
    tbody.innerHTML = list
      .slice(0, 400)
      .map((it) => {
        const cost = it.total_cost ?? it.cost ?? "";
        const stats = (it.stats_text || "").replace(/\n/g, " · ").slice(0, 70);
        return `<tr data-name="${escapeAttr(it.name)}">
          <td>${escapeHtml(it.name)}</td>
          <td>${escapeHtml(String(it.tier || ""))}</td>
          <td>${escapeHtml(it.item_type || "")}</td>
          <td>${cost}</td>
          <td class="muted">${escapeHtml(stats)}</td>
        </tr>`;
      })
      .join("");
    tbody.querySelectorAll("tr").forEach((tr) => {
      tr.addEventListener("click", () => {
        const it = list.find((x) => x.name === tr.dataset.name);
        $("#item-detail").textContent = it
          ? [
              it.name,
              "=".repeat(it.name.length),
              `Tier: ${it.tier}  Type: ${it.item_type}`,
              `Cost: ${it.total_cost ?? it.cost ?? "—"}`,
              "",
              "Stats:",
              it.stats_text || "—",
              "",
              "Passive:",
              it.passive || "—",
              "",
              "Active:",
              it.active || "—",
            ].join("\n")
          : "";
      });
    });
  };
  search.addEventListener("input", render);
  tier.addEventListener("change", render);
  render();
}

/* -------------------- utils -------------------- */
function pill(text) {
  return `<span class="pill">${escapeHtml(text)}</span>`;
}
function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
function escapeAttr(s) {
  return escapeHtml(s).replace(/'/g, "&#39;");
}
function safeJson(s) {
  if (!s) return null;
  if (typeof s !== "string") return s;
  try {
    return JSON.parse(s);
  } catch {
    return null;
  }
}

async function main() {
  setupTabs();
  const loading = $("#loading");
  try {
    await loadData();
    loading.style.display = "none";
    $("#app-main").style.display = "block";

    const exported = state.meta?.exported_at || state.meta?.scraped_at || "";
    $("#meta-line").textContent = [
      "SMITE 2 only",
      exported ? `data ${String(exported).slice(0, 19)}` : "",
      `${(state.gods || []).length} gods`,
      `${Object.keys(state.tiers || {}).length} tier scopes`,
      "max 3 actives / 6 items",
    ]
      .filter(Boolean)
      .join(" · ");

    setupTiers();
    setupGods();
    setupBuilds();
    setupItems();
  } catch (err) {
    loading.innerHTML = `<div class="err"><strong>Failed to load data.</strong><br>${escapeHtml(
      err.message || err
    )}<br><br>If opening the HTML file directly, use a local server or GitHub Pages
    (browsers block fetch() from file://).</div>`;
  }
}

main();
