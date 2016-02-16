#include <iostream>
#include <cmath>
#include <random>

// Number of variables
int nvars;

// Number of clauses
int nclauses;

// Size
int size;

// Number of satisfied paths
int nsatpaths;

// UNSAT counter
int conflict_count = 0;

// Number of formulas having certain property
int formulas_count = 0;

// Representing boolean formula
int *formula;

// Representing seen variables. 0 - empty, 1 - seen X, -1 - seen ~X
int *seen;

std::random_device rd;     // only used once to initialise (seed) engine
std::mt19937 rng(rd());    // random-number engine used (Mersenne-Twister in this case)
std::uniform_int_distribution<int> *uni; // guaranteed unbiased

void print_current_formula();

void print_seen() {
    for (int i = 1; i <= nvars; ++i) {
        if (seen[i] == 1) {
            std::cout << i << " ";
        } else if (seen[i] == -1) {
            std::cout << -i << " ";
        }
    }
    std::cout << std::endl;
}

void inspect_current_formula(int i) {
    if (i < nclauses) {
        int first = formula[2*i];
        int first_abs = std::abs(first);
        int tmp_seen = seen[first_abs];
        if ((tmp_seen == 1 && first < 0) || (tmp_seen == -1 && first > 0)) {
            conflict_count += std::pow(3, nclauses - i - 1);
        } else {
            if (first > 0)
                seen[first_abs] = 1;
            else
                seen[first_abs] = -1;
            inspect_current_formula(i+1);
            seen[first_abs] = tmp_seen;
        }

        int second = formula[2*i+1];
        int second_abs = std::abs(second);
        tmp_seen = seen[second_abs];
        if ((tmp_seen == 1 && second < 0) || (tmp_seen == -1 && second > 0)) {
            conflict_count += std::pow(3, nclauses - i - 1); 
        } else {
            if (second > 0)
                seen[second_abs] = 1;
            else
                seen[second_abs] = -1; 
            inspect_current_formula(i+1);
            seen[second_abs] = tmp_seen;
        }

        int third = formula[2*i+2];
        int third_abs = std::abs(third);
        tmp_seen = seen[third_abs];
        if ((tmp_seen == 1 && third < 0) || (tmp_seen == -1 && third > 0)) {
            conflict_count += std::pow(3, nclauses - i - 1); 
        } else {
            if (third > 0)
                seen[third_abs] = 1;
            else
                seen[third_abs] = -1; 
            inspect_current_formula(i+1);
            seen[third_abs] = tmp_seen;
        }
    } else {
        //print_seen();
    }
}

void evaluate_formula() {
    // Zeroing seen so that none of the variables was observed up to the point
    for (int j = 0; j <= nvars; ++j) {
        seen[j] = 0;
    }
    conflict_count = 0;
    inspect_current_formula(0);
                  
    int sat_paths_count = std::pow(3, nclauses) - conflict_count;
    if (sat_paths_count == nsatpaths) {
        ++formulas_count;
        //print_current_formula();
        //std::cout << "satisfied paths count: " << sat_paths_count << std::endl;
    }     
}

// Generating all 3-SAT formulas with nvars and nclauses
void gen_formulas(int i) {
    if (i < size) {
        for (int j = 1; j <= nvars; ++j) {
            formula[i] = j;
            gen_formulas(i+1);
            formula[i] = -j;
            gen_formulas(i+1);
        }
    }
    else if (i == size) {
        evaluate_formula();
    }
}

// Generating all 3-SAT formulas with distinct literal clauses 
// (i.e it is forbidden to have a clause of a type: (x, x))
void gen_distinct_formulas(int i) {
    if (i < size) {
        for (int j = 1; j <= nvars; ++j) {
            if (i % 3 == 0) {
                formula[i] = j;
                gen_distinct_formulas(i+1);
                formula[i] = -j;
                gen_distinct_formulas(i+1);
            } else if (i % 3 == 1) {
                if (formula[i-1] != j) {
                    formula[i] = j;
                    gen_distinct_formulas(i+1);
                }
                if (formula[i-1] != -j) {
                    formula[i] = -j;
                    gen_distinct_formulas(i+1);
                }
            } else if (i % 3 == 2) {
                 if (formula[i-1] != j && formula[i-2] != j) {
                    formula[i] = j;
                    gen_distinct_formulas(i+1);
                }
                if (formula[i-1] != -j && formula[i-2] != -j) {
                    formula[i] = -j;
                    gen_distinct_formulas(i+1);
                }               
            }
        }
    }
    else if (i == size) {
        evaluate_formula();
    }
}

// Getting random literal
int random_lit() {
    int ret;
    do {
        ret = uni->operator()(rng);
    } while (ret == 0);
    return ret;
}


// Generating random 3-SAT formula with nvars and nclauses
void gen_random() {
    for (int i = 0; i < size; ++i) {
        formula[i] = random_lit();
    }

}

void print_current_formula() {
    for (int j = 0; j < size; ++j) {
        std::cout << formula[j] << ", ";
    }
    std::cout << std::endl;
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <nvars> <nclauses> <nsatpaths>" << std::endl;
        return -1;
    }

    nvars = atoi(argv[1]);
    nclauses = atoi(argv[2]);
    nsatpaths = atoi(argv[3]);
    size = 3 * nclauses;
    uni = new std::uniform_int_distribution<int>(-nvars, nvars);

    std::cout << "nvars: " << nvars << std::endl;
    std::cout << "nclauses: " << nclauses << std::endl;
    std::cout << "nsatpaths: " << nsatpaths << std::endl;

    formula = new int[size];
    seen = new int[nvars+1];

    //gen_distinct_formulas(0);
    gen_formulas(0);
    //const unsigned long long MAX = 1000000ULL;
    //for (unsigned long long l = 0; l < MAX; ++l) {
    //    gen_random();
    //    evaluate_formula();
    //}

    std::cout << "formulas_count: " << formulas_count << std::endl;

    return 0;
}
