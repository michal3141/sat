
__author__ = "Michal Mrowczyk"

def inc():
    i = 0
    while True:
        yield 'C%d' % i
        i += 1

gen = inc()

# Class representing boolean formula in parsed (tree) form
class Formula(object):
    def __init__(self, A=None, B=None):
        self.A = A
        self.B = B

# Tseitin transform is applied to transform arbitrary boolean formula to CNF efficiently
class OR(Formula):
    def __repr__(self):
        return 'OR(%r,%r)' % (self.A, self.B)

    def to_cnf(self):
        C = VAR(gen.next())
        return AND(AND(AND(AND(OR(NOT(self.A), C), OR(NOT(self.B), C)), OR(OR(self.A, self.B), NOT(C))) , self.A.to_cnf()), self.B.to_cnf())

class AND(Formula):
    def __repr__(self):
        return 'AND(%r,%r)' % (self.A, self.B)

    def to_cnf(self):
        C = VAR(gen.next())
        return AND(AND(AND(AND(OR(self.A, NOT(C)), OR(self.B, NOT(C))), OR(OR(NOT(self.A), NOT(self.B)), C)) , self.A.to_cnf()), self.B.to_cnf())

class NOT(Formula):
    def __repr__(self):
        return 'NOT(%r)' % (self.A)

    def to_cnf(self):
        C = VAR(gen.next())
        return AND(AND(OR(NOT(self.A), NOT(C)), OR(self.A, C)), self.A.to_cnf())

class VAR(Formula):
    def __repr__(self):
        return '%r' % (self.A)

    def to_cnf(self):
        return self

def main():
    x = OR(AND(VAR('X'), VAR('Y')), AND(NOT(VAR('X')), NOT(VAR('Y'))))
    cnf_x = x.to_cnf()
    print x
    print cnf_x

if __name__ == '__main__':
    main()
