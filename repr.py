#!/usr/bin/env python
__author__ = "Michal Mrowczyk"

## Solving factorization (and beyond) using boolean SAT solver
## Details of reduction: http://www.mimuw.edu.pl/~mati/fsat-20040420.pdf

import sys
import pycosat


class Var(object):
    def __init__(self, name, index):
        self.name = name
        self._index = index

    @property
    def index(self):
        return self._index

    def __invert__(self):
        return Var(self.name, -self.index)

    def __str__(self):
        return 'Var(name=%s, index=%s)' % (str(self.name), str(self._index))

    __repr__ = __str__

class Seq(object):
    def __init__(self, name, length, index, values=None):
        self.name = name
        self.length = length
        self.index = index
        self.values = values
        self.vars = []
        for i in xrange(self.length):
            self.vars.append(Var(name + '[%s]' % str(i), self.index + i))

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        return self.vars[index]

    def __str__(self):
        if self.values:
            return 'Seq(name=%s, len=%s, index=%s, values=%s)' % (str(self.name), str(self.length), str(self.index), str(self.values))
        else:
            return 'Seq(name=%s, len=%s, index=%s)' % (str(self.name), str(self.length), str(self.index))

    __repr__ = __str__

class Model(object):
    def __init__(self):
        self._index = 1
        self.vars = {}
        self.clauses = []

    def add_var(self, name):
        self.vars[name] = Var(name, self._index) 
        self._index += 1
        return self.vars[name]

    def add_seq(self, name, length, values=None):
        self.vars[name] = Seq(name, length, self._index, values=values)
        self._index += length
        return self.vars[name]

    def add_clause(self, constraints):
        self.clauses.append([c.index for c in constraints])

    ## Adding integer as a constraint and returns a reference to newly created sequence
    def add_integer(self, name, val, length=None):
        bin_val = bin(val)[2:][::-1]
        calculated_length = len(bin_val)
        if length:
            bin_val += '0' * (length - calculated_length)
        else:
            bin_val += '0'
            length = calculated_length + 1

        seq = self.add_seq(name, length, values=bin_val)
        clause = []
        for i in xrange(length):
            if bin_val[i] == '0':
                self.add_clause([~seq[i]])
            else:
                self.add_clause([seq[i]])
        return seq

    ## Adding equality as a constraint
    def add_equality(self, P, R):
        l = len(P)
        for i in xrange(l):
            self.add_clause([R[i], ~P[i]])
            self.add_clause([~R[i], P[i]])

    ## Adding not equality constraints
    def add_not_equality(self, P, R):
        """
        P, Q - seqs
        R - assumed to have fixed values !
        """
        l = len(P)
        clause = []
        for i in xrange(l):
            if R.values[i] == '0':
                clause.append(P[i])
            else:
                clause.append(~P[i])
        self.add_clause(clause)

    ## Adding shift equality as a constraint
    ## R = 2^i * P
    def add_shift_equality(self, P, R, i):
        """
        P, R - seq
        """
        l = len(P)
        for j in xrange(i):
            self.add_clause([~R[j]])
        j = i
        while j < l:
            self.add_clause([R[j], ~P[j-i]])
            self.add_clause([~R[j], P[j-i]])
            j += 1

    ## Adding lbit multiplication as a constraint
    ## R = BP
    def add_lbit_multiplication(self, B, P, R):
        """
        B - var
        P, Q - seq
        """
        l = len(P)
        for j in xrange(l):
            self.add_clause([B, ~R[j]])
            self.add_clause([P[j], ~R[j]])
            self.add_clause([R[j], ~B, ~P[j]])

    ## Adding addition constraints (complex !)
    ## R = P + Q
    def add_addition(self, P, Q, R, C):
        """
        P, Q, R - seq of length l
        C - seq of length l + 1
        """
        l = len(P)
        self.add_clause([~C[0]])
        self.add_clause([~C[l]])
        for j in xrange(1, l):
            self.add_clause([~C[j], P[j], C[j-1]])
            self.add_clause([~C[j], P[j], Q[j]])
            self.add_clause([~C[j], Q[j], C[j-1]])
            self.add_clause([C[j], ~P[j], ~C[j-1]])
            self.add_clause([C[j], ~P[j], ~Q[j]])
            self.add_clause([C[j], ~Q[j], ~C[j-1]])
        for j in xrange(0, l):
            self.add_clause([R[j], Q[j], P[j], ~C[j]])
            self.add_clause([R[j], Q[j], ~P[j], C[j]])
            self.add_clause([R[j], ~Q[j], P[j], C[j]])
            self.add_clause([R[j], ~Q[j], ~P[j], ~C[j]])
            self.add_clause([~R[j], Q[j], P[j], C[j]])
            self.add_clause([~R[j], Q[j], ~P[j], ~C[j]])
            self.add_clause([~R[j], ~Q[j], P[j], ~C[j]])
            self.add_clause([~R[j], ~Q[j], ~P[j], C[j]])

    ## Representing multiplication circuit
    ## N = PQ
    def add_multiplication(self, P, Q, N):
        """
        P, Q - numbers (seqs) being multiplied
        N - result of multiplication (input to factorization)
        """
        l = len(N)
        S = [self.add_seq('S' + str(i), l) for i in xrange(l)]
        C = [self.add_seq('C' + str(i), l+1) for i in xrange(l)]
        M = [self.add_seq('M' + str(i), l) for i in xrange(l)]
        R = [self.add_seq('R' + str(i), l) for i in xrange(l)]

        self.add_equality(S[0], P)
        for i in xrange(1, l):
            self.add_shift_equality(S[i-1], S[i], 1)
        for i in xrange(0, l):
            self.add_lbit_multiplication(Q[i], S[i], M[i])
        self.add_equality(R[0], M[0])
        for i in xrange(1, l):
            self.add_addition(R[i-1], M[i], R[i], C[i])
        self.add_equality(R[l-1], N)

        ## Need to add following restrictions to prune trivial factors
        ## P != N and P != 1 and Q != 1 and Q != N
        ONE = self.add_integer('ONE', 1, length=l)
        self.add_not_equality(P, ONE)
        self.add_not_equality(P, N)
        self.add_not_equality(Q, ONE)
        self.add_not_equality(Q, N)

    def solve(self):
        # for sol in pycosat.itersolve(self.clauses):
        #     print sol
        return pycosat.solve(self.clauses)

    def __getattr__(self, name):
        return self.vars[name]

    def __str__(self):
        return 'Model(vars=%s, clauses=%s)' % (self.vars, self.clauses)

    __repr__ = __str__

# Representation of Integer - Assuming val as decimal
# class Int(object):
#     def __init__(self, val):
#         self.val = bin(val)[2:]
        
#     def __call__(self, startvar=1):
#         clause = []
#         varindex = startvar
#         for digit in self.val:
#             if digit == '0':
#                 clause.append(-varindex)
#             else:
#                 clause.append(varindex)
#             varindex += 1
#         return clause

def main():
    # m1 = Model()
    # x1 = m1.add_var('x1')
    # x2 = m1.add_var('x2')
    # Y = m1.add_seq('Y', 4)
    # Z = m1.add_seq('Z', 8)
    # m1.add_clause([Y[0], Y[2], ~x2])
    # print m1
    # print m1.Y[3]
    # print m1.Z[0]

    # print '------------------------'

    # m2 = Model()
    # X = m2.add_integer('X', 42)
    # Y = m2.add_integer('Y', 42)
    # m2.add_equality(X, Y)
    # # m2.add_shift_equality(X, Y, 1)
    # print m2
    # print m2.solve()

    # print '------------------------'

    sat = Model()
    N = sat.add_integer('N', int(sys.argv[1]))
    l = len(N)
    P = sat.add_seq('P', l)
    Q = sat.add_seq('Q', l)
    sat.add_multiplication(P, Q, N)
    print N
    print '-------SAT model-------'
    print sat
    print '-------solution--------'
    solution = sat.solve()
    print solution
    if solution != 'UNSAT':
        print solution[N.index-1:N.index + l-1]
        print solution[P.index-1:P.index + l-1]
        print solution[Q.index-1:Q.index + l-1]

    # FORTY_TWO = Int(42)
    # FORTY_TWO_CLAUSE = FORTY_TWO()
    # print FORTY_TWO_CLAUSE

if __name__ == '__main__':
    main()
