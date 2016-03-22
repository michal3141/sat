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

    f.unit_propagate()
    # print 'units:', f.all_units
    # print 'clauses:', f.clauses

    while True:
        if f.clauses == []:
            print 'SAT'
            break
        elif f.clauses == [[]]:
            print 'UNSAT'
            break

        orig_units = f.all_units
        all_diff_units_common = set()
        for var in f.vars_set():
            diff_units_list = []
            for lit in [-var, var]:
                fc = Model()
                fc.clauses = f.clauses[:]
                fc.all_units = f.all_units.copy()
                fc.evaluation(lit)
                fc.unit_propagate()
                diff_units = fc.all_units - orig_units
                # print 'units on %r = %r' % (lit, diff_units)
                diff_units_list.append(diff_units)
            diff_units_common = diff_units_list[0] & diff_units_list[1]
            # print 'common units on %r = %r' % (var, diff_units_common)
            all_diff_units_common |= diff_units_common

        # print 'all_diff_units_common:', all_diff_units_common

        for lit in all_diff_units_common:
            f.evaluation(lit)
            f.unit_propagate()
            # print 'clauses after evaluating', lit, ':', f.clauses
        # print 'clauses:', f.clauses

        if len(all_diff_units_common) == 0:
            print len(f.clauses)
            
            forbidden = set()
            for clause in f.clauses:
                set_from_clause = set()
                for lit in clause:
                    forbidden.add(frozenset([lit, -lit]))
                    set_from_clause.add(-lit)
                forbidden.add(frozenset(set_from_clause))

            print 'forbidden:', forbidden

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

            break

            # while True:

            #     f.unit_propagate()
            #     f.superset_elimination()

            #     print 'len(f.clauses):', len(f.clauses)
            #     # print 'f.clauses:', f.clauses


            #     if f.clauses == []:
            #         print 'SAT'
            #         break
            #     elif f.clauses == [[]]:
            #         print 'UNSAT'
            #         break

            #     formula_info = FormulaAnalyzer(f.clauses)
            #     variables_count = formula_info.count_variables()

            #     minimal_product = float('inf')

            #     escape = True

            #     for k in variables_count.keys():
            #         kp = abs(k)
            #         km = -kp
            #         try:
            #             positive_k = variables_count[kp]
            #         except:
            #             positive_k = 0
            #         try:
            #             negative_k = variables_count[km]
            #         except:
            #             negative_k = 0

            #         if negative_k <= 1 or positive_k <= 1:
            #             escape = False

            #         product_k = negative_k * positive_k

            #         # print k, negative_k, positive_k, product_k

            #         if product_k < minimal_product:
            #             minimal_product = product_k
            #             resolution_var = kp
         
            #     if escape:
            #         break

            #     print 'Applying resolution on %d with product %d' % (resolution_var, minimal_product)
            #     f.resolution(resolution_var)


if __name__ == '__main__':
    main()