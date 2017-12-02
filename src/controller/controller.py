# -*- coding: utf-8 -*-
from src.gui.dialogs.dialogs import *
from src.simplex.simplex_method.simplex_method import SimplexMethod
from src.simplex.artificial_basis.artificial_basis_method import ArtificialBasisMethod
from src.exceptions.exceptions import *
from src.common import file_managment
import copy

class Controller:
    def __init__(self, view):
        self.__view = view
        self.__current_task = None
        self.__manual = False
        self.__current_iteration = 0

    def __prepare_method(self, is_artificial):
        dialog = MatrixSizeDialog(self.__view.main_frame())

        dialog_data = dialog.result

        if dialog_data is None:
            return False

        n, m, matrix = dialog_data

        dialog = MatrixValuesDialog(self.__view.main_frame(), n, m, matrix = matrix, is_artificial = is_artificial)
        dialog_data = dialog.result

        if dialog_data is None:
            return False

        return dialog_data

    def simplex_method(self):
        dialog_data = self.__prepare_method(is_artificial = False)

        if not dialog_data:
            return

        self.__view.reset()

        matrix, func, point, fractional, self.__manual = dialog_data

        self.__current_task = SimplexMethod(matrix = matrix, func = func, fractional = fractional, point = point)

        try:
            if self.__manual:
                self.__view.disable_back_button()
                self.__current_task.next()

                if not self.__current_task.can_continue():
                    self.__view.disable_buttons()
            else:
                self.__view.disable_forward_button()
                self.__current_task.auto_solve()
                self.__current_iteration = self.__current_task.current_iteration()

                if self.__current_iteration == 0:
                    self.__view.disable_buttons()

        except (BasisError, SingularMatrixError) as e:
            self.__view.show_error_box(e.message, e.message)
            self.__current_task = None

            return

        self.__show_last_table()

    def artificial_basis(self):
        dialog_data = self.__prepare_method(is_artificial = True)

        if not dialog_data:
            return

        self.__view.reset()
        
        matrix, func, _ , fractional, self.__manual = dialog_data

        self.__current_task = ArtificialBasisMethod(matrix, func, fractional)
        
        if self.__manual:
            self.__view.disable_back_button()
            self.__current_task.next()
        else:
            self.__view.disable_forward_button()
            self.__current_task.auto_solve()
            self.__current_iteration = self.__current_task.current_iteration()

            if self.__current_iteration == 0:
                self.__view.disable_buttons()

        self.__show_last_table()

    def next_step(self):
        if self.__current_task is None:
            return

        self.__view.enable_buttons()

        if self.__manual:
            self.__current_task.next()
            self.__show_last_table()

            if not self.__current_task.can_continue():
                 self.__view.disable_forward_button()
        else:
            if self.__current_iteration + 1 < self.__current_task.tables_number():
                self.__current_iteration += 1
                table = self.__current_task.get_table(self.__current_iteration)
                self.__view.show_table(table, table.has_pivot(), False)

                if self.__current_iteration == self.__current_task.tables_number() - 1:
                    self.__view.disable_forward_button()

    def back_step(self):
        if self.__current_task is None:
            return

        self.__view.enable_buttons()

        if self.__manual:
            self.__current_task.back()
            self.__show_last_table()

            if self.__current_task.tables_number() == 1:
                self.__view.disable_back_button()
        else:
            if self.__current_iteration - 1 >= 0:
                self.__current_iteration -= 1
                table = self.__current_task.get_table(self.__current_iteration)
                self.__view.show_table(table, table.has_pivot(), False)

                if self.__current_iteration == 0:
                    self.__view.disable_back_button()

    def __show_last_table(self):
        if self.__current_task is None:
            return

        is_editable = self.__manual and self.__current_task.can_continue()
        self.__view.show_table(self.last_table(), self.last_table().has_pivot(), is_editable)

    def last_table(self):
        return self.__current_task.last_table()

    def current_task(self):
        return self.__current_task

    def save_task(self):
        if self.__current_task is None:
            self.__view.show_info_box("Сохранение...", "Задачи, доступой для сохранения, ещё нет!")

        else:
            file = DumpTaskDialog(self.__view.main_frame()).get_file()

            if file is None:
                return

            if file_managment.dump_task_to_file(file, self.__current_task):
                self.__view.show_info_box("Сохранение...", "Задача успешно сохранена!")
            else:
                self.__view.show_error_box("Сохранение...", "В ходе сохранения произошла ошибка...")

    def load_task(self):
        file = LoadTaskDialog(Tk.Frame(self.__view.main_frame())).get_file()

        if file is None:
            return

        data = file_managment.load_task_from_file(file)

        if data is None:
            self.__view.show_error_box("Загрузка...", "В ходе загрузки произошла ошибка...")
        else:
            self.__current_task = data
            self.__show_last_table()
            self.__view.disable_forward_button()

    def show_help(self):
        HelpDialog(self.__view.main_frame())
    
    def show_about(self):
        self.__view.show_info_box("О приложении", """Разработал:\n\tстудент 3-го курса\n\tфакультета ИВТ,\n\tнаправления "Прикладная\n\tматематика и информатика"\n\tКуделин Алексей""")