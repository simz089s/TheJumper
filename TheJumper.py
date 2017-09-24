#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
'''
Bugs/TODOs:
- Make maps more intelligently generated (and spawn point)
- Multiple rooms
- Ring of Fire does not work
- Monster HP
- Attack power/skills
- Items
'''
###############################################################################
import os, sys
from subprocess import call
from random import randint
###############################################################################
OS_PLATFORM = ''
test1 = sys.platform
test2 = os.name
if test1.startswith('linux') and test2 == 'posix':
    OS_PLATFORM = 'posix'
elif test1.startswith('win32') and test2 == 'nt':
    OS_PLATFORM = 'windows'
elif test1.startswith('cygwin') and test2 == 'posix':
    OS_PLATFORM = 'posix'
elif test1.startswith('darwin') and test2 == 'posix':
	OS_PLATFORM = 'posix'
###############################################################################
if sys.version_info >= (3,0):
	from builtins import input as raw_input
###############################################################################
AUTHORIZED_CMD = ('exit','quit','help','print','stat','stats','status','w','a',
                  's','d','j','q','e','f')
###############################################################################
class Keybinding:
	Jump = 'j'
	Shield = 'q'
	Inventory = 'e'
	RingOfFire = 'f'
###############################################################################
class Terrain:
	Walk = ' '
	Unwalk = "\x01"
	Fire = '~'
	Heal = '+'
	Jump = 'J'
	Point = 'P'
	Monster = '@'
	Win = '*'
	Life = 'T'
	Shield = 'S'
	Lava = 'L'

class Block:
	'''Block of a certain terrain.'''

	def __init__(self, terrain, x, y):
		'''Create a new block of terrain.'''
		self.terrain = terrain
		self.x = x
		self.y = y

	def morph(self, terrain):
		self.terrain = terrain

	def clear(self):
		self.terrain = Terrain.Walk

	def destroy(self):
		self.terrain = Terrain.Unwalk

	def coords(self):
		return (self.x, self.y)

class Player:
	'''Player character with stats.'''

	def __init__(self, icon='X', x=0, y=0, hp=10, mp=10, gold=1, pts=0, kills=0, lives=3, deaths=0, shield=False, movlen=1, jmp=0, luck=10, inv=[]):
		'''Create player with stats.'''
		self.icon = icon
		self.x = x
		self.y = y
		self.hp = hp
		self.mp = mp
		self.gold = gold
		self.pts = pts
		self.kills = kills
		self.lives = lives
		self.deaths = deaths
		self.shield = shield
		self.movlen = movlen
		self.jmp = jmp
		self.luck = luck
		self.inv = inv

	def die(self):
		self.luck -= randint(0-self.luck, self.luck//self.pts)
		self.lives -= 1
		self.deaths += 1
		self.pts -= 1
		self.gold //= 2
		self.mp //= 2
		self.hp = 1
		self.x = 0
		self.y = 0

##################################

def clr_screen():
	if OS_PLATFORM == 'posix':
		call(['clear'])
	elif OS_PLATFORM == 'windows':
		call(['cmd', '/c', 'cls'])

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
			if   (block < -10): game_map[y][x] = Terrain.Unwalk
			elif (block is 2): game_map[y][x] = Terrain.Fire
			elif (block is 3): game_map[y][x] = Terrain.Heal
			elif (block is 4): game_map[y][x] = Terrain.Jump
			elif (block is 5): game_map[y][x] = Terrain.Point
			elif (block is 6): game_map[y][x] = Terrain.Monster
			elif (block is 7): game_map[y][x] = Terrain.Life
			elif (block is 8): game_map[y][x] = Terrain.Shield
	game_map[randint(1,n-1)][randint(1,n-1)] = Terrain.Win
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
	n = len(game_map)
	cmd = ''
	msg = ''
	win = False
	pc = Player()
	box_coords = ((pc.x-1,pc.y-1),(pc.x,pc.y-1),(pc.x+1,pc.y-1),(pc.x-1,pc.y),(pc.x+1,pc.y),(pc.x-1,pc.y+1),(pc.x,pc.y+1),(pc.x+1,pc.y+1))
	#################

	while (cmd not in AUTHORIZED_CMD[:2]):
		################################## Clear the screen at the beginning of every loop
		clr_screen()
		############################### Variable and stats setup/reset every loop
		print_map(game_map, pc.x, pc.y, pc.icon)
		print(msg)
		msg = ''
		mvmt = pc.movlen + pc.jmp
		pc.jmp = 0
		pc.shield = False
		pc.pts = pc.hp + pc.gold + pc.kills + pc.lives + pc.luck
		################################################## User input
		cmd = raw_input('>> ').lower()
		############################## Input processing
		if (cmd == 'help'):
			clr_screen()
			raw_input(tut)
			continue
		elif (cmd == 'print'):
			raw_input("%d,%d" % (pc.x, pc.y))
			continue
		elif (cmd in AUTHORIZED_CMD[4:7]):
			msg += 'HP: ' + str(pc.hp) + ' | Mana: ' + str(pc.mp) + ' | Gold: '
			msg += str(pc.gold) + ' | Lives: ' + str(pc.lives) + ' | Deaths: '
			msg += str(pc.deaths) + ' | Kills: ' + str(pc.kills) + ' | Points: '
			msg += str(pc.pts) + ' | Movement length: ' + str(pc.movlen)
			msg += ' | Jump: ' + str(pc.jmp) + ' | Shield: ' + str(pc.shield)
			#msg += ' | Luck: ' + str(luck)
			continue
		elif (cmd == 'w') and (pc.y-mvmt >= 0) and (game_map[pc.y-mvmt][pc.x] is not Terrain.Unwalk):
			pc.y-=mvmt
		elif (cmd == 'a') and (pc.x-mvmt >= 0) and (game_map[pc.y][pc.x-mvmt] is not Terrain.Unwalk):
			pc.x-=mvmt
		elif (cmd == 's') and (pc.y+mvmt <  n) and (game_map[pc.y+mvmt][pc.x] is not Terrain.Unwalk):
			pc.y+=mvmt
		elif (cmd == 'd') and (pc.x+mvmt <  n) and (game_map[pc.y][pc.x+mvmt] is not Terrain.Unwalk):
			pc.x+=mvmt
		elif (cmd == Keybinding.Jump):
			if (Keybinding.Jump.upper() in pc.inv):
				pc.jmp = 1
				msg += 'You can now jump. '
			else: msg += 'You do not possess the ability to jump. '
			continue
		elif (cmd == Keybinding.Shield):
			if ('S' in pc.inv):
				pc.shield = True
				msg += 'Shielded. '
			else: msg += 'No shield. '
			continue
		elif (cmd == Keybinding.Inventory):
			msg += str(pc.inv)
			continue
		elif (cmd == Keybinding.RingOfFire):
			if (Keybinding.RingOfFire.upper() in pc.inv):
				pc.mp-=5
				for area in box_coords:
					if (0 <= area[0] < n) and (0 <= area[1] < n) and (game_map[area[1]][area[0]] == Terrain.Monster):
						game_map[area[1]][area[0]] = Terrain.Walk
			else: msg += 'You do not possess a Ring of Fire. '
		elif (cmd == '') or (cmd.count(' ') is len(cmd)):
			#~ continue
			if (pc.luck > 0): pc.luck-=1
		else:
			msg += 'Invalid input. '
		############################ Events depending on current block position
		curpos = game_map[pc.y][pc.x]

		if (curpos == Terrain.Win):
			clr_screen()
			raw_input("You have won the game!\nHere are your points: " + str(pc.pts))
			break
		elif (curpos == Terrain.Fire):
			pc.hp-=1
			msg += 'You lost 1 hp by fire damage. '
			if (randint(0,10+pc.luck) >= 10):
				pc.inv.append(Keybinding.RingOfFire.upper())
				msg += 'You now possess a Ring of Fire. Input "' + Keybinding.RingOfFire + '" to use. Costs 5 mana per use. '
		elif (curpos == Terrain.Heal):
			if (randint(-1,1+pc.luck) < 1): hpgain = 1
			else: hpgain = 1 + pc.luck//5
			pc.hp+=hpgain
			game_map[pc.y][pc.x] = Terrain.Walk
			msg += 'You have gained ' + str(hpgain) + ' hp. '
		elif (curpos == Terrain.Jump):
			pc.inv.append(Keybinding.Jump.upper())
			game_map[pc.y][pc.x] = Terrain.Walk
			msg += 'You now possess the ability to jump. Input "' + Keybinding.Jump + '" and then the direction to use. '
		elif (curpos == Terrain.Point):
			pc.pts+=2
			game_map[pc.y][pc.x] = Terrain.Walk
			msg += 'You have gained 2 points. '
		elif (curpos == Terrain.Monster):
			if (pc.shield):
				dmg = randint(0, (1//pc.luck+1))
			else:
				dmg = randint(0, (1//pc.luck+1)*2)
			pc.hp -= dmg
			msg += 'You attacked a monster and have lost ' + str(dmg) + ' hp. '
			if (randint(-1, pc.luck+1) > 0):
				game_map[pc.y][pc.x] = Terrain.Walk
				msg += 'The monster died. '
		elif (curpos == Terrain.Life):
			pc.lives+=1
			game_map[pc.y][pc.x] = Terrain.Walk
			msg += 'You have gained a life. '
		elif (curpos == Terrain.Shield):
			pc.inv.append('S')
			game_map[pc.y][pc.x] = Terrain.Walk
			msg += 'You have gained a shield. Input "' + Keybinding.Shield + '" to enter shield stance for a turn. '

		if (randint(0,50+pc.luck) is 0):
			game_map[pc.y][pc.x] = Terrain.Unwalk
			msg += 'The ground at your feet feels shaky. '

		################################################## Death and permanent death
		if (pc.hp is 0):
			clr_screen()
			pc.die()
			raw_input('You died.')
			if (pc.lives is 0):
				raw_input("GAME OVER\nHere are your points: " + str(pc.pts))
				break
		#################################################################### Innate HP and mana regen
		if (pc.mp < 20) and (pc.luck > randint(0, pc.luck//2)): pc.mp+=randint(0,2)
		if (pc.hp < 20) and (pc.luck > randint(0, pc.luck//2)): pc.hp+=randint(0,2)
		##################################

	return 0

#######################################################################################

def start_game():
	again = True
	while (again):
		clr_screen()
		try:
			mapsize = int(input('Map size? '))
		except ValueError:
			mapsize = 10
		game_map = gen_empty_map(mapsize)
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
	sys.exit(main(sys.argv))
