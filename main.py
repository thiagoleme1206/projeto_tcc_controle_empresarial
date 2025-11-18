# main.py

import tkinter as tk
from app.views.login_viewer import LoginViewer
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    root = tk.Tk()
    LoginViewer(root)
    root.mainloop()
