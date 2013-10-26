.. _batch:

=======
 Batch
=======

:command:`lmc batch <program> [<input>...]`

The :command:`batch` action runs an assembled program and prints any output to
standard output.  If the program requires input it must be supplied as arguments
to the command.  For example, a program :file:`add` that takes two numbers as
input and outputs their sum would be run as::

  $ lmc batch add 77 16
  93

Errors and Warnings
===================

Any errors or warnings are written to standard error.  If an error is signaled
output is incomplete or not produced at all.  Error messages are preceded by
'Error:', warnings are preceded by 'Warning:'.  Any other problems that occur
during execution are reported as 'Internal:'.  Internal errors are unexpected
and may indicate a bug.  If you see any internal errors please file a bug
report.

Error Messages
--------------

.. glossary::
   Program file not found: :samp:`program`
     The specified program file does not exist.

   Unexpected input type for input: :samp:`input` <type, :samp:`t`>
     Non-integer input was provided.  The input and its type are shown. 

   Not enough inputs.
     The program requires more input than was given.

Warning Messages
----------------

.. glossary::
   Unused inputs: :samp:`input`...
     The input arguments listed were not used by the program.

