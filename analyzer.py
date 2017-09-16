from collections import defaultdict

class FormulaAnalyzer(object):
    def __init__(self, cnf):
        self.cnf = cnf

    def count_variables(self):
        ret = defaultdict(int)
        for clause in self.cnf:
            for var in clause:
                ret[var] += 1
        return ret

    ## Collision is a situation when in one clause there is x and in the other one is ~x
    ## Each such pair is a collision. This function returns collision count over all variables
    def count_collisions(self):
        ret = 0
        var_count = self.count_variables()
        for var_num in var_count.keys():
            if var_num > 0:
                ret = ret + var_count[var_num] * var_count[-var_num]
        return ret


    ## Counting minimum number of clauses that have to be unsat in the given 1CNF
    def count_unsat_clauses_1cnf(self):
        ## Assuring that our formula is in 1CNF form:
        for clause in self.cnf:
            if len(clause) != 1:
                raise Exception('Formula %r is not in 1CNF form' % self.cnf)
        ret = 0
        var_count = self.count_variables()
        for var_num in var_count.keys():
            if var_num > 0:
                ret = ret + min(var_count[var_num], var_count[-var_num])
        return ret

    
    def count_literals(self):
        negative_count = 0
        positive_count = 0
        for clause in self.cnf:
            for var in clause:
                if var < 0: 
                    negative_count += 1
                else:
                    positive_count += 1
        return {
            'negative': negative_count,
            'positive': positive_count
        }


def main():
    pass

if __name__ == '__main__':
    main()
