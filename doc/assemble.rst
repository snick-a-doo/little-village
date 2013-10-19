.. _assemble:

==========
 Assemble
==========

:command:`lmc assemble <input-file> [<output-file>]`

The :command:`batch` action converts an LMC assembly-language program to machine
code.  If the output file is not specified the output file name is formed by
removing the extension from the input file name.  The command::

  lmc assemble add.asm

produces the output file :file:`add`.  If :file:`add` already exists it is
overwritten.  If the output file name is the same as the input file name an
error is reported.  An output file of :samp:`-` causes the machine code to be
printed to standard output.

An assembly-language file has three columns.  The first is for optional labels.
A label is a name that stands for the line of code where it appears.  A label
can be used as an argument for other instructions in the code.  The second
column is for mnemonics that stand for the LMC's instructions.  All of the
mnemonics consist of three upper-case letters.  The third column is for
arguments for those instructions that require arguments.  Blank lines are
ignored.  Comments start with :samp:`;`.  Everything from the first semicolon on
the line to the end of the line is ignored.

The assembler goes through the input file line-by-line.  After stripping
comments it breaks the line into whitespace-separated text strings called
*tokens*.  The assembler doesn't actually care how the text lines up in columns.
If the first token is not one of the LMC's mnemonics it is assumed to be a
label.  If the first token is a mnemonic then the line is assumed not to contain
a label.

There are a few restrictions on what characters make up a label.  It must not
contain a newline or semicolon.  It must not match any mnemonic.  It must
contain at least one character that's not a digit.  These restrictions exist
because of the way the assembler is implemented.  But even if they were not
requirements, breaking these rules would likely lead to confusion. 

The machine code file is a text file with each three-digit instruction on a
separate line.  This is the LMC emulator's executable file format.  A real
computer would use a binary representation but we want the output to be easy for
humans to examine.  The machine code file can be executed with the :command:`batch`,
:command:`prompt`, or :command:`console` actions.  See sections :ref:`batch`,
:ref:`prompt`, and :ref:`console`.

Errors and Warnings
===================

If the assembler can't produce executable machine code from the input file an
error message is displayed and no output file is written.  If machine code can
be produced but something about it looks suspicious, a warning is displayed and
the output file is written.  An error message starts with :samp:`Error:` and a
warning starts with :samp:`Warning:`.  Where possible the line number and the
line of code that caused the trouble is displayed after the message.

Messages that start with a '*' have not been implemented yet.

Error Messages
--------------

.. glossary::
   \*Argument out of range
     An argument greater than 99 was specified.  This is not allowed because an
     argument must give one of the LMC's 100 memory locations.  An argument to
     :samp:`DAT` does not necessarily refer to a memory location; it is limited
     to 999 by the LMC's three-digit word size.

   \*Duplicate label
     A string is defined as a label on two different lines of the input file.
     It can't unambiguously be converted to a memory location when used as an
     argument. 

   Label matches a mnemonic
     Two strings on the line match mnemonics for LMC instructions.  This is not
     allowed because we can't tell if they are intended to be a label followed
     by a mnemonic or a mnemonic followed by an argument.

   Program too long
     The program contains more than 100 instructions and can't fit into the
     LMC's memory.

   Too many errors
     Processing of the input file continues even after an error is discovered so
     that if there are multiple errors you can fix them all at once.  But after
     ten errors we give up on the assumption that the input file is not really
     not an LMC assembly language file.

   \*Undefined label
     A string that was not defined as a label (i.e. it does not appear anywhere
     in the first column of the input) was used as the argument for an
     instruction.  Labels used as arguments must be defined so they can be
     converted to memory locations to produce the machine code.

   Unknown mnemonic
     A string that does not match a mnemonic for an LMC instruction was found
     where an mnemonic is expected.  One of the first two strings in a line of
     assembly code must contain a mnemonic.

   \*Wrong number of arguments for instruction
     We require an argument for LMC mnemonics that take one.  We do not allow an
     argument to be specified for mnemonics that don't need one.  The argument
     for a :samp:`DAT` instruction defaults no zero and need not be specified.

Warning Messages
----------------

.. glossary::
   \*Data may be executed as code
     Data statements appear before the :samp:`HLT` instruction.

   \*Branch to data
     The argument of a branching instruction names a memory location filled by a
     :samp:`DAT` instruction.

   No HLT
     The program does not include a :samp:`HLT` instruction.  Program execution
     may run into memory locations that hold data.

   \*Unlabeled data
     A :samp:`DAT` instruction appears without a label.  This means that the
     data can't be referred to by name.

   Unused label
     A string was defined as a label but not used as an argument to any
     instruction. 
