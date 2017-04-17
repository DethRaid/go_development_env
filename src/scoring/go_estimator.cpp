//
// Created by ddubois on 4/17/17.
//

#include "go_estimator.h"

int go_scorer_score(int** board) {
    score_estimator::Goban goban;
    goban.setSize(9, 9);
    for(int y = 0; y < 9; y++) {
        for(int x = 0; x < 9; x++) {
            goban.board[y][x] = board[y][x];
        }
    }

    return goban.estimate(score_estimator::WHITE, 10000, 0.35).score();
}
