#
# Unit tests for the LMC back-end and clients.
#
import os
import sys
# Allow importing modules from the parent directory
sys.path.append (os.path.abspath ('..'))

import lmc
import batch
import unittest

'''
Check the initial state of the computer.
'''

class Test_Initial (unittest.TestCase):
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

'''
Test the computer with a small program.

The program, "add", takes two values from input.  The input register is loaded
before the program starts and will not change.  So we expect the output to be 2
times the input.
'''

class Test_Run (unittest.TestCase):
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

'''
Test the batch client
'''

class Test_Batch (unittest.TestCase):
    def setUp (self):
        self.inputs = [1, 12, 25, 0]
        self.client = batch.Batch_Client ('square', self.inputs)

    def test_run (self):
        self.client.run ()
        for (x, y) in zip (self.inputs, self.client.outputs):
            self.assertEqual (x**2, y)

'''
A client that breaks execution at a specific line.
'''

class Break_Client (batch.Batch_Client):
    def __init__ (self, program, inputs, line):
        batch.Batch_Client.__init__ (self, program, inputs)
        self.break_line = line

    def notify_step (self):
        # Return False to stop execution when the counter gets to break_line.
        return self.computer.counter != self.break_line

'''
Test breaking, stepping, and resuming.
'''

class Test_Break (unittest.TestCase):
    def setUp (self):
        self.inputs = [888, 99]
        self.line = 2 # Break before this (0-based) instruction.
        self.client = Break_Client ('add', self.inputs, self.line)

    def test_break_and_resume (self):
        self.client.run ()
        self.assertEqual (self.line, self.client.computer.counter)
        self.assertEqual (self.client.outputs, [])
        self.client.computer.resume ()
        self.assertEqual (self.client.outputs, [987])

    def test_break_and_step (self):
        self.client.run ()
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
        self.client.run ()
        self.client.computer.resume ()
        self.assertEqual (self.client.computer.counter, 5)
        self.client.computer.step ()
        # Can't step past HLT.
        self.assertEqual (self.client.computer.counter, 5)
        self.client.computer.step ()
        self.assertEqual (self.client.computer.counter, 5)

if __name__ == '__main__':
    unittest.main ()
