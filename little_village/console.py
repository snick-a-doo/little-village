#!/usr/bin/python

# console.py - A graphical front end for the Little Man Computer emulator.
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
import string
import sys

from gi.repository import Gtk
from gi.repository import Gdk

import lmc

class Register (Gtk.Entry):
    """A numeric entry field for LMC registers.

\param chars The maximum number of characters for the field
\param icon If true display an icon that's shown or hidden with set_ready()"""
    def __init__ (self, chars = 3, icon = False):
        Gtk.Entry.__init__ (self, xalign = 1.0)
        self.chars = chars
        self.set_max_length (chars)
        self.has_icon = icon
        self.set_width_chars (chars + (3 if self.has_icon else 0))

    def set (self, value):
        self.set_text ('%0*d' % (self.chars, value))

    def set_ready (self, ready):
        if self.has_icon:
            self.set_icon_from_stock (Gtk.EntryIconPosition.PRIMARY,
                                      Gtk.STOCK_YES if ready else None)

class Memory (Gtk.Grid):
    def __init__ (self, width, height):
        Gtk.Grid.__init__ (self)
        self.last_step = None
        self.cells = []
        for j in range (width):
            self.attach (Gtk.Label ('%d ' % j), j+1, 0, 1, 1)
        for i in range (height):
            self.attach (Gtk.Label ('%02d ' % (i*width)), 0, i+1, 1, 1)
            for j in range (width):
                cell = Register ()
                self.attach (cell, j+1, i+1, 1, 1)
                self.cells.append (cell)

    def fill (self, data):
        for i in range (len (data)):
            self.cells [i].set_text ('%03d' % data [i])

    def set_step (self, step):
        if self.last_step != None:
            self.cells [self.last_step].set_progress_fraction (0.0)
        self.cells [step].set_progress_fraction (1.0)
        self.last_step = step

class App (lmc.LMC_Client, Gtk.Window):
    def __init__ (self):
        lmc.LMC_Client.__init__ (self)
        Gtk.Window.__init__ (self, title='LMC')

        app_box = Gtk.Box (spacing = 20)
        self.add (app_box)

        space_box = Gtk.Box (orientation = Gtk.Orientation.VERTICAL, spacing = 6)
        control_box = Gtk.Box (orientation = Gtk.Orientation.VERTICAL, spacing = 6)
        input_box = Gtk.Box (orientation = Gtk.Orientation.VERTICAL, spacing = 6)
        output_box = Gtk.Box (orientation = Gtk.Orientation.VERTICAL, spacing = 6)
        display_box = Gtk.Box (orientation = Gtk.Orientation.HORIZONTAL, spacing = 20)

        control_box.pack_start (Gtk.Label (''), False, False, 0)

        self.program_name = Gtk.Label ('')
        control_box.pack_start (self.program_name, False, False, 0)

        self.load = Gtk.Button (label='Load')
        self.load.connect ('clicked', self.on_load)
        control_box.pack_start (self.load, False, False, 0)

        self.run = Gtk.Button (label='Run')
        self.run.connect ('clicked', self.on_run)
        self.run.set_sensitive (False)
        control_box.pack_start (self.run, False, False, 0)

        input_label = Gtk.Label ('Input')
        input_box.pack_start (input_label, False, False, 0)

        self.input_stack = Gtk.TextView ()
        self.input_stack.set_justification (Gtk.Justification.RIGHT)
        self.input_stack.set_wrap_mode (Gtk.WrapMode.CHAR)
        self.input_stack.set_editable (False)

        # Make room for the "ready" icon.
        self.input_entry = Register (icon = True)
        self.input_entry.connect ('key-press-event', self.on_input_key)

        input_box.pack_start (self.input_stack, True, True, 6)
        input_box.pack_start (self.input_entry, False, True, 6)

        output_box.pack_start (Gtk.Label ('Output'), False, False, 0)

        self.output_tape = Gtk.TextView ()
        self.output_tape.set_cursor_visible (False)
        self.output_tape.set_justification (Gtk.Justification.RIGHT)
        self.output_tape.set_wrap_mode (Gtk.WrapMode.CHAR)
        self.output_tape.set_editable (False)

        self.clear_output = Gtk.Button (label='Clear')
        self.clear_output.connect ('clicked', self.on_clear_output)

        output_box.pack_start (self.output_tape, True, True, 6)
        output_box.pack_start (self.clear_output, False, False, 6)

        register_box = Gtk.Box (orientation = Gtk.Orientation.VERTICAL, spacing = 3)
        register_box.pack_start (Gtk.Label (''), False, False, 0)
        register_box.pack_start (Gtk.Label ('Counter'), False, False, 0)
        self.program_counter = Register (2)
        register_box.pack_start (self.program_counter, False, False, 0)
        register_box.pack_start (Gtk.Label (''), False, False, 0)
        register_box.pack_start (Gtk.Label ('Accumulator'), False, False, 0)
        self.accumulator = Register ()
        register_box.pack_start (self.accumulator, False, False, 0)
        register_box.pack_start (Gtk.Label (''), False, False, 0)
        register_box.pack_start (Gtk.Label ('Input'), False, False, 0)
        self.input_register = Register ()
        register_box.pack_start (self.input_register, False, False, 0)
        register_box.pack_start (Gtk.Label (''), False, False, 0)
        register_box.pack_start (Gtk.Label ('Output'), False, False, 0)
        self.output_register = Register ()
        register_box.pack_start (self.output_register, False, False, 0)
        display_box.pack_start (register_box, False, False, 0)

        self.memory = Memory (10, 10)
        self.memory.fill (self.computer.memory)
        display_box.pack_start (self.memory, False, False, 0)

        app_box.pack_start (control_box, False, False, 20)
        app_box.pack_start (input_box, False, False, 0)
        app_box.pack_start (output_box, False, False, 0)
        app_box.pack_start (display_box, False, False, 0)

    def load_file (self, filename):
        self.computer.load (filename)
        self.memory.fill (self.computer.memory)
        self.program_name.set_text (os.path.basename (filename))
        self.run.set_sensitive (True)

    def on_load (self, widget):
        chooser = Gtk.FileChooserDialog ('Select A Program',
                                         buttons = (Gtk.STOCK_CANCEL, 
                                                    Gtk.ResponseType.CANCEL,
                                                    Gtk.STOCK_OPEN, 
                                                    Gtk.ResponseType.OK))
        response = chooser.run ()
        if response == Gtk.ResponseType.OK:
            try:
                self.load_file (chooser.get_filename ())
            except lmc.Bad_Program, (p):
                error = Gtk.MessageDialog (self, 
                                           Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.ERROR,
                                           Gtk.ButtonsType.OK,
                                           'Could not load program %s' % p.file)
                error.format_secondary_text ('Not an LMC machine code file.')
                error.run ()
                error.destroy ()
        chooser.destroy ()

    def on_run (self, widget):
        self.run.set_sensitive (False)
        self.computer.run ()

    def on_input_key (self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            entry = self.input_entry.get_text ()
            self.input_entry.set_text ('')
            n = 0
            try:
                n = int (entry)
            except ValueError:
                return

            buffer = self.input_stack.get_buffer ()
            buffer.insert (buffer.get_end_iter (), entry + '\n')
            if self.computer.waiting_for_input:
                self.input_entry.set_ready (False)
                self.computer.set_input (self.notify_input ())
                self.computer.resume ()

    def on_clear_output (self, widget):
        buffer = self.output_tape.get_buffer ()
        buffer.delete (buffer.get_start_iter (), buffer.get_end_iter ())

    def notify_step (self):
        self.program_counter.set (self.computer.counter)
        self.accumulator.set (self.computer.counter)
        self.input_register.set (self.computer.input)
        self.output_register.set (self.computer.output)
        self.memory.fill (self.computer.memory)
        self.memory.set_step (self.computer.counter)
        return True # Don't block

    def notify_input (self):
        buffer = self.input_stack.get_buffer ()
        text = string.split (buffer.get_text (buffer.get_start_iter (),
                                              buffer.get_end_iter (), 
                                              True),
                             '\n')
        if len (text) > 0 and text [0] != '':
            buffer.set_text (string.join (text [1:], '\n'))
            return int (text [0])
        else:
            # Put an icon in the text field to indicate that we're ready for
            # input.
            self.input_entry.set_ready (True)
            self.input_entry.grab_focus ()
            return False

    def notify_output (self, out):
        buffer = self.output_tape.get_buffer ()
        buffer.insert (buffer.get_start_iter (), '%3d\n' % out)

    def notify_halt (self):
        self.run.set_sensitive (True)

def print_help (app):
    print 'GUI for the Little Man Computer'
    print
    print 'Usage: %s [<program-name>]' % app
    print
    print 'where <program-name> is the name of a machine-code program file.'
    print

def run (program, args):
    if len (args) > 1:
        print_help (program)
    else:
        app = App ()
        if len (args) == 1: app.load_file (args [0])
        app.connect ('delete-event', Gtk.main_quit)
        app.show_all ()
        Gtk.main ()

if __name__ == '__main__':
    run (sys.argv [0], sys.argv [1:])
