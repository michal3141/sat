from model import Model


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
        l = min(len(P), len(R))
        for i in xrange(l):
            self.add_clause([R[i], ~P[i]])
            self.add_clause([~R[i], P[i]])


    ## Adding not equality constraints
    def add_not_equality(self, P, R):
        """
        P, Q - seqs
        R - assumed to have fixed values !
        """
        l = min(len(P), len(R))
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


    ## Adding addition constraints (complex !)
    ## R = P + Q
    def add_addition(self, P, Q, R, C):
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


    ## Representing multiplication circuit for factorization
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

        for i in xrange((l-1)/2+1, l):
            self.add_clause([~P[i]])
            self.add_clause([~Q[i]])

    ## Obtaining decimal value for integer P with respect to solution
    def get_decimal_value(self, P, solution):
        """
        P - integer
        solution: List of integers representing solution
        """
        l = len(P)
        ret = 0
        mult = 1
        for i in xrange(P.index-1, P.index + l-1):
            if solution[i] > 0:
                ret += mult
            mult *= 2
        return ret

# Example of using factorization model when factorizing integer
def main():
    import sys
    sat = FactorizationModel()
    number = int(sys.argv[1])
    bin_number = bin(number)[2:]
    len_bin_number = len(bin_number)

    N = sat.add_integer('N', number, length=len_bin_number*2)
    l = len(N)
    P = sat.add_seq('P', l)
    Q = sat.add_seq('Q', l)

    sat.add_multiplication(P, Q, N)
    print '-------SAT Factorization model:-------'
    print sat
    print '-------Solution:----------------------'
    solution = sat.solve()
    print solution
    if solution != 'UNSAT':
        print '-------Factors:----------------------'
        print 'N.bits: ', solution[N.index-1:N.index + l-1]
        print 'P.bits: ', solution[P.index-1:P.index + l-1]
        print 'Q.bits: ', solution[Q.index-1:Q.index + l-1]
        print 'N:', number
        print 'P:', sat.get_decimal_value(P, solution)
        print 'Q:', sat.get_decimal_value(Q, solution)
    else:
        print 'N: %d is prime' % number

if __name__ == '__main__':
    main()