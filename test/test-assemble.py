# test-assemble.py - Unit tests for the LMC assembler

import os
import sys
# Allow importing modules from the parent directory
sys.path.append (os.path.abspath ('..'))

import assemble
import unittest
import StringIO

'''
Process an empty file
'''

class Test_Assemble (unittest.TestCase):
    def setUp (self):
        self.asm = assemble.Assembler ()

    def messages (self):
        messages = StringIO.StringIO ()
        self.asm.write_messages (messages)
        return messages.getvalue ()

    def test_empty (self):
        self.assertTrue (self.asm.assemble ([]))
        self.assertEqual (self.asm.code, [])

    def test_mnemonics (self):
        program = [ 'ADD', 'SUB', 'STA', 'LDA', 'BRA', 'BRZ', 'BRP',
                    'INP', 'OUT', 'HLT', 'DAT' ]
        self.assertTrue (self.asm.assemble (program))
        self.assertEqual (self.asm.code,
                          [ 100, 200, 300, 500, 600, 700, 800, 
                            901, 902, 000, 000 ])
    def test_unknown_mnemonic (self):
        # LDA is misspelled LDA
        program = [ 'ADD', 'SUB', 'STA', 'LAD', 'BRA', 'BRZ', 'BRP',
                    'INP', 'OUT', 'HLT', 'DAT' ]
        self.assertFalse (self.asm.assemble (program))
        self.assertEqual (self.messages (),
                          'Error: Unknown mnemonic\nline 4  : LAD\n1 error, 0 warnings\n')

if __name__ == '__main__':
    unittest.main ()
