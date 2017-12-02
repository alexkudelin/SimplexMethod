# -*- coding: utf-8 -*-
from src.simplex.artificial_basis.artificial_basis_table import ArtificialBasisTable
from src.simplex.simplex_method.simplex_method import SimplexMethod
from src.simplex.simplex_method.simplex_table import SimplexTable
from src.exceptions.exceptions import *
from src.gauss.gauss import Gauss
from fractions import Fraction
import math

class ArtificialBasisMethod:
    def __init__(self, matrix = None, func = None, fractional = False):
        self.__matrix = matrix
        self.__func = func
        self.__fractional = fractional
        self.__tables = []
        self.__current_iteration = -1
        self.__p0 = None
        self.__can_continue_artificial = True
        self.__can_continue_simplex = False

    def __prepare_matrix(self):
        for row in self.__matrix:
            if row[-1] < 0:
                row[:] = [-item for item in row]

    def __prepare_function(self):
        if self.__fractional:
            self.__func[:] = [Fraction(item) for item in self.__func]

    def auto_solve(self):
        self.__prepare_matrix()
        self.__prepare_function()

        self.__can_continue_artificial = True

        while self.__can_continue_artificial:
            simplex_table = None

            if not self.__tables:
                simplex_table = ArtificialBasisTable(table = self.__matrix[:], fractional = self.__fractional)
            else:
                simplex_table = ArtificialBasisTable(previous_table = self.last_table())

            self.__can_continue_artificial = simplex_table.solve()

            if self.__can_continue_artificial:
                self.__current_iteration += 1

            self.__tables.append(simplex_table)

        point = self.last_table().get_point()
        
        simplex_method = SimplexMethod(matrix = self.__matrix, func = self.__func, fractional = self.__fractional, point = point)

        simplex_method.auto_solve()

        self.__tables += simplex_method.get_tables()
        self.__current_iteration += (simplex_method.current_iteration() + 1)
        
        self.__can_continue_simplex = simplex_method.can_continue()

    def next(self):
        simplex_table = None

        if self.__can_continue_artificial:
            if not self.__tables:
                simplex_table = ArtificialBasisTable(table = self.__matrix[:], fractional = self.__fractional)
            else:
                simplex_table = ArtificialBasisTable(previous_table = self.last_table())

            self.__can_continue_artificial = simplex_table.solve()

            if not self.__can_continue_artificial:
                self.__can_continue_simplex = True
        else:
            if type(self.last_table()) is SimplexTable:
                simplex_table = SimplexTable(previous_table = self.last_table())
            else:
                point = self.last_table().get_point()
                gauss = Gauss(matrix = self.__matrix, fractional = self.__fractional, point = point)

                if not gauss.solve():
                    raise SingularMatrixError()
                
                if any(item < 0 for item in gauss.free_member()):
                    raise BasisError()

                simplex_table = SimplexTable(variables_names = gauss.variables(),
                                             table = gauss.free_part(),
                                             free_member = gauss.free_member(),
                                             fractional = self.__fractional)

            self.__can_continue_simplex = simplex_table.solve(self.__func)

        self.__current_iteration += 1
        self.__tables.append(simplex_table)

    def back(self):
        del self.__tables[-1]
        self.__current_iteration -= 1

        if type(self.last_table()) is SimplexTable:
            self.__can_continue_simplex = self.last_table().third_statement()
            self.__can_continue_artificial = False
        elif type(self.last_table()) is ArtificialBasisTable:
            self.__can_continue_artificial = not self.last_table().end_statement()
            self.__can_continue_simplex = False

    def last_table(self):
        return self.__tables[-1]

    def tables_number(self):
        return len(self.__tables)

    def get_table(self, index = 0):
        return self.__tables[index]
    
    def can_continue(self):
        return self.__can_continue_artificial or self.__can_continue_simplex

    def let_continue(self):
        self.__can_continue = True

    def current_iteration(self):
        return self.__current_iteration

