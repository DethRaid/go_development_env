import curses


def main():
    ## SETUP
    standard_screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    standard_screen.keypad(1)

    ## TEST
    standard_screen.addstr(1, 5, "Lorem Ipsum Dolor sit amet", curses.A_BOLD)
    standard_screen.refresh()
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
