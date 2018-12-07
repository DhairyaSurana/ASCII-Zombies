import random
import curses
import time
import sys

# TODO come to a conclusion on how we'll be sharing all the variables..
# to-be shared variables:
# window
# map .. aka objects on and off the screen aka a big ass array.. BAH NO - lets use a struct!
# key pressed.. actually not nessecary (we can run get key in each function)

#def init_screen(window): 
s = curses.initscr()
curses.curs_set(0)
sh, sw = s.getmaxyx() #TODO CREATE A SET SCREEN SIZE.
window = curses.newwin(sh, sw, 0, 0)
window.nodelay(True)    #does this actually work?
window.keypad(1)    #What does this do?
window.timeout(100) #and this?

class ze_map_class:
    hero = [ [0,0],[0,0] ] # change size as needed.
    

def init_map(ze_map):
    hero_x =  sw / 4
    hero_y =  sh / 2

    ze_map.hero = [
        [hero_y, hero_x],
        [hero_y, hero_x-1],
    ] 


def display_title():
    sys.stdout.flush()
    text = "Sudochad Stud|os presents..."
    for character in text:
        print(character, end = "")
        #time.sleep(0.125) #sexy but too slow for debugging
        time.sleep(.03)
        sys.stdout.flush()
    time.sleep(.12)


def move_hero(ze_map):
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

    #update ze_map.hero pos array
    ze_map.hero[0] = new_hero_head
    ze_map.hero[1] = [ze_map.hero[0][0] + 1, ze_map.hero[0][1]]

    window.addch(int(ze_map.hero[0][0]),int(ze_map.hero[0][1]), '8')
    window.addch(int(ze_map.hero[1][0]),int(ze_map.hero[1][1]), '0')


def main():
    ze_map = ze_map_class()
    init_map(ze_map)

    display_title()

    while True: #TODO stop shit from going off screen and breaking the program lol
        move_hero(ze_map)
        #move_baddies(ze_map)


"""

 ◖========8 ############################## leggo baby. ################################ 8========D

"""

main()

