#!/usr/bin/python 
import urllib.request
import os
import zipfile
import configparser
from oecas_external import parse_csv
import shutil

# Read config data from settings file
config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()

config.read("config.ini")
TEMP_FOLDER = config.get("DIRECTORIES", "temp_data")
LOCAL_FOLDER = config.get("DIRECTORIES", "local_repo")
dl_name = LOCAL_FOLDER + "/" + "oec.zip"

#Downloads the master zip from github
def get():
	#if the zip already exists, it gets deleted
	if os.path.exists(dl_name):
		os.remove(dl_name)
	print("Downloading OEC.")
	url = "https://github.com/OpenExoplanetCatalogue/open_exoplanet_catalogue/archive/master.zip"
	dl_file = urllib.request.urlretrieve(url, dl_name)
	print("Downloading complete.")
	extract()

#extracts the downloaded zip
def extract():
	print("Extracting OEC.")
	zf = zipfile.ZipFile(dl_name)
	zf.extractall(LOCAL_FOLDER + "/oec_temp")
	zf.close()
	print("Extracting complete.")
	move()

#Moves the correct downlaoded files to a local directory and deletes remaining files
def move():
	src = LOCAL_FOLDER + "/oec_temp/open_exoplanet_catalogue-master/systems/"
	dest = LOCAL_FOLDER + "/oec_local/"
	#makes directory if it does not exist
	if not os.path.exists(dest):
		os.makedirs(dest)
	#create a list of files to move
	files = os.listdir(src)
	#iterates through the directory and moves the files
	for x in files:
		try:
			os.rename(src + x, dest + x)
		except FileExistsError:
			os.remove(dest + x)
			os.rename(src + x, dest + x)
			
	print("Cleaning up.")	
	shutil.rmtree(LOCAL_FOLDER + "/oec_temp/")
	os.remove(dl_name)
	
	print("Done.")