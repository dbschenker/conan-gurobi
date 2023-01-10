#include <cstdlib>
#include <gurobi_c++.h>

using namespace std;

int main() {
    GRBEnv env {};
    GRBModel model { env };

    auto x = model.addVar(0.0, 1.0, 0.0, GRB_BINARY, "x");
    auto y = model.addVar(0.0, 1.0, 0.0, GRB_BINARY, "y");

    model.setObjective(x + 3 * y, GRB_MAXIMIZE);
    model.addConstr(x + y <= 2, "upper");
    model.addConstr(x + y >= 1, "lower");

    model.optimize();

    auto objective = model.get(GRB_DoubleAttr_ObjVal);
    bool objectiveValueIsFour = objective > 3.9 && objective < 4.1;
    return objectiveValueIsFour ? EXIT_SUCCESS : EXIT_FAILURE;
}
