#!/usr/bin/env python
# encoding: utf-8

import random
import sys
import matplotlib.pyplot as plt 
import numpy as np

from analyzer import FormulaAnalyzer
from collections import defaultdict, Counter
from model import Model

def greedy(f, forbidden):
    s = set()
    for lit in f.clauses[0]:
        s.add(frozenset([lit]))

    # print s


    unvisited_clauses = set(range(1, len(f.clauses)))

    SAMPLE_SIZE = 100

    while len(unvisited_clauses) > 0:
        # print 'i:', i
        mini_clause = None
        mini = None
        mini_len = float('inf')

        for unvisited_clause in unvisited_clauses:
        #for unvisited_clause in random.sample(unvisited_clauses, SAMPLE_SIZE):
            clause = f.clauses[unvisited_clause]
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
            if len(new_s) < mini_len:
                mini_len = len(new_s)
                mini = new_s
                mini_clause = unvisited_clause

        s = mini
        print 'Expanding on clause: %r' % mini_clause
        print 'len(s):', len(s)

        unvisited_clauses.remove(mini_clause)
        # print 's:', s
    print s


def sorted(f, forbidden):
    s = set()
    for lit in f.clauses[0]:
        s.add(frozenset([lit]))

    dtype = [('clause', 'int'), ('len', 'int')]
    unvisited_clauses = np.array([(x, 0) for x in xrange(0, len(f.clauses))], dtype=dtype)

    SORTING_PERIOD = 1
    for i in xrange(1, len(f.clauses)):
        # print 'i:', i
        mini_clause = None
        mini = None
        mini_len = float('inf')
        if (i - 1) % SORTING_PERIOD == 0:
            for j in xrange(i, len(f.clauses)):
            #for unvisited_clause in random.sample(unvisited_clauses, SAMPLE_SIZE):
                clause = f.clauses[unvisited_clauses[j][0]]

                new_s = combine(s, clause, forbidden)


                unvisited_clauses[j][1] = len(new_s)
                # if len(new_s) < mini_len:
                #     mini_len = len(new_s)
                #     mini = new_s
                #     mini_clause = unvisited_clause

            print 'Sorting unvisited_clauses starting from: %d' % i
            unvisited_clauses[i:].sort(order='len')

        clause = f.clauses[unvisited_clauses[i][0]]
        print 'Expanding on clause: %r' % unvisited_clauses[i][0]
        print 'len(s):', len(s)

        s = combine(s, clause, forbidden)
        # print 's:', s
    print s

def combine(s, clause, forbidden):
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
    return new_s


def fact(n):
    if n == 0: return 1
    ret = 1
    for i in xrange(2, n+1):
        ret *= i
    return ret


def main():
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)
    # f = Model.parse_dimacs('data/5_4_2_1_0.300000.dimacs')
    # f = Model.parse_dimacs('data/random_240_1000_0.500000.dimacs')
    
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

    # sys.exit(0)

    # Evaluating on a particular variable

    clauses_copy = f.clauses[:]
    var = random.choice(list(f.vars_set()))
    print 'Evaluating on %d' % var
    f.evaluation(var)
    greedy(f, forbidden)

    f.clauses = clauses_copy
    print 'Evaluating on %d' % (-var)
    f.evaluation(-var)
    greedy(f, forbidden)

    print 'Variable chosen at random: %d' % (var) 
    # sorted(f, forbidden)

if __name__ == '__main__':
    main()
