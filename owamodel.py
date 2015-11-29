from ilpmodel import ILPModel 
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

        #model = OWAModel(length=len(bin(K)[2:])+1)
        model = OWAModel(length=10)
        y = [model.add_bin() for i in xrange(m)]
        x = [[[model.add_bin() for k in xrange(K)] for j in xrange(m)] for i in xrange(n)]

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
        # for i in xrange(n):
        #     for j in xrange(m):
        #         sum([x[i][j][k] for k in xrange(K)]) == 1

        # (e)
        for i in xrange(n):
            for k in xrange(K-1):
                sum([u[i][j]*x[i][j][k] for j in xrange(m)]) >= sum([u[i][j]*x[i][j][k+1] for j in xrange(m)]) 
        
        sum([(alpha[k]*u[i][j])*x[i][j][k] for i in xrange(n) for j in xrange(m) for k in xrange(K)]) == 42

        solution = model.solve()
        if solution != 'UNSAT':
            for yy in y:
                print model.get_decimal_value(yy, solution),
        else:
            print 'UNSAT'

        # (objective)
        #sol, max_val = model.maximize(sum([(alpha[k]*u[i][j])*x[i][j][k] for i in xrange(n) for j in xrange(m) for k in xrange(K)]), lb=0, ub=100)
        #print max_val
        
        return model


def main():
    owa1 = OWAModel.solvefile('owa/owa1')
    #print owa1
if __name__ == '__main__':
    main()