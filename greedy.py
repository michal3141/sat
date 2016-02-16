## This is a greedy approach that turns clause centric representation into literal centric one
## and greedily tries to use literal sets to cover all clauses

import sys

from collections import defaultdict
from model import Model

def _get_literal_centric_repr(f):
    d = defaultdict(set)
    for i, clause in enumerate(f.clauses):
        for lit in clause:
            d[lit].add(i)
    return d

def greedy_solve(f):
    l = _get_literal_centric_repr(f)
    # Initilize set of not covered clauses to be all clauses
    not_covered = set(range(len(f.clauses)))
    # Initialize set of chosen literals
    chosen_literals = set()

    while len(not_covered) > 0:
        maxi = -1
        for lit in l:
            if lit not in chosen_literals:
            #if lit not in chosen_literals and -lit not in chosen_literals:
                intersection_len = len(l[lit] & not_covered)
                if  intersection_len > maxi:
                    maxi = intersection_len
                    max_cover_literal = lit
        if maxi == -1:
            break

        chosen_literals.add(max_cover_literal)
        not_covered -= l[max_cover_literal]

        print 'max_cover_literal: ', max_cover_literal
        print 'not_covered: ', not_covered
    #print 'not_covered: ', not_covered
    print 'chosen_literals: ', chosen_literals

    print l

def main():
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)

    greedy_solve(f)

if __name__ == '__main__':
    main()