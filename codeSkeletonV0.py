import curses
import random
import sys
import threading
import time

import pygame #make sure we can install on user's computers.. {maybe do an install from source for deployment!}
from pygame.locals import *

# clock = pygame.time.Clock()

####### <RANDOM THOUGHTS> #######

# TODO come to a conclusion on how we'll be sharing all the variables..
# currently shared variables:
# window
# map .. lets use a struct!

####### </RANDOM THOUGHTS> ########


     

####### INITILIZATIONZ ###########

s = curses.initscr()
curses.curs_set(0)
sh, sw = s.getmaxyx() #TODO CREATE A SET SCREEN SIZE.
window = curses.newwin(sh, sw, 0, 0)
window.nodelay(True)    #does this actually work?
window.keypad(1)    #What does this do?


curses.start_color()

#window.addstr((sh // 2) - 5, (sw // 2) - 15, "Sudochad Stud|os presents . . .", curses.color_pair(YELLOW_TEXT))

window.border(0)
window.timeout(100) #and this?

#the pygame init function was causing a lot of errors 
#pygame.mixer.init(44100, -16,2,2048) #I dunno what all these numbers do.. but it makes the sound work! :P

####### </INITILIZATIONZ> ###########


class ze_map_class:
    #self.lock = None     #lock = threading.Lock()
    hero = [ [0,0],[0,0] ] # change size as needed.
    baddies = [[0,0]]    

    # def __init__(): #tbh idu the syntax and shit here.
    #     hero_x =  sw / 4
    #     hero_y =  sh / 2

    #     ze_map.hero = [
    #     [hero_y, hero_x],
    #     [hero_y, hero_x-1],
    #     ] 

    #     baddies = [
    #     [hero_y/2, hero_x/2],
    #     ] 


def dynamic_print(timeSpan, x, y, text, color):

     tempX = x

     for i in range(len(text)):
        window.addstr(y, tempX, text[i], curses.color_pair(color))
        window.refresh()
        time.sleep(timeSpan)
        tempX+=1


def init_map(ze_map, lock):
    ze_map.lock = lock
    
    hero_x =  sw / 4
    hero_y =  sh / 2

    ze_map.hero = [
        [hero_y, hero_x],
        [hero_y, hero_x-1],
    ] 

    baddies = [
        [hero_y/2, hero_x/2],
    ] 

def display_intro_message():

    YELLOW_TEXT = 1
    RED_TEXT = 2

    curses.init_pair(YELLOW_TEXT, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    dynamic_print(0.2,(sw // 2) - 15, (sh // 2) - 5, "Sudochad Stud|os presents ...", YELLOW_TEXT)
    time.sleep(3)
    dynamic_print(0.1, (sw // 2) - 15, (sh // 2) - 5, "                             ", YELLOW_TEXT)
    
    curses.init_pair(RED_TEXT, curses.COLOR_RED, curses.COLOR_BLACK)
    dynamic_print(0.5, (sw // 2) - 10, (sh // 2), "ASCII ZOMBIES", RED_TEXT)
    time.sleep(2)
    dynamic_print(0.05, (sw // 2) - 10, (sh // 2), "              ", RED_TEXT)


def display_title():
    sys.stdout.flush()
    
    crash_sound = pygame.mixer.Sound("crash.wav")
    pygame.mixer.Sound.play(crash_sound)

    pygame.mixer.music.load('jazz.wav') #works!
    pygame.mixer.music.play(-1)
    
    text = "Sudochad Stud|os presents..."
    for character in text:
        print(character, end = "")
        time.sleep(0.125) #sexy but too slow for debugging
        #time.sleep(.03)
        sys.stdout.flush()
    time.sleep(.12)


def move_hero(ze_map):

    #ze_map.lock.acquire() # (;

    key = window.getch()   #TODO figure out how to grab 2 keys at once for moving and shooting, etc..

    #delete old character pos..optimize later - lets see how python can handle it - also it seems like the type of terminal is relevant to updating speed.. research DOM terminal/shell?
    window.addch(int(ze_map.hero[0][0]),int(ze_map.hero[0][1]), ' ')
    window.addch(int(ze_map.hero[1][0]),int(ze_map.hero[1][1]), ' ')

    new_hero_head = [ze_map.hero[0][0], ze_map.hero[0][1]]

    if key == curses.KEY_DOWN:
        new_hero_head[0] += 1
    if key == curses.KEY_UP:
        new_hero_head[0] -= 1
    if key == curses.KEY_LEFT:
        new_hero_head[1] -= 1
    if key == curses.KEY_RIGHT:
        new_hero_head[1] += 1

    #update hero pos array
    ze_map.hero[0] = new_hero_head
    ze_map.hero[1] = [ze_map.hero[0][0] + 1, ze_map.hero[0][1]]

    window.addch(int(ze_map.hero[0][0]),int(ze_map.hero[0][1]), '8')
    window.addch(int(ze_map.hero[1][0]),int(ze_map.hero[1][1]), '0')
   
    #ze_map.lock.release() # ;)

def move_baddies(ze_map, lock):

    while(1):
        ze_map.lock.aquire()

        #clear
        window.addstr(int(ze_map.baddies[0][0]), int(ze_map.baddies[0][1]), '  ')

        #calculate
        target = [ze_map.hero[0][0],ze_map.hero[0][1]] #hero's "head"
        
        if ze_map.baddies[0][0] < target[0]:
            ze_map.baddies[0][0] += 1
        elif ze_map.baddies[0][0] > target[0]:
            ze_map.baddies[0][0] -= 1

        #place
        window.addstr(int(ze_map.baddies[0][0]),int(ze_map.baddies[0][1]), '):')
        
        ze_map.lock.release()
        time.sleep(0.5)

def test_threading(bleh, y):
    time.sleep(5)
    print("diiiiiicj")
    print(bleh)
    print(y)

def main():
    ze_map = ze_map_class()
    lock = threading.Lock()
    init_map(ze_map, lock)


    
    display_intro_message()
    
    
    #display_title()

    
    #baddies_thread = threading.Thread(target=move_baddies,args=ze_map)
    #baddies_thread.start()    
    # bleh = "bnlkasdjf"
    # y = "asd"
    # t1 = threading.Thread(target=test_threading, args=(bleh,y))
    # t1.start()

    while True: #TODO stop shit from going off screen and breaking the program lol
        # key = window.getch() 
        # if key == 'p':
        #     quit()

        move_hero(ze_map)
        
        
    #baddies_thread.join()
    #t1.join()
        


"""

 ◖========8 ############################## leggo baby. ################################ 8========D

"""

main()
