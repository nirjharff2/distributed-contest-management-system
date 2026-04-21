import tkinter as tk
from tkinter import ttk

from ..constants import C, FONTS
from ..widgets import RoundedButton, SearchableTree, StatCard


class PagesMixin:
    def _page_frame(self):
        return tk.Frame(self.content_area, bg=C["bg"])

    def _page_header(self, parent, icon, title, subtitle=""):
        hdr = tk.Frame(parent, bg=C["bg"])
        hdr.pack(fill=tk.X, pady=(14, 10))
        tk.Label(
            hdr,
            text=f"{icon}  {title}",
            font=("Trebuchet MS", 16, "bold"),
            bg=C["bg"],
            fg=C["text"],
        ).pack(side=tk.LEFT)
        if subtitle:
            tk.Label(hdr, text=subtitle, font=FONTS["small"], bg=C["bg"], fg=C["text2"]).pack(side=tk.LEFT, padx=10)
        return hdr

    def _build_scoreboard_page(self):
        f = self._page_frame()

        hdr = self._page_header(f, "🏆", "Live Scoreboard")
        RoundedButton(
            hdr,
            "Export CSV",
            self._export_scoreboard,
            color=C["elevated"],
            hover=C["border"],
            w=110,
            h=28,
            parent_bg=C["bg"],
        ).pack(side=tk.RIGHT)
        RoundedButton(
            hdr,
            "🔄 Refresh",
            self._update_all,
            color=C["elevated"],
            hover=C["border"],
            w=100,
            h=28,
            parent_bg=C["bg"],
        ).pack(side=tk.RIGHT, padx=8)

        cards = tk.Frame(f, bg=C["bg"])
        cards.pack(fill=tk.X, pady=(0, 12))
        self._sc_rank1 = StatCard(cards, "🥇", "First Place", "—", C["amber"])
        self._sc_solved = StatCard(cards, "✅", "Accepted", "0", C["green"])
        self._sc_pcount = StatCard(cards, "👥", "Participants", "0", C["blue"])
        self._sc_penalty = StatCard(cards, "⏱", "Avg Penalty", "0", C["accent"])
        for card in (self._sc_rank1, self._sc_solved, self._sc_pcount, self._sc_penalty):
            card.pack(side=tk.LEFT, padx=(0, 10), pady=4, ipadx=4)

        self._sb_tree = SearchableTree(
            f,
            columns=("Rank", "User", "Solved", "Penalty", "Problems"),
            widths=[70, 200, 80, 100, 400],
            anchors=["center", "w", "center", "center", "w"],
        )
        self._sb_tree.pack(fill=tk.BOTH, expand=True)
        return f

    def _build_participants_page(self):
        f = self._page_frame()
        hdr = self._page_header(f, "👥", "Participants")
        self._part_count_lbl = tk.Label(hdr, text="", font=FONTS["small"], bg=C["bg"], fg=C["text2"])
        self._part_count_lbl.pack(side=tk.LEFT, padx=10)

        self._part_tree = SearchableTree(
            f,
            columns=("Status", "User ID", "Registered"),
            widths=[100, 280, 220],
            anchors=["center", "w", "center"],
        )
        self._part_tree.pack(fill=tk.BOTH, expand=True)
        return f

    def _build_submissions_page(self):
        f = self._page_frame()
        hdr = self._page_header(f, "📝", "Submissions")
        self._sub_count_lbl = tk.Label(hdr, text="", font=FONTS["small"], bg=C["bg"], fg=C["text2"])
        self._sub_count_lbl.pack(side=tk.LEFT, padx=10)
        RoundedButton(
            hdr,
            "👁 View Detail",
            self._view_submission_detail,
            color=C["elevated"],
            hover=C["border"],
            w=120,
            h=28,
            parent_bg=C["bg"],
        ).pack(side=tk.RIGHT)

        self._sub_tree = SearchableTree(
            f,
            columns=("Time", "User", "Problem", "Language", "Verdict", "Score"),
            widths=[160, 130, 80, 90, 130, 80],
            anchors=["center", "w", "center", "center", "center", "center"],
        )
        self._sub_tree.pack(fill=tk.BOTH, expand=True)
        self._sub_data = []
        return f

    def _build_problems_page(self):
        f = self._page_frame()
        hdr = self._page_header(f, "📚", "Problem Set")
        RoundedButton(
            hdr,
            "➕ Add Problem",
            self._add_problem_dialog,
            color=C["green"],
            hover="#34d399",
            w=130,
            h=28,
            parent_bg=C["bg"],
        ).pack(side=tk.RIGHT)
        RoundedButton(
            hdr,
            "🗑 Delete",
            self._delete_problem,
            color=C["red"],
            hover="#f87171",
            w=90,
            h=28,
            parent_bg=C["bg"],
        ).pack(side=tk.RIGHT, padx=8)
        RoundedButton(
            hdr,
            "👁 View",
            self._view_problem_detail,
            color=C["accent"],
            hover=C["accent2"],
            w=90,
            h=28,
            parent_bg=C["bg"],
        ).pack(side=tk.RIGHT, padx=8)

        self._prob_tree = SearchableTree(
            f,
            columns=("ID", "Title", "Difficulty", "Points", "Time Limit", "Tests"),
            widths=[60, 300, 110, 80, 100, 70],
            anchors=["center", "w", "center", "center", "center", "center"],
        )
        self._prob_tree.pack(fill=tk.BOTH, expand=True)
        self._prob_tree.tree.bind("<Double-1>", lambda e: self._view_problem_detail())
        return f

    def _build_announcements_page(self):
        f = self._page_frame()
        self._page_header(f, "📢", "Announcements")

        compose = tk.Frame(f, bg=C["card"], pady=10)
        compose.pack(fill=tk.X, pady=(0, 10))
        inner = tk.Frame(compose, bg=C["card"])
        inner.pack(fill=tk.X, padx=14)

        tk.Label(inner, text="Priority:", font=FONTS["small"], bg=C["card"], fg=C["text2"]).pack(side=tk.LEFT)
        self._ann_prio_var = tk.StringVar(value="normal")
        self._prio_map = {"🔴 High": "high", "🟡 Normal": "normal", "⚪ Low": "low"}
        prio_cb = ttk.Combobox(
            inner,
            textvariable=self._ann_prio_var,
            values=list(self._prio_map.keys()),
            width=12,
            state="readonly",
            font=FONTS["small"],
        )
        prio_cb.set("🟡 Normal")
        prio_cb.pack(side=tk.LEFT, padx=(4, 12))

        tk.Label(inner, text="Message:", font=FONTS["small"], bg=C["card"], fg=C["text2"]).pack(side=tk.LEFT)
        self._ann_var = tk.StringVar()
        self._ann_entry = tk.Entry(
            inner,
            textvariable=self._ann_var,
            font=FONTS["body"],
            bg=C["elevated"],
            fg=C["text"],
            insertbackground=C["text"],
            relief=tk.FLAT,
            width=46,
        )
        self._ann_entry.pack(side=tk.LEFT, padx=8, ipady=4)
        self._ann_entry.bind("<Return>", lambda e: self._send_quick_announcement())

        RoundedButton(
            inner,
            "📤 Send",
            self._send_quick_announcement,
            color=C["accent"],
            hover=C["accent2"],
            w=85,
            h=28,
            parent_bg=C["card"],
        ).pack(side=tk.LEFT)
        RoundedButton(
            inner,
            "🗑 Delete",
            self._delete_announcement,
            color=C["red"],
            hover="#f87171",
            w=90,
            h=28,
            parent_bg=C["card"],
        ).pack(side=tk.LEFT, padx=8)

        self._ann_tree = SearchableTree(
            f,
            columns=("ID", "Priority", "Title", "Content", "Time"),
            widths=[50, 90, 200, 320, 160],
            anchors=["center", "center", "w", "w", "center"],
        )
        self._ann_tree.pack(fill=tk.BOTH, expand=True)
        return f
