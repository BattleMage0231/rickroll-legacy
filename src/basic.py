# Constants

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'

TT_BOOL = 'BOOL'

TT_ARRAY = 'ARRAY'

TT_CHAR = 'CHAR'

TT_UNDEFINED = 'UNDEFINED'

TT_ARRAY_ACCESS = 'ARRAY_ACCESS'

TT_ADD = 'ADD'
TT_SUBTRACT = 'SUBTRACT'
TT_MULTIPLY = 'MULTIPLY'
TT_DIVIDE = 'DIVIDE'
TT_MODULO = 'MODULO'

TT_UNARY_MINUS = 'UNARY_MINUS'

TT_AND = 'AND'
TT_OR = 'OR'
TT_NOT = 'NOT'

TT_GREATER = 'GREATER'
TT_LESS = 'LESS'
TT_GREATER_EQUALS = 'GREATER_EQUALS'
TT_LESS_EQUALS = 'LESS_EQUALS'
TT_EQUALS = 'EQUALS'
TT_NOT_EQUALS = 'NOT_EQUALS'

TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

# Function Constants

FUNCTION_POP = '_pop'
FUNCTION_PUSH = '_push'
FUNCTION_REPLACE = '_replace'
FUNCTION_SUBARR = '_subarr'
FUNCTION_PUTCHAR = '_putchar'
FUNCTION_ARRAYOF = '_arrayof'
FUNCTION_GETLENGTH = '_getlength'
FUNCTION_INPUT = '_input'

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

# Error

class Error:
    def __init__(self, name, details, line=None, child=None):
        self.name = name
        self.details = details
        self.line = line
        self.child = child

    def as_string(self):
        res = str(self.name)
        # line could be 0 so can't cast to boolean
        if self.line != None:
            res += ' on line ' + str(self.line)
        res += ': ' + str(self.details)
        if self.child:
            res += '\n' + self.child.as_string()
        return res

class IllegalCharError(Error):
    def __init__(self, details, line=None, child=None):
        super().__init__('Illegal Character', details, line, child)

class RuntimeError(Error):
    def __init__(self, details, line=None, child=None):
        super().__init__('Runtime Error', details, line, child)

class IllegalArgumentError(Error):
    def __init__(self, details, line=None, child=None):
        super().__init__('Illegal Argument', details, line, child)

class SyntaxError(Error):
    def __init__(self, details, line=None, child=None):
        super().__init__('Syntax Error', details, line, child)

class IllegalCastError(Error):
    def __init__(self, details, line=None, child=None):
        super().__init__('Illegal Case', details, line, child)

class Traceback(Error):
    def __init__(self, line=None, child=None):
        super().__init__('Traceback', '', line, child)

# Token

class Token:
    def __init__(self, token_type, value=None):
        self.type = token_type
        self.value = value
    
    def __repr__(self):
        # if token has a value, return it
        # otherwise return type
        return str(self.value if self.value != None else self.type)

# Operation

class Operation:
    def __init__(self, operator, args):
        self.operator = operator
        self.args = args

    def eval(self):
        # if operation is add
        if self.operator.type == TT_ADD:
            # if operation is binary
            if len(self.args) == 2:
                # if arguments are numbers
                if self.all_satisfies(self.is_number):
                    # if any of the arguments are floats, return a float
                    # otherwise return an int
                    if self.any_of(TT_FLOAT):
                        return Token(TT_FLOAT, self.args[0].value + self.args[1].value), None
                    return Token(TT_INT, self.args[0].value + self.args[1].value), None
        elif self.operator.type == TT_SUBTRACT:
            # subtract operation
            # unary minus handled in lexer
            # if operation is binary
            if len(self.args) == 2:
                # if arguments are numbers
                if self.all_satisfies(self.is_number):
                    # if any of the arguments are floats, return a float
                    # otherwise return an int
                    if self.any_of(TT_FLOAT):
                        return Token(TT_FLOAT, self.args[0].value - self.args[1].value), None
                    return Token(TT_INT, self.args[0].value - self.args[1].value), None
        elif self.operator.type == TT_MULTIPLY:
            # if operation is binary
            if len(self.args) == 2:
                # if arguments are numbers
                if self.all_satisfies(self.is_number):
                    # handle float and integer separately
                    if self.any_of(TT_FLOAT):
                        return Token(TT_FLOAT, self.args[0].value * self.args[1].value), None
                    return Token(TT_INT, self.args[0].value * self.args[1].value), None
        elif self.operator.type == TT_DIVIDE:
            # if operation is binary
            if len(self.args) == 2:
                # if arguments are numbers
                if self.all_satisfies(self.is_number):
                    # if any are float, do floating point division
                    # else do integer division
                    if self.any_of(TT_FLOAT):
                        return Token(TT_FLOAT, self.args[0].value / self.args[1].value), None
                    return Token(TT_INT, self.args[0].value // self.args[1].value), None
        elif self.operator.type == TT_MODULO:
            # if operation is binary
            if len(self.args) == 2:
                # if arguments are numbers
                if self.all_satisfies(self.is_number):
                    # if any are float, do floating point division
                    # else do integer division
                    if self.any_of(TT_FLOAT):
                        return Token(TT_FLOAT, self.args[0].value % self.args[1].value), None
                    return Token(TT_INT, self.args[0].value % self.args[1].value), None
        elif self.operator.type == TT_AND:
            # if operator is binary
            if len(self.args) == 2:
                # if arguments are booleans
                if self.all_of(TT_BOOL):
                    if self.args[0].value == 'TRUE' and self.args[1].value == 'TRUE':
                        return Token(TT_BOOL, 'TRUE'), None
                    return Token(TT_BOOL, 'FALSE'), None
        elif self.operator.type == TT_OR:
            # if operator is binary
            if len(self.args) == 2:
                # if arguments are booleans
                if self.all_of(TT_BOOL):
                    if self.args[0].value == 'TRUE' or self.args[1].value == 'TRUE':
                        return Token(TT_BOOL, 'TRUE'), None
                    return Token(TT_BOOL, 'FALSE'), None
        elif self.operator.type == TT_NOT:
            # if operator is unary
            if len(self.args) == 1:
                if self.all_of(TT_BOOL):
                    if self.args[0].value == 'TRUE':
                        return Token(TT_BOOL, 'FALSE'), None
                    return Token(TT_BOOL, 'TRUE'), None
        elif self.operator.type == TT_GREATER:
            # if operator is binary
            if len(self.args) == 2:
                if self.all_satisfies(self.is_number):
                    if self.args[0].value > self.args[1].value:
                        return Token(TT_BOOL, 'TRUE'), None
                    return Token(TT_BOOL, 'FALSE'), None
        elif self.operator.type == TT_LESS:
            # if operator is binary
            if len(self.args) == 2:
                if self.all_satisfies(self.is_number):
                    if self.args[0].value < self.args[1].value:
                        return Token(TT_BOOL, 'TRUE'), None
                    return Token(TT_BOOL, 'FALSE'), None
        elif self.operator.type == TT_GREATER_EQUALS:
            # if operator is binary
            if len(self.args) == 2:
                if self.all_satisfies(self.is_number):
                    if self.args[0].value >= self.args[1].value:
                        return Token(TT_BOOL, 'TRUE'), None
                    return Token(TT_BOOL, 'FALSE'), None
        elif self.operator.type == TT_LESS_EQUALS:
            # if operator is binary
            if len(self.args) == 2:
                if self.all_satisfies(self.is_number):
                    if self.args[0].value <= self.args[1].value:
                        return Token(TT_BOOL, 'TRUE'), None
                    return Token(TT_BOOL, 'FALSE'), None
        elif self.operator.type == TT_EQUALS:
            # if operator is binary
            if len(self.args) == 2:
                if self.all_satisfies(self.is_number) or self.all_of(TT_BOOL):
                    if self.args[0].value == self.args[1].value:
                        return Token(TT_BOOL, 'TRUE'), None
                    return Token(TT_BOOL, 'FALSE'), None
        elif self.operator.type == TT_NOT_EQUALS:
            # if operator is binary
            if len(self.args) == 2:
                if self.all_satisfies(self.is_number) or self.all_of(TT_BOOL):
                    if self.args[0].value != self.args[1].value:
                        return Token(TT_BOOL, 'TRUE'), None
                    return Token(TT_BOOL, 'FALSE'), None
        elif self.operator.type == TT_ARRAY_ACCESS:
            print('hi')
            # if operator is binary
            if len(self.args) == 2:
                # if arguments are array and int
                if self.args[0].type == TT_ARRAY and self.args[1].type == TT_INT:
                    # if index is not in range
                    if len(self.args[0].value) <= self.args[1].value or self.args[1].value < 0:
                        return None, RuntimeError('Array index out of bounds')
                    # return value at index
                    return self.args[0].value[self.args[1].value], None
        elif self.operator.type == TT_UNARY_MINUS:
            # if operator is unary
            if len(self.args) == 1:
                if self.all_satisfies(self.is_number):
                    return Token(self.args[0].type, -self.args[0].value), None
        return None, RuntimeError('No such operator')

    # returns true if token is a number
    def is_number(self, token):
        return token.type == TT_INT or token.type == TT_FLOAT

    # returns true if all arguments are of given type
    def all_of(self, type):
        return all([operand.type == type for operand in self.args])

    # returns true if all arguments return true when called with function
    def all_satisfies(self, function):
        return all([function(operand) for operand in self.args])

    # returns true if any arguments are of given type
    def any_of(self, type):
        return any([operand.type == type for operand in self.args])

    # returns true if any arguments return true when called with function
    def any_satisfies(self, function):
        return any([function(operand) for operand in self.args])

# Context

# stores information about the scope of a block
# like the current variable cache and the parent blocks 
class Context:
    def __init__(self, parent):
        self.parent = parent
        self.variable_cache = dict()
        self.function_cache = dict() # name -> (args, src)

    # for debugging
    def __repr__(self):
        return str([str(self.variable_cache), str(self.function_cache)])

    # adds a variable to the current variable cache
    def add_var(self, name, value):
        # see if any variable with same name exists
        cur_context = self
        while cur_context != None:
            if name in cur_context.variable_cache:
                return RuntimeError('Variable ' + name + ' already exists')
            cur_context = cur_context.parent
        # assign to current variable cache if not
        self.variable_cache[name] = value

    # sets the value of a variable
    def set_var(self, name, value):
        # checks if variable exists
        cur_context = self
        while cur_context != None:
            # if this context contains the variable
            if name in cur_context.variable_cache:
                # update in sepearate context
                cur_context.variable_cache[name] = value
                return None
            cur_context = cur_context.parent
        # if not throw an error
        return RuntimeError('Variable ' + name + ' doesn\'t exist')
    
    # gets the value of a variable with name
    def get_var(self, name):
        # checks if variable exists
        cur_context = self
        while cur_context != None:
            # if this context contains the variable
            if name in cur_context.variable_cache:
                # return it
                return cur_context.variable_cache[name], None
            cur_context = cur_context.parent
        # if not throw an error
        return None, RuntimeError('Variable ' + name + ' doesn\'t exist')
    
    # add function with name, arguments, source code
    def add_function(self, name, args, src):
        cur_context = self
        # check duplicate names
        while cur_context != None:
            if name in cur_context.function_cache:
                return RuntimeError('Function ' + name + ' already exists')
            cur_context = cur_context.parent
        # add tuple of function info (string array, string array)
        self.function_cache[name] = (args, src)

    # get arguments and source code of function with name
    # returns (string array, string array) = (arguments, code lines)
    def get_function(self, name):
        cur_context = self
        # find function if it exists
        while cur_context != None:
            if name in cur_context.function_cache:
                # return tuple
                return cur_context.function_cache[name][0], cur_context.function_cache[name][1], None
            cur_context = cur_context.parent
        return None, None, RuntimeError('Function ' + name + ' doesn\'t exist')

# Variable Constants

CONSTANTS = {
    'TRUE': Token(TT_BOOL, 'TRUE'),
    'FALSE': Token(TT_BOOL, 'FALSE'),
    'UNDEFINED': Token(TT_UNDEFINED, 'UNDEFINED'),
    'ARRAY': Token(TT_ARRAY, [])
}

OPERATORS = [
    TT_ADD,
    TT_SUBTRACT,
    TT_MULTIPLY,
    TT_DIVIDE,
    TT_MODULO,
    TT_AND,
    TT_OR,
    TT_NOT,
    TT_GREATER,
    TT_LESS,
    TT_GREATER_EQUALS,
    TT_LESS_EQUALS,
    TT_EQUALS,
    TT_NOT_EQUALS,
    TT_ARRAY_ACCESS,
    TT_UNARY_MINUS,
]

DATA_TYPES = [
    TT_INT,
    TT_FLOAT,
    TT_BOOL,
    TT_ARRAY,
    TT_CHAR,
    TT_UNDEFINED
]

# stores names of built-in functions
FUNCTION_CONSTANTS = [
    FUNCTION_POP,
    FUNCTION_PUSH,
    FUNCTION_REPLACE,
    FUNCTION_SUBARR,
    FUNCTION_PUTCHAR,
    FUNCTION_ARRAYOF,
    FUNCTION_GETLENGTH,
    FUNCTION_INPUT
]