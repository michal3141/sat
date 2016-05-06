#!/usr/bin/env python
# encoding: utf-8

import sys
import matplotlib.pyplot as plt 
import numpy as np

from analyzer import FormulaAnalyzer
from collections import defaultdict, Counter
from model import Model


def _get_decimal_value(l):
    total = 0
    multiplier = 1
    for e in l:
        if e > 0:
            total += multiplier
        multiplier *= 2
    return total


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

    print 'clauses/vars ratio: %f' % f.clauses_to_vars_ratio()

    # Converting to SAT-3CNF
    # print f
    # print 'Before conversion to SAT-3CNF:', f.clauses
    # f.to_3cnf()
    # print 'After conversion to SAT-3CNF:', f.clauses
    # sys.exit(0)

    d = defaultdict(int)
    c = Counter()
    positive_counter = Counter()
    avg_positive_count = 0
    positive_vec = []
    decimals = defaultdict(list)

    odd_clauses_count = [0] * len(f.clauses)
    even_clauses_count = [0] * len(f.clauses)

    occurences_counter = 0
    intn = int(n)

    l = len(bin(intn)[2:])
    for i in xrange(4*l*l+3*l-1):
        positive_counter[i] = 0

    specific_clauses = f.clauses[:l-1]
    # f.clauses = f.clauses[l-1:]

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

    parity_to_assignment = defaultdict(list)

    print 'specific_clauses: ', specific_clauses
    for solution in f.itersolve():
        decval_n = _get_decimal_value(solution[:l])
        decval_p = _get_decimal_value(solution[l:2*l])
        decval_q = _get_decimal_value(solution[2*l:3*l])
        # print decval_n
        # sol_tpl = tuple(solution[l:])
        sol_tpl = tuple(solution)
        sol_set = set(solution)

        d[sol_tpl] += 1
        positive_count = len([x for x in sol_tpl if x > 0])
        positive_vec.append(positive_count)
        decimals[positive_count].append((decval_n, decval_p, decval_q))

        total_odd = 0
        total_even = 0
        parity_str = ""

        for i, clause in enumerate(f.clauses):
            number_of_lits_in_sol = 0
            for lit in clause:
                if lit in sol_set:
                    number_of_lits_in_sol += 1
            if number_of_lits_in_sol % 2 == 0:
                parity_str += '0'
                total_even += 1
                even_clauses_count[i] += 1
            else:
                parity_str += '1'
                total_odd += 1
                odd_clauses_count[i] += 1

        parity_to_assignment[parity_str].append(sol_tpl)
        # print 'odd: %d, even: %d' % (total_odd, total_even)


        avg_positive_count += positive_count
        positive_counter[positive_count] += 1
        for elem in sol_tpl:
            c[elem] += 1
            if -elem not in c:
                c[-elem] = 0
        total_count += 1
        # print solution

    print 'Parity to assignment::'
    for k, v in parity_to_assignment.iteritems():
        print k, '-->', v

    print '# of distinct xorified formulas covering solution space: %d' % len(parity_to_assignment.keys())
    sys.exit(0)

    xor_clauses_file = open('xor_clauses_%d.cnf' % intn, 'w')
    always_odd_or_even_count = 0
    unit_clauses_count = 0
    for i, clause in enumerate(f.clauses):
        if len(clause) == 1:
            unit_clauses_count += 1
        if odd_clauses_count[i] == 0:
            always_odd_or_even_count += 1
            xor_clauses_file.write('x')
            xor_clauses_file.write(str(-clause[0]) + ' ')
            for j in xrange(1, len(clause)):
                xor_clauses_file.write(str(clause[j]) + ' ')
            xor_clauses_file.write('0\n')
        elif even_clauses_count[i] == 0:
            xor_clauses_file.write('x')
            for j in xrange(len(clause)):
                xor_clauses_file.write(str(clause[j]) + ' ')
            xor_clauses_file.write('0\n')
            always_odd_or_even_count += 1
        else:
            for j in xrange(len(clause)):
                xor_clauses_file.write(str(clause[j]) + ' ')
            xor_clauses_file.write('0\n')

        print '%d, odd: %d, even: %d' % (i, odd_clauses_count[i], even_clauses_count[i])

    print 'Percentage of always odd or even (crypto clauses): %f ' % (100 * float(always_odd_or_even_count) / len(f.clauses),) 
    print 'Percentage of unit clauses (with one literal only): %f ' % (100 * float(unit_clauses_count) / len(f.clauses),) 
    xor_clauses_file.close()

    sys.exit(0)

    for k, v in d.iteritems():
         # print k, ':', v
         pass

    for k in sorted(decimals):
        print k, ':', ['%d=%d*%d' % (x[0], x[1], x[2]) for x in decimals[k]] # [bin(x)[2:] for x in reversed(sorted(decimals[k]))]
    

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
    print 'positive vars expected percentage:', positive_vec_mean / _number_of_vars(l)

    # sys.exit(0)
    
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