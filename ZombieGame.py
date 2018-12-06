#Unix Project 4: Top-down Zombie Survival Game

#Creators: Dhairya Surana and Luke Knoble

#==================================================================================================================================================

import curses
import time
import sys


def printTextSlowly(text):

    for character in text:
        print(character, end = "")
        time.sleep(0.125)
        sys.stdout.flush()

def introMessage():

    printTextSlowly("Sudochad Stud|os presents...")
    time.sleep(3)

def runGame():

    screen = curses.initscr()
    curses.curs_set(0)
    
    sh, sw = screen.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.border(0)
   # w.addstr(x = 5, y = 5, "Gay")
    w.timeout(100)
    
    while (True):

        key = w.getch()

introMessage()
runGame()

#Test comment