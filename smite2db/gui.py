"""
Simple SMITE 2 desktop GUI (tkinter).

Browse tier lists, god metrics, and Conquest builds from the local SQLite DB.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .db import DEFAULT_DB, connect
from .conquest_builds import generate_all, ROLE_PROFILES

APP_TITLE = "SMITE 2 Database"
ROOT = Path(__file__).resolve().parent.parent
BUILDS_JSON = ROOT / "data" / "conquest_builds.json"


class Smite2App(tk.Tk):
    def __init__(self, db_path: Path | None = None):
        super().__init__()
        self.db_path = Path(db_path) if db_path else DEFAULT_DB
        self.title(APP_TITLE)
        self.geometry("1100x720")
        self.minsize(900, 560)

        # Dark-ish neutral theme via ttk
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("TNotebook.Tab", padding=[12, 6])
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=24, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self._build_menu()
        self._build_header()
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.tab_tiers = ttk.Frame(self.nb)
        self.tab_gods = ttk.Frame(self.nb)
        self.tab_builds = ttk.Frame(self.nb)
        self.tab_items = ttk.Frame(self.nb)
        self.nb.add(self.tab_tiers, text="  Tier List  ")
        self.nb.add(self.tab_gods, text="  Gods  ")
        self.nb.add(self.tab_builds, text="  Conquest Builds  ")
        self.nb.add(self.tab_items, text="  Items  ")

        self._init_tiers_tab()
        self._init_gods_tab()
        self._init_builds_tab()
        self._init_items_tab()

        self.status = tk.StringVar(value=self._status_text())
        ttk.Label(self, textvariable=self.status, anchor="w").pack(
            fill=tk.X, padx=12, pady=(0, 8)
        )

        if not self.db_path.exists():
            messagebox.showwarning(
                "Database missing",
                f"No database at:\n{self.db_path}\n\nRun scrape first:\npython -m smite2db.scrape",
            )
        else:
            self.refresh_all()

    # ------------------------------------------------------------------ UI
    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        file_m = tk.Menu(menubar, tearoff=0)
        file_m.add_command(label="Refresh data", command=self.refresh_all)
        file_m.add_separator()
        file_m.add_command(label="Run analysis…", command=self._run_analysis)
        file_m.add_command(label="Rebuild Conquest builds…", command=self._run_builds)
        file_m.add_separator()
        file_m.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_m)

        help_m = tk.Menu(menubar, tearoff=0)
        help_m.add_command(label="About", command=self._about)
        menubar.add_cascade(label="Help", menu=help_m)
        self.config(menu=menubar)

    def _build_header(self) -> None:
        hdr = ttk.Frame(self)
        hdr.pack(fill=tk.X, padx=12, pady=10)
        ttk.Label(hdr, text="SMITE 2 Data Base", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(hdr, text="Refresh", command=self.refresh_all).pack(side=tk.RIGHT, padx=4)
        ttk.Button(hdr, text="Rebuild builds", command=self._run_builds).pack(side=tk.RIGHT, padx=4)
        ttk.Button(hdr, text="Run analysis", command=self._run_analysis).pack(side=tk.RIGHT, padx=4)

    def _status_text(self) -> str:
        if not self.db_path.exists():
            return f"DB missing · {self.db_path}"
        try:
            conn = connect(self.db_path)
            gods = conn.execute("SELECT COUNT(*) c FROM gods").fetchone()["c"]
            items = conn.execute("SELECT COUNT(*) c FROM items").fetchone()["c"]
            tiers = 0
            try:
                tiers = conn.execute(
                    "SELECT COUNT(*) c FROM tier_list WHERE scope='overall' AND entity_type='god'"
                ).fetchone()["c"]
            except sqlite3.OperationalError:
                pass
            meta = ""
            try:
                row = conn.execute(
                    "SELECT value FROM analysis_meta WHERE key='last_analysis_at'"
                ).fetchone()
                if row:
                    meta = f" · analyzed {row['value'][:19]}"
            except sqlite3.OperationalError:
                pass
            conn.close()
            return f"{self.db_path} · {gods} gods · {items} items · {tiers} ranked{meta}"
        except Exception as exc:  # noqa: BLE001
            return f"DB error: {exc}"

    # ------------------------------------------------------------------ Tiers
    def _init_tiers_tab(self) -> None:
        top = ttk.Frame(self.tab_tiers)
        top.pack(fill=tk.X, padx=8, pady=8)
        ttk.Label(top, text="Scope:").pack(side=tk.LEFT)
        self.tier_scope = tk.StringVar(value="overall")
        self.tier_scope_cb = ttk.Combobox(
            top, textvariable=self.tier_scope, width=28, state="readonly"
        )
        self.tier_scope_cb.pack(side=tk.LEFT, padx=6)
        self.tier_scope_cb.bind("<<ComboboxSelected>>", lambda e: self.load_tiers())

        ttk.Label(top, text="Filter tier:").pack(side=tk.LEFT, padx=(12, 0))
        self.tier_filter = tk.StringVar(value="All")
        ttk.Combobox(
            top,
            textvariable=self.tier_filter,
            values=["All", "S", "A", "B", "C", "D"],
            width=6,
            state="readonly",
        ).pack(side=tk.LEFT, padx=6)
        self.tier_filter.trace_add("write", lambda *_: self.load_tiers())

        cols = ("rank", "tier", "name", "score", "patch", "kit", "build", "conf")
        self.tier_tree = ttk.Treeview(
            self.tab_tiers, columns=cols, show="headings", selectmode="browse"
        )
        headings = {
            "rank": ("#", 50),
            "tier": ("Tier", 50),
            "name": ("God / Item", 180),
            "score": ("Score", 70),
            "patch": ("Patch", 70),
            "kit": ("Kit", 70),
            "build": ("Build", 70),
            "conf": ("Conf", 60),
        }
        for c, (h, w) in headings.items():
            self.tier_tree.heading(c, text=h)
            self.tier_tree.column(c, width=w, anchor=tk.CENTER if c != "name" else tk.W)

        scroll = ttk.Scrollbar(self.tab_tiers, orient=tk.VERTICAL, command=self.tier_tree.yview)
        self.tier_tree.configure(yscrollcommand=scroll.set)
        self.tier_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=(0, 8))
        scroll.pack(side=tk.LEFT, fill=tk.Y, pady=(0, 8), padx=(0, 4))

        self.tier_detail = tk.Text(self.tab_tiers, width=40, wrap=tk.WORD, font=("Segoe UI", 10))
        self.tier_detail.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=8, pady=(0, 8))
        self.tier_tree.bind("<<TreeviewSelect>>", self._on_tier_select)
        self.tier_tree.bind("<Double-1>", self._tier_goto_god)

    def load_tiers(self) -> None:
        self.tier_tree.delete(*self.tier_tree.get_children())
        self.tier_detail.delete("1.0", tk.END)
        if not self.db_path.exists():
            return
        conn = connect(self.db_path)
        try:
            scopes = [
                r["scope"]
                for r in conn.execute(
                    "SELECT DISTINCT scope FROM tier_list ORDER BY scope"
                )
            ]
        except sqlite3.OperationalError:
            conn.close()
            self.tier_detail.insert(
                tk.END, "No tier_list table yet.\n\nFile → Run analysis…"
            )
            return
        self.tier_scope_cb["values"] = scopes or ["overall"]
        if self.tier_scope.get() not in scopes and scopes:
            self.tier_scope.set(scopes[0])

        scope = self.tier_scope.get()
        filt = self.tier_filter.get()
        q = """
            SELECT rank_in_scope, tier, entity_name, entity_type, score,
                   patch_score, kit_score, build_score, confidence, rationale
            FROM tier_list
            WHERE scope = ?
        """
        params: list = [scope]
        if filt and filt != "All":
            q += " AND tier = ?"
            params.append(filt)
        q += " ORDER BY rank_in_scope"
        rows = conn.execute(q, params).fetchall()
        conn.close()

        for r in rows:
            self.tier_tree.insert(
                "",
                tk.END,
                iid=f"{r['entity_type']}:{r['entity_name']}",
                values=(
                    r["rank_in_scope"],
                    r["tier"],
                    r["entity_name"],
                    _fmt(r["score"]),
                    _fmt(r["patch_score"]),
                    _fmt(r["kit_score"]),
                    _fmt(r["build_score"]),
                    f"{r['confidence']:.0%}" if r["confidence"] is not None else "—",
                ),
                tags=(r["tier"],),
            )
        # light tier colors
        self.tier_tree.tag_configure("S", background="#fff3cd")
        self.tier_tree.tag_configure("A", background="#e8f5e9")
        self.tier_tree.tag_configure("B", background="#e3f2fd")
        self.tier_tree.tag_configure("C", background="#f3e5f5")
        self.tier_tree.tag_configure("D", background="#eceff1")

    def _on_tier_select(self, _evt=None) -> None:
        sel = self.tier_tree.selection()
        if not sel:
            return
        iid = sel[0]
        etype, name = iid.split(":", 1)
        vals = self.tier_tree.item(iid, "values")
        conn = connect(self.db_path)
        row = conn.execute(
            """
            SELECT rationale, components_json FROM tier_list
            WHERE scope=? AND entity_type=? AND entity_name=?
            """,
            (self.tier_scope.get(), etype, name),
        ).fetchone()
        conn.close()
        self.tier_detail.delete("1.0", tk.END)
        self.tier_detail.insert(
            tk.END,
            f"{name}\n"
            f"{'=' * len(name)}\n"
            f"Tier {vals[1]}  ·  rank #{vals[0]}  ·  score {vals[3]}\n"
            f"Patch {vals[4]}  Kit {vals[5]}  Build {vals[6]}  Conf {vals[7]}\n\n",
        )
        if row and row["rationale"]:
            self.tier_detail.insert(tk.END, "Rationale\n---------\n")
            self.tier_detail.insert(tk.END, row["rationale"] + "\n\n")
        if etype == "god":
            self.tier_detail.insert(tk.END, "Double-click to open Gods tab.")

    def _tier_goto_god(self, _evt=None) -> None:
        sel = self.tier_tree.selection()
        if not sel:
            return
        etype, name = sel[0].split(":", 1)
        if etype != "god":
            return
        self.nb.select(self.tab_gods)
        self.god_search.set(name)
        self._filter_gods()
        # select in list
        for iid in self.god_list.get_children():
            if self.god_list.item(iid, "values")[0] == name:
                self.god_list.selection_set(iid)
                self.god_list.see(iid)
                self._load_god(name)
                break

    # ------------------------------------------------------------------ Gods
    def _init_gods_tab(self) -> None:
        left = ttk.Frame(self.tab_gods)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        ttk.Label(left, text="Search gods").pack(anchor=tk.W)
        self.god_search = tk.StringVar()
        ent = ttk.Entry(left, textvariable=self.god_search, width=28)
        ent.pack(fill=tk.X, pady=4)
        ent.bind("<KeyRelease>", lambda e: self._filter_gods())

        cols = ("name", "pantheon", "dmg", "tier")
        self.god_list = ttk.Treeview(left, columns=cols, show="headings", height=28, selectmode="browse")
        for c, h, w in (
            ("name", "God", 120),
            ("pantheon", "Pantheon", 90),
            ("dmg", "Dmg", 70),
            ("tier", "Tier", 40),
        ):
            self.god_list.heading(c, text=h)
            self.god_list.column(c, width=w)
        self.god_list.pack(fill=tk.BOTH, expand=True)
        self.god_list.bind("<<TreeviewSelect>>", self._on_god_select)

        right = ttk.Frame(self.tab_gods)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.god_title = ttk.Label(right, text="Select a god", style="Header.TLabel")
        self.god_title.pack(anchor=tk.W)
        self.god_sub = ttk.Label(right, text="", style="Sub.TLabel")
        self.god_sub.pack(anchor=tk.W, pady=(0, 6))

        # metrics strip
        metrics = ttk.Frame(right)
        metrics.pack(fill=tk.X, pady=4)
        self.m_patch = tk.StringVar(value="Patch: —")
        self.m_kit = tk.StringVar(value="Kit: —")
        self.m_build = tk.StringVar(value="Build: —")
        self.m_tier = tk.StringVar(value="Tier: —")
        for v in (self.m_tier, self.m_patch, self.m_kit, self.m_build):
            ttk.Label(metrics, textvariable=v, width=22).pack(side=tk.LEFT, padx=4)

        paned = ttk.Panedwindow(right, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=6)

        ab_frame = ttk.Labelframe(paned, text="Abilities")
        cols_a = ("slot", "name", "dmg5", "str", "int", "cd", "pwr")
        self.ab_tree = ttk.Treeview(ab_frame, columns=cols_a, show="headings", height=8)
        for c, h, w in (
            ("slot", "Slot", 100),
            ("name", "Name", 140),
            ("dmg5", "Dmg R5", 70),
            ("str", "STR%", 55),
            ("int", "INT%", 55),
            ("cd", "CD", 50),
            ("pwr", "Pwr", 50),
        ):
            self.ab_tree.heading(c, text=h)
            self.ab_tree.column(c, width=w, anchor=tk.CENTER if c != "name" and c != "slot" else tk.W)
        self.ab_tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        paned.add(ab_frame, weight=2)

        bot = ttk.Frame(paned)
        paned.add(bot, weight=3)

        build_f = ttk.Labelframe(bot, text="Suggested items (from analysis)")
        build_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        self.god_build_txt = tk.Text(build_f, height=12, wrap=tk.WORD, font=("Consolas", 10))
        self.god_build_txt.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        patch_f = ttk.Labelframe(bot, text="Patch momentum")
        patch_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))
        self.god_patch_txt = tk.Text(patch_f, height=12, wrap=tk.WORD, font=("Consolas", 10))
        self.god_patch_txt.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _filter_gods(self) -> None:
        term = (self.god_search.get() or "").strip().lower()
        self.god_list.delete(*self.god_list.get_children())
        for g in getattr(self, "_god_rows", []):
            if term and term not in g["name"].lower() and term not in (g["pantheon"] or "").lower():
                continue
            self.god_list.insert(
                "",
                tk.END,
                iid=g["name"],
                values=(g["name"], g["pantheon"] or "", g["dmg"] or "", g["tier"] or "—"),
            )

    def load_gods(self) -> None:
        self._god_rows = []
        if not self.db_path.exists():
            return
        conn = connect(self.db_path)
        rows = conn.execute(
            """
            SELECT g.name, g.pantheon, g.primary_damage_type AS dmg,
                   t.tier, t.rank_in_scope
            FROM gods g
            LEFT JOIN tier_list t
              ON t.entity_name = g.name AND t.scope = 'overall' AND t.entity_type = 'god'
            ORDER BY g.name
            """
        ).fetchall()
        conn.close()
        self._god_rows = [dict(r) for r in rows]
        self._filter_gods()

    def _on_god_select(self, _evt=None) -> None:
        sel = self.god_list.selection()
        if not sel:
            return
        self._load_god(sel[0])

    def _load_god(self, name: str) -> None:
        conn = connect(self.db_path)
        g = conn.execute("SELECT * FROM gods WHERE name = ?", (name,)).fetchone()
        if not g:
            conn.close()
            return
        self.god_title.config(text=name)
        self.god_sub.config(
            text=f"{g['title'] or ''} · {g['pantheon'] or ''} · {g['primary_damage_type'] or ''}"
        )

        tier = conn.execute(
            """
            SELECT tier, rank_in_scope, score, patch_score, kit_score, build_score, rationale
            FROM tier_list WHERE scope='overall' AND entity_type='god' AND entity_name=?
            """,
            (name,),
        ).fetchone()
        if tier:
            self.m_tier.set(f"Tier: {tier['tier']}  #{tier['rank_in_scope']}  ({_fmt(tier['score'])})")
            self.m_patch.set(f"Patch: {_fmt(tier['patch_score'])}")
            self.m_kit.set(f"Kit: {_fmt(tier['kit_score'])}")
            self.m_build.set(f"Build: {_fmt(tier['build_score'])}")
        else:
            self.m_tier.set("Tier: — (run analysis)")
            self.m_patch.set("Patch: —")
            self.m_kit.set("Kit: —")
            self.m_build.set("Build: —")

        self.ab_tree.delete(*self.ab_tree.get_children())
        abs_ = conn.execute(
            """
            SELECT a.slot, a.name, m.damage_rank5, m.scaling_str_pct, m.scaling_int_pct,
                   m.cooldown_rank5, m.power_score
            FROM abilities a
            LEFT JOIN ability_metrics m ON m.ability_id = a.id
            WHERE a.god_id = ?
            ORDER BY a.slot_order
            """,
            (g["id"],),
        ).fetchall()
        for a in abs_:
            self.ab_tree.insert(
                "",
                tk.END,
                values=(
                    a["slot"],
                    a["name"],
                    _fmt(a["damage_rank5"]),
                    _fmt(a["scaling_str_pct"]),
                    _fmt(a["scaling_int_pct"]),
                    _fmt(a["cooldown_rank5"]),
                    _fmt(a["power_score"]),
                ),
            )

        self.god_build_txt.delete("1.0", tk.END)
        b = conn.execute(
            "SELECT * FROM god_build_metrics WHERE god_id = ?", (g["id"],)
        ).fetchone()
        if b:
            cores = _safe_json(b["core_items_json"])
            defs = _safe_json(b["defense_items_json"])
            hyb = _safe_json(b["hybrid_items_json"])
            rel = _safe_json(b["relic_suggestions"])
            self.god_build_txt.insert(
                tk.END,
                f"Scaling: {b['primary_scaling']} ({b['damage_type']})\n"
                f"Starter: {b['recommended_starter']}\n\n"
                f"Cores:\n  " + "\n  ".join(cores or []) + "\n\n"
                f"Defense:\n  " + "\n  ".join(defs or []) + "\n\n"
                f"Hybrid:\n  " + "\n  ".join(hyb or []) + "\n\n"
                f"Relics:\n  " + "\n  ".join(rel or []) + "\n\n"
                f"{b['build_notes'] or ''}\n",
            )
        else:
            self.god_build_txt.insert(tk.END, "No build metrics. Run analysis.")

        # conquest tailored if cached
        builds = self._load_builds_cache()
        if builds:
            for role, data in builds.get("roles", {}).items():
                for gb in data.get("recommended_gods", []):
                    if gb.get("god") == name:
                        items = gb.get("items") or gb.get("full_path") or []
                        self.god_build_txt.insert(
                            tk.END,
                            f"\n--- Conquest {role} (1 starter + 6 items) ---\n"
                            f"Starter: {gb.get('starter', {}).get('name')}\n",
                        )
                        for i, it in enumerate(items, 1):
                            self.god_build_txt.insert(
                                tk.END, f"  {i}. {it['name']} ({it.get('cost')}g)\n"
                            )

        self.god_patch_txt.delete("1.0", tk.END)
        p = conn.execute(
            "SELECT * FROM entity_patch_summary WHERE entity_type='god' AND entity_name=?",
            (name,),
        ).fetchone()
        if p:
            self.god_patch_txt.insert(
                tk.END,
                f"Trajectory: {p['trajectory']}\n"
                f"Net weighted: {p['net_weighted_score']:+.2f}\n"
                f"Last 5 patches: {p['recent_5_score']:+.2f}\n"
                f"Buff / Nerf events: {p['buff_events']} / {p['nerf_events']}\n"
                f"Patches touched: {p['patches_touched']}\n"
                f"Last: {p['last_direction']} — {p['last_patch']}\n\n",
            )
            for row in conn.execute(
                """
                SELECT pn.number_label, pn.name, i.direction, i.weighted_score, i.sample_text
                FROM patch_impacts i
                JOIN patch_notes pn ON pn.id = i.patch_id
                WHERE i.entity_type='god' AND i.entity_name=?
                ORDER BY pn.id ASC
                LIMIT 15
                """,
                (name,),
            ):
                lab = row["number_label"] or row["name"][:18]
                self.god_patch_txt.insert(
                    tk.END,
                    f"{lab:8} {row['direction']:7} {row['weighted_score']:+.2f}  "
                    f"{(row['sample_text'] or '')[:70]}\n",
                )
        else:
            self.god_patch_txt.insert(tk.END, "No patch summary for this god.")
        if tier and tier["rationale"]:
            self.god_patch_txt.insert(tk.END, f"\n\nTier rationale:\n{tier['rationale']}")
        conn.close()

    # ------------------------------------------------------------------ Builds
    def _init_builds_tab(self) -> None:
        top = ttk.Frame(self.tab_builds)
        top.pack(fill=tk.X, padx=8, pady=8)
        ttk.Label(top, text="Role:").pack(side=tk.LEFT)
        self.build_role = tk.StringVar(value="Carry")
        cb = ttk.Combobox(
            top,
            textvariable=self.build_role,
            values=list(ROLE_PROFILES.keys()),
            state="readonly",
            width=12,
        )
        cb.pack(side=tk.LEFT, padx=6)
        cb.bind("<<ComboboxSelected>>", lambda e: self.load_builds_view())
        ttk.Button(top, text="Rebuild from DB", command=self._run_builds).pack(side=tk.RIGHT)

        self.build_info = ttk.Label(self.tab_builds, text="", style="Sub.TLabel", wraplength=1000)
        self.build_info.pack(fill=tk.X, padx=12)

        body = ttk.Panedwindow(self.tab_builds, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Labelframe(body, text="Role template · 1 starter + 6 items")
        body.add(left, weight=1)
        self.build_template = tk.Text(left, wrap=tk.WORD, font=("Consolas", 10))
        self.build_template.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        right = ttk.Labelframe(body, text="Top gods in role (tailored)")
        body.add(right, weight=1)
        self.build_gods = tk.Text(right, wrap=tk.WORD, font=("Consolas", 10))
        self.build_gods.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self._builds_cache: dict | None = None

    def _load_builds_cache(self) -> dict | None:
        if self._builds_cache is not None:
            return self._builds_cache
        if BUILDS_JSON.exists():
            try:
                self._builds_cache = json.loads(BUILDS_JSON.read_text(encoding="utf-8"))
                return self._builds_cache
            except json.JSONDecodeError:
                pass
        return None

    def load_builds_view(self) -> None:
        self.build_template.delete("1.0", tk.END)
        self.build_gods.delete("1.0", tk.END)
        data = self._load_builds_cache()
        if not data:
            self.build_info.config(
                text="No conquest_builds.json yet. Click “Rebuild from DB”."
            )
            return
        role = self.build_role.get()
        rd = data.get("roles", {}).get(role)
        if not rd:
            self.build_info.config(text=f"No data for role {role}")
            return
        t = rd["template"]
        self.build_info.config(text=t.get("description", ""))
        starter = t.get("starter") or {}
        items = t.get("items") or t.get("full_path") or []
        n_act = sum(1 for it in items if it.get("is_active"))
        lines = [
            f"ROLE: {role}",
            f"Inventory: 1 starter + 6 items  ·  Actives {n_act}/2 typical (hard max 3)",
            "",
            f"STARTER: {starter.get('name', '—')}  "
            f"(score {starter.get('score')}, {starter.get('cost')}g)",
            "",
            "6 ITEMS (* = Active slot):",
        ]
        for i, it in enumerate(items, 1):
            stats = ", ".join(f"{k}:{v}" for k, v in (it.get("stats") or {}).items())
            star = "*" if it.get("is_active") else " "
            lines.append(
                f"  {i}. {star} {it['name']:28} score={it.get('score')}  "
                f"{it.get('cost')}g  mom={it.get('momentum')}  {stats}"
            )
        lines.append("")
        lines.append("RELICS: " + ", ".join(
            f"{r['name']} ({r.get('score')})" for r in t.get("relics") or []
        ))
        if t.get("starter_alternatives"):
            lines.append("")
            lines.append("Starter alts: " + ", ".join(
                a["name"] for a in t["starter_alternatives"]
            ))
        self.build_template.insert(tk.END, "\n".join(lines))

        gtxt = []
        for gb in rd.get("recommended_gods") or []:
            gtxt.append(
                f"[{gb.get('tier')}] {gb['god']}  ·  {gb.get('damage_type')}  ·  "
                f"{gb.get('scaling')} (STR {gb.get('avg_str_scaling')}% / INT {gb.get('avg_int_scaling')}%)"
            )
            items_g = gb.get("items") or gb.get("full_path") or []
            ga = sum(1 for it in items_g if it.get("is_active"))
            gtxt.append(
                f"  Starter: {(gb.get('starter') or {}).get('name')}  ·  actives {ga}/{gb.get('max_shop_actives', 2)}  ·  pen≈{gb.get('pen_total', '?')}"
            )
            for i, it in enumerate(items_g, 1):
                star = "*" if it.get("is_active") else " "
                gtxt.append(
                    f"  {i}. {star} {it['name']}  ({it.get('cost')}g, score {it.get('score')})"
                )
            gtxt.append(
                "  Relics: "
                + ", ".join(r["name"] for r in gb.get("relics") or [])
            )
            gtxt.append("")
        self.build_gods.insert(tk.END, "\n".join(gtxt) if gtxt else "No god builds.")

    # ------------------------------------------------------------------ Items
    def _init_items_tab(self) -> None:
        top = ttk.Frame(self.tab_items)
        top.pack(fill=tk.X, padx=8, pady=8)
        ttk.Label(top, text="Search:").pack(side=tk.LEFT)
        self.item_search = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.item_search, width=30)
        ent.pack(side=tk.LEFT, padx=6)
        ent.bind("<KeyRelease>", lambda e: self._filter_items())
        ttk.Label(top, text="Tier:").pack(side=tk.LEFT, padx=(12, 0))
        self.item_tier = tk.StringVar(value="All")
        ttk.Combobox(
            top,
            textvariable=self.item_tier,
            values=["All", "3", "2", "1", "Starter", "Relic", "Curio", "Consumable", "God Specific"],
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=6)
        self.item_tier.trace_add("write", lambda *_: self._filter_items())

        cols = ("name", "tier", "type", "cost", "stats")
        self.item_tree = ttk.Treeview(
            self.tab_items, columns=cols, show="headings", selectmode="browse"
        )
        for c, h, w in (
            ("name", "Item", 200),
            ("tier", "Tier", 80),
            ("type", "Type", 100),
            ("cost", "Cost", 70),
            ("stats", "Stats", 280),
        ):
            self.item_tree.heading(c, text=h)
            self.item_tree.column(c, width=w)
        scroll = ttk.Scrollbar(self.tab_items, orient=tk.VERTICAL, command=self.item_tree.yview)
        self.item_tree.configure(yscrollcommand=scroll.set)
        self.item_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=(0, 8))
        scroll.pack(side=tk.LEFT, fill=tk.Y, pady=(0, 8))

        self.item_detail = tk.Text(self.tab_items, width=42, wrap=tk.WORD, font=("Segoe UI", 10))
        self.item_detail.pack(side=tk.LEFT, fill=tk.BOTH, padx=8, pady=(0, 8))
        self.item_tree.bind("<<TreeviewSelect>>", self._on_item_select)

    def load_items(self) -> None:
        self._item_rows = []
        if not self.db_path.exists():
            return
        conn = connect(self.db_path)
        rows = conn.execute(
            """
            SELECT name, tier, item_type, total_cost, cost, stats_text, passive, active, categories
            FROM items ORDER BY name
            """
        ).fetchall()
        conn.close()
        self._item_rows = [dict(r) for r in rows]
        self._filter_items()

    def _filter_items(self) -> None:
        term = (self.item_search.get() or "").lower()
        tier = self.item_tier.get()
        self.item_tree.delete(*self.item_tree.get_children())
        for it in getattr(self, "_item_rows", []):
            if tier != "All" and str(it["tier"] or "") != tier:
                # also match starter category
                if tier == "Starter" and "starter" not in (it.get("categories") or "").lower():
                    continue
                elif tier != "Starter":
                    continue
            if term and term not in it["name"].lower():
                continue
            cost = it["total_cost"] if it["total_cost"] is not None else it["cost"]
            stats = (it["stats_text"] or "").replace("\n", " · ")[:80]
            self.item_tree.insert(
                "",
                tk.END,
                iid=it["name"],
                values=(it["name"], it["tier"] or "", it["item_type"] or "", cost or "", stats),
            )

    def _on_item_select(self, _evt=None) -> None:
        sel = self.item_tree.selection()
        if not sel:
            return
        name = sel[0]
        it = next((x for x in self._item_rows if x["name"] == name), None)
        if not it:
            return
        self.item_detail.delete("1.0", tk.END)
        cost = it["total_cost"] if it["total_cost"] is not None else it["cost"]
        self.item_detail.insert(
            tk.END,
            f"{it['name']}\n{'=' * len(it['name'])}\n"
            f"Tier: {it['tier']}  Type: {it['item_type']}\n"
            f"Cost: {cost}\n\n"
            f"Stats:\n{it['stats_text'] or '—'}\n\n"
            f"Passive:\n{it['passive'] or '—'}\n\n"
            f"Active:\n{it['active'] or '—'}\n",
        )

    # ------------------------------------------------------------------ actions
    def refresh_all(self) -> None:
        self._builds_cache = None
        self.status.set(self._status_text())
        self.load_tiers()
        self.load_gods()
        self.load_builds_view()
        self.load_items()

    def _run_analysis(self) -> None:
        if not messagebox.askyesno(
            "Run analysis",
            "Recompute ability metrics, patch momentum, and tier lists?\n"
            "This may take 10–30 seconds.",
        ):
            return
        self._run_bg(
            [sys.executable, "-m", "smite2db.analyze", "run", "--db", str(self.db_path)],
            "Analysis finished.",
        )

    def _run_builds(self) -> None:
        def work():
            try:
                conn = connect(self.db_path)
                report = generate_all(conn, gods_per_role=4)
                conn.close()
                BUILDS_JSON.parent.mkdir(parents=True, exist_ok=True)
                BUILDS_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
                md_path = ROOT / "data" / "conquest_builds.md"
                from .conquest_builds import render_markdown

                md_path.write_text(render_markdown(report), encoding="utf-8")
                self.after(0, lambda: self._bg_done(True, "Conquest builds rebuilt."))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._bg_done(False, str(exc)))

        self.status.set("Building Conquest loadouts…")
        threading.Thread(target=work, daemon=True).start()

    def _run_bg(self, cmd: list[str], ok_msg: str) -> None:
        def work():
            try:
                subprocess.run(cmd, cwd=str(ROOT), check=True)
                self.after(0, lambda: self._bg_done(True, ok_msg))
            except subprocess.CalledProcessError as exc:
                self.after(0, lambda: self._bg_done(False, f"Failed: {exc}"))

        self.status.set("Working… " + " ".join(cmd[-4:]))
        threading.Thread(target=work, daemon=True).start()

    def _bg_done(self, ok: bool, msg: str) -> None:
        if ok:
            messagebox.showinfo("Done", msg)
            self.refresh_all()
        else:
            messagebox.showerror("Error", msg)
            self.status.set(self._status_text())

    def _about(self) -> None:
        messagebox.showinfo(
            "About",
            "SMITE 2 Database GUI\n\n"
            "Local data from wiki.smite2.com\n"
            "Tier lists = patch momentum + kit + build metrics\n"
            "Conquest builds = 1 starter + 6 items (statistical)\n\n"
            f"DB: {self.db_path}",
        )


def _fmt(v) -> str:
    if v is None:
        return "—"
    try:
        return f"{float(v):.1f}"
    except (TypeError, ValueError):
        return str(v)


def _safe_json(s: str | None):
    if not s:
        return []
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return []


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="SMITE 2 Database GUI")
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = p.parse_args(argv)
    app = Smite2App(db_path=args.db)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
