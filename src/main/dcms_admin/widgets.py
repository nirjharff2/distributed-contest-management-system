"""Admin custom widgets."""
import tkinter as tk
from tkinter import ttk

from .constants import C, FONTS

# ══════════════════════════════════════════════════════════════════════════════
#  Custom Widgets
# ══════════════════════════════════════════════════════════════════════════════

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, color=None, hover=None,
                 w=120, h=34, icon="", parent_bg=None, **kw):
        bg = parent_bg or C["bg"]
        super().__init__(
            parent, width=w, height=h,
            highlightthickness=0, bg=bg, cursor="hand2"
        )
        self.command = command
        self.color   = color or C["accent"]
        self.hover   = hover or C["accent2"]
        self.text    = f"{icon} {text}".strip() if icon else text
        self.w, self.h = w, h
        self.active  = True
        self._draw(self.color)
        self.bind("<Enter>", lambda e: self._draw(self.hover) if self.active else None)
        self.bind("<Leave>", lambda e: self._draw(self.color) if self.active else None)
        self.bind("<Button-1>", lambda e: self._click())

    def _draw(self, color):
        self.delete("all")
        r = 7
        corners = [
            (0, 0, r*2, r*2),
            (self.w - r*2, 0, self.w, r*2),
            (0, self.h - r*2, r*2, self.h),
            (self.w - r*2, self.h - r*2, self.w, self.h),
        ]
        for x1, y1, x2, y2 in corners:
            self.create_oval(x1, y1, x2, y2, fill=color, outline="")
        self.create_rectangle(r, 0, self.w - r, self.h, fill=color, outline="")
        self.create_rectangle(0, r, self.w, self.h - r, fill=color, outline="")
        self.create_text(
            self.w // 2, self.h // 2, text=self.text,
            fill="white", font=FONTS["body"]
        )

    def _click(self):
        if self.active and self.command:
            self.command()

    def disable(self):
        self.active = False
        self._draw("#3a3a5a")

    def enable(self):
        self.active = True
        self._draw(self.color)


class SidebarItem(tk.Frame):
    def __init__(self, parent, icon, label, command, **kw):
        super().__init__(parent, bg=C["sidebar"], cursor="hand2")
        self.command  = command
        self.selected = False

        self.indicator = tk.Frame(self, bg=C["sidebar"], width=4)
        self.indicator.pack(side=tk.LEFT, fill=tk.Y)

        inner = tk.Frame(self, bg=C["sidebar"])
        inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.icon_lbl = tk.Label(
            inner, text=icon, font=("Segoe UI Emoji", 14),
            bg=C["sidebar"], fg=C["text2"]
        )
        self.icon_lbl.pack(side=tk.LEFT)

        self.text_lbl = tk.Label(
            inner, text=label, font=FONTS["body"],
            bg=C["sidebar"], fg=C["text2"]
        )
        self.text_lbl.pack(side=tk.LEFT, padx=8)

        self.badge = tk.Label(
            inner, text="", font=FONTS["small"],
            bg=C["accent"], fg="white", padx=5, pady=1
        )

        for w in (self, inner, self.icon_lbl, self.text_lbl):
            w.bind("<Button-1>", lambda e: self._click())
            w.bind("<Enter>",    lambda e: self._hover(True))
            w.bind("<Leave>",    lambda e: self._hover(False))

    def _click(self):
        if self.command:
            self.command()

    def _hover(self, on):
        if not self.selected:
            col = C["card"] if on else C["sidebar"]
            for w in (self, self.winfo_children()[1]):
                w.configure(bg=col)
            self.icon_lbl.configure(bg=col)
            self.text_lbl.configure(bg=col)

    def select(self):
        self.selected = True
        self.indicator.configure(bg=C["accent"])
        for w in (self, self.winfo_children()[1]):
            w.configure(bg=C["elevated"])
        self.icon_lbl.configure(bg=C["elevated"], fg=C["text"])
        self.text_lbl.configure(bg=C["elevated"], fg=C["text"])

    def deselect(self):
        self.selected = False
        self.indicator.configure(bg=C["sidebar"])
        for w in (self, self.winfo_children()[1]):
            w.configure(bg=C["sidebar"])
        self.icon_lbl.configure(bg=C["sidebar"], fg=C["text2"])
        self.text_lbl.configure(bg=C["sidebar"], fg=C["text2"])

    def set_badge(self, value):
        if value:
            self.badge.configure(text=str(value))
            self.badge.pack(side=tk.RIGHT)
        else:
            self.badge.pack_forget()


class StatCard(tk.Frame):
    def __init__(self, parent, icon, label, value="0", color=None):
        super().__init__(parent, bg=C["card"], padx=16, pady=12)
        self._color = color or C["accent"]

        tk.Label(
            self, text=icon, font=("Segoe UI Emoji", 18),
            bg=C["card"], fg=self._color
        ).pack(anchor=tk.W)
        self.value_lbl = tk.Label(
            self, text=str(value), font=("Trebuchet MS", 22, "bold"),
            bg=C["card"], fg=C["text"]
        )
        self.value_lbl.pack(anchor=tk.W)
        tk.Label(
            self, text=label, font=FONTS["small"],
            bg=C["card"], fg=C["text2"]
        ).pack(anchor=tk.W)

    def update(self, value, color=None):
        self.value_lbl.configure(text=str(value))
        if color:
            self.value_lbl.configure(fg=color)


class SearchableTree(tk.Frame):
    """Treeview with integrated search bar and sortable columns."""
    def __init__(self, parent, columns, widths, anchors=None, **kw):
        super().__init__(parent, bg=C["bg"])
        self.columns = columns
        self._sort_col = None
        self._sort_rev = False

        # Search bar
        search_row = tk.Frame(self, bg=C["bg"])
        search_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            search_row, text="🔍", font=("Segoe UI Emoji", 11),
            bg=C["bg"], fg=C["text2"]
        ).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._filter)
        tk.Entry(
            search_row, textvariable=self.search_var, font=FONTS["body"],
            bg=C["elevated"], fg=C["text"], insertbackground=C["text"],
            relief=tk.FLAT, bd=0
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=6)
        tk.Button(
            search_row, text="✕", font=FONTS["small"],
            bg=C["elevated"], fg=C["text2"], relief=tk.FLAT, bd=0,
            command=lambda: self.search_var.set("")
        ).pack(side=tk.LEFT)

        # Treeview
        tree_frame = tk.Frame(self, bg=C["bg"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure(
            "ST.Treeview",
            background=C["surface"], foreground=C["text"],
            fieldbackground=C["surface"], rowheight=28,
            borderwidth=0, font=FONTS["body"]
        )
        style.configure(
            "ST.Treeview.Heading",
            background=C["elevated"], foreground=C["text"],
            borderwidth=0, font=FONTS["h2"]
        )
        style.map(
            "ST.Treeview",
            background=[("selected", C["accent"])],
            foreground=[("selected", C["white"])]
        )

        self.tree = ttk.Treeview(
            tree_frame, columns=columns,
            show="headings", style="ST.Treeview"
        )
        anchors = anchors or ["center"] * len(columns)
        for col, w, anc in zip(columns, widths, anchors):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, anchor=anc)

        sb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._all_rows = []

    def _sort(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        col_idx = self.columns.index(col)
        self._all_rows.sort(key=lambda r: r[col_idx], reverse=self._sort_rev)
        self._refresh_display()

    def _filter(self, *_):
        self._refresh_display()

    def _refresh_display(self):
        q = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for row in self._all_rows:
            if not q or any(q in str(v).lower() for v in row):
                self.tree.insert("", "end", values=row)

    def set_rows(self, rows):
        self._all_rows = list(rows)
        if self._sort_col:
            idx = self.columns.index(self._sort_col)
            self._all_rows.sort(key=lambda r: r[idx], reverse=self._sort_rev)
        self._refresh_display()

    def clear(self):
        self._all_rows = []
        self.tree.delete(*self.tree.get_children())

    def selected_values(self):
        sel = self.tree.selection()
        if sel:
            return self.tree.item(sel[0])["values"]
        return None


