#include <cstdlib>
#include <gurobi_c++.h>

using namespace std;

int main()
{
    const char* envAppName = std::getenv("GRB_APP_NAME");
    const char* envClientName = std::getenv("GRB_CLIENT_NAME");
    const char* envExpDate = std::getenv("GRB_EXP_DATE");
    const char* envSecret = std::getenv("GRB_SECRET");
    bool haveCIVars { envAppName && envClientName && envExpDate && envSecret };

    GRBEnv env(haveCIVars);
    if (haveCIVars) {
        // todo env.set()
    }
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
