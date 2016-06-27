#!/usr/bin/env python
# encoding: utf-8

import random
import sys
import matplotlib.pyplot as plt 
import numpy as np

from analyzer import FormulaAnalyzer
from collections import defaultdict, Counter
from model import Model

d = defaultdict(int)
total_conflicts_count = 0

def count_literals_top_line(f):
    global d
    for clause in f.clauses:
        print clause
        d[clause[0]] += 1

def calculate_conflicts_count(f):
    global d, total_conflicts_count
    total_conflicts_count = 0
    for k in d.keys():
        if k > 0:
            print 'k=%d d[%d]=%d d[-%d]=%d' % (k, k, d[k], k, d[-k])
            total_conflicts_count += (d[k] * d[-k])

def shuffle(f):
    for i in xrange(len(f.clauses)):
        maxi = len(f.clauses[i]) - 1
        rand = random.randint(0, maxi)
        f.clauses[i][0], f.clauses[i][rand] = f.clauses[i][rand], f.clauses[i][0]

def swap_first_to_decrease_conflicts_count(f):
    global d, total_conflicts_count
    min_swap_balance = 0
    min_i = 0
    min_j = 0
    for i in xrange(len(f.clauses)):
        for j in xrange(1, len(f.clauses[i])):
            # Calculating potential swap gain...
            curr = f.clauses[i][0]
            swapped = f.clauses[i][j]
            loss = -d[-curr]
            gain = d[-swapped]
            swap_balance = loss + gain
            if swap_balance < min_swap_balance:
                min_swap_balance = swap_balance
                min_i = i
                min_j = j

    if min_swap_balance < 0:
        total_conflicts_count += min_swap_balance
        print 'Performing swap in clause %d: %d <-> %d' % (min_i, f.clauses[min_i][0], f.clauses[min_i][min_j])
        print 'total_conflicts_count: %d' % total_conflicts_count
        curr = f.clauses[min_i][0]
        swapped = f.clauses[min_i][min_j]
        f.clauses[min_i][0], f.clauses[min_i][min_j] = f.clauses[min_i][min_j], f.clauses[min_i][0]
        d[curr] -= 1
        d[swapped] += 1
        return total_conflicts_count

    return None


def main():
    global d, total_conflicts_count
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)
    f.unit_propagate()
    if f.clauses == [[]]:
        print 'UNSAT'
        sys.exit(0)

    shuffle(f)

    print 'f:', f
    count_literals_top_line(f)
    print 'd:', d
    calculate_conflicts_count(f)
    print 'total_conflicts_count:', total_conflicts_count

    while True:
        ret_val = swap_first_to_decrease_conflicts_count(f)
        if ret_val is None:
            break

    calculate_conflicts_count(f)

if __name__ == '__main__':
    main()