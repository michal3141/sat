from inequalities import InequalityModel
from copy import deepcopy, copy

class ILPModel(InequalityModel):
    def __init__(self, length=8):
        super(ILPModel, self).__init__()
        self.length = length

    def __len__(self):
        return self.length

        
    def add_seq(self, name=None, l=None):
        name = name if name is not None else self.get_seq_name()
        length = l if l is not None else self.length
        seq = super(ILPModel, self).add_seq(name, length=length)
        seq.model = self
        return seq


    def add_integer(self, name, value):
        integer = super(ILPModel, self).add_integer(name, value, length=self.length)
        integer.model = self
        return integer

    def add_var(self, name=None):
        var = super(ILPModel, self).add_var(name)
        var.model = self
        return var

    # Adding sequence constrained to binary values 0 and 1
    def add_bin(self, name=None, l=None):
        X = self.add_seq(name=name, l=l)
        for i in xrange(1, len(X)):
            self.add_clause([~X[i]])
        return X

    def maximize(self, obj, lb=0, ub=1000):
        """
        obj - some objective function subject to maximization
        lb - lower bound for obj function,
        ub - upper bound for obj function
        """
        clauses_cpy = deepcopy(self.clauses)

        last_sat = None
        solution = 'UNSAT'
        while lb <= ub:
            self.clauses = deepcopy(clauses_cpy)
            curr = (lb + ub) / 2
            obj >= curr
            print 'ILPModel::maximize for %d lb=%d ub=%d' % (curr, lb, ub)
            solution = self.solve()
            if solution == 'UNSAT':
                ub = curr - 1
            else:
                lb = curr + 1
                last_sat = curr

        # Going back to last satisfied optimization subproblem
        if solution == 'UNSAT' and last_sat is not None:
            self.clauses = deepcopy(clauses_cpy)
            obj >= last_sat
            print 'ILPModel::maximize::last_sat for %d' % last_sat
            solution = self.solve()

        # Getting objective value when possible
        obj_val = None
        if solution != 'UNSAT':
            obj_val = self.get_decimal_value(obj, solution)

        return solution, obj_val

    def minimize(self, obj, lb=0, ub=1000):
        """
        obj - some objective function subject to minimization
        lb - lower bound for obj function,
        ub - upper bound for obj function
        """
        clauses_cpy = deepcopy(self.clauses)

        last_sat = None
        solution = 'UNSAT'
        while lb <= ub:
            self.clauses = deepcopy(clauses_cpy)
            curr = (lb + ub) / 2
            obj <= curr
            #print 'ILPModel::minimize for %d' % curr
            solution = self.solve()
            if solution == 'UNSAT':
                lb = curr + 1
            else:
                ub = curr - 1
                last_sat = curr

        # Going back to last satisfied optimization subproblem
        if solution == 'UNSAT' and last_sat is not None:
            self.clauses = deepcopy(clauses_cpy)
            obj <= last_sat
            #print 'ILPModel::minimize for %d' % last_sat
            solution = self.solve()

        # Getting objective value when possible
        obj_val = None
        if solution != 'UNSAT':
            obj_val = self.get_decimal_value(obj, solution)

        return solution, obj_val


class ILPModelMinimizer(object):
    def __init__(self, model):
        self.model = model

class ILPModelMaximizer(object):
    def __init__(self, model):
        self.model = model


def main():
    m1 = ILPModel(length=5)
    X = m1.add_seq('X')
    Y = m1.add_seq('Y')
    Z = m1.add_seq('Z')
    # sum([3*X, Y, 2*Z]) == 17
    3*X + Y + 2*Z == 17
    2*Y + Z == 10
    2*X + 3*Z == 16

    # print m1
    # Getting solution
    solution = m1.solve()
    # print solution
    if solution != 'UNSAT':
        print 'X:', m1.get_decimal_value(X, solution)
        print 'Y:', m1.get_decimal_value(Y, solution)
        print 'Z:', m1.get_decimal_value(Z, solution)

    m2 = ILPModel(length=5)
    X = m2.add_seq()
    Y = m2.add_seq()
    Y <= X + 1
    3*X + 2*Y <= 12
    2*X + 3*Y <= 13
    
    # solution, obj_value = m2.maximize(Y, lb=2, ub=10)
    solution, obj_value = m2.minimize(Y, lb=0, ub=10)

    # print m2
    # Getting solution
    # solution = m2.solve()
    # print solution
    if solution != 'UNSAT':
        print 'Objective function value:', obj_value
        print 'X:', m2.get_decimal_value(X, solution)
        print 'Y:', m2.get_decimal_value(Y, solution)
    else:
        print 'UNSAT'

    m3 = ILPModel(length=27)
    X = m3.add_seq()
    Y = m3.add_seq()
    Z = m3.add_seq()

    # X >= 1
    Y >= 423
    Z >= 423
    # Fermat's diophantine equation
    X*X*X + Y*Y*Y == Z*Z*Z

    solution = m3.solve()
    print 'Fermat diophantine equation solution'
    if solution != 'UNSAT':
        print 'X:', m3.get_decimal_value(X, solution)
        print 'Y:', m3.get_decimal_value(Y, solution)
        print 'Z:', m3.get_decimal_value(Y, solution)
    else:
        print 'UNSAT'    

    ## Simple way of adding binary constrained variables
    m4 = ILPModel(length=5)
    X = m4.add_bin()
    #X <= 1
    print 'm4:', m4

    ## And new model
    m5 = ILPModel(length=5)
    X = m5.add_seq()
    Y = m5.add_seq()
    X >= 27
    X >= 29
    print 'm5:', m5
    solution = m5.solve()
    if solution != 'UNSAT':
        print 'X:', m5.get_decimal_value(X, solution)
    else:
        print 'UNSAT'        

if __name__ == '__main__':
    main()