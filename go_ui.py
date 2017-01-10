import curses

def main():
    ## SETUP
    standard_screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    standard_screen.keypad(1)
    standard_screen.refresh()

    ## TEST
    game_area = curses.newwin(30, 80, 0, 0)
    game_area.box()
    game_area.addstr(1, 1, "Match: A vs. B", curses.A_BOLD)
    game_area.refresh()
    while True:
        user_input = standard_screen.getch()
        if user_input == ord('q'):
            break
        else:
            continue

    ## TEARDOWN
    curses.echo()
    curses.nocbreak()
    standard_screen.keypad(0)
    curses.endwin()

main()
