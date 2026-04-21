"""DCMS Admin Dashboard (modular).

`AdminGUI` is composed from mixins in `dcms_admin/mixins/`.
"""

import threading

from .constants import C
from .mixins.actions import ActionsMixin
from .mixins.layout import LayoutMixin
from .mixins.navigation import NavigationMixin
from .mixins.pages import PagesMixin
from .mixins.update import UpdateMixin


class AdminGUI(LayoutMixin, PagesMixin, NavigationMixin, ActionsMixin, UpdateMixin):
    def __init__(self, root):
        self.root = root
        self.root.title("DCMS Admin  ⚡  v3.1")
        self.root.geometry("1280x800")
        self.root.configure(bg=C["bg"])
        self.root.minsize(1100, 700)

        self._running = True
        self._online_count = 0
        self._problem_count = 0
        self._submission_count = 0
        self._contest_active = False
        self._pages = {}
        self._sidebar_items = {}
        self._active_page = None

        self._problems_cache = []

        self._setup_global_styles()
        self._build_layout()
        self._show_page("scoreboard")

        threading.Thread(target=self._update_loop, daemon=True).start()

        self.root.bind("<Control-r>", lambda e: self._update_all())
        self.root.bind("<Control-s>", lambda e: self._start_contest())
        self.root.bind("<Control-e>", lambda e: self._end_contest())

    def on_close(self):
        self._running = False
        self.root.destroy()
