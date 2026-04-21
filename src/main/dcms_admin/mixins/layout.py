import tkinter as tk
from tkinter import ttk

from ..constants import C, FONTS
from ..widgets import RoundedButton, SidebarItem


class LayoutMixin:
    def _setup_global_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure(
            "TScrollbar",
            background=C["elevated"],
            troughcolor=C["surface"],
            borderwidth=0,
            arrowsize=12,
        )

    def _stat_row(self, parent, icon, label, value):
        row = tk.Frame(parent, bg=C["sidebar"])
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=icon, font=("Segoe UI Emoji", 10), bg=C["sidebar"]).pack(side=tk.LEFT)
        tk.Label(row, text=label, font=FONTS["small"], bg=C["sidebar"], fg=C["text2"]).pack(side=tk.LEFT, padx=6)
        lbl = tk.Label(row, text=value, font=("Trebuchet MS", 10, "bold"), bg=C["sidebar"], fg=C["text"])
        lbl.pack(side=tk.RIGHT)
        return lbl

    def _build_topbar(self, parent):
        bar = tk.Frame(parent, bg=C["surface"], height=68)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        inner = tk.Frame(bar, bg=C["surface"])
        inner.pack(fill=tk.BOTH, expand=True, padx=20)

        left = tk.Frame(inner, bg=C["surface"])
        left.pack(side=tk.LEFT, fill=tk.Y)

        ctrl_row = tk.Frame(left, bg=C["surface"])
        ctrl_row.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        tk.Label(ctrl_row, text="Duration:", font=FONTS["small"], bg=C["surface"], fg=C["text2"]).pack(side=tk.LEFT)
        self._dur_var = tk.StringVar(value="120")
        tk.Entry(
            ctrl_row,
            textvariable=self._dur_var,
            width=5,
            font=FONTS["body"],
            bg=C["elevated"],
            fg=C["text"],
            insertbackground=C["text"],
            relief=tk.FLAT,
            justify=tk.CENTER,
        ).pack(side=tk.LEFT, padx=(4, 2), ipady=3)
        tk.Label(ctrl_row, text="min", font=FONTS["small"], bg=C["surface"], fg=C["text2"]).pack(side=tk.LEFT)

        RoundedButton(
            ctrl_row,
            "▶ Start",
            self._start_contest,
            color=C["green"],
            hover="#34d399",
            w=90,
            h=30,
            parent_bg=C["surface"],
        ).pack(side=tk.LEFT, padx=(12, 4), pady=8)
        RoundedButton(
            ctrl_row,
            "⏹ End",
            self._end_contest,
            color=C["red"],
            hover="#f87171",
            w=80,
            h=30,
            parent_bg=C["surface"],
        ).pack(side=tk.LEFT, padx=4, pady=8)

        tk.Frame(inner, bg=C["border"], width=1).pack(side=tk.LEFT, fill=tk.Y, padx=16, pady=8)

        bc = tk.Frame(inner, bg=C["surface"])
        bc.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(bc, text="Broadcast:", font=FONTS["small"], bg=C["surface"], fg=C["text2"]).pack(side=tk.LEFT)
        self._prob_var = tk.StringVar(value="A")
        tk.Entry(
            bc,
            textvariable=self._prob_var,
            width=5,
            font=FONTS["body"],
            bg=C["elevated"],
            fg=C["text"],
            insertbackground=C["text"],
            relief=tk.FLAT,
            justify=tk.CENTER,
        ).pack(side=tk.LEFT, padx=4, ipady=3)
        RoundedButton(
            bc,
            "Send",
            self._send_problem,
            color=C["blue"],
            hover="#60a5fa",
            w=70,
            h=30,
            parent_bg=C["surface"],
        ).pack(side=tk.LEFT, padx=4, pady=8)
        RoundedButton(
            bc,
            "All",
            self._send_all_problems,
            color=C["blue"],
            hover="#60a5fa",
            w=55,
            h=30,
            parent_bg=C["surface"],
        ).pack(side=tk.LEFT, padx=4, pady=8)

        right = tk.Frame(inner, bg=C["surface"])
        right.pack(side=tk.RIGHT, fill=tk.Y)

        self._status_dot = tk.Label(right, text="●", font=("Trebuchet MS", 18), bg=C["surface"], fg=C["text3"])
        self._status_dot.pack(side=tk.LEFT)
        self._status_lbl = tk.Label(
            right,
            text="Idle",
            font=("Trebuchet MS", 12, "bold"),
            bg=C["surface"],
            fg=C["text2"],
        )
        self._status_lbl.pack(side=tk.LEFT, padx=(4, 16))

        self._clock_lbl = tk.Label(
            right,
            text="⏱ --:--",
            font=("Courier New", 14, "bold"),
            bg=C["surface"],
            fg=C["amber"],
        )
        self._clock_lbl.pack(side=tk.LEFT)

        self._clock_tick()

    def _build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=C["sidebar"], width=210)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        logo = tk.Frame(self.sidebar, bg=C["sidebar"], pady=20)
        logo.pack(fill=tk.X)
        tk.Label(logo, text="⚡", font=("Segoe UI Emoji", 28), bg=C["sidebar"], fg=C["accent"]).pack()
        tk.Label(logo, text="DCMS", font=("Trebuchet MS", 18, "bold"), bg=C["sidebar"], fg=C["text"]).pack()
        tk.Label(logo, text="Admin Console", font=FONTS["small"], bg=C["sidebar"], fg=C["text3"]).pack()

        tk.Frame(self.sidebar, bg=C["border"], height=1).pack(fill=tk.X, pady=10)

        nav_items = [
            ("scoreboard", "🏆", "Scoreboard"),
            ("participants", "👥", "Participants"),
            ("submissions", "📝", "Submissions"),
            ("problems", "📚", "Problems"),
            ("announcements", "📢", "Announcements"),
        ]
        for key, icon, label in nav_items:
            item = SidebarItem(self.sidebar, icon, label, command=lambda k=key: self._show_page(k))
            item.pack(fill=tk.X)
            self._sidebar_items[key] = item

        tk.Frame(self.sidebar, bg=C["border"], height=1).pack(fill=tk.X, pady=10)

        stats_frame = tk.Frame(self.sidebar, bg=C["sidebar"], padx=16)
        stats_frame.pack(fill=tk.X)
        tk.Label(
            stats_frame,
            text="QUICK STATS",
            font=("Trebuchet MS", 8, "bold"),
            bg=C["sidebar"],
            fg=C["text3"],
        ).pack(anchor=tk.W, pady=(0, 6))

        self._sb_online = self._stat_row(stats_frame, "🟢", "Online", "0")
        self._sb_problems = self._stat_row(stats_frame, "📚", "Problems", "0")
        self._sb_subs = self._stat_row(stats_frame, "📝", "Submissions", "0")

        footer = tk.Frame(self.sidebar, bg=C["sidebar"])
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=12)
        self._conn_lbl = tk.Label(footer, text="● Connected", font=FONTS["small"], bg=C["sidebar"], fg=C["green"])
        self._conn_lbl.pack(anchor=tk.W)
        self._update_lbl = tk.Label(footer, text="Updated: --:--", font=FONTS["small"], bg=C["sidebar"], fg=C["text3"])
        self._update_lbl.pack(anchor=tk.W)

        main = tk.Frame(self.root, bg=C["bg"])
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_topbar(main)

        self.content_area = tk.Frame(main, bg=C["bg"])
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 12))

        self._pages["scoreboard"] = self._build_scoreboard_page()
        self._pages["participants"] = self._build_participants_page()
        self._pages["submissions"] = self._build_submissions_page()
        self._pages["problems"] = self._build_problems_page()
        self._pages["announcements"] = self._build_announcements_page()
