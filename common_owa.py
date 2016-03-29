#!/usr/bin/env python
# encoding: utf-8

import sys
import matplotlib.pyplot as plt 
import numpy as np

from analyzer import FormulaAnalyzer
from collections import defaultdict, Counter
from model import Model



def graph_distribution(c):
    labels, values = zip(*[(key, val) for key, val in c.items() if key > 0])

    indexes = np.arange(len(labels))
    width = 1

    plt.bar(indexes, values, width)
    plt.xticks(indexes + width * 0.5, labels)
    plt.show()

LIMIT = 10000

def main():
    # f = Model.parse_dimacs('data/binowa1.dimacs')
    # f = Model.parse_dimacs('data/5_4_2_1_0.300000.dimacs')
    # f = Model.parse_dimacs('data/10_7_4_3_0.300000.dimacs')
    # f = Model.parse_dimacs('data/20_12_6_4_0.300000.dimacs')

    # f = Model.parse_dimacs('data/random_100_1000_0.500000.dimacs')
    # f = Model.parse_dimacs('data/random_170_1000_0.500000.dimacs')
    # f = Model.parse_dimacs('data/random_200_1000_0.500000.dimacs')
    # f = Model.parse_dimacs('data/random_220_1000_0.500000.dimacs')
    # f = Model.parse_dimacs('data/random_230_1000_0.500000.dimacs')
    # f = Model.parse_dimacs('data/random_240_1000_0.000000.dimacs')
    # f = Model.parse_dimacs('data/random_240_1000_0.200000.dimacs')
    # f = Model.parse_dimacs('data/random_240_1000_0.500000.dimacs')
    # f = Model.parse_dimacs('data/random_240_1000_0.800000.dimacs')
    f = Model.parse_dimacs('data/random_240_1000_1.000000.dimacs')
    # f = Model.parse_dimacs('data/random_250_1000_0.500000.dimacs')
    # f = Model.parse_dimacs('data/random_500_1000_0.500000.dimacs')
    

    d = defaultdict(int)
    c = Counter()
    positive_counter = Counter()
    avg_positive_count = 0
    positive_vec = []

    occurences_counter = 0

    formula_info = FormulaAnalyzer(f.clauses)
    print 'literals_count:', formula_info.count_literals()
    variables_count = formula_info.count_variables()
    print 'Variables counts: %r' % variables_count

    l = len(set([abs(x) for x in variables_count.keys()]))
    for i in xrange(l):
        positive_counter[i] = 0

    fixed_set = set()

    total_count = 0
    # Number of auxiliary variables that are appearing set the same way (fixed) in all satisfying assignments
    fixed_set_count = 0

    # Propagating units and adding units as clauses
    # f.unit_propagate()

    # print 'After unit propagation:'
    # print f.clauses

    # for unit in f.all_units:
    #     f.clauses.append([unit])

    # print 'number of propagated units: ', len(f.all_units)

    for solution in f.itersolve():
        sol_tpl = tuple(solution)
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

        if total_count > LIMIT:
            break
        # print solution

    if total_count == 0:
        print 'UNSAT'
        sys.exit(-1)

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
    print 'positive vars expected percentage:', positive_vec_mean / float(l)
    
    graph_distribution(positive_counter)

    graph_distribution(c)

    # fixed_set_minus_all_units = fixed_set - f.all_units
    # print 'fixed_set - f.all_units:', fixed_set_minus_all_units

    # for lit in fixed_set_minus_all_units:
    #     f.evaluation(lit)

    # f.unit_propagate()

    # print 'After unit propagation and taking advantage of fixed set:'
    # print f.clauses



    print 'positive_counter:', positive_counter

if __name__ == '__main__':
    main()