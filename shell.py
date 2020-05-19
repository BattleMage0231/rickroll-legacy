import basic
import interpreter
import re
import os

os.system("cls") # windows workaround to fix color formatting bug

# color constants
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_END = '\033[0m'

# format text in color
def in_color(text, color):
    return color + text + COLOR_END

def format_lineStr(line):
    lineStr = str(line % 1000)
    length = len(lineStr)
    if length == 1:
        return '  ' + lineStr
    if length == 2:
        return ' ' + lineStr
    return lineStr

inter = interpreter.Interpreter()

in_editor = False
line = 1

while True:
    # if currently editing code
    if in_editor:
        # format in yellow
        text = input(in_color(format_lineStr(line) + ' > ', COLOR_YELLOW))
        # detect for exiting editor
        if text.strip() == 'exit':
            in_editor = False
        else:
            # otherwise append text to program
            inter.append(text)
            line += 1
    else:
        # otherwise in console
        text = input(in_color('rickroll > ', COLOR_GREEN)).strip()
        if text == 'edit':
            in_editor = True
        elif text == 'run':
            code = inter.execute(basic.Context(None))
            if code != None:
                print('The program finished with return value ' + str(code))
        elif re.match('^delete \d+$', text):
            index = int(text[7 : ])
            # if index in bounds
            if index < line:
                inter.pop(index)
                line -= 1
            else:
                print(in_color('No such index', COLOR_RED))
        elif re.match('^insert \d+$', text):
            index = int(text[7 : ])
            # if index in bounds or one after (new line)
            if index <= line:
                text = input(in_color(format_lineStr(index) + ' > ', COLOR_YELLOW))
                inter.insert(index, text)
                line += 1
            else:
                print(in_color('No such index', COLOR_RED))
        elif re.match('^replace \d+$', text):
            index = int(text[8 : ])
            # if index in bounds
            if index < line:
                text = input(in_color(format_lineStr(index) + ' > ', COLOR_YELLOW))
                inter.replace(index, text)
            else:
                print(in_color('No such index', COLOR_RED))
        elif text == 'display':
            lines = inter.text
            index = 1
            for program_line in lines:
                print(in_color(format_lineStr(index) + ' > ', COLOR_YELLOW) + program_line)
                index += 1
        elif text == 'new':
            inter = interpreter.Interpreter()
            line = 1 # reset line
        elif text == 'exit':
            exit()