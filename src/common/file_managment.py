# -*- coding: utf-8 -*-
import pickle

def read_matrix_from_file(file):
    try:
        data = file.read()
        
        matrix = data.split("\n")

        raw_matrix = list(filter(lambda x: x != "", matrix))

        matrix = []

        for raw_row in raw_matrix:
            row = raw_row.replace("\t", " ").split(" ")
            row[:] = list(filter(lambda x: x != "", row))

            matrix.append(row)
        return matrix
    except:
        return None

def read_func_from_file(file):
    try:
        data = file.read()

        func = data.replace("\t", " ").split(" ")
        func[:] = list(filter(lambda x: x != "", func))

        return func
    except:
        return None

def dump_task_to_file(file, task):
    try:
        pickle.dump(task, file)

        return True
    except:
        return False

def load_task_from_file(file):
    try:
        data = pickle.load(file)

        return data
    except:
        return None

def dump_matrix_to_file(file, matrix):
    try:
        file.write("\n".join([" ".join([str(item) for item in row]) for row in matrix]))

        return True
    except:
        return False

def dump_func_to_file(file, func):
    try:
        file.write(" ".join([str(item) for item in func]))

        return True
    except:
        return False
