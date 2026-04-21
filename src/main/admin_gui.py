"""Launch the DCMS admin dashboard (see package ``dcms_admin``)."""

import tkinter as tk

from dcms_admin import AdminGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
