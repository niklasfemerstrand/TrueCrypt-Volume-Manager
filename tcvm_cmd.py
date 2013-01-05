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
import os
import sys
import getpass
import signal
import ConfigParser
from tcvm_lib import *

executable = ["help", "clear", "showconf", "configure",
              "create", "chpass", "list", "mount",
              "unmount", "exit"]

def help(args = ""):
	help = []
	help.append({ "help"                     : "Shows this help" })
	help.append({ "clear"                    : "Clears the terminal" })
	help.append({ "showconf"                 : "Prints current configuration table" })
	help.append({ "configure"                : "Configuration wizard" })
	help.append({ "create"                   : "Creates encrypted container (wizard)" })
	help.append({ "chpass <drive>"           : "Changes passphrase of given drive" })
	help.append({ "list <all|mounted>"       : "Lists located containers" })
	help.append({ "mount <drive> <path>" : "Mounts a drive" })
	help.append({ "unmount <all|drive>"      : "Unmounts a drive" })
	help.append({ "exit"                     : "Exits tcvm" })

	if args is not "":
		for dicts in help:
			for k in dicts.keys():
				if args == k:
					print dicts[k]
	else:
		print "%-26s   %s" % ("Command", "Description")
		print "%-26s   %s" % ("-------", "-----------")

		for dicts in help:
			for k in dicts.keys():
				print("%-26s   %s" % (k, dicts[k]))

def clear(args = ""):
	for i in range(0, 20):
		print "\n"

def list(args = ""):
	if args is "":
		args = "all"

	mounted = subprocess.Popen(["truecrypt", "-t", "-l"],
                               shell=False,
                               stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE).communicate()

	if args == "all":
		container_path = configValue("main", "container_path")
		containers = os.listdir(container_path)

		if containers == []:
			print "No containers found in container path"
			return

		print("%7s %10s") % ("Mounted", "Container")
		print("----------------------------------")

		for container in containers:
			mountStatus = ""

			try:
				mounted[0].index(container)
			except ValueError:
				pass
			else:
				mountStatus = "*   "

			print("%7s %10s") % (mountStatus, container_path + container)
	elif args == "mounted":
		if mounted[1] == "Error: No volumes mounted.\n":
			print "No drive mounted"
			return

		print mounted[0],
	else:
		print "Invalid arg"

def exit(args = ""):
	print "Bye!"
	sys.exit()

def showconf(args = ""):
	if not os.path.isfile(HOME + "/.tcvm.conf"):
		print "No configuration found"
		return

	with open(HOME + "/.tcvm.conf") as f:
		for l in f:
			if l != "\x0a":
				print l, # <- Not a typo, the lines contain \n

def configure(args = ""):
	if os.path.isfile(HOME + "/.tcvm.conf"):
		overwrite_config = query_yes_no("Configuration file exists, delete?", default="no")

		# TODO reload conf to prevent forced shell reload
		if overwrite_config is "yes":
			os.remove(HOME + "/.tcvm.conf")
		elif overwrite_config is "no":
			return

	config = ConfigParser.RawConfigParser()
	config.add_section("main")

	unmountDrive()

	container_path = raw_input("Container location (default: " + HOME + "/containers/): ")

	if container_path is "":
		container_path = HOME + "/containers/"

	if not os.path.exists(container_path):
		os.makedirs(container_path, 0755)

	config.set("main", "container_path", container_path)

	use_master_container = query_yes_no("Use master container to store passphrases?", default="yes")

	if use_master_container == "yes":
		master_container_path = container_path + "master.tc"
		createContainer({ "volume-type" : "normal", "size" : "1002400",
                          "encryption"  : "AES-Twofish-Serpent",
                          "hash" : "SHA-512", "filesystem" : "FAT",
                          "path" : master_container_path })

	config.set("main", "use_master_container", use_master_container)

	with open(HOME + "/.tcvm.conf", "wb") as configfile:
	    config.write(configfile)

	CONFIG = loadConfig()

	q = query_yes_no("Create first container?", default="yes")

	if q == "yes":
		createContainer({})

def mount(args = ""):
	container_path = configValue("main", "container_path")

	if args is "":
		args = raw_input("Path: "  )

	if os.path.isfile(container_path + args) is False:
		print "Drive not found"
		return;

	mountContainer({ "path" : container_path + args })

def unmount(args = ""):
	if args == "":
		unmountDrive()
		return

	unmountDrive({ "path" : configValue("main", "container_path") + args })

def create(args = ""):
	createContainer({})

def chpass(args = ""):
	if args == "":
		print "Missing drive"
		return

	changePassphrase({ "drive" : args })
