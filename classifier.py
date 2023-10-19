#!/usr/bin/env python3

from read_table import *
from checker import *
from colors import *
from displayer import *
from example import *
from lexer import *
from parser import *
from read_rules import *
from read_table import *
from rewriter import *

''' The CLASSIFIER allocates classes to tokens.
'''

token_test = [['SUR', '(', ['PARENTHESIS', 'open', 1], 0], ['STR', 'quid', ['variable', 4], 1], ['OP', '+', ['PLUS', 'binary', 'LR', 4], 2], ['STR', 'b', ['variable', 1], 3], ['OP', '- ', ['MINUS', 'binary', 'LR', 4], 4], ['SUR', '[', ['BRAKET', 'open', 2], 5], ['STR', 'c', ['variable', 1], 6], ['SUR', ']', ['BRAKET', 'close', 2], 7], ['SUR', ')', ['PARENTHESIS', 'close', 1], 8]]

class Token:
    def __init__(self,token):
        self.token = token

class Symbols(Token):
    def __init__(self,token):
        self.type=token[0]
        self.symbol=token[1]
        self.name=token[2][0]
        self.index=token[3]
        match self.type:
            case "SUR": Surrounders.__init__(self,token)
            case "OP" : Operators.__init__(self,token)
            case "STR": Strings.__init__(self,token)

class Surrounders(Symbols):
    def __init__(self,token):
        self.action=token[2][1]
        self.nestedness=token[2][2]

class Operators(Symbols):
    def __init__(self,token):
        self.arity=token[2][1]
        self.operands_direction=token[2][2]
        self.precedence=token[2][3]

class Meta(Symbols):
    def __init__(self,token):
        self.length=token[2][1]

class Strings(Symbols):
    def __init__(self,token):
        self.length=token[2][1]

print(Symbols(token_test[2]).precedence)
