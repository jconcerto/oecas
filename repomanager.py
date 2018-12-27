#!/usr/bin/env python

from oecas_external import parse_csv
import configparser
import github
import gui
import datetime
import xml.etree.ElementTree as ET 
import os
from base64 import b64decode

# commit code based on: http://stackoverflow.com/questions/38594717/how-do-i-push-new-files-to-github/39627647#39627647

# Read config data from settings file
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()
config.read("config.ini")
TEMP_FOLDER = config.get("DIRECTORIES", "temp_data")
TEMPLATES = config.get("DIRECTORIES", "templates")
LOCAL_FOLDER = config.get("DIRECTORIES", "local_repo")

BRANCH_NAME = config.get("GITHUB", "branch_name")
REPO_NAME = config.get("GITHUB", "repo_location")

def update():
	"""
		Gets exoplanet data from other catalogues, parses them, and saves them as xml
		format in a local folder.
    """
	# Get catalogue configuration data, loop through and update each one
	cat_list = [x for x in config.sections() if 'CATALOGUE' in x]
	
	# Loops though all catalogues, commented out for now in order to 
	# seperate files to different folders.
	for cat in cat_list:
		url         = config.get(cat, "url")
		filename    = config.get(cat, "filename")
		template    = TEMPLATES + '/' + config.get(cat, "template")
		parsed_dir  = config.get(cat, "parsed_dir")
		# download file from given url and check if identical to existing (if any)
		identical_to_existing = parse_csv.get(url, TEMP_FOLDER, filename)
		parse_csv.parse(filename, parsed_dir, TEMP_FOLDER, template)
		
		# do post processing on xml data (if a script was specified)
		if config.has_option(cat, "pp_script"):
			parse_csv.post_process(parsed_dir, config.get(cat, "pp_script"))



def auth_user():
	"""(NoneType) -> Github

        Checks if the user is already logged in.
        If not, prompts the user to login to Github
        and returns the Github class
    """
	auth = gui.prompt_login()
	if auth == None:
		print("\nTry again")
	else:
		current_user = auth.get_user()
	return auth

def get_main_repo(auth):
	"""(Github) -> Repository

        Given the Github class, attempts to find the
        repository described in config.ini and returns it
     """
	print("\nConnecting to Github...")
	# find the output repository
	try:
		# get the main repository location
		repo_name = REPO_NAME
		repo = auth.get_repo(repo_name)
	except github.GithubException:
		print("Failed, cannot reach repository: " + repo_name)
		print("Check repo_location in config.ini and try again")
		return
	except ConnectionResetError:
		print("\nFailed\n")
		return
	return repo

def get_ref(repo, branch = 'heads/master'):
	"""(Repository, String) -> GitRef

        Gets the git reference of the given branch for the given repository
    """
	return repo.get_git_ref(branch)

def get_ref_sha(repo, branch=None):
	"""(Repository, String or NoneType) -> GitRef, String

        Gets the git reference and sha of the given branch for the given repository
    """
	master_ref = get_ref(repo, branch) if branch else get_ref(repo)
	master_sha = master_ref.object.sha
	return master_ref, master_sha

def get_base_repo(current_user, main_repo, main_sha, DEBUG=False):
	"""(NamedUser, Repository, String, Bool) -> Repository, GitRef, Bool, Bool

        Given the current user, the main repository and its sha, 
        get the base repository (the temporary repository we want to store our files in),
        its reference, whether or not it is a branch, and if it was created during this run of the function
    """
	was_created = False
	base_is_branch = False
	base_repo = None
	base_ref = None
	# check if user has write access to the repo
	if main_repo.permissions.push == True:
		try:
			# get the branch to which merge requests will be made
			base_ref = get_ref(main_repo, "heads/" + BRANCH_NAME)
		except github.GithubException:
			# branch does not exist
			if DEBUG: print("Creating branch: " + BRANCH_NAME)
			# create the branch to which merge requests will be made
			base_ref = main_repo.create_git_ref("refs/heads/" + BRANCH_NAME, main_sha)
			was_created = True
		else:
			if DEBUG: print("Found branch: " + BRANCH_NAME)
		base_is_branch = True
	else:
		# user does not have write access, so going to commit to a fork
		# check if user has already has repository forked
		for r in current_user.get_repos():
			if r.parent == main_repo:
				# user has repository forked
				if DEBUG: print("Found fork: " + r.full_name)
				base_repo = r
				base_ref = get_ref(base_repo)
				break

	if not (base_ref or base_repo):
		# if no base repository to push to, create a new fork
		base_repo = current_user.create_fork(main_repo)
		if DEBUG: print("Created fork: " + base_repo.full_name)
		base_ref = get_ref(base_repo)
		was_created = True

	return base_repo, base_ref, base_is_branch, was_created

def commit_to_repo(file_input, file_output, base_repo, base_ref, base_is_branch):
	"""(String, String, Repository, GitRef, Bool) -> Bool

        Commits the files stored at the given location to the given Repository on Github
        and returns its success
    """
	base_sha = base_ref.object.sha
	base_ref.edit(base_sha, True)

	# push local files to temporary repository to prepare pull request
	print("Committing files...")
	diff_online = False
	base_tree = base_repo.get_git_tree(base_sha)
	element_list = list()
	for entry in os.listdir(file_input):
		with open(file_input + "/" + entry, 'r') as input_file:
			data = input_file.read()
		file_name = os.path.basename(input_file.name)
		file_path = file_output+(file_name.replace(" ", "%20")) # replace whitespace with whitespace characters
		online = None
		try:
			# try to create a new file in the repo
			online = base_repo.create_file(path=file_path, message="Update: " + file_name, content=data, branch=(BRANCH_NAME if base_is_branch else "master"))
		except github.GithubException:
			# file already exists in repo, get it
			online = None
			try:
				online = base_repo.get_contents(file_path) # has 1000 request limit
			except github.RateLimitExceededException:
				print("GitHub Rate Limit Exceeded. Please try again later.")
				return;
			# compare file contents to see if we should update it
			# online contents are doubly encoded so decode online once, and encode local once
			if data.encode("utf-8") != b64decode(online.content):
				sha = online.sha
				base_repo.update_file(path=file_path, message="Update: " + file_name, content=data, branch=(BRANCH_NAME if base_is_branch else "master"), sha=sha)
			else:
				online = None

		if online:
			# file was found and is different
			print(" + " + file_name)
			diff_online = True
		else:
			# file is same as
			pass 

	if not diff_online:
		# end this whole thing if nothing is changed
		print("Nothing to commit, " + ("branch" if base_is_branch else "fork")+ " is up to date with local changes")
		return
	return True


def commit():
	"""
		Commits all files in a specific directory to a repository on Github, where it will be sent to the main repository
		as a pull request.
    """
	auth = auth_user()
	if auth == None:
		# invalid information entered
		return
	current_user = auth.get_user()
	repo = get_main_repo(auth)
	if repo == None:
		# cannot reach repository so exit
		return

	# get the reference code to the repository's master branch
	master_ref, master_sha = get_ref_sha(repo)
	print("Finding somewhere to push files before sending pull request...")
	base_repo, base_ref, base_is_branch, was_created = get_base_repo(current_user, repo, master_sha, True)
	if base_is_branch:
		base_repo = repo
	if not was_created:
		# if the base was not created in this command call, merge master to it to update it
		if base_is_branch:
			commits_behind = base_repo.compare('master', BRANCH_NAME).behind_by
			if commits_behind > 0:
				print("Branch is " + str(commits_behind) + " commit" + ("" if commits_behind == 1 else "s") + " behind master. Merging to branch: " + BRANCH_NAME + "...")
				commit = base_repo.merge(BRANCH_NAME, "master")
				base_ref.edit(commit.sha)
			print("Branch is up-to-date with master.")
		else:
			commits_behind = repo.compare("master", current_user.login+":master").behind_by
			if commits_behind > 0:
				print("Fork is " + str(commits_behind) + " commit" + ("" if commits_behind == 1 else "s") + " behind " + repo.full_name + ". Merging to fork: " + base_repo.full_name + "...")
				commit = base_repo.merge("master", master_sha)
				base_ref.edit(commit.sha)

	success = commit_to_repo(LOCAL_FOLDER+"/parsed_eu", "/systems/", base_repo, base_ref, base_is_branch)
	if not success: return
	print("Files committed.")
	date = datetime.datetime.now()
	print("Sending Pull Request to " + repo.full_name)
	pull_req = None
	try:
		pull_req = repo.create_pull(title="Update: "+ str(date),base="master", head=(BRANCH_NAME if base_is_branch else current_user.login+":master"), body="")
	except github.GithubException as e:
		# a pull request for this user already exists
		# so search through all pull requests to find the one owned by this user to edit it
		for pr in repo.get_pulls():
			if pr.user.login == current_user.login:
				pull_req = pr
				print("Found existing pull request for " + current_user.login)
				break
		if pull_req:
			pull_req.edit()
		else:
			print("Failed: " + str(e.data['errors'][0]['message']) + "\n")
			return

	print("Success!\n")



def cherry_pick_changes(base_repo):
	temp_branch_name = "temp_branch_eocas"
	temp_ref = None
	try:
		# create a branch to stage pull requests
		temp_ref = base_repo.get_git_ref("heads/" + temp_branch_name)
	except github.GithubException:
		pass
	else:
		# delete the temporary branch if it exists
		temp_ref.delete()
	temp_ref = base_repo.create_git_ref("refs/heads/" + temp_branch_name, master_sha)