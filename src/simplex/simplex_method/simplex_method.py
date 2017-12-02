# -*- coding: utf-8 -*-
import math
from src.gauss.gauss import Gauss
from src.exceptions.exceptions import *
from .simplex_table import SimplexTable
from fractions import Fraction

class SimplexMethod:
    def __init__(self, matrix = None, func = None, fractional = False, point = None, current_iteration = 0):
        self.__matrix = matrix
        self.__func = func
        self.__fractional = fractional
        self.__tables = []
        self.__current_iteration = current_iteration
        self.__point = point

    def auto_solve(self):
        gauss = Gauss(matrix = self.__matrix, fractional = self.__fractional, point = self.__point)

        if not gauss.solve():
            raise SingularMatrixError()

        if any(item < 0 for item in gauss.free_member()):
            raise BasisError()

        self.__can_continue = True

        if self.__fractional:
            self.__func[:] = [Fraction(item) for item in self.__func]

        while self.__can_continue:
            simplex_table = None

            if not self.__tables:
                simplex_table = SimplexTable(variables_names = gauss.variables(),
                                             table = gauss.free_part(),
                                             free_member = gauss.free_member(),
                                             fractional = self.__fractional)
            else:
                simplex_table = SimplexTable(previous_table = self.last_table())

            self.__can_continue = simplex_table.solve(self.__func)

            if not self.__can_continue:
                self.__p0 = simplex_table.p0()
            
            self.__current_iteration = simplex_table.iteration_number()
            self.__tables.append(simplex_table)

    def next(self):
        simplex_table = None

        if not self.__tables:
            gauss = Gauss(matrix = self.__matrix, fractional = True, point = self.__point)

            if not gauss.solve():
                raise SingularMatrixError()

            if any(item < 0 for item in gauss.free_member()):
                raise BasisError()

            simplex_table = SimplexTable(variables_names = gauss.variables(),
                                         table = gauss.free_part(),
                                         free_member = gauss.free_member(),
                                         fractional = self.__fractional)
        else:
            simplex_table = SimplexTable(previous_table = self.last_table())

        self.__can_continue = simplex_table.solve(self.__func)
        
        if not self.__can_continue:
            self.__p0 = simplex_table.p0()

        self.__current_iteration = simplex_table.iteration_number()
        self.__tables.append(simplex_table)

    def back(self):
        del self.__tables[-1]
        self.__current_iteration -= 1
        self.let_continue()
        
    def last_table(self):
        return self.__tables[-1]

    def tables_number(self):
        return len(self.__tables)

    def get_table(self, index = 0):
        return self.__tables[index]

    def get_tables(self):
        return self.__tables

    def p0(self):
        return self.__p0

    def can_continue(self):
        return self.__can_continue

    def let_continue(self):
        self.__can_continue = True

    def current_iteration(self):
        return self.__current_iteration
