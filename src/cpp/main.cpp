#include <iostream>

auto load_positions(std::string positions_file_name) {
    auto positions_file = std::ifstream(positions_file_name);

    if(positions_file.open()) {

    } else {
        throw std::runtime_error("Cannot open positions file " + positions_file_name);
    }
}

int main() {
    auto positions = load_positions("data/input_positions.dat");
    std::cout << "Hello, World!" << std::endl;
    return 0;
}