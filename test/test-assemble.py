# test-assemble.py - Unit tests for the LMC assembler

import os
import sys
# Allow importing modules from the source directory
sys.path = [os.path.abspath ('../little_village')] + sys.path

import assemble
import unittest
import string
import StringIO

'''
Process an empty file
'''

class Test_Assemble (unittest.TestCase):
    def setUp (self):
        self.asm = assemble.Assembler ()

    def messages (self):
        messages = StringIO.StringIO ()
        self.asm.messages.write (messages)
        return messages.getvalue ()

    def test_empty (self):
        self.assertTrue (self.asm.assemble ([]))
        self.assertEqual (self.asm.code, [])

    def test_mnemonics (self):
        program = [ 'ADD 50', 'SUB 51', 'STA 52', 'LDA 53',
                    'BRA 01', 'BRZ 02', 'BRP 03',
                    'INP', 'OUT', 'HLT', 'DAT' ]
        self.assertTrue (self.asm.assemble (program))
        self.assertEqual (self.asm.code,
                          [ 150, 251, 352, 553, 601, 702, 803, 
                            901, 902, 000, 000 ])

    def test_unknown_mnemonic (self):
        # LDA is misspelled LDA
        program = [ 'ADD 50', 'SUB 51', 'STA 52', 'LAD 53', 'HLT' ]
        self.assertFalse (self.asm.assemble (program))
        self.assertEqual (self.messages (),
                          'Error: Unknown mnemonic\n'
                          '  line 4  : LAD 53\n'
                          '\n'
                          '1 error, 0 warnings\n')

    def test_unused_label (self):
        program = [ 'ADD 50', 'nothing DAT', 'HLT' ]
        self.assertTrue (self.asm.assemble (program))
        self.assertEqual (self.asm.code, [ 150, 000, 000 ])
        self.assertEqual (self.messages (),
                          'Warning: Unused label\n'
                          '  line 2  : nothing DAT\n'
                          '\n'
                          '0 errors, 1 warning\n')

    def test_too_long (self):
        # Avoid the no-halt warning.
        program = [ 'HLT' ] + [ 'ADD 50' ] * 111
        self.assertFalse (self.asm.assemble (program))
        self.assertEqual (self.messages (),
                          'Error: Program too long\n'
                          '  line 101: ADD 50\n'
                          '\n'
                          '1 error, 0 warnings\n')

    def test_label_is_mnemonic (self):
        # 'STA SUB' will be read as op=STA arg=SUB
        program = [ ';comment', '', 'ADD 50', 'STA SUB', 'HLT' ]
        self.assertFalse (self.asm.assemble (program))
        # The line number is source file lines.  Comments and blanks are
        # included in the count.
        self.assertEqual (self.messages (),
                          'Error: Label matches a mnemonic\n'
                          '  line 4  : STA SUB\n'
                          '\n'
                          '1 error, 0 warnings\n')

    def test_no_halt (self):
        program = [ 'ADD 50', 'SUB 51' ]
        self.assertTrue (self.asm.assemble (program))
        self.assertEqual (self.asm.code, [ 150, 251 ])
        self.assertEqual (self.messages (),
                          'Warning: No HLT instruction in input\n'
                          '\n'
                          '0 errors, 1 warning\n')

    def test_too_many_errors (self):
        self.asm.messages.max_errors = 4
        program = [ 'MOO', 'WEE', 'ZIP', 'TOP', 'BAG' ]
        self.assertFalse (self.asm.assemble (program))
        messages = string.split (self.messages (), '\n')
        self.assertEqual (messages[0], 'Error: Unknown mnemonic')
        self.assertEqual (messages[1], '  line 1  : MOO')
        self.assertEqual (messages[2], 'Error: Unknown mnemonic')
        self.assertEqual (messages[3], '  line 2  : WEE')
        self.assertEqual (messages[4], 'Error: Unknown mnemonic')
        self.assertEqual (messages[5], '  line 3  : ZIP')
        self.assertEqual (messages[6], 'Error: Unknown mnemonic')
        self.assertEqual (messages[7], '  line 4  : TOP')
        self.assertEqual (messages[8], 'Error: 4 errors.  Quitting.')
        self.assertEqual (messages[9], '')
        self.assertEqual (messages[10], '5 errors, 0 warnings')

    def test_not_enough_arguments (self):
        program = [ 'ADD', 'SUB', 'STA', 'LDA', 'BRA', 'BRZ', 'BRP', 'HLT', 'DAT' ]
        self.assertFalse (self.asm.assemble (program))
        messages = string.split (self.messages (), '\n')
        self.assertEqual (messages[0], 'Error: ADD requires 1 argument, 0 given')
        self.assertEqual (messages[1], '  line 1  : ADD')
        self.assertEqual (messages[2], 'Error: SUB requires 1 argument, 0 given')
        self.assertEqual (messages[3], '  line 2  : SUB')
        self.assertEqual (messages[4], 'Error: STA requires 1 argument, 0 given')
        self.assertEqual (messages[5], '  line 3  : STA')
        self.assertEqual (messages[6], 'Error: LDA requires 1 argument, 0 given')
        self.assertEqual (messages[7], '  line 4  : LDA')
        self.assertEqual (messages[8], 'Error: BRA requires 1 argument, 0 given')
        self.assertEqual (messages[9], '  line 5  : BRA')
        self.assertEqual (messages[10], 'Error: BRZ requires 1 argument, 0 given')
        self.assertEqual (messages[11], '  line 6  : BRZ')
        self.assertEqual (messages[12], 'Error: BRP requires 1 argument, 0 given')
        self.assertEqual (messages[13], '  line 7  : BRP')
        self.assertEqual (messages[14], '')
        self.assertEqual (messages[15], '7 errors, 0 warnings')

if __name__ == '__main__':
    unittest.main ()
