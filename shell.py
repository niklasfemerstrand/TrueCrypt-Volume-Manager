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
import tcvm_cmd
import signal
import sys
import os
import tcvm_lib
import readline

if not sys.stdin.isatty():
	raise Exception("Error: Not attached to tty")

signal.signal(signal.SIGINT, signal.SIG_IGN)
signal.signal(signal.SIGQUIT, signal.SIG_IGN)
signal.signal(signal.SIGTSTP, signal.SIG_IGN)
signal.signal(signal.SIGTTIN, signal.SIG_IGN)
signal.signal(signal.SIGTTOU, signal.SIG_IGN)
#signal.signal(signal.SIGCHLD, signal.SIG_IGN)

print "\033[1;41m:: TrueCrypt Volume Manager (c) 2013 qnrq ::\033[1;m"
print "\033[1;42m:: type help for help for help for help.. ::\033[1;m"

tcvm_lib.CONFIG = tcvm_lib.loadConfig()

no_conf_whitelist = ["help", "clear", "exit", "configure", "unmount"]

def complete(text, state):
	for cmd in tcvm_cmd.executable:
		if cmd.startswith(text):
			if not state:
				return cmd + " "
			else:
				state -= 1

while True:
	readline.parse_and_bind("tab: complete")
	readline.set_completer(complete)
	cmd = raw_input("\033[1;31mTCVM>\033[1;m ")
	c = cmd.split(' ', 1)

	try:
		args = c[1]
	except:
		args = ""

	if c[0] not in tcvm_cmd.executable:
		if len(c[0]) > 0:
			print "Invalid command:", c[0]
		continue

	# Exclude tcvm_lib definitions from typable commands
	try:
	    command = getattr(tcvm_cmd, c[0])
	except AttributeError:
		if len(cmd) > 0:
			print "Command not found:", c[0]
	else:
		if not os.path.isfile(tcvm_lib.HOME + "/.tcvm.conf"):
			if c[0] not in no_conf_whitelist:
				print "\033[1;31mSeriously: configure\033[1;m"
				continue
		command(args)
