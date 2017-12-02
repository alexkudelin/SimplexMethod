# -*- coding: utf-8 -*-
import tkinter as Tk
import tkinter.ttk as Ttk
from tkinter import simpledialog
from tkinter import filedialog
from fractions import Fraction
from src.common import file_managment
from src.exceptions.exceptions import *
from src.gui.dialogs.docs.doc import Doc

class MatrixSizeDialog(simpledialog.Dialog):
    def __init__(self, root):
        simpledialog.Dialog.__init__(self, root, "Введите размеры матрицы ограничений")
        
    def body(self, root):
        main_frame = Tk.Frame(root)

        self.__option_var = Tk.IntVar(0)

        self.__create_manual_frame(main_frame)
        self.__create_auto_frame(main_frame)

        self.__switch_frames()

        main_frame.grid(row = 0, column = 0)

    def __create_manual_frame(self, main_frame):
        Tk.Radiobutton(main_frame, text = "Ввести размеры матрицы вручную", variable = self.__option_var, value = 0, command = lambda: self.__switch_frames()).grid(row = len(main_frame.winfo_children()), column = 0, padx = 5, pady = 5, sticky = Tk.W)

        self.__manual_frame = Tk.Frame(main_frame)

        Tk.Label(self.__manual_frame, text = "N:").grid(row = 1, column = 0, sticky = Tk.E)
        Tk.Label(self.__manual_frame, text = "M:").grid(row = 2, column = 0, sticky = Tk.E)

        self.__N, self.__M = Tk.IntVar(self.__manual_frame, 0), Tk.IntVar(self.__manual_frame, 0)

        self.__entry_N = Tk.Spinbox(self.__manual_frame, textvariable = self.__N, from_ = 1, to = 16)
        self.__entry_M = Tk.Spinbox(self.__manual_frame, textvariable = self.__M, from_ = 1, to = 16)

        self.__entry_N.grid(row = 1, column = 1)
        self.__entry_M.grid(row = 2, column = 1)

        self.__manual_frame.grid(row = len(main_frame.winfo_children()), column = 0, padx = 5, pady = 5, sticky = Tk.N + Tk.S)

    def __create_auto_frame(self, main_frame):
        Tk.Radiobutton(main_frame, text = "Загрузить матрицу из файла", variable = self.__option_var, value = 1, command = lambda: self.__switch_frames()).grid(row = len(main_frame.winfo_children()), column = 0, padx = 5, pady = 5, sticky = Tk.W)

        self.__auto_frame = Tk.Frame(main_frame)

        self.__file = None
        
        Tk.Button(self.__auto_frame, text = "Выбрать файл", command = lambda: self.__ask_open_file()).grid(row = 3, column = 0, columnspan = 2, padx = 5, pady = 5)

        self.__auto_frame.grid(row = len(main_frame.winfo_children()), column = 0, padx = 5, pady = 5, sticky = Tk.N + Tk.S)

    def __switch_frames(self):
        state = bool(self.__option_var.get())

        for child in self.__manual_frame.winfo_children():
            child.config(state = [Tk.NORMAL, Tk.DISABLED][state])

        for child in self.__auto_frame.winfo_children():
            child.config(state = [Tk.NORMAL, Tk.DISABLED][not state])

    def __ask_open_file(self):
        options = {}
        options["defaultextension"] = ".mat"
        options["filetypes"] = [("Файлы матрицы", ".mat"), ("Текстовые файлы", ".txt")]
        options["initialdir"] = "./"
        options["parent"] = self.__auto_frame
        options["title"] = "Открыть файл матрицы"

        file = filedialog.askopenfile("r", **options)

        if file is not None:
            self.__file = file
            filename = self.__file.name.replace("\\", "/").split("/")[-1]
            Tk.Label(self.__auto_frame, text = "Текущий файл: " + filename).grid(row = 4, column = 0, columnspan = 2, padx = 5, pady = 5)

    def apply(self):
        if self.__option_var.get():
            if self.__file is not None:
                matrix = file_managment.read_matrix_from_file(self.__file)

                if matrix is None:
                    self.result = None
                    return

                n = len(matrix)
                m = len(matrix[0]) - 1

                self.result = [n, m, matrix]
        else:
            try:
                if 0 < self.__N.get() <= 16 and 0 < self.__M.get() <= 16:
                    self.result = [self.__N.get(), self.__M.get(), None]
                else:
                    self.result = None
            except:
                self.result = None

    def validate(self):
        if self.__option_var.get():
            if self.__file is not None:
                return True
        else:
            if 0 < self.__N.get() <= 16 and 0 < self.__M.get() <= 16:
                return True
            else:
                Tk.messagebox.showerror(title = MatrixSizeError().message, message = MatrixSizeError().message)
                return False

class MatrixValuesDialog(simpledialog.Dialog):
    def __init__(self, root, row_number, column_number, is_artificial, matrix = None):
        self.__row_number, self.__column_number = row_number, column_number
        self.__is_artificial = is_artificial
        self.__fractional, self.__manual = Tk.BooleanVar(root, False), Tk.BooleanVar(root, False)
        self.__matrix = [[Tk.StringVar() for _ in range(self.__column_number + 1)] for _ in range(self.__row_number)]
        self.__func = [Tk.StringVar() for _ in range(self.__column_number)]
        self.__point = [Tk.BooleanVar(False) for _ in range(self.__column_number)]

        if matrix is not None:
            for row_1, row_2 in zip(self.__matrix, matrix):
                for entry, item in zip(row_1, row_2):
                    entry.set(item)
        
        simpledialog.Dialog.__init__(self, root, "Введите значения матрицы ограничений")

    def apply(self):
        self.__parse_matrix()
        self.__parse_func()
        self.__parse_point()

        self.fractional = self.__fractional.get()
        self.manual = self.__manual.get()

        self.result = [self.matrix, self.func, self.point, self.fractional, self.manual]

    def validate(self):
        if not self.__validate_matrix():
            Tk.messagebox.showerror(title = ParsingValueError("матрицы").message, message = ParsingValueError("матрицы").message)
            return False
        if not self.__validate_func():
            Tk.messagebox.showerror(title = ParsingValueError("функции").message, message = ParsingValueError("функции").message)
            return False
        if not self.__validate_point():
            Tk.messagebox.showerror(title = BasisSizeError().message, message = BasisSizeError().message)
            return False
        
        return True

    def __ask_open_file(self, root):
        options = {}
        options["defaultextension"] = ".func"
        options["filetypes"] = [("Файлы со значениями функций", ".func"), ("Текстовые файлы", ".txt")]
        options["initialdir"] = "./"
        options["parent"] = root
        options["title"] = "Открыть файл функции"

        file = filedialog.askopenfile("r", **options)

        if file is not None:
            func = file_managment.read_func_from_file(file)
            for entry, item in zip(self.__func, func):
                entry.set(item)

    def __dump_matrix(self, root):
        file = DumpMatrixDialog(root).get_file()

        if file is None:
            return

        if not self.__validate_matrix():
            Tk.messagebox.showerror(title = "Сохранение...", message = "Формат введенных данных неправильный!")
            return
        
        self.__parse_matrix()

        if not file_managment.dump_matrix_to_file(file, self.matrix):
            Tk.messagebox.showerror(title = "Сохранение...", message = "Произошла ошибка при записи матрицы в файл!\nПовторите попытку!")
        else:
            Tk.messagebox.showinfo(title = "Сохранение...", message = "Запись прошла успешно!")

    def __dump_func(self, root):
        file = DumpFuncDialog(root).get_file()

        if file is None:
            return

        if not self.__validate_func():
            Tk.messagebox.showerror(title = "Сохранение...", message = "Формат введенных данных неправильный!")
            return
        
        self.__parse_func()

        if not file_managment.dump_func_to_file(file, self.func):
            Tk.messagebox.showerror(title = "Сохранение...", message = "Произошла ошибка при записи функции в файл!\nПовторите попытку!")
        else:
            Tk.messagebox.showinfo(title = "Сохранение...", message = "Запись прошла успешно!")

    def body(self, root):
        self.__create_matrix_frame(root)        
        self.__create_func_frame(root)

        if not self.__is_artificial:
            self.__create_point_frame(root)
            
        Tk.Checkbutton(root, text = "Оставить обыкновенные дроби", variable = self.__fractional, font = ("Arial", 10)).grid(row = len(root.winfo_children()), column = 0)
        Tk.Checkbutton(root, text = "Решать в пошаговом режиме", variable = self.__manual, font = ("Arial", 10)).grid(row = len(root.winfo_children()), column = 0)
        
    def __create_matrix_frame(self, root):
        if self.__row_number == 0 or self.__column_number == 0:
            return

        matrix_frame = Tk.Frame(root)
        
        Tk.Label(matrix_frame, text = "Введите значения матрицы в клетки ниже", font = ("Arial", 12)).grid(row = len(matrix_frame.winfo_children()), column = 0, padx = 5, pady = 3)

        matrix_value_frame = Tk.Frame(matrix_frame)

        for i in range(self.__column_number):
            Tk.Label(matrix_value_frame, text = "x{0}".format(i + 1)).grid(row = 0, column = i, padx = 5, pady = 2)

        Tk.Label(matrix_value_frame, text = "b").grid(row = 0, column = self.__column_number, padx = 5, pady = 2)
        

        for i in range(self.__row_number):
            for j in range(self.__column_number + 1):
                Tk.Entry(matrix_value_frame, textvariable = self.__matrix[i][j], width = 10).grid(row = i + 1, column = j, padx = 3, pady = 1)
        
        matrix_value_frame.grid(row = len(matrix_frame.winfo_children()), column = 0, padx = 5, pady = 5)

        Tk.Button(matrix_frame, text = "Сохранить данную матрицу в файл", command = lambda: self.__dump_matrix(root)).grid(row = len(matrix_frame.winfo_children()), column = 0, padx = 5, pady = 3)

        matrix_frame.grid(row = len(root.winfo_children()), column = 0, padx = 5, pady = 5)

        Ttk.Separator(root, orient = Tk.HORIZONTAL).grid(row = len(root.winfo_children()), column = 0, padx = 5, pady = 5, sticky = Tk.W + Tk.E)

    def __create_func_frame(self, root):
        func_frame = Tk.Frame(root)

        Tk.Label(func_frame, text = "Введите коэффициенты функции в поля ниже", font = ("Arial", 12)).grid(row = len(func_frame.winfo_children()), column = 0, padx = 5, pady = 5)

        func_value_frame = Tk.Frame(func_frame)
        
        for i in range(self.__column_number - 1):
            Tk.Entry(func_value_frame, textvariable = self.__func[i], width = 10).grid(row = 0, column = len(func_value_frame.winfo_children()), padx = 2, pady = 5)            
            Tk.Label(func_value_frame, text = "*x{0} + ".format(i + 1)).grid(row = 0, column = len(func_value_frame.winfo_children()), padx = 2, pady = 5)            
        
        Tk.Entry(func_value_frame, textvariable = self.__func[-1], width = 10).grid(row = 0, column = len(func_value_frame.winfo_children()), padx = 2, pady = 5)
        Tk.Label(func_value_frame, text = "*x{0} -> MIN".format(self.__column_number)).grid(row = 0, column = len(func_value_frame.winfo_children()), padx = 2, pady = 5)

        func_value_frame.grid(row = len(func_frame.winfo_children()), column = 0, padx = 5, pady = 5)

        button_frame = Tk.Frame(func_frame)

        Tk.Button(button_frame, text = "Загрузить функцию из файла", command = lambda: self.__ask_open_file(root)).grid(row = 0, column = 0, padx = 3)
        Tk.Button(button_frame, text = "Сохранить функцию в файл", command = lambda: self.__dump_func(root)).grid(row = 0, column = 1, padx = 3)

        button_frame.grid(row = len(func_frame.winfo_children()), column = 0, padx = 5, pady = 3)

        func_frame.grid(row = len(root.winfo_children()), column = 0, padx = 5, pady = 5)
        Ttk.Separator(root, orient = Tk.HORIZONTAL).grid(row = len(root.winfo_children()), column = 0, padx = 5, pady = 5, sticky = Tk.W + Tk.E)

    def __create_point_frame(self, root):
        self.__point_frame = Tk.Frame(root)

        Tk.Label(self.__point_frame, text = "Выберите {0} базисные переменные".format(self.__row_number), font = ("Arial", 12)).grid(row = len(self.__point_frame.winfo_children()), column = 0, padx = 5, pady = 5)

        point_subframe = Tk.Frame(self.__point_frame, relief = Tk.GROOVE, bd = 3)

        for i in range(self.__column_number):
            Tk.Label(point_subframe, text = "x{0}".format(i + 1)).grid(row = 0, column = i, padx = 5)
            Tk.Checkbutton(point_subframe, variable = self.__point[i]).grid(row = 1, column = i, padx = 5, pady = 2)
        
        point_subframe.grid(row = len(self.__point_frame.winfo_children()), column = 0, padx = 5)

        self.__point_frame.grid(row = len(root.winfo_children()), column = 0, padx = 5, pady = 5)
        Ttk.Separator(root, orient = Tk.HORIZONTAL).grid(row = len(root.winfo_children()), column = 0, padx = 5, pady = 5, sticky = Tk.W + Tk.E)

    def __validate_matrix(self):
        try:
            matrix = [[None for _ in range(self.__column_number + 1)] for _ in range(self.__row_number)]
            for i, row in enumerate(self.__matrix):
                for j, item in enumerate(row):
                    value = Fraction(item.get().replace("\\", "/").replace(",", "."))
                    
                    if not self.__fractional.get():
                        value = float(value)
                        
                    matrix[i][j] = value

            return True
        except ValueError:
            return False

    def __parse_matrix(self):
        try:
            self.matrix = []

            for row in self.__matrix:
                temp_row = []

                for item in row:
                    value = Fraction(item.get().replace("\\", "/").replace(",", "."))

                    if not self.__fractional.get():
                        value = float(value)

                    temp_row.append(value)

                self.matrix.append(temp_row)
        except ValueError:
            self.matrix = None

    def __validate_func(self):
        try:
            func = []
            for item in self.__func:
                value = Fraction(item.get().replace("\\", "/").replace(",", "."))
                
                if not self.__fractional.get():
                    value = float(value)

                func.append(value)

            return True
        except ValueError:
            return False

    def __parse_func(self):
        try:
            self.func = []

            for item in self.__func:
                value = Fraction(item.get().replace("\\", "/").replace(",", "."))
                
                if not self.__fractional.get():
                    value = float(value)

                self.func.append(value)
        except ValueError:
            self.func = None

    def __validate_point(self):
        if self.__is_artificial:
            return True

        point = [int(item.get()) for item in self.__point]

        return point.count(1) == self.__row_number

    def __parse_point(self):
        if self.__is_artificial:
            self.point = None

        self.point = [int(item.get()) for item in self.__point]

class DumpTaskDialog:

    def __init__(self, root):
        self.__root = root

    def get_file(self):
        options = {}
        options["defaultextension"] = ".task"
        options["filetypes"] = [("Файл задачи", ".task")]
        options["initialdir"] = "./"
        options["parent"] = self.__root
        options["title"] = "Сохранить задачу в файл"

        return filedialog.asksaveasfile(mode = "wb", **options)

class LoadTaskDialog:

    def __init__(self, root):
        self.__root = root
    
    def get_file(self):
        options = {}
        options["defaultextension"] = ".task"
        options["filetypes"] = [("Файл задачи", ".task")]
        options["initialdir"] = "./"
        options["parent"] = self.__root
        options["title"] = "Открыть задачу из файла"

        return filedialog.askopenfile(mode = "rb", **options)

class DumpMatrixDialog:

    def __init__(self, root):
        self.__root = root

    def get_file(self):
        options = {}
        options["defaultextension"] = ".mat"
        options["filetypes"] = [("Файлы матрицы", ".mat"), ("Текстовые файлы", ".txt")]
        options["initialdir"] = "./"
        options["parent"] = self.__root
        options["title"] = "Сохранить матрицу в файл"

        return filedialog.asksaveasfile(mode = "w", **options)

class DumpFuncDialog:

    def __init__(self, root):
        self.__root = root

    def get_file(self):
        options = {}
        options["defaultextension"] = ".func"
        options["filetypes"] = [("Файлы со значениями функций", ".func"), ("Текстовые файлы", ".txt")]
        options["initialdir"] = "./"
        options["parent"] = self.__root
        options["title"] = "Открыть файл функции"

        return filedialog.asksaveasfile(mode = "w", **options)

class HelpDialog(simpledialog.Dialog):

    def __init__(self, root):
        simpledialog.Dialog.__init__(self, root, "Справка")
        
    def body(self, root):
        frame = Tk.Frame(self, width = 400, height = 400)
        
        self.__main_frame = Tk.Frame(frame, width = 350, height = 30)
        self.__listbox = Tk.Listbox(frame, width = 50, height = 30)

        steps_names = ["Начало работы", "Главный экран", "Интерфейс", "Сохранение и открытие задач"]
        
        for index, step_name in enumerate(steps_names):
            self.__listbox.insert(index, step_name)
        
        self.__listbox.bind("<Double-Button-1>", lambda index: self.__show_step(index = self.__listbox.curselection()[0]))
        self.__show_step(index = 0)
        
        self.__listbox.pack(side = Tk.LEFT, padx = 10, pady = 10, fill = Tk.Y)
        self.__main_frame.pack(side = Tk.LEFT, padx = 10, pady = 10)

        frame.pack(side = Tk.TOP)
        
    def __show_step(self, event = None, index = 0):
        for child in self.__main_frame.winfo_children():
            child.destroy()

        step_frame = Tk.Frame(self.__main_frame, width = 120, relief = Tk.RIDGE)
        step = Tk.Label(self.__main_frame, width = 120, text = Doc.CHAPTERS[index], font = ("Arial", 11), anchor = Tk.W, justify = Tk.LEFT)

        step.pack(side = Tk.LEFT, padx = 10, pady = 10, fill = Tk.Y)
        step_frame.pack(side = Tk.LEFT, padx = 10, pady = 10, fill = Tk.Y)

    def buttonbox(self):
        button_box = Tk.Frame(self)

        close_button = Tk.Button(button_box, text = "Закрыть", width = 10, command = self.cancel, default = Tk.ACTIVE)
        close_button.pack(padx = 5, pady = 5)

        self.bind("<Escape>", self.cancel)

        button_box.pack(side = Tk.TOP)

    def ok(self, event = None):
        pass
    
    def validate(self):
        return True
