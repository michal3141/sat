#!/usr/bin/env python
# encoding: utf-8

import sys
from matplotlib import pyplot as plt
from analyzer import FormulaAnalyzer
from factmodel import FactorizationModel
from sympy.ntheory import factorint
from time import time
from xor_converter import solve_xor, solve_or

def factors_count(number):
    return sum(factorint(number).values())
    return 0

def count_0s(number):
    count = 0
    for digit in bin(number)[2:]: 
        if digit == '0': count += 1
    return count

def main():
    start = int(sys.argv[1])
    try: end = int(sys.argv[2])
    except: end = start
    x_range = range(start, end+1)
    y_range = []
    p_range = []
    #count_0s_range = []
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
        sat.add_multiplication_without_trivial_factors(P, Q, N)
        build_model_duration = time() - build_model_start

        #sat.unit_propagate()
        for j in [1, 42]:
            sat.resolution(j)
            print 'resolution: %d' % j
            print sat.clauses

        solve_model_start = time()
        solution = sat.solve()
        solve_model_duration = time() - solve_model_start

        sat.save_dimacs('data/%d.dimacs' % i)

        formula_info = FormulaAnalyzer(sat.clauses)

        #print sat.clauses
        print 'Time for building: %f, Time for solving: %f, # of factors: %d, # of vars: %d, # of clauses: %d' % (
            build_model_duration, 
            solve_model_duration,
            factors_count(number),
            sat.vars_count(),
            sat.clauses_count()
        )

        print 'Variables counts: %r' % formula_info.count_variables()
        literals_count = formula_info.count_literals()
        #print 'Literal counts: %r' % literals_count
        try:
            print 'Positive/negative ratio: %f' % (literals_count['positive'] / float(literals_count['negative']))
        except ZeroDivisionError:
            print 'Number of negative literals is 0'
            
        collisions_count = formula_info.count_collisions()
        y_range.append(collisions_count)
        print 'Collision count: %d' % collisions_count

        #count_0s_range.append(count_0s(i) + y_range[0] - count_0s(start))

        sat_xor, solution_xor = solve_xor(sat)
        # sat_or, solution_or = solve_or(sat)
        print 'XOR SAT: %r' % sat_xor
        # print 'OR SAT: %r' % sat_or

        # if sat_xor:
        #     print "Amazing ! - we've got a satisfiable XOR extension"

        # if solution != 'UNSAT':
        #     p_range.append(0)
        #     factor1 = sat.get_decimal_value(P, solution)
        #     factor2 = sat.get_decimal_value(Q, solution)
        #     print '%d = %d * %d' % (number, factor1, factor2)
        #     if factor1 * factor2 != number:
        #         raise Exception("Bad factorization!")
        #     if factor1 == 1 or factor2 == 1:
        #         raise Exception("1 should not appear in prime factorization!")
        # else:
        #     p_range.append(1)
        #     if factors_count(number) > 1:
        #         raise Exception("Number should not be treated as prime!")
        #     print '%d is prime' % number
        print '---------------------------------'
        i += 1

    plt.title('Collisions count')
    plt.xlabel('N')
    plt.ylabel('Collisions')
    plt.scatter(x_range, y_range, c=p_range, cmap='gray')
    #plt.scatter(x_range, count_0s_range, c='red')
    plt.show()

if __name__ == '__main__':
    main()
