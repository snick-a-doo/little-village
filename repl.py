#!/usr/bin/python

# repl.py - A command-line interface for the Little Man Computer emulator.
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

import lmc
import string

class REPL_Client (lmc.LMC_Client):
    prompt = 'LMC> '

    def notify_input (self):
        return int (raw_input ('  input: '))

    def notify_output (self, out):
        print out
        return True

    def run (self):
        try:
            while self.parse (raw_input (REPL_Client.prompt)):
                pass
        except EOFError:
            # Quit on Ctrl+D
            pass
        print 'bye'

    def read (self):
        response = raw_input (REPL_Client.prompt);

    def parse (self, input):
        tokens = string.split (input)

        if len (tokens) == 0:
            return True

        command = tokens [0]
        argument = ''
        if len (tokens) > 1:
            argument = tokens [1]

        if command[0] == 'q':
            return False
        elif command == 'load':
            self.computer.load (argument)
        elif command == 'run':
            self.computer.run ()
        elif command == 'show':
            print self.computer

        return True

if __name__ == '__main__':
    client = REPL_Client ()
    client.run ()
