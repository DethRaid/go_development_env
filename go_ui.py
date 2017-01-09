import curses


def main():
    ## SETUP
    standard_screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    standard_screen.keypad(1)

    ## TEARDOWN
    curses.echo()
    curses.nocbreak()
    standard_screen.keypad(0)
    curses.endwin()

main()
