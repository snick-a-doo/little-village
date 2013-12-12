#!/usr/bin/python

# command.py - Master command for the Little Man Computer emulator.
#
# Copyright 2013 Sam Varner
#
# This file is part of Little Village
#
# Little Village is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Little Village is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Little Village.  If not, see <http://www.gnu.org/licenses/>.

from . import assemble
from . import batch
from . import prompt
from . import console

import sys

# The name of each imported module above must be in this list.
commands = ['assemble', 'batch', 'prompt', 'console', 'help', 'version']

def find_command (name):
    matches = []
    # Strip leading dashes, e.g. '--version' becomes 'version'.
    name = name.split ('-')[-1]
    for cmd in commands:
        if cmd.find (name) == 0:
            matches.append (cmd)
    return matches [0] if len (matches) == 1 else 'help'

def print_help (app):
    print (
'''Master command for the Little Man Computer

Usage: %s <command> [<arguments>]

where <command> is one of''' % app)
    for cmd in commands:
        print ('  %s' % cmd)
    print(
'''
For help on a command, use
  $ %s help <command>
''' % app)

def print_version ():
    print ('''
Little-village version 0.1
Copyright (C) 2013 Sam Varner <snick-a-doo@comcast.net>
This program is free software; you are welcome to redistribute it
under certain conditions.''')

def run ():
    command = 'help' if len (sys.argv) < 2 else find_command (sys.argv [1])
    rest = sys.argv [2:]

    need_help = False
    if command == 'help' and len (rest) > 0:
        # If "help <command>" was entered record that help was requested and get
        # the command name.
        need_help = True
        command = find_command (rest [0])

    if command == 'help':
        # If the command is still "help" show the top-level help message.
        print_help (sys.argv [0])
    elif command == 'version':
        print_version ()
    else:
        program = '%s %s' % (sys.argv [0], command)
        # Find the module that corresponds to the command.  This is why the
        # module names must be in the command list.
        module = getattr (sys.modules[__name__], command)
        if need_help:
            # Show the full command in the help message. 
            program = '%s %s' % (sys.argv [0], command)
            module.print_help (program)
        else:
            module.run (command, rest)
