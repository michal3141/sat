import sys
from matplotlib import pyplot as plt
from analyzer import FormulaAnalyzer
from factmodel import FactorizationModel
from sympy.ntheory import factorint
from time import time

def factors_count(number):
    return sum(factorint(number).values())

def main():
    start = int(sys.argv[1])
    try: end = int(sys.argv[2])
    except: end = start
    x_range = range(start, end+1)
    y_range = []
    p_range = []
    i = start
    while i <= end:
        build_model_start = time()
        sat = FactorizationModel()
        number = i
        bin_number = bin(number)[2:]
        len_bin_number = len(bin_number)
        N = sat.add_integer('N', number, length=len_bin_number)
        l = len(N)
        P = sat.add_seq('P', l)
        Q = sat.add_seq('Q', l)
        sat.add_multiplication(P, Q, N)
        build_model_duration = time() - build_model_start

        solve_model_start = time()
        solution = sat.solve()
        solve_model_duration = time() - solve_model_start

        formula_info = FormulaAnalyzer(sat.clauses)

        print 'Time for building: %f, Time for solving: %f, # of factors: %d, # of vars: %d, # of clauses: %d' % (
            build_model_duration, 
            solve_model_duration,
            factors_count(number),
            sat.vars_count(),
            sat.clauses_count()
        )
        # print sat
        # print 'Variables counts: %r' % formula_info.count_variables()
        collisions_count = formula_info.count_collisions()
        y_range.append(collisions_count)
        print 'Collision count: %d' % collisions_count

        if solution != 'UNSAT':
            p_range.append(0)
            factor1 = sat.get_decimal_value(P, solution)
            factor2 = sat.get_decimal_value(Q, solution)
            print '%d = %d * %d' % (number, factor1, factor2)
            if factor1 * factor2 != number:
                raise Exception("Bad factorization!")
        else:
            p_range.append(1)
            if factors_count(number) > 1:
                raise Exception("Number should not be treated as prime!")
            print '%d is prime' % number
        print '---------------------------------'
        i += 1

    plt.title('Collisions count')
    plt.xlabel('N')
    plt.ylabel('Collisions')
    plt.scatter(x_range, y_range, c=p_range, cmap='gray')
    plt.show()

if __name__ == '__main__':
    main()