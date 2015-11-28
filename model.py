#!/usr/bin/env python
__author__ = "Michal Mrowczyk"

import sys
import pycosat
from formula import AND, OR, NOT, VAR, cnf

def is_num(v):
    return type(v) == int or type(v) == long

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
    def __init__(self, name, length, index):
        self.name = name
        self.length = length
        self.index = index
        self.vars = []
        for i in xrange(self.length):
            self.vars.append(Var(name + '|%d' % i, self.index + i))

    def __mul__(self, other):
        m = self.model
        if is_num(other):
            s2 = m.add_integer(m.get_seq_name(), other)
        else:
            s2 = other
        rhs = m.add_seq(m.get_seq_name())
        m.add_multiplication(self, s2, rhs)
        return rhs

    def __add__(self, other):
        m = self.model
        if is_num(other):
            s2 = m.add_integer(m.get_seq_name(), other)
        else:
            s2 = other
        rhs = m.add_seq(m.get_seq_name())
        m.add_addition(self, s2, rhs)
        return rhs

    def __le__(self, other):
        m = self.model
        if is_num(other):
            m.add_lei(self, other)
        else:
            m.add_les(self, other)


    def __ge__(self, other):
        m = self.model
        if is_num(other):
            m.add_gei(self, other)
        else:
            m.add_ges(self, other)

    def __eq__(self, other):
        # print 'Seq::__eq__'
        m = self.model
        if is_num(other):
            s2 = m.add_integer(m.get_seq_name(), other)
            m.add_equality(self, s2)
        else:
            m.add_equality(self, other)

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        return self.vars[index]

    def __str__(self):
        return 'Seq(name=%s, len=%s, index=%s)' % (str(self.name), str(self.length), str(self.index))

    __repr__ = __str__

    __rmul__ = __mul__

    __radd__ = __add__

## Representing integer type which is simply a sequence of bits with fixed values
class Int(Seq):
    def __init__(self, name, length, index, values):
        super(Int, self).__init__(name, length, index)
        self.values = values

    def __str__(self):
        return 'Int(name=%s, len=%s, index=%s, values=%s)' % (str(self.name), str(self.length), str(self.index), str(self.values))

    __repr__ = __str__

class Model(object):
    def __init__(self):
        self._seq_index = 1 # Keeping sequence index for automaticaly created sequences
        self._index = 1
        self.vars = {}
        self.clauses = []
        self.all_units = set()

    def add_var(self, name):
        self.vars[name] = Var(name, self._index) 
        self._index += 1
        return self.vars[name]


    def add_seq(self, name, length=1):
        self.vars[name] = Seq(name, length, self._index)
        self._index += length
        return self.vars[name]


    def add_int(self, name, length=1, values='0'):
        self.vars[name] = Int(name, length, self._index, values)
        self._index += length
        return self.vars[name]

    ## This allows to add arbitrary boolean formula to the model !
    ## Formula is automatically converted to CNF before being added as a series of constraints !
    ## Tseytin transformation is used when converting to CNF to ensure decent formula complexity
    def add_formula(self, f):
        cnf_f = cnf(f)
        for clause in cnf_f.A:
            constraints = []
            for lit in clause.A:
                if type(lit) == NOT:
                    name = lit.A.name
                    var_ref = self.get_ref_by_name(name)
                    constraints.append(~var_ref)
                elif type(lit) == VAR:
                    name = lit.name
                    var_ref = self.get_ref_by_name(name)
                    constraints.append(var_ref)
            self.add_clause(constraints)


    def add_clause(self, constraints):
        self.clauses.append([c.index for c in constraints])


    # Returns sequence name for automatically created sequences
    def get_seq_name(self):
        seq_name = '_' + str(self._seq_index)
        self._seq_index += 1
        return seq_name


    def get_ref_by_name(self, name):
        """
        Returns reference to variable by name, creating variable when needed
        """
        if name in self.vars:
            return self.vars[name]

        seq_name_and_index = name.split('|')

        if len(seq_name_and_index) == 2:
            seq_name, index = name.split('|')
            if seq_name in self.vars:
                return self.vars[seq_name][int(index)]

        ret = self.add_var(name)
        return ret


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


    ## Returns binary value for number I of length l
    def get_bin(self, I, length=None):
        values = bin(I)[2:][::-1]
        if length is None:
            length = len(values)
        return values + '0' * (length - len(values))


    ## Obtaining bits of sequence P in solution
    def get_bits(self, P, solution):
        l = len(P)
        return solution[P.index-1:P.index + l-1]


    ## Performing unit propagation to simplify the formula further
    def unit_propagate(self):
        while True:
            new_clauses = []
            units = set()

            # Collecting units
            for clause in self.clauses:
                if len(clause) == 1:
                    lit = clause[0]
                    # When conflicting units appear
                    if -lit in units:
                        self.clauses = [[1], [-1]]
                        return
                    else:
                        units.add(lit)

            #print 'unit_propagate::units: %r' % units

            # Merging units that are already collected
            self.all_units = self.all_units.union(units)
            #print 'unit_propagate::all_units: %r' % self.all_units

            # Escaping when there are no units to make use of
            if len(units) == 0:
                break

            # Simplifying following clauses making use of units
            for clause in self.clauses:
                if len(units.intersection(set(clause))) > 0: 
                    continue
                new_clause = []
                for lit in clause:
                    if -lit not in units:
                        new_clause.append(lit)
                # In case when whole clause got liquidated, we need to report UNSAT formula
                if len(new_clause) == 0:
                    self.clauses = [[1], [-1]]
                    return
                new_clauses.append(new_clause)

            self.clauses = new_clauses
            #print 'unit_propagate::clauses:', self.clauses


    def vars_count(self):
        s = set()
        for clause in self.clauses:
            for lit in clause:
                var = abs(lit)
                if var not in s:
                    s.add(var)
        return len(s)


    def clauses_count(self):
        return len(self.clauses)

        
    def solve(self):
        solution = pycosat.solve(self.clauses)
        if solution == 'UNSAT':
            return 'UNSAT'
        else:
            #print solution
            solution = [x for x in solution if -x not in self.all_units]
            solution.extend(list(self.all_units))
            return sorted(list(set(solution)), key=abs)


    def itersolve(self):
        return (sol for sol in pycosat.itersolve(self.clauses))

    
    def save_dimacs(self, filename='f.dimacs'):
        with open(filename, 'w') as f:
            f.write('p cnf %d %d\n' % (self.vars_count(), self.clauses_count()))
            for clause in self.clauses:
                for var in clause:
                    f.write('%d ' % var)
                f.write('\n')


    def __getattr__(self, name):
        return self.vars[name]

    def __str__(self):
        return 'Model(vars=%s, clauses=%s)' % (self.vars, self.clauses)

    __repr__ = __str__

def main():
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

    m2 = Model()
    m2.add_formula(AND(VAR('X'), NOT(VAR('X'))))
    print m2
    print m2.solve()

    m3 = Model()
    m3.add_formula(AND(OR(VAR('X1'), VAR('X2')), OR(NOT(VAR('X1')), VAR('X2')), OR(VAR('X1'), NOT(VAR('X2'))), OR(NOT(VAR('X1')), NOT(VAR('X2')))))
    print m3
    print m3.solve()

if __name__ == '__main__':
    main()
