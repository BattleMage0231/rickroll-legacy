import os
import re
import sys
import traceback
from enum import Enum

import basic
import interpreter

class ShellColors(Enum):
    COLOR_RED = '\033[91m'
    COLOR_GREEN = '\033[92m'
    COLOR_YELLOW = '\033[93m'
    COLOR_END = '\033[0m'

    @ staticmethod
    def in_color(text, color):
        return color.value + text + ShellColors.COLOR_END.value

INTERNAL_ERROR_MSG = 'An internal exception has occured'
INTERRUPTED_MSG = 'The program execution has been interrupted'
FILE_NOT_EXIST_MSG = 'The file does not exist'
CONSOLE_MSG = 'rickroll > '

INTERNAL_ERROR = ShellColors.in_color(INTERNAL_ERROR_MSG, ShellColors.COLOR_RED)
INTERRUPTED = ShellColors.in_color(INTERRUPTED_MSG, ShellColors.COLOR_RED)
FILE_NOT_EXIST = ShellColors.in_color(FILE_NOT_EXIST_MSG, ShellColors.COLOR_RED)
CONSOLE = ShellColors.in_color(CONSOLE_MSG, ShellColors.COLOR_GREEN)

class Shell:
    def __init__(self):
        self.code = []
        self.in_editor = False
        self.line = 1
    def loop(self):
        """Launches the shell"""
        os.system("cls") # windows workaround to fix color formatting bug
        while True:
            # if currently editing code
            if self.in_editor:
                # format in yellow
                input_msg = self.format_lineStr(self.line) + ' > '
                input_colored = ShellColors.in_color(input_msg, ShellColors.COLOR_YELLOW)
                text = input(input_colored)
                # detect for exiting editor
                if text.strip() == 'exit':
                    self.in_editor = False
                else:
                    # otherwise append text to program
                    self.code.append(text)
                    self.line += 1
                continue
            # otherwise in console
            text = input(CONSOLE).strip()
            if text == 'edit':
                self.in_editor = True
            elif text == 'run':
                try:
                    inter = interpreter.Interpreter(self.code)
                    exit_code, error = inter.run()
                    if error is not None:
                        err_str = error.as_string()
                        print(ShellColors.in_color(err_str, ShellColors.COLOR_RED))
                except KeyboardInterrupt:
                    print(INTERRUPTED)
                except BaseException:
                    print(INTERNAL_ERROR)
                    print(traceback.format_exc())
            elif re.match('^delete \d+$', text):
                index = int(text[7 : ])
                # if index in bounds
                if index < self.line:
                    self.code.pop(index - 1)
                    self.line -= 1
                else:
                    err_str = 'No such index'
                    print(ShellColors.in_color(err_str, ShellColors.COLOR_RED))
            elif re.match('^insert \d+$', text):
                index = int(text[7 : ])
                # if index in bounds or one after (new line)
                if index <= self.line:
                    input_msg = self.format_lineStr(index) + ' > '
                    input_colored = ShellColors.in_color(input_msg, ShellColors.COLOR_YELLOW)
                    text = input(input_colored)
                    self.code.insert(index - 1, text)
                    self.line += 1
                else:
                    print(ShellColors.in_color('No such index', ShellColors.COLOR_RED))
            elif re.match('^replace \d+$', text):
                index = int(text[8 : ])
                # if index in bounds
                if index < self.line:
                    input_msg = self.format_lineStr(index) + ' > '
                    input_colored = ShellColors.in_color(input_msg, ShellColors.COLOR_YELLOW)
                    text = input(input_colored)
                    self.code[index - 1] = text
                else:
                    print(ShellColors.in_color('No such index', ShellColors.COLOR_RED))
            elif text == 'display':
                for index in range(len(self.code)):
                    input_msg = self.format_lineStr(index + 1) + ' > '
                    input_colored = ShellColors.in_color(input_msg, ShellColors.COLOR_YELLOW)
                    print(input_colored + self.code[index])
            elif text == 'new':
                self.code = []
                self.line = 1 # reset line
            elif text == 'exit':
                exit()
    def format_lineStr(self, line):
        """
        Formats an integer index in the line format.
        1 becomes "  1", 10 becomes " 10", 100 becomes "100", 1000 becomes "0"
        """
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
                    exit_code, error = inter.run()
                    if error is not None:
                        print(ShellColors.in_color(error.as_string(), ShellColors.COLOR_RED))
                except KeyboardInterrupt:
                    print(INTERRUPTED)
                except BaseException:
                    print(INTERNAL_ERROR)
                    print(traceback.format_exc())
        else:
            print(FILE_NOT_EXIST)
