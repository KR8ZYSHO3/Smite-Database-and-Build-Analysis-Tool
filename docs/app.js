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

  // Compare dropdown
  const cmp = $("#god-compare");
  if (cmp) {
    const names = [...(state.gods || [])].map((g) => g.name).sort();
    cmp.innerHTML =
      `<option value="">— none —</option>` +
      names.map((n) => `<option value="${escapeAttr(n)}">${escapeHtml(n)}</option>`).join("");
    cmp.addEventListener("change", () => {
      renderGodCompare(state.selectedGod?.name, cmp.value);
    });
  }
}

function renderGodCompare(nameA, nameB) {
  const panel = $("#god-compare-panel");
  if (!panel) return;
  if (!nameA || !nameB || nameA === nameB) {
    panel.style.display = "none";
    panel.innerHTML = "";
    return;
  }
  const a = (state.gods || []).find((g) => g.name === nameA);
  const b = (state.gods || []).find((g) => g.name === nameB);
  if (!a || !b) {
    panel.style.display = "none";
    return;
  }
  const pathFor = (g) => {
    const by = g.conquest_by_role || {};
    const roles = Object.keys(by);
    if (!roles.length) return { role: "—", items: [], starter: null, arch: null };
    const order = ["Carry", "Mid", "Jungle", "Solo", "Support"];
    roles.sort((x, y) => order.indexOf(x) - order.indexOf(y));
    const role = roles[0];
    const gb = by[role];
    return {
      role,
      items: gb.items || gb.full_path || [],
      starter: gb.starter,
      arch: gb.archetype,
      why: gb.why,
    };
  };
  const pa = pathFor(a);
  const pb = pathFor(b);
  const axesA = a.patch_axes || a.recent_axes || {};
  const axesB = b.patch_axes || b.recent_axes || {};
  const axisKeys = [...new Set([...Object.keys(axesA), ...Object.keys(axesB)])].sort();
  panel.style.display = "block";
  panel.innerHTML = `
    <div class="card compare-card">
      <h3>Compare · ${escapeHtml(a.name)} vs ${escapeHtml(b.name)}</h3>
      <div class="compare-grid">
        <div>
          <h4>${escapeHtml(a.name)}</h4>
          <div class="muted">${escapeHtml(a.primary_damage_type || "")} · tier ${escapeHtml(a.tier || "?")} · ${escapeHtml(a.trajectory || "—")}</div>
          <div class="build-meta" style="margin:8px 0">
            <span class="pill">r5 ${fmt(a.recent_5_score, 1)}</span>
            <span class="pill">kit ${fmt(a.kit_score)}</span>
            ${pa.arch ? `<span class="pill hot">${escapeHtml(String(pa.arch).replace(/_/g, " "))}</span>` : ""}
          </div>
          <div><strong>${escapeHtml(pa.role)}</strong> starter: ${escapeHtml(pa.starter?.name || "—")}</div>
          <ol class="buy-list">${pa.items.map((it, i) => buyRow(it, i + 1)).join("")}</ol>
        </div>
        <div>
          <h4>${escapeHtml(b.name)}</h4>
          <div class="muted">${escapeHtml(b.primary_damage_type || "")} · tier ${escapeHtml(b.tier || "?")} · ${escapeHtml(b.trajectory || "—")}</div>
          <div class="build-meta" style="margin:8px 0">
            <span class="pill">r5 ${fmt(b.recent_5_score, 1)}</span>
            <span class="pill">kit ${fmt(b.kit_score)}</span>
            ${pb.arch ? `<span class="pill hot">${escapeHtml(String(pb.arch).replace(/_/g, " "))}</span>` : ""}
          </div>
          <div><strong>${escapeHtml(pb.role)}</strong> starter: ${escapeHtml(pb.starter?.name || "—")}</div>
          <ol class="buy-list">${pb.items.map((it, i) => buyRow(it, i + 1)).join("")}</ol>
        </div>
      </div>
      ${
        axisKeys.length
          ? `<table class="compare-axes"><thead><tr><th>Axis</th><th>${escapeHtml(a.name)}</th><th>${escapeHtml(b.name)}</th></tr></thead>
             <tbody>${axisKeys
               .map((k) => {
                 const va = Number(axesA[k] || 0);
                 const vb = Number(axesB[k] || 0);
                 return `<tr><td>${escapeHtml(k)}</td>
                   <td class="${va > 0.15 ? "axis-up" : va < -0.15 ? "axis-down" : ""}">${va >= 0 ? "+" : ""}${fmt(va, 2)}</td>
                   <td class="${vb > 0.15 ? "axis-up" : vb < -0.15 ? "axis-down" : ""}">${vb >= 0 ? "+" : ""}${fmt(vb, 2)}</td></tr>`;
               })
               .join("")}</tbody></table>`
          : ""
      }
    </div>`;
}

function selectGod(name, switchTab) {
  const g = (state.gods || []).find((x) => x.name === name);
  if (!g) return;
  state.selectedGod = g;
  if (switchTab) {
    $$(".tab-btn").find((b) => b.dataset.tab === "gods")?.click();
  }
  const cmp = $("#god-compare");
  if (cmp && cmp.value) {
    renderGodCompare(g.name, cmp.value);
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

  // Compact banner — only the essentials (full stats live in patch/abilities details)
  $("#god-metrics").innerHTML = [
    pill(`${g.tier || "—"} #${g.rank_in_scope ?? "—"}`),
    pill(`${fmt(g.score)}`),
    pill(g.trajectory || "—"),
    pill(`${fmt(g.avg_scaling_str, 0)}/${fmt(g.avg_scaling_int, 0)} STR/INT`),
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
                .slice(0, 5)
                .map((s) => {
                  const ab = s.ability_hint
                    ? `<span class="tag">${escapeHtml(s.ability_hint)}</span> `
                    : "";
                  return `<li><span class="tag ${
                    s.direction === "buff" ? "axis-up" : s.direction === "nerf" ? "axis-down" : ""
                  }">${escapeHtml(s.direction || "")}</span> ${ab}${escapeHtml(
                    (s.sample_text || "").slice(0, 100)
                  )} <span class="muted">${escapeHtml(s.patch_name || "")}</span></li>`;
                })
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
    const byAspect = g.conquest_by_role_aspect || {};
    const aspectMeta = (g.aspects || [])[0];
    $("#god-build").innerHTML = roleKeys
      .map((role) => {
        const gb = byRole[role];
        const ga = byAspect[role];
        const cards = [renderRolePathCard(gb, role, dtype, g, false)];
        if (ga && aspectMeta) {
          cards.push(renderRolePathCard(ga, role, dtype, g, true, aspectMeta));
        }
        return cards.join("");
      })
      .join("");
  }

  // Keep banner in view; only nudge if builds are far below
  requestAnimationFrame(() => {
    const dossier = document.querySelector(".god-dossier");
    if (dossier) dossier.scrollTop = 0;
  });

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

function renderRolePathCard(gb, role, dtype, g, isAspect, aspectMeta) {
  if (!gb) return "";
  const items = gb.items || gb.full_path || [];
  const nAct = gb.active_count ?? items.filter((i) => i.is_active).length;
  const maxA = gb.max_shop_actives ?? 2;
  const penG = gb.pen_total ?? items.reduce((s, it) => s + (it.pen || 0), 0);
  let label =
    role === "Mid" && (g.role_list || []).includes("Support") && dtype === "magical"
      ? "Mid (full damage option)"
      : role;
  if (isAspect) {
    label = `${role} · ${aspectMeta?.name || gb.aspect_name || "Aspect"}`;
  }
  return `
    <div class="card build-card god-role-build ${isAspect ? "is-aspect" : ""}">
      <h3>${escapeHtml(label)}</h3>
      <div class="build-meta">
        ${isAspect ? `<span class="pill aspect">aspect</span>` : `<span class="pill">base kit</span>`}
        ${gb.archetype ? `<span class="pill hot">${escapeHtml(String(gb.archetype).replace(/_/g, " "))}</span>` : ""}
        <span class="pill">actives ${nAct}/${maxA}</span>
        <span class="pill">pen ≈ ${fmt(penG, 0)}</span>
      </div>
      ${
        isAspect && (gb.aspect_description || aspectMeta?.description)
          ? `<p class="aspect-blurb">${escapeHtml(gb.aspect_description || aspectMeta.description)}</p>`
          : ""
      }
      ${
        (gb.kit_effects || []).length
          ? `<div class="kit-effects"><span class="muted">Kit effects:</span> ${(gb.kit_effects || [])
              .slice(0, 6)
              .map((t) => `<span class="tag effect">${escapeHtml(t)}</span>`)
              .join("")}</div>`
          : ""
      }
      <p class="muted why">${escapeHtml(gb.why || "")}</p>
      <div><strong>Starter</strong> — ${escapeHtml(gb.starter?.name || "—")}${
        gb.starter?.why ? ` <span class="item-why">— ${escapeHtml(gb.starter.why)}</span>` : ""
      }</div>
      <ol class="buy-list">
        ${items.map((it, i) => buyRow(it, i + 1)).join("")}
      </ol>
      <div class="muted">Relics: ${(gb.relics || []).map((r) => r.name).join(", ") || "—"}</div>
    </div>`;
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
  const effects = gb.kit_effects || [];
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
        ${gb.is_aspect ? `<span class="pill aspect">aspect</span>` : ""}
        ${gb.archetype ? `<span class="pill hot">${escapeHtml(String(gb.archetype).replace(/_/g, " "))}</span>` : `<span class="pill">kit-fit</span>`}
        <span class="pill">actives ${ga}/${maxG}</span>
        <span class="pill">pen ≈ ${fmt(penG, 0)}</span>
        ${showMit ? `<span class="pill">mit ≈ ${fmt(mitG, 0)}</span>` : ""}
        ${gb.patch_trajectory ? `<span class="pill ice">${escapeHtml(gb.patch_trajectory)}</span>` : ""}
      </div>
      ${
        gb.is_aspect && gb.aspect_name
          ? `<div class="aspect-blurb"><strong>${escapeHtml(gb.aspect_name)}</strong>${
              gb.aspect_description ? ` — ${escapeHtml(String(gb.aspect_description).slice(0, 160))}` : ""
            }</div>`
          : ""
      }
      ${
        effects.length
          ? `<div class="kit-effects"><span class="muted">Kit effects:</span> ${effects
              .slice(0, 6)
              .map((t) => `<span class="tag effect">${escapeHtml(t)}</span>`)
              .join("")}</div>`
          : ""
      }
      ${
        (gb.kit_tags || []).length
          ? `<div class="kit-tags">${(gb.kit_tags || [])
              .slice(0, 8)
              .map((t) => `<span class="tag">${escapeHtml(t)}</span>`)
              .join("")}</div>`
          : ""
      }
      <p class="why">${escapeHtml(gb.why || "")}</p>
      <div class="starter-line"><span class="tag-start">Starter</span> ${escapeHtml(gb.starter?.name || "—")}${
        gb.starter?.why ? ` <span class="item-why">— ${escapeHtml(gb.starter.why)}</span>` : ""
      }</div>
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
      : it.troll
        ? "is-troll"
        : it.counter || it.slot === "counter"
          ? "is-counter"
          : it.slot === "mitigate"
            ? "is-mitigate"
            : it.is_active
              ? "is-active"
              : "";
  const why = it.why ? `<div class="item-why">${escapeHtml(it.why)}</div>` : "";
  return `<li class="buy-row ${slotClass}" title="${escapeAttr(it.why || it.effect || "")}">
    <span class="buy-n">${n}</span>
    <div class="buy-main">
      <span class="buy-name">${escapeHtml(it.name)}</span>
      ${why}
    </div>
    <span class="buy-tags">${tags.map((t) => `<span class="tag">${escapeHtml(t)}</span>`).join("")}</span>
    <span class="buy-cost">${it.cost != null ? it.cost + "g" : ""}</span>
  </li>`;
}

/* -------------------- Items -------------------- */
function setupItems() {
  const search = $("#item-search");
  const tier = $("#item-tier");
  const sortSel = $("#item-sort");
  const render = () => {
    const q = (search.value || "").toLowerCase().trim();
    const t = tier.value;
    const sort = (sortSel && sortSel.value) || "name";
    let list = [...(state.items || [])];
    if (t !== "All") {
      list = list.filter(
        (it) =>
          String(it.tier || "") === t ||
          (t === "Starter" && (it.categories || "").includes("Starter"))
      );
    }
    if (q) list = list.filter((it) => it.name.toLowerCase().includes(q));
    list.sort((a, b) => {
      if (sort === "hot") return (b.recent_5_score || 0) - (a.recent_5_score || 0);
      if (sort === "cold") return (a.recent_5_score || 0) - (b.recent_5_score || 0);
      if (sort === "ladder")
        return (a.ladder_rank ?? 999) - (b.ladder_rank ?? 999);
      if (sort === "cost")
        return (a.total_cost ?? a.cost ?? 0) - (b.total_cost ?? b.cost ?? 0);
      return a.name.localeCompare(b.name);
    });
    const tbody = $("#item-body");
    tbody.innerHTML = list
      .slice(0, 400)
      .map((it) => {
        const cost = it.total_cost ?? it.cost ?? "";
        const r5 = it.recent_5_score;
        const r5s = r5 == null || r5 === "" ? "—" : (r5 >= 0 ? "+" : "") + fmt(r5, 1);
        const meta = it.ladder_tier
          ? `${it.ladder_tier}${it.ladder_rank != null ? " #" + it.ladder_rank : ""}`
          : it.trajectory || "—";
        return `<tr data-name="${escapeAttr(it.name)}">
          <td>${escapeHtml(it.name)}</td>
          <td>${escapeHtml(String(it.tier || ""))}</td>
          <td class="tier-${it.ladder_tier || ""}">${escapeHtml(String(meta))}</td>
          <td>${escapeHtml(r5s)}</td>
          <td>${cost}</td>
        </tr>`;
      })
      .join("");
    tbody.querySelectorAll("tr").forEach((tr) => {
      tr.addEventListener("click", () => {
        tbody.querySelectorAll("tr").forEach((x) => x.classList.remove("selected"));
        tr.classList.add("selected");
        const it = list.find((x) => x.name === tr.dataset.name);
        showItemDetail(it);
      });
    });
  };
  search.addEventListener("input", render);
  tier.addEventListener("change", render);
  if (sortSel) sortSel.addEventListener("change", render);
  render();
}

function showItemDetail(it) {
  const box = $("#item-patch-box");
  if (!it) {
    if (box) box.textContent = "Select an item.";
    $("#item-detail").textContent = "";
    return;
  }
  const axes = it.patch_axes || {};
  const axEntries = Object.entries(axes).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
  const hints = [];
  if ((it.recent_5_score || 0) >= 0.8) hints.push("recently buffed — strong meta pick");
  if ((it.recent_5_score || 0) <= -0.8) hints.push("recently nerfed — flexible swap");
  if (Number(axes.pen || 0) > 0.2) hints.push("pen axis up");
  if (Number(axes.survivability || 0) > 0.2) hints.push("survivability axis up");
  if (Number(axes.damage || 0) > 0.2) hints.push("damage axis up");
  if (box) {
    box.innerHTML = `
      <div class="build-meta" style="margin-bottom:8px">
        <span class="pill ice">${escapeHtml(it.trajectory || "stable")}</span>
        ${it.ladder_tier ? `<span class="pill hot">ladder ${escapeHtml(it.ladder_tier)} #${it.ladder_rank ?? "—"}</span>` : ""}
        <span class="pill">r5 ${it.recent_5_score != null ? ((it.recent_5_score >= 0 ? "+" : "") + fmt(it.recent_5_score, 2)) : "—"}</span>
        <span class="pill">net ${it.net_weighted_score != null ? ((it.net_weighted_score >= 0 ? "+" : "") + fmt(it.net_weighted_score, 2)) : "—"}</span>
      </div>
      <div class="kit-tags">
        ${
          axEntries.length
            ? axEntries
                .slice(0, 8)
                .map(([k, v]) => {
                  const n = Number(v);
                  const cls = n > 0.15 ? "axis-up" : n < -0.15 ? "axis-down" : "";
                  return `<span class="tag ${cls}">${escapeHtml(k)} ${n >= 0 ? "+" : ""}${fmt(n, 1)}</span>`;
                })
                .join("")
            : `<span class="muted">No patch axes (unmentioned).</span>`
        }
      </div>
      ${
        hints.length
          ? `<p class="why" style="margin-top:8px"><strong>Intel:</strong> ${escapeHtml(hints.join("; "))}.</p>`
          : ""
      }`;
  }
  $("#item-detail").textContent = [
    it.name,
    "=".repeat(Math.min(it.name.length, 40)),
    `Shop tier: ${it.tier || "—"}  Type: ${it.item_type || "—"}`,
    `Cost: ${it.total_cost ?? it.cost ?? "—"}`,
    `Buff/Nerf events: ${it.buff_events ?? "—"} / ${it.nerf_events ?? "—"}`,
    it.ladder_rationale ? `Ladder: ${it.ladder_rationale}` : "",
    "",
    "Stats:",
    it.stats_text || "—",
    "",
    "Passive:",
    it.passive || "—",
    "",
    "Active:",
    it.active || "—",
  ]
    .filter((x) => x !== "")
    .join("\n");
}

/* -------------------- About momentum lists -------------------- */
function setupAboutMomentum() {
  const fill = (sel, rows, nameKey, scoreKey) => {
    const el = $(sel);
    if (!el) return;
    el.innerHTML = rows.length
      ? rows
          .map((r) => {
            const sc = Number(r[scoreKey] || 0);
            const cls = sc > 0 ? "axis-up" : sc < 0 ? "axis-down" : "";
            return `<li><span class="tag ${cls}">${sc >= 0 ? "+" : ""}${fmt(sc, 1)}</span> ${escapeHtml(
              r[nameKey]
            )} <span class="muted">${escapeHtml(r.trajectory || "")}</span></li>`;
          })
          .join("")
      : `<li class="muted">—</li>`;
  };
  const gods = [...(state.gods || [])].filter((g) => g.recent_5_score != null);
  const items = [...(state.items || [])].filter((i) => i.recent_5_score != null);
  const gHot = [...gods].sort((a, b) => (b.recent_5_score || 0) - (a.recent_5_score || 0)).slice(0, 6);
  const gCold = [...gods].sort((a, b) => (a.recent_5_score || 0) - (b.recent_5_score || 0)).slice(0, 6);
  const iHot = [...items].sort((a, b) => (b.recent_5_score || 0) - (a.recent_5_score || 0)).slice(0, 6);
  const iCold = [...items].sort((a, b) => (a.recent_5_score || 0) - (b.recent_5_score || 0)).slice(0, 6);
  fill("#about-gods-hot", gHot, "name", "recent_5_score");
  fill("#about-gods-cold", gCold, "name", "recent_5_score");
  fill("#about-items-hot", iHot, "name", "recent_5_score");
  fill("#about-items-cold", iCold, "name", "recent_5_score");
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

/* -------------------- Counter builds -------------------- */
const counterState = { enemies: [] };

function findGodByName(q) {
  const s = (q || "").trim().toLowerCase();
  if (!s) return null;
  const gods = state.gods || [];
  return (
    gods.find((g) => (g.name || "").toLowerCase() === s) ||
    gods.find((g) => (g.name || "").toLowerCase().includes(s)) ||
    null
  );
}

function analyzeEnemyTeamJS(enemyGods) {
  let magical = 0;
  let physical = 0;
  const healers = [];
  const ccGods = [];
  const critGods = [];
  const mageNames = [];
  const physNames = [];

  for (const g of enemyGods) {
    const dtype = (g.primary_damage_type || "").toLowerCase();
    const tags = new Set(g.kit_tags || []);
    const scale = (g.primary_scaling || "").toLowerCase();
    const isMage = dtype === "magical" || scale === "intelligence";
    const isPhys = !isMage && (dtype === "physical" || scale === "strength");
    if (isMage) {
      magical += 1;
      mageNames.push(g.name);
    } else if (isPhys) {
      physical += 1;
      physNames.push(g.name);
    } else {
      magical += 0.5;
      physical += 0.5;
    }
    if (tags.has("heal") || tags.has("heavy_heal") || tags.has("self_sustain")) {
      healers.push(g.name);
    }
    if (tags.has("hard_cc") || tags.has("high_cc")) {
      ccGods.push(g.name);
    }
    const aa = Number(g.aa_score || 0);
    if (isPhys && (tags.has("aa") || tags.has("as_steroid") || tags.has("sustained") || aa >= 0.5)) {
      critGods.push(g.name);
    }
  }

  const reasons = [];
  const need_mprot = magical >= 2 || magical > physical;
  const need_pprot = physical >= 2 || (physical >= 1 && magical <= 1);
  const need_anti_crit = critGods.length >= 1;
  const need_antiheal = healers.length >= 1;
  const need_magi = ccGods.length >= 2 || (ccGods.length >= 1 && magical >= 2);
  const need_anti_as = need_anti_crit;

  if (magical >= 3) reasons.push(`Heavy magic (${Math.floor(magical)}): Genji / Oni / mprot`);
  else if (magical >= 2) reasons.push(`Magic pressure (${Math.floor(magical)}): magical defense`);
  if (physical >= 2) reasons.push(`Physical front (${Math.floor(physical)}): Breastplate / Spectral`);
  if (critGods.length) reasons.push(`Crit/AA (${critGods.join(", ")}): Spectral`);
  if (healers.length) reasons.push(`Healing (${healers.join(", ")}): Contagion / Divine`);
  if (ccGods.length) reasons.push(`CC (${ccGods.join(", ")}): Magi's / Beads`);
  if (!reasons.length) reasons.push("Balanced lobby — light defense flex on kit path");

  return {
    magical_count: magical,
    physical_count: physical,
    healers,
    cc_gods: ccGods,
    crit_gods: critGods,
    mage_names: mageNames,
    phys_names: physNames,
    need_mprot,
    need_pprot,
    need_anti_crit,
    need_antiheal,
    need_magi,
    need_anti_as,
    reasons,
    summary: reasons.slice(0, 4).join(" · "),
  };
}

function itemStat(it, key) {
  const st = it.stats || it.stats_parsed || {};
  if (st[key] != null) return Number(st[key]) || 0;
  // stats_text fallback — wiki style "MProt: 60" / "PProt: 50"
  const t = String(it.stats_text || "");
  const map = {
    mprot: /m\s*prot[^\d\n]*(\d+)|mag(?:ical)?\s*prot[^\d\n]*(\d+)/i,
    pprot: /p\s*prot[^\d\n]*(\d+)|phys(?:ical)?\s*prot[^\d\n]*(\d+)/i,
    pen: /pen(?:etration)?[^\d\n]*(\d+)/i,
    hp: /(?:max\s*)?health[^\d\n]*(\d+)|hp[^\d\n]*(\d+)/i,
    cdr: /cooldown[^\d\n]*(\d+)|cdr[^\d\n]*(\d+)/i,
  };
  const re = map[key];
  if (!re) return 0;
  const m = t.match(re);
  return m ? Number(m[1] || m[2] || 0) : 0;
}

function isT3Item(it) {
  const tier = String(it.tier || "");
  const cost = Number(it.total_cost ?? it.cost ?? 0);
  if (tier === "3" || tier === "T3") return true;
  if (cost >= 2000 && tier !== "1" && tier !== "Starter" && tier !== "Relic") return true;
  return false;
}

function counterItemScore(it, threat, role) {
  const n = (it.name || "").toLowerCase();
  let s = 0;
  const why = [];
  const mprot = itemStat(it, "mprot");
  const pprot = itemStat(it, "pprot");
  const cats = String(it.categories || "").toLowerCase();
  const passive = `${it.passive || ""} ${it.active || ""}`.toLowerCase();

  if (threat.need_mprot) {
    if (n.includes("genji") || n.includes("oni hunter")) {
      s += 72;
      why.push("vs magic — Genji/Oni");
    } else if (mprot >= 40) {
      s += 45;
      why.push("high mprot");
    } else if (mprot >= 25) s += 22;
    if (threat.magical_count >= 3 && mprot >= 30) s += 18;
  }
  if (threat.need_pprot) {
    if (n.includes("breastplate") || n.includes("valor")) {
      s += 55;
      why.push("vs physical — Breastplate");
    } else if (pprot >= 40) {
      s += 40;
      why.push("high pprot");
    } else if (pprot >= 25) s += 18;
  }
  if (threat.need_anti_crit) {
    if (n.includes("spectral") || n.includes("nemean")) {
      s += 85;
      why.push("anti-crit vs ADC");
    }
    if (n.includes("midgardian")) {
      s += 48;
      why.push("cut enemy AS");
    }
  }
  if (threat.need_antiheal) {
    if (
      n.includes("contagion") ||
      n.includes("divine ruin") ||
      n.includes("pestilence") ||
      n.includes("brawler")
    ) {
      s += 78;
      why.push("anti-heal");
    } else if (passive.includes("heal") && (passive.includes("reduc") || passive.includes("anti"))) {
      s += 50;
      why.push("healing reduction");
    }
  }
  if (threat.need_magi) {
    if (n.includes("magi") || n.includes("mantle of discord")) {
      s += 70;
      why.push("anti-CC");
    } else if (n.includes("mantle")) {
      s += 55;
      why.push("mantle / bulk CC");
    }
  }
  if (role === "Support" || role === "Solo") {
    if ((it.item_type || "").toLowerCase() === "defensive" || cats.includes("defensive")) s += 12;
    if (n.includes("dreamer") || n.includes("parashu") || n.includes("deathbringer")) s -= 50;
  }
  // Prefer full T3
  s += Math.min(15, (Number(it.total_cost || it.cost || 0) / 300) | 0);
  // Patch heat light bias
  s += (Number(it.recent_5_score) || 0) * 4;
  return { score: s, why };
}

function injectCounterCores(baselineNames, threat, role) {
  const wanted = [];
  if (threat.need_anti_crit) wanted.push("spectral");
  if (threat.need_mprot && threat.magical_count >= 2) {
    wanted.push("genji");
    if (threat.magical_count >= 3) wanted.push("oni hunter");
  }
  if (threat.need_antiheal) wanted.push(role === "Support" || role === "Solo" ? "contagion" : "divine ruin");
  if (threat.need_magi) wanted.push("magi");
  if (threat.need_pprot && (role === "Support" || role === "Solo" || role === "Jungle")) {
    wanted.push("breastplate");
  }
  if (threat.need_anti_as && (role === "Support" || role === "Solo")) wanted.push("midgardian");

  const items = (state.items || []).filter(isT3Item);
  const byName = Object.fromEntries(items.map((it) => [it.name, it]));
  let path = baselineNames.map((n) => byName[n]).filter(Boolean);
  if (!path.length) {
    // No baseline — pure counter top items
    path = [];
  }
  const seen = new Set(path.map((p) => p.name));
  const maxInject = role === "Support" || role === "Solo" ? 3 : 2;
  let injected = 0;

  for (const key of wanted) {
    if (injected >= maxInject) break;
    if ([...seen].some((n) => n.toLowerCase().includes(key))) continue;
    const scored = items
      .filter((it) => it.name.toLowerCase().includes(key) && !seen.has(it.name))
      .map((it) => ({ it, ...counterItemScore(it, threat, role) }))
      .sort((a, b) => b.score - a.score);
    if (!scored.length) continue;
    const pick = scored[0].it;
    // Drop lowest counter-score / glass
    if (path.length >= 6) {
      let drop = -1;
      let worst = Infinity;
      path.forEach((it, i) => {
        const n = it.name.toLowerCase();
        if (["spectral", "genji", "contagion", "magi", "divine", "oni hunter"].some((k) => n.includes(k))) {
          return;
        }
        const sc = counterItemScore(it, threat, role).score;
        if (sc < worst) {
          worst = sc;
          drop = i;
        }
      });
      if (drop >= 0) {
        seen.delete(path[drop].name);
        path[drop] = pick;
        seen.add(pick.name);
        injected += 1;
      }
    } else {
      path.push(pick);
      seen.add(pick.name);
      injected += 1;
    }
  }

  // Fill to 6 with best remaining counter scores if short
  if (path.length < 6) {
    const rest = items
      .filter((it) => !seen.has(it.name))
      .map((it) => ({ it, ...counterItemScore(it, threat, role) }))
      .filter((x) => x.score > 15)
      .sort((a, b) => b.score - a.score);
    for (const r of rest) {
      if (path.length >= 6) break;
      path.push(r.it);
      seen.add(r.it.name);
    }
  }
  return path.slice(0, 6).map((it) => {
    const { score, why } = counterItemScore(it, threat, role);
    return {
      name: it.name,
      cost: it.total_cost ?? it.cost,
      why: why[0] || "kit / role fit",
      counter: score >= 40,
      score,
      is_active: String(it.categories || "").toLowerCase().includes("active"),
      pen: itemStat(it, "pen") || undefined,
      slot: score >= 40 ? "counter" : it.item_type || "",
    };
  });
}

function getBaselinePath(god, role) {
  const byRole = god.conquest_by_role || {};
  if (byRole[role]?.items?.length) {
    return byRole[role].items.map((i) => i.name);
  }
  // From builds.json top lists
  const rec = state.builds?.roles?.[role]?.recommended_gods || [];
  const hit = rec.find((g) => g.god === god.name);
  if (hit?.items?.length) return hit.items.map((i) => i.name);
  return [];
}

function getStarter(god, role) {
  const byRole = god.conquest_by_role || {};
  if (byRole[role]?.starter) return byRole[role].starter;
  const rec = state.builds?.roles?.[role]?.recommended_gods || [];
  const hit = rec.find((g) => g.god === god.name);
  return hit?.starter || null;
}

function renderEnemyPicks() {
  const box = $("#ctr-enemy-picks");
  if (!box) return;
  box.innerHTML = counterState.enemies
    .map(
      (n, i) =>
        `<button type="button" class="enemy-chip" data-rm="${i}">${escapeHtml(n)} ×</button>`
    )
    .join("");
  box.querySelectorAll("[data-rm]").forEach((btn) => {
    btn.addEventListener("click", () => {
      counterState.enemies.splice(Number(btn.getAttribute("data-rm")), 1);
      renderEnemyPicks();
    });
  });
}

/* -------------------- Troll builds (client) -------------------- */
const TROLL_AXIS_KEYS = {
  unkillable: ["shifter", "hussar", "freya", "spectral", "magi", "mantle", "alchemist", "phoenix", "pridwen", "bancroft", "asclepius", "lifebinder", "heartwood", "draconic", "oni hunter", "gladiator"],
  peel_prison: ["stygian", "binding", "isolation", "midgardian", "spectral", "magi", "mantle", "contagion", "genji", "breastplate", "chronos"],
  antiheal_tax: ["contagion", "divine ruin", "pestilence", "brawler", "toxic"],
  infinite_poke: ["chronos", "pendant", "gem of focus", "breastplate", "genji", "thoth", "doom orb", "isolation", "magus", "soul gem", "myrddin"],
  aa_clown: ["deathbringer", "demon", "riptalon", "avenging", "musashi", "qins", "ichival", "wind", "executioner", "bloodforge", "devourer"],
  aura_tax: ["thebes", "chandra", "sovereign", "heartward", "providence", "contagion", "spectral", "midgardian"],
  active_toybox: ["dreamer", "wish-granting", "parashu", "arondight", "pridwen"],
};
const TROLL_TITLES = {
  unkillable: ["Please Report Simulator", "Unkillable Clown Fiesta", "I Am A Raid Boss", "Your Ult Was A Suggestion"],
  peel_prison: ["Nobody Gets To Hit Anything", "Peel Prison Warden", "ADC Timeout Corner", "Crowd Control Tax Office"],
  antiheal_tax: ["Healing? In THIS Economy?", "Contagion Enjoyer", "Your Bancroft Is Decorative", "Anti-Fun Pharmacy"],
  infinite_poke: ["Death By A Thousand Ticks", "Cooldown Rate Menace", "Zone Tax Forever", "We Do Not Fight — We Annoy"],
  aa_clown: ["Basics Were A Mistake", "On-Hit Menace", "This God Shouldn't Auto Like This", "Crit Is A Lifestyle"],
  aura_tax: ["I Get Paid To Exist", "Aura Farmer Supreme", "Free Stats For Standing", "Thebes And Chill"],
  active_toybox: ["Button Mashing Menace", "On-Use Toybox", "Ultimate? We Have Actives At Home", "Cooldown For Chaos"],
};
const TROLL_BLURBS = {
  unkillable: "Maximize time-on-screen and soft sustain. Waste their cooldowns.",
  peel_prison: "Deny free hits. Slow, anti-crit, and bulk so their backline feels trapped.",
  antiheal_tax: "If they heal, they tilt. Stack reduction and sit on their face.",
  infinite_poke: "CDR + zone/tick pressure. Chip and leave — never a fair fight.",
  aa_clown: "Lean into basic-attack identity the ranked path ignores. Wrong, but sticky.",
  aura_tax: "Bodyblock, auras, and free team value for existing.",
  active_toybox: "Splashy On-Use chaos within the active budget.",
};

function hashStr(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function detectTrollAxesJS(god, role, useAspect) {
  const tags = new Set(god.kit_tags || []);
  const aspect = useAspect && (god.aspects || [])[0] ? god.aspects[0] : null;
  const blob = ((aspect && aspect.description) || "").toLowerCase();
  const aa = Number(god.aa_score || 0);
  const scores = {
    unkillable: 0,
    peel_prison: 0,
    antiheal_tax: 0,
    infinite_poke: 0,
    aa_clown: 0,
    aura_tax: 0,
    active_toybox: 0,
  };
  if (role === "Support" || role === "Solo") {
    scores.unkillable += 0.8;
    scores.peel_prison += 1.0;
    scores.aura_tax += 0.9;
    scores.aa_clown -= 1.2;
  }
  if (role === "Mid" || role === "Carry") {
    scores.infinite_poke += 0.9;
    scores.aa_clown += 0.4;
  }
  if (role === "Jungle") {
    scores.aa_clown += 0.5;
    scores.antiheal_tax += 0.6;
  }
  if (tags.has("heal") || tags.has("heavy_heal") || tags.has("self_sustain")) scores.unkillable += 2.0;
  if (tags.has("hard_cc") || tags.has("high_cc")) scores.peel_prison += 2.2;
  if (tags.has("dot") || tags.has("heavy_dot") || tags.has("zone") || tags.has("pet_zone") || tags.has("channel"))
    scores.infinite_poke += 2.0;
  if (tags.has("mana_stack") || tags.has("spam")) scores.infinite_poke += 1.2;
  const aaReal = aa >= 0.6 || (tags.has("aa") && tags.has("as_steroid"));
  if (aaReal) scores.aa_clown += 2.4;
  else if (tags.has("aa")) scores.aa_clown += 0.5;
  if (tags.has("team_buff")) scores.aura_tax += 1.6;
  if (tags.has("shield") || tags.has("immobile")) scores.unkillable += 1.3;
  if (tags.has("burst") || tags.has("ult_nuke") || tags.has("execute")) scores.active_toybox += 1.0;
  if (aspect) {
    if (/no scaling|base damage with no scaling/i.test(blob)) {
      scores.unkillable += 1.5;
      scores.aura_tax += 1.0;
      scores.aa_clown -= 0.8;
    }
    if (/basics? are ranged|on-hit|crit|attack speed/i.test(blob)) scores.aa_clown += 2.0;
    if (/cooldown rate|reduced cooldown/i.test(blob)) scores.infinite_poke += 1.3;
  }
  // Per-god micro bias
  for (const ax of Object.keys(scores)) {
    scores[ax] += (hashStr(god.name + ax) % 17) * 0.06;
  }
  return Object.entries(scores).sort((a, b) => b[1] - a[1]);
}

function buildTrollPathJS(god, role, useAspect, chaos) {
  let ranked = detectTrollAxesJS(god, role, useAspect);
  // God-salt among top-3 close axes (not always global #1)
  const best = ranked[0][1];
  const axisPool = ranked.filter(([, s], i) => i === 0 || s >= best - 0.9).slice(0, 3);
  const salt = hashStr(`${god.name}|${role}|asp=${useAspect}|${(god.aspects || [])[0]?.name || ""}`);
  let primary = axisPool[salt % axisPool.length][0];
  let secondary = ranked.find(([a]) => a !== primary)?.[0] || primary;
  if (chaos && secondary !== primary) {
    const t = primary;
    primary = secondary;
    secondary = t;
  }
  const titles = TROLL_TITLES[primary] || ["Certified Troll Path"];
  const title = titles[salt % titles.length];
  const aspect = useAspect && (god.aspects || [])[0] ? god.aspects[0] : null;

  // Kit baseline first (god-specific serious path)
  const baselineNames = useAspect
    ? (god.conquest_by_role_aspect?.[role]?.items || []).map((i) => i.name)
    : getBaselinePath(god, role);
  const pool = (state.items || []).filter(isT3Item);
  const byName = Object.fromEntries(pool.map((it) => [it.name, it]));
  let picked = baselineNames.map((n) => byName[n]).filter(Boolean);
  const seen = new Set(picked.map((p) => p.name));

  // Kit tag signature keys (god tags)
  const tagKeys = {
    heal: ["asclepius", "lifebinder", "bancroft", "soul gem"],
    heavy_heal: ["asclepius", "lifebinder"],
    hard_cc: ["isolation", "binding", "stygian"],
    high_cc: ["isolation", "binding"],
    dot: ["magus", "desolat", "isolation", "contagion"],
    heavy_dot: ["magus", "desolat"],
    pet_zone: ["isolation", "magus", "soul gem"],
    mana_stack: ["thoth", "doom orb", "book of"],
    spam: ["chronos", "genji", "breastplate"],
    channel: ["chronos", "gem of focus", "myrddin"],
    shield: ["phoenix", "pridwen", "shifter"],
    team_buff: ["thebes", "chandra"],
    aa: ["riptalon", "avenging", "demon"],
    as_steroid: ["riptalon", "ichival"],
  };
  const tags = god.kit_tags || [];
  let sigKeys = [];
  for (const t of tags) {
    for (const k of tagKeys[t] || []) if (!sigKeys.includes(k)) sigKeys.push(k);
  }
  if (sigKeys.length) {
    const rot = salt % sigKeys.length;
    sigKeys = sigKeys.slice(rot).concat(sigKeys.slice(0, rot));
  }

  function injectKey(key, why, maxN) {
    if (picked.length >= 6 && maxN <= 0) return false;
    if ([...seen].some((n) => n.toLowerCase().includes(key))) return false;
    const hits = pool
      .filter((it) => !seen.has(it.name) && it.name.toLowerCase().includes(key))
      .sort((a, b) => (b.total_cost || 0) - (a.total_cost || 0));
    if (!hits.length) return false;
    const it = hits[salt % Math.min(hits.length, 4)];
    it._trollWhy = why;
    if (picked.length < 6) {
      picked.push(it);
    } else {
      // replace lowest-cost non-signature-ish
      let drop = 0;
      for (let i = 0; i < picked.length; i++) {
        const n = picked[i].name.toLowerCase();
        if (!sigKeys.some((k) => n.includes(k))) {
          drop = i;
          break;
        }
      }
      seen.delete(picked[drop].name);
      picked[drop] = it;
    }
    seen.add(it.name);
    return true;
  }

  // Pin up to 2 kit signatures
  let sigN = 0;
  for (const k of sigKeys) {
    if (sigN >= 2) break;
    if (injectKey(k, `😈 kit:${k}`, 2)) sigN++;
  }

  // Rotate troll axis keys by god salt
  let keys = [...(TROLL_AXIS_KEYS[primary] || [])];
  for (const k of TROLL_AXIS_KEYS[secondary] || []) {
    if (!keys.includes(k)) keys.push(k);
  }
  if (keys.length) {
    const rot = salt % keys.length;
    keys = keys.slice(rot).concat(keys.slice(0, rot));
  }
  let trollN = 0;
  for (const key of keys) {
    if (trollN >= 3) break;
    if (injectKey(key, `😈 troll ${primary.replace(/_/g, " ")}`, 3)) trollN++;
  }

  // Fill from baseline leftovers / pool diversify
  if (picked.length < 6) {
    const rest = pool
      .filter((it) => !seen.has(it.name))
      .sort((a, b) => {
        const ha = hashStr(god.name + a.name) % 40;
        const hb = hashStr(god.name + b.name) % 40;
        return (b.total_cost || 0) + hb - ((a.total_cost || 0) + ha);
      });
    for (const it of rest) {
      if (picked.length >= 6) break;
      const n = it.name.toLowerCase();
      if (primary !== "aa_clown" && (role === "Support" || role === "Solo")) {
        if ((it.item_type || "").toLowerCase() === "offensive" && !keys.some((k) => n.includes(k)))
          continue;
      }
      it._trollWhy = `😈 troll flex · ${god.name}`;
      picked.push(it);
      seen.add(it.name);
    }
  }

  // Final god flavor swap
  if (picked.length >= 4) {
    const fi = salt % picked.length;
    const alts = pool.filter((it) => !seen.has(it.name));
    if (alts.length) {
      const alt = alts[hashStr(god.name + "flex") % Math.min(alts.length, 8)];
      seen.delete(picked[fi].name);
      alt._trollWhy = `😈 ${god.name} flavor`;
      picked[fi] = alt;
      seen.add(alt.name);
    }
  }

  const starter = useAspect
    ? god.conquest_by_role_aspect?.[role]?.starter || getStarter(god, role)
    : getStarter(god, role);
  const items = picked.slice(0, 6).map((it) => ({
    name: it.name,
    cost: it.total_cost ?? it.cost,
    why: it._trollWhy || `😈 troll ${primary.replace(/_/g, " ")}`,
    troll: true,
    slot: "counter",
    is_active: String(it.categories || "").toLowerCase().includes("active"),
  }));

  let monologue = `${title}. ${TROLL_BLURBS[primary] || "Be annoying on purpose."} Primary annoyance: ${primary.replace(
    /_/g,
    " "
  )}; backup bit: ${secondary.replace(/_/g, " ")}. Kit-first troll for ${god.name}.`;
  if (aspect) monologue += ` Running ${aspect.name} because the bit is better.`;

  return {
    title,
    primary,
    secondary,
    monologue,
    disclaimer: "TROLL / MEME — not ranked advice. Legal items, illegal vibes.",
    aspect,
    starter,
    items,
    baseline: baselineNames,
  };
}

function setupTroll() {
  $("#troll-run")?.addEventListener("click", () => {
    const god = findGodByName($("#troll-god")?.value);
    const role = $("#troll-role")?.value || "Support";
    const useAspect = !!$("#troll-aspect")?.checked;
    const chaos = !!$("#troll-chaos")?.checked;
    const box = $("#troll-result");
    if (!god) {
      box.innerHTML = `<p class="muted">Pick a valid god.</p>`;
      return;
    }
    const t = buildTrollPathJS(god, role, useAspect, chaos);
    box.innerHTML = `
      <article class="card build-card god-build-card is-troll">
        <header class="gbc-head">
          <h3>😈 ${escapeHtml(t.title)}</h3>
          <div class="muted gbc-meta">${escapeHtml(god.name)} · ${escapeHtml(role)}</div>
        </header>
        <div class="build-meta">
          <span class="pill troll-pill">TROLL</span>
          <span class="pill hot">${escapeHtml(t.primary.replace(/_/g, " "))}</span>
          <span class="pill">${escapeHtml(t.secondary.replace(/_/g, " "))}</span>
          ${t.aspect ? `<span class="pill aspect">${escapeHtml(t.aspect.name)}</span>` : ""}
        </div>
        <p class="aspect-blurb troll-blurb">${escapeHtml(t.disclaimer)}</p>
        <p class="why">${escapeHtml(t.monologue)}</p>
        <div class="starter-line"><span class="tag-start">Starter</span> ${escapeHtml(t.starter?.name || "—")}</div>
        <ol class="buy-list">
          ${t.items.map((it, i) => buyRow(it, i + 1)).join("")}
        </ol>
        ${
          t.baseline?.length
            ? `<p class="muted">Serious baseline (for contrast): ${t.baseline.map(escapeHtml).join(" → ")}</p>`
            : ""
        }
      </article>
    `;
  });
}

function setupCounter() {
  const list = $("#ctr-god-list");
  if (!list) return;
  const names = [...(state.gods || [])].map((g) => g.name).sort();
  list.innerHTML = names.map((n) => `<option value="${escapeAttr(n)}"></option>`).join("");

  const addIn = $("#ctr-enemy-add");
  addIn?.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    const g = findGodByName(addIn.value);
    if (!g) return;
    if (counterState.enemies.length >= 5) return;
    if (counterState.enemies.includes(g.name)) {
      addIn.value = "";
      return;
    }
    counterState.enemies.push(g.name);
    addIn.value = "";
    renderEnemyPicks();
  });

  $("#ctr-run")?.addEventListener("click", () => {
    const you = findGodByName($("#ctr-you")?.value);
    const role = $("#ctr-role")?.value || "Support";
    const threatEl = $("#ctr-threat");
    const resultEl = $("#ctr-result");
    if (!you) {
      threatEl.textContent = "Pick a valid god for yourself.";
      resultEl.innerHTML = "";
      return;
    }
    if (!counterState.enemies.length) {
      threatEl.textContent = "Add at least one enemy god (type name + Enter).";
      resultEl.innerHTML = "";
      return;
    }
    const enemyGods = counterState.enemies.map(findGodByName).filter(Boolean);
    const threat = analyzeEnemyTeamJS(enemyGods);
    threatEl.innerHTML = `
      <strong>Threat</strong> — ${escapeHtml(threat.summary)}
      <ul class="threat-list">${threat.reasons.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}</ul>
      <div class="muted">Magic ${fmt(threat.magical_count, 0)} · Physical ${fmt(threat.physical_count, 0)}</div>
    `;

    const baseline = getBaselinePath(you, role);
    const path = injectCounterCores(baseline, threat, role);
    const starter = getStarter(you, role);
    const baselineNote = baseline.length
      ? `<p class="muted">Baseline kit path: ${baseline.map(escapeHtml).join(" → ")}</p>`
      : `<p class="muted">No baseline path for ${escapeHtml(you.name)} ${escapeHtml(role)} — pure counter ranking.</p>`;

    resultEl.innerHTML = `
      <article class="card build-card god-build-card">
        <header class="gbc-head">
          <h3>${escapeHtml(you.name)} · ${escapeHtml(role)} · counter</h3>
          <div class="muted gbc-meta">vs ${enemyGods.map((g) => escapeHtml(g.name)).join(", ")}</div>
        </header>
        <div class="build-meta">
          <span class="pill hot">counter</span>
          ${threat.need_anti_crit ? `<span class="pill">anti-crit</span>` : ""}
          ${threat.need_mprot ? `<span class="pill">mprot</span>` : ""}
          ${threat.need_antiheal ? `<span class="pill">antiheal</span>` : ""}
          ${threat.need_magi ? `<span class="pill">anti-CC</span>` : ""}
        </div>
        ${baselineNote}
        <div class="starter-line"><span class="tag-start">Starter</span> ${escapeHtml(starter?.name || "—")}</div>
        <ol class="buy-list">
          ${path.map((it, i) => buyRow(it, i + 1)).join("")}
        </ol>
      </article>
    `;
  });
}

async function main() {
  setupTabs();
  const loading = $("#loading");
  try {
    await loadData();
    loading.style.display = "none";
    $("#app-main").style.display = "block";

    const exported = state.meta?.exported_at || state.meta?.scraped_at || "";
    const analysis = state.meta?.analysis_last_analysis_at || state.meta?.last_analysis_at || "";
    $("#meta-line").textContent = [
      exported ? `EXPORT ${String(exported).slice(0, 10)}` : "LIVE INTEL",
      analysis ? `ANALYZED ${String(analysis).slice(0, 10)}` : "",
      `${(state.gods || []).length} GODS`,
      `${(state.items || []).length} ITEMS`,
      "PATCH · KIT · BUILD",
    ]
      .filter(Boolean)
      .join("  //  ");

    setupBuilds();
    setupCounter();
    setupTroll();
    setupGods();
    setupTiers();
    setupItems();
    setupAboutMomentum();
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
