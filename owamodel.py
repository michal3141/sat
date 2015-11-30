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

        #model = OWAModel(length=len(bin(K)[2:])+1)
        model = OWAModel(length=10)
        y = [model.add_bin() for j in xrange(m)]
        x = [[[model.add_bin() for k in xrange(K)] for j in xrange(m)] for i in xrange(n)]

        # print 'len(x[0][0][0])', len(x[0][0][0])
        #print 'type of sum(y) is:', type(sum(y))
        # (a) Exactly K candidates are chosen
        sum(y) == K

        # (b)
        for i in xrange(n):
            for j in xrange(m):
                for k in xrange(K):
                    model.add_clause([~x[i][j][k][0], y[j][0]])
                    #x[i][j][k] <= y[j]

        # (c) Only 1 candidate is ranked as k-th best
        for i in xrange(n):
            for k in xrange(K):
                 sum([x[i][j][k] for j in xrange(m)]) == 1
        
        # (d) Item 'j' is ranked precisly on one position for 'i'
        for i in xrange(n):
            for j in xrange(m):
                sum([x[i][j][k] for k in xrange(K)]) <= 1

        # (e)
        for i in xrange(n):
            for k in xrange(K-1):
                sum([u[i][j]*x[i][j][k] for j in xrange(m)]) >= sum([u[i][j]*x[i][j][k+1] for j in xrange(m)]) 
        
        # sum([(alpha[k]*u[i][j])*x[i][j][k] for i in xrange(n) for j in xrange(m) for k in xrange(K)]) == int(sys.argv[1])
        # solution = model.solve()

        # (objective)
        solution, max_val = model.maximize(sum([(alpha[k]*u[i][j])*x[i][j][k] for i in xrange(n) for j in xrange(m) for k in xrange(K)]), lb=0, ub=77)
        print max_val
        
        # Getting solution - finally !
        if solution != 'UNSAT':
            print 'y=%r' % [model.get_decimal_value(y[j], solution) for j in xrange(m)]
            print 'x=%r' % [[[model.get_decimal_value(x[i][j][k], solution) for k in xrange(K)] for j in xrange(m)] for i in xrange(n)]
        else:
            print 'UNSAT'

        return model


def main():
    #trivial = OWAModel.solvefile('owa/trivial')
    #print trivial
    owa1 = OWAModel.solvefile('owa/owa1')
    #print owa1
if __name__ == '__main__':
    main()