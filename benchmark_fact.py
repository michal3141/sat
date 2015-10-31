import sys
from factmodel import FactorizationModel
from sympy.ntheory import factorint
from time import time

def factors_count(number):
    return sum(factorint(number).values())

def main():
    start = int(sys.argv[1])
    try: end = int(sys.argv[2])
    except: end = start
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

        print 'Time for building: %f, Time for solving: %f, # of factors: %d, # of vars: %d, # of clauses: %d' % (
            build_model_duration, 
            solve_model_duration,
            factors_count(number),
            sat.vars_count(),
            sat.clauses_count()
        )
        if solution != 'UNSAT':
            factor1 = sat.get_decimal_value(P, solution)
            factor2 = sat.get_decimal_value(Q, solution)
            print '%d = %d * %d' % (number, factor1, factor2)
            if factor1 * factor2 != number:
                raise Exception("Bad factorization!")
        else:
            if factors_count(number) > 1:
                raise Exception("Number should not be treated as prime!")
            print '%d is prime' % number
        print '---------------------------------'
        i += 1

if __name__ == '__main__':
    main()