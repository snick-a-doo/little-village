#!/usr/bin/python

# assemble.py - An assembler for the Little Man Computer
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

import string
import sys

# Errors:
#   Unknown mnemonic
#   Wrong number of arguments for opcode
#   Argument out of range
#   Undefined label
#
# Warnings:
#   Unused label
#   No HLT

class Assembler:
    # Ignore everything from this string to the end of the line in input files.
    comment = ';'

    # Mnemonic/opcode associations.  For convenience 'DAT' is treated as opcode 0.
    opcodes = { 'HLT':000, 'ADD':100, 'SUB':200, 'STA':300, 'LAD':500, 
                'BRA':600, 'BRZ':700, 'BRP':800, 'INP':901, 'OUT':902,
                'DAT':000 }

    def __init__ (self):
        # The numeric values of labels are defined in a dictionary.  An empty
        # label is zero.
        self.data = { '':0 }
        self.errors = []
        self.code = []

    def interpret_mnemonics (self, program):
        code = []
        line_number = 0
        for line in program:
            line_number += 1
            # Remove comments.
            line = string.split (line, self.comment)[0]
            # Split the line into tokens.
            tokens = string.split (line)
            # Ignore empty lines.
            n = len (tokens)
            if n > 0:
                if n > 1 and not self.opcodes.has_key (tokens[0]):
                    # If the 1st token is not a mnemonic assume it's a label.  Its
                    # value is the memory location of the instruction, which is the
                    # same as the number of instructions processed so far.
                    self.data [tokens[0]] = len (code)
                    # Remove the label from the token list.
                    tokens = tokens[1:]
                    # Interpret the instruction (possibly after label removal).
                try:
                    code.append (self.translate (tokens))
                except KeyError:
                    self.errors.append (('Error', 'Unknown mnemonic', line_number, line))
        return code

    def translate (self, instruction):
        # Get the machine code for the mnemonic
        op = self.opcodes [instruction[0]]

        # Use the empty string if there's no argument.
        arg = ''
        if len (instruction) > 1:
            arg = instruction[1]
        return (op, arg)

    def resolve_labels (self, code):
        out = []
        for line in code:
            # Don't process messages
            if type (line[0]) == type (''):
                out.append (line)
            else:
                arg = 0
                try:
                    # Try to find the value for the (possibly empty) argument label...
                    arg = self.data [line[1]]
                except KeyError:
                    # ...if that fails try to treat the argument as a number.
                    arg = int (line[1])
                    # Add the numeric argument to the machine code.
                out.append (line[0] + arg)
        return out

    def assemble (self, program):
        # The first pass turns the program into an array of tuples.  The 1st
        # element is the machine instruction for the mnemonic.  The second is a
        # string which may be empty, a label, or the string represtation of a
        # numeric argument.
        code = self.interpret_mnemonics (program)

        # The second pass replaces labels with their addresses and generates the
        # machine code.
        self.code = self.resolve_labels (code)

        return len (self.errors) == 0

    def print_program (self):
        for line in self.code:
            print '%03d' % line

    def show_errors (self):
        for error in self.errors:
            sys.stderr.write ('%s: %s\nline %-3d: %s\n' % error)

if __name__ == '__main__':
    if len (sys.argv) != 2:
        print 'Usage: assemble.py program'
        sys.exit (1)

    # Read the whole program into an array.
    program = open (sys.argv [1], 'r').readlines ()
    asm = Assembler ()
    if asm.assemble (program):
        asm.print_program ()
    else:
        asm.show_errors ()


