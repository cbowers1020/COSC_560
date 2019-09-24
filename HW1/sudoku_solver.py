"""Solves a sudoku with given constraints and initial vals"""


import sys
from z3 import *
import argparse
import numpy as np

def parseArgs(args):
    """ Parse Args for this script """

    parser = argparse.ArgumentParser(description="This script takes an input file that defines preconditions for \
                                                    a sudoku and solves it")

    parser.add_argument("--input_file", "-if", type=str, dest="input_file", default="sudoku_input.txt",
                        help="Name of sudoku input file. Default=\"sudoku_input.txt\"")

    parser.add_argument("--remove_constraint", "-rc", action="store_true", help="Set this to remove first constraint. Runs for a long time...")

    args = parser.parse_args(args)

    return args


def vars_gen(rows, cols, vals):

    tot_vars = []
    cell_vars = []

    for r in rows:
        for c in cols:
            cell_vars.append(r + c)
            for v in vals:
                tot_vars.append(r + c + v)

    return cell_vars, tot_vars
    

def parse_input_file(args):

    on_vars = []

    with open(args.input_file, "r") as fn:
        for line in fn:
            line = line.strip()
            on_vars.append(line)

    return on_vars


def print_board(rows, cols, vals, bool_vars, model, init=False, on_vars=""):

    print_vars = np.zeros((9,9))

    if(init):
        r_count = 0
        for r in rows:
            c_count = 0
            for c in cols:
                for val in vals:
                    for v in on_vars:
                        if(v == str(r) + str(c) + str(val)):
                            print_vars[r_count][c_count] = int(val)
                c_count += 1
            r_count += 1

    else:
        r_count = 0
        for r in rows:
            c_count = 0
            for c in cols:
                for val in vals:
                    if(model[bool_vars[str(r) + str(c) + str(val)]]):
                        print_vars[r_count][c_count] = int(val)
                c_count += 1
            r_count += 1


    for r in range(0, 9):
        for c in range(0, 9):
            print(str(print_vars[r][c]) + "  ", end = '')
        print("")


def is_unique_sol(s, bool_vars, model):

    for key in bool_vars.keys():
        if(model[bool_vars[key]]):
            s.add(Not(bool_vars[key]))

    if(s.check() == sat):
        new_model = s.model()
        return False, new_model
    else:
        return True, model


def sudoku_solver(on_vars, output=True, check_unique=True, model_list=[]):
    """ Solver function to solve sudoku puzzle """

    rows = ["1_","2_","3_","4_","5_","6_","7_","8_","9_"]
    cols = ["1_","2_","3_","4_","5_","6_","7_","8_","9_"]
    vals = ["1","2","3","4","5","6","7","8","9"]

    cell_vars, tot_vars = vars_gen(rows, cols, vals)
    if(output):
        print("Number of boolean vars = " + str(len(tot_vars)))

    # cell_bool_vars = {e: Bool(e) for e in cell_vars}
    bool_vars = {e: Bool(e) for e in tot_vars}

    s = Solver()

    # Iitial conditions
    count_vars = 0
    for v in bool_vars.keys():
        if v in on_vars:
            count_vars += 1
            s.add(bool_vars[v])
    if(output):
        print("Added " + str(count_vars) + " for initial conditions")
        print("\nInitial board:\n")
        model=False
        print_board(rows, cols, vals, bool_vars, model, init=True, on_vars=on_vars)
        print("")

    # Add constraints from previous solves
    if(len(model_list) > 0):
        if(output):
            print("adding previous model constraints")
        count_vars = 0
        for key in bool_vars.keys():
            for model in model_list:
                if(model[bool_vars[key]] and (key not in on_vars)):
                    count_vars += 1
                    s.add(Not(bool_vars[key]))
        if(output):
            print("Added " + str(count_vars) + " from previous model(s)")


    # First constrain every cell to contain at least one of the values
    count_vars = 0
    # Iterate over each cell
    for cell in cell_vars:
        # Initialize to false since we are OR-ing everything
        cell_expr = False
        count_vars += 1
        s.add(Or([bool_vars[str(cell) + str(v)] for v in range(1,10)]))


    # Constrains each cell to not represent two different digits
    # Implies(cell_1_1_1, And(Not(cell_1_1_2), Not(cell_1_1_3), ...)
    count_vars = 0
    # Iterate over every cell
    for cell in cell_vars:
        # Init to false since we have everything OR'd
        # cell_expr = False
        # Start evaluating each value
        for v1 in range(1,10):
            # We want this value to be NOT, so we only have one value
            not_list = []
            for v2 in range(1,10):
                if(v1 == v2):
                    continue
                not_list.append(Not(bool_vars[str(cell) + str(v2)]))
            # not_func = Not()
            count_vars += 1
            s.add(Implies(bool_vars[str(cell) + str(v1)], And(not_list)))
    if(output):
        print("Added " + str(count_vars) + " constraints to restrict each cell not to represent two different digits")


    ##### Constrain each "Zone"#####

    # Row constraint
    count_vars = 0
    # define the cells to iterate over
    for r in range(1, 10):
        cells_in_zone = []
        for c in range(1,10):
            cells_in_zone.append(str(r) + "_" + str(c) + "_")

        # For each value that the cell could have
        for val in range(1,10):
            for c1 in cells_in_zone:
                # We want this to be true
                not_list = []
                for c2 in cells_in_zone:
                    if(c1 == c2):
                        continue
                    not_list.append(Not(bool_vars[str(c2) + str(val)]))
                    # AND these other values to be not true
                count_vars += 1
                s.add(Implies(bool_vars[str(c1) + str(val)], And(not_list)))
    if(output):
        print("Added " + str(count_vars) + " constraints to restrict each row not to repeat truth values")


    # Repeat for columns
    # Define the cells to iterate over
    count_vars = 0
    for c in range(1, 10):
        cells_in_zone = []
        for r in range(1,10):
            cells_in_zone.append(str(r) + "_" + str(c) + "_")

        # Each value the cell could have
        for val in range(1,10):
            for r1 in cells_in_zone:
                # We want this val to be true
                not_list = []
                for r2 in cells_in_zone:
                    if(r1 == r2):
                        continue
                    # AND other vals to not be true
                    not_list.append(Not(bool_vars[str(r2) + str(val)]))
                # All sub expressions are AND-ed together in solver
                count_vars += 1
                s.add(Implies(bool_vars[str(r1) + str(val)], And(not_list)))
    if(output):
        print("Added " + str(count_vars) + " constraints to restrict each column not to repeat truth values")


    # Repeat for squares
    # each sudoku is a 9X9 broken into 3X3 squares
    count_vars = 0
    # Define cells to iterate over
    for r in [1,4,7]:
        for c in [1,4,7]:
            cells_in_zone = []
            for m in range(0,3):
                for n in range(0,3):
                        cells_in_zone.append(str(r + m) + "_" + str(c + n) + "_")

        # Each value that can be in a cell
        for val in range(1,10):
            for s1 in cells_in_zone:
                # list to hold all "Not" vars
                not_list = []
                for s2 in cells_in_zone:
                    if(s1 == s2):
                        continue
                    # AND all others to be false
                    not_list.append(Not(bool_vars[str(s2) + str(val)]))
                # All sub expressions are AND-ed together in solver
                count_vars += 1
                s.add(Implies(bool_vars[str(s1) + str(val)], And(not_list)))
    if(output):
        print("Added " + str(count_vars) + " constraints to restrict each square not to repeat truth values")


    # print total assertions
    if(output):
        count = 0
        for i, formula in enumerate(s.assertions()):
            count += 1
            # print("{" + str(i) + "}: {" + str(formula) + "}")
        print("There are " + str(count) + " assertions")

    # Check if there is a solution
    if s.check() == sat:
        if(output):
            print("sat!\n")

            model = s.model()
            print("Solution:\n")
            print_board(rows, cols, vals, bool_vars, model)
            print("")

        # Check if unique
        if(check_unique):
            unique, model = is_unique_sol(s, bool_vars, model)
            if(unique):
                print("The above solution is unique!")
            else:
                print("There are more solutions! For example:")
                print_board(rows, cols, vals, bool_vars, model)

        return True, model

    else:
        if(output):
            print("Unsat!")
        model = False
        return False, model


def main(args):
    """main entry point"""

    args = parseArgs(args)

    on_vars = parse_input_file(args)

    solvable, model = sudoku_solver(on_vars)
    
    if(args.remove_constraint):
        print("\n\n\nRemoving first constraint: 1_2_1")
        print("Calculating number of solutions")
        on_vars = on_vars[1:]
        num_sols = 0
        model_list = []
        while(True):
            solvable, new_model = sudoku_solver(on_vars, output=True, check_unique=False, model_list=model_list)
            if (solvable):
                model_list.append(new_model)
                num_sols += 1
            else:
                break

        print("There are a total of " + str(num_sols) + " solutions after removing the first constraint")


if __name__ == '__main__':
    main(sys.argv[1:])