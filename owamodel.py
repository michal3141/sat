from ilpmodel import ILPModel 
from functools import partial
import sys

def _get_line(f):
    return map(int, f.readline().strip().split())

class OWAModel(ILPModel):
    @staticmethod
    def solvefile(filename):
        with open(filename, 'r') as f:
            n, m, K = _get_line(f)
            alpha = _get_line(f)
            u = []
            for _ in xrange(n):
                u.append(_get_line(f))

        print 'n=%d, m=%d, K=%d' % (n, m, K)
        print 'alpha=%r' % alpha
        print 'u=%r' % u

        model = OWAModel(length=10)
        y = [model.add_var('y' + str(j)) for j in xrange(m)]
        x = [[[model.add_var('x' + str(i) + '|' + str(j) + '|' + str(k)) for k in xrange(K)] for j in xrange(m)] for i in xrange(n)]

        # (a) Exactly K candidates are chosen
        sum([1*yy for yy in y]) == K

        # (b)
        for i in xrange(n):
            for j in xrange(m):
                for k in xrange(K):
                    model.add_clause([~x[i][j][k], y[j]])

        # (c) Only 1 candidate is ranked as k-th best
        for i in xrange(n):
            for k in xrange(K):
                model.exactly_one_of([x[i][j][k] for j in xrange(m)])

        # (d) Item 'j' is ranked precisly on one position for 'i'
        for i in xrange(n):
            for j in xrange(m):
                model.at_most_one_of([x[i][j][k] for k in xrange(K)])

        # (e)
        for i in xrange(n):
            for k in xrange(K-1):
                sum([u[i][j]*x[i][j][k] for j in xrange(m)]) >= sum([u[i][j]*x[i][j][k+1] for j in xrange(m)]) 

        # (objective)
        solution, max_val = model.maximize(sum([(alpha[k]*u[i][j])*x[i][j][k] for i in xrange(n) for j in xrange(m) for k in xrange(K)]), lb=0, ub=500)
        print max_val
        
        # Getting solution - finally !
        if solution != 'UNSAT':
            print 'y=%r' % [model.get_binary_value(y[j], solution) for j in xrange(m)]
            print 'x=%r' % [[[model.get_binary_value(x[i][j][k], solution) for k in xrange(K)] for j in xrange(m)] for i in xrange(n)]
        else:
            print 'UNSAT'

        return model


def main():
    #trivial = OWAModel.solvefile('owa/trivial')
    #print trivial
    #owa1 = OWAModel.solvefile('owa/owa1')
    owa2 = OWAModel.solvefile('owa/owa2')
    owa2.save_dimacs('data/owa2.dimacs')
    # owa3 = OWAModel.solvefile('owa/owa3')
    # owa3.save_dimacs('data/owa3.dimacs')
    #print owa1
if __name__ == '__main__':
    main()