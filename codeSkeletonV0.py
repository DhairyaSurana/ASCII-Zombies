import curses
import random
import sys
import threading
from threading import Thread
import time
import subprocess
import queue
# $ python3.7 -m pip install pygame
import pygame #make sure we can install on user's computers.. {maybe do an install from source for deployment!}
from pygame.locals import *
import numpy as np   #non stl.. $ pip3 install numpy # $python3.7 -m pip install numpy


####### <RANDOM THOUGHTS> #######

#premature optimization is the root of all evil!


####### </RANDOM THOUGHTS> ########


####### INITILIZATIONZ ###########

s = curses.initscr()
curses.curs_set(0)
sh, sw = s.getmaxyx() #TODO CREATE A SET SCREEN SIZE.
window = curses.newwin(sh, sw, 0, 0)
barWindow = curses.newwin(sh//4, sw//4, 5, 5)

window.nodelay(True)    #does this actually work?
barWindow.nodelay(True)

window.keypad(1)    #What does this do?
barWindow.keypad(1)

curses.start_color()
curses.noecho()

time_start = time.time()
last_time_fired = time.time()
hero_func_first_run = 1
zomb_func_first_run = 1

window.border(0)
window.timeout(100) #and this?

#the pygame init function was causing a lot of errors 
#pygame.mixer.init(44100, -16,2,2048) #I dunno what all these numbers do.. but it makes the sound work! :P

hero_sprite_type = 1
old_health = 10
old_points = 10
#old_health_bar = "❤" * old_health
####### </INITILIZATIONZ> ###########

class turret:

    col = 0
    row = 0
    health = 10

    facing_up_ln1 =   "++||++"
    facing_up_ln2 =   "+ [] +"
    facing_up_ln3 =   "++++++"
    
    facing_down_ln1 = "++++++"
    facing_down_ln2 = "+ [] +"
    facing_down_ln3 = "++||++"
    
    facing_right_ln1 = "++++++"
    facing_right_ln2 = "+ I==="
    facing_right_ln3 = "++++++"

    facing_left_ln1 = "++++++"
    facing_left_ln2 = "===I +"
    facing_left_ln3 = "++++++"

class hero:
    col = 0
    row = 0
    health = 10
    points = 10

    spriteRest = "┌(ᶱ1ᶱ)┐"

    spriteMove1 = "┌(ᶱ1ᶱ)┘"
    spriteMoveFired1 = "┌(ᶱ.ᶱ)┘"

    spriteMove2 = "└(ᶱ1ᶱ)┐"
    spriteMoveFired2 = "└(ᶱ.ᶱ)┐"
    len_of_sprite = 7 #UPDATE IF MORE SPRITES COME


class zombie:
    col = 0
    row = 0

    zombie_sprite_left_attack_head ='~{#_#}'
    zombie_sprite_right_attack_head ='{#_#}~' #TODO make bodies too and implement
    
    zombie_sprite_head = '{#_#}'
    zombie_sprite_body = ' (o)'

    len_of_row0 = 5
    len_of_row1 = 3
    offset_of_row1 = 1


class environment:
    lock = threading.Lock()
    #hero = [0,0] # TODO MAKE HERO AND SHIT A CLASS WITH ROW, COL, AND STRINGS FOR ANIMATIONS!!!
    baddies = [0,0]  
    player = hero()  
    baddy = zombie()
    hero_sprite = ''
    zombie_sprite = ''
    playerTurret = turret()
    bullet_queue = queue.Queue()
    checkerboard = np.zeros((sh,sw),dtype=int) 
    #0 for nothing there, -1 for player, -2 for turret, -10 for walls, 1 to inf correspond to zombos
      

def dynamic_print(timeSpan, x, y, text, color):

     tempX = x

     for i in range(len(text)):
        window.addstr(y, tempX, text[i], curses.color_pair(color))
        window.refresh()
        time.sleep(timeSpan)
        tempX+=1

def boundError(x, y):

    if(x > sw or y > sh):
        print("Values are not within bounds")
        return True

    return False

def drawHealthBar(x, y, health):

    global old_health
    #global old_health_bar

    if(health != old_health):

        old_health_bar = "❤ " * old_health
        clear_sprite(y, x + 8, old_health_bar)
        old_health = health

    if(not boundError(x, y)):
        window.addstr(y, x, "Health: ", curses.A_BOLD)

    if(not boundError(x + 8, y)):
        
        RED_TEXT = 1
        curses.init_pair(RED_TEXT, curses.COLOR_RED, curses.COLOR_BLACK)

        bar = "❤ " * health
          #  old_health_bar = bar
        window.addstr(y, x + 8, bar, curses.color_pair(RED_TEXT))

def drawPointBar(x, y, points):

    global old_points

    if(points != old_points):

        old_points_bar = "$ " * old_points
        clear_sprite(y, x + 8, old_points_bar)
        old_points = points

    if(not boundError(x, y)):
        window.addstr(y, x, "Points: ", curses.A_BOLD)

    if(not boundError(x + 8, y)):
        
        YELLOW_TEXT = 2
        curses.init_pair(YELLOW_TEXT, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        bar = "$ " * points
        window.addstr(y, x + 8, bar, curses.color_pair(YELLOW_TEXT))

def init_map(env, lock):
    env.lock = lock
    
    hero_x =  sw / 4
    hero_y =  sh / 2

    env.player.row = hero_y
    env.player.column =  hero_x

    baddies = [
        [2, 3],
    ] 

    #sets the initial sprite for the player
    env.hero_sprite = env.player.spriteRest 


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

    space = " " * len(sprite)
    if y < sh and y >= 0:
        if x < sw and x >= 0:
            window.addstr(int(y),int(x), space)
            # str_size = len(sprite)
            # spaces_str = ""
            # for i in (0,str_size):
            #     spaces_str += " "


# TODO make sure every action is checked to be in map bounds!!
def move_hero(env, keypress):

    global last_time_fired
    global hero_sprite_type
    global hero_func_first_run
    
    env.lock.acquire() ####### (;

    key = keypress

    bulletFired = False

    #delete old character pos..optimize later - lets see how python can handle it - also it seems like the type of terminal is relevant to updating speed.. research DOM terminal/shell?
    clear_sprite(env.player.row, env.player.col, env.hero_sprite)
    #clear from the map
    if not hero_func_first_run:
        row = int(env.player.row)
        col = int(env.player.col)
        for i in range(0,6):
            if(env.checkerboard[row][col+i] != -1):
                window.addstr(8,10, "ERROR IN CLEARING HERO")
                window.addstr(10,10, "hero row" + str(row))
                window.addstr(12,10, "hero col" + str(col))
            env.checkerboard[row][col+i] = 0
    hero_func_first_run = False
        
    new_hero_pos = [env.player.row, env.player.col]

    if key == curses.KEY_DOWN:
        if placement_is_valid(row + 1, col, env, env.baddy.zombie_sprite_head, env.baddy.zombie_sprite_body):
            new_hero_pos[0] += 1
    elif key == curses.KEY_UP:
        if(env.player.health !=  10):#For testing purposes, remove once done
            env.player.health+=1 #For testing purposes, remove once done
        if placement_is_valid(row - 1, col, env, env.baddy.zombie_sprite_head, env.baddy.zombie_sprite_body):
            new_hero_pos[0] -= 1
    elif key == curses.KEY_LEFT:
        if placement_is_valid(row, col - 1, env, env.baddy.zombie_sprite_head, env.baddy.zombie_sprite_body):
            new_hero_pos[1] -= 1
    elif key == curses.KEY_RIGHT:
        if placement_is_valid(row, col + 1, env, env.baddy.zombie_sprite_head, env.baddy.zombie_sprite_body):
            new_hero_pos[1] += 1

    if key == ord('d') or key == ord('D') or key == ord('a') or key == ord('A') or key == ord('s') or key == ord('S') or key == ord('w') or key == ord('W'):
        bulletFired = True
        env.player.health-=1 #For testing purposes, remove once done
        if(time.time() > (last_time_fired)+ 0.45):
            last_time_fired = time.time()
            if key == ord('d') or key == ord('D'):
                bullet_info = [new_hero_pos,'right','•']
                env.bullet_queue.put(bullet_info)
            elif key == ord('a') or key == ord('A'):
                bullet_info = [new_hero_pos,'left','•']
                env.bullet_queue.put(bullet_info)
            elif key == ord('w') or key == ord('W'):
                bullet_info = [new_hero_pos,'up','•']
                env.bullet_queue.put(bullet_info)
            elif key == ord('s') or key == ord('S'):
                bullet_info = [new_hero_pos,'down','•']
                env.bullet_queue.put(bullet_info)
    
    if env.player.points == 10:
        window.addstr((sh // 2) - ((sh // 2) - 2), (sw // 2) - ((sw // 2) - 30), "Press E to build a turret", curses.A_BLINK)

        if key == ord('e'):
            clear_sprite((sh // 2) - ((sh // 2) - 2), (sw // 2) - ((sw // 2) - 30), "Press E to build a turret")
            place_turret(int(env.player.row), int(env.player.col) + 5, env)
            env.player.points = 0

    elif env.player.points != 10:
        if key == ord('i'):
            env.player.points+=1
        
    if hero_sprite_type == 1:
        if bulletFired:
            env.hero_sprite = env.player.spriteMoveFired1
        else:
            env.hero_sprite = env.player.spriteMove1
    elif hero_sprite_type == 2:
        if bulletFired:
            env.hero_sprite = env.player.spriteMoveFired2
        else:
            env.hero_sprite = env.player.spriteMove2

        hero_sprite_type = 0

    #update hero pos array
    env.player.row = new_hero_pos[0]
    env.player.col = new_hero_pos[1]
    place_sprite(env.player.row, env.player.col, env.hero_sprite)
    #update hero on backend
    row = int(env.player.row)
    col = int(env.player.col)
    for i in range(0,6):
        if(env.checkerboard[row][col+i] != 0):
            window.addstr(8,10, "ERROR hero stepping in bad spot")
            window.addstr(10,10, "hero row " + str(row))
            window.addstr(12,10, "hero col " + str(col))
        env.checkerboard[row][col+i] = -1
   
    hero_sprite_type+=1
    env.lock.release() # ;)


def move_baddies(env):
    global zomb_func_first_run
    while(1):
        env.lock.acquire()

    # zombie_sprite_head = '{#_#}'
    # zombie_sprite_body = ' (o)'

        clear_sprite(env.baddy.row, env.baddy.col + 1, env.baddy.zombie_sprite_head)
        clear_sprite(env.baddy.row + 1, env.baddy.col + 1, env.baddy.zombie_sprite_body)
        row = int(env.baddy.row)
        col = int(env.baddy.col)
        if(zomb_func_first_run == 0):
            for i in range(0,4):
                if(env.checkerboard[row][col+i] != 1):
                    window.addstr(8,10, "ERROR zomb stepping in bad spot")
                    window.addstr(10,10, "zomb row " + str(row))
                    window.addstr(12,10, "zomb col " + str(col))
                env.checkerboard[row][col+i] = 0
            
            for i in range(1,3):
                if(env.checkerboard[row+1][col+i] != 1):
                    window.addstr(8,10, "ERROR zomb stepping in bad spot")
                    window.addstr(10,10, "zomb row " + str(row))
                    window.addstr(12,10, "zomb col " + str(col))
                env.checkerboard[row+1][col+i] = 0
        zomb_func_first_run = 0

        #calculate
        target = [env.player.row, env.player.column+2] # + 2 for near middle of hero's body
        
        if env.baddy.row < target[0]:
            #if env.checkerboard[row+2][col] == 0:
            if placement_is_valid(env.baddy.row + 1, env.baddy.col, env,
                                env.baddy.zombie_sprite_head, env.baddy.zombie_sprite_body):
                env.baddy.row += 1
        elif env.baddy.row > target[0]:
            #if env.checkerboard[row-1][col] == 0:
            if placement_is_valid(env.baddy.row - 1 ,env.baddy.col, env,
                                env.baddy.zombie_sprite_head, env.baddy.zombie_sprite_body):
                env.baddy.row -= 1

        if env.baddy.col < target[1]:
            if placement_is_valid(env.baddy.row ,env.baddy.col + 1, env,
                                env.baddy.zombie_sprite_head, env.baddy.zombie_sprite_body):
                env.baddy.col += 1
        elif env.baddy.col > target[1]:
            if placement_is_valid(env.baddy.row ,env.baddy.col - 1, env,
                                env.baddy.zombie_sprite_head, env.baddy.zombie_sprite_body):
                env.baddy.col -= 1


        #place
        window.addstr(int(env.baddy.row),int(env.baddy.col) + 1, env.baddy.zombie_sprite_head)
        window.addstr(int(env.baddy.row+1),int(env.baddy.col+1), env.baddy.zombie_sprite_body)
        row = int(env.baddy.row)
        col = int(env.baddy.col)
        for i in range(0,4):
            if(env.checkerboard[row][col+i] != 0):
                window.addstr(8,10, "ERROR zomb stepping in bad spot2")
                window.addstr(10,10, "zomb row " + str(row))
                window.addstr(12,10, "zomb col " + str(col))
            env.checkerboard[row][col+i] = 1
        
        for i in range(1,3):
            if(env.checkerboard[row+1][col+i] != 0):
                window.addstr(8,10, "ERROR zomb stepping in bad spot2")
                window.addstr(10,10, "zomb row " + str(row))
                window.addstr(12,10, "zomb col " + str(col))
            env.checkerboard[row+1][col+i] = 1



        env.lock.release()
        time.sleep(0.5)


#This function is currently gay
def auto_turret(env):

    turret = "++||++"
    turret = "+ [] +"
    turret = "++++++"
    
    turret = "++++++"
    turret = "+ [] +"
    turret = "++||++"
    
    turret = "++++++"
    turret = "+ I==="
    turret = "++++++"

    turret = "++++++"
    turret = "===I +"
    turret = "++++++"
 
def place_turret(x, y, env):

    if(not boundError(x, y)):

        window.addstr(y, x, env.playerTurret.facing_up_ln1)
        window.addstr(y + 1, x, env.playerTurret.facing_up_ln2)
        window.addstr(y + 2, x, env.playerTurret.facing_up_ln3)

#character ID: zombie = range(1,999), hero = -1 
def place_if_valid(env, old_origin, new_origin, character_ID ):
    
    #first check if placement is valid
    #then wipe old 
    #place new
    newrow = new_origin[0]
    newcol = new_origin[1]
    oldrow = old_origin[0]
    oldcol = old_origin[1]
    
    if(character_ID == -1):
        #check
        for i in range(0,env.player.len_of_sprite):
            if(env.checkerboard[newrow][newcol+i] != 0):
                return False
        #wipe
        for i in range(0,env.player.len_of_sprite):
            env.checkerboard[oldrow][oldcol+i] = 0
            window.addch(oldrow, oldcol + i, ' ')
        #place
        for i in range(0,env.player.len_of_sprite):
            env.checkerboard[newrow][newcol+i] = 0
            #TODO add hero sprite changing here
            window.addch(newrow, newrow + i, env.player.spriteRest[i])
        #window.addstr(8,10, "ERROR zomb stepping in bad spot") #faster likely
    return True

    # TODO change baddy to specific zombie
    if(character_ID >= 1):
        #check
        for i in range(0,env.baddy.len_of_row0):
            if(env.checkerboard[newrow][newcol+i] != 0 and 
            env.checkerboard[newrow][newcol+i] != character_ID):
                return False
        
        offset = env.baddy.offset_of_row1
        for i in range(0,env.baddy.len_of_row1):
            if(env.checkerboard[newrow+1][newcol+i+offset] != 0 and 
            env.checkerboard[newrow+1][newcol+i+offset] != character_ID ):
                return False
        #wipe
        for i in range(0,env.baddy.len_of_row0):
            env.checkerboard[oldrow][oldcol+i] = 0
            window.addch(oldrow, oldcol + i, ' ')
        
        # for i in range(0,env.baddy.len_of_row0):
        #     env.checkerboard[oldrow][oldcol+i] = 0
        #     window.addch(oldrow, oldcol + i, ' ')


                



    

def placement_is_valid(row, col, env, ln1_sprite, ln2_sprite = "", ln3_sprite = "", ln4_sprite = "" ):
    for i in range(0,len(ln1_sprite)):
        if(env.checkerboard[row][col+i] != 0 ):
            return False
    
    for i in range(0,len(ln2_sprite)):
        if(env.checkerboard[row+1][col+i] != 0 ):
            return False
    
    for i in range(0,len(ln3_sprite)):
        if(env.checkerboard[row+2][col+i] != 0 ):
            return False
    
    for i in range(0,len(ln4_sprite)):
        if(env.checkerboard[row+3][col+i] != 0 ):
            return False

    return True


def fireBullet(env): 
    while 1:
        bullet_info = None
        try:
            bullet_info = env.bullet_queue.get_nowait() #this should be fine to do before lock.aquire() ..even though it's odd.
        except:
            pass
        if bullet_info is not None:
            bullet_origin = bullet_info[0]
            bullet_direction = bullet_info[1] 
            bullet_type = bullet_info[2]           
            # vert_range = 8 
            # horiz_range = 20 
            distance = 20
            for i in range(1,distance):
                env.lock.acquire()
                
                if(bullet_direction == "right"):
                    clear_sprite(bullet_origin[0], bullet_origin[1]+i-1, ' ')
                    place_sprite(bullet_origin[0], bullet_origin[1]+i, bullet_type)
                elif(bullet_direction == "left"):
                    clear_sprite(bullet_origin[0], bullet_origin[1]-i+1, ' ')
                    place_sprite(bullet_origin[0], bullet_origin[1]-i, bullet_type)
                elif(bullet_direction == "up"):
                    clear_sprite(bullet_origin[0]-i+1, bullet_origin[1], ' ')
                    place_sprite(bullet_origin[0]-i, bullet_origin[1], bullet_type)
                elif(bullet_direction == "down"):
                    clear_sprite(bullet_origin[0]+i-1, bullet_origin[1], ' ')
                    place_sprite(bullet_origin[0]+i, bullet_origin[1], bullet_type)
                    
                env.lock.release()
                time.sleep(0.04)        
            
            env.lock.acquire()
            if(bullet_direction == "right"):
                clear_sprite(bullet_origin[0], bullet_origin[1]+distance-1, ' ')
            elif(bullet_direction == "left"):
                clear_sprite(bullet_origin[0], bullet_origin[1]-distance+1, ' ')
            elif(bullet_direction == "up"):
                clear_sprite(bullet_origin[0]-distance+1, bullet_origin[1], ' ')
            elif(bullet_direction == "down"):
                clear_sprite(bullet_origin[0]+distance-1, bullet_origin[1], ' ')
            env.lock.release()
            

def main():

    env = environment()
    lock = threading.Lock()
    init_map(env, lock)

    #display_intro_message()
    
    baddies_thread = Thread(target=move_baddies,args=(env,))
    baddies_thread.daemon = True #exit when main exits
    baddies_thread.start()    
    bullets_thread = Thread(target=fireBullet,args=(env,))
    bullets_thread.daemon = True #exit when main exits
    bullets_thread.start()    

    while True: #TODO stop shit from going off screen and breaking the program lol
        key = window.getch() 
        if key == ord('p'): 
            curses.endwin()
            subprocess.call(["reset"])
            quit() # TODO MAKE A PAUSE SCREEN? IF WE HAVE TIME.
        else:
            move_hero(env, key)

        window.border(0)

        drawHealthBar((sw // 2) - ((sw // 2) - 1), (sh // 2) - ((sh // 2) - 1), env.player.health)
        drawPointBar((sw // 2) - ((sw // 2) - 1), (sh // 2) - ((sh // 2) - 2), env.player.points)

        

    
    ## DONT FORGET TO JOIN THY THREADS!
    baddies_thread.join()
    bullets_thread.join()

    curses.endwin()
    subprocess.call(["reset"])
"""

 ◖========8 ############################## leggo baby. ################################ 8========D

"""

main()
