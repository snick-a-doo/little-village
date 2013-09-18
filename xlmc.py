#!/usr/bin/python

# xlmc.py - A graphical front end for the Little Man Computer emulator.
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
from gi.repository import Gtk
from gi.repository import Gdk

import lmc

class Number_Pad (Gtk.Grid):
    def __init__ (self):
        Gtk.Grid.__init__ (self)
        self.buttons = []
        for i in range (3):
            for j in range (3):
                button = Gtk.Button (label = '%d' % (3*(2-i) + j + 1))
                self.attach (button, j, i, 1, 1)
                self.buttons.append (button)
        button = Gtk.Button (label = '0')
        self.attach (button, 0, 3, 1, 1)
        self.buttons.append (button)
        button = Gtk.Button (label = 'Enter')
        self.attach (button, 1, 3, 2, 1)
        self.buttons.append (button)

        for button in self.buttons:
            button.connect ('clicked', self.on_click)

    def set_sensitive (self, sensitive):
        for button in self.buttons:
            button.set_sensitive (sensitive)

    def connect (self, event, callback):
        if event == 'clicked':
            self.callback = callback

    def on_click (self, widget):
        self.callback (self, widget.get_label ())

class Register (Gtk.Entry):
    def __init__ (self, chars = 3):
        Gtk.Entry.__init__ (self, xalign = 1.0)
        self.set_max_length (chars)
        self.set_width_chars (chars)

class Memory (Gtk.Grid):
    def __init__ (self, width, height):
        Gtk.Grid.__init__ (self)
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

        self.power = Gtk.Button (label='Power')
        self.power.connect ('clicked', self.on_power)
        control_box.pack_start (self.power, False, False, 0)

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

        # Keep the blank space before the digits like a calculator.
        #self.input = Register ()
        #self.input.set_sensitive (False)
        #self.input.set_icon_from_stock (Gtk.EntryIconPosition.PRIMARY,
        #                                Gtk.STOCK_NO)
        #self.input.set_icon_from_stock (Gtk.EntryIconPosition.SECONDARY,
        #                                Gtk.STOCK_CLEAR)
        #self.input.connect ('activate', self.on_input)
        #self.input.connect ('icon-press', self.on_clear)

        #input_box.pack_start (self.input, False, False, 0)

        self.input = Gtk.TextView ()
        self.input.set_justification (Gtk.Justification.RIGHT)
        self.input.set_wrap_mode (Gtk.WrapMode.CHAR)

        input_box.pack_start (self.input, True, True, 6)

        self.pad = Number_Pad ()
        self.pad.set_sensitive (False)
        self.pad.connect ('clicked', self.on_number)
        #input_box.pack_start (self.pad, False, False, 0)

        output_box.pack_start (Gtk.Label ('Output'), False, False, 0)

        self.output = Gtk.TextView ()
        self.output.set_cursor_visible (False)
        self.output.set_justification (Gtk.Justification.RIGHT)
        self.output.set_wrap_mode (Gtk.WrapMode.CHAR)
        self.output.set_editable (False)

        output_box.pack_start (self.output, True, True, 6)

        register_box = Gtk.Box (orientation = Gtk.Orientation.VERTICAL, spacing = 6)
        register_box.pack_start (Gtk.Label (''), False, False, 0)
        register_box.pack_start (Gtk.Label ('Counter'), False, False, 0)
        self.program_counter = Register (2)
        register_box.pack_start (self.program_counter, False, False, 0)
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

        #app_box.pack_start (space_box, False, False, 0)
        app_box.pack_start (control_box, False, False, 20)
        app_box.pack_start (input_box, False, False, 0)
        app_box.pack_start (output_box, False, False, 0)
        app_box.pack_start (display_box, False, False, 0)

    def load_file (self, filename):
        self.computer.load (filename)
        self.memory.fill (self.computer.memory)
        self.program_name.set_text (os.path.basename (filename))
        self.run.set_sensitive (True)

    def on_power (self, widget):
        Gtk.main_quit ()

    def on_load (self, widget):
        chooser = Gtk.FileChooserDialog ('Select A Program',
                                         buttons = (Gtk.STOCK_CANCEL, 
                                                    Gtk.ResponseType.CANCEL,
                                                    Gtk.STOCK_OPEN, 
                                                    Gtk.ResponseType.OK))
        response = chooser.run ()
        if response == Gtk.ResponseType.OK:
            self.load_file (chooser.get_filename ())
        chooser.destroy ()

    def on_run (self, widget):
        self.run.set_sensitive (False)
        self.output.get_buffer ().set_text ('')
        self.computer.run ()

    def on_input (self, widget):
        self.input.set_icon_from_stock (Gtk.EntryIconPosition.PRIMARY,
                                        Gtk.STOCK_NO)
        self.input.set_sensitive (False)
        self.pad.set_sensitive (False)
        self.computer.set_input (int (self.input.get_text ()))
        self.computer.resume ()

    def on_clear (self, widget, position, event):
        if position == Gtk.EntryIconPosition.SECONDARY:
            self.input.set_text ('')

    def on_number (self, widget, label):
        if label == 'Enter':
            self.on_input (None)
        else:
            text = self.input.get_text ()
            if len (text) < 3:
                self.input.set_text (text + label)

    def input_callback (self):
        self.input.set_sensitive (True)
        self.pad.set_sensitive (True)
        self.input.set_icon_from_stock (Gtk.EntryIconPosition.PRIMARY,
                                        Gtk.STOCK_OK)

    def output_callback (self, out):
        buffer = self.output.get_buffer ()
        buffer.insert (buffer.get_start_iter (), '%3d\n' % out)

    def halt_callback (self):
        self.run.set_sensitive (True)


app = App ()
if len (sys.argv) > 1:
    app.load_file (sys.argv [1])

app.connect ('delete-event', Gtk.main_quit)
app.show_all ()
Gtk.main ()
