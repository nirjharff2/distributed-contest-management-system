"""
DCMS Client v2.1

This file intentionally stays small: it defines the `ClientGUI` class and
assembles behavior via mixins. The actual logic is split into `dcms_client/mixins/`.
"""

import tkinter as tk
from tkinter import font
from typing import Dict, List, Optional

from .constants import COLORS
from .mixins.execution import ExecutionMixin
from .mixins.login import LoginMixin
from .mixins.messages import MessagesMixin
from .mixins.styles import StylesMixin
from .mixins.toast import ToastMixin
from .mixins.ui import UiMixin
from .mixins.websocket import WebSocketMixin


class ClientGUI(
    StylesMixin,
    ToastMixin,
    LoginMixin,
    WebSocketMixin,
    UiMixin,
    MessagesMixin,
    ExecutionMixin,
):
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ DCMS Contest Client")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS["bg_dark"])

        self.title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.code_font = font.Font(family="Consolas", size=11)
        self.normal_font = font.Font(family="Segoe UI", size=10)
        self.small_font = font.Font(family="Segoe UI", size=9)

        self.user_id: Optional[str] = None
        self.ws = None
        self.ws_loop = None
        self.ws_thread = None
        self.connected = False
        self.reconnecting = False
        self.contest_active = False
        self.contest_end_time: Optional[str] = None
        self.current_problem: Optional[str] = None
        self.problems: Dict[str, dict] = {}
        self.submissions: List[dict] = []
        self.announcements: List[dict] = []
        self.scoreboard: List[dict] = []
        self.last_language = "Python"

        self.setup_styles()
        self.create_login_screen()

    def on_closing(self):
        self.connected = False
        try:
            if self.ws_loop and self.ws_loop.is_running():
                self.ws_loop.call_soon_threadsafe(self.ws_loop.stop)
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()