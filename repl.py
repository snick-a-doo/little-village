#!/usr/bin/python
#
# An interactive LMC
#
import lmc
import string

class REPL_Client (lmc.LMC_Client):
    prompt = 'LMC> '

    def notify_input (self):
        return int (raw_input ('  input: '))

    def notify_output (self, out):
        print out
        return True

    def run (self):
        try:
            while self.parse (raw_input (REPL_Client.prompt)):
                pass
        except EOFError:
            # Quit on Ctrl+D
            pass
        print 'bye'

    def read (self):
        response = raw_input (REPL_Client.prompt);

    def parse (self, input):
        tokens = string.split (input)

        if len (tokens) == 0:
            return True

        command = tokens [0]
        argument = ''
        if len (tokens) > 1:
            argument = tokens [1]

        if command[0] == 'q':
            return False
        elif command == 'load':
            self.computer.load (argument)
        elif command == 'run':
            self.computer.run ()
        elif command == 'show':
            print self.computer

        return True

if __name__ == '__main__':
    client = REPL_Client ()
    client.run ()
