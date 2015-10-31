import sys
from factmodel import FactorizationModel

def main():
    n = int(sys.argv[1])
    for i in xrange(1, n+1):
        sat = FactorizationModel()
        number = i
        bin_number = bin(number)[2:]
        len_bin_number = len(bin_number)

        N = sat.add_integer('N', number, length=len_bin_number*2)
        l = len(N)
        P = sat.add_seq('P', l)
        Q = sat.add_seq('Q', l)

        sat.add_multiplication(P, Q, N)
        solution = sat.solve()

        if solution != 'UNSAT':
            print '%d = %d * %d' % (number, sat.get_decimal_value(P, solution), sat.get_decimal_value(Q, solution))
        else:
            print '%d is prime' % number

if __name__ == '__main__':
    main()