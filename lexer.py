#!/usr/bin/env python3

from read_table import *

''' The LEXER always takes a STRING as INPUT.
When the PARSER will communicate with the LEXER, it should transform TOKENS (LISTS) into STRINGS.
Vice versa, the PARSER only takes TOKENS (LISTS) as INPUT.

TOKENS have no TRUTH VALUE. It is the job of the PARSER to assess it.
'''

def TOKENIZE(INPUT):
    return build_token(INPUT)

def build_token(INPUT):
    ''' Build a token of len(INPUT) empty lists
    Each list represents the place of each character
    in the input string'''

    TOKEN = [[] for x in INPUT] # Captures a token of length-of-input []

    ''' If INPUT is empty, OR INPUT is empty when
    removing trailing NULLs and duplicate NULLs,
    then return TOKEN'''
    if INPUT == '' : return TOKEN

    INPUT = remove_trailing_and_duplicate_null(INPUT)
    if INPUT == '' : return []

    ''' Populate TOKEN with [   identifier,     (e.g. 'STR')
                                symbol,         (e.g. 'hello')
                                [properties],   (e.g. ['immutable',5])
                                index ]         (e.g. 1)
    at its appropriate place in that order :
        1. Surrounders : property 'open/close'
        2. Operators   : property ['n_ary','direction']
        ?? ... Int?, Meta?
        3. Strings     : property '[(im)mutable, len(string)]'
            |_> should always be last, as not in table!
    '''
    for TOKEN_SUR in index_surrounders(INPUT)[1]:
        index = TOKEN_SUR[3]
        TOKEN[index] = TOKEN_SUR

    for TOKEN_OP in index_operators(INPUT)[1]:
        index = TOKEN_OP[3]
        TOKEN[index] = TOKEN_OP

    # Might need to do META here?

    '''Strings are the last to be built '''
    '''They are the remaining characters'''
    strings_indexes = []
    for i in range(len(INPUT)):
        if not TOKEN[i] == [] :
            strings_indexes.append(i)
    for TOKEN_STR in index_strings(INPUT,strings_indexes)[1]:
        index = TOKEN_STR[3]
        TOKEN[index] = TOKEN_STR

    '''Pop out unused or RESERVED indexes in the TOKEN'''
    index = 0
    while index < len(TOKEN):
        if TOKEN[index] == [] or TOKEN[index][0] == 'RESERVED':
            TOKEN.pop(index)
            continue
        index+=1

    '''Replace old indexes in TOKEN by new correct indexes'''
    for i in range(len(TOKEN)):
        TOKEN[i][3] = i

    return TOKEN

def index_surrounders(INPUT):
    '''Returns ['SUR','(', ['open/close','PARENTHESIS','nest level'], index_in_token]'''
    indexes    = [True, []]
    nest_count = 0
    for i in range(len(INPUT)):
        char = INPUT[i]
        for sur in SYMBOLS['SURROUNDERS']:
            if char in sur :
                prop = []
                prop.append(SYMBOLS['SURROUNDERS NAMES'][SYMBOLS['SURROUNDERS'].index(sur)])
                if sur.index(char) == 0 :
                    prop.append("open")
                    nest_count+=1
                else :
                    prop.append("close")
                prop.append(nest_count)
                if sur.index(char) == 1: nest_count+=-1
                indexes[1].append(["SUR",char,prop,i])
    return indexes

def index_operators(INPUT):
    '''Returns ['OP','+', ['OP NAME','n_ary','LR','precedence'], index_in_token]'''
    indexes = [True, []]
    index = 0
    max_length_op = max(len(x) for x in SYMBOLS['OPERATORS'])
    while len(INPUT) > 0:
        found_operator = False
        if INPUT[0] == NULL:
            INPUT=INPUT[1:]
            index+=1
            continue
        for i in reversed(range(max_length_op)):
            if INPUT[0:i+1] in [x for x in SYMBOLS['OPERATORS']]:
                operator = INPUT[0:i+1]
                operator_name = SYMBOLS['OPERATORS NAMES'][SYMBOLS['OPERATORS'].index(operator)]
                operand_direction = SYMBOLS['OPERATORS OPERANDS'][SYMBOLS['OPERATORS'].index(operator)]
                precedence = int(SYMBOLS['OPERATORS PRECEDENCE'][SYMBOLS['OPERATORS'].index(operator)])
                n_ary = len(operand_direction)
                if n_ary == 1: n_ary = "unary"
                if n_ary == 2: n_ary = "binary"
                prop = [operator_name,n_ary,operand_direction,precedence]
                indexes[1].append(['OP',operator,prop,index])
                for j in range(len(operator)-1):
                    indexes[1].append(['RESERVED',operator,prop,index+j+1])
                INPUT=INPUT[len(operator):]
                found_operator = True
                index+=len(operator)
                break
        if found_operator: continue
        index+=1
        INPUT=INPUT[1:]
    return indexes

def index_strings(INPUT,indexes_to_avoid):
    '''Returns ['STR','the_string', [(im)mutable, len(the_string)], index_in_token]'''
    indexes = [True, []]
    index = 0
    while len(INPUT) > 0:
        string = ""
        if index not in indexes_to_avoid and INPUT[0] != NULL:
            string+=INPUT[0]
            INPUT=INPUT[1:]
            start_index = index
            index+=1
            while len(INPUT)>0 and index not in indexes_to_avoid and INPUT[0] != NULL:
                string+=INPUT[0]
                INPUT=INPUT[1:]
                index+=1
            prop = []
            if string in SYMBOLS['META']:
                prop.append(SYMBOLS['META NAMES'][SYMBOLS['META'].index(string)])
            else :
                prop.append('immutable')
            prop.append(len(string))
            indexes[1].append(['STR',string,prop,start_index])
            for j in range(len(string)-1):
                indexes[1].append(['RESERVED',string,prop,start_index+j+1])
        INPUT=INPUT[1:]
        index+=1
    return indexes

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
