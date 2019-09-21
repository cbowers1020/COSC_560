'z3 demo using graph coloring'

from z3 import *

def main():
    'main entry point'

    s = Solver()

    colors = ['r', 'g', 'b', 'y']

    # make boolean variables
    v0 = [Bool(f'v0_{c}') for c in colors]
    v1 = [Bool(f'v1_{c}') for c in colors]
    v2 = [Bool(f'v2_{c}') for c in colors]
    v3 = [Bool(f'v3_{c}') for c in colors]
    v4 = [Bool(f'v4_{c}') for c in colors]

    vertices = [v0, v1, v2, v3, v4]

    # If(v1[0], And(Not(v1[1]), v1[2], v1[3]))

    # each vertex has at most one color
    for vertex_vars in vertices:
        for color1 in vertex_vars:
            for color2 in vertex_vars:
                if color1 is color2:
                    continue
                
                s.add(Implies(color1, Not(color2)))

    # each vertex has at least one color
    for vertex_vars in vertices:
        expr = vertex_vars[0]

        for color in vertex_vars[1:]:
            expr = Or(expr, color)

        s.add(expr)

    # edge constraints
    edges = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3], [0, 4], [1, 4], [3, 4]]

    for edge in edges:
        a, b = edge
        
        # vertices[a] -> !vertices[b] and vertices[b] -> !vertices[a]
        for color_a, color_b in zip(vertices[a], vertices[b]):
            s.add(Implies(color_a, Not(color_b)))
            s.add(Implies(color_b, Not(color_a)))

    s.add(vertices[0][0]) # make vertex 0 red

    if s.check() == sat:
        print("sat!")

        model = s.model()

        for vertex_vars in vertices:
            for color in vertex_vars:
                if model[color]:
                    print(color)

    else:
        print("unsat")

    
    # print all added assertions
    
    #for i, formula in enumerate(s.assertions()):
    #    print(f"{i}: {formula}")

if __name__ == '__main__':
    main()
    
