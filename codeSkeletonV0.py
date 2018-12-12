import curses
import random
import sys
import threading
from threading import Thread
import time
import subprocess
import queue
import pygame #make sure we can install on user's computers.. {maybe do an install from source for deployment!}
from pygame.locals import *


####### <RANDOM THOUGHTS> #######

#premature optimization is the root of all evil!


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
    lock = threading.Lock()
    hero = [0,0] # TODO MAKE HERO AND SHIT A CLASS WITH ROW, COL, AND STRINGS FOR ANIMATIONS!!!
    baddies = [[0,0]]    
    hero_sprite = ''
    zombie_sprite = ''
    bullet_queue = queue.Queue()
      

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

    ze_map.hero = [hero_y, hero_x]   

    baddies = [
        [2, 3],
    ] 

    f = open("Playah.txt", "r")
    ze_map.hero_sprite = f.read()
    #ff = open("Zombie.txt", "r")
    #ze_map.zombie_sprite = ff.read().rstrip()
    ze_map.zombie_sprite_head = '{#_#}'
    ze_map.zombie_sprite_body = ' (o)'


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


## should be run inside a locked function body!
def place_sprite(y, x, sprite):
    if y < sh and y >= 0:
        if x < sw and x >= 0:
            window.addstr(int(y),int(x), sprite)

## should be run inside a locked function body!
def clear_sprite(y, x, sprite):
    if y < sh and y >= 0:
        if x < sw and x >= 0:
            window.addstr(int(y),int(x), sprite)
            # str_size = len(sprite)
            # spaces_str = ""
            # for i in (0,str_size):
            #     spaces_str += " "

# TODO make sure every action is checked to be in map bounds!!
def move_hero(ze_map, keypress):

    ze_map.lock.acquire() # (;
    key = keypress

    #delete old character pos..optimize later - lets see how python can handle it - also it seems like the type of terminal is relevant to updating speed.. research DOM terminal/shell?
    clear_sprite(ze_map.hero[0],ze_map.hero[1], '     ')
    new_hero_pos = ze_map.hero

    if key == curses.KEY_DOWN:
        new_hero_pos[0] += 1
    if key == curses.KEY_UP:
        new_hero_pos[0] -= 1
    if key == curses.KEY_LEFT:
        new_hero_pos[1] -= 1
    if key == curses.KEY_RIGHT:
        new_hero_pos[1] += 1
    elif key == ord('a') :
        bullet_info = [new_hero_pos,'left','•']
        ze_map.bullet_queue.put(bullet_info)
        #fireBullet(ze_map,new_hero_pos,0,'•')

    #update hero pos array
    ze_map.hero = new_hero_pos
    place_sprite(ze_map.hero[0], ze_map.hero[1], ze_map.hero_sprite)
   
    ze_map.lock.release() # ;)


def move_baddies(ze_map):

    while(1):
        ze_map.lock.acquire()

        #clear
        window.addstr(int(ze_map.baddies[0][0]+1), int(ze_map.baddies[0][1]), '     ')
        window.addstr(int(ze_map.baddies[0][0]+2), int(ze_map.baddies[0][1]+1), '   ')

        #calculate
        target = [ze_map.hero[0],ze_map.hero[1]] #hero's "head"
        
        if ze_map.baddies[0][0] < target[0]:
            ze_map.baddies[0][0] += 1
        elif ze_map.baddies[0][0] > target[0]:
            ze_map.baddies[0][0] -= 1

        #place
        window.addstr(int(ze_map.baddies[0][0]),int(ze_map.baddies[0][1]+1), ze_map.zombie_sprite_head)
        window.addstr(int(ze_map.baddies[0][0]+1),int(ze_map.baddies[0][1]+1), ze_map.zombie_sprite_body)
        
        ze_map.lock.release()
        time.sleep(0.5)


def fireBullet(ze_map): 
    while 1:
        bullet_info = None
        try:
            bullet_info = ze_map.bullet_queue.get_nowait() #this should be fine to do before lock.aquire() ..even though it's odd.
        except:
            pass
        if bullet_info is not None:
            bullet_origin = bullet_info[0]
            bullet_direction = bullet_info[1] 
            bullet_type = bullet_info[2]           
            for i in range(1,20):
                ze_map.lock.acquire()
                clear_sprite(bullet_origin[0], bullet_origin[1]+i-1, ' ')
                place_sprite(bullet_origin[0], bullet_origin[1]+i, bullet_type)
                ze_map.lock.release()
                time.sleep(0.05)        



    # window.addstr(int(bulletOrigin[0]),int(bulletOrigin[0]), bulletType)
    # for i in range(1,10): 
    #     ze_map.lock.acquire()
        
    #     #window.addstr(int(bulletOrigin[0]),int(bulletOrigin[0]+i-1), ' ')
    #     window.addstr(int(bulletOrigin[0]),int(bulletOrigin[0]+i), bulletType)
    #     #print (i)

    #     ze_map.lock.release()
    #     time.sleep(0.1)


def main():

    ze_map = ze_map_class()
    lock = threading.Lock()
    init_map(ze_map, lock)
    
    #display_intro_message()
    #display_title()
    
    baddies_thread = Thread(target=move_baddies,args=(ze_map,))
    baddies_thread.daemon = True #exit when main exits
    baddies_thread.start()    
    bullets_thread = Thread(target=fireBullet,args=(ze_map,))
    bullets_thread.daemon = True #exit when main exits
    bullets_thread.start()    

    while True: #TODO stop shit from going off screen and breaking the program lol
        key = window.getch() 
        if key == ord('p'): 
            subprocess.Popen("reset")  #TODO fix this
            quit() # TODO MAKE A PAUSE SCREEN? IF WE HAVE TIME.
        else:
            move_hero(ze_map, key)

        window.border(0)
    
    ## DONT FORGET TO JOIN THY THREADS!
    baddies_thread.join()
    bullets_thread.join()

    subprocess.Popen("reset")  #TODO fix this


"""

 ◖========8 ############################## leggo baby. ################################ 8========D

"""

main()
