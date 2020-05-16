import basic
import interpreter

inter = interpreter.Interpreter()

while True:
    text = input('rickroll > ')
    if text.strip() == 'run':
        inter.execute()
        inter = interpreter.Interpreter()
    else :
        inter.append(text)