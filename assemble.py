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

import os
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
    opcodes = { 'HLT':000, 'ADD':100, 'SUB':200, 'STA':300, 'LDA':500, 
                'BRA':600, 'BRZ':700, 'BRP':800, 'INP':901, 'OUT':902,
                'DAT':000 }

    def __init__ (self):
        # The numeric values of labels are defined in a dictionary.  An empty
        # label is zero.
        self.data = { '':0 }
        self.code = []
        self.messages = []
        self.n_errors = 0
        self.n_warnings = 0

    def add_message (self, fatal, message, line_number, line):
        severity = ''
        if fatal:
            self.n_errors += 1
            severity = 'Error'
        else:
            self.n_warnings += 1
            severity = 'Warning'
        self.messages.append ((severity, message, line_number, line))

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
                    self.add_message (True, 'Unknown mnemonic', line_number, line)
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

        return self.n_errors == 0

    def write_program (self, stream = sys.stdin):
        for line in self.code:
            stream.write ('%03d\n' % line)

    def write_messages (self, stream = sys.stderr):
        for message in self.messages:
            stream.write ('%s: %s\n  line %-3d: %s\n' % message)

        if self.n_errors > 0 or self.n_warnings > 0:
            stream.write ('\n%s, %s\n' 
                          % (count (self.n_errors, 'error'),
                             count (self.n_warnings, 'warning')))

def count (n, word):
    '''A helper to format a count of things.
We assume the word is made plural by adding "s".'''
    if n != 1: word += 's'
    return ('%d %s' % (n, word))


if __name__ == '__main__':
    n_args = len (sys.argv)
    if n_args < 2 or n_args > 3:
        print 'Usage: assemble.py program [output_file]'
        sys.exit (1)

    # Read the whole program into an array.
    input_file = sys.argv [1]
    program = open (input_file, 'r').readlines ()

    output_stream = sys.stdout
    output_file = os.path.splitext (input_file)[0]
    if n_args > 2:
        output_file = sys.argv [2]
    if output_file != '' and output_file != '-':
        output_stream = open (output_file, 'w')

    asm = Assembler ()
    if asm.assemble (program):
        asm.write_program (output_stream)
    else:
        asm.write_messages ()
