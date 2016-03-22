#!/usr/bin/env python
# encoding: utf-8

import sys
import matplotlib.pyplot as plt 
import numpy as np

from analyzer import FormulaAnalyzer
from collections import defaultdict, Counter
from model import Model


def fact(n):
    if n == 0: return 1
    ret = 1
    for i in xrange(2, n+1):
        ret *= i
    return ret


def main():
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)
    total_conflicts_count = 0

    f.unit_propagate()

    if f.clauses == []:
        print 'SAT'
        sys.exit(0)
    elif f.clauses == [[]]:
        print 'UNSAT'
        sys.exit(0)

    print 'f.clauses:', f.clauses

    forbidden = set()
    for clause in f.clauses:
        set_from_clause = set()
        for lit in clause:
            forbidden.add(frozenset([lit, -lit]))
            set_from_clause.add(-lit)
        forbidden.add(frozenset(set_from_clause))

    print 'forbidden:', forbidden

    formula_info = FormulaAnalyzer(f.clauses)
    variables_count = formula_info.count_variables()
    print 'Variables counts: %r' % variables_count

    # Gathering info about conflicts
    for clause in forbidden:
        mult = 1
        for lit in clause:
            mult *= variables_count[lit]
        mult /= fact(len(clause))
        print clause, ':', mult
        total_conflicts_count += mult

    print 'total_conflicts_count:', total_conflicts_count

    sys.exit(0)

    s = set()
    for lit in f.clauses[0]:
        s.add(frozenset([lit]))

    # print s

    for i in xrange(1, len(f.clauses)):
        print 'i:', i
        clause = f.clauses[i]
        new_s = set()
        for lit in clause:
            for seq in s:
                new_seq = seq | frozenset([lit])
                for forbid in forbidden:
                    if forbid <= new_seq:
                        # print 'Forbidden clause:', forbid, 'detected inside of:', new_seq
                        break
                else:
                    for nseq in new_s:
                        if nseq <= new_seq:
                            break
                    else:
                        new_s.add(new_seq)
        s = new_s
        print 'len(s):', len(s)
        # print 's:', s

    print s

if __name__ == '__main__':
    main()