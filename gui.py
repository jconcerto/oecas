#!/usr/bin/env python

import github	
import re
import getpass
import configparser
import os

# Read config data from settings file
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()
config.read("config.ini")
TOKEN_LOC = config.get("GITHUB", "token_loc")

global current_auth;
current_auth = None

def get_token():
	token = None
	if os.path.exists(TOKEN_LOC):
		with open(TOKEN_LOC) as f:
			token = f.read().strip(' \t\n\r')
			f.close()
	return token

def rm_token():
	if os.path.exists(TOKEN_LOC):
		os.remove(TOKEN_LOC)

def prompt_login():
	global current_auth;
	cancel = False
	if current_auth == None:
		token = get_token()
		used_token = False
		success = True
		if not token:
			# ask user to log in
			print("You must sign into Github to complete that action")
			print("\nUsername: ", end="")
			username = input()
			password = getpass.getpass()
			print("\nAuthenticating...")
			try:
				# try connecting to github
				auth = github.Github(username, password)
			except AssertionError:
				# try again because in some cases, input is encoded with unicode on Unix
				username, password = fix_str(username), fix_str(password)
				auth = github.Github(username, password)
		else:
			# login with saved token that was generated on github website, requires no user input
			print("Logging in with saved credentials...")
			auth = github.Github(token)
			used_token = True

		# to do: catch when user requires 2-step verification
		try:
			current_auth = auth
			current_user = auth.get_user()
			# try to catch an error when calling the login
			current_user.login
		except github.GithubException:
			success = False
			if used_token:
				print("Token did not work. Please get a new GitHub Personal Access Token, or login normally")
				# wipe the file with the token that didn't work
				rm_token()
			else:
				print("Invalid login credentials")
			current_auth = None
		if success:	
			print("\nWelcome " + (current_user.name or current_user.login))
	return current_auth

def fix_str(input_str):
	# fixes rare case of unicode encoded input strings on unix-based systems
	return re.search("\w?.?([\s\d\w]*).?",str(input_str)).group(1)
