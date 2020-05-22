from basic import *

TT_HEAD = 'HEAD'
TT_TAIL = 'TAIL'

class UnaryConstants:
    # constants for how to handle chained unary operators
    CANCEL_OUT = 'CANCEL_OUT'
    ERROR = 'ERROR'

# expression is stored as a linkedlist since
# all traversals start from the head and
# elements are removed in O(1)
class TokenNode:
    def __init__(self, token_type, value=None):
        self.token = Token(token_type, value)
        self.type = token_type
        self.value = value
        self.left = None
        self.right = None
        self.exists = True

    def __repr__(self):
        return 'Node: ' + str(self.left.get_token()) + ' --> ' + str(self.get_token()) + ' --> ' + str(self.right.get_token())

    def get_token(self):
        return self.token

    def pop(self):
        self.exists = False

class Expression:
    def __init__(self, tokens):
        self.head = TokenNode(TT_HEAD)
        self.head.left = self.head
        cur_node = self.head
        for token in tokens:
            node = Expression.make_node(token)
            cur_node.right = node
            node.left = cur_node
            cur_node = node
        self.tail = TokenNode(TT_TAIL)
        self.tail.left = cur_node
        cur_node.right = self.tail
        self.tail.right = self.tail
        self.pos = self.head

    def __repr__(self):
        cur_node = self.head.right
        res = ''
        while cur_node != self.tail:
            res += ' --> ' + str(cur_node.get_token())
            cur_node = cur_node.right
        return res

    def traverse_from_head(self):
        self.pos = self.head

    def traverse_from_tail(self):
        self.pos = self.head

    def traverse_from(self, node):
        self.pos = node

    def get_cur_token(self):
        return self.pos.get_token()

    def traverse_left(self):
        self.pos = self.pos.left

    def traverse_right(self):
        self.pos = self.pos.right

    def pop_current_node(self):
        if self.pos.type == TT_HEAD or self.pos.type == TT_TAIL:
            pass
        else:
            self.pos.left.right = self.pos.right
            self.pos.pop()
            self.pos = self.pos.right
            self.pos.left = self.pos.left.left
            
    def insert_at_current(self, token):
        token_node = Expression.make_node(token)
        if self.pos.type == TT_HEAD:
            pass
        else:
            self.pos.left.right = token_node
            token_node.left = self.pos.left
            self.pos.left = token_node
            token_node.right = self.pos
            self.pos = token_node

    @staticmethod
    def make_node(token):
        return TokenNode(token.type, token.value)

class Parser:
    def __init__(self, tokens):
        self.expression = Expression(tokens)
        self.expression.traverse_right()
        self.cur_token = self.expression.get_cur_token()
        self.cur_node = self.expression.pos
        self.start_stack = []

    ### TODO handle case where start gets popped

    def update(self):
        self.cur_token = self.expression.get_cur_token()
        self.cur_node = self.expression.pos

    def pop(self):
        if self.cur_node == self.start_stack[-1]:
            self.start_stack[-1] = self.start_stack[-1].right
        self.expression.pop_current_node()
        self.update()

    def insert(self, token):
        is_start = self.cur_node == self.start_stack[-1]
        self.expression.insert_at_current(token)
        self.update()
        if is_start:
            self.start_stack[-1] = self.start_stack[-1].left

    def advance(self):
        self.expression.traverse_right()
        self.update()

    def reset(self):
        self.expression.traverse_from(self.start_stack[-1])
        self.update()

    def recurse(self):
        self.start_stack.append(self.cur_node) # stores starting point
        # do all parenthesis operations first
        while self.cur_node != self.expression.tail:
            if self.cur_token.type == TT_LPAREN:
                self.advance()
                val, error = self.recurse()
                if error != None:
                    self.start_stack.pop()
                    return None, error
                self.pop()
                self.insert(val)
                self.expression.traverse_left()
                self.update()
            elif self.cur_token.type == TT_RPAREN:
                # this case should never happen since each left parenthesis
                # will get rid of its own right parenthesis
                break
            self.advance()

        # do array access operation
        self.reset()
        error = self.evaluate_for_binary([TT_ARRAY_ACCESS])
        if error != None:
            self.start_stack.pop()
            return None, error

        # do unary NOT operation
        self.reset()
        error = self.evaluate_for_unary([TT_NOT], UnaryConstants.CANCEL_OUT)
        if error != None:
            self.start_stack.pop()
            return None, error

        # do multiply and divide operations
        self.reset()
        error = self.evaluate_for_binary([TT_MULTIPLY, TT_DIVIDE, TT_MODULO])
        if error != None:
            self.start_stack.pop()
            return None, error

        # do add and subtract operations
        self.reset()
        error = self.evaluate_for_binary([TT_ADD, TT_SUBTRACT])
        if error != None:
            self.start_stack.pop()
            return None, error

        # do all comparison operations
        self.reset()
        error = self.evaluate_for_binary([TT_GREATER, TT_LESS, TT_GREATER_EQUALS, TT_LESS_EQUALS, TT_EQUALS, TT_NOT_EQUALS])
        if error != None:
            self.start_stack.pop()
            return None, error

        # do AND and OR operations
        self.reset()
        error = self.evaluate_for_binary([TT_AND, TT_OR])
        if error != None:
            self.start_stack.pop()
            return None, error

        # check for right parenthesis
        self.reset()
        last = None
        lastOp = None
        while self.cur_node != self.expression.tail:
            if self.is_data_type(self.cur_token):
                last = self.cur_token # store value in case of closing parenthesis
            elif self.cur_token.type == TT_RPAREN:
                # if current expression inside parenthesis
                # pop every item of current expression and leave pointer at 
                # left parenthesis (start - 1)
                while self.cur_node != self.start_stack[-1]:
                    self.pop()
                    self.expression.traverse_left()
                    self.update()
                self.pop()
                self.expression.traverse_left()
                self.update()
                self.start_stack.pop()
                return last, None
            self.advance()

        # is there is an unevaluated operator
        if lastOp != None or last == None:
            self.start_stack.pop()
            return None, RuntimeError('Unexpected end of statement')

        # if type of answer is not a data type
        # probably impossible
        if not self.is_data_type(last):
            self.start_stack.pop()
            return None, RuntimeError('Not a statement')
        self.start_stack.pop()
        return last,  None

    # evaluate for binary operators
    def evaluate_for_binary(self, operators):
        last = None
        lastOp = None
        while self.cur_node != self.expression.tail:
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
                        self.pop()
                        self.expression.traverse_left()
                        self.update()
                    # self.pos now one below insert position because of last "self.pos - 1"
                    self.expression.traverse_right()
                    self.update()
                    self.insert(last)
                    self.expression.traverse_left()
                    self.update()
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
        while self.cur_node != self.expression.tail:
            if self.is_operator(self.cur_token):
                # if there is a previous NOT, remove both since NOT cancels itself
                if self.cur_token.type in operators and lastOp != None and lastOp.type in operators:
                    if stack_mode == UnaryConstants.CANCEL_OUT:
                        # [operator, operand] -> []
                        for i in range(2):
                            self.pop()
                            self.expression.traverse_left()
                            self.update()
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
                        self.pop()
                        self.expression.traverse_left()
                        self.update()
                    # self.pos now one below insert position because of last "self.pos - 1"
                    self.expression.traverse_right()
                    self.update()
                    self.insert(last)
                    self.expression.traverse_left()
                    self.update()
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
        or token.type == TT_UNDEFINED or token.type == TT_ARRAY or token.type == TT_CHAR\
    
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