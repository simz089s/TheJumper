#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################################################
NOTES = '''
Bugs:_________________________________________________________________________________________________________________

'''
######################################################################################################################

# IMPORTS
#######################################
import os
from subprocess import call
from random import randint
#######################################

# GLOBAL DEFS (STRING VALUES)
############################################################################################################################################
TERRAIN = {'WALK':' ', 'UNWALK':"\x01", 'FIRE':'~', 'HEAL':'+', 'JUMP':'J', 'POINT':'P', 'MONSTER':'@', 'WIN':'*', 'LIFE':'T', 'SHIELD':'S'}
AUTHORIZED_CMD = ('exit','quit','help','print','stat','stats','status','w','a','s','d','j','q','e','f')
############################################################################################################################################

def clr_screen():
	call(['clear'])

##################################

def gen_empty_map(size):
	empty_map = size * ['']
	for line in range(size):
		empty_map[line] = size * [' ']
	return empty_map

##################################################################

def populate_map(game_map):
	n = len(game_map)
	for x in range(n):
		for y in range(n):
			block = randint(-20,8)
			if   (block < -10): game_map[y][x] = TERRAIN['UNWALK']
			elif (block is 2): game_map[y][x] = TERRAIN['FIRE']
			elif (block is 3): game_map[y][x] = TERRAIN['HEAL']
			elif (block is 4): game_map[y][x] = TERRAIN['JUMP']
			elif (block is 5): game_map[y][x] = TERRAIN['POINT']
			elif (block is 6): game_map[y][x] = TERRAIN['MONSTER']
			elif (block is 7): game_map[y][x] = TERRAIN['LIFE']
			elif (block is 8): game_map[y][x] = TERRAIN['SHIELD']
	game_map[randint(1,n-1)][randint(1,n-1)] = TERRAIN['WIN']
	return game_map

##################################################################

def print_map(game_map, curpos_x, curpos_y, icon):
	mapgrid = '\b'
	for x in game_map:
		for y in x:
			mapgrid += y
		mapgrid += "\n"
	
	curpos = curpos_x + (len(game_map)+1) * curpos_y
	mapgrid = mapgrid[:curpos+1] + icon + mapgrid[curpos+2:]
	print(' '.join(mapgrid))

###########################################################

def game_loop(game_map):
	'''Input "exit" or "quit" to stop playing.
Input "w", "a", "s", "d" for movement.
Input "stat", "stats" or "status" to show player status.
Input "j" to jump for a turn if you have the ability.
Input "q" to shield up if you have a shield.
Input "e" to show inventory.
Input "f" to cast ring of fire around player.
Input "help" to show this again.
'''
	tut = game_loop.__doc__
	
	# STATS AND VARS
	#################
	cmd = ''
	msg = ''
	icon = 'X'
	x = 0
	y = 0
	hp = 10
	mana = 10
	gold = 1
	points = 0
	kills = 0
	lives = 3
	deaths = 0
	shield = False
	movelen = 1
	jump = 0
	luck = 10
	inv = []
	win = False
	n = len(game_map)
	#################
	
	while (cmd not in AUTHORIZED_CMD[:2]):
		################################## Clear the screen at the beginning of every loop
		clr_screen()
		############################### Variable and stats setup/reset every loop
		print_map(game_map, x, y, icon)
		print(msg)
		msg = ''
		mvmt = movelen + jump
		jump = 0
		shield = False
		points = hp + gold + kills + lives + luck
		################################################## User input
		cmd = raw_input('>> ').lower()
		############################## Input processing
		if (cmd == 'help'):
			clr_screen()
			raw_input(tut)
			continue
		elif (cmd == 'print'):
			raw_input("%d,%d" % (x,y))
			continue
		elif (cmd in AUTHORIZED_CMD[4:7]):
			msg += 'HP: ' + str(hp) + ' | Mana: ' + str(mana) + ' | Gold: ' + str(gold) + ' | Lives: ' + str(lives) + ' | Deaths: ' + str(deaths) + ' | Kills: ' + str(kills) + ' | Points: ' + str(points) + ' | Movement length: ' + str(movelen) + ' | Jump: ' + str(jump) + ' | Shield: ' + str(shield)#+ ' | Luck: ' + str(luck)
			continue
		elif (cmd == 'w') and (y-mvmt >= 0) and (game_map[y-mvmt][x] is not TERRAIN['UNWALK']):
			y-=mvmt
		elif (cmd == 'a') and (x-mvmt >= 0) and (game_map[y][x-mvmt] is not TERRAIN['UNWALK']):
			x-=mvmt
		elif (cmd == 's') and (y+mvmt <  n) and (game_map[y+mvmt][x] is not TERRAIN['UNWALK']):
			y+=mvmt
		elif (cmd == 'd') and (x+mvmt <  n) and (game_map[y][x+mvmt] is not TERRAIN['UNWALK']):
			x+=mvmt
		elif (cmd == 'j'):
			if ('J' in inv):
				jump = 1
				msg += 'You can now jump. '
			else: msg += 'You do not possess the ability to jump. '
			continue
		elif (cmd == 'q'):
			if ('S' in inv):
				shield = True
				msg += 'Shielded. '
			else: msg += 'No shield. '
			continue
		elif (cmd == 'e'):
			msg += str(inv)
			continue
		elif (cmd == 'f'):
			if ('F' in inv):
				mana-=5
				for area in ((x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1)):
					if (0 <= area[0] < n) and (0 <= area[1] < n) and (game_map[area[1]][area[0]] == '@'):
						game_map[area[1]][area[0]] = ' '
			else: msg += 'You do not possess a Ring of Fire. '
		elif (cmd == '') or (cmd.count(' ') is len(cmd)):
			#~ continue
			if (luck > 0): luck-=1
		else:
			msg += 'Invalid input. '
		############################ Events depending on current block position
		curpos = game_map[y][x]
		
		if (curpos == TERRAIN['WIN']):
			clr_screen()
			raw_input("You have won the game!\nHere are your points: " + str(points))
			break
		elif (curpos == TERRAIN['FIRE']):
			hp-=1
			msg += 'You lost 1 hp by fire damage. '
			if (randint(0,10+luck) >= 10):
				inv.append('F')
				msg += 'You now possess a Ring of Fire. Input "f" to use. Costs 5 mana per use. '
		elif (curpos == TERRAIN['HEAL']):
			if (randint(-1,1+luck) < 1): hpgain = 1
			else: hpgain = 1 + luck/5
			hp+=hpgain
			game_map[y][x] = TERRAIN['WALK']
			msg += 'You have gained ' + str(hpgain) + ' hp. '
		elif (curpos == TERRAIN['JUMP']):
			inv.append('J')
			game_map[y][x] = TERRAIN['WALK']
			msg += 'You now possess the ability to jump. Input "j" and then the direction to use. '
		elif (curpos == TERRAIN['POINT']):
			points+=2
			game_map[y][x] = TERRAIN['WALK']
			msg += 'You have gained 2 points. '
		elif (curpos == TERRAIN['MONSTER']):
			msg += 'A monster. '
		elif (curpos == TERRAIN['LIFE']):
			lives+=1
			game_map[y][x] = TERRAIN['WALK']
			msg += 'You have gained a life. '
		elif (curpos == TERRAIN['SHIELD']):
			inv.append('S')
			game_map[y][x] = TERRAIN['WALK']
			msg += 'You have gained a shield. Input "q" to enter shield stance for a turn. '
		
		if (randint(0,50+luck) is 0):
			game_map[y][x] = TERRAIN['UNWALK']
			msg += 'The ground at your feet feels shaky. '
		
		################################################## Death and permanent death
		if (hp is 0):
			clr_screen()
			lives-=1
			deaths+=1
			points-=1
			gold/=2
			mana/=2
			x = 0
			y = 0
			raw_input('You died.')
			if (lives is 0):
				raw_input("GAME OVER\nHere are your points: " + str(points))
				break
		#################################################################### Innate HP and mana regen
		if (mana < 20): mana+=randint(0,1)
		if (hp < 20): hp+=randint(0,1)
		##################################
	
	return 0

#######################################################################################

def start_game():
	again = True
	while (again):
		clr_screen()
		mapsize = input('Map size? ')
		game_map = gen_empty_map(int(mapsize))
		populate_map(game_map)
		raw_input(game_loop.__doc__)
		game_loop(game_map)
		while (again not in ('y','n')): again = raw_input('Play again? (y/n) ').lower()
		again = True if (again == 'y') else False

#######################################################################################

def main(args):
	start_game()
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
