import re
import sys
from basic import *
from lexer import *
from expression_parser import *

# TODO add custom handling for functions and move array methods from interpreter to shell
# interpreter should only be for execution

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

CAST = '^Never gonna make \w+ \w+$'

ARGUMENT_NAMES = '\(Ooh give you .+\)'
RETURN = '^\(Ooh\) Never gonna give, never gonna give \(give you .+\)$'
CALL = 'Never gonna run .+ and desert .+'
CALL_VALUE = '\(Ooh give you \w+\) Never gonna run \w+ and desert .+'

class Interpreter: 
    def __init__(self, text=[], is_main=True):
        self.text = text
        self.is_main = is_main

    def execute(self, context):
        # set local global context and current context
        self.global_context = context
        self.cur_context = self.global_context
        no_intro = False
        cur_block = None
        function_info = None
        loop_stack = [] # stores lines of loop declarations
        loop_balance = 0
        pos = 0
        while pos < len(self.text):
            line = self.text[pos].strip()
            if line == '':
                pass
            elif re.match(INTRO, line):
                if no_intro:
                    return None, SyntaxError('[Intro] block already found', pos)
                no_intro = True
                # line is starting point of intro block
                cur_block = TT_INTRO
            elif re.match(VERSE, line):
                no_intro = True
                # line is starting point of verse block
                # if there was a previous verse, store it
                if cur_block == TT_VERSE:
                    # tuple of (name, args, src)
                    if loop_balance != 0:
                        return None, RuntimeError('Unexpected function end', pos)
                    self.cur_context.add_function(function_info[0], function_info[1], function_info[2])
                loop_balance = 0
                cur_block = TT_VERSE
                name = line[7 : -1] # name of function
                pos += 1 # arguments are on next line
                # if arguments are missing
                if pos == len(self.text) or not re.match(ARGUMENT_NAMES, self.text[pos].strip()):
                    return None, SyntaxError('Unexpected EOF (no parameters provided)', pos)
                    function_info = (name, [], [])
                else:
                    # get arguments delimited by space
                    args = [arg.strip() for arg in self.text[pos].strip()[14 : -1].split(' ') if arg.strip()]
                    # up is a constant for no args
                    if len(args) == 1 and args[0] == 'up':
                        args = []
                    # store function info
                    function_info = (name, args, [])
            elif re.match(CHORUS, line):
                no_intro = True
                # line is starting point of chorus block
                # if there was a previous verse, store it
                if cur_block == TT_VERSE:
                    if loop_balance != 0:
                        return None, RuntimeError('Unexpected function end', pos)
                    self.cur_context.add_function(function_info[0], function_info[1], function_info[2])
                loop_balance = 0
                cur_block = TT_CHORUS
                self.cur_context = Context(self.cur_context) # new local context
            elif cur_block == TT_VERSE:
                if re.match(CHECK_TRUE, line):
                    loop_balance += 1
                elif re.match(IF_END, line) or re.match(WHILE_END, line):
                    loop_balance -= 1
                if loop_balance < 0:
                    return None, RuntimeError('Unexpected function end', pos)
                function_info[2].append(line) # do not execute immediately since part of block
            elif cur_block == TT_INTRO or cur_block == TT_CHORUS:
                if re.match(SAY, line):
                    expr = line[16 : ] # get expression
                    # special command goodbye exits the program
                    if expr == 'goodbye':
                        exit()
                    # evaluate expression and print
                    res, error = self.evaluate(expr)
                    if error != None:
                        return None, Traceback(pos + 1, error)
                    else:
                        print(res)
                elif re.match(DECLARE, line):
                    name = line[16 : -5] # variable name
                    # add variable to current context
                    error = self.cur_context.add_var(name, CONSTANTS['UNDEFINED'])
                    if error != None:
                        return None, Traceback(pos + 1, error)
                elif re.match(ASSIGN, line):
                    value = line[17 : ] # get arguments as raw text
                    index = value.find(' ') # variable names cannot have spaces
                    # if no space found
                    if index == -1:
                        return None, IllegalArgumentError(value, pos)
                    else:
                        name = value[ : index] # everything before space is name
                        expr = value[index : ] # everything after is expression
                        value, error = self.evaluate(expr)
                        if error != None:
                            return None, Traceback(pos + 1, error)
                        else:
                            # set variable
                            error = self.cur_context.set_var(name, value)
                            if error != None:
                                return None, Traceback(pos + 1, error)
                elif re.match(CHECK_TRUE, line):
                    expr = line[20 : ] # get boolean expression
                    res, error = self.evaluate(expr)
                    if error != None:
                        return None, Traceback(pos + 1, error)
                    else:
                        if res.type != TT_BOOL:
                            res, error = self.cast(res, TT_BOOL)
                            if error != None:
                                return None, IllegalArgumentError('Boolean expected', pos)
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
                                return None, RuntimeError('Unexpected EOF', pos)
                            else:
                                # position was already incremented to the next
                                # during the while loop so no need for pos += 1
                                continue
                elif re.match(IF_END, line):
                    # if loop stack is empty
                    if not loop_stack:
                        return None, RuntimeError('Unexpected statement end', pos)
                    else:
                        # if statement end, simply pop
                        loop_stack.pop()
                        self.cur_context = self.cur_context.parent # remove context
                elif re.match(WHILE_END, line):
                    # if loop stack is empty
                    if not loop_stack:
                        return None, RuntimeError('Unexpected statement end', pos)
                    else:
                        # reset position to the original position - 1
                        # pos gets incremented at the end of this loop
                        pos = loop_stack.pop() - 1
                        self.cur_context = self.cur_context.parent # remove context
                elif re.match(RETURN, line):
                    # get return value
                    return_val, error = self.evaluate(line[51 : -1])
                    if error != None:
                        return None, Traceback(pos + 1, error)
                    else:
                        # prematurely return
                        return return_val, None
                elif re.match(CALL, line):
                    value = line[16 : ]
                    index = value.find(' ')
                    name = value[ : index].strip() # get function name
                    index = value.find('desert') # get first index of 'desert' as reference
                    # get arguments trimmed and delimited by ', '
                    # also prune arguments for empty spaces
                    args = [arg.strip() for arg in value[index + 7 : ].split(', ') if arg.strip()]
                    res, error = self.exec(name, args)
                    if error != None:
                        return None, Traceback(pos + 1, error)
                elif re.match(CALL_VALUE, line):
                    value = line[14 : ]
                    index = value.find(' ')
                    return_var = value[ : index - 1] # get return variable
                    value = value[index + 17 : ]
                    index = value.find(' ')
                    name = value[ : index].strip() # get function name
                    index = value.find('desert') # get first index of 'desert' as reference
                    # get arguments trimmed and delimited by ', '
                    # also prune arguments for empty spaces
                    args = [arg.strip() for arg in value[index + 7 : ].split(', ') if arg.strip()]
                    res, error = self.exec(name, args)
                    if error != None:
                        return None, Traceback(pos + 1, error)
                    else:
                        # assign value to return)var
                        error = self.cur_context.set_var(return_var, res)
                        if error != None:
                            return None, Traceback(pos + 1, error)
                elif re.match(CAST, line):
                    value = line[17 : ]
                    index = value.find(' ')
                    name = value[ : index]
                    to_type = value[index + 1 : ]
                    var, error = self.cur_context.get_var(name)
                    if error != None:
                        return None, Traceback(pos + 1, error)
                    res, error = self.cast(var, to_type)
                    if error != None:
                        return None, Traceback(pos + 1, error)
                    self.cur_context.set_var(name, res)
                else:
                    print('Other!')
            else:
                print('Other!')
            pos += 1
        # if loop stack has not been closed
        if loop_stack:
            return None, RuntimeError('Unexpected EOF', pos)
        return None, None

    # evaluates an expression using expression_parser and lexer
    def evaluate(self, text, context=None):
        if context == None:
            context = self.cur_context
        l = Lexer(text, context) # pass in current context as a parameter
        tokens, error = l.make_tokens()
        if error:
            return None, error
        p = Parser(tokens)
        res, error = p.recurse()
        if error:
            return None, error
        return res, None

    # takes in function name and unevaluated arguments
    # executes function and returns result
    def exec(self, function, args):
        # 'you' is a constant that means no arguments
        if args[0] == 'you':
            args = []
        # evaluate in self.exec_builtin if function is built-in
        if function in FUNCTION_CONSTANTS:
            return self.exec_builtin(function, args)
        # otherwise get arguments and source code from current context
        func_args, src, error = self.cur_context.get_function(function)
        if error != None:
            return None, error 
        tmp_interpreter = Interpreter() # new runtime
        tmp_interpreter.append('[Chorus]')
        # if argument count matches
        if len(args) == len(func_args):
            # create all passed in variables locally at the start
            for i in range(len(args)):
                tmp_interpreter.append('Never gonna let ' + func_args[i] + ' down')
                res, error = self.evaluate(args[i]) # evaluate arguments before appending
                if error != None:
                    return None, error
                tmp_interpreter.append('Never gonna give ' + func_args[i] + ' ' + str(res.value))
            # append all function lines
            for line in src:
                tmp_interpreter.append(line)
            # add undefined return value in case no return statement at the end
            tmp_interpreter.append('(Ooh) Never gonna give, never gonna give (give you UNDEFINED)')
            # execute with global context so runtime has access to variables and functions
            res, error = tmp_interpreter.execute(self.global_context)
            return res, error
        else:
            return None, SyntaxError('Too many or too little arguments')

    # executes a built-in function
    def exec_builtin(self, function, args):
        # evaluate all arguments
        for i in range(len(args)):
            res, error = self.evaluate(args[i])
            if error != None:
                return None, error
            args[i] = res
        if function == FUNCTION_POP:
            if len(args) == 2:
                # takes parameters [array, index]
                if args[0].type == TT_ARRAY and args[1].type == TT_INT:
                    # if index in bounds
                    if len(args[0].value) > args[1].value and args[1].value >= 0:
                        tmp_arr = args[0].value[:] # clone of array
                        tmp_arr.pop(args[1].value)
                        return Token(TT_ARRAY, tmp_arr), None
                    else:
                        return None, RuntimeError('Array index out of bounds')
                else:
                    return None, IllegalArgumentError('Unsupported argument types')
            else:
                return None, SyntaxError('Too many or too little arguments')
        elif function == FUNCTION_PUSH:
            if len(args) == 2:
                # takes parameters [array]
                if args[0].type == TT_ARRAY:
                    tmp_arr = args[0].value[:] # clone of array
                    tmp_arr.append(args[1])
                    return Token(TT_ARRAY, tmp_arr), None
                else:
                    return None, IllegalArgumentError('Unsupported argument types')
            else:
                return None, SyntaxError('Too many or too little arguments')
        elif function == FUNCTION_REPLACE:
            if len(args) == 3:
                # takes parameters [array, index, any]
                if args[0].type == TT_ARRAY and args[1].type == TT_INT:
                    # if index in bounds
                    if len(args[0].value) > args[1].value and args[1].value >= 0:
                        tmp_arr = args[0].value[:] # clone of array
                        tmp_arr[args[1].value] = args[2]
                        return Token(TT_ARRAY, tmp_arr), None
                    else:
                        return None, RuntimeError('Array index out of bounds')
                else:
                    return None, IllegalArgumentError('Unsupported argument types')
            else:
                return None, SyntaxError('Too many or too little arguments')
        elif function == FUNCTION_SUBARR:
            # takes parameters [array, startIndex, endIndex]
            # [startIndex, endIndex)
            if len(args) == 3:
                # check if indexes are in bounds
                if args[0].type == TT_ARRAY and args[1].type == TT_INT and args[2].type == TT_INT:
                    if len(args[0].value) > args[1].value and len(args[0].value) >= args[2].value\
                    and args[1].value >= 0 and args[2].value >= 0 and args[1].value <= args[2].value:
                        tmp_arr = args[0].value[args[1].value : args[2].value] # subarray
                        return Token(TT_ARRAY, tmp_arr), None
                    else:
                        return None, RuntimeError('Array index out of bounds')
                else:
                    return None, IllegalArgumentError('Unsupported argument types')
            else:
                return None, SyntaxError('Too many or too little arguments')
        elif function == FUNCTION_PUTCHAR:
            if len(args) == 1:
                # takes parameter [char]
                if args[0].type == TT_CHAR:
                    tmp_arr = args[0].value[:] # clone array
                    sys.stdout.write(args[0].value)
                    return CONSTANTS['UNDEFINED'], None
                else:
                    return None, IllegalArgumentError('Unsupported argument types')
            else:
                return None, SyntaxError('Too many or too little arguments')
        elif function == FUNCTION_ARRAYOF:
            # make array
            return Token(TT_ARRAY, [arg for arg in args]), None
        elif function == FUNCTION_GETLENGTH:
            if len(args) == 1:
                # takes parameter [array]
                if args[0].type == TT_ARRAY:
                    # returns an int with length of array
                    return Token(TT_INT, len(args[0].value)), None
                else:
                    return None, IllegalArgumentError('Unsupported argument types')
            else:
                return None, SyntaxError('Too many or too little arguments')
        elif function == FUNCTION_INPUT:
            # takes no parameters
            if len(args) == 0:
                char_arr = [Token(TT_CHAR, char) for char in list(input())]
                return Token(TT_ARRAY, char_arr), None
            else:
                return None, SyntaxError('Too many or too little arguments')

    def cast(self, token, new_type):
        if token.type == new_type:
            return token, None
        # casting to INT
        if new_type == TT_INT:
            if token.type == TT_FLOAT:
                return Token(TT_INT, int(token.value)), None
            if token.type == TT_BOOL:
                return Token(TT_INT, 1 if token.value == 'TRUE' else 0), None
            if token.type == TT_CHAR:
                return Token(TT_INT, ord(token.value)), None
        elif new_type == TT_FLOAT:
            # casting to FLOAT
            if token.type == TT_INT:
                return Token(TT_FLOAT, float(token.value)), None
            if token.type == TT_BOOL:
                return Token(TT_FLOAT, 1.0 if token.value == 'TRUE' else 0.0), None
            if token.type == TT_CHAR:
                return Token(TT_FLOAT, float(ord(token.value))), None
        elif new_type == TT_BOOL:
            # casting to BOOL
            if token.type == TT_INT:
                return CONSTANTS['FALSE'] if token.value == 0 else CONSTANTS['TRUE'], None
            if token.type == TT_FLOAT:
                return CONSTANTS['FALSE'] if token.value == 0.0 else CONSTANTS['TRUE'], None
            if token.type == TT_ARRAY:
                return CONSTANTS['FALSE'] if not token.value else CONSTANTS['TRUE'], None
            if token.type == TT_UNDEFINED:
                return CONSTANTS['FALSE']
        elif new_type == TT_ARRAY:
            # casting to ARRAY
            pass
        elif new_type == TT_CHAR:
            # casting to CHAR
            try:
                if token.type == TT_INT:
                    return Token(TT_CHAR, chr(token.value)), None
                if token.type == TT_FLOAT:
                    return Token(TT_CHAR, chr(int(token.value))), None
            except:
                return None, IllegalCastError('Not a valid ASCII value')
        elif new_type == TT_UNDEFINED:
            # casting to undefined
            pass
        else:
            return None, IllegalArgumentError(new_type + ' not a data type')
        return None, IllegalCastError('Cannot cast ' + token.type + ' to ' + new_type)