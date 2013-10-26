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

class Not_Enough_Inputs (Exception):
    '''Exception raised when program requires more inputs than were provided.'''
    def __str__ (self):
        return 'Not enough inputs.'

class Unused_Inputs (Exception):
    '''Exception raised when some of the provided inputs were not used by the program.'''
    def __init__ (self, inputs):
        self.inputs = inputs
    def __str__ (self):
        str = 'Unused inputs: '
        for a in self.inputs:
            str += (a + ' ')
        return str

class Batch_Client (lmc.LMC_Client):
    '''A non-interactive LMC client.

    All input is supplied when the object is created.  All program output is
    stored in the member list "outputs".'''
    def __init__ (self, program, inputs):
        lmc.LMC_Client.__init__ (self)
        self.inputs = inputs
        self.outputs = []
        self.computer.load (program)

    def run (self):
        '''Start execution of the program.'''
        self.computer.run ()

    def notify_input (self):
        '''Provide input when needed by the program during execution.

        The input value is removed from the input list.  If the input list is
        empty (before removal) Not_Enough_Inputs is raised.''' 
        if len (self.inputs) == 0:
            raise Not_Enough_Inputs
        arg = self.inputs [0]
        self.inputs = self.inputs [1:]
        return arg

    def notify_output (self, out):
        '''Receive output from the program during execution.

        The outputs are saved to an array where they can be used as needed.
        This object does not handle display of the output.'''
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

def print_message (prefix, exception):
    sys.stderr.write (prefix + ': ' + exception.__str__ () + '\n')

def run (program, args):
    if len (args) < 1:
        print_help (program)
    else:
        try:
            client = Batch_Client (args [0], args [1:])
            client.run ()
            # Print the output.
            for n in client.outputs:
                print n
            # Check for extra input.
            if len (client.inputs) > 0:
                raise Unused_Inputs (client.inputs)
        except (lmc.Program_File_Not_Found,
                lmc.Bad_Input_Type, 
                Not_Enough_Inputs), error:
            print_message ('Error', error)
        except (Unused_Inputs), warning:
            print_message ('Warning', warning)
        except Exception, error:
            print_message ('Internal', error)

if __name__ == '__main__':
    run (sys.argv [1:])
