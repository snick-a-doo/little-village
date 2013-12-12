=======================================
 A Short Course in Machine Programming
=======================================

This is an introduction to programming in machine language and assembly language
using the Little Man Computer.

A computer program is a list of instructions, like a to-do list.  It doesn't
actually get anything done.  In the case of a Python program, the instructions
are for the program "python".  Many other programs that are installed on your
computer may be involved when you run your Python program to help it do things
like advanced math or graphics.  Then there's the terminal where you run the
program, the user interface, and the operating system which is in charge of all
programs.  These things are all just lists of instructions.

When you run your program, something happens.  Something in the real world
changes.

  This is worth thinking about for a while.  You don't even have to be convinced
  that this is true.

Since the change happens in the real world it
must happen in a piece of *hardware* not *software*.  The hardware is called the
*central processing unit*, or *CPU*, or *processor*.

A processor could be made of levers and gears, or balls and tracks, or tubing
and valves.  In fact mechanical computers have been made.

  Research: Charles Babbage and his "Difference Engine" and "Analytical Engine"

Mechanical "adding machines" were used by businesses in the years before
electronic calculators.  Modern processors use electricity for doing their
computations.

  Why is electricity a good choice?  Can you think of any other good choices?

Since a processor is a piece of hardware it's difficult to change its behavior.
Software is easy to change; you just open the file in your editor and type.  To
change your processor you'd have to crack open the plastic case and rearrange
microscopic wires etched into silicon.

  Research: Integrated circuit

This is impractical at best.  A
processor has a set of things it can do called its *instruction set*.  These are
usually very simple things like "store a number in memory", or "add two
numbers".  And by "number" I mean voltages on a set of wires that represent ones
and zeroes.

Processors made by different manufacturers, and different models of processors
made by the same company may have different instruction sets.  Part of the
reason for the layers of software described at the beginning of this section is
to deal with these differences so the same programs can run on computers with
different processors.

Modern processors have large instruction sets and operate on huge numbers.  So
we're going to use a made-up processor that's designed to be understood by
humans.  Although it's simple, it works in the same way as real processors, and
can do any calculation that any other computer can.

  Research: Universal computer

Your Office
===========

The Little Man Computer (LMC) can be thought of as a sort of office where a
person works.  It's a silly, but useful analogy that we can use until we're used
to vocabulary of computer processors.  Here's the story.

You work in an office.  You have an inbox and an outbox.  These are your only
means of communication with the world outside your office.  These boxes can only
hold one 3-digit number.  You're pretty isolated.

You have 100 more boxes that you can use for storing something you need to
remember later.  They each hold one 3-digit number.  This is your *memory*.
Your boss uses some of these boxes to put the tasks you need to perform.  Don't
get them mixed up!

You have a calculator that can add and subtract, you guessed it, 3-digit
numbers.

Finally, you have a counter that tells you which of your boss's instructions
you're supposed to work on next.

  Make a picture of the office that shows (at least) the items mentioned above.

Your boss came up with a code so all of your instructions can be written as
3-digit numbers.  For example, :samp:`123` means "add what's in box 23 to
whatever is in the calculator, :samp:`321` means "put what's in the calculator
into box 21.  For most instructions the last two digits give a box number, or
*address*.

  Question: What's the largest box number?  What's the smallest.

Here's an incomplete listing of your *instruction set*.

=========== ===========
Code        Instruction
----------- -----------
1xx         Add a number in memory 
2xx         Subtract a number in memory
3xx         Store in memory
5xx         Load from memory
901         Load from inbox
902         Store in outbox
=========== ===========

Actual codes have a memory address in place of 'xx'.  There are four more
instructions we'll talk about later.

Your Job
========

When you get to your office in the morning your boss has already loaded your
instructions into the memory boxes.  The first instruction is in box 00.
Remember the counter that tells you what instruction you're working on?  That's
always at 00 when you come in.

Here's your daily routine:
# Read the number from the counter.
# Get the instruction from the box that has that number.
# Increase the counter by 1.
# Decode and execute the instruction.
# Go back to #1.

There's an important instruction we need to mention: the *halt* instruction.
When you get to that instruction you're done.  No need to go back to step #1.
It has the memorable code 000.

Let's say that your boss wants you to add two numbers that she puts in your
inbox.  The sequence of instructions might be
# Load from inbox
# Store in memory box 06
# Load from inbox
# Add the number in memory box 06
# Store in outbox
# Halt

This means that when you get to work your first six memory boxes are filled with
these numbers:

=== ======
Box Number
--- ------
00  901
01  306
02  901
03  106
04  902
05  000
=== ======

Let's go through this program step by step.  First you read the instruction from
box 00.  It tells you to copy what's in the inbox into the calculator.  (The
number is still in the inbox, but whatever was in the calculator is gone.)  Then
you copy it from the calculator to memory box 06.  Why can't you just copy from
the inbox to memory?  Your boss doesn't have a code for that.  It's not in your
instruction set, so it has to be done using two codes that *are* in your
instruction set.

Note that boxes 00 through 05 are filled with instructions.  So box 06 is a fine
place to put something that will be needed later.  If the instruction were 302
you would be storing the input where your next instruction is.  What happens
next would depend on the number in your inbox.  To avoid this problem it's
usually best to keep the data separate from the program.

Next you execute the instruction in box 02 which is the same as the first
instruction: copy the number in the inbox to the calculator.  But whoever is
running the program will have entered the second number of the addition problem
by then.

Now we add the first number (stored in box 06) to the second number (currently
in the calculator).  Then you copy the result to the outbox and you're done.

-- introduce real names

Those six numbers in memory are all that's needed to get you to add any two
numbers.  They make up a *machine language program*.

Assembly Language
=================

When we run the computer with :samp:`901 306 901 106 90 200` in its first six
memory locations it knows exactly what to do.  But it's hard for people to
understand.  This makes it hard to write and change machine language programs.

Assembly language has three features that make programming a little easier.
# Names are used in place of the operation codes.
# Memory locations can be labeled.
# Comments can be written to help explain the code.

Here's an assembly language version of our addition program::

 ;;; 
 ;;; Add two numbers
 ;;; 
         INP         ; Get the first number
         STA first   ; Store it
         INP         ; Get the second number
         ADD first   ; Add the first to it
         OUT         ; Give the result
         HLT
 first   DAT         ; Storage for the first number

Everything after a :samp:`;` on a line is a *comment*.  Comments are messages to
anyone who might need to understand the program.  Often they are messages to
yourself.  

