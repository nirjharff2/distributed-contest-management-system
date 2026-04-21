import time
from datetime import datetime

from ..constants import C


class UpdateMixin:
    def _clock_tick(self):
        try:
            self._clock_lbl.configure(text=f"⏱ {datetime.now().strftime('%H:%M:%S')}")
        except Exception:
            return
        self.root.after(1000, self._clock_tick)

    def _set_status(self, text: str, kind: str = "idle"):
        color = {
            "idle": C["text3"],
            "ok": C["green"],
            "warn": C["amber"],
            "err": C["red"],
            "work": C["accent"],
        }.get(kind, C["text3"])
        try:
            self._status_lbl.configure(text=text)
            self._status_dot.configure(fg=color)
        except Exception:
            pass

    def _update_loop(self):
        while getattr(self, "_running", False):
            try:
                self.root.after(0, self._update_all)
            except Exception:
                break
            time.sleep(2.5)

    def _update_all(self):
        self._set_status("Syncing…", "work")
        ok = True
        ok = self._refresh_contest_state() and ok
        ok = self._refresh_participants() and ok
        ok = self._refresh_problems() and ok
        ok = self._refresh_submissions() and ok
        ok = self._refresh_scoreboard() and ok
        ok = self._refresh_announcements() and ok

        if ok:
            self._conn_lbl.configure(text="● Connected", fg=C["green"])
            self._set_status("Up to date", "ok")
        else:
            self._conn_lbl.configure(text="● Error", fg=C["red"])
            self._set_status("Some requests failed", "warn")

        self._update_lbl.configure(text=f"Updated: {datetime.now().strftime('%H:%M')}")
