#!/usr/bin/python
#
# A non-interactive LMC
#
import lmc
import sys

class Batch_Client (lmc.LMC_Client):
    def __init__ (self, program, inputs):
        lmc.LMC_Client.__init__ (self)
        self.inputs = inputs
        self.computer.load (program)
        self.computer.run ()

    def notify_input (self):
        n = self.inputs [0]
        self.inputs = self.inputs [1:]
        return int (n)

    def notify_output (self, out):
        print out
        return True

if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'Usage: batch program-name [input...]'
    else:
        program = sys.argv [1]
        inputs = sys.argv [2:]
        client = Batch_Client (program, inputs)
