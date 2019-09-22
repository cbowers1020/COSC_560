"""Solves a sudoku with given constraints and initial vals"""


import sys
from z3 import *
import argparse

def parseArgs(args):
    """ Parse Args for this script """

    parser = argparse.ArgumentParser(description="This script takes an input file that defines preconditions for \
                                                    a sudoku and solves it")

    parser.add_argument("--input_file", "-if", type=str, dest="input_file", default="sudoku_input.txt",
                        help="Name of sudoku input file. Default=\"sudoku_input.txt\"")

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


def main(args):
    """main entry point"""

    args = parseArgs(args)

    on_vars = parse_input_file(args)


    rows = ["1_","2_","3_","4_","5_","6_","7_","8_","9_"]
    cols = ["1_","2_","3_","4_","5_","6_","7_","8_","9_"]
    vals = ["1","2","3","4","5","6","7","8","9"]

    cell_vars, tot_vars = vars_gen(rows, cols, vals)
    print(str(len(tot_vars)))

    # cell_bool_vars = {e: Bool(e) for e in cell_vars}
    bool_vars = {e: Bool(e) for e in tot_vars}

    s = Solver()

    for v in bool_vars.keys():
        if v in on_vars:
            s.add(bool_vars[v])


    # print(bool_vars)

    

    # First constrain every cell to contain at least one of the values
    for cell in cell_vars:
        for v1 in range(1,10):
            for v2 in range(v1+1,10):
                s.add(Or(bool_vars[cell + str(v1)],bool_vars[cell + str(v2)]))

    # count = 0
    # for i, formula in enumerate(s.assertions()):
    #     count += 1
    #     # print("{" + str(i) + "}: {" + str(formula) + "}")
    # print("There are " + str(count) + " assertions")
    # sys.exit()


    # Constrains each cell to not denote two different digits
    for cell in cell_vars:
        for v1 in range(1,10):
            for v2 in range(v1+1,10):
                s.add(And(Or(Not(bool_vars[cell+str(v1)]),Not(bool_vars[cell+str(v2)]))))

    # Constrain each "Zone"
    # Row constraint
    # This algorithm was taken from this paper:
    # http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.94.5591&rep=rep1&type=pdf
    # It establishes the "validity" of a "zone". The zones being rows, columns, and squares
    # This is saying that that no two cells within a zone (e.g., a row) can contain the same digit
    # which are the constraints I placed in Part 1 of problem 5
    for r in range(1, 10):
        for c1 in range(1, 10):
            for c2 in range (c1 + 1, 10):
                for val in range(1, 10):
                    s.add(And(Or(Not(bool_vars[str(r) + "_" + str(c1) + "_" + str(val)]), Not(bool_vars[str(r) + "_" + str(c2) + "_" + str(val)]))))

    # Repeat for columns
    for c in range(1, 10):
        for r1 in range(1, 10):
            for r2 in range(r1+1, 10):
                for val in range(1, 10):
                    s.add(And(Or(Not(bool_vars[str(r1) + "_" + str(c) + "_" + str(val)]), Not(bool_vars[str(r2) + "_" + str(c) + "_" + str(val)]))))


    # Repeat for squares
    # each sudoku is a 9X9 broken into 3X3 squares
    for r,c in [[1,1],[4,4],[7,7]]:
        vars_to_test = []
        for m in range(0,3):
            for n in range(0,3):
                    vars_to_test.append(str(r + m) + "_" + str(c + n))

        len_of_vars = len(vars_to_test) #--> should be nine, since there are nine cells in a square
        for i in range(0, len(vars_to_test)):
            for j in range(i+1, len(vars_to_test)):
                for val in range(1,10):
                    s.add(And(Or(Not(bool_vars[str(vars_to_test[i]) + "_" + str(val)]), Not(bool_vars[str(vars_to_test[j]) + "_" + str(val)]))))


    # print(s.assertions())
    count = 0
    for i, formula in enumerate(s.assertions()):
        count += 1
        # print("{" + str(i) + "}: {" + str(formula) + "}")
    print("There are " + str(count) + " assertions")

    if s.check() == sat:
        print("sat!")

        # model = s.model()

    else:
        print("Unsat!")

    sys.exit()

    # s = Solver()

    # bool_vars = []

    # for r in range(1,10):
    #     for c in range(1, 10):
    #         for v in range(1,10):



if __name__ == '__main__':
    main(sys.argv[1:])