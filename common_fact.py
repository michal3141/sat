#!/usr/bin/env python
# encoding: utf-8

import sys
import matplotlib.pyplot as plt 
import numpy as np

from analyzer import FormulaAnalyzer
from collections import defaultdict, Counter
from model import Model


def _number_of_vars(n):
    return 4*n*n+3*n-1


def types_of_variables(n):
    print 'N', '1->%d' % n
    print 'P', '%d->%d' % (n+1, 2*n)
    print 'Q', '%d->%d' % (2*n+1, 3*n)
    print 'S', '%d->%d' % (3*n+1, n*n+3*n)
    print 'C', '%d->%d' % (n*n+3*n+1, 2*n*n+3*n-1)
    print 'M', '%d->%d' % (2*n*n+3*n, 3*n*n+3*n-1)
    print 'R', '%d->%d' % (3*n*n+3*n, 4*n*n+3*n-1)


def graph_distribution(c):
    labels, values = zip(*[(key, val) for key, val in c.items() if key > 0])

    indexes = np.arange(len(labels))
    width = 1

    plt.bar(indexes, values, width)
    plt.xticks(indexes + width * 0.5, labels)
    plt.show()


def main():
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)
    d = defaultdict(int)
    c = Counter()
    positive_counter = Counter()
    avg_positive_count = 0
    positive_vec = []

    occurences_counter = 0
    intn = int(n)

    l = len(bin(intn)[2:])
    for i in xrange(4*l*l+3*l-1):
        positive_counter[i] = 0

    specific_clauses = f.clauses[:l-1]
    f.clauses = f.clauses[l-1:]

    fixed_set = set()

    total_count = 0
    # Number of auxiliary variables that are appearing set the same way (fixed) in all satisfying assignments
    fixed_set_count = 0

    # Propagating units and adding units as clauses
    # f.unit_propagate()

    # print 'After unit propagation:'
    # print f.clauses

    # for unit in f.all_units:
    #     if abs(unit) >= l:
    #         f.clauses.append([unit])

    # print 'number of propagated units: ', len(f.all_units)

    print 'specific_clauses: ', specific_clauses
    for solution in f.itersolve():
        sol_tpl = tuple(solution[l:])
        # sol_tpl = tuple(solution)
        d[sol_tpl] += 1
        positive_count = len([x for x in sol_tpl if x > 0])
        positive_vec.append(positive_count)

        avg_positive_count += positive_count
        positive_counter[positive_count] += 1
        for elem in sol_tpl:
            c[elem] += 1
            if -elem not in c:
                c[-elem] = 0
        total_count += 1
        # print solution

    for k, v in d.iteritems():
         # print k, ':', v
         pass
    
    print 'len(d):', len(d) 
    print 'total_count:', total_count
    print 'most_common:'
    for k, v in c.most_common():
        # print k, ':', v
        if v == total_count:
            fixed_set.add(k)
            fixed_set_count += 1
    print 'fixed_set_count:', fixed_set_count
    print 'all_literals_count:', (len(c.keys()) + fixed_set_count) / 2

    fixed_set_positive_count = len([x for x in fixed_set if x > 0])
    print 'fixed_set_positive_count:', fixed_set_positive_count

    print 'Average number of positive literals in solution:', float(avg_positive_count) / total_count
    print 'min:', np.min(positive_vec)
    print 'median:', np.median(positive_vec)
    positive_vec_mean = np.mean(positive_vec)
    print 'avg:', positive_vec_mean
    print 'max:', np.max(positive_vec)
    print 'std:', np.std(positive_vec)
    print 'positive vars expected precentage:', positive_vec_mean / _number_of_vars(l)

    graph_distribution(positive_counter)

    types_of_variables(l)
    graph_distribution(c)

    # fixed_set_minus_all_units = fixed_set - f.all_units
    # print 'fixed_set - f.all_units:', fixed_set_minus_all_units

    # for lit in fixed_set_minus_all_units:
    #     f.evaluation(lit)

    # f.unit_propagate()

    # print 'After unit propagation and taking advantage of fixed set:'
    # print f.clauses

    formula_info = FormulaAnalyzer(f.clauses)
    print 'literals_count:', formula_info.count_literals()
    print 'Variables counts: %r' % formula_info.count_variables()

    print 'positive_counter:', positive_counter

if __name__ == '__main__':
    main()