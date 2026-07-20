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
    el.innerHTML = "Pick a row.";
    return;
  }
  const bar = (label, val) => {
    const n = Math.max(0, Math.min(100, Number(val) || 0));
    return `<div class="stat-bar-row"><span>${escapeHtml(label)}</span><div class="stat-bar"><i style="width:${n}%"></i></div><span class="val">${fmt(n, 0)}</span></div>`;
  };
  el.innerHTML = `
    <div style="font-family:var(--display);font-size:1.1rem;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px">
      <span class="tier-${escapeAttr(row.tier || "")}">[${escapeHtml(row.tier || "?")}]</span>
      ${escapeHtml(row.entity_name)}
    </div>
    <div class="muted">#${row.rank_in_scope ?? "—"} · ${escapeHtml(row.entity_type || "")} · conf ${
      row.confidence != null ? (row.confidence * 100).toFixed(0) + "%" : "—"
    }</div>
    <div class="stat-bars">
      ${bar("Score", row.score)}
      ${bar("Patch", row.patch_score)}
      ${bar("Kit", row.kit_score)}
      ${bar("Build", row.build_score)}
    </div>
    <p class="muted" style="margin:12px 0 6px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;font-size:0.75rem">Rationale</p>
    <div class="detail" style="margin:0">${escapeHtml(row.rationale || "—")}</div>
    <p class="muted" style="margin-top:10px;font-size:0.85rem">Double-click a god → Gods tab.</p>
  `;
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

  const conf = g.confidence != null ? Number(g.confidence) : null;
  $("#god-metrics").innerHTML = [
    pill(`Tier ${g.tier || "—"} #${g.rank_in_scope ?? "—"}`),
    pill(`Score ${fmt(g.score)}`),
    pill(`Patch ${fmt(g.patch_score)}`),
    pill(`Kit ${fmt(g.kit_score)}`),
    pill(`Build ${fmt(g.build_score)}`),
    pill(`STR% ${fmt(g.avg_scaling_str, 0)} / INT% ${fmt(g.avg_scaling_int, 0)}`),
    pill(`Trajectory ${g.trajectory || "—"}`),
    conf != null ? pill(`Conf ${Math.round(conf * 100)}%`) : "",
  ]
    .filter(Boolean)
    .join(" ");

  // Patch exploit panel: r5 axes → how we itemize
  const axes = g.patch_axes || g.recent_axes || g.axes || {};
  const axEntries = Object.entries(axes).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
  const exploitHints = [];
  const dmgA = Number(axes.damage || 0);
  const cdA = Number(axes.cooldown || 0);
  const asA = Number(axes.attack_speed || 0);
  if (dmgA >= 0.25) exploitHints.push("damage buffed → pen + power");
  if (dmgA <= -0.35) exploitHints.push("damage nerfed → bulk / CDR / efficiency");
  if (cdA <= -0.25) exploitHints.push("CD nerfed → stack CDR");
  if (cdA >= 0.25) exploitHints.push("CD buffed → free to stack damage");
  if (asA >= 0.2) exploitHints.push("AS buffed → attack-speed cores");
  if (Number(axes.survivability || 0) >= 0.25) exploitHints.push("survivability buffed → prots / HP");
  if (Number(axes.pen || 0) >= 0.15) exploitHints.push("pen buffed → shred items");
  const axesEl = $("#god-patch-axes");
  if (axesEl) {
    if (!axEntries.length && !exploitHints.length) {
      axesEl.innerHTML = `<span class="muted">No strong r5 patch axes (stable / unmentioned).</span>
        <span class="pill ice">${escapeHtml(g.trajectory || "stable")}</span>
        <span class="muted">net ${fmt(g.net_weighted_score, 2)} · r5 ${fmt(g.recent_5_score, 2)}</span>`;
    } else {
      axesEl.innerHTML = `
        <div class="build-meta" style="margin-bottom:8px">
          <span class="pill ice">${escapeHtml(g.trajectory || "stable")}</span>
          <span class="pill">net ${fmt(g.net_weighted_score, 2)}</span>
          <span class="pill">r5 ${fmt(g.recent_5_score, 2)}</span>
        </div>
        <div class="kit-tags">
          ${axEntries
            .slice(0, 8)
            .map(([k, v]) => {
              const n = Number(v);
              const cls = n > 0.15 ? "axis-up" : n < -0.15 ? "axis-down" : "";
              return `<span class="tag ${cls}">${escapeHtml(k)} ${n >= 0 ? "+" : ""}${fmt(n, 1)}</span>`;
            })
            .join("")}
        </div>
        ${
          exploitHints.length
            ? `<p class="why" style="margin-top:8px"><strong>Exploit:</strong> ${escapeHtml(
                exploitHints.join("; ")
              )}.</p>`
            : ""
        }
        ${
          (g.patch_samples || []).length
            ? `<ul class="patch-sample-list">${(g.patch_samples || [])
                .slice(0, 4)
                .map(
                  (s) =>
                    `<li><span class="tag ${
                      s.direction === "buff" ? "axis-up" : s.direction === "nerf" ? "axis-down" : ""
                    }">${escapeHtml(s.direction || "")}</span> ${escapeHtml(
                      (s.sample_text || "").slice(0, 100)
                    )} <span class="muted">${escapeHtml(s.patch_name || "")}</span></li>`
                )
                .join("")}</ul>`
            : ""
        }`;
    }
  }

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

  // One clear Conquest path per role (no separate Cores/Defense dump).
  const byRole = g.conquest_by_role || {};
  let roleKeys = Object.keys(byRole);
  if (!roleKeys.length) {
    // Fallback: hunt role lists in builds export
    for (const [role, data] of Object.entries(state.builds?.roles || {})) {
      for (const gb of data.recommended_gods || []) {
        if (gb.god === g.name) {
          byRole[role] = gb;
        }
      }
    }
    roleKeys = Object.keys(byRole);
  }

  const dtype = (g.primary_damage_type || "").toLowerCase();
  const powerHint =
    dtype === "magical"
      ? "Magical damage → INT / magical items (ignore inflated basic-attack STR%)."
      : dtype === "physical"
        ? "Physical damage → STR / physical items."
        : `Kit scaling: ${g.primary_scaling || "—"}.`;

  $("#god-build-hint").textContent = powerHint;

  if (!roleKeys.length) {
    $("#god-build").innerHTML = `<p class="muted">${escapeHtml(g.build_notes || "No conquest path exported for this god yet.")}</p>`;
  } else {
    // Prefer Support / listed roles first, Mid full-damage last for guardians
    const order = ["Carry", "Mid", "Jungle", "Solo", "Support"];
    roleKeys.sort((a, b) => order.indexOf(a) - order.indexOf(b));
    $("#god-build").innerHTML = roleKeys
      .map((role) => {
        const gb = byRole[role];
        const items = gb.items || gb.full_path || [];
        const nAct = gb.active_count ?? items.filter((i) => i.is_active).length;
        const maxA = gb.max_shop_actives ?? 2;
        const penG = gb.pen_total ?? items.reduce((s, it) => s + (it.pen || 0), 0);
        const label =
          role === "Mid" && (g.role_list || []).includes("Support") && dtype === "magical"
            ? "Mid (full damage option)"
            : role;
        return `
        <div class="card build-card god-role-build">
          <h3>${escapeHtml(label)}</h3>
          <div class="build-meta">
            ${gb.archetype ? `<span class="pill hot">${escapeHtml(String(gb.archetype).replace(/_/g, " "))}</span>` : ""}
            <span class="pill">actives ${nAct}/${maxA}</span>
            <span class="pill">pen ≈ ${fmt(penG, 0)}</span>
          </div>
          <p class="muted why">${escapeHtml(gb.why || "")}</p>
          <div><strong>Starter</strong> — ${escapeHtml(gb.starter?.name || "—")}</div>
          <ol class="buy-list">
            ${items.map((it, i) => buyRow(it, i + 1)).join("")}
          </ol>
          <div class="muted">Relics: ${(gb.relics || []).map((r) => r.name).join(", ") || "—"}</div>
        </div>`;
      })
      .join("");
  }

  const axLines = Object.entries(axes)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .map(([k, v]) => `  ${k}: ${Number(v) >= 0 ? "+" : ""}${fmt(v, 2)}`);
  const samples = (g.patch_samples || [])
    .slice(0, 8)
    .map(
      (s) =>
        `  [${s.direction}] ${s.patch_name || "?"} — ${(s.sample_text || "").slice(0, 120)}`
    );
  $("#god-patch").textContent = [
    `Trajectory: ${g.trajectory || "—"}`,
    `Net weighted: ${fmt(g.net_weighted_score, 2)}`,
    `Last 5 patches: ${fmt(g.recent_5_score, 2)}`,
    `Buff / Nerf events: ${g.buff_events ?? "—"} / ${g.nerf_events ?? "—"}`,
    conf != null ? `Confidence: ${Math.round(conf * 100)}%` : "",
    "",
    "Patch axes (recent / full):",
    ...(axLines.length ? axLines : ["  (none)"]),
    "",
    "Recent balance lines:",
    ...(samples.length ? samples : ["  (none attributed)"]),
    "",
    "Tier rationale:",
    g.rationale || "—",
    g.build_notes ? `\nBuild notes:\n${g.build_notes}` : "",
  ]
    .filter((x) => x !== "")
    .join("\n");
}

/* -------------------- Builds (god-first) -------------------- */
const ROLE_JOB = {
  Carry: { title: "Carry — backline ADC", blurb: "AS, crit, pen, lifesteal. Support peels so you free-hit." },
  Mid: { title: "Mid — backline burst", blurb: "INT power, pen, CDR. Support peels for combos." },
  Jungle: { title: "Jungle — ganks", blurb: "Bumba clear, burst pen, CDR, Blink. Not full-tank solo." },
  Solo: { title: "Solo — unkillable frontline", blurb: "Dual prots, HP, Damp/Plat/Ten, hybrid offline damage." },
  Support: { title: "Support — peel for ADC & mid", blurb: "Mitigate, anti-AS/crit, auras. Not personal lifesteal DPS." },
};

function setupBuilds() {
  const roles = ["Carry", "Mid", "Jungle", "Solo", "Support"].filter(
    (r) => state.builds?.roles?.[r]
  );
  const pills = $("#role-pills");
  const search = $("#build-god-search");
  let activeRole = roles[0] || "Mid";

  pills.innerHTML = roles
    .map(
      (r) =>
        `<button type="button" class="role-pill ${r === activeRole ? "active" : ""}" data-role="${r}">${r}</button>`
    )
    .join("");

  const render = () => {
    const data = state.builds?.roles?.[activeRole];
    const t = data?.template || {};
    const job = ROLE_JOB[activeRole] || { title: activeRole, blurb: t.description || "" };
    const pri = t.priority_stats || Object.keys(t.stat_priorities || {}).slice(0, 5);
    const commons = t.common_items || t.top_scored_items || [];
    const st = t.typical_starter || t.starter;

    $("#role-job").innerHTML = `
      <div class="role-job-head">
        <h2>${escapeHtml(job.title)}</h2>
        <span class="pill hot">Job only — not a full build</span>
      </div>
      <p class="role-job-blurb">${escapeHtml(job.blurb || t.description || "")}</p>
      <div class="build-meta">
        ${pri.map((p) => `<span class="pill">${escapeHtml(p)}</span>`).join("")}
        ${st ? `<span class="pill ice">Typical starter: ${escapeHtml(st.name)}</span>` : ""}
      </div>
      ${
        commons.length
          ? `<p class="muted common-label">Items this role often likes (unordered — use a god card for buy order):</p>
             <div class="build-line">${commons
               .slice(0, 8)
               .map((it, i) => chip(it, String(i + 1)))
               .join("")}</div>`
          : ""
      }
      <p class="muted" style="margin:0"><strong>Next:</strong> pick a god below — each path is scored to that god’s kit.</p>
    `;

    const q = (search.value || "").toLowerCase().trim();
    let gods = [...(data?.recommended_gods || [])].sort(
      (a, b) => (a.rank ?? 99) - (b.rank ?? 99)
    );
    if (q) gods = gods.filter((g) => (g.god || "").toLowerCase().includes(q));
    $("#build-god-count").textContent = `${gods.length} kit-fit builds · ${activeRole}`;

    $("#build-gods").innerHTML = gods.length
      ? gods.map((gb) => godBuildCard(gb, activeRole)).join("")
      : `<div class="card muted">No gods for this filter.</div>`;
  };

  pills.querySelectorAll(".role-pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeRole = btn.dataset.role;
      pills.querySelectorAll(".role-pill").forEach((b) => b.classList.toggle("active", b === btn));
      search.value = "";
      render();
    });
  });
  search.addEventListener("input", render);
  $("#build-gods").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-open-god]");
    if (!btn) return;
    selectGod(btn.getAttribute("data-open-god"), true);
  });
  render();
}

function godBuildCard(gb, role) {
  const itemsG = gb.items || gb.full_path || [];
  const ga = gb.active_count ?? itemsG.filter((i) => i.is_active).length;
  const maxG = gb.max_shop_actives ?? 2;
  const penG = gb.pen_total ?? itemsG.reduce((s, it) => s + (it.pen || 0), 0);
  const mitG = itemsG.reduce((s, it) => s + (it.damp || 0) + (it.plat || 0) + (it.ten || 0), 0);
  const showMit = role === "Support" || role === "Solo";
  return `
    <article class="card build-card god-build-card">
      <header class="gbc-head">
        <h3>
          <span class="tier-${gb.tier || ""}">[${gb.tier || "?"}]</span>
          ${escapeHtml(gb.god)}
        </h3>
        <div class="muted gbc-meta">#${gb.rank ?? "—"} · ${escapeHtml(gb.damage_type || "")} · ${escapeHtml(gb.scaling || "—")} scale</div>
      </header>
      <div class="build-meta">
        ${gb.archetype ? `<span class="pill hot">${escapeHtml(String(gb.archetype).replace(/_/g, " "))}</span>` : `<span class="pill">kit-fit</span>`}
        <span class="pill">actives ${ga}/${maxG}</span>
        <span class="pill">pen ≈ ${fmt(penG, 0)}</span>
        ${showMit ? `<span class="pill">mit ≈ ${fmt(mitG, 0)}</span>` : ""}
        ${gb.patch_trajectory ? `<span class="pill ice">${escapeHtml(gb.patch_trajectory)}</span>` : ""}
      </div>
      ${
        (gb.kit_tags || []).length
          ? `<div class="kit-tags">${(gb.kit_tags || [])
              .slice(0, 8)
              .map((t) => `<span class="tag">${escapeHtml(t)}</span>`)
              .join("")}</div>`
          : ""
      }
      <p class="why">${escapeHtml(gb.why || "")}</p>
      <div class="starter-line"><span class="tag-start">Starter</span> ${escapeHtml(gb.starter?.name || "—")}</div>
      <ol class="buy-list">
        ${itemsG.map((it, i) => buyRow(it, i + 1)).join("")}
      </ol>
      <div class="muted gbc-relics">Relics: ${(gb.relics || []).map((r) => r.name).join(", ") || "—"}</div>
      <button type="button" class="linkish" data-open-god="${escapeAttr(gb.god)}">Open full god page →</button>
    </article>`;
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
  if (it.damp) tags.push(`damp ${it.damp}`);
  if (it.plat) tags.push(`plat ${it.plat}`);
  if (it.ten) tags.push(`ten ${it.ten}`);
  const slotClass =
    it.slot === "pen"
      ? "is-pen"
      : it.slot === "mitigate" || it.slot === "counter"
        ? "is-mitigate"
        : it.is_active
          ? "is-active"
          : "";
  return `<li class="buy-row ${slotClass}">
    <span class="buy-n">${n}</span>
    <span class="buy-name">${escapeHtml(it.name)}</span>
    <span class="buy-tags">${tags.map((t) => `<span class="tag">${escapeHtml(t)}</span>`).join("")}</span>
    <span class="buy-cost">${it.cost != null ? it.cost + "g" : ""}</span>
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
      exported ? `INTEL ${String(exported).slice(0, 10)}` : "LIVE INTEL",
      `${(state.gods || []).length} GODS`,
      `${(state.items || []).length} ITEMS`,
      "PATCH · KIT · BUILD",
    ]
      .filter(Boolean)
      .join("  //  ");

    setupBuilds();
    setupGods();
    setupTiers();
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
