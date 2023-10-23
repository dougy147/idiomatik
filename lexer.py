#!/usr/bin/env python3

#from parser import *
from read_table import *

''' The LEXER always takes a STRING as INPUT.
When the PARSER will communicate with the LEXER, it should transform TOKENS (LISTS) into STRINGS.
Vice versa, the PARSER only takes TOKENS (LISTS) as INPUT.

TOKENS have no TRUTH VALUE. It is the job of the PARSER to assess it.
'''

class Token:
    def __init__(self,category: str ="",symbol: str ="",prop: list = [""],index: int = 0):
        self.category = category
        self.symbol = symbol
        self.length_symbol = len(symbol)
        self.prop = prop
        self.index = index


def get_category(token): return token.category
def get_symbol(token): return token.symbol
def get_index(token): return token.index
def get_name(token): return token.name
def is_surrounder(token): return token.category == 'SUR'
def is_surrounder_open(token):
    if is_surrounder(token): return token.action == 'open'
    return False
def is_surrounder_close(token):
    if is_surrounder(token): return token.action == 'close'
    return False
def is_surrounder_wrap(token):
    if is_surrounder(token): return token.action == 'wrap'
    return False
def is_operator(token): return token.category == 'OP'
def is_operator_unary(token): return len(token.operands_place) == 1
def is_operator_binary(token): return len(token.operands_place) == 2
def is_operator_terary(token): return len(token.operands_place) == 3
def is_operator_prop_id(token): return token.name == 'PROP_ID'
def get_operator_operands_position(token): return token.operands_place
def get_operator_precedence(token):
    if is_operator(token): return token.precedence
    return False
def get_operands(token):
    if is_operator(token): return token.operands
    return False
def is_meta(token): return token.category == 'META'
def is_string(token): return token.category == 'STR'
def attribute_properties(token: Token):
    token.name = token.prop[0]
    if is_surrounder(token): attribute_surrounders_properties(token)
    if is_operator(token): attribute_operators_properties(token)
    #if is_meta(token): attribute_meta_properties(token)
    #if is_string(token): attribute_string_properties(token)
def attribute_surrounders_properties(token: Token):
    token.action = token.prop[1]
def attribute_operators_properties(token: Token):
    token.operands_place = token.prop[1]
    token.precedence = int(token.prop[2])
    token.operands = []


def TOKENIZE(INPUT: str) -> list:
    CHAIN = []
    INPUT = INPUT.lstrip().rstrip()
    if INPUT == '' : return [Token()]

    while len(INPUT) > 0:
        if INPUT[0:len(NULL)] == NULL:
            INPUT=INPUT[len(NULL):]
            continue
        found_category = False
        max_len = 0
        for i in range(len(SYMBOLS['CATEGORIES'])):
            for potential_symbol in reversed(sorted(SYMBOLS[SYMBOLS['CATEGORIES'][i]], key=lambda x: len(x))):
                if INPUT[0:len(potential_symbol)] == potential_symbol :
                    if len(potential_symbol) <= max_len: continue
                    max_len = len(potential_symbol)
                    chosen_symbol = potential_symbol
                    category = SYMBOLS['CATEGORIES'][i]
                    found_category = True
        if found_category:
            cur_token = tokenize_general(chosen_symbol,category)
            attribute_properties(cur_token)
            CHAIN.append(cur_token)
            INPUT = INPUT[len(chosen_symbol):]
            continue
        else:
            cur_token = tokenize_string(INPUT,CHAIN)
            attribute_properties(cur_token)
            CHAIN.append(cur_token)
            string_length = cur_token.length_symbol
            INPUT = INPUT[string_length:]
    '''Replace old indexes in TOKEN by new correct indexes'''
    for i in range(len(CHAIN)):
        CHAIN[i].index = i
    return CHAIN

def tokenize_general(SYMBOL,CATEGORY):
    category_index = SYMBOLS['CATEGORIES'].index(CATEGORY)
    symbol_index   = SYMBOLS[CATEGORY].index(SYMBOL)
    cat    = CATEGORY # index 0 in token
    symbol = SYMBOL   # index 1 in token
    prop   = []       # index 2 in token
    index  = 0        # always at last index of token
    for subcat in SYMBOLS['SUBCATEGORIES'][category_index]:
        property_index_for_symbol = SYMBOLS[subcat][symbol_index]
        prop.append(property_index_for_symbol)
    return Token(cat,symbol,prop,index)

def tokenize_string(INPUT,CHAIN):
    cat    = "STR"
    string = ""
    prop = []
    index = 0
    ''' CHECK IF QUOTATION '''
    quoting = False
    if len(CHAIN) > 0 and \
            CHAIN[len(CHAIN)-1].category == 'SUR' and \
            CHAIN[len(CHAIN)-1].prop[1] == 'wrap' :
                quoting = True
                quoting_symbol = CHAIN[len(CHAIN)-1].symbol
    while len(INPUT) > 0 :
        if not quoting and INPUT[0:len(NULL)] == NULL: break
        found_category = False
        # Stop if encounter a symbol other than string (except if we are quoting and did not meet the quoting symbol)
        for i in range(len(SYMBOLS['CATEGORIES'])):
            for potential_symbol in reversed(sorted(SYMBOLS[SYMBOLS['CATEGORIES'][i]], key=lambda x: len(x))):
                if INPUT[0:len(potential_symbol)] == potential_symbol :
                    if not quoting or potential_symbol == quoting_symbol:
                        found_category = True
        if found_category: break
        string += str(INPUT[0])
        INPUT = INPUT[1:]
    prop.append('variable')
    prop.append(len(string))
    return Token(cat,string,prop,index)


