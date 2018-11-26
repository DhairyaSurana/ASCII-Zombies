#Unix Project 4: Top-down Zombie Survival Game

#Creators: Dhairya Surana and Luke Knoble

#==================================================================================================================================================

import curses
import threading

def introMessage():
    
    print("The Zombie game will be launched in 5 seconds")
    
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
timer = threading.Timer(5.0, runGame)
timer.start()
