#!/usr/bin/python
#
# An assembler for the Little Man Computer
#
import string
import sys

# Ignore everything from this string to the end of the line in input files.
comment = ';'

# Mnemonic/opcode associations.  For convenience 'DAT' is treated as opcode 0.
opcodes = { 'HLT':000, 'ADD':100, 'SUB':200, 'STA':300, 'LDA':500, 
            'BRA':600, 'BRZ':700, 'BRP':800, 'INP':901, 'OUT':902,
            'DAT':000 }

def interpret_mnemonics (program, data):
    code = []
    for line in program:
        # Remove comments.
        line = string.split (line, comment)[0]
        # Split the line into tokens.
        tokens = string.split (line)
        # Ignore empty lines.
        if len (tokens) > 0:
            if not opcodes.has_key (tokens[0]):
                # If the 1st token is not a mnemonic assume it's a label.  Its
                # value is the memory location of the instruction, which is the
                # same as the number of instructions processed so far.
                data [tokens[0]] = len (code)
                # Remove the label from the token list.
                tokens = tokens[1:]
            # Interpret the instruction (possibly after label removal).
            code.append (translate (tokens))
    return code

def translate (instruction):
    # Get the machine code for the mnemonic
    op = opcodes [instruction[0]]
    # Use the empty string if there's no argument.
    arg = ''
    if len (instruction) > 1:
        arg = instruction[1]
    return (op, arg)

def resolve_labels (code, data):
    out = []
    for line in code:
        arg = 0
        try:
            # Try to find the value for the (possibly empty) argument label...
            arg = data [line[1]]
        except KeyError:
            # ...if that fails try to treat the argument as a number.
            arg = int (line[1])
        # Add the numeric argument to the machine code.
        out.append (line[0] + arg)
    return out

def assemble (file):
    # Read the whole program into an array.
    program = open (file, 'r').readlines ()

    # The numeric values of labels are defined in a dictionary.  An empty lable is zero.
    data = { '':0 }

    # The first pass turns the program into an array of tuples.  The 1st
    # element is the machine instruction for the mnemonic.  The second is a
    # string which may be empty, a label, or the string represtation of a
    # numeric argument.
    code = interpret_mnemonics (program, data)

    # The second pass replaces labels with their addresses and generates the machine code.
    return resolve_labels (code, data)

if __name__ == '__main__':
    for line in assemble (sys.argv [1]):
        print '%03d' % line
