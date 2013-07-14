#!/usr/bin/env python

import sys, os, subprocess, shutil
from os import path
import urllib2

#--------------------------------------------------------------------
# User config, with defaults
#--------------------------------------------------------------------
CONFIG = \
{
	"app_entry" : "src/__main__.py",
	"requirements_file" : "requirements.txt"
}

#--------------------------------------------------------------------
# Constants (mostly paths) used by the script
#--------------------------------------------------------------------
WINDOWS = sys.platform == "win32"
if WINDOWS:
	sys.stderr.write(
	"""Currently virtualenv-autodeply doesn't support Windows,
	since Windows doesn't ship with a way to untar virtualenv,
	meaning it can't be installed automatically for sure.\n""")
	exit(1)

# virtualenv installation files/URLs
VENV_SRC_DIR = "virtualenv-1.9.1"
VENV_TAR = VENV_SRC_DIR + ".tar.gz"
VENV_URL = "https://pypi.python.org/packages/source/v/virtualenv/" + VENV_TAR
# directories created and used by virtualenv
DIR = path.abspath(path.dirname(__file__))
BIN = path.join(DIR, "Scripts" if WINDOWS else "bin")
LIB = path.join(DIR, "Lib" if WINDOWS else "lib")
INCLUDE = path.join(DIR, "include")
LOCAL = path.join(DIR, "local") # local not always present
# relevant file paths
PYTHON = path.join(BIN, "python.exe" if WINDOWS else "python")
PIP = path.join(BIN, "pip.exe" if WINDOWS else "pip")
REQUIREMENTS = path.join(DIR, CONFIG["requirements_file"])
PREV_REQUIREMENTS = path.join(DIR, "virtualenv-ploy-prev-requirements.txt")

#--------------------------------------------------------------------
# virtualenv-deploy implementation
#--------------------------------------------------------------------
def main():
	if not path.exists(PYTHON):
		setup_virtualenv()
	else:
		# requirements may have changed, must compare
		requirements = ""

		if path.exists(REQUIREMENTS):
			with open(REQUIREMENTS, "r") as file:
				requirements = file.read()

		# instead of directly reading PIP freeze, we read the cached version
		# from when we last installed - slightly less safe, but freeze is slow,
		# and this is run every time
		prev_requirements = ""
		if path.exists(PREV_REQUIREMENTS):
			with open(PREV_REQUIREMENTS, "r") as file:
				prev_requirements = file.read()

		if requirements != prev_requirements:
			print("! requirements.txt changed, reinstalling this virtualenv")
			setup_virtualenv()

	# go through real entry point only once all is set up

	# note that we don't use check_call - we don't personally care about the
	# return code, just patching it through, so no reason to raise an error on
	# non-zero return code
	args = sys.argv[1:]
	app_entry = path.join(DIR, CONFIG["app_entry"])
	return_code = subprocess.call([PYTHON, app_entry] + args)
	exit(return_code)

def setup_virtualenv():
	remove_virtualenv()

	try:
		print("--- Downloading virtualenv")
		handle = urllib2.urlopen(VENV_URL)
		with open(VENV_TAR, "wb") as file:
			file.write(handle.read())
		del handle
		
		print("--- Unzipping virtualenv")
		subprocess.check_call(["tar", "-xf", VENV_TAR])

		print("--- Installing virtualenv")
		os.chdir(VENV_SRC_DIR)
		subprocess.check_call(["python", "virtualenv.py", ".."])
		if path.exists(REQUIREMENTS):
			subprocess.check_call([PIP, "install", "-r", REQUIREMENTS])

		print("--- Saving off virtualenv-deploy-prev-requirements.txt")
		if path.exists(REQUIREMENTS):
			shutil.copyfile(REQUIREMENTS, PREV_REQUIREMENTS)
	except:
		remove_virtualenv()
		raise
	finally:
		cleanup_virtualenv_src()

def remove_virtualenv():
	print("--- Removing virtualenv")
	for folder in [BIN, LIB, INCLUDE, LOCAL]:
		if path.exists(folder):
			shutil.rmtree(folder)
	if path.exists(PREV_REQUIREMENTS):
		os.remove(PREV_REQUIREMENTS)

def cleanup_virtualenv_src():
	print("--- Cleaning up virtualenv src...")
	os.chdir(DIR)
	if path.exists(VENV_SRC_DIR):
		shutil.rmtree(VENV_SRC_DIR)
	if path.exists(VENV_TAR):
		os.remove(VENV_TAR)

if __name__ == "__main__":
	main()

