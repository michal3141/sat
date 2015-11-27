from model import Model, Int
from itertools import product

## Solving factorization (and beyond) using boolean SAT solver
## Inspired by: http://www.mimuw.edu.pl/~mati/fsat-20040420.pdf

class FactorizationModel(Model):
    """
    Class containing all primitives needed when creating model capable of factorizing integers
    i.e. multiplication circuit, addition ciruit, shift circuit, checking equality, 
    adding integral constraints etc.
    """

    ## Adding integer as a constraint and returns a reference to newly created sequence
    def add_integer(self, name, val, length=None):
        bin_val = bin(val)[2:][::-1]
        calculated_length = len(bin_val)
        if length:
            bin_val += '0' * (length - calculated_length)
        else:
            length = calculated_length

        seq = self.add_int(name, length=length, values=bin_val)
        clause = []
        for i in xrange(length):
            if bin_val[i] == '0':
                self.add_clause([~seq[i]])
            else:
                self.add_clause([seq[i]])
        return seq


    ## Adding equality as a constraint
    def add_equality(self, P, R):
        """ 
        P, R - sequences
        """
        l = len(P)
        for i in xrange(l):
            self.add_clause([R[i], ~P[i]])
            self.add_clause([~R[i], P[i]])


    ## Adding not equality constraints
    def add_not_equality(self, P, I):
        """
        P - Seq
        I - integer
        """
        l = len(P)
        clause = []
        if type(I) == Int:
            values = I.values
        else:
            values = self.get_bin(I, length=l)
        for i in xrange(l):
            if values[i] == '0':
                clause.append(P[i])
            else:
                clause.append(~P[i])
        self.add_clause(clause)


    ## Adding shift equality as a constraint
    ## R = 2^i * P
    def add_shift_equality(self, P, R, i):
        """
        P, R - seq of length l
        """
        l = len(R)
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
        P, Q - seq of length l
        """
        l = len(P)
        for j in xrange(l):
            self.add_clause([B, ~R[j]])
            self.add_clause([P[j], ~R[j]])
            self.add_clause([R[j], ~B, ~P[j]])


    ## Adding addition constraints
    def add_addition(self, P, Q, R):
        """
        P, Q, R - seq of length l
        """
        l = len(P)
        C = self.add_seq(self.get_seq_name(), l+1)
        self.add_addition_with_carry(P, Q, R, C)


    ## Adding addition constraints (with carry)
    ## R = P + Q, carry C
    def add_addition_with_carry(self, P, Q, R, C):
        """
        P, Q, R - seq of length l
        C - seq of length l+1
        """
        l = len(P)
        self.add_clause([~C[0]])
        self.add_clause([~C[l]])
        for j in xrange(1, l+1):
            self.add_clause([~C[j], P[j-1], C[j-1]])
            self.add_clause([~C[j], P[j-1], Q[j-1]])
            self.add_clause([~C[j], Q[j-1], C[j-1]])
            self.add_clause([C[j], ~P[j-1], ~C[j-1]])
            self.add_clause([C[j], ~P[j-1], ~Q[j-1]])
            self.add_clause([C[j], ~Q[j-1], ~C[j-1]])
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
        N - result of multiplication
        """
        ln = len(N)
        lq = len(Q)
        S = [self.add_seq(self.get_seq_name(), ln) for i in xrange(lq)]
        C = [self.add_seq(self.get_seq_name(), ln+1) for i in xrange(lq-1)]
        M = [self.add_seq(self.get_seq_name(), ln) for i in xrange(lq)]
        R = [self.add_seq(self.get_seq_name(), ln) for i in xrange(lq)]

        self.add_equality(S[0], P)
        for i in xrange(1, lq):
            self.add_shift_equality(S[i-1], S[i], 1)
        for i in xrange(0, lq):
            self.add_lbit_multiplication(Q[i], S[i], M[i])
        self.add_equality(R[0], M[0])
        for i in xrange(1, lq):
            self.add_addition_with_carry(R[i-1], M[i], R[i], C[i-1])
        self.add_equality(R[lq-1], N)

        # We need to also make sure that our multiplication won't result in number
        # that has more than l bits !
        for i, j in product(xrange(ln), xrange(lq)):
            if i + j >= ln:
                self.add_clause([~P[i], ~Q[j]])

        # Q will be smaller factor wlog (without loss of generality)
        for i in xrange(lq):
            if i > (lq - 1)/ 2:
                self.add_clause([~Q[i]])


    def add_multiplication_without_trivial_factors(self, P, Q, N):
        """
        P, Q - numbers (seqs) being multiplied
        N - result of multiplication
        P != 1, Q != 1, P != N, Q != N
        """
        self.add_multiplication(P, Q, N)

        ## Need to add restriction to prune trivial factors: Q != 1

        self.add_not_equality(Q, 1)


# Example of using factorization model when factorizing integer
def main():
    import sys
    sat = FactorizationModel()
    number = int(sys.argv[1])
    bin_number = bin(number)[2:]
    len_bin_number = len(bin_number)

    N = sat.add_integer('N', number, length=len_bin_number)
    l = len(N)
    P = sat.add_seq('P', length=l)
    Q = sat.add_seq('Q', length=l)

    sat.add_multiplication_without_trivial_factors(P, Q, N)
    print 'Before unit propagation:', sat.clauses
    sat.unit_propagate()
    print 'After unit propagation:', sat.clauses
    print '-------SAT Factorization model:-------'
    print sat
    print '-------Solution:----------------------'
    solution = sat.solve()
    print '# of vars: %d, # of clauses: %d' % (sat.vars_count(), sat.clauses_count())
    print solution
    if solution != 'UNSAT':
        print '-------Factors:----------------------'
        print 'P.bits: ', sat.get_bits(P, solution)
        print 'Q.bits: ', sat.get_bits(Q, solution)
        print 'N:', number
        print 'P:', sat.get_decimal_value(P, solution)
        print 'Q:', sat.get_decimal_value(Q, solution)
    else:
        print 'N: %d is prime' % number

if __name__ == '__main__':
    main()