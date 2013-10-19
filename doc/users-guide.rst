==============
 User's Guide
==============

Little Village contains an assemble and three different interfaces for using the
LMC emulator.  All of this functionality is through the :command:`lmc` command.

:command:`lmc [assemble|batch|prompt|console|help|version]`

The command::

  lmc help

lists all of the available actions.  Leading dashes are ignored in action names,
so :command:`lmc --help` and :command:`lmc --version` work as expected.  To get
help on a specific action use::

  lmc help <action>

Actions may be abbreviated to a unique prefix.  Since all of the current actions
begin with different letters, that means that typing the first letter of the
action is sufficient.  The actions are described in the following sections

.. toctree::
   :maxdepth: 2

   assemble
   batch
   prompt
   console

