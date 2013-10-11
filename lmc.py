# lmc.py - A Little Man Computer emulator.
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

class LMC_Client:
    def __init__ (self):
        self.computer = LMC ()
        self.computer.register (self)

    def notify_input (self): return True
    def notify_output (self, output): return True
    def notify_step (self): return True
    def notify_halt (self): return True

class Bad_Program (Exception):
    def __init__ (self, file):
        self.file = file

class LMC:
    """Implementation of the Little Man Computer."""
    HLT = 0
    ADD = 1
    SUB = 2
    STA = 3
    LDA = 5
    BRA = 6
    BRZ = 7
    BRP = 8
    IO = 9

    def __init__ (self):
        """Initialize memory and registers."""
        self.client = None
        self.memory = 100*[0]
        self.input = 0
        self.output = 0
        self.counter = 0
        self.accumulator = 0
        self.overflow = False
        self.negative = False
        self.waiting_for_input = False

    def register (self, client):
        """Register the client to be notified when something happens."""
        self.client = client

    def load (self, file):
        """Load a machine-language program from a file"""
        f = open (file)
        program = f.readlines ()
        try:
            for i in range (len (program)):
                self.memory [i] = int (program [i]) % 1000
        except ValueError:
            raise Bad_Program (file);

    def run (self):
        """Start the program from the beginning.

        We only reset the counter, the other registers retain their values.  It
        is the programmer's responsibility to make sure the code does not depend
        on previous register values if it is to be re-run.
        """
        self.counter = 0
        # Give the client a chance to break before the 1st instruction is
        # executed. 
        if not self.client or self.client.notify_step ():
            self.resume ()

    def is_waiting_for_input (self):
        return self.waiting_for_input

    def resume (self):
        """Start or restart the program.

        Any initialization must be done beforehand.  This can be used to by a
        client to resume after returning False to a notification method.
        """
        while self.step () and (not self.client or self.client.notify_step ()):
            pass

    def set_input (self, value):
        """Receive input from a client."""
        self.waiting_for_input = False
        self.input = value % 1000
        self._set_accumulator (self.input)

    def _set_accumulator (self, value):
        """Load a value into the accumulator.

        Since this value may come from addition or subtraction we must roll over
        and set the appropriate flag if it's out of range.
        """
        self.overflow = value > 999
        self.negative = value < 0
        self.accumulator = value % 1000

    def step (self):
        """Decode and execute a single instruction.

        Return True if the program can continue, False otherwise.  If False is
        returned the program can be restarted from where it left of with
        resume()
        """
        opcode = self.memory [self.counter]
        self.counter += 1

        op = opcode / 100
        arg = opcode - 100 * op

        go_on = True;

        if op == LMC.HLT:
            if self.client: self.client.notify_halt ()
            # Don't step the counter past HLT.
            self.counter -= 1
            go_on = False
        if op == LMC.ADD:
            self._set_accumulator (self.accumulator + self.memory [arg])
        elif op == LMC.SUB:
            self._set_accumulator (self.accumulator - self.memory [arg])
        elif op == LMC.STA:
            self.memory [arg] = self.accumulator
        elif op == LMC.LDA:
            self._set_accumulator (self.memory [arg])
        elif op == LMC.BRA:
            self.counter = arg
        elif op == LMC.BRZ:
            if self.accumulator == 0:
                self.counter = arg
        elif op == LMC.BRP:
            if not self.negative:
                self.counter = arg
        elif op == LMC.IO:
            if arg == 1:
                if self.client:
                    response = self.client.notify_input ();
                    # If an integer was returned use it as the input and
                    # continue executing.
                    if type (response) == type (int ()):
                        self.set_input (response)
                    else:
                        go_on = response
                        self.waiting_for_input = not go_on
                else:
                    # If there's no client take what's in the input register.
                    self.set_input (self.input)

            elif arg == 2:
                self.output = self.accumulator
                if self.client:
                    go_on = self.client.notify_output (self.output)

        return go_on


    def __str__ (self):
        str =  '\n'
        str += '      Input: %03d    Accumulator: %03d\n' % (self.input, self.accumulator)
        str += '     Output: %03d        Counter:  %02d\n' % (self.output, self.counter)
        str += '\n'
        width = 10
        for i in range (0, len (self.memory), width):
            for j in range (width):
                str += ' %03d' % self.memory [i+j]
            str += '\n'
        return str
