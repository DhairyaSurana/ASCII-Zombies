#Unix Project 4: Top-down Zombie Survival Game

#Creators: Dhairya Surana and Luke Knoble

#==================================================================================================================================================

import curses
import time
import sys

def introMessage():

    seconds = [5, 4, 3, 2, 1]
    for second in seconds:
       print("The Zombie game will be launched in " + str(second) + " seconds", end = "\r")
       time.sleep(1)
        
       

def runGame():

    screen = curses.initscr()
    curses.curs_set(0)
    sh, sw = screen.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.timeout(100)

    key = w.getch()

    while (True):
        
        if(key == curses.KEY_ENTER):
            curses.endwin()
            quit()
       

     
      
introMessage()
runGame()
