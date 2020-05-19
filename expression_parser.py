from basic import *

class UnaryConstants:
    CANCEL_OUT = 'CANCEL_OUT'
    ERROR = 'ERROR'

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = -1
        self.advance()
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.cur_token = self.tokens[self.pos]
        else:
            self.cur_token = None

    def recurse(self):
        # resets position to start
        def reset():
            self.pos = start - 1
            self.advance() # load current token

        start = self.pos # stores starting point
        # do all parenthesis operations first
        while self.cur_token != None:
            if self.cur_token.type == TT_LPAREN:
                self.advance()
                val, error = self.recurse()
                if error != None:
                    return None, error
                self.tokens.pop(self.pos) # pop the left parenthesis character
                self.tokens.insert(self.pos, val) # insert result of parenthesis
                self.pos -= 1
            elif self.cur_token.type == TT_RPAREN:
                # this case should never happen since each left parenthesis
                # will get rid of its own right parenthesis
                break
            self.advance()

        # do array append and access operation
        reset()
        error = self.evaluate_for_binary([TT_ARRAY_APPEND, TT_ARRAY_ACCESS])
        if error != None:
            return None, error

        # do unary NOT operation
        reset()
        error = self.evaluate_for_unary([TT_NOT], UnaryConstants.CANCEL_OUT)
        if error != None:
            return None, error

        # do unary GETLENGTH operation
        reset()
        error = self.evaluate_for_unary([TT_ARRAY_GETLENGTH], UnaryConstants.ERROR)
        if error != None:
            return None, error

        # do multiply and divide operations
        reset()
        error = self.evaluate_for_binary([TT_MULTIPLY, TT_DIVIDE, TT_MODULO])
        if error != None:
            return None, error

        # do add and subtract operations
        reset()
        error = self.evaluate_for_binary([TT_ADD, TT_SUBTRACT])
        if error != None:
            return None, error

        # do all comparison operations
        reset()
        error = self.evaluate_for_binary([TT_GREATER, TT_LESS, TT_GREATER_EQUALS, TT_LESS_EQUALS, TT_EQUALS, TT_NOT_EQUALS])
        if error != None:
            return None, error

        # do AND and OR operations
        reset()
        error = self.evaluate_for_binary([TT_AND, TT_OR])
        if error != None:
            return None, error

        # check for right parenthesis
        reset()
        last = None
        lastOp = None
        while self.cur_token != None:
            if self.is_data_type(self.cur_token):
                last = self.cur_token # store value in case of closing parenthesis
            elif self.cur_token.type == TT_RPAREN:
                # if current expression inside parenthesis
                # pop every item of current expression and leave pointer at 
                # left parenthesis (start - 1)
                while self.pos - start >= 0:
                    self.tokens.pop(self.pos)
                    self.pos -= 1 # ends at left parenthesis
                return last, None
            self.advance()

        # is there is an unevaluated operator
        if lastOp != None or last == None:
            return None, RuntimeError('Unexpected end of statement')

        # if type of answer is not a data type
        # probably impossible
        if not self.is_data_type(last):
            return None, RuntimeError('Not a statement')
        return last,  None

    def evaluate_for_binary(self, operators):
        last = None
        lastOp = None
        while self.cur_token != None:
            # if is current char is an operator
            if self.is_operator(self.cur_token):
                lastOp = self.cur_token
            elif self.is_data_type(self.cur_token):
                # if there is no operator
                if lastOp == None:
                    last = self.cur_token
                elif lastOp.type in operators:
                    # if operator is add or subtract
                    last, error = self.eval_binary(last, lastOp, self.cur_token)
                    if error != None:
                        return error
                    # pop two operands and one operator
                    # [operand, operator, operand] -> []
                    for i in range(3):
                        self.tokens.pop(self.pos)
                        self.pos -= 1
                    # self.pos now one below insert position because of last "self.pos - 1"
                    self.tokens.insert(self.pos + 1, last)
                else:
                    last = self.cur_token
                lastOp = None
            elif self.cur_token.type == TT_RPAREN:
                break
            else:
                return RuntimeError(self.cur_token)
            self.advance()

    # assumes two operations in a row cancel eachother out
    # and left to right associativity
    def evaluate_for_unary(self, operators, stack_mode=UnaryConstants.CANCEL_OUT):
        last = None
        lastOp =  None
        while self.cur_token != None:
            if self.is_operator(self.cur_token):
                # if there is a previous NOT, remove both since NOT cancels itself
                if self.cur_token.type in operators and lastOp != None and lastOp.type in operators:
                    if stack_mode == UnaryConstants.CANCEL_OUT:
                        # [operator, operand] -> []
                        for i in range(2):
                            self.tokens.pop(self.pos)
                            self.pos -= 1
                        lastOp = None
                    elif stack_mode == UnaryConstants.ERROR:
                        return RuntimeError(str(self.cur_token.type) + ' cannot be chained')
                else:
                    lastOp = self.cur_token
            elif self.is_data_type(self.cur_token):
                # if current character is first
                if lastOp == None:
                    last = self.cur_token
                elif lastOp.type in operators:
                    # if last operator was unary NOT
                    last, error = self.eval_unary(lastOp, self.cur_token)
                    if error != None:
                        return error
                    # pop two operands and one operator
                    # [operator, operand] -> []
                    for i in range(2):
                        self.tokens.pop(self.pos)
                        self.pos -= 1
                    # self.pos now one below insert position because of last "self.pos - 1"
                    self.tokens.insert(self.pos + 1, last)
                    # don't need to increment self.pos since while loop will increment it
                else:
                    # if operation was addition or subtraction
                    # takes this number as the new starting candidate
                    last = self.cur_token
                # reset operator
                lastOp = None
            elif self.cur_token.type == TT_RPAREN:
                # if current expression is inside parenthesis
                break
            else:
                return RuntimeError(self.cur_token)
            self.advance()

    # returns true if token is operator
    def is_operator(self, token):
        return token.type in OPERATORS

    # returns true if token is data type
    def is_data_type(self, token):
        return token.type == TT_INT or token.type == TT_FLOAT or token.type == TT_BOOL\
        or token.type == TT_UNDEFINED or token.type == TT_ARRAY
    
    # performs and returns result of binary operation
    def eval_binary(self, left, operation, right):
        op = Operation(operation, [left, right])
        res, error = op.eval()
        if error != None:
            return None, error
        return res, None

    # performs and returns result of unary operation
    def eval_unary(self, operation, operand):
        op = Operation(operation, [operand])
        res, error = op.eval()
        if error != None:
            return None, error
        return res, None