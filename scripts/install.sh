git clone https://github.com/openai/gym.git libraries/gym
virtualenv -p /usr/bin/python2.7 rit_go_venv
source rit_go_venv/bin/activate
pip install -e './libraries/gym[board_game]'
