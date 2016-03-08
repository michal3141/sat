#!/usr/bin/env python
__author__ = "Michal Mrowczyk"

import sys
import pycosat
from formula import AND, OR, NOT, VAR, cnf

def is_num(v):
    return type(v) == int or type(v) == long

def merge_clauses(c1, c2, excluded_var):
    c1 = [var for var in c1 if abs(var) != excluded_var]
    c2 = [var for var in c2 if abs(var) != excluded_var]

    for var in c1:
        if -var in c2:
            return None

    new_clause = []
    for var in c1:
        if var not in new_clause:
            new_clause.append(var)
    for var in c2:
        if var not in new_clause:
            new_clause.append(var)

    return new_clause


class Var(object):
    def __init__(self, name, index):
        self.name = name
        self._index = index

    @property
    def index(self):
        return self._index

    def __invert__(self):
        return Var(self.name, -self.index)

    def __mul__(self, other):
        m = self.model
        if is_num(other):
            s = m.add_seq(m.get_seq_name())
            other_bin = m.get_bin(other, length=len(m))
            for i in xrange(len(other_bin)):
                if other_bin[i] == '0':
                    m.add_clause([~s[i]])
                else:
                    m.add_clause([~s[i], self])
                    m.add_clause([s[i], ~self])
            return s
        raise Exception('Unsupported type in Var multiplication: %s' % str(type(other)))

    def __str__(self):
        return 'Var(name=%s, index=%s)' % (str(self.name), str(self._index))

    __repr__ = __str__

    __rmul__ = __mul__

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

    def add_var(self, name=None):
        name = name if name is not None else self.get_seq_name()
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

    def exactly_one_of(self, l):
        """
        Adding constraint that exactly one of the binary variables in 'l' is true
        """
        # l >= 1
        self.add_clause(l)
        # l <= 1
        self.at_most_one_of(l)

    def at_most_one_of(self, l):
        """
        Adding constraint that at most of the binary variables in 'l' is true
        """
        for i in xrange(len(l)):
            for j in xrange(i+1, len(l)):
                self.add_clause([~l[i], ~l[j]])

    # Using Carsten Sinz approach (http://www.carstensinz.de/papers/CP-2005.pdf)
    def exactly_k_of(self, x, k):
        self.at_most_k_of(x, k)
        self.at_least_k_of(x, k)


    def at_most_k_of(self, x, k):
        n = len(x)
        if n <= 1:
            return

        s = [[self.add_var() for j in xrange(k)] for i in xrange(n-1)]
        self.add_clause([~x[0], s[0][0]])
        for j in xrange(1, k):
            self.add_clause([~s[0][j]])
        for i in xrange(1, n-1):
            self.add_clause([~x[i], s[i][0]])
            self.add_clause([~s[i-1][0], s[i][0]])
            for j in xrange(1, k):
                self.add_clause([~x[i], ~s[i-1][j-1], s[i][j]])
                self.add_clause([~s[i-1][j], s[i][j]])
            self.add_clause([~x[i], ~s[i-1][k-1]])
        self.add_clause([~x[n-1], ~s[n-2][k-1]])
        return s

    def at_least_k_of(self, x, k):
        n = len(x)
        if n <= 1:
            return

        s = [[self.add_var() for j in xrange(k)] for i in xrange(n)]
        self.add_clause([~s[0][0], x[0]])
        for j in xrange(1, k):
            self.add_clause([~s[0][j]])
        for i in xrange(1, n):
            for j in xrange(1, k):
                self.add_clause([~s[i][j], s[i-1][j-1]])
                self.add_clause([~s[i][j], s[i-1][j], x[i]])
            self.add_clause([~s[i][0], s[i-1][0], x[i]])
        self.add_clause([s[n-1][k-1]])
        return s


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
        #print 'Variable %s not found !' % name
        seq_name_and_index = name.split('|')

        if len(seq_name_and_index) == 2:
            seq_name, index = name.split('|')
            if seq_name in self.vars:
                return self.vars[seq_name][int(index)]

        #print 'Adding var: %s' % name
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

    ## Obtaining binary value for Var V with respet to solution
    def get_binary_value(self, V, solution):
        """
        V - binary value
        solution: List of integers representing solution
        """
        if solution[V.index-1] > 0:
            return 1
        else:
            return 0


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
                        self.clauses = [[]]
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
                    self.clauses = [[]]
                    return
                new_clauses.append(new_clause)

            self.clauses = new_clauses
            #print 'unit_propagate::clauses:', self.clauses


    ## Performs resolution on particular variable
    def resolution(self, var):
        new_clauses = []
        var_clauses = [clause for clause in self.clauses if var in clause]
        not_var_clauses = [clause for clause in self.clauses if -var in clause]

        # Collecting all clauses that does not contain 'var' variable
        for clause in self.clauses:
            if var not in clause and -var not in clause:
                new_clauses.append(clause)

        # Going through var and -var clauses and merging them together
        for var_clause in var_clauses:
            for not_var_clause in not_var_clauses:
                merged = merge_clauses(var_clause, not_var_clause, var)
                if merged is not None:
                    merged = sorted(merged)
                    if merged not in new_clauses:
                        new_clauses.append(merged)

        self.clauses = new_clauses


    ## Performs superset elimination i.e. removes
    ## clauses which are supersets of other clauses
    def superset_elimination(self):
        i = 0
        while i < len(self.clauses):
            new_clauses = []
            clause_s = set(self.clauses[i])
            for j in xrange(len(self.clauses)):
                if clause_s < set(self.clauses[j]):
                    pass
                else:
                    new_clauses.append(self.clauses[j])
            self.clauses = new_clauses
            i += 1
            

    ## Performs evaluation on particular variable
    def evaluation(self, var):
        new_clauses = []

        # Completing clauses not containing 'var'
        clauses_without_var = [clause for clause in self.clauses if var not in clause]

        # Removing -var from remaining clauses
        for clause in clauses_without_var:
            new_clause = []
            for lit in clause:
                if lit != -var:
                    new_clause.append(lit)
            new_clauses.append(new_clause)
            
        self.clauses = new_clauses

    def entangled(self, var):
        clauses_copy = self.clauses[:]

        # Performing unit propagation and evaluation to simplify formula radically
        self.evaluation(var)
        self.unit_propagate()

        simplified_clauses = self.clauses[:]

        simplified_clauses_set = set([frozenset(clause) for clause in simplified_clauses])
        clauses_set = set([frozenset(clause) for clause in clauses_copy])

        # Keeping only those clauses that were not present in clauses_set
        simplified_clauses_set -= (simplified_clauses_set & clauses_set)

        # for clause in simplified_clauses_set:
        #     if clause 
        self.clauses = clauses_copy

        return simplified_clauses_set


    def vars_set(self):
        vars_set = set()
        for clause in self.clauses:
            for lit in clause:
                var = abs(lit)
                vars_set.add(var)
        return vars_set


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


    ## Expected number of satisfied clauses to number of all clauses
    def sat_expectation(self):
        number_of_clauses = self.clauses_count()

        ## In case there are no clauses to satisfy we can be assured that formula is SAT
        if number_of_clauses == 0:
            return 1

        expected_number_of_sat_clauses = 0.0
        for clause in self.clauses:
            expected_number_of_sat_clauses += (1 - 0.5 ** len(clause))
        return expected_number_of_sat_clauses / number_of_clauses

        
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

    @staticmethod
    def parse_dimacs(filename='f.dimacs'):
        model = Model()
        clauses = []
        with open(filename, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                # Reading only important lines
                if not (stripped_line.startswith('p') or stripped_line.startswith('#')):
                    clause = map(int, stripped_line.split())
                    clauses.append(clause)
        model.clauses = clauses
        return model


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
    print 'm1:'
    print m1
    print m1.Y[3]
    print m1.Z[0]
    print m1.solve()

    m2 = Model()
    m2.add_formula(AND(VAR('X'), NOT(VAR('X'))))
    print 'm2:'
    print m2
    print m2.solve()

    m3 = Model()
    m3.add_formula(AND(OR(VAR('X1'), VAR('X2')), OR(NOT(VAR('X1')), VAR('X2')), OR(VAR('X1'), NOT(VAR('X2'))), OR(NOT(VAR('X1')), NOT(VAR('X2')))))
    print 'm3:'
    print m3
    print m3.solve()

    m4 = Model()
    x1 = m4.add_var('x1')
    x2 = m4.add_var('x2')
    x3 = m4.add_var('x3')
    m4.add_clause([~x1])
    m4.exactly_k_of([x1, x2, x3], 2)
    print 'm4:'
    print m4
    print m4.solve()

    m5 = Model()
    m5.clauses = [[1, 2], [-1, -2], [-1, 2], [1, -2]]
    m5.resolution(1)
    m5.resolution(2)
    print 'm5.clauses:', m5.clauses

if __name__ == '__main__':
    main()
