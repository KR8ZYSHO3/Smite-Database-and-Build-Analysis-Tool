/* SMITE 2 Database — static web GUI (CDN / Netlify / any static host) */

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

function applyPayload(payload) {
  if (!payload || typeof payload !== "object") {
    throw new Error("Invalid data payload");
  }
  state.meta = payload.meta || {};
  state.tiers = payload.tiers || {};
  state.builds = payload.builds || {};
  state.gods = payload.gods || [];
  state.items = payload.items || [];
}

async function fetchJson(url) {
  const r = await fetch(url, { cache: "no-cache" });
  if (!r.ok) throw new Error(`HTTP ${r.status} for ${url}`);
  return r.json();
}

async function loadData() {
  // Embedded single-file build (standalone.html) — no network fetch needed.
  if (window.__SMITE2_DATA__) {
    applyPayload(window.__SMITE2_DATA__);
    return;
  }

  const base = new URL("./data/", window.location.href);
  // Prefer one-shot bundle (fewer requests on CDNs).
  try {
    applyPayload(await fetchJson(new URL("bundle.json", base)));
    return;
  } catch (bundleErr) {
    console.warn("bundle.json failed, falling back to split files", bundleErr);
  }

  const [meta, tiers, builds, gods, items] = await Promise.all([
    fetchJson(new URL("meta.json", base)),
    fetchJson(new URL("tiers.json", base)),
    fetchJson(new URL("builds.json", base)),
    fetchJson(new URL("gods.json", base)),
    fetchJson(new URL("items.json", base)),
  ]);
  applyPayload({ meta, tiers, builds, gods, items });
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
        const nAct = gb.active_count ?? items.filter((i) => i.is_active).length;
        const maxA = gb.max_shop_actives ?? 2;
        buildText.push(
          "",
          `--- Conquest ${role} (actives ${nAct}/${maxA}, pen ≈ ${gb.pen_total ?? "?"}) ---`,
          `Starter: ${gb.starter?.name || "—"}`,
          "Buy order:",
          ...items.map((it, i) => {
            const bits = [it.slot || "", it.is_active ? "active" : "", it.pen ? `pen ${it.pen}` : "", `${it.cost}g`]
              .filter(Boolean)
              .join(", ");
            return `  ${i + 1}. ${it.name} (${bits})`;
          })
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
    const maxA = t.max_shop_actives ?? 2;
    const penT = t.pen_total ?? items.reduce((s, it) => s + (it.pen || 0), 0);
    $("#build-desc").textContent =
      (t.description || "") +
      "  ·  Buy order: early power → pen → more power → defense → luxury. " +
      "Shop actives default 2 (hard max 3; curio shares budget).";

    $("#build-template").innerHTML = `
      <h2>Role template — ${escapeHtml(role)}</h2>
      <div class="build-meta">
        <span class="pill">1 starter + 6 items</span>
        <span class="pill">actives ${nAct}/${maxA}</span>
        <span class="pill">pen ≈ ${fmt(penT, 0)}</span>
      </div>
      ${t.build_notes ? `<p class="muted">${escapeHtml(t.build_notes)}</p>` : ""}
      <h3>Starter</h3>
      <div class="build-line">${chip(t.starter, "S")}</div>
      <h3>Buy order (full build)</h3>
      <ol class="buy-list">
        ${items.map((it, i) => buyRow(it, i + 1)).join("")}
      </ol>
      <h3>Relics <span class="muted">(separate slot — not actives)</span></h3>
      <div class="build-line">${(t.relics || []).map((it) => chip(it, "R")).join("")}</div>
      ${(t.starter_alternatives || []).length
        ? `<details class="alts"><summary>Starter alternatives</summary>
           <div class="build-line">${(t.starter_alternatives || []).map((it) => chip(it, "A")).join("")}</div>
           </details>`
        : ""}
    `;

    const gods = [...(data.recommended_gods || [])].sort(
      (a, b) => (a.rank ?? 99) - (b.rank ?? 99)
    );
    $("#build-gods").innerHTML = gods
      .map((gb) => {
        const itemsG = gb.items || gb.full_path || [];
        const ga = gb.active_count ?? itemsG.filter((i) => i.is_active).length;
        const maxG = gb.max_shop_actives ?? 2;
        const penG = gb.pen_total ?? itemsG.reduce((s, it) => s + (it.pen || 0), 0);
        return `
        <div class="card build-card">
          <h3>
            <span class="tier-${gb.tier || ""}">[${gb.tier || "?"}]</span>
            ${escapeHtml(gb.god)}
            <span class="muted">#${gb.rank ?? "—"} · ${escapeHtml(gb.damage_type || "")} · ${escapeHtml(gb.scaling || "")}</span>
          </h3>
          <div class="build-meta">
            <span class="pill">actives ${ga}/${maxG}</span>
            <span class="pill">pen ≈ ${fmt(penG, 0)}</span>
          </div>
          <p class="muted why">${escapeHtml(gb.why || "")}</p>
          <div class="muted"><strong>Starter</strong> — ${escapeHtml(gb.starter?.name || "—")}</div>
          <ol class="buy-list">
            ${itemsG.map((it, i) => buyRow(it, i + 1)).join("")}
          </ol>
          <div class="muted">Relics: ${(gb.relics || []).map((r) => r.name).join(", ") || "—"}</div>
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
  const pen = it.pen ? ` pen ${it.pen}` : "";
  return `<span class="item-chip ${active ? "active" : ""} ${it.slot === "pen" ? "pen" : ""}" title="${escapeAttr(
    it.effect || ""
  )}">
    <span class="n">${n}${active ? "A" : ""}</span>${escapeHtml(it.name)}
    <span class="muted"> ${it.cost != null ? it.cost + "g" : ""}${pen}</span>
  </span>`;
}

function buyRow(it, n) {
  if (!it) return "";
  const tags = [];
  if (it.slot) tags.push(it.slot);
  if (it.is_active) tags.push("active");
  if (it.pen) tags.push(`pen ${it.pen}`);
  return `<li class="buy-row ${it.is_active ? "is-active" : ""} ${it.slot === "pen" ? "is-pen" : ""}">
    <span class="buy-n">${n}</span>
    <span class="buy-name">${escapeHtml(it.name)}</span>
    <span class="buy-tags">${tags.map((t) => `<span class="tag">${escapeHtml(t)}</span>`).join("")}</span>
    <span class="buy-cost muted">${it.cost != null ? it.cost + "g" : ""}</span>
  </li>`;
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
    )}<br><br>
    <strong>Do not use jsDelivr for .html</strong> — it serves HTML as plain text.<br>
    Use the <code>standalone.html</code> link (raw.githack), desktop GUI, or
    <code>python -m http.server</code> in the docs folder.</div>`;
  }
}

main();
