import basic
import interpreter
import re

inter = interpreter.Interpreter()

in_editor = False
line = 1

while True:
    if in_editor:
        text = input('line ' + str(line) + ' > ')
        if text.strip() == 'exit':
            in_editor = False
        else:
            inter.append(text)
            line += 1
    else:
        text = input('rickroll > ').strip()
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
                print('No such index')
        elif re.match('^insert \d+$', text):
            index = int(text[7 : ])
            if index <= line:
                text = input('line ' + str(index) + ' > ')
                inter.insert(index, text)
                line += 1
            else:
                print('No such index')
        elif re.match('^replace \d+$', text):
            index = int(text[8 : ])
            if index < line:
                text = input('line ' + str(index) + ' > ')
                inter.replace(index, text)
                line += 1
            else:
                print('No such index')
        elif text == 'display':
            lines = inter.text
            index = 1
            for program_line in lines:
                print('line ' + str(index) + ' > ' + program_line)
                index += 1
        elif text == 'new':
            inter = interpreter.Interpreter()