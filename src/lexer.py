import re

from basic import *

SPECIAL_CHARACTERS = '&|<>=:#'

class Lexer:
    def __init__(self, text, context):
        self.text = text
        self.context = context
        self.pos = -1
        self.cur_char = None
        self.advance()
    
    # advances the pointer one step
    def advance(self):
        self.pos += 1
        # if position is valid
        self.cur_char = self.text[self.pos] if self.pos < len(self.text) else None

    def make_tokens(self):
        tokens = [] 
        parenthesis_balance = 0
        # handles case where text is empty
        if len(self.text.strip()) == 0: 
            return None, IllegalCharError('Unexpected end of statement')
        # while there is still more text to parse
        while self.cur_char != None:
            # if current character is a digit
            if self.cur_char.isdigit():
                number, error = self.make_number()
                if error:
                    return None, error
                tokens.append(number)
                continue
            # if current character is in the alphabet (part of variable name)
            if self.cur_char.isalpha():
                var, error = self.make_variable()
                if error:
                    return None, error
                tokens.append(var)
                continue
            # if current character could be the start of a complex operator
            if self.cur_char in SPECIAL_CHARACTERS:
                op, error = self.make_operator()
                if error:
                    return None, error
                # if there is an operator
                # even amounts of unary NOT will cancel eachother out
                if op:
                    tokens.append(op)
                continue
            # if character is start of a char variable
            if self.cur_char == '\'':
                self.advance()
                char = self.cur_char
                # if current char is another quote, there is nothing in the middle
                # thus make an empty character
                if char == '\'':
                    char = ''
                    tokens.append(Token(TT_CHAR, char))
                    self.advance()
                    continue
                elif char == '\\':
                    # otherwise if there is an escape character, read the next one instead
                    self.advance()
                    if self.cur_char == 'n':
                        char = '\n'
                    else:
                        char = self.cur_char
                self.advance()
                # if no ending quote found
                if self.cur_char != '\'':
                    return None, SyntaxError('Unbalanced char quotations')
                # append char
                tokens.append(Token(TT_CHAR, char))
                self.advance()
                continue
            if self.cur_char == '+':
                tokens.append(Token(TT_ADD))
            elif self.cur_char == '-':
                # if current character is first character or last token
                # was not int or float
                if len(tokens) == 0 or (tokens[-1].type != TT_INT and tokens[-1].type != TT_FLOAT):
                    tokens.append(Token(TT_UNARY_MINUS))
                else:
                    tokens.append(Token(TT_SUBTRACT))
            elif self.cur_char == '*':
                tokens.append(Token(TT_MULTIPLY))
            elif self.cur_char == '/':
                tokens.append(Token(TT_DIVIDE)) 
            elif self.cur_char == '%':
                tokens.append(Token(TT_MODULO))
            elif self.cur_char == '(':
                tokens.append(Token(TT_LPAREN)) 
                parenthesis_balance += 1
            elif self.cur_char == ')':
                tokens.append(Token(TT_RPAREN)) 
                parenthesis_balance -= 1
                # checks parenthesis balance
                if parenthesis_balance < 0:
                    return None, IllegalCharError('Unbalanced parenthesis')
            elif self.cur_char == '!':
                tokens.append(Token(TT_NOT))
            elif self.cur_char.isspace():
                pass
            else:
                # invalid character
                return None, IllegalCharError('\'' + self.cur_char + '\'')
            self.advance()
        if parenthesis_balance != 0:
            return None, IllegalCharError('Unbalanced parenthesis')
        return tokens, None

    # parses a number
    def make_number(self):
        num = 0 # stores the number
        is_float = False
        decimal_digits = 0
        # while there is more text to parse and the current char is number or decimal
        while self.cur_char != None and self.cur_char.isdigit() or self.cur_char == '.':
            # if current char is decimal point
            if self.cur_char == '.':
                # if there was already a decimal point
                if is_float:
                    return None, IllegalCharError('\'.\'')
                decimal_digits = 1
                is_float = True
                self.advance() 
                continue # skip to next iteration
            # if is decimal, add to decimal places instead
            if is_float:
                num += int(self.cur_char) / (10 ** decimal_digits)
                decimal_digits += 1
            else:
                # else add normally
                num *= 10
                num += int(self.cur_char)
            self.advance()
        # assign type to token
        return Token((TT_FLOAT if is_float else TT_INT), num), None

    # parses a variable name
    def make_variable(self):
        name = ''
        # while character exists and is still alphanumeric
        while self.cur_char != None and (self.cur_char.isalpha() or self.cur_char == '_'):
            name += self.cur_char
            self.advance()
        # if name is a language constant
        if name in CONSTANTS:
            return CONSTANTS[name], None
        # if variable exists
        # look for it in context
        cur_context = self.context
        while cur_context:
            # if variable exists in this context, return it
            if name in cur_context.variable_cache:
                return cur_context.variable_cache[name], None
            cur_context = cur_context.parent
        # otherwise variable was not found
        return None, RuntimeError('Variable ' + name + ' not found')

    # parses complex operators (non-binary, multiple characters, etc)
    def make_operator(self):
        operator = ''
        while self.cur_char != None and self.cur_char in SPECIAL_CHARACTERS:
            operator += self.cur_char
            self.advance()
        if operator == '&&':
            return Token(TT_AND), None
        if operator == '||':
            return Token(TT_OR), None
        if operator == '!':
            return Token(TT_NOT), None
        if operator == '>':
            return Token(TT_GREATER), None
        if operator == '<':
            return Token(TT_LESS), None
        if operator == '>=':
            return Token(TT_GREATER_EQUALS), None
        if operator == '<=':
            return Token(TT_LESS_EQUALS), None
        if operator == '==':
            return Token(TT_EQUALS), None
        if operator == '!=':
            return Token(TT_NOT_EQUALS), None
        if operator == ':':
            return Token(TT_ARRAY_ACCESS), None
        return None, RuntimeError('Operator ' + operator + ' not found')
