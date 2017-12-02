# -*- coding: utf-8 -*-
import tkinter as Tk
from src.gui.main_screen import MainScreen

root = Tk.Tk()
root.title("Решение задач симплекс методом")
app = MainScreen(root)
root.mainloop()
