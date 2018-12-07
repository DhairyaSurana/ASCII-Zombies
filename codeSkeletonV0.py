import random
import curses

s = curses.initscr()
curses.curs_set(0)
sh, sw = s.getmaxyx() #TODO CREATE A SET SCREEN SIZE.
window = curses.newwin(sh, sw, 0, 0)
window.nodelay(True)
window.keypad(1)    #What does this do?
window.timeout(100)

hero_x = sw/4
hero_y = sh/2
hero = [
    [hero_y, hero_x],
    [hero_y, hero_x-1],
]

#window.addch(int(food[0]), int(food[1]), int(curses.ACS_PI))

key = curses.KEY_RIGHT

while True:
    next_key = window.getch()
    #key = key if next_key == -1 else next_key
    key = next_key

    #delete old character pos..optimize later - lets see how python can handle it
    window.addch(int(hero[0][0]),int(hero[0][1]), ' ')
    window.addch(int(hero[1][0]),int(hero[1][1]), ' ')

    new_hero_head = [hero[0][0], hero[0][1]]

    if key == curses.KEY_DOWN:
        new_hero_head[0] += 1
    if key == curses.KEY_UP:
        new_hero_head[0] -= 1
    if key == curses.KEY_LEFT:
        new_hero_head[1] -= 1
    if key == curses.KEY_RIGHT:
        new_hero_head[1] += 1

    #update hero pos array
    hero[0] = new_hero_head
    hero[1] = [hero[0][0] + 1, hero[0][1]]

    window.addch(int(hero[0][0]),int(hero[0][1]), '8')
    window.addch(int(hero[1][0]),int(hero[1][1]), '0')


