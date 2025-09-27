# run.py (ponto de entrada do sistema)
import tkinter as tk
from login import LoginScreen

if __name__ == "__main__":
    root_login = tk.Tk()
    app_login = LoginScreen(root_login)
    root_login.mainloop()

if __name__ == "__main__":
    import sys
    if getattr(sys, 'frozen', False):
        import multiprocessing
        multiprocessing.freeze_support()