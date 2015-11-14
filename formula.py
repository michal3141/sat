
__author__ = "Michal Mrowczyk"

def inc():
    i = 0
    while True:
        yield 'C%d' % i
        i += 1

gen = inc()

# Class representing boolean formula in parsed (tree) form
class Formula(object):
    def __init__(self, *A):
        self.A = A

# Tseitin transformation is applied to transform arbitrary boolean formula to CNF efficiently
class OR(Formula):
    def __repr__(self):
        return 'OR(%s)' % ','.join(map(str, self.A))

    def to_cnf(self):
        C = VAR(gen.next())
        ret = [x.to_cnf() for x in self.A]
        roots = [x['root'] for x in ret]
        cnfs = [x['clauses'] for x in ret]

        clauses = []
        clauses += [OR(NOT(A), C) for A in roots]
        clauses += [OR(NOT(C), *[A for A in roots])]
        for cnf in cnfs:
            for clause in cnf:
                if clause != []:
                    clauses.append(clause)

        return {
            'clauses': clauses,
            'root': C 
        }

    __str__ = __repr__

class AND(Formula):
    def __repr__(self):
        return 'AND(%s)' % ','.join(map(str, self.A))

    def to_cnf(self):
        C = VAR(gen.next())
        ret = [x.to_cnf() for x in self.A]
        roots = [x['root'] for x in ret]
        cnfs = [x['clauses'] for x in ret]

        clauses = []
        clauses += [OR(A, NOT(C)) for A in roots]
        clauses += [OR(C, *[NOT(A) for A in roots])]
        for cnf in cnfs:
            for clause in cnf:
                if clause != []:
                    clauses.append(clause)

        return {
            'clauses': clauses,
            'root': C
        }

    __str__ = __repr__

class NOT(Formula):
    def __init__(self, A):
        self.A = A

    def __repr__(self):
        return 'NOT(%r)' % (self.A)

    def to_cnf(self):
        C = VAR(gen.next())
        ret = self.A.to_cnf()
        root = ret['root']
        cnf = ret['clauses']

        clauses = [OR(NOT(root), NOT(C)), OR(root, C)]

        if cnf != []:
            clauses += cnf

        return {
            'clauses': clauses,
            'root': C
        }

    __str__ = __repr__

class VAR(Formula):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '%r' % (self.name)

    def to_cnf(self):
        return {
            'clauses': [],
            'root': self
        }

    __str__ = __repr__

def cnf(x):
    x_cnf = x.to_cnf()
    root = x_cnf['root']
    clauses = x_cnf['clauses']
    # root is required to force whole formula to be 1
    return AND(OR(root), *clauses)

def main():

    x1 = OR(VAR('X'), VAR('Y'))
    print 'x1:', x1
    print 'cnf(x1):', cnf(x1)

    x2 = OR(AND(VAR('X'), VAR('Y')), AND(NOT(VAR('X')), NOT(VAR('Y'))))
    print 'x2:', x2
    print 'cnf(x2):', cnf(x2)

    x3 = NOT(NOT(AND(VAR('X'), VAR('Y'))))
    print 'x3:', x3
    print 'cnf(x3):', cnf(x3)

if __name__ == '__main__':
    main()
