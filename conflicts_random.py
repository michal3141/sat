#!/usr/bin/env python
# encoding: utf-8

import sys
import matplotlib.pyplot as plt 
import numpy as np

from analyzer import FormulaAnalyzer
from collections import defaultdict, Counter
from model import Model
from random import randint

ITERS = 2000

def main():
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)
    # f.unit_propagate()

    # print 'vars_count: %d' % f.vars_count() 
    # print 'clauses_count: %d' % f.clauses_count()
    # print 'clauses/vars ratio: %f' % f.clauses_to_vars_ratio()

    # formula_info = FormulaAnalyzer(f.clauses)
    # print 'literals_count:', formula_info.count_literals()
    # print 'Variables counts: %r' % formula_info.count_variables()
    # print 'Collisions counts:', formula_info.count_collisions()

    no_of_collisions_list = []
    no_of_unsat_clauses_list = []

    for _ in xrange(ITERS):
        random_literals = Model()
        random_literals.clauses = [[clause[randint(0, len(clause)-1)]] for clause in f.clauses]
        random_literals_formula_info = FormulaAnalyzer(random_literals.clauses)
        no_of_collisions_list.append(random_literals_formula_info.count_collisions())
        no_of_unsat_clauses_list.append(random_literals_formula_info.count_unsat_clauses_1cnf())

    print 'Collisions counts after %d iterations:' % (ITERS,)
    print no_of_collisions_list
    print 'Unsat clauses counts after %d iterations:' % (ITERS,)
    print no_of_unsat_clauses_list
    print 'Minimum collision count:', min(no_of_collisions_list)
    print 'Average collision count:', float(sum(no_of_collisions_list)) / len(no_of_collisions_list)
    print 'Maximum collision count:', max(no_of_collisions_list)
    print 'Minimum unsat clauses count:', min(no_of_unsat_clauses_list)
    print 'Average unsat clauses count:', float(sum(no_of_unsat_clauses_list)) / len(no_of_unsat_clauses_list)
    print 'Maximum unsat clauses count:', max(no_of_unsat_clauses_list)

if __name__ == '__main__':
    main()