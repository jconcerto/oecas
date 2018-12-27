#!/usr/bin/env python
import get_oec
import repomanager
import catmanager
import os

# available commands
oecas_commands = {"exit", "help", "update", "commit", "clear", "clog",
                  "clog -add", "clog -edit", "clog -del"}

def display_commands():
	print("Commands:")
	print("   update: Updates local repo")
	print("   commit: Commits local repo to Git")
	print("   clog: View catalogue information currently in system")
	print("       -add: Add a new catalogue to the system")
	print("       -edit: Edit existing catalogue configuration data in the system")
	print("       -del: Delete existing catalogue data in the system")
	print("   clear: Clears the screen")
	print("   help: Display all commands")
	print("   exit: Close OECAS")

def clear_oecas():
	os.system('cls' if os.name == 'nt' else 'clear')
	print("Welcome to the Open Exoplanet Catalogue Approval System (OECAS)\n")
	display_commands()

def close_oecas():
	global taking_input
	taking_input = False

def run_command(command):
	if command == 'exit':
		close_oecas()
	elif command == 'help':
		display_commands()
	elif command == 'update':
		repomanager.update()
		get_oec.get()
	elif command == 'commit':
		repomanager.commit()
	elif command == 'clog':
		catmanager.info_catalogues()
	elif command == 'clog -add':
		catmanager.add_catalogue()		
	elif command == 'clog -edit':
		catmanager.edit_catalogues()
	elif command == 'clog -del':
		catmanager.del_catalogue()
	elif command == 'oec_local':
		get_oec.get()
	elif command == 'clear':
		clear_oecas()

def main():
	global taking_input
	clear_oecas()
	# begin taking input from user
	taking_input = True
	while taking_input == True:
		print("> ", end="")
		# get user input and set it to lowercase for easy comparison
		com_input = input().lower()
		if com_input and not (com_input in oecas_commands):
			# get regex of input just in case
			com_input = fix_str(com_input)
		# check if input is an existing command
		if (com_input in oecas_commands):
			run_command(com_input)
		elif not (len(com_input) == 0):
			print("Invalid command")
	exit()

try:
	main()
except Exception:
	raise
