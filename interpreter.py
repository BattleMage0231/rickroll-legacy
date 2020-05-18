# TODO: implement strings, chorus

import re
from basic import *
from lexer import *
from expression_parser import *

# blocks
VERSE = '^\[Verse \w+\]$'
CHORUS = '^\[Chorus\]$'
INTRO = '^\[Intro\]$'

TT_INTRO = 'INTRO'
TT_VERSE = 'VERSE'
TT_CHORUS = 'CHORUS'

# statements
SAY = '^Never gonna say .+$'
DECLARE = '^Never gonna let \w+ down$'
ASSIGN = '^Never gonna give \w+ .+$'

CHECK_TRUE = '^Inside we both know .+$'
WHILE_END = '^We know the game and we\'re gonna play it$'
IF_END = '^Your heart\'s been aching but you\'re too shy to say it$'

ARGUMENT_TYPES = '(Ooh give you .+)'
RETURN = '^\(Ooh\) Never gonna give, never gonna give \(give you .+\)$'
CALL = 'Never gonna run .+ and desert .+'
CALL_VALUE = '\(Ooh give you \w+\) Never gonna run \w+ and desert .+'

class Interpreter: 
    def __init__(self, text=None):
        global_context = Context(None)
        self.text = text.split('\n') if text else []
        self.cur_context = global_context

    def append(self, line):
        self.text.append(line)

    # one indexed
    def pop(self, index):
        self.text.pop(index - 1)

    # one indexed
    def insert(self, index, text):
        self.text.insert(index - 1, text)

    # one indexed
    def replace(self, index, text):
        self.text[index - 1] = text

    def execute(self):
        global_context = Context(None)
        self.cur_context = global_context
        cur_block = None
        loop_stack = [] # stores lines of loop declarations
        pos = 0
        while pos < len(self.text):
            line = self.text[pos].strip()
            if line == '':
                pass
            elif re.match(INTRO, line):
                cur_block = TT_INTRO
            elif re.match(VERSE, line):
                cur_block = TT_VERSE
                name = line[7 : -1]
            elif re.match(CHORUS, line):
                cur_block = TT_CHORUS
                self.cur_context = Context(self.cur_context)
            elif cur_block == TT_VERSE:
                raise NotImplementedError('Not yet implemented')
            elif cur_block == TT_INTRO or cur_block == TT_CHORUS:
                if re.match(SAY, line):
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
                    # add variable to current context
                    error = self.cur_context.add_var(name, Token(TT_UNDEFINED, 'UNDEFINED'))
                    if error != None:
                        print(error.as_string())
                elif re.match(ASSIGN, line):
                    value = line[17 : ] # get arguments as raw text
                    index = value.find(' ') # variable names cannot have spaces
                    # if no space found
                    if index == -1:
                        print(IllegalArgumentError(value).as_string())
                    else:
                        name = value[ : index] # everything before space is name
                        expr = value[index : ] # everything after is expression
                        value, error = self.evaluate(expr)
                        if error != None:
                            print(error.as_string())
                        else:
                            # set variable
                            error = self.cur_context.set_var(name, value)
                            if error != None:
                                print(error.as_string())
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
                                self.cur_context = Context(self.cur_context) # make new context
                            else:
                                # else skip to the end
                                pos += 1
                                loop_balance = 1 # start with current CHECK_TRUE statement
                                # while pos is not end of program and loop is not balanced
                                while pos < len(self.text) and loop_balance != 0:
                                    # new CHECK_TRUE statement
                                    if re.match(CHECK_TRUE, self.text[pos].strip()):
                                        loop_balance += 1
                                    elif re.match(IF_END, self.text[pos].strip()) or re.match(WHILE_END, self.text[pos].strip()):
                                        # new closing statement
                                        loop_balance -= 1
                                    # error, loop not balanced
                                    if loop_balance < 0:
                                        break
                                    pos += 1
                                # if position is end of file and balance is not 0
                                # then the loop is not balanced
                                if loop_balance != 0 and pos == len(self.text):
                                    print(RuntimeError('Unexpected EOF').as_string())
                                else:
                                    # position was already incremented to the next
                                    # during the while loop so no need for pos += 1
                                    continue
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
                        self.cur_context = self.cur_context.parent # remove context
                elif re.match(WHILE_END, line):
                    # if loop stack is empty
                    if not loop_stack:
                        print('Unexpected statement end')
                    else:
                        # reset position to the original position - 1
                        # pos gets incremented at the end of this loop
                        pos = loop_stack.pop() - 1
                        self.cur_context = self.cur_context.parent # remove context
                elif re.match(RETURN, line):
                    return_val, error = self.evaluate(line[51 : -1])
                    if error != None:
                        print(error.as_string())
                    else:
                        return return_val
                else:
                    print('Other!')
            else:
                print('Other!')
            pos += 1
        # if loop stack has not been closed
        if loop_stack:
            print(RuntimeError('Unexpected EOF').as_string())

    # evaluates an expression using expression_parser and lexer
    def evaluate(self, text):
        l = Lexer(text, self.cur_context) # pass in current context as a parameter
        tokens, error = l.make_tokens()
        if error:
            return None, error
        p = Parser(tokens)
        res, error = p.recurse()
        if error:
            return None, error
        return res, None