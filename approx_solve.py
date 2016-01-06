## This is an approximation algorithm for MAX 3-SAT. The basic idea here is to follow
## the greedy heuristic based on expected satisifiability ratio i.e. ratio defined as number of
## satisfied clauses to number of all clauses

import sys

from model import Model

def approx_solve(f):
    while True:
        f.unit_propagate()

        print 'f.clauses:', f.clauses
        if len(f.clauses) == 0:
            print 'SAT'
            break
        elif [] in f.clauses:
            print 'UNSAT'
            break
        elif f.clauses == [[1], [-1]]:
            print 'UNSAT'
            break

        orig_clauses = f.clauses[:]

        best_value = 0
        best_var = 0

        for var in f.vars_set():
            f.clauses = orig_clauses[:]
            f.evaluation(var)
            var_sat_expectation = f.sat_expectation()
            print 'sat_expectation for: %d = %f' % (var, var_sat_expectation) 

            if var_sat_expectation > best_value:
                best_var = var
                best_value = var_sat_expectation


            f.clauses = orig_clauses[:]
            f.evaluation(-var)
            not_var_sat_expectation = f.sat_expectation()
            print 'sat_expectation for: %d = %f' % (-var, not_var_sat_expectation) 

            if not_var_sat_expectation > best_value:
                best_var = -var
                best_value = not_var_sat_expectation

        f.clauses = orig_clauses[:]

        print 'best_var: %d' % best_var
        print 'best_value: %f' % best_value

        # Greedy evaluation based on satisfiability expectation
        # if var_sat_expectation >= not_var_sat_expectation:
        f.evaluation(best_var)
        # else:
        #     f.evaluation(-var)

        if len(f.clauses) == 0:
            print 'SAT'
            break

def analyze_entanglement(f):
    f.unit_propagate()

    unsat_count = 0
    # print 'f.clauses: %r' % f.clauses

    for var in f.vars_set():
        entangled_var = f.entangled(var)
        entangled_not_var = f.entangled(-var)

        if len(entangled_var) == 1:
            # print 'f.entangled_clauses[%d]: %r' % (var, entangled_var)
            unsat_count += 1
        # print 'len(f.entangled_clauses[%d]): %d' % (var, len(entangled_var))
        if len(entangled_not_var) == 1:
            # print 'f.entangled_clauses[%d]: %r' % (-var, entangled_not_var)
            unsat_count += 1
        # print 'len(f.entangled_clauses[%d]): %d' % (-var, len(entangled_not_var))

    print 'unsat_count = %d' % unsat_count

def entaglement_solve(f):
    f.unit_propagate()

    while True:
        print 'f.clauses: %r' % f.clauses

        if f.clauses == [] or f.clauses == [[]]:
            break

        eval_vars = []
        # eval_var = 0
        for var in f.vars_set():
            entangled_var = f.entangled(var)
            entangled_not_var = f.entangled(-var)
            if len(entangled_var) == 1:
                print 'f.entangled_clauses[%d]: %r' % (var, entangled_var)
                # eval_var = -var
                eval_vars.append(-var)
                # break
            if len(entangled_not_var) == 1:
                print 'f.entangled_clauses[%d]: %r' % (-var, entangled_not_var)
                # eval_var = var
                eval_vars.append(var)
                # break
        if len(eval_vars) == 0:
            print 'No variable found to perform evaluation on !'
            break
        for eval_var in eval_vars:
            print 'Performing evaluation with: %d' % eval_var
            f.evaluation(eval_var)
            f.unit_propagate()


def main():
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)

    # approx_solve(f)
    # analyze_entanglement(f)
    entaglement_solve(f)

if __name__ == '__main__':
    main()