from factmodel import FactorizationModel
from formula import AND, OR, NOT, VAR, cnf

import os
import sys

class InequalityModel(FactorizationModel):
    """
    Inequalities constraints between sequences and between sequences and integers
    """

    ## Less or equal than sequence => LES
    def add_les(self, X, Y):
        """
        Comparing two sequences:
        X - sequence
        Y - sequence
        """
        l = len(X)
        x0 = VAR(X[0].name)
        y0 = VAR(Y[0].name)

        f = OR(AND(NOT(x0), y0), AND(OR(NOT(x0), y0), OR(x0, NOT(y0))))

        for i in xrange(1, l):
            xi = VAR(X[i].name)
            yi = VAR(Y[i].name)
            f = OR(AND(NOT(xi), yi), AND(AND(OR(NOT(xi), yi), OR(xi, NOT(yi))), f))

        self.add_formula(f)

    ## Greater or equal than sequence => GES
    def add_ges(self, X, Y):
        self.add_les(Y, X)

    ## Less or equal than integer => LEI
    def add_lei(self, X, I):
        """
        Comparing sequence against integer
        X - sequence
        I - integer
        """
        l = len(X)
        x0 = VAR(X[0].name)
        i0 = I.values[0]

        if i0 == '0':
            f = NOT(x0)
        elif i0 == '1':
            f = OR(x0, NOT(x0))

        for i in xrange(1, l):
            xi = VAR(X[i].name)
            ii = I.values[i]
            if ii == '0':
                f = AND(NOT(xi), f)    
            elif ii == '1':
                # Keeping original f
                pass

        self.add_formula(f)

    ## Greater or equal than integer => GEI
    def add_gei(self, X, I):
        l = len(X)
        x0 = VAR(X[0].name)
        i0 = I.values[0]

        if i0 == '0':
            f = OR(x0, NOT(x0))
        elif i0 == '1':
            f = x0

        for i in xrange(1, l):
            xi = VAR(X[i].name)
            ii = I.values[i]
            if ii == '0':
                # Keeping original f
                pass
            elif ii == '1':
                f = AND(xi, f)  

        self.add_formula(f)        

def main():
    sys.setrecursionlimit(100000)
    LEN_IN_BITS = 6

    ## Problem 1:
    ## Find X - integer such that: X <= 2, X >= 2, X != 2 (Obviously such number does not exist) 

    # Creating sequences and integers needed to state the problem
    m1 = InequalityModel()
    X = m1.add_seq('X', LEN_IN_BITS)
    TWO = m1.add_integer('TWO', 2, length=LEN_IN_BITS)

    # Q != 2
    m1.add_not_equality(X, TWO)

    # X >= 2
    m1.add_gei(X, TWO)

    # X <= 2
    m1.add_lei(X, TWO)
    
    print m1
    # Getting solution
    solution = m1.solve()
    print solution
    if solution != 'UNSAT':
        print 'X:', m1.get_decimal_value(X, solution)

    m1.save_dimacs(os.path.join('data', 'inequalities_1.dimacs'))

    ## Problem 2:
    ## Find P, Q - integers such that: P + Q = 42, P >= Q, P >= 24

    # Creating sequences and integers needed to state the problem
    m2 = InequalityModel()
    P = m2.add_seq('P', LEN_IN_BITS)
    Q = m2.add_seq('Q', LEN_IN_BITS)
    FORTY_TWO = m2.add_integer('FORTY_TWO', 42, LEN_IN_BITS)
    TWENTY_FOUR = m2.add_integer('TWENTY_FOUR', 24, LEN_IN_BITS)

    # Forcing P + Q = 42
    m2.add_addition(P, Q, FORTY_TWO)

    # P >= Q
    m2.add_ges(P, Q)

    # P >= 24
    m2.add_gei(P, TWENTY_FOUR)

    print m2
    # Getting solution
    solution = m2.solve()
    print solution
    if solution != 'UNSAT':
        print 'P:', m2.get_decimal_value(P, solution)
        print 'Q:', m2.get_decimal_value(Q, solution)

    m2.save_dimacs(os.path.join('data', 'inequalities_2.dimacs'))

    ## Problem 3:
    ## Checking feasibility of some linear integer program

    m3 = InequalityModel()
    X = m3.add_seq('X', LEN_IN_BITS)
    Y = m3.add_seq('Y', LEN_IN_BITS)
    RHS1 = m3.add_seq('RHS1', LEN_IN_BITS)
    M1 = m3.add_seq('M1', LEN_IN_BITS)
    M2 = m3.add_seq('M2', LEN_IN_BITS)
    M3 = m3.add_seq('M3', LEN_IN_BITS)
    M4 = m3.add_seq('M4', LEN_IN_BITS)
    S1 = m3.add_seq('S1', LEN_IN_BITS)
    S2 = m3.add_seq('S2', LEN_IN_BITS)

    ONE = m3.add_integer('ONE', 1, length=LEN_IN_BITS)
    TWO = m3.add_integer('TWO', 2, length=LEN_IN_BITS)
    THREE = m3.add_integer('THREE', 3, length=LEN_IN_BITS)
    TWELVE = m3.add_integer('TWELVE', 12, length=LEN_IN_BITS)

    # Constraints:
    # y <= 1 + x

    m3.add_addition(X, ONE, RHS1)
    m3.add_les(Y, RHS1)

    # 3x + 2y <= 12
    
    m3.add_multiplication(THREE, X, M1)
    m3.add_multiplication(TWO, Y, M2)
    m3.add_addition(M1, M2, S1)
    m3.add_lei(S1, TWELVE)

    # 2x + 3y <= 12

    m3.add_multiplication(TWO, X, M3)
    m3.add_multiplication(THREE, Y, M4)
    m3.add_addition(M3, M4, S2)
    m3.add_lei(S2, TWELVE)

    print m3
    # Getting solution
    solution = m3.solve()
    print solution
    if solution != 'UNSAT':
        print 'X:', m3.get_decimal_value(X, solution)
        print 'Y:', m3.get_decimal_value(Y, solution)

    m3.save_dimacs(os.path.join('data', 'inequalities_3.dimacs'))


if __name__ == '__main__':
    main()

