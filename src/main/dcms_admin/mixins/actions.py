import csv
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from ..constants import C, FONTS, SERVER
from ..controllers import announcements as ann_ctl
from ..controllers import broadcast as bc_ctl
from ..controllers import contest as contest_ctl
from ..controllers import problems as prob_ctl
from ..controllers import refresh as refresh_ctl
from ..controllers import submissions as sub_ctl
from ..services.api import AdminApi


class ActionsMixin:
    def _api(self) -> AdminApi:
        api = getattr(self, "_api_client", None)
        if api is None:
            api = AdminApi(base_url=SERVER)
            self._api_client = api
        return api

    # -------------------- Contest controls --------------------
    def _start_contest(self):
        try:
            minutes = int(self._dur_var.get().strip() or "0")
        except ValueError:
            messagebox.showerror("Invalid duration", "Please enter contest duration in minutes.")
            return
        if minutes <= 0:
            messagebox.showerror("Invalid duration", "Duration must be > 0 minutes.")
            return

        if not messagebox.askyesno("Start contest", f"Start contest for {minutes} minutes?"):
            return
        try:
            contest_ctl.start_contest(self._api(), minutes)
        except Exception as e:
            messagebox.showerror("Start failed", str(e))
            return
        self._update_all()

    def _end_contest(self):
        if not messagebox.askyesno("End contest", "End the contest now?"):
            return
        try:
            contest_ctl.end_contest(self._api())
        except Exception as e:
            messagebox.showerror("End failed", str(e))
            return
        self._update_all()

    # -------------------- Broadcast --------------------
    def _send_problem(self):
        pid = (self._prob_var.get() or "").strip()
        if not pid:
            return
        try:
            bc_ctl.send_problem(self._api(), pid)
        except Exception as e:
            messagebox.showerror("Broadcast failed", str(e))
            return
        self._set_status(f"Sent {pid}", "ok")

    def _send_all_problems(self):
        try:
            sent = bc_ctl.send_all_problems(self._api())
        except Exception as e:
            messagebox.showerror("Failed", str(e))
            return
        self._set_status(f"Broadcasted {sent} problems", "ok")

    # -------------------- Refreshers --------------------
    def _refresh_contest_state(self) -> bool:
        try:
            data = refresh_ctl.contest_state(self._api())
            self._contest_active = bool(data.get("active"))
            self._online_count = int(data.get("connected_clients", 0) or 0)
            self._sb_online.configure(text=str(self._online_count))
            return True
        except Exception:
            return False

    def _refresh_participants(self) -> bool:
        try:
            rows, total, online_count = refresh_ctl.participants(self._api())
            self._part_tree.set_rows(rows)
            self._part_count_lbl.configure(text=f"{total} total • {online_count} online")
            self._sb_online.configure(text=str(online_count))
            return True
        except Exception:
            return False

    def _refresh_submissions(self) -> bool:
        try:
            subs, rows = refresh_ctl.submissions(self._api(), limit=100)
            self._submission_count = len(subs)
            self._sb_subs.configure(text=str(self._submission_count))
            self._sub_count_lbl.configure(text=f"{self._submission_count} submissions")
            self._sub_data = subs
            self._sub_tree.set_rows(rows)
            return True
        except Exception:
            return False

    def _refresh_problems(self) -> bool:
        try:
            problems, rows = refresh_ctl.problems(self._api())
            self._problem_count = len(problems)
            self._sb_problems.configure(text=str(self._problem_count))

            # cache raw list for view/delete
            self._problems_cache = problems
            self._prob_tree.set_rows(rows)
            return True
        except Exception:
            return False

    def _refresh_scoreboard(self) -> bool:
        try:
            sb, rows, derived = refresh_ctl.scoreboard(self._api())
            self._sc_rank1.update(derived["first_user"])
            self._sc_pcount.update(str(derived["participants"]))
            self._sc_solved.update(str(derived["accepted_total"]))
            self._sc_penalty.update(str(derived["avg_penalty"]))
            self._sb_tree.set_rows(rows)
            return True
        except Exception:
            return False

    def _refresh_announcements(self) -> bool:
        try:
            rows = refresh_ctl.announcements(self._api())
            self._ann_tree.set_rows(rows)
            return True
        except Exception:
            return False

    # -------------------- Scoreboard actions --------------------
    def _export_scoreboard(self):
        try:
            sb = refresh_ctl.scoreboard(self._api())[0]
        except Exception as e:
            messagebox.showerror("Export failed", str(e))
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["rank", "user_id", "problems_solved", "penalty"])
            for e in sb:
                w.writerow([e.get("rank"), e.get("user_id"), e.get("problems_solved"), e.get("penalty")])
        messagebox.showinfo("Exported", f"Saved to:\n{path}")

    # -------------------- Submissions actions --------------------
    def _view_submission_detail(self):
        sel = self._sub_tree.selected_values()
        if not sel:
            messagebox.showinfo("Select a row", "Select a submission row first.")
            return
        ts, user, prob, lang, verdict, score = sel
        rec = sub_ctl.find_submission_record(self._sub_data, ts, user, prob)
        if not rec:
            rec = {"timestamp": ts, "user_id": user, "problem_id": prob, "language": lang, "verdict": verdict}

        win = tk.Toplevel(self.root)
        win.title("Submission Detail")
        win.configure(bg=C["bg"])
        txt = scrolledtext.ScrolledText(win, width=110, height=28, bg=C["surface"], fg=C["text"], insertbackground=C["text"])
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        txt.insert("1.0", "\n".join(f"{k}: {v}" for k, v in rec.items()))
        txt.configure(state="disabled")

    # -------------------- Problems actions --------------------
    def _get_selected_problem_id(self):
        sel = self._prob_tree.selected_values()
        if not sel:
            return None
        pid = sel[0]
        return str(pid).strip()

    def _view_problem_detail(self):
        pid = self._get_selected_problem_id()
        if not pid:
            messagebox.showinfo("Select a problem", "Select a problem first.")
            return
        try:
            problem = prob_ctl.get_problem(self._api(), pid)
        except Exception as e:
            messagebox.showerror("Failed", str(e))
            return

        win = tk.Toplevel(self.root)
        win.title(f"Problem {pid}")
        win.configure(bg=C["bg"])
        txt = scrolledtext.ScrolledText(win, width=120, height=34, bg=C["surface"], fg=C["text"], insertbackground=C["text"])
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        statement = problem.get("statement", "")
        info = (
            f"ID: {problem.get('problem_id')}\n"
            f"Title: {problem.get('title')}\n"
            f"Difficulty: {problem.get('difficulty')}\n"
            f"Points: {problem.get('points')}\n"
            f"Time limit: {problem.get('time_limit')}s\n"
            f"Memory: {problem.get('memory_limit')}MB\n"
            f"Tests: {len(problem.get('test_cases', []))}\n\n"
        )
        txt.insert("1.0", info + statement)
        txt.configure(state="disabled")

    def _delete_problem(self):
        pid = self._get_selected_problem_id()
        if not pid:
            messagebox.showinfo("Select a problem", "Select a problem first.")
            return
        if not messagebox.askyesno("Delete problem", f"Delete problem {pid}?"):
            return
        try:
            prob_ctl.delete_problem(self._api(), pid)
        except Exception as e:
            messagebox.showerror("Delete failed", str(e))
            return
        self._update_all()

    def _add_problem_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Problem")
        win.configure(bg=C["bg"])

        frm = tk.Frame(win, bg=C["bg"])
        frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        def row(label, default=""):
            r = tk.Frame(frm, bg=C["bg"])
            r.pack(fill=tk.X, pady=4)
            tk.Label(r, text=label, font=FONTS["small"], bg=C["bg"], fg=C["text2"], width=14, anchor="w").pack(side=tk.LEFT)
            v = tk.StringVar(value=default)
            e = tk.Entry(r, textvariable=v, bg=C["surface"], fg=C["text"], insertbackground=C["text"], relief=tk.FLAT)
            e.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
            return v

        pid_v = row("ID", "A")
        title_v = row("Title", "Untitled")
        diff_v = row("Difficulty", "easy")
        points_v = row("Points", "100")
        tl_v = row("Time limit", "2.0")

        tk.Label(frm, text="Statement", font=FONTS["small"], bg=C["bg"], fg=C["text2"]).pack(anchor="w", pady=(10, 4))
        stmt = scrolledtext.ScrolledText(frm, height=10, bg=C["surface"], fg=C["text"], insertbackground=C["text"], relief=tk.FLAT)
        stmt.pack(fill=tk.BOTH, expand=True)

        btns = tk.Frame(frm, bg=C["bg"])
        btns.pack(fill=tk.X, pady=(10, 0))

        def submit():
            try:
                payload = {
                    "problem_id": pid_v.get().strip(),
                    "title": title_v.get().strip(),
                    "statement": stmt.get("1.0", "end").strip(),
                    "difficulty": diff_v.get().strip(),
                    "points": int(points_v.get().strip() or "0"),
                    "time_limit": float(tl_v.get().strip() or "2.0"),
                }
                prob_ctl.create_problem(self._api(), payload)
            except Exception as e:
                messagebox.showerror("Create failed", str(e))
                return
            win.destroy()
            self._update_all()

        tk.Button(btns, text="Create", command=submit, bg=C["accent"], fg="white", relief=tk.FLAT).pack(side=tk.RIGHT)
        tk.Button(btns, text="Cancel", command=win.destroy, bg=C["elevated"], fg=C["text"], relief=tk.FLAT).pack(
            side=tk.RIGHT, padx=8
        )

    # -------------------- Announcements actions --------------------
    def _send_quick_announcement(self):
        msg = (self._ann_var.get() or "").strip()
        if not msg:
            return
        prio_key = self._ann_prio_var.get()
        prio = self._prio_map.get(prio_key, "normal")
        payload = {"title": "📢 Announcement", "content": msg, "priority": prio}
        try:
            ann_ctl.create_announcement(self._api(), payload)
        except Exception as e:
            messagebox.showerror("Send failed", str(e))
            return
        self._ann_var.set("")
        self._update_all()

    def _delete_announcement(self):
        sel = self._ann_tree.selected_values()
        if not sel:
            messagebox.showinfo("Select an announcement", "Select an announcement first.")
            return
        ann_id = sel[0]
        if not messagebox.askyesno("Delete announcement", f"Delete announcement {ann_id}?"):
            return
        try:
            ann_ctl.delete_announcement(self._api(), ann_id)
        except Exception as e:
            messagebox.showerror("Delete failed", str(e))
            return
        self._update_all()
