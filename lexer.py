#!/usr/bin/env python3

from read_table import *

''' The LEXER always takes a STRING as INPUT.
When the PARSER will communicate with the LEXER, it should transform TOKENS (LISTS) into STRINGS.
Vice versa, the PARSER only takes TOKENS (LISTS) as INPUT.

TOKENS have no TRUTH VALUE. It is the job of the PARSER to assess it.
'''

def TOKENIZE(INPUT):
    ''' Build a token of len(INPUT) empty lists
    Each list represents the place of each character
    in the input string'''

    TOKEN = []

    ''' If INPUT is empty, OR INPUT is empty when
    removing trailing NULLs and duplicate NULLs,
    then return TOKEN'''
    if INPUT == '' : return [TOKEN]

    INPUT = remove_trailing_and_duplicate_null(INPUT)
    if INPUT == '' : return [TOKEN]

    while len(INPUT) > 0:
        if INPUT[0:len(NULL)] == NULL:
            INPUT=INPUT[len(NULL):]
            continue
        found_category = False
        max_len = 0
        for i in range(len(SYMBOLS['SYMBOLS_CATEGORIES'])):
            for potential_symbol in reversed(sorted(SYMBOLS[SYMBOLS['SYMBOLS_CATEGORIES'][i]], key=lambda x: len(x))):
                if INPUT[0:len(potential_symbol)] == potential_symbol :
                    if len(potential_symbol) <= max_len: continue
                    max_len = len(potential_symbol)
                    chosen_symbol = potential_symbol
                    category = SYMBOLS['SYMBOLS_CATEGORIES'][i]
                    found_category = True
        if found_category:
            match category:
                case "SURROUNDERS": TOKEN.append(tokenize_surrounder(chosen_symbol))
                case "OPERATORS":   TOKEN.append(tokenize_operator(chosen_symbol))
                case "META":        TOKEN.append(tokenize_meta(chosen_symbol))
            INPUT = INPUT[len(chosen_symbol):]
            continue
        else:
            STRING_TOKEN = tokenize_string(INPUT,TOKEN)
            TOKEN.append(STRING_TOKEN)
            string_length = STRING_TOKEN[2][1]
            INPUT = INPUT[string_length:]

    '''Correct nestedness of surrounders'''
    nestedness_level     = 0
    #wrappers_encountered = 0
    for i in range(len(TOKEN)):
        if TOKEN[i][0] == 'SUR':
            if   TOKEN[i][2][1] == 'open':
                nestedness_level += 1
                TOKEN[i][2][2] = nestedness_level
            elif TOKEN[i][2][1] == 'close':
                TOKEN[i][2][2] = nestedness_level
                nestedness_level -= 1
            #elif TOKEN[i][2][1] == 'wrap':
            #    wrappers_encountered += 1
            #    if not wrappers_encountered % 2 == 0:
            #        nestedness_level += 1
            #    else :
            #        nestedness_level -= 1
            #    TOKEN[i][2][2] = nestedness_level

    '''Replace old indexes in TOKEN by new correct indexes'''
    for i in range(len(TOKEN)):
        TOKEN[i][3] = i

    return TOKEN

def tokenize_surrounder(SYMBOL):
    sur = SYMBOL
    index = 0
    nest_count = 0
    prop = []
    name   = SYMBOLS['SURROUNDERS NAMES'][SYMBOLS['SURROUNDERS'].index(sur)]
    action = SYMBOLS['SURROUNDERS ACTION'][SYMBOLS['SURROUNDERS'].index(sur)]
    prop.append(name)
    prop.append(action)
    prop.append(nest_count)
    return ["SUR",sur,prop,index]

def tokenize_operator(SYMBOL):
    op = SYMBOL
    index = 0
    prop = []
    name = SYMBOLS['OPERATORS NAMES'][SYMBOLS['OPERATORS'].index(op)]
    direction = SYMBOLS['OPERATORS OPERANDS'][SYMBOLS['OPERATORS'].index(op)]
    precedence = int(SYMBOLS['OPERATORS PRECEDENCE'][SYMBOLS['OPERATORS'].index(op)])
    n_ary = len(direction)
    operands_init = [] # empty operands before parsing
    for i in range(n_ary):
        operands_init.append([])
    if n_ary == 1   : n_ary = "unary"
    elif n_ary == 2 : n_ary = "binary"
    elif n_ary == 3 : n_ary = "ternary"
    else            : n_ary = str(n_ary) + "-ary"
    prop = [name,n_ary,direction,precedence,operands_init]
    return ['OP',op,prop,index]

def tokenize_meta(SYMBOL):
    meta = SYMBOL
    index = 0
    prop = []
    name = SYMBOLS['META NAMES'][SYMBOLS['META'].index(meta)]
    prop = [name,len(name)]
    return ['META',meta,prop,index]

def tokenize_string(INPUT,TOKEN):
    string = ""
    ''' CHECK IF QUOTATION '''
    quoting = False
    if len(TOKEN) > 0 and \
            TOKEN[len(TOKEN)-1][0] == 'SUR' and \
            TOKEN[len(TOKEN)-1][2][1] == 'wrap' :
                quoting = True
                quoting_symbol = TOKEN[len(TOKEN)-1][1]
    ''''''
    while len(INPUT) > 0 :
        if not quoting and INPUT[0:len(NULL)] == NULL: break
        found_category = False
        ''''''''''''
        # Stop if encounter a symbol other than string (except if we are quoting and did not meet the quoting symbol)
        for i in range(len(SYMBOLS['SYMBOLS_CATEGORIES'])):
            for potential_symbol in reversed(sorted(SYMBOLS[SYMBOLS['SYMBOLS_CATEGORIES'][i]], key=lambda x: len(x))):
                if INPUT[0:len(potential_symbol)] == potential_symbol :
                    if not quoting or potential_symbol == quoting_symbol:
                        found_category = True
        ''''''''''''''''''
        if found_category: break
        string += str(INPUT[0])
        INPUT = INPUT[1:]
    index = 0
    prop = []
    prop.append('variable')
    prop.append(len(string))
    return ['STR',string,prop,index]

def remove_trailing_and_duplicate_null(INPUT):
    return remove_duplicate_null(remove_trailing_null(INPUT))

def remove_duplicate_null(INPUT):
    Finput = ""
    while len(INPUT) > 0:
        if INPUT[0] == NULL:
            Finput+=NULL
            INPUT=INPUT[1:]
            while INPUT[0] == NULL:
                INPUT=INPUT[1:]
                continue
        Finput+=INPUT[0]
        INPUT=INPUT[1:]
    return Finput

def remove_trailing_null(INPUT):
    while INPUT[0] == NULL:
        INPUT=INPUT[1:]
        if len(INPUT) == 0:
            return ""
    while INPUT[len(INPUT)-1] == NULL:
        INPUT=INPUT[0:len(INPUT)-1]
    return INPUT

class Lex:
    def __init__(self,raw_input):
        self.I = raw_input
        self.cursor = 0
        self.chain  = TOKENIZE(self.I)
        self.token  = self.chain[self.cursor]
        self.length = len(self.chain)
    def next_token(self):
        if self.cursor + 1 > self.length - 1:
            print("End of token chain reached.")
            return
        self.cursor += 1
        self.token = self.chain[self.cursor]
    def prev_token(self):
        if self.cursor - 1 < 0:
            print("Start of token chain reached.")
            return
        self.cursor -= 1
        self.token = self.chain[self.cursor]

#token_chain = Lex("(a+b) --> x")
#token_chain.next_token()
#token_chain.next_token()
#token_chain.next_token()
#token_chain.next_token()
#token_chain.next_token()
#token_chain.prev_token()
#token_chain.prev_token()
#token_chain.prev_token()
#print(token_chain.cursor)
#print(token_chain.token)




