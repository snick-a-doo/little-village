#!/usr/bin/python

# batch.py - A non-interactive front end for the Little Man Computer emulator.
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
import sys

class Batch_Client (lmc.LMC_Client):
    def __init__ (self, program, inputs):
        lmc.LMC_Client.__init__ (self)
        self.inputs = inputs
        self.outputs = []
        self.computer.load (program)

    def run (self):
        self.computer.run ()

    def notify_input (self):
        n = self.inputs [0]
        self.inputs = self.inputs [1:]
        return int (n)

    def notify_output (self, out):
        self.outputs.append (out)
        return True

def print_help (app):
    print 'Execute a Little Man Computer program'
    print
    print 'Usage: %s <program-name> [<input>...]' % app
    print
    print 'where <program-name> is the name of a machine-code program file'
    print 'and <input>s are any integer inputs needed by the program.'
    print

def run (args):
    if len (args) < 1:
        print_help (args [0])
    else:
        program = args [0]
        inputs = args [1:]
        client = Batch_Client (program, inputs)
        client.run ()
        for n in client.outputs:
            print n

if __name__ == '__main__':
    run (sys.argv [1:])
