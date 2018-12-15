import curses
import random
import sys
import threading
from threading import Thread
import time
import subprocess
import queue
from random import randint
import math
# $ python3.7 -m pip install pygame
import pygame #make sure we can install on user's computers.. {maybe do an install from source for deployment!}
from pygame.locals import *
from pygame import mixer
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
mixer.init()

old_health = 3
old_points = 10
#old_health_bar = "❤" * old_health
bullet_row = 1
bullet_col = 1
####### </INITILIZATIONZ> ###########

class finishLine:
   row0 = "  E +"
   row1 = "  E +"
   row2 = "  E +"
   row3 = "  E +"
   row4 = "  E +"
   row5 = "  E +"
   row6 = "  E +"
   row7 = "  E +"
   row8 = "  R +"
   rows = [row0, row1, row2, row3, row4, row5, row6, row7, row8]
   num_rows_or_height = 9
   width_or_length = 5


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

    len_of_row = 6

class hero:
    col = 0
    row = 0
    health = 3
    points = 0

    spriteRest = "┌(ᶱ1ᶱ)┐"

    spriteMove1 = "┌(ᶱ1ᶱ)┘"
    spriteMoveFired1 = "┌(ᶱ.ᶱ)┘"

    spriteMove2 = "└(ᶱ1ᶱ)┐"
    spriteMoveFired2 = "└(ᶱ.ᶱ)┐"
    len_of_sprite = 7 #UPDATE IF MORE SPRITES COME

    hero_sprite_type = 1



class zombie:
    col = sw - (sw // 20)
    row = 0

    zombie_sprite_left_attack_head ='~{#_#}'
    zombie_sprite_right_attack_head ='{#_#}~' #TODO make bodies too and implement
    
    zombie_sprite_head = "{#_#}"
    zombie_sprite_body =  '(o)'

    len_of_row0 = 5
    len_of_row1 = 3
    offset_of_row1 = 1
    zombie_ID = 1
    alive = True

class environment:
    lock = threading.Lock()
    player = hero()  
    zombie_list = list()
    hero_sprite = ''
    turrets = list()
    playerTurret = turret()
    turret_queue = queue.Queue()
    bullet_queue = queue.Queue()
    checkerboard = np.zeros((sh,sw),dtype=int) 

    #0 for nothing there, -1 for player, -10 to -20 for turret, -5 for walls,
    #  1 to inf correspond to zombos, -99 is finish line

def draw_finish_line(env):
    
    pos = [sh//2 + finishLine.num_rows_or_height//2, 1 ]
    
    for x in range(0, finishLine.num_rows_or_height):
        for i in range(0,finishLine.width_or_length):
            env.checkerboard[pos[0]-x][pos[1]+i] = -99
        window.addstr(pos[0]-x,pos[1], finishLine.rows[x])


def create_bounds(env):
    for col in range(0,sw):
        env.checkerboard[0][col] = -5
        env.checkerboard[sh-1][col] = -5
    
    for row in range(0,sh):
        env.checkerboard[row][0] = -5
        env.checkerboard[row][sw-1] = -5
        

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
    
    hero_x =  sw // 4
    hero_y =  sh // 2

    env.player.row = hero_y
    env.player.col =  hero_x

    #starting with 3 zombies 
    # ATTENTION: zombie ID in zombie class initialize is 1
    # Since all the zombie >=1
    for i in range (0,3):
        eachZombie = zombie()
        eachZombie.zombie_ID = i + 1
        eachZombie.row = randint(0,sh - (sh // 5)) # create zombie at random position
        eachZombie.col = randint(sw - (sw // 10),sw - (sw // 20))
        env.zombie_list.append(eachZombie)    

    #sets the initial sprite for the player
    env.hero_sprite = env.player.spriteRest

    draw_finish_line(env)
    create_bounds(env)
                

def display_intro_message():

    song = mixer.Sound('ost_1_SQ.wav') #works!
    song.play()

    YELLOW_TEXT = 1
    RED_TEXT = 2

    scale = 0.15 #time scale

    curses.init_pair(YELLOW_TEXT, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    dynamic_print(0.2*scale,(sw // 2) - 15, (sh // 2) - 5, "Sudochad Stud|os presents ...", YELLOW_TEXT)
    time.sleep(3*scale)
    dynamic_print(0.1*scale, (sw // 2) - 15, (sh // 2) - 5, "                             ", YELLOW_TEXT)
    
    curses.init_pair(RED_TEXT, curses.COLOR_RED, curses.COLOR_BLACK)
    dynamic_print(0.5*scale, (sw // 2) - 10, (sh // 2), "ASCII ZOMBIES", RED_TEXT)
    time.sleep(2*scale)
    dynamic_print(0.05*scale, (sw // 2) - 10, (sh // 2), "              ", RED_TEXT)


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


def move_hero(env, keypress):

    global last_time_fired
    
    global hero_func_first_run
    
    env.lock.acquire() ####### (;

    key = keypress

    bulletFired = False
        
    old_pos = [env.player.row, env.player.col]
    new_pos = [env.player.row, env.player.col]
    
    if key == curses.KEY_DOWN:
        new_pos = [env.player.row + 1, env.player.col]
        
    elif key == curses.KEY_UP:
        new_pos = [env.player.row - 1, env.player.col]
        
    elif key == curses.KEY_LEFT:
        new_pos = [env.player.row, env.player.col - 1]
       
    elif key == curses.KEY_RIGHT:
        new_pos = [env.player.row, env.player.col + 1]
        
    place_if_valid(env,old_pos,new_pos,-1)
    

    if key == ord('d') or key == ord('D') or key == ord('a') or key == ord('A') or key == ord('s') or key == ord('S') or key == ord('w') or key == ord('W'):
        bulletFired = True
        #s  drawExplosion(, bullet_col)
        if(time.time() > (last_time_fired)+ 0.45):
            last_time_fired = time.time()
            if key == ord('d') or key == ord('D'):
                bullet_info = [new_pos,'right','⁍']
                env.bullet_queue.put(bullet_info)
            elif key == ord('a') or key == ord('A'):
                bullet_info = [new_pos,'left','⁌']
                env.bullet_queue.put(bullet_info)
            elif key == ord('w') or key == ord('W'):
                bullet_info = [new_pos,'up','•']
                env.bullet_queue.put(bullet_info)
            elif key == ord('s') or key == ord('S'):
                bullet_info = [new_pos,'down','•']
                env.bullet_queue.put(bullet_info)
    
    if env.player.points >= 10:
        window.addstr((sh // 2) - ((sh // 2) - 2), (sw // 2) - ((sw // 2) - 30), "Press E to build a turret", curses.A_BLINK)

        if key == ord('e'):
            clear_sprite((sh // 2) - ((sh // 2) - 2), (sw // 2) - ((sw // 2) - 30), "Press E to build a turret")
            env.turrets.append(turret())
            env.turrets[-1].row = env.player.row
            env.turrets[-1].col = env.player.col + 10
            place_turret(env.turrets[-1].col, env.turrets[-1].row, "up", env)

            env.player.points -= 10

    elif key == ord('i'):
        env.player.points+=1
        
    if env.player.hero_sprite_type == 1:
        if bulletFired:
            env.hero_sprite = env.player.spriteMoveFired1
        else:
            env.hero_sprite = env.player.spriteMove1
    elif env.player.hero_sprite_type == 2:
        if bulletFired:
            env.hero_sprite = env.player.spriteMoveFired2
        else:
            env.hero_sprite = env.player.spriteMove2

        env.player.hero_sprite_type = 0
   
    env.player.hero_sprite_type+=1
    env.lock.release() 

def move_baddies(env, counter, timeValue):
    """
    this function is run in a seperate thread. It will move
    all the zombie into the new location.
    """

    while(1):
        env.lock.acquire()

        newZombies = 0
        if (counter == 10):
            newZombies = int (math.e ** (timeValue/5))
            counter = 0
            timeValue += 1

        i = 0
        for i in range (0,newZombies):
            eachZombie = zombie()
            eachZombie.zombie_ID = len(env.zombie_list) + 1
            eachZombie.row = randint(0,sh - (sh // 5)) # create zombie at random position
            eachZombie.col = randint(sw - (sw // 10),sw - (sw // 20))
            env.zombie_list.append(eachZombie)    

        #target = [env.player.row, env.player.col+2] # + 2 for near middle of hero's body
        target = [sh//2 + finishLine.num_rows_or_height//2, 1 ]

        for each_zombie in env.zombie_list:
            if each_zombie.alive:

                if(random.randint(1,10)==1):
                    target = [env.player.row, env.player.col+2] # + 2 for near middle of hero's body

                if each_zombie.row < target[0] and random.randint(1,10) > 2:
                    new_pos = [each_zombie.row+1,each_zombie.col]
                    old_pos = [each_zombie.row,each_zombie.col]
                    place_if_valid(env,old_pos,new_pos, each_zombie.zombie_ID)
                #elif each_zombie.row > target[0]:
                else:
                    new_pos = [each_zombie.row-1,each_zombie.col]
                    old_pos = [each_zombie.row,each_zombie.col]
                    place_if_valid(env,old_pos,new_pos, each_zombie.zombie_ID)
        

                if each_zombie.col < target[1]:
                    new_pos = [each_zombie.row,each_zombie.col+1]
                    old_pos = [each_zombie.row,each_zombie.col]
                    place_if_valid(env,old_pos,new_pos, each_zombie.zombie_ID)
    
                elif each_zombie.col > target[1]:
                    new_pos = [each_zombie.row,each_zombie.col-1]
                    old_pos = [each_zombie.row,each_zombie.col]
                    place_if_valid(env,old_pos,new_pos, each_zombie.zombie_ID)

        if (timeValue > 23):
            timeValue = 23

        counter += 1
        env.lock.release()
        time.sleep(0.5) #SPEED UP OR SLOW DOWN THE GAME WITH THIS..LAG FIX OR LAG ++


def fire_turret(env, tur, dir):
    
    if dir == "right":
        dist = 30
        for i in range(0,dist):
            env.lock.acquire()

            bullet_origin = [tur.row + 1, tur.col + 6]
            bullet_type = '@'
            
            clear_sprite(bullet_origin[0], bullet_origin[1]+i-1, ' ')
            place_sprite(bullet_origin[0], bullet_origin[1]+i, bullet_type)
            bullet_row = bullet_origin[0]
            bullet_col = bullet_origin[1] + i
                        
            if( i == dist//2):
                shrapnel_origin = [bullet_row, bullet_col]
                bullet_info = [shrapnel_origin,'up','±']
                bullet_info2 = [shrapnel_origin,'down','±']
                env.bullet_queue.put(bullet_info)
                env.bullet_queue.put(bullet_info2)

            if killZombie(env, bullet_row, bullet_col):
                clear_sprite(bullet_origin[0], bullet_origin[1]+i-1, ' ')
                env.lock.release() 
                return True
                    
            env.lock.release()
            time.sleep(0.02)        

    elif dir == "left":
        dist = 30
        for i in range(0,dist):
            env.lock.acquire()

            bullet_origin = [tur.row + 1, tur.col - 2]
            bullet_type = '@'
            
            clear_sprite(bullet_origin[0], bullet_origin[1]-i+1, ' ')
            place_sprite(bullet_origin[0], bullet_origin[1]-i, bullet_type)
            bullet_row = bullet_origin[0]
            bullet_col = bullet_origin[1] - i
                        
            if( i == dist//2):
                shrapnel_origin = [bullet_row, bullet_col]
                bullet_info = [shrapnel_origin,'up','±']
                bullet_info2 = [shrapnel_origin,'down','±']
                env.bullet_queue.put(bullet_info)
                env.bullet_queue.put(bullet_info2)

            if killZombie(env, bullet_row, bullet_col):
                clear_sprite(bullet_origin[0], bullet_origin[1]-i+1, ' ')
                env.lock.release() 
                return True
                    
            env.lock.release()
            time.sleep(0.02)        

    elif dir == "down":
        dist = 10
        for i in range(0,dist):

            env.lock.acquire()

            bullet_origin = [tur.row + 3, tur.col + 3]
            bullet_type = '@'

            clear_sprite(bullet_origin[0]+i-1, bullet_origin[1], ' ')
            place_sprite(bullet_origin[0]+i, bullet_origin[1], bullet_type)
            bullet_row = bullet_origin[0]+i
            bullet_col = bullet_origin[1]

            if( i == dist//2):
                shrapnel_origin = [bullet_row, bullet_col]
                bullet_info = [shrapnel_origin,'left','¥']
                bullet_info2 = [shrapnel_origin,'right','¥']
                env.bullet_queue.put(bullet_info)
                env.bullet_queue.put(bullet_info2)
            
            if killZombie(env, bullet_row, bullet_col):
                clear_sprite(bullet_origin[0]+i-1, bullet_origin[1], ' ')
                env.lock.release() 
                return True

            env.lock.release()
            time.sleep(0.02)  

    elif dir == "up":
        dist = 10
        for i in range(0,dist):

            env.lock.acquire()

            bullet_origin = [tur.row - 1, tur.col + 3]
            bullet_type = '@'

            clear_sprite(bullet_origin[0]-i+1, bullet_origin[1], ' ')
            place_sprite(bullet_origin[0]-i, bullet_origin[1], bullet_type)
            bullet_row = bullet_origin[0]-i
            bullet_col = bullet_origin[1]

            if( i == dist//2):
                shrapnel_origin = [bullet_row, bullet_col]
                bullet_info = [shrapnel_origin,'left','¥']
                bullet_info2 = [shrapnel_origin,'right','¥']
                env.bullet_queue.put(bullet_info)
                env.bullet_queue.put(bullet_info2)
            
            if killZombie(env, bullet_row, bullet_col):
                clear_sprite(bullet_origin[0]-i+1, bullet_origin[1], ' ')
                env.lock.release() 
                return True

            env.lock.release()
            time.sleep(0.02)  


def automateTurret2(env):

    while 1:

        time.sleep(0.5)
        if len(env.turrets) > 0:
            env.lock.acquire()
            for tur in env.turrets:
                
                horiz_targeting_dist = 6+14
                vert_targeting_dist = 3+6

                #target right randomly
                if(random.randint(0,1)):
                    
                    place_turret(tur.col, tur.row, "right", env)

                    for rcols in range(0,horiz_targeting_dist, 4):

                        if tur.col + rcols < sw :
                            if env.checkerboard[tur.row][tur.col + rcols] >= 1:
                                env.lock.release()
                                fire_turret(env, tur, "right")
                                env.lock.acquire()

                #target left randomly #!
                if(random.randint(0,1)):
                    
                    place_turret(tur.col, tur.row, "left", env)

                    for lcols in range(0,horiz_targeting_dist, 4):

                        if tur.col - lcols > 1 :
                            if env.checkerboard[tur.row][tur.col - lcols] >= 1:
                                env.lock.release()
                                fire_turret(env, tur, "left")
                                env.lock.acquire()
                

                #target down randomly
                elif(random.randint(0,1)):

                    place_turret(tur.col, tur.row, "down", env)

                    for drows in range(0, vert_targeting_dist):

                        if tur.row + drows < sh:
                                if env.checkerboard[tur.row + drows][tur.col] >= 1:
                                    env.lock.release()
                                    fire_turret(env, tur, "down")
                                    env.lock.acquire()

                #target up randomly
                elif(random.randint(0,1)):

                    place_turret(tur.col, tur.row, "up", env)

                    for urows in range(0, vert_targeting_dist):

                        if tur.row - urows > 1:
                                if env.checkerboard[tur.row - urows][tur.col] >= 1:
                                    env.lock.release()
                                    fire_turret(env, tur, "up")
                                    env.lock.acquire()

            env.lock.release()

 
def place_turret(x, y, direction, env):

    for cols in range(0, 6):
        env.checkerboard[y][x+cols] = -10
        env.checkerboard[y+1][x+cols] = -10
        env.checkerboard[y+2][x+cols] = -10
    
    if(direction == "up"):
        window.addstr(y, x, env.playerTurret.facing_up_ln1)
        window.addstr(y + 1, x, env.playerTurret.facing_up_ln2)
        window.addstr(y + 2, x, env.playerTurret.facing_up_ln3)

    elif(direction == "down"):
        window.addstr(y, x, env.playerTurret.facing_down_ln1)
        window.addstr(y + 1, x, env.playerTurret.facing_down_ln2)
        window.addstr(y + 2, x, env.playerTurret.facing_down_ln3)

    elif(direction == "left"):
        window.addstr(y, x, env.playerTurret.facing_left_ln1)
        window.addstr(y + 1, x, env.playerTurret.facing_left_ln2)
        window.addstr(y + 2, x, env.playerTurret.facing_left_ln3)

    elif(direction == "right"):
        window.addstr(y, x, env.playerTurret.facing_right_ln1)
        window.addstr(y + 1, x, env.playerTurret.facing_right_ln2)
        window.addstr(y + 2, x, env.playerTurret.facing_right_ln3)

def clear_turret(x, y, direction, env):

    clear_sprite(y, x, env.playerTurret.facing_up_ln1)
    clear_sprite(y + 1, x, env.playerTurret.facing_up_ln2)
    clear_sprite(y + 2, x, env.playerTurret.facing_up_ln3)
        

def verify_player_row(row, col, env, character_ID):

    for i in range(0,env.player.len_of_sprite):
        if(env.checkerboard[row][col+i] != 0 and env.checkerboard[row][col+i] != character_ID):
            return False
    return True

def verify_zombie_rows(row, col, env, offset, character_ID, ZOMBIE): 
    """
    game over happens thru here. also -
    This function verifies if the location is valid to either
    having a new zombie appear in this location or having an
    existing zombie move to this location. The function return
    false for the bad location and true for good location.
    """
    for i in range(0,ZOMBIE.len_of_row0):
        if(env.checkerboard[row][col+i] != 0 and env.checkerboard[row][col+i] != character_ID):
                        
            if(env.checkerboard[row][col+i] == -1): #hit the player
                
                env.player.health -= 1
                if(env.player.health < 1):
                    game_over()

            elif(env.checkerboard[row][col+i] == -99):
                    game_over()
                    
            return False
    
    for i in range(0,ZOMBIE.len_of_row1):
        if(env.checkerboard[row+1][col+i+offset] != 0 and env.checkerboard[row+1][col+i+offset] != character_ID ):
            
            if(env.checkerboard[row][col+i] == -1): #hit the player
                
                env.player.health -= 1
                if(env.player.health < 1):
                    game_over()

            elif(env.checkerboard[row][col+i] == -99):
                    game_over()

            return False

    return True


def clear_player_row(row, col, env):

    for i in range(0,env.player.len_of_sprite):
        env.checkerboard[row][col+i] = 0
        window.addch(row, col + i, ' ')

def clear_zombie_rows(row, col, env, offset, ZOMBIE):
    """
    This function take in the old location of the zombie
    and clear it.
    """
    for i in range(0,ZOMBIE.len_of_row0):
        env.checkerboard[row][col+i] = 0
        window.addch(row, col + i, ' ')
        
    for i in range(0,ZOMBIE.len_of_row1):
        env.checkerboard[row+1][col+i+offset] = 0
        window.addch(row+1, col + i + offset, ' ')

def place_player(row, col, env):

    for i in range(0,env.player.len_of_sprite):
        env.checkerboard[row][col+i] = -1
        window.addch(row, col + i, env.hero_sprite[i])
        
################################################ Finish Changing ######################################

def place_zombie_rows(row, col, offset,  env, character_ID, ZOMBIE):
    """
    This function will place the zombie into the new location
    """
    for i in range(0,ZOMBIE.len_of_row0):
        env.checkerboard[row][col+i] = character_ID
        window.addch(row, col+i, ZOMBIE.zombie_sprite_head[i])
        
    for i in range(0,ZOMBIE.len_of_row1):
        env.checkerboard[row+1][col+i+offset] = character_ID
        window.addch(row+1, col+i+offset, ZOMBIE.zombie_sprite_body[i])

################################################ Finish Changing ######################################

#character ID: zombie = range(1,999), hero = -1 , etc..
def place_if_valid(env, old_origin, new_origin, character_ID):
    
    #first check if placement is valid
    #then wipe old 
    #place new
    newrow = new_origin[0]
    newcol = new_origin[1]
    oldrow = old_origin[0]
    oldcol = old_origin[1]
    
    #Player
    if(character_ID == -1):
        #checks if 
        if verify_player_row(newrow, newcol, env, character_ID):

            #wipe
            clear_player_row(oldrow, oldcol, env)

            #place
            place_player(newrow, newcol, env)
        
            env.player.row = newrow
            env.player.col = newcol
            return True
        else:
            return False

    # TODO change baddy to specific zombie
    elif(character_ID >= 1):

        offset = 1 #env.zombie.offset_of_row1
        ZOMBIE = env.zombie_list[character_ID - 1] #get the right zombie from the list

        if verify_zombie_rows(newrow, newcol, env, offset, character_ID, ZOMBIE):

            clear_zombie_rows(oldrow, oldcol, env, offset, ZOMBIE)
            
            place_zombie_rows(newrow, newcol, offset,  env, character_ID, ZOMBIE)

            ZOMBIE.row = newrow
            ZOMBIE.col = newcol
            return True
        else:
            return False

    #Turret
    if(character_ID <= -10 and character_ID >= -20):
        for i in range(0, env.playerTurret.len_of_row):
            env.checkerboard[env.player.row][env.player.col + 10] = character_ID
                
    
def drawExplosion(y, x):
    place_sprite(y, x, "ꙮ")
    place_sprite(y, x,  "꙰")
   # time.sleep(0.25)
   # clear_sprite(y, x, "ꙮ")
    #clear_sprite(y, x,  "꙰")

def automateTurret(env):

    while 1:
        turret_info = None
        try:
            turret_info = env.turret_info.get_nowait()
        except:
            pass
        if turret_info is not None:

            x = turret_info[0]
            y = turret_info[1]

            time.sleep(2)
            env.lock.acquire()
            place_turret(x, y, "up", env)
            env.lock.release()

            time.sleep(2)

            env.lock.acquire()
            clear_turret(x, y, "up", env)
            place_turret(x, y, "right", env)
            env.lock.release()

            time.sleep(2)
            
            env.lock.acquire()
            clear_turret(x, y, "right", env)
            place_turret(x, y, "down", env)
            env.lock.release()

            time.sleep(2)

            env.lock.acquire()
            clear_turret(x, y, "down", env)
            place_turret(x, y, "left", env)
            env.lock.release()

#run in a locked function!
def killZombie(env, bullet_row, bullet_col):
    """
    This function is to compare the location of bullet vs zombie
    if bullet hits a zombie, it will erase zombie from the board
    and delete zombie from zombie_list
    """
    if bullet_row < sh and bullet_row >= 0:
        if bullet_col < sw and bullet_col >= 0:
            zombieID = env.checkerboard[bullet_row][bullet_col]
            if  (zombieID >= 1):
                    death_zombie = env.zombie_list[zombieID-1]
                    death_zombie.alive = False
                    clear_zombie_rows(death_zombie.row, death_zombie.col, env, 1, death_zombie)
                    env.player.points += 1
                    return True
    return False


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
            distance = (sw // 5)
            if(bullet_type == '±'): #for shrapnel!
                distance = 6
            elif(bullet_type == '¥'):
                distance = 3
            for i in range(1,distance):
                env.lock.acquire()
                
                if(bullet_direction == "right"):
                    clear_sprite(bullet_origin[0], bullet_origin[1]+i-1, ' ')
                    place_sprite(bullet_origin[0], bullet_origin[1]+i, bullet_type)
                    bullet_row = bullet_origin[0]
                    bullet_col = bullet_origin[1] + i
                    if killZombie(env, bullet_row, bullet_col):
                        env.lock.release() 
                        break

                elif(bullet_direction == "left"):
                    clear_sprite(bullet_origin[0], bullet_origin[1]-i+1, ' ')
                    place_sprite(bullet_origin[0], bullet_origin[1]-i, bullet_type)
                    bullet_row = bullet_origin[0]
                    bullet_col = bullet_origin[1] - i
                    if killZombie(env, bullet_row, bullet_col):
                        env.lock.release() 
                        break

                elif(bullet_direction == "up"):
                    clear_sprite(bullet_origin[0]-i+1, bullet_origin[1], ' ')
                    place_sprite(bullet_origin[0]-i, bullet_origin[1], bullet_type)
                    bullet_row = bullet_origin[0] - i
                    bullet_col = bullet_origin[1]
                    if killZombie(env, bullet_row, bullet_col):
                        env.lock.release() 
                        break

                elif(bullet_direction == "down"):
                    clear_sprite(bullet_origin[0]+i-1, bullet_origin[1], ' ')
                    place_sprite(bullet_origin[0]+i, bullet_origin[1], bullet_type)
                    bullet_row = bullet_origin[0] + i
                    bullet_col = bullet_origin[1]
                    if killZombie(env, bullet_row, bullet_col):
                        env.lock.release() 
                        break
               
               
                env.lock.release()
                time.sleep(0.01)        
            
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
            

def game_over():
    window.clear()
    window.addstr(int(sh//2),int(sw//2),"u lose.")
    time.sleep(1)
    subprocess.call(["reset"])
    quit()     



def main():

    display_intro_message()

    env = environment()
    lock = threading.Lock()
    init_map(env, lock)

    counter = 0
    timeValue = 0
   
    
    baddies_thread = Thread(target=move_baddies,args=(env, counter, timeValue, ))
    baddies_thread.daemon = True #exit when main exits
    baddies_thread.start()    

    bullets_thread = Thread(target=fireBullet,args=(env,))
    bullets_thread.daemon = True #exit when main exits
    bullets_thread.start()    

    #turrets_thread = Thread(target=automateTurret1, args=(env,))
    turrets_thread = Thread(target=automateTurret2, args=(env,))
    turrets_thread.daemon = True #exit when main exits
    turrets_thread.start()

    while True: #TODO stop shit from going off screen and breaking the program lol
        key = window.getch() 
        if key == ord('p'): 
            curses.endwin()
            subprocess.call(["reset"])
            quit() # TODO MAKE A PAUSE SCREEN? IF WE HAVE TIME.
        else:
            move_hero(env, key)

        #window.border(0)

        drawHealthBar((sw // 2) - ((sw // 2) - 1), (sh // 2) - ((sh // 2) - 1), env.player.health)
        drawPointBar((sw // 2) - ((sw // 2) - 1), (sh // 2) - ((sh // 2) - 2), env.player.points)

            
    ## DONT FORGET TO JOIN THY THREADS!
    baddies_thread.join()
    bullets_thread.join()
    turrets_thread.join()

    curses.endwin()
    subprocess.call(["reset"])
"""

 ◖========8 ############################## leggo baby. ################################ 8========D

"""

main()
