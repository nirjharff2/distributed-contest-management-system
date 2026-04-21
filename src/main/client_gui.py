"""Launch the DCMS participant client (see package ``dcms_client``)."""

import tkinter as tk

from dcms_client import ClientGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
