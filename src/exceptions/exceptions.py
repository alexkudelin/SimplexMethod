# -*- coding: utf-8 -*-

class BasisError(Exception):
    def __init__(self):
        self.message = "Выбранные переменные не могут образовывать базис для решения данной задачи"

class BasisSizeError(Exception):
    def __init__(self):
        self.message = "Задано неправильное количество базисных переменных"

class SingularMatrixError(Exception):
    def __init__(self):
        self.message = "Матрица оказалась вырожденной"

class MatrixSizeError(Exception):
    def __init__(self):
        self.message = "Матрица имеет недопустимые размеры"

class ParsingValueError(Exception):
    def __init__(self, error_object):
        self.message = "Произошла ошибка при обработке значений " + error_object
