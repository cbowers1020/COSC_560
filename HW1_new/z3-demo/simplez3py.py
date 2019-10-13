'z3 demo using graph coloring'

from z3 import *

def main():
    'main entry point'

    p = Bool('p')

    s = Solver()

    s.add(Or(p, Not(p)))

    s.add(p)

    if s.check() == sat:
        print("sat!")

        print(f"model: {s.model()}")
        print(f"p = {s.model()[p]}")
    else:
        print("unsat")

if __name__ == '__main__':
    main()
    
