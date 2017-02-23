#include <iostream>
#include <fstream>
#include <unordered_map>
#include <cstring>

#include <easylogging++.h>

INITIALIZE_EASYLOGGINGPP

void convert_to_ints(char board[81]);

/*!
 * \brief Loads the logging configuration file
 */
void initialize_logging() {
    // Configure the logger
    el::Configurations conf("conf/logging.conf");

    // Turn debug and trace off in release builds
#ifdef NDEBUG
    conf.parseFromText("*DEBUG:\n ENABLED=false");
    conf.parseFromText("*TRACE:\n ENABLED=false");
#else
    conf.parseFromText("*ALL: FORMAT = \"%datetime{%h:%m:%s} [%level] at %loc - %msg\"");
#endif

    el::Loggers::reconfigureAllLoggers(conf);
}

/*!
 * Loads the board positions from the positions file
 *
 * \param positions_file_name The location of the positions file
 * \return A map from zorbitz hash to game board
 */
std::unordered_map<std::string, char[81]> load_positions(std::string positions_file_name) {
    auto positions_file = std::ifstream(positions_file_name);
    auto count = 0;

    if(positions_file.is_open()) {
        auto positions = std::unordered_map<std::string, char[81]>{};

        char zorbitz[8];
        char dummy[8];
        char board_state[81];

        while(!positions_file.eof()) {
            positions_file.read(zorbitz, 8);

            positions_file.read(dummy, 2);

            positions_file.read(board_state, 81);
            convert_to_ints(board_state);

            std::memcpy(board_state, positions[zorbitz], 81 * sizeof(char));

            char has_extra_info;
            positions_file.read(&has_extra_info, 1);

            if (has_extra_info == 1) {
                positions_file.read(dummy, 8);
            }

            count++;
            if (count % 10000 == 0) {
                LOG(INFO) << "Read in " << count << " positions";
            }
        }

        LOG(INFO) << "Read in " << count << " positions total";

        return positions;

    } else {
        throw std::runtime_error("Cannot open positions file " + positions_file_name);
    }
}

/*!
 * \brief Converts the board which is a string into a board which is a number
 *
 * Empty spaces become 0, white pieces become 1, and black pieces become -1
 *
 * \param board The board to convert
 */
void convert_to_ints(char board[81]) {
    for(int i = 0; i < 81; i++) {
        switch(board[i]) {
            case '.':
                board[i] = 0;
                break;
            case '#':
                board[i] = -1;
                break;
            case 'O':
                board[i] = 1;
                break;
            default:
                LOG(ERROR) << "Unsupported character " << int(board[i]) << " in game board";
        }
    }
}

/*!
 * \brief Loads the scores from the scores file
 *
 * \param scores_file_name The location of the scores file
 * \return A map from zorbitz hash to score
 */
std::unordered_map<std::string, int> load_scores(std::string scores_file_name) {
    auto scores_file = std::ifstream(scores_file_name);

    if(scores_file.is_open()) {
        auto scores = std::unordered_map<std::string, int>();

        char zorbitz[8];
        char dummy[2];
        char score;
        char confidence;

        int count = 0;

        while(!scores_file.eof()) {
            scores_file.read(zorbitz, 8);
            scores_file.read(dummy, 2);
            scores_file.read(&score, 1);
            scores_file.read(&confidence, 1);

            scores[zorbitz] = score;

            count++;
            if(count % 10000 == 0) {
                LOG(INFO) << "Read in " << count << " scores";
            }
        }

        LOG(INFO) << "Read in " << count << " scores total";

        return scores;

    } else {
        throw std::runtime_error("Could not open scores file " + scores_file_name);
    }
}

/*!
 * Takes the scores and positions
 *
 * \param positions
 * \param scores
 * \return
 */
std::pair<std::vector<char[81]>, std::vector<int>> corellate_scores_with_positions(
        std::unordered_map<std::string, char[81]> positions,
        std::unordered_map<std::string, int> scores) {
    auto position_list = std::vector<char[81]>{};
    auto score_list = std::vector<int>{};

    for(auto& position_entry : positions) {
        auto score_location = scores.find(position_entry.first);
        if(score_location != scores.end()) {
            position_list.push_back(position_entry.second);
            score_list.push_back((*score_location).second);
        }
    }

    return std::make_pair(position_list, score_list);
}

int main() {
    initialize_logging();

    auto positions = load_positions("data/input_positions.dat");
    auto scores = load_scores("data/fuego_chinese.dat");
    auto data = corellate_scores_with_positions(positions, scores);

    return 0;
}