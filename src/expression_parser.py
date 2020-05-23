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

    # for debugging
    def __repr__(self):
        return 'Node: ' + str(self.left.get_token()) + ' --> ' + str(self.get_token()) + ' --> ' + str(self.right.get_token())

    # getter for inner token
    def get_token(self):
        return self.token

    # mark node as no longer existing
    def pop(self):
        self.exists = False

class Expression:
    def __init__(self, tokens):
        self.head = TokenNode(TT_HEAD) # make head
        self.head.left = self.head # head loops into itself
        cur_node = self.head
        for token in tokens:
            node = Expression.make_node(token) # make node from token
            # assign right node of node to the left
            # and left node to this node
            cur_node.right = node
            node.left = cur_node
            cur_node = node
        self.tail = TokenNode(TT_TAIL) # make tail
        # tail attached to last node
        self.tail.left = cur_node 
        cur_node.right = self.tail 
        self.tail.right = self.tail # tail loops into itself
        # set initial position to head
        self.pos = self.head

    # for debugging
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

    # precondition: node exists or existed in the expression
    def traverse_from(self, node):
        self.pos = node

    def get_cur_token(self):
        return self.pos.get_token()

    def traverse_left(self):
        self.pos = self.pos.left

    def traverse_right(self):
        self.pos = self.pos.right

    # pops current node and shifts position to node to the right
    def pop_current_node(self):
        # program should never pop the 
        # head or tail of the expression
        if self.pos.type == TT_HEAD or self.pos.type == TT_TAIL:
            raise IndexError('Bad pop on head or tail')
        self.pos.left.right = self.pos.right # change left node's right node
        self.pos.pop() # set current node to popped
        self.pos = self.pos.right # change node to right node
        self.pos.left = self.pos.left.left # change left node to left node's left node
            
    # inserts token at current position, pushing everything including and to
    # the right of the current position to the right by one
    # shifts position to inserted node
    def insert_at_current(self, token):
        token_node = Expression.make_node(token)
        if self.pos.type == TT_HEAD:
            # should never insert on head
            raise IndexError('Bad insert on head')
        else:
            self.pos.left.right = token_node # change left node's right node to node to insert
            token_node.left = self.pos.left # change node to insert's left node
            self.pos.left = token_node # change current node to insert
            token_node.right = self.pos # change insert's right node to current node
            self.pos = token_node # change position to insert

    # makes node from token
    # tokennode is just a wrapper
    @staticmethod
    def make_node(token):
        return TokenNode(token.type, token.value)

class Parser:
    def __init__(self, tokens):
        self.expression = Expression(tokens) # make expression
        self.expression.traverse_right() # get first character (starts at head)
        self.cur_token = self.expression.get_cur_token() # cur_token stores Token
        self.cur_node = self.expression.pos # cur_node stores TokenNode
        self.start_stack = [] # stack of recursive indexes

    # updates cur_token and cur_node
    def update(self):
        self.cur_token = self.expression.get_cur_token() 
        self.cur_node = self.expression.pos

    # pops current position
    def pop(self):
        # if popping current start position, move start position to the right
        if self.cur_node == self.start_stack[-1]:
            self.start_stack[-1] = self.start_stack[-1].right
        # pop and update
        self.expression.pop_current_node()
        self.update()

    # inserts token at current position
    def insert(self, token):
        is_start = self.cur_node == self.start_stack[-1] # whether current node is start
        # insert and update
        self.expression.insert_at_current(token)
        self.update()
        # if node was inserted before start, update start to be node
        if is_start:
            self.start_stack[-1] = self.start_stack[-1].left

    def advance(self):
        # traverse and update
        self.expression.traverse_right()
        self.update()

    # reset from starting position
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
                if error:
                    self.start_stack.pop()
                    return None, error
                self.pop()
                self.insert(val)
                self.expression.traverse_left()
                self.update()
            elif self.cur_token.type == TT_RPAREN:
                # in case current expression is in parenthesis
                break
            self.advance()

        # do unary minus operation
        self.reset()
        error = self.evaluate_for_unary([TT_UNARY_MINUS], UnaryConstants.CANCEL_OUT)
        if error:
            self.start_stack.pop()
            return None, error

        # do array access operation
        self.reset()
        error = self.evaluate_for_binary([TT_ARRAY_ACCESS])
        if error:
            self.start_stack.pop()
            return None, error

        # do unary NOT operation
        self.reset()
        error = self.evaluate_for_unary([TT_NOT], UnaryConstants.CANCEL_OUT)
        if error:
            self.start_stack.pop()
            return None, error

        # do multiply and divide operations
        self.reset()
        error = self.evaluate_for_binary([TT_MULTIPLY, TT_DIVIDE, TT_MODULO])
        if error:
            self.start_stack.pop()
            return None, error

        # do add and subtract operations
        self.reset()
        error = self.evaluate_for_binary([TT_ADD, TT_SUBTRACT])
        if error:
            self.start_stack.pop()
            return None, error

        # do all comparison operations
        self.reset()
        error = self.evaluate_for_binary([TT_GREATER, TT_LESS, TT_GREATER_EQUALS, TT_LESS_EQUALS, TT_EQUALS, TT_NOT_EQUALS])
        if error:
            self.start_stack.pop()
            return None, error

        # do AND and OR operations
        self.reset()
        error = self.evaluate_for_binary([TT_AND, TT_OR])
        if error:
            self.start_stack.pop()
            return None, error

        # check for right parenthesis
        self.reset()
        last = None
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
        if not last:
            self.start_stack.pop()
            return None, RuntimeError('Unexpected end of statement')

        # if type of answer is not a data type
        # probably impossible
        if not self.is_data_type(last):
            self.start_stack.pop()
            return None, RuntimeError('Not a statement')
        self.start_stack.pop()
        return last, None

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
                if not lastOp:
                    last = self.cur_token
                elif lastOp.type in operators:
                    # if operator is add or subtract
                    last, error = self.eval_binary(last, lastOp, self.cur_token)
                    if error:
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
        if lastOp:
            return IllegalArgumentError('Expected argument for operator ' + str(lastOp))

    # assumes two operations in a row cancel eachother out
    # and left to right associativity
    def evaluate_for_unary(self, operators, stack_mode=UnaryConstants.CANCEL_OUT):
        last = None
        lastOp =  None
        while self.cur_node != self.expression.tail:
            if self.is_operator(self.cur_token):
                # if there is a previous NOT, remove both since NOT cancels itself
                if self.cur_token.type in operators and lastOp and lastOp.type in operators:
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
                if not lastOp:
                    last = self.cur_token
                elif lastOp.type in operators:
                    # if last operator was unary NOT
                    last, error = self.eval_unary(lastOp, self.cur_token)
                    if error:
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
        if lastOp:
            return IllegalArgumentError('Expected argument for operator ' + str(lastOp))

    # returns true if token is operator
    def is_operator(self, token):
        return token.type in OPERATORS

    # returns true if token is data type
    def is_data_type(self, token):
        return token.type in DATA_TYPES
    
    # performs and returns result of binary operation
    def eval_binary(self, left, operation, right):
        res, error = Operation(operation, [left, right]).eval()
        return (None, error) if error else (res, None)

    # performs and returns result of unary operation
    def eval_unary(self, operation, operand):
        res, error = Operation(operation, [operand]).eval()
        return (None, error) if error else (res, None)