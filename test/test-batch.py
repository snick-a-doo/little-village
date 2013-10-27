# test-batch.py - Unit tests for the LMC batch client
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
import sys
# Allow importing modules from the source directory
sys.path.insert (0, os.path.abspath('../little_village'))

import re
import string
import StringIO
import unittest

import batch
import lmc

class Test_Batch (unittest.TestCase):
    def setUp (self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = StringIO.StringIO ()
        sys.stderr = StringIO.StringIO ()

    def tearDown (self):
        sys.stdout.close ()
        sys.stderr.close ()
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def test_add (self):
        batch.run ('test-batch', ['../programs/add', 123, 45])
        self.assertEqual (sys.stdout.getvalue (), '168\n')
        self.assertEqual (sys.stderr.getvalue (), '')

    def test_no_arguments (self):
        batch.run ('test-batch', [])
        # Make sure we get a usage message that shows the passed-in app name.
        # Don't worry abut the rest of the text.
        target = 'Usage: test-batch'
        match = re.search (target, sys.stdout.getvalue ())
        self.assertEqual (match.group (0), target)
        self.assertEqual (sys.stderr.getvalue (), '')

    def test_bad_file (self):
        batch.run ('test-batch', ['moo', 123, 45])
        self.assertEqual (sys.stdout.getvalue (), '')
        self.assertEqual (sys.stderr.getvalue (),
                          "Error: Program file not found: 'moo'\n")

    def test_bad_input (self):
        batch.run ('test-batch', ['../programs/add', 123, 'waffles', -12, 33])
        self.assertEqual (sys.stdout.getvalue (), '')
        self.assertEqual (sys.stderr.getvalue (),
                          "Error: Unexpected input type for input: "
                          "waffles <type 'str'>.\n"
                          "Should be bool, or something that can be "
                          "converted to an integer.\n")

    def test_input_out_of_range (self):
        batch.run ('test-batch', ['../programs/add', 123, 4567])
        self.assertEqual (sys.stdout.getvalue (), '')
        self.assertEqual (sys.stderr.getvalue (), 
                          'Error: Input out of range: 4567.\n'
                          'Input must be from 0 to 999.\n')

    def test_non_enough_inputs (self):
        batch.run ('test-batch', ['../programs/add', 123])
        self.assertEqual (sys.stdout.getvalue (), '')
        self.assertEqual (sys.stderr.getvalue (), 'Error: Not enough inputs.\n')

    def test_extra_input (self):
        batch.run ('test-batch', ['../programs/add', 123, 45, 'waffles', -12, 33])
        self.assertEqual (sys.stdout.getvalue (), '168\n')
        self.assertEqual (sys.stderr.getvalue (),
                          "Warning: Unused inputs: 'waffles' -12 33 \n")

if __name__ == '__main__':
    unittest.main ()
