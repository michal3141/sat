from ilpmodel import ILPModel 
from functools import partial
import sys

def _get_line(f):
    return map(int, f.readline().strip().split())

def _parse_owa_file(filename):
    with open(filename, 'r') as f:
        n, m, K = _get_line(f)
        alpha = _get_line(f)
        u = []
        for _ in xrange(n):
            u.append(_get_line(f))

    print 'n=%d, m=%d, K=%d' % (n, m, K)
    print 'alpha=%r' % alpha
    print 'u=%r' % u
    return (n, m, K, alpha, u)

def _print_owa_solution(model, solution, x, y, n, m, K):
    # Getting solution - finally !
    if solution != 'UNSAT':
        print 'y=%r' % [model.get_binary_value(y[j], solution) for j in xrange(m)]
        print 'x=%r' % [[[model.get_binary_value(x[i][j][k], solution) for k in xrange(K)] for j in xrange(m)] for i in xrange(n)]
    else:
        print 'UNSAT'
    print '---------------------------------------------------------------'

def _assert_binary(alpha, u):
    for e in alpha:
        if e > 1:
            raise Exception('In BinaryOWAModel all alpha coefficients must be binary but found: %d' % e)
    for l in u:
        for e in l:
            if e > 1:
                raise Exception('In BinaryOWAModel all u coefficients must be binary but found: %d' % e)

class OWAModel(ILPModel):
    @staticmethod
    def solvefile(filename):
        n, m, K, alpha, u = _parse_owa_file(filename)

        model = OWAModel(length=8)
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
        solution, max_val = model.maximize(sum([(alpha[k]*u[i][j])*x[i][j][k] for i in xrange(n) for j in xrange(m) for k in xrange(K)]), lb=0, ub=250)
        print max_val
        
        _print_owa_solution(model, solution, x, y, n, m, K)
        return model

class BinaryOWAModel(ILPModel):
    @staticmethod
    def solvefile(filename):
        n, m, K, alpha, u = _parse_owa_file(filename)

        # Ensuring that both 'alpha' and 'u' are binary-valued vectors
        _assert_binary(alpha, u)

        model = BinaryOWAModel(length=1)
        y = [model.add_var('y' + str(j)) for j in xrange(m)]
        x = [[[model.add_var('x' + str(i) + '|' + str(j) + '|' + str(k)) for k in xrange(K)] for j in xrange(m)] for i in xrange(n)]

        # (a) Exactly K candidates are chosen
        model.exactly_k_of(y, K)

        # (b)
        for i in xrange(n):
            for j in xrange(m):
                for k in xrange(K):
                    model.add_clause([~x[i][j][k], y[j]])

        # (c) Only 1 candidate is ranked as k-th best
        for i in xrange(n):
            for k in xrange(K):
                model.exactly_k_of([x[i][j][k] for j in xrange(m)], 1)

        # (d) Item 'j' is ranked precisely on one position for 'i'
        for i in xrange(n):
            for j in xrange(m):
                model.at_most_k_of([x[i][j][k] for k in xrange(K)], 1)

        # (e)
        # for i in xrange(n):
        #     for k in xrange(K-1):
        #         sum([u[i][j]*x[i][j][k] for j in xrange(m)]) >= sum([u[i][j]*x[i][j][k+1] for j in xrange(m)]) 

        # (objective)
        # solution, max_val = model.maximize(sum([(alpha[k]*u[i][j])*x[i][j][k] for i in xrange(n) for j in xrange(m) for k in xrange(K)]), lb=0, ub=250)
        # print max_val

        l = [x[i][j][k] for i in xrange(n) for j in xrange(m) for k in xrange(K) if alpha[k]*u[i][j] > 0]
        print 'len(l)=%d' % len(l)
        # print l

        model.at_least_k_of(l, int(sys.argv[1]))

        solution = model.solve()
        
        _print_owa_solution(model, solution, x, y, n, m, K)

        return model

def test_general_owa_model():
    trivial = OWAModel.solvefile('owa/trivial')
    trivial.save_dimacs('data/trivial.dimacs')
    owa1 = OWAModel.solvefile('owa/owa1')
    owa1.save_dimacs('data/owa1.dimacs')
    owa2 = OWAModel.solvefile('owa/owa2')
    owa2.save_dimacs('data/owa2.dimacs')
    # owa3 = OWAModel.solvefile('owa/owa3')
    # owa3.save_dimacs('data/owa3.dimacs')

def test_binary_owa_model():
    bin1 = BinaryOWAModel.solvefile('owa/bin1')
    bin1.save_dimacs('data/bin1.dimacs')
    # bintrivial = BinaryOWAModel.solvefile('owa/trivial')
    # bintrivial.save_dimacs('data/bintrivial.dimacs')
    # binowa1 = BinaryOWAModel.solvefile('owa/owa1')
    # binowa1.save_dimacs('data/binowa1.dimacs')
    # binowa2 = BinaryOWAModel.solvefile('owa/owa2')
    # binowa2.save_dimacs('data/binowa2.dimacs')

def main():
    #test_general_owa_model()
    test_binary_owa_model()

if __name__ == '__main__':
    main()