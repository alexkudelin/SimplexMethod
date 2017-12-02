# -*- coding: utf-8 -*-
from fractions import Fraction

class SimplexTable:
    """Class for descripting object of simplex table"""

    def __init__(self, variables_names = None, table = None, free_member = None, fractional = False, previous_table = None):
        self.__previous_table = previous_table

        if self.__previous_table:
            self.__row_variables_names = self.__previous_table.row_variables()
            self.__column_variables_names = self.__previous_table.column_variables()

            row_number, column_number = self.__previous_table.row_number(), self.__previous_table.column_number()

            self.__table = [[None for _ in range(column_number)] for _ in range(row_number)]

            self.__fractional = self.__previous_table.is_fractional()

            self.__iteration_number = self.__previous_table.iteration_number() + 1
        else:
            self.__table = table

            for free_value, row in zip(free_member, self.__table):
                row.append(free_value)

            self.__table.append([None for _ in range(len(self.__table[0]))])

            self.__variables = ["x{}".format(i + 1) for i in range(len(table[0]) + 1)]
            self.__variables.append("b")
            
            self.__row_variables_names = variables_names[0:len(self.__table) - 1]
            self.__column_variables_names = variables_names[len(self.__table) - 1 : -1]

            self.__fractional = fractional

            self.__iteration_number = 0

        self.__pivot_element = None

    def iteration_number(self):
        """Returns the number of iteration of simplex table"""
        return self.__iteration_number

    def size(self):
        return [len(self.__table) + 1, len(self.__table[0]) + 1]

    def is_fractional(self):
        """Returns **True** if table contains fractional values"""
        return self.__fractional
    
    def column_variables(self):
        """Returns names of variables that stay in columns headers as list of strings"""
        return self.__column_variables_names.copy()

    def row_variables(self):
        """Returns names of variables that stay in rows headers as list of strings"""
        return self.__row_variables_names.copy()

    def p0(self):
        """Returns p0 value, that is minimized value of goal function"""
        return -self.__table[-1][-1]

    def row_number(self):
        """Returns the number of rows in table (including vector P)"""
        return len(self.__table)

    def column_number(self):
        """Returns the number of columns in table (including free member)"""
        return len(self.__table[0])

    def free_member(self):
        """Returns vector of free members as list"""
        return [row[-1] for row in self.__table[:-1]]    

    def pivot_element(self):
        """Returns pivot element by **[row_var, col_var]** pair of variables names, like ["x1", "x2"]"""
        return self.__pivot_element

    def pivot_index(self):
        if self.__pivot_element is None:
            return

        pivot_row_var, pivot_column_var = self.__pivot_element
        pivot_row_var_index, pivot_column_var_index = self.__row_index_by_var(pivot_row_var), self.__column_index_by_var(pivot_column_var)

        return [pivot_row_var_index, pivot_column_var_index]
    
    def has_pivot(self):
        return self.__pivot_element is not None
    
    def p_vector(self):
        return self.__table[-1]

    def is_possible_pivot(self, row_index, column_index):
        p_vector = self.p_vector()

        if column_index == len(p_vector) - 1:
            return False

        if p_vector[column_index] >= 0:
            return False

        column = self.column(column_index)

        row_indices = [index for index, value in enumerate(column) if value > 0]

        ratios = None
        
        if self.__fractional:
            ratios = [Fraction(self.free_member()[index], column[index]) for index in row_indices]
        else:
            ratios = [self.free_member()[index]/column[index] for index in row_indices]

        possible_row_index = row_indices[ratios.index(min(ratios))]
        
        return possible_row_index == row_index

    def value_table(self):
        return self.__table

    def set_pivot_element(self, i, j):
        """Setting pivot element by **[row_var, col_var]** pair of variables names, like ["x1", "x2"]"""
        self.__pivot_element = [self.__row_variables_names[i], self.__column_variables_names[j]]
    
    def unset_pivot_element(self):
        self.__pivot_element = None

    def solve(self, func):
        """Method that performs auto-solving (automatic mode for choosing pivot element and etc.)"""
        if self.__pivot_element is None:
            if self.__previous_table:
                self.__previous_table.find_pivot_element()

        if self.__previous_table:
            self.__push_table()
        else:
            self.__calc_p_vector(func)

        return self.third_statement()

    def __push_table(self):
        prev_pivot_row_var, prev_pivot_column_var = self.__previous_table.pivot_element()
        prev_pivot_row_index, prev_pivot_column_index = self.__row_index_by_var(prev_pivot_row_var), self.__column_index_by_var(prev_pivot_column_var)

        self.__row_variables_names[prev_pivot_row_index] = prev_pivot_column_var
        self.__column_variables_names[prev_pivot_column_index] = prev_pivot_row_var

        prev_pivot_value = self.__previous_table.get_value_by_var(prev_pivot_row_var, prev_pivot_column_var)

        new_pivot_value = 1/prev_pivot_value
        new_pivot_row_var, new_pivot_column_var = prev_pivot_column_var, prev_pivot_row_var

        self.__set_value_by_var(new_pivot_row_var, new_pivot_column_var, new_pivot_value)

        new_pivot_row = []
        for index, item in enumerate(self.__previous_table.row_by_var(prev_pivot_row_var)):
            if index == self.__column_index_by_var(new_pivot_column_var):
                new_pivot_row.append(new_pivot_value)
            else:
                new_pivot_row.append(item/prev_pivot_value)

        new_pivot_column = []
        for index, item in enumerate(self.__previous_table.column_by_var(prev_pivot_column_var)):
            if index == self.__row_index_by_var(new_pivot_row_var):
                new_pivot_column.append(new_pivot_value)
            else:
                new_pivot_column.append(-1*item/prev_pivot_value)

        self.__set_row(self.__row_index_by_var(new_pivot_row_var), new_pivot_row)
        self.__set_column(self.__column_index_by_var(new_pivot_column_var), new_pivot_column)

        for index, row in enumerate(self.__table):
            if all(value is not None for value in row):
                continue
            prev_row = self.__previous_table.row(index)
            coeff = self.__previous_table.column_by_var(prev_pivot_column_var)[index]
            for row_index, item in enumerate(row):
                if item is None:
                    self.__table[index][row_index] = prev_row[row_index] - coeff*new_pivot_row[row_index]

    def get_value_by_var(self, row_var, col_var):
        """Returns the value of cell at coords **[row_var, col_var]**"""
        i, j = self.__row_variables_names.index(row_var), self.__column_variables_names.index(col_var)
        return self.__table[i][j]

    def __set_value_by_var(self, row_var, col_var, value):
        """Sets the **value** for cell at coords **[row_var, col_var]**"""
        if self.__fractional:
            value = Fraction(value)

        i, j = self.__row_variables_names.index(row_var), self.__column_variables_names.index(col_var)
        self.__table[i][j] = value

    def __calc_p_vector(self, func):
        """Methods that calculates the P vector"""
        for index, column_char in enumerate(self.__column_variables_names):
            s = func[self.__variables.index(column_char)]
            for row_char in self.__row_variables_names:
                s += -func[self.__variables.index(row_char)]*self.get_value_by_var(row_char, column_char)
            self.__table[-1][index] = s

        p0 = sum(-func[self.__variables.index(row_char)]*value for value, row_char in zip(self.free_member(), self.__row_variables_names))

        self.__table[-1][-1] = p0

    def first_statement(self):
        """For all **i > 0**: **P[i] >= 0** => **P[0] - minimal value of goal function**"""
        p_vector = self.p_vector()
        for item in p_vector[:-1]:
            if item < 0:
                return False

        return True

    def second_statement(self):
        """If *EXIST* the number **S** that: **P[S] < 0 and column[S][i] <= 0 (for all i=1,2,...,m)** => goal function is *unlimited*"""
        p_vector = self.p_vector()
        indices = [index for index, value in enumerate(p_vector[:-1]) if value < 0]

        for index in indices:
            if all(value <= 0 for value in self.column(index)):
                return True

        return False

    def third_statement(self):
        """If *EXIST* the number **S** that **P[S] < 0 and *EXIST* the number *R* that column[S][R] > 0 => possible to do one more iteration"""
        p_vector = self.p_vector()
        indices = [index for index, value in enumerate(p_vector[:-1]) if value < 0]
        for index in indices:
            if any(value <= 0 for value in self.column(index)):
                return True

        return False

    def column_by_var(self, var):
        """Returns column by name of varible"""
        if var not in self.__column_variables_names:
            return -1
        column_index = self.__column_variables_names.index(var)
        return self.column(column_index)

    def row_by_var(self, var):
        """Returns row by name of varible"""
        if var not in self.__row_variables_names:
            return -1
        row_index = self.__row_variables_names.index(var)
        return self.row(row_index)

    def column(self, index):
        """Returns the column by **index**"""
        if index < 0 or index >= len(self.__table[0]):
            return -1
        return [row[index] for row in self.__table]

    def row(self, index):
        """Returns the row by **index**"""
        if index < 0 or index >= len(self.__table):
            return -1
        return self.__table[index]

    def __column_index_by_var(self, var):
        """Returns the column index by **var**"""
        if var not in self.__column_variables_names:
            return -1

        return self.__column_variables_names.index(var)

    def __row_index_by_var(self, var):
        """Returns the row index by **var**"""
        if var not in self.__row_variables_names:
            return -1

        return self.__row_variables_names.index(var)

    def __set_column(self, index, new_col):
        """Set the new column at **index** in table"""
        for col_val, row in zip(new_col, self.__table):
            row[index] = col_val

    def __set_row(self, index, new_row):
        """Set the new row at **index** in table"""
        self.__table[index] = new_row

    def find_pivot_element(self):
        """Method that performs finding a pivot element in table"""
        if self.__pivot_element is not None:
            return

        p_vector = self.p_vector()

        col_indices = [index for index, value in enumerate(p_vector[:-1]) if value < 0 and any(item > 0 for item in self.column(index))]
        
        if len(col_indices) == 0:
            self.__pivot_element = None
            return

        col_index = p_vector.index(min([p_vector[index] for index in col_indices]))
        
        column = self.column(col_index)[:-1]

        row_indices = [index for index, value in enumerate(column) if value > 0]

        if len(row_indices) == 0:
            self.__pivot_element = None
            return

        ratios = None
        if self.__fractional:
            ratios = [Fraction(self.free_member()[index], column[index]) for index in row_indices]
        else:
            ratios = [self.free_member()[index]/column[index] for index in row_indices]

        row_index = row_indices[ratios.index(min(ratios))]

        self.__pivot_element = [self.__row_variables_names[row_index], self.__column_variables_names[col_index]]
