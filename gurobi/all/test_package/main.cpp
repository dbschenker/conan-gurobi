#include <cstdlib>
#include <gurobi_c++.h>

using namespace std;

int main()
{
    const char* envAppName = getenv("GRB_APP_NAME");
    if (envAppName) cout << "GRB_APP_NAME found" << endl;
    const char* envClientName = getenv("GRB_CLIENT_NAME");
    if (envClientName) cout << "GRB_CLIENT_NAME found" << endl;
    const char* envExpDate = getenv("GRB_EXP_DATE");
    if (envExpDate) cout << "GRB_EXP_DATE found" << endl;
    const char* envSecret = getenv("GRB_SECRET");
    if (envSecret) cout << "GRB_SECRET found" << endl;
    bool haveCIVars { envAppName && envClientName && envExpDate && envSecret };

    bool objectiveValueIsFour { false };
    try {
        GRBEnv env(haveCIVars);
        if (haveCIVars) {
            env.set(GRB_IntParam_OutputFlag, 0);
            env.set("GURO_PAR_ISVNAME", envClientName);
            env.set("GURO_PAR_ISVAPPNAME", envAppName);
            env.set("GURO_PAR_ISVEXPIRATION", envExpDate);
            env.set("GURO_PAR_ISVKEY", envSecret);
            env.start();
            env.set(GRB_IntParam_OutputFlag, 1);
        }
        GRBModel model { env };

        auto x = model.addVar(0.0, 1.0, 0.0, GRB_BINARY, "x");
        auto y = model.addVar(0.0, 1.0, 0.0, GRB_BINARY, "y");

        model.setObjective(x + 3 * y, GRB_MAXIMIZE);
        model.addConstr(x + y <= 2, "upper");
        model.addConstr(x + y >= 1, "lower");

        model.optimize();

        auto objective = model.get(GRB_DoubleAttr_ObjVal);
        objectiveValueIsFour = objective > 3.9 && objective < 4.1;
    } catch (GRBException& e) {
        // If the ISV license information is incorrect, one gets
        // an exception with error code:
        // NO_LICENSE	10009	Failed to obtain a valid license
        cout << "Error code = " << e.getErrorCode() << endl;
        cout << e.getMessage() << endl;
    } catch (...) {
        cout << "Unexpected exception while setting up the Gurobi environment" << endl;
    }

    return objectiveValueIsFour ? EXIT_SUCCESS : EXIT_FAILURE;
}
