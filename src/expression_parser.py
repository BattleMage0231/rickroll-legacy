from enum import Enum

from basic import *

TT_HEAD = 'HEAD'
TT_TAIL = 'TAIL'

class UnaryConstants(Enum):
    """Constants for how to handle chained unary operators"""
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
        left = str(self.left.get_token())
        this = str(self.get_token())
        right = str(self.right.get_token())
        return 'Node: ' + left + ' --> ' + this + ' --> ' + right
    def get_token(self):
        """Gets the token inside of the node"""
        return self.token
    def pop(self):
        """Marks current node as no longer existing"""
        self.exists = False

OPERATOR_PRECEDENCE = [
    (1, [TT_UNARY_MINUS], UnaryConstants.CANCEL_OUT),
    (2, [TT_ARRAY_ACCESS], None),
    (1, [TT_NOT], UnaryConstants.CANCEL_OUT),
    (2, [TT_MULTIPLY, TT_DIVIDE, TT_MODULO], None),
    (2, [TT_ADD, TT_SUBTRACT], None),
    (2, [TT_GREATER, TT_LESS, TT_GREATER_EQUALS, TT_LESS_EQUALS, TT_EQUALS, TT_NOT_EQUALS], None),
    (2, [TT_AND], None),
    (2, [TT_OR], None)
]

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
        """Sets pointer to head"""
        self.pos = self.head
    def traverse_from_tail(self):
        """Sets pointer to tail"""
        self.pos = self.head
    def traverse_from(self, node):
        """
        Sets pointer to given node.
        Does not check whether node is in expression.
        """
        self.pos = node
    def get_cur_token(self):
        """Gets the token being pointed to"""
        return self.pos.get_token()
    def traverse_left(self):
        """Traverses left by one"""
        self.pos = self.pos.left
    def traverse_right(self):
        """Traverses right by one"""
        self.pos = self.pos.right
    def pop_current_node(self):
        """Pops current node and shifts pointer to node to the right"""
        # program should never pop the
        # head or tail of the expression
        if self.pos.type == TT_HEAD or self.pos.type == TT_TAIL:
            raise IndexError('Bad pop on head or tail')
        self.pos.left.right = self.pos.right # change left node's right node
        self.pos.pop() # set current node to popped
        self.pos = self.pos.right # change node to right node
        self.pos.left = self.pos.left.left # change left node to left node's left node
    def insert_at_current(self, token):
        """
        Inserts node at current position and shifts pointer to inserted node.
        Shifts all nodes including current node to the right by one.
        """
        token_node = Expression.make_node(token)
        if self.pos.type == TT_HEAD:
            # interpreter should never try to insert on head
            # raising internal error since user should never have access to this
            raise IndexError('Bad insert on head')
        self.pos.left.right = token_node # change left node's right node to node to insert
        token_node.left = self.pos.left # change node to insert's left node
        self.pos.left = token_node # change current node to insert
        token_node.right = self.pos # change insert's right node to current node
        self.pos = token_node # change position to insert
    @staticmethod
    def make_node(token):
        """Makes a TokenNode from a Token"""
        return TokenNode(token.type, token.value)

class Parser:
    def __init__(self, tokens):
        self.expression = Expression(tokens) # make expression
        self.expression.traverse_right() # get first character (starts at head)
        self.cur_token = self.expression.get_cur_token() # cur_token stores Token
        self.cur_node = self.expression.pos # cur_node stores TokenNode
        self.start_stack = [] # stack of recursive indexes
    def update(self):
        """Updates cur_token and cur_node"""
        self.cur_token = self.expression.get_cur_token()
        self.cur_node = self.expression.pos
    def pop(self):
        """Pops current position and updates values"""
        # if popping current start position, move start position to the right
        if self.cur_node == self.start_stack[-1]:
            self.start_stack[-1] = self.start_stack[-1].right
        # pop and update
        self.expression.pop_current_node()
        self.update()
    def insert(self, token):
        """Inserts token at current position and updates values"""
        is_start = self.cur_node == self.start_stack[-1] # whether current node is start
        # insert and update
        self.expression.insert_at_current(token)
        self.update()
        # if node was inserted before start, update start to be node
        if is_start:
            self.start_stack[-1] = self.start_stack[-1].left
    def advance(self):
        """Traverses right by one"""
        # traverse and update
        self.expression.traverse_right()
        self.update()
    def reset(self):
        """Reset to starting position"""
        self.expression.traverse_from(self.start_stack[-1])
        self.update()
    def recurse(self):
        """Evaluates an expression or a part of an expression"""
        self.start_stack.append(self.cur_node) # stores starting point
        # do all parenthesis operations first
        while self.cur_node != self.expression.tail:
            if self.cur_token.type == TT_LPAREN:
                self.advance()
                val, error = self.recurse()
                if error is not None:
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
        for arg_count, operators, chain_type in OPERATOR_PRECEDENCE:
            self.reset()
            if arg_count == 1:
                error = self.evaluate_for_unary(operators, chain_type)
                if error is not None:
                    self.start_stack.pop()
                    return None, error
            elif arg_count == 2:
                error = self.evaluate_for_binary(operators)
                if error is not None:
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
        if last is None:
            self.start_stack.pop()
            return None, RuntimeError('Unexpected end of statement')
        # if type of answer is not a data type
        # probably impossible
        if not self.is_data_type(last):
            self.start_stack.pop()
            return None, RuntimeError('Not a statement')
        self.start_stack.pop()
        return last, None
    def evaluate_for_binary(self, operators):
        """Evaluates a group of binary operators from left to right"""
        last = None
        last_op = None
        while self.cur_node != self.expression.tail:
            # if is current char is an operator
            if self.is_operator(self.cur_token):
                last_op = self.cur_token
            elif self.is_data_type(self.cur_token):
                # if there is no operator
                if last_op is None:
                    last = self.cur_token
                elif last_op.type in operators:
                    # if operator is add or subtract
                    last, error = self.eval_binary(last, last_op, self.cur_token)
                    if error is not None:
                        return error
                    # pop two operands and one operator
                    # [operand, operator, operand] -> []
                    for _ in range(3):
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
                last_op = None
            elif self.cur_token.type == TT_RPAREN:
                break
            else:
                return IllegalArgumentError(str(self.cur_token) + ' not a token')
            self.advance()
        if last_op is not None:
            return IllegalArgumentError('Expected argument for operator ' + str(last_op))
    # assumes two operations in a row cancel eachother out
    # and left to right associativity
    def evaluate_for_unary(self, operators, stack_mode=UnaryConstants.CANCEL_OUT):
        """Evaluates a group of unary operators from left to right."""
        last = None
        last_op = None
        while self.cur_node != self.expression.tail:
            if self.is_operator(self.cur_token):
                is_valid_operator = self.cur_token.type in operators
                last_valid_operator = (last_op is not None and last_op.type in operators)
                # if there is a previous NOT, remove both since NOT cancels itself
                if is_valid_operator and last_valid_operator:
                    if stack_mode == UnaryConstants.CANCEL_OUT:
                        # [operator, operand] -> []
                        for _ in range(2):
                            self.pop()
                            self.expression.traverse_left()
                            self.update()
                        last_op = None
                    elif stack_mode == UnaryConstants.ERROR:
                        return RuntimeError(str(self.cur_token.type) + ' cannot be chained')
                else:
                    last_op = self.cur_token
            elif self.is_data_type(self.cur_token):
                # if current character is first
                if last_op is None:
                    last = self.cur_token
                elif last_op.type in operators:
                    # if last operator was unary NOT
                    last, error = self.eval_unary(last_op, self.cur_token)
                    if error:
                        return error
                    # pop two operands and one operator
                    # [operator, operand] -> []
                    for _ in range(2):
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
                last_op = None
            elif self.cur_token.type == TT_RPAREN:
                # if current expression is inside parenthesis
                break
            else:
                return IllegalArgumentError(str(self.cur_token) + ' not a token')
            self.advance()
        if last_op is not None:
            return IllegalArgumentError('Expected argument for operator ' + str(last_op))
    def is_operator(self, token):
        """Returns true if token is operator"""
        return token.type in OPERATORS
    def is_data_type(self, token):
        """Returns true if token is data type"""
        return token.type in DATA_TYPES
    def eval_binary(self, left, operation, right):
        """Performs and returns result of binary operation"""
        res, error = Operation(operation, [left, right]).eval()
        return (None, error) if error else (res, None)
    def eval_unary(self, operation, operand):
        """Performs and returns result of unary operation"""
        res, error = Operation(operation, [operand]).eval()
        return (None, error) if error else (res, None)
