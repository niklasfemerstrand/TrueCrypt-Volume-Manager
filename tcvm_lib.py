#!/usr/bin/python2.7
# Copyright (c) 2013, Niklas Femerstrand <nik@qnrq.se>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# -*- coding: utf-8 -*-
import re
import os
import json
import getpass
import hashlib
import subprocess
import ConfigParser

global HOME
global CONFIG
HOME = os.path.expanduser('~')

def loadConfig():
	if not os.path.isfile(HOME + "/.tcvm.conf"):
		print "\033[1;31mWARNING: Missing configuration file, run configure\033[1;m"
		return

	config = ConfigParser.RawConfigParser()
	config.read(HOME + "/.tcvm.conf")

	return config

def configValue(section, value):
	global CONFIG

	if hasattr(CONFIG, "get"):
		return CONFIG.get(section, value)

	CONFIG = loadConfig()

	try:
		return CONFIG.get(section, value)
	except AttributeError:
		return 0

# http://code.activestate.com/recipes/577058/
# Yes it sucks so what
def query_yes_no(question, default="yes"):
    valid = { "yes" : "yes", "y" : "yes", "ye" : "yes",
              "no"  :"no",   "n" : "no" }

    if default == None:
        prompt = " [y/n]:"
    elif default == "yes":
        prompt = " (default yes) [Y/n]:"
    elif default == "no":
        prompt = " (default no) [y/N]:"
    else:
        raise ValueError("Invalid default answer: '%s'" % default)

    while 1:
		print question + prompt,
		choice = raw_input().lower()

		if default is not None and choice == '':
			return default
		elif choice in valid.keys():
			return valid[choice]
		else:
			print("Please respond with 'yes' or 'no' (or 'y' or 'n').")

def query_range(question, opts, default = ""):
	while True:
		i = 0
		print "\033[1;31m" + question + "\033[1;m"

		for opt in opts:
			print "%i: %s" % (i, opt)
			i += 1

		if default != "":
			print "(Default %i)" % (default)

		choice = query_int({ "default" : default })

		try:
			return opts[choice]
		except IndexError:
			print "You failed to select an item from a list, n00b."
			pass

def query_int(opts = {}):
	if not "question" in opts:
		opts["question"] = ": "

	while True:
		answer = raw_input(opts["question"])

		if "default" in opts:
			if opts["default"] != "":
				if answer == "":
					return opts["default"]

		try:
			answer = int(answer)
		except ValueError:
			continue
		else:
			break

	return answer

def query_str(opts = {}):
	if "question" not in opts:
		opts["question"] = ": "

	while True:
		answer = raw_input(opts["question"])

		if answer == "":
			print "\033[1;31mCan not be empty\033[1;m"
		else:
			return answer
	
def validFilename(filename):
	valid = ['-', '_', '.', '(', ')', 'a', 'b', 'c',
             'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
             'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
             't', 'u', 'v', 'w', 'x', 'y', 'z', 'A',
             'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
             'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
             'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
             'Z', '0', '1', '2', '3', '4', '5', '6',
             '7', '8', '9']

	for c in filename:
		if c not in valid:
			return 0

	if filename == "master.tc":
		return 0

	return 1

def escape(s):
	return "\\'".join("'" + p + "'" for p in s.split("'"))

def createContainer(opts = {}):
	if "volume-type" not in opts:
		opts["volume-type"] = query_range("Volume type:", ["Normal", "Hidden"], 0)

	if "path" not in opts:
		container_path = configValue("main", "container_path")

		while True:
			name = query_str({ "question" : "Container name: " })

			if not validFilename(name):
				print "Illegal filename"
			elif os.path.exists(container_path + name):
				print "Container already exists"
			else:
				opts["path"] = configValue("main", "container_path") + name
				break
	else:
		name = "master.tc"

	if "size" not in opts:
		opts["size"] = 0

		while opts["size"] < 1:
			opts["size"] = query_int({ "question" : "Size int(Gb): " }) * 1073741824

	if "encryption" not in opts:
		opts["encryption"] = query_range("Encryption algorithm: ",
                                        ["AES", "Serpent", "Twofish",
                                         "AES-Twofish", "AES-Twofish-Serpent",
                                         "Serpent-AES", "Serpent-Twofish-AES",
                                         "Twofish-Serpent"], 4)

	if "hash" not in opts:
		opts["hash"] = query_range("Hash algorihm:",
                                  ["RIPEMD-160", "SHA-512", "Whirlpool"], 0)

	if "filesystem" not in opts:
		opts["filesystem"] = query_range("Filesystem:",
                                        ["None", "FAT", "EXT2",
                                         "EXT3", "EXT4"])

		for k in opts:
			print "\033[1;32m%-12s\033[1;m: %s" % (k, opts[k])
			opts[k] = escape(str(opts[k]))

	if name != "master.tc" and configValue("main", "use_master_container") == "yes":
		rand = os.urandom(64)
		passphrase = hashlib.sha512(rand).hexdigest()[:64]
		savePass(name, passphrase)
	else:
		passphrase = getPass()

	print "\033[1;32mCreating container " + opts["path"] + "\033[1;m"

	os.popen("truecrypt -t -c --random-source=\"/dev/random\" --volume-type=" + opts["volume-type"] + " --size=" + opts["size"] + " --encryption=" + opts["encryption"] + " --hash=" + opts["hash"] + " --filesystem=" + opts["filesystem"] + " --password=" + escape(passphrase) + " --keyfiles='' " + opts["path"])

	if name != "master.tc":
		if query_yes_no("Would you like to mount " + name + " now?") == "yes":
			mountContainer({ "path" : opts["path"] })

def unmountDrive(opts = {}):
	if "path" not in opts:
		opts["path"] = ""

	if opts["path"] == "":
		os.popen("truecrypt -t -d")
		return

	if not os.path.exists(opts["path"]):
		print "Invalid path"
		return

	os.popen("truecrypt -t -d " + escape(opts['path']))

# TODO Detect when container fails to mount (switch os.popen with subprocess.Popen() and parse stderr)
def mountContainer(opts = {}):
	if "path" not in opts:
		print "Missing container path"
		return

	for k in opts:
		opts[k] = escape(opts[k])

	print "\033[1;32mMounting container " + opts["path"] + "...\033[1;m"

	if configValue("main", "use_master_container") == "yes":
		if re.search("master\.tc", opts["path"]) is None:
			masterMount = findMount("master.tc")
			master_path = configValue("main", "container_path") + "master.tc"
			if masterMount is False:
				print "I need to mount master.tc to access this container's passphrase."
				mountContainer({ "path" : master_path })
				masterMount = findMount("master.tc")

			if os.path.exists(masterMount + "/drives.txt") is False:
				# TODO Add more serious warning
				# TODO Read passphrase from stdin
				print "[!] drives.txt missing from master.tc mount"
				return

			f = open(masterMount + "/drives.txt", "r+")
			data = json.load(f)

			for drive in data["drives"]:
				container_path = configValue("main", "container_path")

				# "'" after escape()
				if "'" + container_path + drive + "'" == opts["path"]:
					passphrase = data["drives"][drive]
					break

			f.close()
			unmountDrive({ "path" : master_path })
		else:
			passphrase = getPass(0)
	else:
		passphrase = getPass(0)

	i = 1

	while True:
		tmp = "/media/truecrypt%i" % (i)
		p = subprocess.Popen(["truecrypt", "-t", "-l", tmp],
                             shell  = False,
                             stderr = subprocess.PIPE,
                             stdout = subprocess.PIPE)

		if p.communicate()[1] == "Error: No such volume is mounted.\n":
			mountPoint = tmp
			break

		i += 1

	os.popen("truecrypt -t --protect-hidden=no --keyfiles='' --password=" + escape(passphrase) + " " + opts["path"] + " " + mountPoint)

def getPass(verify = 1):
	while True:
		p1 = getpass.getpass("Passphrase: ")

		if len(p1) < 8:
			print "Your passphrase must be minimum 8 characters, at least 20 is recommended"
			continue

		if len(p1) < 20 and verify == 1:
			print "Your passphrase should really be at least 20 characters, but I won't stand in your way."

		if verify is 1:
			p2 = getpass.getpass("Verify passphrase: ")

			if p1 != p2:
				print "Passphrase string mismatch"
			else:
				break
		else:
			break

	return p1

def savePass(name, passphrase):
	mountPoint = findMount("master.tc")
	master_path = configValue("main", "container_path") + "master.tc" 

	if mountPoint is False:
		# TODO Fix failure detection in mountContainer() so the script doesn't crash here
		mountContainer({ "path" : master_path })
		savePass(name, passphrase)
		return

	# TODO pretty hackish, structure better
	if os.path.exists(mountPoint + "/drives.txt"):
		f = open(mountPoint + "/drives.txt", "r+")
		data = json.load(f)
		data["drives"].update({ name : passphrase })
		f.seek(0)
		f.write(json.dumps(data))
	else:
		f = open(mountPoint + "/drives.txt", 'w')
		f.write(json.dumps({ "drives" : { name : passphrase } }))

	f.close()
	unmountDrive({ "path" : master_path })

def findMount(drive):
	path = configValue("main", "container_path") + drive
	p = subprocess.Popen(["truecrypt", "-t", "-l", path],
                          shell  = False,
                          stderr = subprocess.PIPE,
                          stdout = subprocess.PIPE)
	ret = p.communicate()

	if ret[1] == "Error: No such volume is mounted.\n":
		return False

	m = re.split(" ", ret[0])
	mountPoint = m[3].replace("\n", "")

	return mountPoint

def changePassphrase(opts = {}):
	if "drive" not in opts:
		raise Exception("Missing drive")

	container_path = configValue("main", "container_path") + opts["drive"]

	if not os.path.isfile(container_path):
		print "Drive not found"
		return

	drive_was_unmounted = True
	mountPoint = findMount(opts["drive"])
	use_master_container = configValue("main", "use_master_container")

	if mountPoint is False:
		print "Found ejected drive, mounting..."
		drive_was_unmounted = False
		mountContainer({ "path" : container_path })
		mountPoint = findMount(opts["drive"])

	if use_master_container == "yes" and opts["drive"] != "master.tc":
		master_path = configValue("main", "container_path") + "master.tc"
		print "Generating new random passphrase..."
		rand = os.urandom(64)
		new_passphrase = hashlib.sha512(rand).hexdigest()[:64]
		print "New passphrase:", new_passphrase

		print "I need to mount master.tc to update the passphrase storage"

		mountContainer({ "path" : master_path })
		f = open(findMount("master.tc") + "/drives.txt", "r+")
		data = json.load(f)
		old_passphrase = data["drives"][opts["drive"]]
		print "Old passphrase:", old_passphrase
		f.close()
		unmountDrive({ "path" : master_path })
	else:
		print "Current"
		old_passphrase = getPass(0)
		print "Change to"
		new_passphrase = getPass()

	print "Changing passphrase, this might take a while"
	os.popen("truecrypt -t -C --new-keyfiles='' --random-source='/dev/random' -p=" + escape(old_passphrase) + " --new-password=" + escape(new_passphrase) + " " + container_path)

	if opts["drive"] != "master.tc" and use_master_container == "yes":
		# TODO Only do this if passphrase update succeeded
		savePass(opts["drive"], new_passphrase)

	if drive_was_unmounted:
		unmountDrive({ "path" : container_path })
