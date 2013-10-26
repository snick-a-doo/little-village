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

import math
import string

class LMC_Client:
    '''A minimal client for an LMC object.

    Derive clients from this class and override the methods as needed.  Call
    __init__() in the derived class' __init__() to create the back end and
    register for notification.

    The methods below are called by the LMC object that was registered with.
    '''
    def __init__ (self, base = 10, memory = 100):
        self.computer = LMC (base, memory)
        self.computer.connect (self)

    def notify_input (self):
        '''Called when the computer is ready for input.

        If an integer (including 0) is returned that number is entered into the
        input register and execution continues.  Returning anything else that
        evaluates to True continues without changing the input register.
        Returning False pauses until LMC.resume() is called.
        '''
        return True

    def notify_output (self, output):
        '''Called when the computer has produced output.

        The value of the computer's output register is passed.
        '''
        pass

    def notify_step (self):
        '''Called before executing each instruction.

        Return True to continue execution, False to pause until LMC.resume() is
        called.
        '''
        return True

    def notify_halt (self):
        '''Called when the program finishes.'''
        pass

class Program_File_Not_Found (Exception):
    '''Exception raised when a program file that does not exist is specified.'''
    def __init__ (self, file):
        self.file = file
    def __str__ (self):
        return ('Program file not found: %s' % self.file)

class Bad_Instruction_Type (Exception):
    '''Exception raised when a non-integer is found in a program.'''
    def __init__ (self, instruction, address):
        self.instruction = instruction
        self.address = address
    def __str__ (self):
        return ('Unexpected input type for instruction: %s %s at address %d.\n'
                'Should be something that can be converted to an integer.'
                % (self.instruction, type (self.instruction), self.address))

class Instruction_Out_Of_Range (Exception):
    '''Exception raised when an instruction does not fit in a word.'''
    def __init__ (self, instruction, address, max_instruction):
        self.instruction = instruction
        self.address = address
        self.max_instruction = max_instruction
    def __str__ (self):
        return ('Instruction out of range: %d at address %d.\n'
                'Instructions must be from 0 to %d'
                % (self.instruction, self.address, self.max_input))

class Input_Out_Of_Range (Exception):
    '''Exception raised when a client gives input that does not fit in a word.'''
    def __init__ (self, input, max_input):
        self.input = input
        self.max_input = max_input
    def __str__ (self):
        return ('Input out of range: %d.\n'
                'Input must be from 0 to %d'
                % (self.input, self.max_input))

class Bad_Input_Type (Exception):
    '''Exception raised when a client gives input that is not Boolean or integer.'''
    def __init__ (self, input):
        self.input = input
    def __str__ (self):
        return ('Unexpected input type for input: %s %s.\n'
                'Should be bool, or something that can be '
                'converted to an integer.'
                % (self.input, type (self.input)))

def digits (n, base):
    '''Return the number of digits needed to provide n different values.'''
    return int (math.ceil (math.log (n, base)))

class LMC:
    '''Implementation of the Little Man Computer.'''

    # TODO: Use same mnemonic info as assemble?
    HLT = 0
    ADD = 1
    SUB = 2
    STA = 3
    LDA = 5
    BRA = 6
    BRZ = 7
    BRP = 8
    IO = 9

    def __init__ (self, base = 10, memory = 100):
        '''Initialize memory and registers.

        Base is the numeric base for data in registers; 2 for binary, 10 for
        decimal, etc.  Memory is the number of memory cells.  Together, these
        arguments determine the word size.
        '''
        self.base = base
        self.memory_size = memory

        # A word needs some number of digits to specify the 10 instruction codes
        # and an additional number address all of the memory.
        self.address_digits = digits (self.memory_size, self.base)
        self.word_digits = digits (10, self.base) + self.address_digits
        # The number of different values a word can have.
        self.word_range = self.base**self.word_digits
        # The maximum value a word can have.
        self.word_max = self.word_range - 1

        self.client = None

        # Make a memory cell for each possible argument.  Initialize to 0.
        self.memory = memory*[0]
        # Initialize all registers to zero.
        self.input = 0
        self.output = 0
        self.counter = 0
        self.accumulator = 0
        self.overflow = False
        self.negative = False
        self.waiting_for_input = False
        self.waiting_for_step = False

    def connect (self, client):
        '''Specify the client to be notified when something happens.

        A client calls this method passing itself as the argument.  Only one
        client may be connected at a time.
        '''
        self.client = client

    def load (self, file):
        '''Load a machine-language program from a file'''
        try:
            f = open (file)
        except IOError:
            raise Program_File_Not_Found (file)

        program = f.readlines ()
        for i in range (len (program)):
            try:
                code = int (program [i])
                if not self._is_in_word_range (code):
                    raise Instruction_Out_Of_Range (code, i, self.word_max)
                self.memory [i] = code
            except ValueError:
                raise Bad_Instruction_Type (code, i);

    def run (self):
        '''Start the program from the beginning.

        We only reset the counter, the other registers retain their values.  It
        is the programmer's responsibility to make sure the code does not depend
        on previous register values if it is to be re-run.
        '''
        self.counter = 0
        self.resume ()

    def resume (self):
        '''Start or restart the program.

        Any initialization must be done beforehand.  This can be used to by a
        client to resume after returning False to a notification method.
        '''
        while self.step (): pass

    def set_input (self, value):
        '''Called by a client to fill the input register.'''
        self.waiting_for_input = False
        if not self._is_in_word_range (value):
            raise Input_Out_Of_Range (response, self.word_max)
        self.input = value;
        self._set_accumulator (self.input)

    def _set_accumulator (self, value):
        '''Load a value into the accumulator.

        Since this value may come from addition or subtraction we must roll over
        and set the appropriate flag if it's out of range.
        '''
        self.overflow = value > self.word_max
        self.negative = value < 0
        self.accumulator = value % self.word_range

    def step (self):
        '''Decode and execute the instruction pointed to by the program counter.

        Return True if the program can continue, False otherwise.  If False is
        returned the program can be restarted from where it left of with
        resume()
        '''
        if not self._can_do_step (): return False

        opcode = self.memory [self.counter]
        self.counter += 1

        op = opcode / self.memory_size
        arg = opcode - self.memory_size * op

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
                    # continue executing.  Note that a bool is also an int so
                    # we check for bool first.
                    if isinstance (response, bool):
                        go_on = response
                        self.waiting_for_input = not go_on
                    else:
                        try:
                            self.set_input (int (response))
                        except ValueError:
                            raise Bad_Input_Type (response)
                else:
                    # If there's no client take what's in the input register.
                    self.set_input (self.input)

            elif arg == 2:
                self.output = self.accumulator
                if self.client:
                    self.client.notify_output (self.output)
        return go_on

    def _can_do_step (self):
        '''Return False to pause execution.'''
        # Always step when resuming after a wait.
        if self.waiting_for_step:
            self.waiting_for_setp = False
            return True
        # Ask the client what to do.
        if self.client: 
            self.waiting_for_step = not self.client.notify_step ()
            return not self.waiting_for_step
        return True

    def _is_in_word_range (self, n):
        '''Internal: Return true if n fits in a word.'''
        return n >= 0 and n < self.word_range

    def _format (self, n, address = False):
        '''Internal: Format the contents of a register for pretty printing.'''
        spec = '%%0*%c' % ('d' if self.base == 10 else 'x')
        digits = self.address_digits if address else self.word_digits
        return spec % (digits, n)

    def __str__ (self):
        '''Return the string representation of the registers and memory.'''
        str =  '\n'
        str += ('      Input: %s    Accumulator: %s\n' 
                % (self._format (self.input), self._format (self.accumulator)))
        str += ('     Output: %s        Counter:  %s\n'
                % (self._format (self.output), self._format (self.counter, True)))

        width = 10 if self.base == 10 else 16
        for i in range (0, self.memory_size):
            if i % width == 0: str += '\n'
            str += ' %s' % self._format (self.memory [i])
        return str
