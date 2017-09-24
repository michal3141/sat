from matplotlib import pyplot as plt


def main():
    # number_to_factor,  clauses_to_vars_fact = [], []
    # with open('../results/clauses_to_vars_fact', 'r') as f:
    #     for line in f:
    #         arr = line.strip().split()
    #         number_to_factor.append(int(arr[0]))
    #         clauses_to_vars_fact.append(float(arr[1]))
    # plt.scatter(number_to_factor, clauses_to_vars_fact)
    # plt.xlabel('number of bits')
    # plt.ylabel('clauses-to-variables ratio')
    # plt.savefig('../images/clauses_to_vars_fact.png')
    # plt.show()

    # value_owa, total_time_owa, clauses_to_vars_owa = [], [], []
    # with open('../results/picosat_50_12_6_4_0.300000', 'r') as f:
    #     for line in f:
    #         arr = line.strip().split()
    #         value_owa.append(int(arr[0]))
    #         total_time_owa.append(float(arr[1]))
    #         clauses_to_vars_owa.append(float(arr[4]))
    # plt.scatter(value_owa, total_time_owa)
    # plt.xlabel('target value')
    # plt.ylabel('running time [s]')
    # plt.savefig('../images/picosat_50_12_6_4_0.300000_running_time_vs_target.png')
    # plt.show()
    # plt.scatter(value_owa, clauses_to_vars_owa)
    # plt.xlabel('target value')
    # plt.ylabel('clauses-to-variables ratio')
    # plt.savefig('../images/picosat_50_12_6_4_0.300000_clauses_to_vars_vs_target.png')
    # plt.show()

    value_owa, total_time_owa, clauses_to_vars_owa = [], [], []
    with open('../results/picosat_100_24_10_1_0.300000', 'r') as f:
        for line in f:
            arr = line.strip().split()
            value_owa.append(int(arr[0]))
            total_time_owa.append(float(arr[1]))
            clauses_to_vars_owa.append(float(arr[4]))
    plt.scatter(value_owa, total_time_owa)
    plt.xlabel('target value')
    plt.ylabel('running time [s]')
    plt.savefig('../images/picosat_100_24_10_1_0.300000_running_time_vs_target.png')
    plt.show()
    plt.scatter(value_owa, clauses_to_vars_owa)
    plt.xlabel('target value')
    plt.ylabel('clauses-to-variables ratio')
    plt.savefig('../images/picosat_100_24_10_1_0.300000_clauses_to_vars_vs_target.png')
    plt.show()


if __name__ == '__main__':
    main()