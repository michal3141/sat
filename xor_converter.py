from model import Model 
from pycryptosat import Solver

def solve_xor(model):
    s = Solver()
    for clause in model.clauses:
        s.add_xor_clause(_only_positive(clause), rhs=_get_clause_parity(clause))
    return s.solve()

def solve_or(model):
    s = Solver()
    for clause in model.clauses:
        s.add_clause(clause)
    return s.solve()

    
def _get_clause_parity(clause):
    total_negated = 0
    for lit in clause:
        if lit < 0:
            total_negated += 1
    return total_negated % 2 == 1

def _only_positive(clause):
    ret = []
    for lit in clause:
        ret.append(abs(lit))
    return ret

def main():
    pass

if __name__ == '__main__':
    main()