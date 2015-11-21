from inequalities import InequalityModel


class ILPModel(InequalityModel):
    def __init__(self, length=8):
        super(ILPModel, self).__init__()
        self.length = length


    def add_seq(self, name=None, l=None):
        name = name if name is not None else self.get_seq_name()
        length = l if l is not None else self.length
        seq = super(ILPModel, self).add_seq(name, length=length)
        seq.model = self
        return seq


    def add_integer(self, name, value):
        integer = super(ILPModel, self).add_integer(name, value, length=self.length)
        integer.model = self
        return integer


def main():
    m1 = ILPModel(length=5)
    X = m1.add_seq('X')
    Y = m1.add_seq('Y')
    Z = m1.add_seq('Z')
    3*X + Y + 2*Z == 17
    2*Y + Z == 10
    2*X + 3*Z == 16

    # print m1
    # Getting solution
    solution = m1.solve()
    # print solution
    if solution != 'UNSAT':
        print 'X:', m1.get_decimal_value(X, solution)
        print 'Y:', m1.get_decimal_value(Y, solution)
        print 'Z:', m1.get_decimal_value(Z, solution)

    m2 = ILPModel(length=5)
    X = m2.add_seq()
    Y = m2.add_seq()
    Y <= X + 1
    3*X + 2*Y <= 12
    2*X + 3*Y <= 13

    # print m1
    # Getting solution
    solution = m2.solve()
    # print solution
    if solution != 'UNSAT':
        print 'X:', m2.get_decimal_value(X, solution)
        print 'Y:', m2.get_decimal_value(Y, solution)

if __name__ == '__main__':
    main()