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

inter = interpreter.Interpreter()

in_editor = False
line = 1

while True:
    if in_editor:
        text = input(in_color('line ' + str(line) + ' > ', COLOR_YELLOW))
        if text.strip() == 'exit':
            in_editor = False
        else:
            inter.append(text)
            line += 1
    else:
        text = input(in_color('rickroll > ', COLOR_GREEN)).strip()
        if text == 'edit':
            in_editor = True
        elif text == 'run':
            inter.execute()
        elif re.match('^delete \d+$', text):
            index = int(text[7 : ])
            if index < line:
                inter.pop(index)
                line -= 1
            else:
                print(in_color('No such index', COLOR_RED))
        elif re.match('^insert \d+$', text):
            index = int(text[7 : ])
            if index <= line:
                text = input(in_color('line ' + str(index) + ' > ', COLOR_YELLOW))
                inter.insert(index, text)
                line += 1
            else:
                print(in_color('No such index', COLOR_RED))
        elif re.match('^replace \d+$', text):
            index = int(text[8 : ])
            if index < line:
                text = input(in_color('line ' + str(index) + ' > ', COLOR_YELLOW))
                inter.replace(index, text)
                line += 1
            else:
                print(in_color('No such index', COLOR_RED))
        elif text == 'display':
            lines = inter.text
            index = 1
            for program_line in lines:
                print(in_color('line ' + str(index) + ' > ', COLOR_YELLOW) + program_line)
                index += 1
        elif text == 'new':
            inter = interpreter.Interpreter()
        elif text == 'exit':
            exit()