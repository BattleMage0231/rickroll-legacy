# Constants

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'

TT_BOOL = 'BOOL'

TT_ADD = 'ADD'
TT_SUBTRACT = 'SUBTRACT'
TT_MULTIPLY = 'MULTIPLY'
TT_DIVIDE = 'DIVIDE'

TT_AND = 'AND'
TT_OR = 'OR'
TT_NOT = 'NOT'

TT_GREATER = 'GREATER'
TT_LESS = 'LESS'
TT_GREATER_EQUALS = 'GREATER_EQUALS'
TT_LESS_EQUALS = 'LESS_EQUALS'
TT_EQUALS = 'EQUALS'

TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

TT_UNDEFINED = 'UNDEFINED'

# Error

class Error:
    def __init__(self, name, details):
        self.name = name
        self.details = details

    def as_string(self):
        result = str(self.name) + ': ' + str(self.details)
        return result

class IllegalCharError(Error):
    def __init__(self, details):
        super().__init__('Illegal Character', details)

class RuntimeError(Error):
    def __init__(self, details):
        super().__init__('Runtime Error', details)

class IllegalArgumentError(Error):
    def __init__(self, details):
        super().__init__('Illegal Argument', details)

class SyntaxError(Error):
    def __init__(self, details):
        super().__init__('Syntax Error', details)

# Token

class Token:
    def __init__(self, token_type, value=None):
        self.type = token_type
        self.value = value
    
    def __repr__(self):
        # if token has value, return with value
        # else return type only
        if self.value != None:
            return str(self.type) + ': ' + str(self.value)
        return str(self.type)

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

# Variable Constants

CONSTANTS = {
    'TRUE': Token(TT_BOOL, 'TRUE'),
    'FALSE': Token(TT_BOOL, 'FALSE')
}

OPERATORS = {
    TT_ADD,
    TT_SUBTRACT,
    TT_MULTIPLY,
    TT_DIVIDE,
    TT_AND,
    TT_OR,
    TT_NOT,
    TT_GREATER,
    TT_LESS,
    TT_GREATER_EQUALS,
    TT_LESS_EQUALS,
    TT_EQUALS
}
