# -*- coding: utf-8 -*-
from fractions import Fraction
import time
import random

class Gauss:
    """Class that implement Gauss method for solving matrices"""

    def __init__(self, matrix, fractional = False, point = None):
        """Constructor. Defines attributes: matrix, variables names, _'fractional'_ flag that uses for indicate using fractions (else, floats with rounding)"""
        self.__matrix = matrix
        self.__variables = ["x{0}".format(i + 1) for i in range(len(self.__matrix[0]) - 1)]
        self.__variables += "b"
        self.__fractional = fractional
        self.__point = point

    def __del__(self):
        """Destrcutor"""
        del self.__matrix
        del self.__variables
        del self.__fractional

    def free_part(self):
        """Returns free part of matrix as list of lists(list of rows) exclude _free member_"""
        return [row[len(self.__matrix):-1] for row in self.__matrix]

    def variables(self):
        """Returns variables names as list like ["x1", "x2", ..., "xN", "b"] where 'b' is a _free member_"""
        return self.__variables

    def free_member(self):
        """Returns _free member_ as list of values"""
        return [row[-1] for row in self.__matrix]

    def __convert_to_fractions(self):
        """Converter of matrix values to fractions"""
        for row in self.__matrix:
            row[:] = [Fraction(item) for item in row]

    def solve(self):
        """Method that starts solving"""
        print("Start Gauss method")

        if self.__fractional:
            self.__convert_to_fractions()
        
        if self.__point is not None:
            for i in range(len(self.__variables) - 1):
                for j in range(i, len(self.__variables) - 1):
                    if self.__point[j] > self.__point[i]:
                        self.__point[i], self.__point[j] = self.__point[j], self.__point[i]
                        self.__swap_columns(i, j)

        self.__find_zero_columns()
        self.__straight_way()
        self.__reversal_way()

        print("End Gauss method")
        return self.__is_not_singular()

    def __straight_way(self):
        """Method that performs a _straight way_"""
        print("Straight way...")
        steps = len(self.__matrix)

        for step in range(steps):
            if self.__matrix[step][step] == 0:
                row_index = next((index for index, value in enumerate(self.__column(step)) if value != 0), None)
                if row_index is None:
                    self.__move_column_back(step)
                    continue
                else:
                    self.__swap_rows(step, row_index)

            for k in range(step + 1, steps):
                self.__subtract(i = step, j = k)

            self.__normalize(step)
            self.__find_zero_columns()

    def __reversal_way(self):
        """Method that performs a _reversal way_"""
        print("Reversal way...")
        steps = len(self.__matrix)

        for step in reversed(range(steps)):
            if self.__matrix[step][step] == 0:
                row_index = next((index for index, value in enumerate(self.__column(step)) if value != 0), None)
                if row_index is None:
                    self.__move_column_back(step)
                    continue
                else:
                    self.__swap_rows(step, row_index)

            for k in range(0, step):
                self.__subtract(i = step, j = k)

            self.__normalize(step)
            self.__find_zero_columns()

    def __is_not_singular(self):
        """Returns _**True**_ if matrix is not singular"""
        flag = True
        for i in range(len(self.__matrix)):
            column = self.__column(i)
            flag &= (column.count(1) == 1 and column[i] == 1)

        return flag

    def __subtract(self, i, j):
        """Method that substract row at _**i**_-pos from row at _**j**_-pos"""
        row_length = len(self.__matrix[0])
        self.__matrix[j] = [self.__matrix[j][k]*self.__matrix[i][i] - self.__matrix[i][k]*self.__matrix[j][i] for k in range(row_length)]

    def __swap_rows(self, i, j):
        """Method that performs swap of _i_ and _j_ rows"""
        self.__matrix[i], self.__matrix[j] = self.__matrix[j], self.__matrix[i]

    def __swap_columns(self, i, j):
        """Method that performs swap of _i_ and _j_ columns"""
        for row in self.__matrix:
            row[i], row[j] = row[j], row[i]

        self.__variables[i], self.__variables[j] = self.__variables[j], self.__variables[i]

    def __move_column_back(self, index):
        """Method that moves column at _index_ to the pre-last position (before _free member_)"""
        column = self.__pop_column(index)
        self.__append_column(column)

        # перемещаем названия переменных соответственно
        self.__variables.insert(-1, self.__variables.pop(index))

    def __pop_column(self, index):
        """Method that performs popping column that has index _index_"""
        column = []
        for row in self.__matrix:
            column.append(row.pop(index))

        return column

    def __append_column(self, column):
        """Method that performs appending _column_ to the pre-last position (before _free member_)"""
        for row_index, row in enumerate(self.__matrix):
            row.insert(-1, column[row_index])

    def __normalize(self, row_index):
        """Method that normalize row that has index _row_index_"""
        coeff = self.__matrix[row_index][row_index]

        if coeff == 0:
            return

        for k in range(row_index, len(self.__matrix[row_index])):                
            self.__matrix[row_index][k] /= coeff

            if not self.__fractional:
                self.__matrix[row_index][k] = round(self.__matrix[row_index][k], 3)

    def __find_zero_columns(self):
        """Method that finding all-zeroes columns in matrix and performs their moving to the back"""
        for column_index in range(len(self.__matrix[0])):
            column = self.__column(column_index)
            if all(item == 0 for item in column):
                self.__move_column_back(column_index)

    def __column(self, index):
        """Returns column at _index_ as list"""
        return [self.__matrix[row_index][index] for row_index in range(len(self.__matrix))]

    def __str__(self):
        """Prints matrix fancy"""
        print("============================")
        print(self.__variables)
        for row in self.__matrix:
            print([str(item) for item in row])
        print("============================")

# if __name__ == "__main__":
#     matrix = [[int(random.random()*100)%15 for j in range(7)] for i in range(4)]

#     for j in range(len(matrix)):
#         matrix[j][2] = 0

#     g = Gauss(matrix = matrix, fractional = True)
#     print(g.solve())
#     print(g.variables())