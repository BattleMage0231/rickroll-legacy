# TODO: implement booleans, strings, loops, if statement, chorus

import re
from basic import *
from lexer import *
from expression_parser import *

# blocks
VERSE = '^\[Verse \w+\]$'
CHORUS = '^\[Chorus\]$'
INTRO = '^\[Intro\]$'

# statements
SAY = '^Never gonna say .+$'
DECLARE = '^Never gonna let \w+ down$'
ASSIGN = '^Never gonna give \w+ .+$'

CHECK_TRUE = '^Inside we both know .+$'
WHILE_END = '^We know the game and we\'re gonna play it$'
IF_END = '^Your heart\'s been aching but you\'re too shy to say it$'

class Interpreter: 
    def __init__(self, text=None):
        self.text = text.split('\n') if text else []
        self.variable_cache = dict()

    def append(self, line):
        self.text.append(line)

    def execute(self):
        inMain = False
        loop_stack = [] # stores lines of loop declarations
        pos = 0
        while pos < len(self.text):
            line = self.text[pos].strip()
            if line == '':
                pass
            elif re.match(INTRO, line):
                print('Intro!')
            elif re.match(VERSE, line):
                print('Verse!')
            elif re.match(CHORUS, line):
                print('Chorus!')
            elif re.match(SAY, line):
                expr = line[16 : ] # get expression
                # special command goodbye exits the program
                if expr == 'goodbye':
                    exit()
                # evaluate expression and print
                res, error = self.evaluate(expr)
                if error != None:
                    print(error.as_string())
                else:
                    print(res.value)
            elif re.match(DECLARE, line):
                name = line[16 : -5] # variable name
                # if variable already exists
                if name in self.variable_cache:
                    print(RuntimeError('Variable ' + name + ' already exists').as_string())
                else:
                    # create new undefined token since we don't know type
                    self.variable_cache[name] = Token(TT_UNDEFINED, 'UNDEFINED')
            elif re.match(ASSIGN, line):
                value = line[17 : ] # get arguments as raw text
                index = value.find(' ') # variable names cannot have spaces
                # if no space found
                if index == -1:
                    print(IllegalArgumentError(value).as_string())
                else:
                    name = value[ : index] # everything before space is name
                    expr = value[index : ] # everything after is expression
                    # if variable exists
                    if name in self.variable_cache:
                        # assign evaluated result to variable
                        self.variable_cache[name], error = self.evaluate(expr)
                        # if error occured
                        if error != None:
                            print(error.as_string())
                    else:
                        print(RuntimeError('Variable ' + name + ' does not exist').as_string())
            elif re.match(CHECK_TRUE, line):
                expr = line[20 : ] # get boolean expression
                res, error = self.evaluate(expr)
                if error != None:
                    print(error.as_string())
                else:
                    # check if result is a boolean
                    if res.type == TT_BOOL:
                        # if true, execute the inside
                        if res.value == 'TRUE':
                            loop_stack.append(pos)
                        else:
                            # else skip to the end
                            while pos < len(self.text) and not (re.match(WHILE_END, self.text[pos].strip()) or re.match(IF_END, self.text[pos].strip())):
                                pos += 1
                            # if there's no ending statement
                            if pos == len(self.text):
                                print(RuntimeError('Unexpected EOF').as_string())
                    else:
                        # if result is not a boolean
                        print(IllegalArgumentError('Boolean expected').as_string())
            elif re.match(IF_END, line):
                # if loop stack is empty
                if not loop_stack:
                    print('Unexpected statement end')
                else:
                    # if statement end, simply pop
                    loop_stack.pop()
            elif re.match(WHILE_END, line):
                # if loop stack is empty
                if not loop_stack:
                    print('Unexpected statement end')
                else:
                    # reset position to the original position - 1
                    # pos gets incremented at the end of this loop
                    pos = loop_stack.pop() - 1
            else:
                print('Other!')
            pos += 1
        # if loop stack has not been closed
        if loop_stack:
            print(RuntimeError('Unexpected EOF').as_string())

    # evaluates an expression using expression_parser and lexer
    def evaluate(self, text):
        l = Lexer(text, self.variable_cache)
        tokens, error = l.make_tokens()
        if error:
            return None, error
        p = Parser(tokens)
        res, error = p.recurse()
        if error:
            return None, error
        return res, None
