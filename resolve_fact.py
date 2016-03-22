#!/usr/bin/env python
# encoding: utf-8

import sys
import matplotlib.pyplot as plt 
import numpy as np

from analyzer import FormulaAnalyzer
from collections import defaultdict, Counter
from model import Model


def main():
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)

    products = []
    number_of_clauses = []
    x_range = []
    i = 0

    l = len(bin(int(n))[2:])


    # for i in xrange(1, 3*l+1):
    #     i += 1
    #     x_range.append(i)
        
    #     number_of_clauses.append(len(f.clauses))

    #     f.resolution(i)
    #     f.unit_propagate()
    #     f.superset_elimination()

    #     print 'len(f.clauses):', len(f.clauses)

    # print 'f.clauses after resolving N, P, Q variables:', f.clauses

    while True:
        i += 1

        f.unit_propagate()
        f.superset_elimination()

        x_range.append(i)
        number_of_clauses.append(len(f.clauses))

        print 'len(f.clauses):', len(f.clauses)
        # print 'f.clauses:', f.clauses


        if f.clauses == []:
            print 'SAT'
            break
        elif f.clauses == [[]]:
            print 'UNSAT'
            break

        formula_info = FormulaAnalyzer(f.clauses)
        variables_count = formula_info.count_variables()

        minimal_product = float('inf')

        # print 'variables_count:', variables_count
        for k in variables_count.keys():
            kp = abs(k)
            km = -kp
            try:
                positive_k = variables_count[kp]
            except:
                positive_k = 0
            try:
                negative_k = variables_count[km]
            except:
                negative_k = 0
            product_k = negative_k * positive_k

            # print k, negative_k, positive_k, product_k

            if product_k < minimal_product:
                minimal_product = product_k
                resolution_var = kp
 
        products.append(minimal_product)

        print 'Applying resolution on %d with product %d' % (resolution_var, minimal_product)
        f.resolution(resolution_var)


    # print 'Variables counts: %r' % formula_info.count_variables()

    # plt.scatter(x_range[:-1], products)
    plt.scatter(x_range, number_of_clauses)
    plt.show()

if __name__ == '__main__':
    main()