//
// Created by ddubois on 4/17/17.
//

#ifndef GO_AI_ESTIMATOR_H
#define GO_AI_ESTIMATOR_H

#include "../../score-estimator/estimator.h"

extern "C" {
    int go_scorer_score(int** board);
};

#endif //GO_AI_ESTIMATOR_H
