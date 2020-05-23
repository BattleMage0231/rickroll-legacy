import os
import re
import sys
import traceback

import basic
import interpreter

class Colors:
    COLOR_RED = '\033[91m'
    COLOR_GREEN = '\033[92m'
    COLOR_YELLOW = '\033[93m'
    COLOR_END = '\033[0m'

    @ staticmethod
    def in_color(text, color):
        return color + text + Colors.COLOR_END

class Shell:
    def __init__(self):
        self.code = []
        self.in_editor = False
        self.line = 1

    def loop(self):
        os.system("cls") # windows workaround to fix color formatting bug
        while True:
            # if currently editing code
            if self.in_editor:
                # format in yellow
                text = input(Colors.in_color(self.format_lineStr(self.line) + ' > ', Colors.COLOR_YELLOW))
                # detect for exiting editor
                if text.strip() == 'exit':
                    self.in_editor = False
                else:
                    # otherwise append text to program
                    self.code.append(text)
                    self.line += 1
                continue
            # otherwise in console
            text = input(Colors.in_color('rickroll > ', Colors.COLOR_GREEN)).strip()
            if text == 'edit':
                self.in_editor = True
            elif text == 'run':
                try:
                    inter = interpreter.Interpreter(self.code)
                    exit_code, error = inter.execute(basic.Context(None))
                    if error != None:
                        print(Colors.in_color(error.as_string(), Colors.COLOR_RED))
                except KeyboardInterrupt:
                    print(Colors.in_color('The program execution has been interrupted', Colors.COLOR_RED))
                except BaseException:
                    print(Colors.in_color('An internal exception has occured', Colors.COLOR_RED))
                    print(traceback.format_exc())
            elif re.match('^delete \d+$', text):
                index = int(text[7 : ])
                # if index in bounds
                if index < self.line:
                    self.code.pop(index - 1)
                    self.line -= 1
                else:
                    print(Colors.in_color('No such index', Colors.COLOR_RED))
            elif re.match('^insert \d+$', text):
                index = int(text[7 : ])
                # if index in bounds or one after (new line)
                if index <= self.line:
                    text = input(Colors.in_color(self.format_lineStr(index) + ' > ', Colors.COLOR_YELLOW))
                    self.code.insert(index - 1, text)
                    self.line += 1
                else:
                    print(Colors.in_color('No such index', Colors.COLOR_RED))
            elif re.match('^replace \d+$', text):
                index = int(text[8 : ])
                # if index in bounds
                if index < self.line:
                    text = input(Colors.in_color(self.format_lineStr(index) + ' > ', Colors.COLOR_YELLOW))
                    self.code[index - 1] = text
                else:
                    print(Colors.in_color('No such index', Colors.COLOR_RED))
            elif text == 'display':
                for index in range(len(self.code)):
                     print(Colors.in_color(self.format_lineStr(index + 1) + ' > ', Colors.COLOR_YELLOW) + self.code[index])
            elif text == 'new':
                self.code = []
                self.line = 1 # reset line
            elif text == 'exit':
                exit()

    def format_lineStr(self, line):
        lineStr = str(line % 1000)
        length = len(lineStr)
        return ' ' * (3 - length) + str(lineStr)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        shell = Shell()
        shell.loop()
    else:
        os.system("cls") # windows workaround to fix color formatting bug
        # get file name and check if it exists
        file_name = sys.argv[1]
        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                src = f.read()
                inter = interpreter.Interpreter(src.split('\n'))
                try:
                    exit_code, error = inter.execute(basic.Context(None))
                    if error != None:
                        print(Colors.in_color(error.as_string(), Colors.COLOR_RED))
                except KeyboardInterrupt:
                    print(Colors.in_color('The program execution has been interrupted', Colors.COLOR_RED))
                except BaseException:
                    print(Colors.in_color('An internal exception has occured', Colors.COLOR_RED))
                    print(traceback.format_exc())
        else:
            print(Colors.in_color('The file does not exist', Colors.COLOR_RED))
