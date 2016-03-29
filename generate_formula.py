#!/usr/bin/env python

## ./generate_formula.py <number_of_variables> <number_of_clauses> <probability of a positive literal> 

from model import Model
from random import random, randint
import sys


def main():

    if len(sys.argv) != 4:
        print 'usage: ./generate_formula.py <number_of_variables> <number_of_clauses> <probability of a positive literal>'
        sys.exit(-1)

    f = Model()
    num_of_vars = int(sys.argv[1])
    num_of_clauses =  int(sys.argv[2])
    probability_of_positive_literal = float(sys.argv[3])

    for i in xrange(num_of_clauses):
        # Creating 3 SAT instances
        clause = []
        for _ in xrange(3):
            lit = randint(1, num_of_vars)
            if random() >= probability_of_positive_literal:
                lit = (-lit)
            clause.append(lit)
        f.clauses.append(clause)

    print f.clauses
    f.save_dimacs('data/random_%d_%d_%f.dimacs' % (num_of_vars, num_of_clauses, probability_of_positive_literal))

if __name__ == '__main__':
    main()