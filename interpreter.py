# TODO: implement booleans, strings, loops, if statement, chorus

import re
from basic import *
from lexer import *
from expression_parser import *

# blocks
VERSE = '^\[Verse \w+\]$'
CHORUS = '\[Chorus\]$'
INTRO = '\[Intro\]$'

# statements
SAY = 'Never gonna say .+'
DECLARE = 'Never gonna let \w+ down$'
ASSIGN = 'Never gonna give \w+ .+'

class Interpreter: 
    def __init__(self, text=None):
        self.text = text.split('\n') if text else []
        self.variable_cache = dict()

    def append(self, line):
        self.text.append(line)

    def execute(self):
        inMain = False
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
            else:
                print('Other!')
            pos += 1

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
