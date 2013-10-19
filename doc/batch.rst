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

Supplying too few input arguments results in an error.  Providing too many
results in a warning.  Errors and warnings are printed to standard error.

