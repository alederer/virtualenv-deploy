#!/usr/bin/env python

import sys, os, subprocess, shutil
from os import path
import urllib2

WINDOWS = sys.platform == 'win32'

if WINDOWS:
	sys.stderr.write(
	"""Currently virtualenv-autodeply doesn't support Windows,
	since Windows doesn't ship with a way to untar virtualenv,
	meaning it can't be installed automatically for sure.\n""")
	exit(1)

VENV_SRC_DIR = "virtualenv-1.9.1"
VENV_TAR = VENV_SRC_DIR + ".tar.gz"
VENV_URL = "https://pypi.python.org/packages/source/v/virtualenv/" + VENV_TAR
DIR = path.abspath(path.dirname(__file__))
BIN = path.join(DIR, 'Scripts' if WINDOWS else 'bin')
LIB = path.join(DIR, 'Lib' if WINDOWS else 'lib')
INCLUDE = path.join(DIR, 'include')
PYTHON = path.join(BIN, 'python.exe' if WINDOWS else 'python')
PIP = path.join(BIN, 'pip.exe' if WINDOWS else 'pip')
REQUIREMENTS = path.join(DIR, 'requirements.txt')
PREV_REQUIREMENTS = path.join(DIR, 'virtualenv-autodeploy-prev-requirements.txt')

def main():
	if not path.exists(PYTHON):
		setup_virtualenv()
	else:
		# requirements may have changed, must compare
		requirements = ""

		if path.exists(REQUIREMENTS):
			with open(REQUIREMENTS, "r") as file:
				requirements = file.read()

		# at this point we could directly compare against the output of
		# PIP freeze, but it's actually pretty slow...
		### process = subprocess.Popen([PIP, "freeze"], stdout=subprocess.PIPE)
		### prevRequirements, err = process.communicate()

		# instead of directly reading PIP freeze, we read the cached version
		# from when we last installed
		prevRequirements = ""
		if path.exists(PREV_REQUIREMENTS):
			with open(PREV_REQUIREMENTS, "r") as file:
				prevRequirements = file.read()

		if requirements != prevRequirements:
			print("! requirements.txt has changed, reinstalling the virtualenv")
			setup_virtualenv()

	# go through real entry point once all is well
	args = sys.argv[1:]
	# note that we don't use check_call - we don't personally care about the return code,
	# just patching it through, so no reason to raise an error on non-zero return code
	return_code = subprocess.call([PYTHON, path.join(DIR, "src", "main.py")] + args)
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
		subprocess.check_call([PIP, "install", "-r", REQUIREMENTS])

		shutil.copyfile(REQUIREMENTS, PREV_REQUIREMENTS)
	except:
		remove_virtualenv()
		raise
	finally:
		cleanup()

def remove_virtualenv():
	print("--- Removing virtualenv")
	for folder in [BIN, LIB, INCLUDE]:
		if path.exists(folder):
			shutil.rmtree(folder)
	if path.exists(PREV_REQUIREMENTS):
		os.remove(PREV_REQUIREMENTS)

def cleanup():
	print("--- Cleaning up...")
	os.chdir(DIR)
	if path.exists(VENV_SRC_DIR):
		shutil.rmtree(VENV_SRC_DIR)
	if path.exists(VENV_TAR):
		os.remove(VENV_TAR)
	# note that prev-requirements is required to stay around

if __name__ == "__main__":
	main()
