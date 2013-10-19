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
#  * Unknown mnemonic
#   Wrong number of arguments for instruction
#   Argument out of range
#   Undefined label
#  * Too long
#  * Label matches mnemonic
#  * Too many errors
#   Duplicate label
#
# Warnings:
#  * Unused label
#  * No HLT
#   Data may be executed as code
#   Branch to data
#   Unlabeled data

def count (n, word):
    '''A helper to format a count of things.
We assume the word is made plural by adding "s".'''
    if n != 1: word += 's'
    return ('%d %s' % (n, word))

'''
An exception that stops processing.
'''

class Abort (Exception): pass

'''
A class for collecting and displaying warnings and error messages.
'''

class Message_Queue:
    def __init__ (self, max_errors):
        self.messages = []
        self.n_errors = 0
        self.n_warnings = 0
        self.max_errors = max_errors 

    def add (self, fatal, message, line_number = -1, line = ''):
        severity = ''
        if fatal:
            self.n_errors += 1
            severity = 'Error'
        else:
            self.n_warnings += 1
            severity = 'Warning'
        self.messages.append ((severity, message, line_number, line))
        if self.n_errors == self.max_errors:
            self.add (True, '%d errors.  Quitting.' % self.max_errors)
            raise Abort

    def has_error (self):
        return self.n_errors > 0

    def write (self, stream = sys.stderr):
        for message in self.messages:
            if message[2] < 0:
                stream.write ('%s: %s\n' % message[:2])
            else:
                stream.write ('%s: %s\n  line %-3d: %s\n' % message)

        if self.n_errors > 0 or self.n_warnings > 0:
            stream.write ('\n%s, %s\n' 
                          % (count (self.n_errors, 'error'),
                             count (self.n_warnings, 'warning')))

'''
A program label and associated information.
'''

class Label_Entry:
    def __init__ (self, value, line_number):
        self.value = value
        self.line_number = line_number
        self.references = 0

    def get (self):
        self.references += 1
        return self.value

'''
A lookup table for program labels.
'''

class Lookup:
    def __init__ (self):
        self.table = {}

    def set (self, name, value, line_number):
        self.table [name] = Label_Entry (value, line_number)

    def get (self, name):
        # The empty name has a value of zero.
        if name == '':
            return 0
        if self.table.has_key (name):
            return self.table [name].get ()
        # If it's not empty and not in the dictionary return its integer
        # representation.  Will raise ValueError if it doesn't have one.
        return int (name)

    def unused (self):
        out = []
        for label in self.table:
            entry = self.table [label]
            if entry.references == 0:
                out.append (entry)
        return out

'''
A class that handles converting assembly language code to machine language.
'''

class Assembler:
    # Ignore everything from this string to the end of the line in input files.
    comment = ';'

    # Mnemonic/opcode associations.  For convenience 'DAT' is treated as opcode 0.
    opcodes = { 'DAT':(000, 0, 1), 'HLT':(000, 0, 0), 
                'ADD':(100, 1, 0), 'SUB':(200, 1, 0), 
                'STA':(300, 1, 0), 'LDA':(500, 1, 0), 
                'BRA':(600, 1, 0), 'BRZ':(700, 1, 0), 'BRP':(800, 1, 0),
                'INP':(901, 0, 0), 'OUT':(902, 0, 0) }

    def __init__ (self):
        # Make a lookup table for the labels.
        self.labels = Lookup ()
        self.code = []
        self.has_halt = False
        self.messages = Message_Queue (10)

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
            if tokens == []:
                continue
            (label, mnemonic, arguments) = self.parse (tokens, line_number, line)
            if mnemonic == '':
                continue
            if label != '':
                self.labels.set (label, len (code), line_number)
            # Interpret the instruction.
            code.append (self.translate (mnemonic, arguments, line_number, line))
            # Fail if the program won't fit into the 100 words of memory.  Note
            # that we count code lines and not source lines.
            if len (code) > 100:
                self.messages.add (True, 'Program too long', line_number, line)
                raise Abort
        return code

    def parse (self, tokens, line_number, line):
        n = len (tokens)
        label = ''
        mnemonic = ''
        arguments = []
        if self.opcodes.has_key (tokens[0]):
            mnemonic = tokens[0]
            if n > 1:
                arguments = tokens[1:]
        elif (n > 1) and self.opcodes.has_key (tokens[1]):
            label = tokens[0]
            mnemonic = tokens[1]
            if n > 2:
                arguments = tokens[2:]
        else:
            self.messages.add (True, 'Unknown mnemonic', line_number, line)

        if len (arguments) > 0 and self.opcodes.has_key (arguments[0]):
            self.messages.add (True, 
                               'Label matches a mnemonic',
                               line_number,
                               line)
            mnemonic = ''

        if mnemonic == 'HLT':
            self.has_halt = True

        return (label, mnemonic, arguments)

    def translate (self, mnemonic, argument, line_number, line):
        # Get the machine code for the mnemonic
        (op, n_required, n_optional) = self.opcodes [mnemonic]

        # Use the empty string if there's no argument.
        arg = ''
        n_args = len (argument)
        if n_args != n_required:
            self.messages.add (True, 
                               ('%s requires %s, %d given'
                                % (mnemonic, count (n_required, 'argument'), n_args)),
                               line_number,
                               line)
        elif len (argument) > 0:
            arg = argument[0]
        return (op, arg)

    def assemble (self, program):
        self.has_halt = False
        try:
            # The first pass turns the program into an array of tuples.  The 1st
            # element is the machine instruction for the mnemonic.  The second is a
            # string which may be empty, a label, or the string represtation of a
            # numeric argument.
            code = self.interpret_mnemonics (program)

            # Fill in the address digits of the opcodes with the address that
            # the labels stand for.
            self.code = [ op + self.labels.get (label) for (op, label) in code ]
        except Abort:
            pass
        else:
            for entry in self.labels.unused ():
                line = entry.line_number
                self.messages.add (False, 'Unused label', line, program [line - 1])

            if not self.has_halt:
                self.messages.add (False, 'No HLT instruction in input')

        return not self.messages.has_error ()

    def write_program (self, stream = sys.stdin):
        for line in self.code:
            stream.write ('%03d\n' % line)

def print_help (app):
    print 'Convert a Little Man Computer assembly program to machine code'
    print
    print 'Usage: %s <input-file> [<output-file>]' % app
    print
    print 'where <input-file> is an LMC assembly language file and the machine'
    print 'code is written to <output-file>.  If <output-file> is not given then'
    print 'the output file name is constructed by removing the extension from'
    print '<input-file>.  An error is signaled and nothing is written if'
    print '<output-file> is the same as <input-file>.'
    print

def run (args):
    n_args = len (sys.argv)
    if n_args < 2 or n_args > 3:
        print_help (args [0])
        sys.exit (1)

    output_file = None
    if len (args) > 1:
        output_file = args [1]
    else:
        output_file = os.path.splitext (input_file)[0]
    output_stream = sys.stdout
    if output_file == input_file:
        'Error: output file %s has the same name as the input file.'
        sys.exit (1)
    if output_file != '' and output_file != '-':
        output_stream = open (output_file, 'w')

    # Read the whole program into an array.
    program = open (input_file, 'r').readlines ()
    asm = Assembler ()
    if asm.assemble (program):
        asm.write_program (output_stream)
    else:
        asm.messages.write ()

if __name__ == '__main__':
    run (sys.argv)

