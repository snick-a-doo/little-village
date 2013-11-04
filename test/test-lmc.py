# test-lmc.py - Unit tests for the LMC back-end and clients.
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

import os
import sys
import unittest

# Allow importing modules from the source directory
sys.path.insert (0, os.path.abspath ('..'))

from little_village import lmc
from little_village import batch

class Test_Initial (unittest.TestCase):
    '''Check the initial state of the computer.'''
    def setUp (self):
        self.computer = lmc.LMC ()

    def test_registers (self):
        for m in self.computer.memory:
            self.assertEqual (m, 0)
        self.assertEqual (self.computer.input, 0)
        self.assertEqual (self.computer.output, 0)
        self.assertEqual (self.computer.accumulator, 0)
        self.assertEqual (self.computer.counter, 0)

    def test_run (self):
        # Run the computer with no program.  The 1st instruction will be
        # interpreted as HLT.  The only effect will be to increment the program
        # counter.
        self.computer.run ()
        for m in self.computer.memory:
            self.assertEqual (m, 0)
        self.assertEqual (self.computer.input, 0)
        self.assertEqual (self.computer.output, 0)
        self.assertEqual (self.computer.accumulator, 0)
        self.assertEqual (self.computer.counter, 0)

class Test_Run (unittest.TestCase):
    '''Test the computer with a small program.

    The program, "add", takes two values from input.  The input register is
    loaded before the program starts and will not change.  So we expect the
    output to be 2 times the input.'''
    def setUp (self):
        self.computer = lmc.LMC ()
        self.computer.load ('add')

    def test_loaded (self):
        self.assertEqual (self.computer.memory [0], 901)
        self.assertEqual (self.computer.memory [4], 902)
        for m in self.computer.memory[5:]:
            self.assertEqual (m, 0)

    def test_run (self):
        self.computer.input = 123
        self.computer.run ()
        self.assertEqual (self.computer.counter, 5)
        self.assertEqual (self.computer.accumulator, 246)
        self.assertEqual (self.computer.output, 246)
    
    def test_rerun (self):
        self.computer.input = 123
        self.computer.run ()
        self.computer.run ()
        # Should get the same answer the 2nd time.
        self.assertEqual (self.computer.output, 246)

class Break_Client (batch.Batch_Client):
    '''A client that breaks execution at a specific line.'''
    def __init__ (self, line):
        batch.Batch_Client.__init__ (self)
        self.break_line = line

    def run (self, program, inputs):
        # Redefine run() so that it does not raise an exception.
        self.inputs = inputs
        self.computer.load (program)
        self.computer.run ()

    def notify_step (self):
        # Return False to stop execution when the counter gets to break_line.
        return self.computer.counter != self.break_line

class Test_Break (unittest.TestCase):
    '''Test breaking, stepping, and resuming.'''
    def setUp (self):
        self.inputs = [888, 99]
        self.line = 2 # Break before this (0-based) instruction.
        self.client = Break_Client (self.line)
        self.client.run ('add', self.inputs)

    def test_break_and_resume (self):
        self.assertEqual (self.line, self.client.computer.counter)
        self.assertEqual (self.client.outputs, [])
        self.client.computer.resume ()
        self.assertEqual (self.client.outputs, [987])

    def test_break_and_step (self):
        self.assertEqual (self.client.computer.input, 888)
        self.assertEqual (self.client.computer.accumulator, 888)
        self.assertEqual (self.client.outputs, [])
        self.client.computer.step () # get 2nd input
        self.assertEqual (self.client.computer.input, 99)
        self.assertEqual (self.client.computer.accumulator, 99)
        self.assertEqual (self.client.outputs, [])
        self.client.computer.step () # add
        self.assertEqual (self.client.computer.accumulator, 987)
        self.assertEqual (self.client.outputs, [])
        self.client.computer.resume ()
        self.assertEqual (self.client.outputs, [987])

    def test_step_at_end (self):
        self.client.computer.resume ()
        self.assertEqual (self.client.computer.counter, 5)
        self.client.computer.step ()
        # Can't step past HLT.
        self.assertEqual (self.client.computer.counter, 5)
        self.client.computer.step ()
        self.assertEqual (self.client.computer.counter, 5)

if __name__ == '__main__':
    unittest.main ()
