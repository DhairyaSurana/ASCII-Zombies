#Unix Project 4: Top-down Zombie Survival Game

#Creators: Dhairya Surana and Luke Knoble

#==================================================================================================================================================

import curses
import time
from math import *


def introMessage():

    for second in range(5, 0, -1):
        
       if(second != 1):
           print("The Zombie game will be launched in " + str(second) + " seconds", end = "\r")
       else:
           print("The Zombie game will be launched in " + str(second) + " second ", end = "\r")

       time.sleep(1)
        


def runGame():

    screen = curses.initscr()
    curses.curs_set(0)
    
    sh, sw = screen.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.border(0)
    w.timeout(100)
    curses.initscr()
    
    
    while (True):

        key = w.getch()
        

      
introMessage()
runGame()


