# -*- coding: utf-8 -*-
import tkinter as Tk
from src.controller.controller import Controller
from src.gui.dialogs.dialogs import *

class MainScreen:
    WHITE = "#F1F1F1" # фон всех виджетов
    ROSE = "#FFA69E" # названия свободных переменных
    BLUE = "#B8F3FF" # названия базисных переменных
    YELLOW = "#FBFFB8" # вектор P
    SALAD = "#C3FF94" # вектор b
    DARK_YELLOW = "#FFD31A" # P0
    DARK_BLUE = "#2B68E9" # опорный элемент
    LIGHT_BLUE = "#A4BFF9" # возможные опорные элементы

    def __init__(self, root, width = 800, height = 600):
        self.__window_height = height
        self.__window_width = width

        self.__main_frame = Tk.Frame(master = root, height = self.__window_height, width = self.__window_width, bg = MainScreen.WHITE)

        self.__controller = Controller(view = self)
        
        self.__create_menu_bar(root)
        self.__create_control_bar()
        self.__create_canvas()
        self.__configure_shortcuts()

        self.__steps_menu = None

        self.__main_frame.pack(fill = Tk.BOTH, expand = True)
        
    def main_frame(self):
        return self.__main_frame
        
    def __create_menu_bar(self, root):
        menu_bar = Tk.Menu(root)

        main_menu = Tk.Menu(menu_bar, tearoff = 0)
        edit_menu = Tk.Menu(menu_bar, tearoff = 0)
        # tools_menu = Tk.Menu(menu_bar, tearoff = 0)
        help_menu = Tk.Menu(menu_bar, tearoff = 0)

        new_task_menu = Tk.Menu(main_menu, tearoff = 0)
        new_task_menu.add_command(label = "симплекс-метод", command = lambda: self.__controller.simplex_method(), accelerator = "Ctrl+N, Ctrl+S")
        new_task_menu.add_command(label = "метод искусственного базиса", command = lambda: self.__controller.artificial_basis(), accelerator = "Ctrl+N, Ctrl+A")

        main_menu.add_cascade(label = "Новая задача...", menu = new_task_menu)
        main_menu.add_separator()
        main_menu.add_command(label = "Открыть задачу из файла", command = lambda: self.__controller.load_task(), accelerator = "Ctrl+O")
        main_menu.add_separator()
        main_menu.add_command(label = "Сохранить задачу в файл", command = lambda: self.__controller.save_task(), accelerator = "Ctrl+Shift+S")
        main_menu.add_separator()
        main_menu.add_command(label = "Выйти", command = root.quit)

        edit_menu.add_command(label = "Шаг назад", command = lambda: self.__controller.back_step())
        edit_menu.add_command(label = "Шаг вперед", command = lambda: self.__controller.next_step())

        help_menu.add_command(label = "Документация", command = lambda: self.__controller.show_help(), accelerator = "F1")
        help_menu.add_separator()
        help_menu.add_command(label = "О программе", command = lambda: self.__controller.show_about())
        
        menu_bar.add_cascade(label = "Файл", menu = main_menu)
        menu_bar.add_cascade(label = "Правка", menu = edit_menu)        
        menu_bar.add_cascade(label = "Справка", menu = help_menu)

        root.config(menu = menu_bar)

    def __create_control_bar(self):
        self.__control_bar = Tk.Frame(master = self.__main_frame, bg = MainScreen.WHITE)

        self.__back_button = Tk.Button(master = self.__control_bar, text = "Шаг назад", command = lambda: self.__controller.back_step(), bg = MainScreen.WHITE)
        self.__forward_button = Tk.Button(master = self.__control_bar, text = "Шаг вперед", command = lambda: self.__controller.next_step(), bg = MainScreen.WHITE)

        self.__steps_menu_frame = Tk.Frame(master = self.__control_bar, bg = MainScreen.WHITE)

        self.__back_button.pack(fill = Tk.X, side = Tk.LEFT, padx = 5, pady = 5)
        self.__steps_menu_frame.place(relx = .5, rely = .5, anchor = Tk.CENTER)
        self.__forward_button.pack(fill = Tk.X, side = Tk.RIGHT, padx = 5, pady = 5)
        
        self.__control_bar.pack(fill = Tk.X)

    def __configure_shortcuts(self):
        self.__main_frame.bind_all("<Control-o>", lambda event: self.__load_task(event))
        self.__main_frame.bind_all("<Control-S>", lambda event: self.__save_task(event))
        self.__main_frame.bind_all("<Control-n><Control-s>", lambda event: self.__new_simplex_task(event))
        self.__main_frame.bind_all("<Control-n><Control-a>", lambda event: self.__new_artificial_task(event))
        self.__main_frame.bind_all("<F1>", lambda event: self.__show_help(event))

    def __load_task(self, event = None):
        self.__controller.load_task()

    def __save_task(self, event = None):
        self.__controller.save_task()

    def __show_help(self, event = None):
        self.__controller.show_help()

    def __new_simplex_task(self, event = None):
        self.__controller.simplex_method()

    def __new_artificial_task(self, event = None):
        self.__controller.artificial_basis()

    def forward_button(self):
        return self.__forward_button

    def back_button(self):
        return self.__back_button

    def __create_canvas(self):
        self.__canvas = Tk.Canvas(master = self.__main_frame, bg = MainScreen.WHITE)
        self.__canvas.pack(fill = Tk.BOTH, expand = True)
        
    def __create_cell(self, master, data, bgcolor = None):
        return Tk.Label(master, text = data, bd = 3, relief = Tk.RIDGE, height = 4, width = 8, bg = bgcolor, font = ("Arial", 18))

    def show_table(self, table, has_pivot, is_editable):
        self.__clear_canvas()

        iteration_number = table.iteration_number()
        row_number, column_number = table.size()

        if has_pivot:
            pivot_row, pivot_column = table.pivot_index()

        table_frame = Tk.Frame(self.__canvas)
        
        self.__create_cell(table_frame, iteration_number).grid(row = 0, column = 0, padx = 2, pady = 2, sticky = Tk.N + Tk.W + Tk.S + Tk.E)
        self.__create_cell(table_frame, "b", MainScreen.YELLOW).grid(row = 0, column = column_number - 1, padx = 2, pady = 2, sticky = Tk.N + Tk.W + Tk.S + Tk.E)
        self.__create_cell(table_frame, "P", MainScreen.SALAD).grid(row = row_number - 1, column = 0, padx = 2, pady = 2, sticky = Tk.N + Tk.W + Tk.S + Tk.E)
        
        for index, item in enumerate(table.row_variables()):
            self.__create_cell(table_frame, item, MainScreen.ROSE).grid(row = index + 1, column = 0, padx = 2, pady = 2, sticky = Tk.N + Tk.W + Tk.S + Tk.E)
        
        for index, item in enumerate(table.column_variables()):
            self.__create_cell(table_frame, item, MainScreen.BLUE).grid(row = 0, column = index + 1, padx = 2, pady = 2, sticky = Tk.N + Tk.W + Tk.S + Tk.E)

        for i, row in enumerate(table.value_table()):
            for j, item in enumerate(row):
                color = MainScreen.WHITE

                if i == row_number - 2 and j != column_number - 2:
                    color = MainScreen.SALAD

                if j == column_number - 2 and i != row_number - 2:
                    color = MainScreen.YELLOW

                if i == row_number - 2 and j == column_number - 2:
                    color = MainScreen.DARK_YELLOW

                if table.is_possible_pivot(i, j):
                    color = MainScreen.LIGHT_BLUE
                
                if has_pivot:
                    if i == pivot_row and j == pivot_column:
                        color = MainScreen.DARK_BLUE

                cell = self.__create_cell(table_frame, item, color)

                if is_editable:
                    if table.is_possible_pivot(i, j):
                        cell.bind("<Button-1>", lambda event = None, i = i, j = j: self.__lmb_click(event, table, i, j))
                        cell.bind("<Button-3>", lambda event = None, i = i, j = j: self.__rmb_click(event, table, i, j))

                cell.grid(row = i + 1, column = j + 1, padx = 2, pady = 2, sticky = Tk.N + Tk.W + Tk.S + Tk.E)

        for i in range(row_number):
            table_frame.rowconfigure(i, weight = 1)

        for i in range(column_number):
            table_frame.columnconfigure(i, weight = 1)

        table_frame.pack(fill = Tk.BOTH, expand = True)

    def __lmb_click(self, event, table, i, j):
        table_frame = self.__canvas.winfo_children()[0]

        if table.pivot_element() is not None:
            current_pivot_i, current_pivot_j = table.pivot_index()
            current_pivot_label = table_frame.grid_slaves(current_pivot_i + 1, current_pivot_j + 1)[0]

            current_pivot_label.configure(bg = MainScreen.LIGHT_BLUE)

        table.set_pivot_element(i, j)
        new_pivot_label = table_frame.grid_slaves(i + 1, j + 1)[0]
        new_pivot_label.configure(bg = MainScreen.DARK_BLUE)

    def __rmb_click(self, event, table, i, j):
        table_frame = self.__canvas.winfo_children()[0]
        pivot_label = table_frame.grid_slaves(i + 1, j + 1)[0]
        pivot_label.configure(bg = MainScreen.LIGHT_BLUE)
        table.unset_pivot_element()

    def show_error_box(self, title, message):
        Tk.messagebox.showerror(title = title, message = message)
    
    def show_info_box(self, title, message):
        Tk.messagebox.showinfo(title = title, message = message)

    def disable_buttons(self):
        self.disable_forward_button()
        self.disable_back_button()

    def disable_forward_button(self):
        self.__forward_button.configure(state = Tk.DISABLED)

    def disable_back_button(self):
        self.__back_button.configure(state = Tk.DISABLED)

    def enable_buttons(self):
        self.enable_forward_button()
        self.enable_back_button()

    def enable_forward_button(self):
        self.__forward_button.configure(state = Tk.NORMAL)

    def enable_back_button(self):
        self.__back_button.configure(state = Tk.NORMAL)

    def reset(self):
        self.__clear_canvas()
        self.enable_buttons()

    def __clear_canvas(self):
        for child in self.__canvas.winfo_children():
            child.destroy()

        self.__canvas.delete("all")
