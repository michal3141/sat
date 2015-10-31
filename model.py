#!/usr/bin/env python
__author__ = "Michal Mrowczyk"

## Solving factorization (and beyond) using boolean SAT solver
## Inspired by: http://www.mimuw.edu.pl/~mati/fsat-20040420.pdf

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


    def solve(self):
        # for sol in pycosat.itersolve(self.clauses):
        #     print sol
        return pycosat.solve(self.clauses)

    def __getattr__(self, name):
        return self.vars[name]

    def __str__(self):
        return 'Model(vars=%s, clauses=%s)' % (self.vars, self.clauses)

    __repr__ = __str__

def main():
    import pprint as pp
    m1 = Model()
    x1 = m1.add_var('x1')
    x2 = m1.add_var('x2')
    Y = m1.add_seq('Y', 4)
    Z = m1.add_seq('Z', 8)
    m1.add_clause([Y[0], Y[2], ~x2])
    print m1
    print m1.Y[3]
    print m1.Z[0]
    print m1.solve()


if __name__ == '__main__':
    main()
