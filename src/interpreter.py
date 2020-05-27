import os
import re
import sys

from basic import *
from expression_parser import *
from lexer import *

class Interpreter:
    def __init__(self, file, text=None):
        self.file = file
        if text is None:
            text = []
        self.text = text
        self.global_context = Context(None)
        self.cur_context = self.global_context
    def parse(self):
        """Parses the stored code"""
        no_intro = False
        no_chorus = False
        cur_block = None
        cur_function = None
        self.intro_info = None
        self.chorus_info = None
        loop_balance = 0
        pos = 0
        while pos < len(self.text):
            line = self.text[pos].strip()
            if not line:
                pass
            elif INTRO.match(line):
                if no_intro:
                    return SyntaxError('[Intro] block must be the first block', pos + 1, self.file)
                no_intro = True
                self.intro_info = ([], pos + 1)
                # line is starting point of intro block
                cur_block = TT_INTRO
            elif VERSE.match(line):
                no_intro = True
                # line is starting point of verse block
                # if there was a previous verse, store it
                if cur_block == TT_VERSE:
                    if loop_balance != 0:
                        return RuntimeError('Unexpected function end', pos + 1, self.file)
                    error = self.cur_context.add_function(cur_function)
                    if error is not None:
                        return None, error
                loop_balance = 0
                cur_block = TT_VERSE
                name = line[7 : -1] # name of function
                pos += 1 # arguments are on next line
                # if arguments are missing
                if pos == len(self.text) or not re.match(ARGUMENT_NAMES, self.text[pos].strip()):
                    return SyntaxError('Unexpected EOF (no parameters provided)', pos + 1, self.file)
                else:
                    # get arguments delimited by space
                    arg_list = self.text[pos].strip()[14 : -1].split()
                    args = [arg.strip() for arg in arg_list if arg.strip()]
                    # up is a constant for no args
                    if len(args) == 1 and args[0] == 'up':
                        args = []
                    cur_function = Function(name, args, [], pos + 1, self.file)
            elif CHORUS.match(line):
                if no_chorus:
                    return SyntaxError('[Chorus] block already found', pos + 1, self.file)
                no_chorus = True
                self.chorus_info = ([], pos + 1)
                no_intro = True
                # line is starting point of chorus block
                # if there was a previous verse, store it
                if cur_block == TT_VERSE:
                    if loop_balance != 0:
                        return RuntimeError('Unexpected function end', pos + 1, self.file)
                    error = self.cur_context.add_function(cur_function)
                    if error is not None:
                        return None, error
                loop_balance = 0
                cur_block = TT_CHORUS
                self.cur_context = Context(self.cur_context) # new local context
            elif cur_block == TT_VERSE:
                if re.match(CHECK_TRUE, line):
                    loop_balance += 1
                elif re.match(IF_END, line) or re.match(WHILE_END, line):
                    loop_balance -= 1
                if loop_balance < 0:
                    return RuntimeError('Unexpected function end', pos + 1, self.file)
                cur_function.src.append(line) # do not execute immediately since part of block
            elif cur_block == TT_INTRO:
                self.intro_info[0].append(line)
            elif cur_block == TT_CHORUS:
                self.chorus_info[0].append(line)
            else:
                return SyntaxError('Not a statement', pos + 1, self.file)
            pos += 1
        # if loop stack has not been closed
        if loop_balance != 0:
            return RuntimeError('Unexpected EOF', pos + 1, self.file)
        if cur_block == TT_VERSE:
            self.cur_context.add_function(cur_function)
    def run(self):
        """Runs the stored code"""
        if self.intro_info is not None:
            res, error = self.execute(self.intro_info[0], self.global_context, self.intro_info[1], self.file)
            if error is not None:
                return error
        if self.chorus_info:
            res, error = self.execute(self.chorus_info[0], Context(self.global_context), self.chorus_info[1], self.file)
            if error is not None:
                return error
    def execute(self, code, context, line_index, file):
        """Executes some code in context where code is stored as an array of lines"""
        loop_stack = []
        cur_context = context
        pos = 0
        while pos < len(code):
            line = code[pos].strip()
            if not line:
                pass
            elif IMPORT.match(line):
                path = line[22 : ].strip()
                if os.path.isfile(path):
                    try:
                        with open(path, 'r') as import_file:
                            tmp_inter = Interpreter(os.path.basename(path), import_file.read().split('\n'))
                            error = tmp_inter.parse()
                            if error is not None:
                                trace = Traceback(line + 1, error, os.path.basename(path))
                                return None, Traceback(line_index + pos + 1, trace, file)
                            # hijack the function and intro info
                            tmp_intro = tmp_inter.intro_info
                            functions = tmp_inter.cur_context.function_cache
                            for name in functions:
                                error = context.add_function(functions[name])
                                func_file = functions[name].file
                                if error is not None:
                                    trace = Traceback(line + 1, error, func_file)
                                    return None, Traceback(line_index + pos + 1, trace, file)
                            if tmp_intro is not None:
                                res, error = self.execute(tmp_intro[0], context, tmp_intro[1], tmp_inter.file)
                                if error is not None:
                                    trace = Traceback(line + 1, error, func_file)
                                    return None, Traceback(line_index + pos + 1, trace, file)
                    except PermissionError:
                        err_msg = 'Permission denied'
                        return None, FileError(err_msg, line_index + pos + 1, file)
                else:
                    err_msg = 'File ' + path + ' does not exist or is invalid'
                    return None, FileError(err_msg, line_index + pos + 1, file)
            elif SAY.match(line):
                expr = line[16 : ] # get expression
                # special command goodbye exits the program
                if expr == 'goodbye':
                    os._exit(0)
                # evaluate expression and print
                res, error = self.evaluate(expr, cur_context)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
                print(res)
            elif DECLARE.match(line):
                name = line[16 : -5] # variable name
                # add variable to current context
                error = cur_context.add_var(name, CONSTANTS['UNDEFINED'])
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
            elif ASSIGN.match(line):
                value = line[17 : ] # get arguments as raw text
                index = value.find(' ') # variable names cannot have spaces
                # if no space found
                if index == -1:
                    return None, IllegalArgumentError(value, line_index + pos + 1, file)
                name = value[ : index] # everything before space is name
                expr = value[index : ] # everything after is expression
                value, error = self.evaluate(expr, cur_context)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
                # set variable
                error = cur_context.set_var(name, value)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
            elif CHECK_TRUE.match(line):
                expr = line[20 : ] # get boolean expression
                res, error = self.evaluate(expr, cur_context)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
                if res.type != TT_BOOL:
                    res, error = self.cast(res, TT_BOOL)
                    if error is not None:
                        err_msg = 'Boolean expected, instead found ' + str(res)
                        err_index = line_index + pos + 1
                        error = IllegalArgumentError(err_msg, err_index, file)
                        return None, error
                # if true, execute the inside
                if res.value == 'TRUE':
                    loop_stack.append(pos)
                    cur_context = Context(cur_context) # make new context
                else:
                    # else skip to the end
                    pos += 1
                    loop_balance = 1 # start with current CHECK_TRUE statement
                    # while pos is not end of program and loop is not balanced
                    while pos < len(code) and loop_balance != 0:
                        # new CHECK_TRUE statement
                        if CHECK_TRUE.match(code[pos].strip()):
                            loop_balance += 1
                        elif IF_END.match(code[pos].strip()) or WHILE_END.match(code[pos].strip()):
                            # new closing statement
                            loop_balance -= 1
                        # error, loop not balanced
                        if loop_balance < 0:
                            break
                        pos += 1
                    # if position is end of file and balance is not 0
                    # then the loop is not balanced
                    if loop_balance != 0 and pos == len(self.text):
                        return None, RuntimeError('Unexpected EOF', line_index + pos + 1, file)
                    # position was already incremented to the next
                    # during the while loop so no need for pos += 1
                    continue
            elif IF_END.match(line):
                # if loop stack is empty
                if not loop_stack:
                    return None, RuntimeError('Unexpected statement end', line_index + pos + 1, file)
                # if statement end, simply pop
                loop_stack.pop()
                cur_context = cur_context.parent # remove context
            elif WHILE_END.match(line):
                # if loop stack is empty
                if not loop_stack:
                    return None, RuntimeError('Unexpected statement end', line_index + pos + 1, file)
                # reset position to the original position - 1
                # pos gets incremented at the end of this loop
                pos = loop_stack.pop() - 1
                cur_context = cur_context.parent # remove context
            elif RETURN.match(line):
                # get return value
                return_val, error = self.evaluate(line[51 : -1], cur_context)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
                # prematurely return
                return return_val, None
            elif CALL.match(line):
                value = line[16 : ]
                index = value.find(' ')
                name = value[ : index].strip() # get function name
                index = value.find('desert') # get first index of 'desert' as reference
                # get arguments trimmed and delimited by ', '
                # also prune arguments for empty spaces
                args = [arg.strip() for arg in value[index + 7 : ].split(',') if arg.strip()]
                res, error = self.exec(name, args, cur_context, file)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
            elif CALL_VALUE.match(line):
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
                res, error = self.exec(name, args, cur_context, file)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
                # assign value to return)var
                error = cur_context.set_var(return_var, res)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
            elif CAST.match(line):
                value = line[17 : ]
                index = value.find(' ')
                name = value[ : index]
                to_type = value[index + 1 : ]
                var, error = cur_context.get_var(name)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
                res, error = self.cast(var, to_type)
                if error is not None:
                    return None, Traceback(line_index + pos + 1, error, file)
                cur_context.set_var(name, res)
            else:
                return None, SyntaxError('Not a statement', line_index + pos + 1, file)
            pos += 1
        return CONSTANTS['UNDEFINED'], None
    def evaluate(self, text, context):
        """Evaluates an expression using parser and lexer"""
        lexer = Lexer(text, context) # pass in current context as a parameter
        tokens, error = lexer.make_tokens()
        if error is not None:
            return None, error
        parser = Parser(tokens)
        res, error = parser.recurse()
        if error is not None:
            return None, error
        return res, None
    def exec(self, function, args, context, file):
        """
        Executes the function with the given function name.
        Function must be inside context with same number of arguments.
        Returns result of function call.
        """
        # 'you' is a constant that means no arguments
        if args[0] == 'you':
            args = []
        # evaluate in self.exec_builtin if function is built-in
        if function in FUNCTION_CONSTANTS:
            return self.exec_builtin(function, args, context)
        # otherwise get arguments, source code, and line index from current context
        function_info, error = context.get_function(function)
        func_file = function_info.file
        line = function_info.line
        func_args = function_info.args
        src = function_info.src
        if error is not None:
            if file != func_file:
                return None, Traceback(line + 1, error, func_file)
            return None, error
        if len(args) != len(func_args):
            if file != func_file:
                return None, Traceback(line + 1, SyntaxError('Too many or too little arguments'), func_file)
            return None, SyntaxError('Too many or too little arguments')
        new_context = Context(self.global_context)
        for (arg, func_arg) in zip(args, func_args):
            res, error = self.evaluate(arg, context)
            if error is not None:
                if file != func_file:
                    return None, Traceback(line + 1, error, func_file)
                return None, error
            new_context.unsafe_set_var(func_arg, res) # allow duplicate variables in global
        res, error = self.execute(src, new_context, line, func_file)
        if error is not None:
            if file != func_file:
                return None, Traceback(line + 1, error, func_file)
            return None, error
        return res, None
    # executes a built-in function
    def exec_builtin(self, function, args, context):
        """
        Executes a built-in function in context.
        Function must have same number of arguments.
        """
        # evaluate all arguments
        for i in range(len(args)):
            res, error = self.evaluate(args[i], context)
            if error is not None:
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
                        err_str = 'Array index ' + str(args[1].value) + ' out of bounds'
                        return None, IndexOutOfBoundsError(err_str)
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
                        err_str = 'Array index ' + str(args[1].value) + ' out of bounds'
                        return None, IndexOutOfBoundsError(err_str)
                else:
                    return None, IllegalArgumentError('Unsupported argument types')
            else:
                return None, SyntaxError('Too many or too little arguments')
        elif function == FUNCTION_SUBARR:
            # takes parameters [array, startIndex, endIndex]
            # [startIndex, endIndex)
            if len(args) == 3:
                # check if indices are in bounds
                if args[0].type == TT_ARRAY and args[1].type == TT_INT and args[2].type == TT_INT:
                    first_in_bounds = (len(args[0].value) > args[1].value and args[1].value >= 0)
                    second_in_bounds = (len(args[0].value) >= args[2].value and args[2].value >= 0)
                    if first_in_bounds and second_in_bounds and args[1].value <= args[2].value:
                        tmp_arr = args[0].value[args[1].value : args[2].value] # subarray
                        return Token(TT_ARRAY, tmp_arr), None
                    else:
                        err_str = 'Array index ' + str(args[1].value) + ' out of bounds'
                        return None, IndexOutOfBoundsError(err_str)
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
        """Casts a token to another type and returns the new token"""
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
            except ValueError:
                return None, IllegalCastError('Not a valid ASCII value')
        elif new_type == TT_UNDEFINED:
            # casting to undefined
            pass
        else:
            return None, IllegalArgumentError(new_type + ' not a data type')
        return None, IllegalCastError('Cannot cast ' + token.type + ' to ' + new_type)
