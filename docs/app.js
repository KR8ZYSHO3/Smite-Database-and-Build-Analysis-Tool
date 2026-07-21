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

/* -------------------- Visual / share helpers (Package D) -------------------- */
const ROLE_THEME = {
  Carry: "role-carry",
  Mid: "role-mid",
  Jungle: "role-jungle",
  Solo: "role-solo",
  Support: "role-support",
};

const shareStore = new Map();
let shareSeq = 0;
let activeShare = null;

function roleClass(role) {
  return ROLE_THEME[role] || "role-mid";
}

function setActiveRoleTheme(role) {
  document.body.classList.remove("role-carry", "role-mid", "role-jungle", "role-solo", "role-support");
  if (role && ROLE_THEME[role]) document.body.classList.add(ROLE_THEME[role]);
}

function slotKind(it) {
  if (!it) return "core";
  if (it.troll) return "troll";
  if (it.counter || it.slot === "counter") return "counter";
  if (it.is_active) return "active";
  if (it.slot === "pen") return "pen";
  if (it.slot === "mitigate") return "mitigate";
  if (it.slot === "luxury" || /luxury/i.test(String(it.slot || ""))) return "luxury";
  return it.slot || "core";
}

function itemInitials(name) {
  const parts = String(name || "?")
    .replace(/[''"]/g, "")
    .split(/[\s\-–—/]+/)
    .filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return String(name || "?").slice(0, 2).toUpperCase();
}

function loadoutRail(items) {
  const list = items || [];
  if (!list.length) return "";
  const parts = [];
  list.forEach((it, i) => {
    const kind = slotKind(it);
    parts.push(`<div class="loadout-slot is-${escapeAttr(kind)}${
      it.is_diff ? " is-diff" : ""
    }" title="${escapeAttr(it.name || "")}${it.is_diff ? " · lobby swap" : ""}">
      <span class="ls-n">${i + 1}</span>
      <span class="ls-icon">${escapeHtml(itemInitials(it.name))}</span>
      <span class="ls-name">${escapeHtml(it.name || "—")}</span>
    </div>`);
    if (i < list.length - 1) parts.push(`<span class="loadout-conn" aria-hidden="true"></span>`);
  });
  return `<div class="loadout-rail" role="list" aria-label="Buy order">${parts.join("")}</div>`;
}

function registerShare(data) {
  const id = `s${++shareSeq}`;
  shareStore.set(id, data);
  return id;
}

function shareBar(data) {
  if (!data.deeplink) data.deeplink = deeplinkForShare(data);
  const id = registerShare(data);
  return `<div class="card-actions">
    <button type="button" class="btn-share" data-share-id="${id}">Share</button>
  </div>`;
}

function trustLine(extra) {
  return `<p class="trust-line">Not live win rates${extra ? ` · ${escapeHtml(extra)}` : ""}</p>`;
}

function emptyHud(title, body) {
  return `<div class="empty-hud card">
    <div class="empty-hud-title">${escapeHtml(title)}</div>
    <p class="muted">${escapeHtml(body)}</p>
  </div>`;
}

function showToast(msg) {
  const el = $("#toast");
  if (!el) return;
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => el.classList.remove("show"), 2200);
}

function closeIntelModal() {
  const modal = $("#intel-modal");
  if (!modal) return;
  modal.classList.remove("open");
  modal.hidden = true;
  activeShare = null;
}

function intelPreviewHtml(data) {
  const mode = data.mode || "base";
  const items = data.items || [];
  const tags = (data.tags || []).map((t) => `<span class="pill">${escapeHtml(t)}</span>`).join("");
  const path = items
    .map(
      (it, i) =>
        `<li><span class="n">${i + 1}</span><span>${escapeHtml(it.name || "—")}</span><span class="cost">${
          it.cost != null ? it.cost + "g" : ""
        }</span></li>`
    )
    .join("");
  const starter = data.starter
    ? `<li><span class="n">S</span><span>${escapeHtml(data.starter)}</span><span class="cost">start</span></li>`
    : "";
  return `
    <div class="ic-brand">SMITE 2 · Arena Intel</div>
    ${mode === "troll" ? `<div class="ic-stamp">Not ranked</div>` : ""}
    <h2 class="ic-title">${escapeHtml(data.title || data.god || "Intel")}</h2>
    <p class="ic-sub">${escapeHtml(data.subtitle || "")}</p>
    ${tags ? `<div class="ic-tags">${tags}</div>` : ""}
    ${data.why ? `<p class="ic-why">${escapeHtml(data.why)}</p>` : ""}
    <ul class="ic-path">${starter}${path}</ul>
    <div class="ic-footer">
      <span>${escapeHtml(data.footerLeft || "kit · patch · build")}</span>
      <span>${escapeHtml(data.footerRight || "smitebuilddatabase.netlify.app")}</span>
    </div>`;
}

function openIntelModal(data) {
  activeShare = data;
  const modal = $("#intel-modal");
  const preview = $("#intel-card-preview");
  if (!modal || !preview) return;
  preview.className = `intel-card-preview mode-${escapeAttr(data.mode || "base")}`;
  preview.innerHTML = intelPreviewHtml(data);
  modal.hidden = false;
  modal.classList.add("open");
}

function intelPathText(data) {
  const lines = [
    `SMITE 2 Arena Intel — ${data.title || data.god || ""}`,
    data.subtitle || "",
    data.why ? `Why: ${data.why}` : "",
    data.starter ? `Starter: ${data.starter}` : "",
    ...(data.items || []).map((it, i) => `${i + 1}. ${it.name}${it.cost != null ? ` (${it.cost}g)` : ""}`),
    data.mode === "troll" ? "TROLL / MEME — not ranked advice." : "",
    "smitebuilddatabase.netlify.app",
  ].filter(Boolean);
  return lines.join("\n");
}

function downloadIntelPng(data) {
  const W = 900;
  const H = 520;
  const canvas = document.createElement("canvas");
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext("2d");
  const mode = data.mode || "base";

  // bg
  const bg = ctx.createLinearGradient(0, 0, W, H);
  bg.addColorStop(0, "#0a0c14");
  bg.addColorStop(0.5, "#10141f");
  bg.addColorStop(1, "#080a12");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  // radial accents
  const r1 = ctx.createRadialGradient(80, 40, 10, 80, 40, 320);
  r1.addColorStop(0, mode === "troll" ? "rgba(244,114,182,0.22)" : "rgba(247,37,133,0.18)");
  r1.addColorStop(1, "transparent");
  ctx.fillStyle = r1;
  ctx.fillRect(0, 0, W, H);
  const r2 = ctx.createRadialGradient(W - 60, 60, 10, W - 60, 60, 280);
  r2.addColorStop(0, "rgba(76,201,240,0.16)");
  r2.addColorStop(1, "transparent");
  ctx.fillStyle = r2;
  ctx.fillRect(0, 0, W, H);

  // top stripe
  const stripe = ctx.createLinearGradient(0, 0, W, 0);
  if (mode === "troll") {
    stripe.addColorStop(0, "#f472b6");
    stripe.addColorStop(0.5, "#a855f7");
    stripe.addColorStop(1, "#22d3ee");
  } else if (mode === "counter") {
    stripe.addColorStop(0, "#ff4d6d");
    stripe.addColorStop(0.5, "#f72585");
    stripe.addColorStop(1, "#4cc9f0");
  } else if (mode === "aspect") {
    stripe.addColorStop(0, "#fbbf24");
    stripe.addColorStop(1, "#ffd60a");
  } else {
    stripe.addColorStop(0, "#f72585");
    stripe.addColorStop(0.5, "#ffd60a");
    stripe.addColorStop(1, "#4cc9f0");
  }
  ctx.fillStyle = stripe;
  ctx.fillRect(0, 0, W, 4);

  // border
  ctx.strokeStyle = "rgba(76,201,240,0.35)";
  ctx.lineWidth = 2;
  ctx.strokeRect(12, 12, W - 24, H - 24);

  ctx.fillStyle = "#6b7a99";
  ctx.font = "600 14px Consolas, monospace";
  ctx.fillText("SMITE 2  ·  ARENA INTEL", 36, 48);

  ctx.fillStyle = "#eef2ff";
  ctx.font = "800 36px Orbitron, Rajdhani, sans-serif";
  const title = String(data.title || data.god || "Intel").slice(0, 42);
  ctx.fillText(title, 36, 96);

  ctx.fillStyle = "#8b97b3";
  ctx.font = "600 18px Rajdhani, sans-serif";
  const sub = String(data.subtitle || "").slice(0, 80);
  ctx.fillText(sub, 36, 126);

  if (data.why) {
    ctx.fillStyle = "rgba(76,201,240,0.08)";
    ctx.fillRect(36, 144, W - 72, 48);
    ctx.fillStyle = "#c5d0e8";
    ctx.font = "500 16px Rajdhani, sans-serif";
    wrapCanvasText(ctx, String(data.why).slice(0, 160), 48, 166, W - 96, 18);
  }

  let y = 220;
  if (data.starter) {
    drawItemLine(ctx, "S", data.starter, "", y);
    y += 36;
  }
  (data.items || []).slice(0, 6).forEach((it, i) => {
    drawItemLine(ctx, String(i + 1), it.name || "—", it.cost != null ? `${it.cost}g` : "", y);
    y += 36;
  });

  if (mode === "troll") {
    ctx.save();
    ctx.translate(W - 120, 90);
    ctx.rotate(0.2);
    ctx.strokeStyle = "rgba(244,114,182,0.7)";
    ctx.lineWidth = 2;
    ctx.strokeRect(-70, -16, 140, 32);
    ctx.fillStyle = "rgba(249,168,212,0.9)";
    ctx.font = "700 14px Orbitron, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("NOT RANKED", 0, 6);
    ctx.restore();
  }

  ctx.fillStyle = "#5a6a88";
  ctx.font = "500 12px Consolas, monospace";
  ctx.textAlign = "left";
  ctx.fillText(String(data.footerLeft || "KIT · PATCH · BUILD"), 36, H - 36);
  ctx.textAlign = "right";
  ctx.fillText(String(data.footerRight || "smitebuilddatabase.netlify.app"), W - 36, H - 36);

  canvas.toBlob((blob) => {
    if (!blob) {
      showToast("PNG export failed");
      return;
    }
    const a = document.createElement("a");
    const safe = String(data.god || data.title || "intel")
      .replace(/[^\w\-]+/g, "_")
      .slice(0, 40);
    a.href = URL.createObjectURL(blob);
    a.download = `arena-intel-${safe}.png`;
    a.click();
    URL.revokeObjectURL(a.href);
    showToast("PNG downloaded");
  }, "image/png");
}

function drawItemLine(ctx, n, name, cost, y) {
  ctx.fillStyle = "rgba(0,0,0,0.35)";
  ctx.strokeStyle = "rgba(42,53,80,0.85)";
  ctx.lineWidth = 1;
  roundRect(ctx, 36, y - 22, 828, 32, 8);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#4cc9f0";
  ctx.font = "800 14px Orbitron, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(n, 56, y);
  ctx.fillStyle = "#eef2ff";
  ctx.font = "700 17px Rajdhani, sans-serif";
  ctx.textAlign = "left";
  ctx.fillText(String(name).slice(0, 48), 78, y);
  if (cost) {
    ctx.fillStyle = "#8b97b3";
    ctx.font = "500 13px Consolas, monospace";
    ctx.textAlign = "right";
    ctx.fillText(cost, 848, y);
  }
  ctx.textAlign = "left";
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function wrapCanvasText(ctx, text, x, y, maxW, lineH) {
  const words = text.split(/\s+/);
  let line = "";
  let yy = y;
  let lines = 0;
  for (const w of words) {
    const test = line ? `${line} ${w}` : w;
    if (ctx.measureText(test).width > maxW && line) {
      ctx.fillText(line, x, yy);
      line = w;
      yy += lineH;
      lines++;
      if (lines >= 2) {
        ctx.fillText(line.slice(0, 60) + "…", x, yy);
        return;
      }
    } else line = test;
  }
  if (line) ctx.fillText(line, x, yy);
}

function deeplinkForShare(data) {
  const mode = data.mode || "base";
  if (mode === "counter" && data.god) {
    const vs = (data.enemies || []).map(encodeURIComponent).join(",");
    return `#counter/${encodeURIComponent(data.god)}/${encodeURIComponent(data.role || "Support")}${
      vs ? `/${vs}` : ""
    }`;
  }
  if (mode === "troll" && data.god) {
    let h = `#troll/${encodeURIComponent(data.god)}/${encodeURIComponent(data.role || "Support")}`;
    const flags = [];
    if (data.aspect !== false && data.aspect !== 0) flags.push("aspect");
    if (data.chaos) flags.push("chaos");
    if (flags.length) h += `/${flags.join(",")}`;
    return h;
  }
  if (data.god) return `#gods/${encodeURIComponent(data.god)}`;
  if (data.role) return `#builds/${encodeURIComponent(data.role)}`;
  return "#builds";
}

function absoluteShareUrl(data) {
  const hash = data.deeplink || deeplinkForShare(data);
  return `${location.origin}${location.pathname}${location.search}${hash}`;
}

async function copyText(text, okMsg) {
  try {
    await navigator.clipboard.writeText(text);
    showToast(okMsg || "Copied");
  } catch {
    showToast("Copy failed");
  }
}

function setupShareUi() {
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-share-id]");
    if (btn) {
      const data = shareStore.get(btn.getAttribute("data-share-id"));
      if (data) openIntelModal(data);
      return;
    }
  });
  $("#intel-close")?.addEventListener("click", closeIntelModal);
  $("#intel-modal")?.addEventListener("click", (e) => {
    if (e.target === $("#intel-modal")) closeIntelModal();
  });
  $("#intel-copy-text")?.addEventListener("click", () => {
    if (!activeShare) return;
    copyText(intelPathText(activeShare), "Path copied");
  });
  $("#intel-copy-link")?.addEventListener("click", () => {
    if (!activeShare) return;
    copyText(absoluteShareUrl(activeShare), "Link copied");
  });
  $("#intel-dl-png")?.addEventListener("click", () => {
    if (!activeShare) return;
    downloadIntelPng(activeShare);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if ($("#intel-modal")?.classList.contains("open")) {
        closeIntelModal();
        return;
      }
      const sheet = $("#mobile-more-sheet");
      if (sheet && !sheet.hidden) {
        sheet.hidden = true;
      }
    }
  });
}

function itemsForShare(items) {
  return (items || []).map((it) => ({
    name: it.name,
    cost: it.cost ?? it.total_cost ?? null,
    slot: it.slot || null,
  }));
}

/* -------------------- Routing / deep links -------------------- */
const VALID_TABS = new Set(["builds", "counter", "troll", "gods", "tiers", "items", "about"]);
const routeState = {
  suppressHash: false,
  build: null, // { getRole, setRole }
};

const ADVANCED_TABS = new Set(["counter", "troll", "tiers", "items", "about"]);

function activateTab(tab, { updateHash = true } = {}) {
  if (!VALID_TABS.has(tab)) tab = "builds";
  $$(".tab-btn").forEach((b) => {
    if (b.classList.contains("more-trigger")) {
      b.classList.toggle("active", ADVANCED_TABS.has(tab));
      return;
    }
    b.classList.toggle("active", b.dataset.tab === tab);
  });
  $$(".mobile-tab").forEach((b) => {
    if (b.dataset.tab === "more") {
      b.classList.toggle("active", ["troll", "tiers", "items", "about"].includes(tab));
    } else {
      b.classList.toggle("active", b.dataset.tab === tab);
    }
  });
  $$(".panel").forEach((p) => p.classList.toggle("active", p.id === `panel-${tab}`));
  const sheet = $("#mobile-more-sheet");
  if (sheet) sheet.hidden = true;
  const menu = $("#more-menu");
  if (menu) menu.hidden = true;
  const moreBtn = $("#more-tools-btn");
  if (moreBtn) moreBtn.setAttribute("aria-expanded", "false");
  if (updateHash) syncHashFromUi(tab);
  return tab;
}

function setupTabs() {
  const onTab = (tab) => {
    if (tab === "more") {
      const sheet = $("#mobile-more-sheet");
      if (sheet) sheet.hidden = !sheet.hidden;
      return;
    }
    activateTab(tab, { updateHash: true });
  };
  $$(".tab-btn").forEach((btn) => {
    if (btn.classList.contains("more-trigger")) return;
    btn.addEventListener("click", () => onTab(btn.dataset.tab));
  });
  $$(".mobile-tab, .mobile-sheet-btn, .more-item").forEach((btn) => {
    btn.addEventListener("click", () => onTab(btn.dataset.tab));
  });
  const moreBtn = $("#more-tools-btn");
  const menu = $("#more-menu");
  moreBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    if (!menu) return;
    const open = menu.hidden;
    menu.hidden = !open;
    moreBtn.setAttribute("aria-expanded", open ? "true" : "false");
  });
  document.addEventListener("click", (e) => {
    if (!menu || menu.hidden) return;
    if (e.target.closest(".more-wrap")) return;
    menu.hidden = true;
    moreBtn?.setAttribute("aria-expanded", "false");
  });
}

function setupHelp() {
  const panel = $("#help-panel");
  const open = () => {
    if (panel) panel.hidden = false;
  };
  const close = () => {
    if (panel) panel.hidden = true;
    try {
      localStorage.setItem("arena_intel_help_v3", "1");
    } catch (_) {}
  };
  $("#btn-help")?.addEventListener("click", open);
  $("#help-close")?.addEventListener("click", close);
  panel?.addEventListener("click", (e) => {
    if (e.target === panel) close();
  });
  // First visit: show help once
  try {
    if (localStorage.getItem("arena_intel_help_v3") !== "1") {
      open();
    }
  } catch (_) {}
}

function currentHash() {
  return (location.hash || "").replace(/^#/, "");
}

function parseRoute(hash) {
  const raw = (hash || "").replace(/^#/, "").trim();
  if (!raw) return { tab: "builds" };
  const segs = raw.split("/").map((s) => {
    try {
      return decodeURIComponent(s);
    } catch {
      return s;
    }
  });
  const tab = (segs[0] || "builds").toLowerCase();
  if (!VALID_TABS.has(tab)) return { tab: "builds" };
  if (tab === "builds") {
    return { tab, role: segs[1] || null };
  }
  if (tab === "gods") {
    return { tab, god: segs[1] || null };
  }
  if (tab === "counter") {
    return {
      tab,
      god: segs[1] || null,
      role: segs[2] || null,
      enemies: segs[3] ? segs[3].split(",").map((x) => x.trim()).filter(Boolean) : [],
    };
  }
  if (tab === "troll") {
    const flags = (segs[3] || "").toLowerCase();
    return {
      tab,
      god: segs[1] || null,
      role: segs[2] || null,
      aspect: !flags || flags.includes("aspect"),
      chaos: flags.includes("chaos"),
    };
  }
  return { tab };
}

function writeHash(hash) {
  const next = hash.startsWith("#") ? hash : `#${hash}`;
  if ((location.hash || "") === next) return;
  // replaceState keeps the URL shareable without re-firing hashchange loops
  history.replaceState(null, "", `${location.pathname}${location.search}${next}`);
}

function syncHashFromUi(tab) {
  if (routeState.suppressHash) return;
  let hash = tab || "builds";
  if (hash === "builds" && routeState.build?.getRole) {
    hash = `builds/${encodeURIComponent(routeState.build.getRole())}`;
  } else if (hash === "gods" && state.selectedGod?.name) {
    hash = `gods/${encodeURIComponent(state.selectedGod.name)}`;
  } else if (hash === "counter") {
    const you = ($("#ctr-you")?.value || "").trim();
    const role = $("#ctr-role")?.value || "Support";
    if (you) {
      const vs = (counterState.enemies || []).map(encodeURIComponent).join(",");
      hash = `counter/${encodeURIComponent(you)}/${encodeURIComponent(role)}${vs ? `/${vs}` : ""}`;
    }
  } else if (hash === "troll") {
    const god = ($("#troll-god")?.value || "").trim();
    const role = $("#troll-role")?.value || "Support";
    if (god) {
      const flags = [];
      if ($("#troll-aspect")?.checked) flags.push("aspect");
      if ($("#troll-chaos")?.checked) flags.push("chaos");
      hash = `troll/${encodeURIComponent(god)}/${encodeURIComponent(role)}${
        flags.length ? `/${flags.join(",")}` : ""
      }`;
    }
  }
  writeHash(hash);
}

function applyRoute(route) {
  if (!route) return;
  routeState.suppressHash = true;
  activateTab(route.tab, { updateHash: false });

  if (route.tab === "builds" && route.role && routeState.build?.setRole) {
    routeState.build.setRole(route.role, { updateHash: false });
  }
  if (route.tab === "gods" && route.god) {
    selectGod(route.god, false);
  }
  if (route.tab === "counter") {
    if (route.god && $("#ctr-you")) $("#ctr-you").value = route.god;
    if (route.role && $("#ctr-role")) {
      const opt = [...($("#ctr-role").options || [])].find(
        (o) => o.value.toLowerCase() === String(route.role).toLowerCase()
      );
      if (opt) $("#ctr-role").value = opt.value;
    }
    if (route.enemies?.length) {
      counterState.enemies = route.enemies
        .map((n) => findGodByName(n)?.name)
        .filter(Boolean)
        .slice(0, 5);
      renderEnemyPicks();
    }
    if (route.god && route.enemies?.length) {
      runCounterFromForm({ updateHash: false });
    }
  }
  if (route.tab === "troll") {
    if (route.god && $("#troll-god")) $("#troll-god").value = route.god;
    if (route.role && $("#troll-role")) {
      const opt = [...($("#troll-role").options || [])].find(
        (o) => o.value.toLowerCase() === String(route.role).toLowerCase()
      );
      if (opt) $("#troll-role").value = opt.value;
    }
    if ($("#troll-aspect")) $("#troll-aspect").checked = route.aspect !== false;
    if ($("#troll-chaos")) $("#troll-chaos").checked = !!route.chaos;
    if (route.god) runTrollFromForm({ updateHash: false });
  }

  queueMicrotask(() => {
    routeState.suppressHash = false;
  });
}

function setupRouting() {
  window.addEventListener("hashchange", () => {
    if (routeState.suppressHash) return;
    applyRoute(parseRoute(currentHash()));
  });
  applyRoute(parseRoute(currentHash()));
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
    activateTab("gods", { updateHash: false });
  }
  if (!routeState.suppressHash && switchTab) {
    writeHash(`gods/${encodeURIComponent(g.name)}`);
  } else if (!routeState.suppressHash && !switchTab) {
    // Stay on current tab (e.g. tiers) but still allow share links when on gods
    const active = $$(".tab-btn").find((b) => b.classList.contains("active"))?.dataset.tab;
    if (active === "gods") writeHash(`gods/${encodeURIComponent(g.name)}`);
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

  // Ambient pantheon glow on dossier
  const dossierEl = document.querySelector(".god-dossier");
  if (dossierEl) {
    const pan = String(g.pantheon || "")
      .toLowerCase()
      .replace(/\s+/g, "-");
    dossierEl.dataset.pantheon = pan;
  }

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
  const conf = g.confidence;
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
  const shareData = {
    mode: isAspect ? "aspect" : "base",
    god: g.name,
    role,
    title: `${g.name} · ${label}`,
    subtitle: `${role} · ${isAspect ? "aspect path" : "base kit"} · ${g.primary_damage_type || ""} · tier ${g.tier || "?"}`,
    why: gb.why || "",
    starter: gb.starter?.name || "",
    items: itemsForShare(items),
    tags: [
      isAspect ? "aspect" : "base",
      role,
      gb.archetype ? String(gb.archetype).replace(/_/g, " ") : null,
      `actives ${nAct}/${maxA}`,
    ].filter(Boolean),
    footerLeft: `PATCH · KIT · ${role.toUpperCase()}`,
    deeplink: `#gods/${encodeURIComponent(g.name)}`,
  };
  return `
    <div class="card build-card god-role-build simple-build ${roleClass(role)} ${isAspect ? "is-aspect" : ""}">
      <h3>${escapeHtml(label)}</h3>
      <p class="card-plain-what">Buy top → bottom${isAspect ? " · aspect" : " · base kit"}</p>
      ${
        isAspect && (gb.aspect_description || aspectMeta?.description)
          ? `<p class="aspect-blurb">${escapeHtml(
              String(gb.aspect_description || aspectMeta.description).slice(0, 180)
            )}</p>`
          : ""
      }
      <div class="starter-line"><span class="tag-start">Start</span> ${escapeHtml(gb.starter?.name || "—")}</div>
      ${loadoutRail(items)}
      <ol class="buy-list simple-buy">
        ${items.map((it, i) => buyRow(it, i + 1, { simple: true })).join("")}
      </ol>
      <div class="muted gbc-relics">Relics: ${(gb.relics || []).map((r) => r.name).join(", ") || "—"}</div>
      <details class="extra-details">
        <summary>Why this path?</summary>
        <p class="why">${escapeHtml(gb.why || "")}</p>
        <div class="build-meta">
          ${gb.archetype ? `<span class="pill">${escapeHtml(String(gb.archetype).replace(/_/g, " "))}</span>` : ""}
          <span class="pill">pen ≈ ${fmt(penG, 0)}</span>
          <span class="pill">actives ${nAct}/${maxA}</span>
        </div>
      </details>
      ${shareBar(shareData)}
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

  const setRole = (role, { updateHash = true } = {}) => {
    const hit = roles.find((r) => r.toLowerCase() === String(role || "").toLowerCase());
    if (!hit) return false;
    activeRole = hit;
    pills.querySelectorAll(".role-pill").forEach((b) =>
      b.classList.toggle("active", b.dataset.role === activeRole)
    );
    if (search) search.value = "";
    render();
    if (updateHash) syncHashFromUi("builds");
    return true;
  };

  const render = () => {
    const data = state.builds?.roles?.[activeRole];
    const t = data?.template || {};
    const job = ROLE_JOB[activeRole] || { title: activeRole, blurb: t.description || "" };
    const pri = t.priority_stats || Object.keys(t.stat_priorities || {}).slice(0, 5);
    const commons = t.common_items || t.top_scored_items || [];
    const st = t.typical_starter || t.starter;

    setActiveRoleTheme(activeRole);
    const rj = $("#role-job");
    if (rj) {
      rj.className = `card role-job ${roleClass(activeRole)}`;
      rj.innerHTML = `
        <div class="role-job-head">
          <h2>${escapeHtml(job.title)}</h2>
        </div>
        <p class="role-job-blurb">${escapeHtml(job.blurb || t.description || "")}</p>
        ${
          st
            ? `<p class="muted">Common starter idea: <strong>${escapeHtml(st.name)}</strong> — still pick a god below for a full path.</p>`
            : ""
        }
        <p class="muted" style="margin:0">This is only role context. The <strong>god cards below</strong> are the real builds.</p>
      `;
    }

    const q = (search.value || "").toLowerCase().trim();
    let gods = [...(data?.recommended_gods || [])].sort(
      (a, b) => (a.rank ?? 99) - (b.rank ?? 99)
    );
    if (q) gods = gods.filter((g) => (g.god || "").toLowerCase().includes(q));
    const countEl = $("#build-god-count");
    if (countEl) countEl.textContent = `(${gods.length} in ${activeRole})`;

    $("#build-gods").innerHTML = gods.length
      ? gods.map((gb) => godBuildCard(gb, activeRole)).join("")
      : emptyHud(
          "No gods match",
          q
            ? `Nothing in ${activeRole} matches “${q}”. Clear the search or try another role.`
            : `No builds for ${activeRole} yet.`
        );
  };

  pills.querySelectorAll(".role-pill").forEach((btn) => {
    btn.addEventListener("click", () => setRole(btn.dataset.role));
  });
  search.addEventListener("input", render);
  $("#build-gods").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-open-god]");
    if (!btn) return;
    selectGod(btn.getAttribute("data-open-god"), true);
  });

  routeState.build = {
    getRole: () => activeRole,
    setRole,
  };
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
  const shareData = {
    mode: gb.is_aspect ? "aspect" : "base",
    god: gb.god,
    role,
    title: `${gb.god} · ${role}`,
    subtitle: `Tier ${gb.tier || "?"} · #${gb.rank ?? "—"} · ${gb.damage_type || ""} · ${gb.is_aspect ? gb.aspect_name || "aspect" : "base kit"}`,
    why: gb.why || "",
    starter: gb.starter?.name || "",
    items: itemsForShare(itemsG),
    tags: [
      gb.is_aspect ? "aspect" : "kit-fit",
      role,
      gb.archetype ? String(gb.archetype).replace(/_/g, " ") : null,
      gb.patch_trajectory || null,
    ].filter(Boolean),
    footerLeft: `CONQUEST // ${role.toUpperCase()}`,
    deeplink: `#gods/${encodeURIComponent(gb.god)}`,
  };
  const shortWhy = String(gb.why || "").split(".")[0];
  return `
    <article class="card build-card god-build-card simple-build ${roleClass(role)}">
      <header class="gbc-head">
        <h3>
          ${escapeHtml(gb.god)}
          <span class="tier-pill tier-${gb.tier || ""}">${escapeHtml(gb.tier || "?")}</span>
        </h3>
        <p class="card-plain-what">
          <strong>${escapeHtml(role)}</strong> buy order — top first${gb.is_aspect ? " · aspect path" : ""}
        </p>
      </header>
      ${shortWhy ? `<p class="why simple-why">${escapeHtml(shortWhy)}.</p>` : ""}
      <div class="starter-line"><span class="tag-start">Start</span> ${escapeHtml(gb.starter?.name || "—")}</div>
      ${loadoutRail(itemsG)}
      <ol class="buy-list simple-buy">
        ${itemsG.map((it, i) => buyRow(it, i + 1, { simple: true })).join("")}
      </ol>
      <div class="muted gbc-relics">Relics: ${(gb.relics || []).map((r) => r.name).join(", ") || "—"}</div>
      <details class="extra-details">
        <summary>More detail</summary>
        <div class="build-meta">
          ${gb.archetype ? `<span class="pill">${escapeHtml(String(gb.archetype).replace(/_/g, " "))}</span>` : ""}
          <span class="pill">pen ≈ ${fmt(penG, 0)}</span>
          ${showMit ? `<span class="pill">mit ≈ ${fmt(mitG, 0)}</span>` : ""}
        </div>
        ${
          effects.length
            ? `<div class="kit-effects">${effects
                .slice(0, 6)
                .map((t) => `<span class="tag effect">${escapeHtml(t)}</span>`)
                .join("")}</div>`
            : ""
        }
        <p class="why">${escapeHtml(gb.why || "")}</p>
      </details>
      <div class="card-actions">
        <button type="button" class="btn-share" data-share-id="${registerShare(shareData)}">Share</button>
        <button type="button" class="linkish" data-open-god="${escapeAttr(gb.god)}">All roles for this god →</button>
      </div>
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

function buyRow(it, n, opts = {}) {
  if (!it) return "";
  const kind = slotKind(it);
  const simple = !!opts.simple;
  const tags = [];
  if (!simple) {
    if (it.slot) tags.push({ t: it.slot, metal: kind });
    if (it.is_active) tags.push({ t: "active", metal: "active" });
    if (it.pen) tags.push({ t: `pen ${it.pen}`, metal: "pen" });
    if (it.damp) tags.push({ t: `damp ${it.damp}`, metal: "mitigate" });
    if (it.plat) tags.push({ t: `plat ${it.plat}`, metal: "mitigate" });
    if (it.ten) tags.push({ t: `ten ${it.ten}`, metal: "mitigate" });
  }
  if (it.troll) tags.push({ t: "troll", metal: "troll" });
  if (it.counter || it.is_diff) tags.push({ t: "counter", metal: "counter" });
  if (it.is_active && simple) tags.push({ t: "active", metal: "active" });
  const slotClass = `is-${kind}${it.is_diff ? " is-diff" : ""}`;
  const why = it.why
    ? `<details class="item-why-details"><summary>Why?</summary><div class="item-why">${escapeHtml(
        it.why
      )}</div></details>`
    : "";
  return `<li class="buy-row ${slotClass}" title="${escapeAttr(it.why || it.effect || "")}">
    <span class="buy-n">${n}</span>
    <div class="buy-main">
      <span class="buy-name">${escapeHtml(it.name)}</span>
      ${why}
    </div>
    <span class="buy-tags">${tags
      .map((x) => `<span class="tag metal-${escapeAttr(x.metal)}">${escapeHtml(x.t)}</span>`)
      .join("")}</span>
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
  const divers = [];
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
    if (
      isPhys &&
      (tags.has("gap_close") || tags.has("mobile") || tags.has("execute") || tags.has("heavy_shield"))
    ) {
      divers.push(g.name);
    }
  }

  const reasons = [];
  const need_mprot = magical >= 2 || magical > physical;
  const need_pprot = physical >= 2 || (physical >= 1 && magical <= 1);
  const need_anti_crit = critGods.length >= 1;
  const need_antiheal = healers.length >= 1;
  const need_magi = ccGods.length >= 2 || (ccGods.length >= 1 && magical >= 2);
  const need_anti_as = need_anti_crit;
  const need_dive_shell = divers.length >= 1 && physical >= 2;

  if (magical >= 3) reasons.push(`Heavy magic (${Math.floor(magical)}): Genji / Oni / mprot`);
  else if (magical >= 2) reasons.push(`Magic pressure (${Math.floor(magical)}): magical defense`);
  if (physical >= 2) reasons.push(`Physical front (${Math.floor(physical)}): Breastplate / Spectral`);
  if (need_dive_shell) {
    reasons.push(`Dive (${divers.join(", ")}): shell first before antiheal greed`);
  }
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
    divers,
    mage_names: mageNames,
    phys_names: physNames,
    need_mprot,
    need_pprot,
    need_anti_crit,
    need_antiheal,
    need_magi,
    need_anti_as,
    need_dive_shell,
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
    const boost = threat.need_dive_shell ? 70 : 55;
    if (n.includes("breastplate") || n.includes("valor")) {
      s += boost;
      why.push("vs physical — Breastplate");
    } else if (pprot >= 40) {
      s += 40 + (threat.need_dive_shell ? 15 : 0);
      why.push("high pprot");
    } else if (pprot >= 25) s += 18;
  }
  if (threat.need_anti_crit) {
    if (n.includes("spectral") || n.includes("nemean")) {
      s += 85;
      why.push("anti-crit vs ADC");
    }
    if (n.includes("midgardian")) {
      s += threat.need_dive_shell ? 62 : 48;
      why.push("cut enemy AS");
    }
  }
  if (threat.need_antiheal) {
    const ah =
      threat.need_dive_shell && (role === "Support" || role === "Solo") ? 52 : 78;
    if (
      n.includes("contagion") ||
      n.includes("divine ruin") ||
      n.includes("pestilence") ||
      n.includes("brawler")
    ) {
      s += ah;
      why.push("anti-heal");
    } else if (passive.includes("heal") && (passive.includes("reduc") || passive.includes("anti"))) {
      s += threat.need_dive_shell ? 28 : 50;
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
  // Shell (dive + turrets) before antiheal greed — matches CLI counter engine
  const wanted = [];
  const dive = !!threat.need_dive_shell;
  if (threat.need_pprot && (role === "Support" || role === "Solo" || role === "Jungle")) {
    wanted.push("breastplate");
  }
  if (threat.need_mprot && threat.magical_count >= 2) {
    wanted.push("genji");
    if (threat.magical_count >= 3) wanted.push("oni hunter");
  }
  if (dive && (role === "Support" || role === "Solo")) wanted.push("midgardian");
  if (threat.need_anti_crit) wanted.push("spectral");
  if (threat.need_anti_as && (role === "Support" || role === "Solo") && !wanted.includes("midgardian")) {
    wanted.push("midgardian");
  }
  if (threat.need_antiheal) {
    wanted.push(role === "Support" || role === "Solo" ? "contagion" : "divine ruin");
  }
  if (threat.need_magi) wanted.push("magi");

  const items = (state.items || []).filter(isT3Item);
  const byName = Object.fromEntries(items.map((it) => [it.name, it]));
  let path = baselineNames.map((n) => byName[n]).filter(Boolean);
  if (!path.length) {
    // No baseline — pure counter top items
    path = [];
  }
  const seen = new Set(path.map((p) => p.name));
  const maxInject =
    (role === "Support" || role === "Solo") && dive ? 4 : role === "Support" || role === "Solo" ? 3 : 2;
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
  return getBaselineItems(god, role).map((i) => i.name);
}

function getBaselineItems(god, role) {
  const byRole = god.conquest_by_role || {};
  if (byRole[role]?.items?.length) return byRole[role].items;
  const rec = state.builds?.roles?.[role]?.recommended_gods || [];
  const hit = rec.find((g) => g.god === god.name);
  if (hit?.items?.length) return hit.items;
  return [];
}

function getStarter(god, role) {
  const byRole = god.conquest_by_role || {};
  if (byRole[role]?.starter) return byRole[role].starter;
  const rec = state.builds?.roles?.[role]?.recommended_gods || [];
  const hit = rec.find((g) => g.god === god.name);
  return hit?.starter || null;
}

function markPathDiffs(baselineItems, counterItems) {
  const baseSet = new Set((baselineItems || []).map((i) => i.name));
  return (counterItems || []).map((it) => ({
    ...it,
    is_diff: !baseSet.has(it.name),
    counter: it.counter || !baseSet.has(it.name),
  }));
}

function pathCompareHtml(baselineItems, counterItems, starter) {
  const base = baselineItems || [];
  const ctr = markPathDiffs(base, counterItems || []);
  const baseBuy = base.length
    ? base.map((it, i) => buyRow(it, i + 1)).join("")
    : `<li class="muted" style="list-style:none;padding:8px">No kit baseline for this role.</li>`;
  const ctrBuy = ctr.map((it, i) => buyRow(it, i + 1)).join("");
  return `
    <div class="path-compare">
      <div class="path-col">
        <h4 class="path-col-title">Kit path</h4>
        <p class="muted path-col-sub">Default kit-fit buy order</p>
        <div class="starter-line"><span class="tag-start">Starter</span> ${escapeHtml(
          starter?.name || "—"
        )}</div>
        ${base.length ? loadoutRail(base) : ""}
        <ol class="buy-list">${baseBuy}</ol>
      </div>
      <div class="path-col path-col-counter">
        <h4 class="path-col-title">Lobby path</h4>
        <p class="muted path-col-sub">Re-weighted vs enemy 5 · <span class="diff-legend">highlighted = swap</span></p>
        <div class="starter-line"><span class="tag-start">Starter</span> ${escapeHtml(
          starter?.name || "—"
        )}</div>
        ${loadoutRail(ctr)}
        <ol class="buy-list">${ctrBuy}</ol>
      </div>
    </div>`;
}

function renderEnemyPicks() {
  const box = $("#ctr-enemy-picks");
  if (!box) return;
  const slots = [];
  for (let i = 0; i < 5; i++) {
    const n = counterState.enemies[i];
    if (n) {
      slots.push(
        `<button type="button" class="lobby-slot filled" data-rm="${i}" title="Remove ${escapeAttr(
          n
        )}">${escapeHtml(n)}</button>`
      );
    } else {
      slots.push(`<div class="lobby-slot">Slot ${i + 1}</div>`);
    }
  }
  box.innerHTML = slots.join("");
  box.querySelectorAll("[data-rm]").forEach((btn) => {
    btn.addEventListener("click", () => {
      counterState.enemies.splice(Number(btn.getAttribute("data-rm")), 1);
      renderEnemyPicks();
    });
  });
}

function threatMetersHtml(threat) {
  const meters = [
    { key: "magic", label: "Magic", val: Math.min(1, (threat.magical_count || 0) / 5) },
    { key: "phys", label: "Physical", val: Math.min(1, (threat.physical_count || 0) / 5) },
    { key: "crit", label: "Crit", val: threat.need_anti_crit ? 0.85 : 0.15 },
    { key: "heal", label: "Heal", val: threat.need_antiheal ? 0.9 : 0.1 },
    { key: "cc", label: "CC", val: threat.need_magi ? 0.8 : 0.2 },
  ];
  return `<div class="threat-meters">${meters
    .map(
      (m) => `<div class="threat-meter">
      <span class="label">${m.label}</span>
      <div class="track"><div class="fill" style="width:${Math.round(m.val * 100)}%"></div></div>
      <span class="val">${Math.round(m.val * 100)}</span>
    </div>`
    )
    .join("")}</div>`;
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

function runTrollFromForm({ updateHash = true } = {}) {
  const god = findGodByName($("#troll-god")?.value);
  const role = $("#troll-role")?.value || "Support";
  const useAspect = !!$("#troll-aspect")?.checked;
  const chaos = !!$("#troll-chaos")?.checked;
  const box = $("#troll-result");
  if (!box) return;
  if (!god) {
    box.innerHTML = emptyHud("Pick a god", "Type a valid god name, then generate a kit-true troll path.");
    return;
  }
  const t = buildTrollPathJS(god, role, useAspect, chaos);
  const shareData = {
    mode: "troll",
    god: god.name,
    role,
    title: t.title,
    subtitle: `${god.name} · ${role}${t.aspect ? ` · ${t.aspect.name}` : ""} · troll path`,
    why: t.monologue || t.disclaimer || "",
    starter: t.starter?.name || "",
    items: itemsForShare(t.items),
    tags: ["TROLL", t.primary.replace(/_/g, " "), t.secondary.replace(/_/g, " ")],
    footerLeft: "TROLL / MEME — NOT RANKED",
    aspect: useAspect,
    chaos,
    deeplink: `#troll/${encodeURIComponent(god.name)}/${encodeURIComponent(role)}/${[
      useAspect ? "aspect" : null,
      chaos ? "chaos" : null,
    ]
      .filter(Boolean)
      .join(",") || "base"}`,
  };
  box.innerHTML = `
    <article class="card build-card god-build-card is-troll ${roleClass(role)}">
      <span class="hud-br bl" aria-hidden="true"></span><span class="hud-br br" aria-hidden="true"></span>
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
      ${loadoutRail(t.items)}
      <ol class="buy-list">
        ${t.items.map((it, i) => buyRow(it, i + 1)).join("")}
      </ol>
      ${
        t.baseline?.length
          ? `<p class="muted">Serious baseline (for contrast): ${t.baseline.map(escapeHtml).join(" → ")}</p>`
          : ""
      }
      ${trustLine("meme only — not ranked advice")}
      ${shareBar(shareData)}
    </article>
  `;
  if (updateHash) syncHashFromUi("troll");
}

function setupTroll() {
  const box = $("#troll-result");
  if (box && !box.innerHTML.trim()) {
    box.innerHTML = emptyHud(
      "Troll path standby",
      "Pick a god + role. We build a kit-true off-meta path designed to be frustrating — not ranked advice."
    );
  }
  $("#troll-run")?.addEventListener("click", () => runTrollFromForm({ updateHash: true }));
}

function runCounterFromForm({ updateHash = true } = {}) {
  const you = findGodByName($("#ctr-you")?.value);
  const role = $("#ctr-role")?.value || "Support";
  const threatEl = $("#ctr-threat");
  const resultEl = $("#ctr-result");
  if (!threatEl || !resultEl) return;

  if (!you) {
    threatEl.innerHTML = "";
    resultEl.innerHTML = emptyHud("Pick your god", "Choose your god + role, then fill enemy lobby slots (type name + Enter).");
    return;
  }
  if (!counterState.enemies.length) {
    threatEl.innerHTML = "";
    resultEl.innerHTML = emptyHud(
      "Enemy lobby empty",
      "Add at least one enemy (up to 5). Threat meters and the lobby path unlock after that."
    );
    return;
  }

  const enemyGods = counterState.enemies.map(findGodByName).filter(Boolean);
  const threat = analyzeEnemyTeamJS(enemyGods);
  threatEl.innerHTML = `
    <strong>Threat</strong> — ${escapeHtml(threat.summary)}
    ${threatMetersHtml(threat)}
    <ul class="threat-list">${threat.reasons.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}</ul>
    <div class="muted">Magic ${fmt(threat.magical_count, 0)} · Physical ${fmt(threat.physical_count, 0)}</div>
  `;

  const baselineItems = getBaselineItems(you, role);
  const baselineNames = baselineItems.map((i) => i.name);
  const path = markPathDiffs(baselineItems, injectCounterCores(baselineNames, threat, role));
  const starter = getStarter(you, role);

  const vsList = enemyGods.map((g) => g.name);
  const vs = vsList.join(", ");
  const shareData = {
    mode: "counter",
    god: you.name,
    role,
    enemies: vsList,
    title: `${you.name} · ${role} · counter`,
    subtitle: `vs ${vs}`,
    why: threat.summary || "",
    starter: starter?.name || "",
    items: itemsForShare(path),
    tags: [
      "counter",
      threat.need_anti_crit ? "anti-crit" : null,
      threat.need_mprot ? "mprot" : null,
      threat.need_antiheal ? "antiheal" : null,
      threat.need_magi ? "anti-CC" : null,
    ].filter(Boolean),
    footerLeft: "COUNTER PATH · LOBBY INTEL",
    deeplink: `#counter/${encodeURIComponent(you.name)}/${encodeURIComponent(role)}/${vsList
      .map(encodeURIComponent)
      .join(",")}`,
  };

  resultEl.innerHTML = `
    <article class="card build-card god-build-card ${roleClass(role)}">
      <span class="hud-br bl" aria-hidden="true"></span><span class="hud-br br" aria-hidden="true"></span>
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
        ${path.some((p) => p.is_diff) ? `<span class="pill ice">swaps highlighted</span>` : ""}
      </div>
      ${pathCompareHtml(baselineItems, path, starter)}
      ${trustLine("lobby re-weight · not live WR")}
      ${shareBar(shareData)}
    </article>
  `;
  if (updateHash) syncHashFromUi("counter");
}

function setupCounter() {
  const list = $("#ctr-god-list");
  if (!list) return;
  const names = [...(state.gods || [])].map((g) => g.name).sort();
  list.innerHTML = names.map((n) => `<option value="${escapeAttr(n)}"></option>`).join("");

  const resultEl = $("#ctr-result");
  if (resultEl && !resultEl.innerHTML.trim()) {
    resultEl.innerHTML = emptyHud(
      "Counter lobby standby",
      "Your god + up to 5 enemies → kit path vs lobby path side-by-side."
    );
  }

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

  $("#ctr-run")?.addEventListener("click", () => runCounterFromForm({ updateHash: true }));
}

async function main() {
  setupTabs();
  setupShareUi();
  setupHelp();
  const loading = $("#loading");
  try {
    await loadData();
    loading.style.display = "none";
    $("#app-main").style.display = "block";

    const exported = state.meta?.exported_at || state.meta?.scraped_at || "";
    const analysis = state.meta?.analysis_last_analysis_at || state.meta?.last_analysis_at || "";
    $("#meta-line").textContent = [
      `${(state.gods || []).length} gods`,
      `${(state.items || []).length} items`,
      exported ? `data ${String(exported).slice(0, 10)}` : "live data",
      "model: kit + patch — not live win rate",
    ]
      .filter(Boolean)
      .join(" · ");

    setupBuilds();
    setupCounter();
    setupTroll();
    setupGods();
    setupTiers();
    setupItems();
    setupAboutMomentum();
    renderEnemyPicks();
    setupRouting();
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
