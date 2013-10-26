==============
 Installation
==============

The source code comes with the usual :file:`setup.py` file.  You can run::

 $ python setup.py install

to install everything.  If you just want to try it out without installing you
can run the software from the top-level source directory.  Just remember that
you may need to put :samp:`./` before the command name.  For example, you'd
use::

 $ ./lmc assemble

instead of::

 $ lmc assemble

Currently documentation is not installed when you run :file:`setup.py`.  If you
have `Sphinx <http://sphinx-doc.org/index.html>`_ installed you can go to the
:file:`doc` directory and execute::

 $ make html

or substitute your favorite flavor for :samp:`html`.  The documentation will be
generated in the :file:`_build/html` directory.  Just point your browser to
:file:`index.html`.  The documentation is incomplete at this time, but the
end-user applications are pretty well covered.
