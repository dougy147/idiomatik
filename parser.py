#!/usr/bin/env python3

from lexer import *
from read_table import *
from colors import *

''' The PARSER receives STRINGS as INPUT, send them to the LEXER that returns LISTS of TOKENS.
The PARSER then evaluates the LIST of TOKENS' syntax (is it a "well formed expression"?).
It returns EXPRESSIONS.
'''

class Expression:
    def __init__(self,tokens: list = []):
        self.tokens   = tokens
        self.length   = len(self.tokens)
        self.validity = True
        self.string   = NULL.join(map(str,[x.symbol for x in self.tokens]))
    def get_silent(self):
        silent_surrounding(CHAIN = self.tokens,EXP = self)
        return self
    def get_subexp(self,SECURE_SURROUND=True):
        extract_subexpressions(CHAIN = self.tokens,EXP = self,SECURE_SURROUND=SECURE_SURROUND)
        return self

def PARSE(INPUT: str, ERROR_LOG: bool = True) -> Expression:
    def parse_surrounders(EXP: Expression, ERROR_LOG: bool = True):
        if not check_surrounders(EXP.tokens,ERROR_LOG = ERROR_LOG):
            EXP.validity = False
    def parse_operators(EXP: Expression, ERROR_LOG: bool = True):
        for token in EXP.tokens:
            if is_operator(token):
                extract_operands = check_operands(token,EXP.tokens,EXTRACT_OPERAND = True,ERROR_LOG = ERROR_LOG)
                if not extract_operands[0]:
                    EXP.validity = False
                    #break
                token.operands = extract_operands[1]
    #if   isinstance(INPUT,str):
    EXP = Expression(TOKENIZE(INPUT))
    #elif isinstance(INPUT,list):
    #    EXP = Expression(TOKENIZE(NULL.join(map(str,[x.symbol for x in INPUT]))))
    parse_surrounders(EXP, ERROR_LOG = ERROR_LOG)
    parse_operators(EXP, ERROR_LOG = ERROR_LOG)
    return EXP


def check_surrounders(CHAIN: list, cursor: int = 0, ERROR_LOG: bool = True) -> bool :
    #last_open_name, last_open_index, last_open_token = [], [], []
    last_open_token = []
    first_wrap = []
    nestedness = 0
    while cursor < len(CHAIN):
        TOKEN = CHAIN[cursor]
        if is_surrounder_open(TOKEN):
            nestedness+=1
            #last_open_name.append(TOKEN.name)
            #last_open_index.append(TOKEN.index)
            last_open_token.append(TOKEN)
        TOKEN.nestedness = nestedness
        if is_surrounder_close(TOKEN):
            if len(last_open_token) == 0 :
                if ERROR_LOG :
                    print(bcolors.FAIL + f"ERROR: unmatched closing {TOKEN.name} (index {TOKEN.index})." + bcolors.ENDC)
                return False
            elif last_open_token[len(last_open_token)-1].name != TOKEN.name:
                if ERROR_LOG :
                    print(bcolors.FAIL + f"ERROR: expected closing {last_open_name[len(last_open_name)-1]}, got closing {TOKEN.name} (index {TOKEN.index})." + bcolors.ENDC)
                return False
            #last_open_name.pop(len(last_open_name)-1)
            #last_open_index.pop(len(last_open_index)-1)
            # add surrounders their matching partner as a property:
            last_open_token[len(last_open_token)-1].match, TOKEN.match = TOKEN, last_open_token[len(last_open_token)-1]
            last_open_token.pop(len(last_open_token)-1)
            nestedness-=1
        if is_surrounder_wrap(TOKEN):
            if len(first_wrap) == 0:
                first_wrap.append(TOKEN)
            elif first_wrap[0].name != TOKEN.name:
                # transform wrapper to type string if inside a different wrapper symbol
                TOKEN.category = "STR"
            else:
                first_wrap[0].match, TOKEN.match = TOKEN, first_wrap[0]
                first_wrap.pop(0)
        cursor += 1
    if nestedness != 0:
        s = "s" if nestedness > 1 else ""
        es = "es" if nestedness > 1 else ""
        if ERROR_LOG :
            print(bcolors.FAIL + f"ERROR: {nestedness} unmatched opening{s} (index{es} {','.join(map(str,[x.index for x in last_open_token]))})." + bcolors.ENDC)
        return False
    if len(first_wrap) != 0:
        first_wrap[0].match = first_wrap[0] # make it match itself
        if ERROR_LOG :
            print(bcolors.FAIL + f"ERROR: unmatched wrapper `{first_wrap[0].symbol}` (index {first_wrap[0].index})." + bcolors.ENDC)
        return False
    return True

def check_operands(OP_TOKEN: Token, CHAIN: list,EXTRACT_OPERAND = False,ERROR_LOG = True) -> [bool, list]:
    ''' EXTRACT_OPERAND is here in case we need to extract an operator's operand(s)
    for example in the "silent_surrounding()" function.
    '''
    op_index          = OP_TOKEN.index
    operands_position = OP_TOKEN.operands_place
    last_index        = op_index
    operands          = []
    precedence        = OP_TOKEN.precedence
    # LR
    for i in range(len(operands_position)):
        if i != 0:
            if operands_position[i] == operands_position[i-1]:
                last_operand = get_operand(OP_TOKEN,CHAIN,operands_position[i-1],last_index)
                if operands_position[i] == 'L':
                    last_index = last_operand[1][0].index
                if operands_position[i] == 'R':
                    last_index = last_operand[1][len(last_operand[1])-1].index
            else :
                last_index = op_index
        if precedence == 0: last_index = op_index # TODO : test in progress
        if not get_operand(OP_TOKEN,CHAIN,operands_position[i],last_index)[0] :
            if ERROR_LOG:
                print(bcolors.FAIL + "ERROR: invalid operand for operator '{}' at index '{}'.".format(OP_TOKEN.symbol,op_index) + bcolors.ENDC)
            #if not EXTRACT_OPERAND: return False
            #if not EXTRACT_OPERAND: return [False, []]
            #else :                  return [False, []]
            return [False, []]
        if EXTRACT_OPERAND :
            operands.append(get_operand(OP_TOKEN,CHAIN,operands_position[i],last_index)[1])
    if not EXTRACT_OPERAND:
        #return True
        return [True, []]
    else :
        return [True, operands]
    #return True

def get_operand(OP_TOKEN: Token, CHAIN: list, DIRECTION: str, index: int) -> [bool, list]:
    if DIRECTION == "L":
        direction, break_point = -1, -1
        add_surrounder, substract_surrounder = 'close', 'open'

    if DIRECTION == "R":
        direction, break_point = +1, len(CHAIN)
        add_surrounder, substract_surrounder = 'open', 'close'
    ''' Test for operators with 0 precedence '''
    precedence = OP_TOKEN.precedence #OPERATOR[2][2]
    if precedence == 0: operator_index = OP_TOKEN.index #OPERATOR[4]
    else : index += direction
    #index += direction
    ''''''
    surrounder_counter, operand = 0, []
    found_operand = False

    if index < 0 or index >= len(CHAIN): return [False,[]]

    ''' For 0-precedence operators '''
    if precedence == 0:
        index = 0
        while found_operand == False:
            if index < 0 or index >= len(CHAIN): return [False,[]]
            if DIRECTION == "L" :
                if index >= operator_index: break
                operand_to_test = CHAIN[index:operator_index]
            elif DIRECTION == "R" :
                if len(CHAIN) - index <= operator_index + 1: break
                operand_to_test = CHAIN[operator_index+1:len(CHAIN)-index]
            if check_surrounders(operand_to_test,ERROR_LOG=False):
                found_operand = True
                for k in range(len(operand_to_test)):
                    if DIRECTION == "L"  : operand.append(CHAIN[index+k])
                    elif DIRECTION == "R": operand.append(CHAIN[operator_index+1+k]) # TODO : check around here
                return [True, operand]
            index += 1
        return [False,[]]
    ''''''

    if is_string(CHAIN[index]) or \
            (is_meta(CHAIN[index]) and CHAIN[index].name == 'ANY_STR') or \
            (is_meta(CHAIN[index]) and CHAIN[index].name == 'ANY_OPERAND') or \
            (is_meta(CHAIN[index]) and CHAIN[index].name == 'ANY_VALID_EXP') :
                return [True,[CHAIN[index]]]

    if is_operator(CHAIN[index]):
        if DIRECTION != CHAIN[index].operands_place: # if meet operator that doesn't go the same direction (exclusively): False
            return [False,[CHAIN[index]]]

    if is_surrounder(CHAIN[index]):
        if CHAIN[index].action == substract_surrounder :
            return [False,[CHAIN[index]]]
        else :
            operand.append(CHAIN[index])
            surrounder_counter+=1
            index += direction

    while found_operand == False or surrounder_counter != 0 :
        if index == break_point :
            if DIRECTION == "L": operand = [x for x in reversed(operand)]
            return [False, operand]

        if not found_operand and is_operator(CHAIN[index]):
            if DIRECTION != CHAIN[index].operands_place:
                return [False,[CHAIN[index]]]

        if is_surrounder(CHAIN[index]):
            found_operand = True
            if CHAIN[index].action == substract_surrounder : surrounder_counter-=1
            if CHAIN[index].action == add_surrounder : surrounder_counter+=1

        if is_string(CHAIN[index]) or \
                (is_meta(CHAIN[index]) and CHAIN[index].name == 'ANY_STR') or \
                (is_meta(CHAIN[index]) and CHAIN[index].name == 'ANY_OPERAND') or \
                (is_meta(CHAIN[index]) and CHAIN[index].name == 'ANY_VALID_EXP') : found_operand = True

        operand.append(CHAIN[index])
        index += direction
    if DIRECTION == "L": operand = [x for x in reversed(operand)]
    return [True, operand]


def silent_surrounding(CHAIN: list = [], EXP = None) -> str :
    operators_in_token = [x for x in filter(lambda y: y.category == 'OP', CHAIN)]
    if operators_in_token == []: return NULL.join(map(str,[x.symbol for x in CHAIN]))

    positive_sorted_operators = [x for x in filter(lambda y: y.precedence >= 0, sorted(operators_in_token, key=lambda x: (x.precedence, x.index) ) )]
    negative_sorted_operators = [x for x in filter(lambda y: y.precedence < 0, sorted(operators_in_token, key=lambda x:  (x.precedence, x.index), reverse=True ) )]

    # Replace negative values by positive in negative_sorted_operators
    for OP in negative_sorted_operators:
        OP.precedence = abs(OP.precedence)
    concatenated_positive_negative = sorted(positive_sorted_operators + negative_sorted_operators, key=lambda x: x.precedence)
    sorted_operators = concatenated_positive_negative

    # Go to index of the top priority operator and surround its operands.
    for OP in sorted_operators :
        index_op = OP.index
        surrounder_counter = 0
        # If priority is NON-NULL, operators are surrounded WITH their operands, (so, EXCEPTION for 0 (=, ==, ===))
        if OP.precedence != 0 :
            cur_operands = check_operands(OP,CHAIN,EXTRACT_OPERAND = True,ERROR_LOG=False)[1]
            if cur_operands == [] : continue
            lowest_index, highest_index = cur_operands[0][0].index, cur_operands[-1:][0][-1:][0].index
            # "Special case" for unary operators :
            if is_operator_unary(OP):
                if OP.operands_place == "R":
                    # Ignore if already surrounded!
                    if lowest_index > 0 and highest_index < len(CHAIN) - 1:
                        if  is_surrounder(CHAIN[lowest_index-1-1])     and \
                                CHAIN[lowest_index-1-1].action == 'open' and \
                                is_surrounder(CHAIN[highest_index+1])     and \
                                CHAIN[highest_index+1].action == 'close' :
                                    continue
                    CHAIN[lowest_index-1:lowest_index-1] = TOKENIZE("(")
                    CHAIN[highest_index+1+1:highest_index+1+1] = TOKENIZE(")")
                if OP.operands_place == "L":
                    # Ignore if already surrounded!
                    if lowest_index > 0 and highest_index < len(CHAIN) - 1:
                        if  is_surrounder(CHAIN[lowest_index-1])      and \
                                CHAIN[lowest_index-1].action == 'open' and \
                                is_surrounder(CHAIN[highest_index+1+1]) and \
                                CHAIN[highest_index+1+1].action == 'close' :
                                    #print("Already surrounded :)")
                                    continue
                    CHAIN[lowest_index:lowest_index] = TOKENIZE("(")
                    CHAIN[highest_index+1+1+1:highest_index+1+1+1] = TOKENIZE(")")
            else :
                # Ignore if already surrounded!
                if lowest_index > 0 and highest_index < len(CHAIN) - 1:
                    if  is_surrounder(CHAIN[lowest_index-1])     and \
                            CHAIN[lowest_index-1].action == 'open' and \
                            is_surrounder(CHAIN[highest_index+1])   and \
                            CHAIN[highest_index+1].action == 'close' :
                                #print("Already surrounded :)")
                                continue
                CHAIN[lowest_index:lowest_index] = TOKENIZE("(")
                CHAIN[highest_index+1+1:highest_index+1+1] = TOKENIZE(")")
            CHAIN = TOKENIZE(NULL.join(map(str, [x.symbol for x in CHAIN])))
            for OPE in sorted_operators :
                if OPE.index < lowest_index: continue
                if OPE.index <= highest_index: OPE.index += 1
                if OPE.index > highest_index:  OPE.index += 2
        else :
            #This is where things could get sketchy ...
            #Here is how 0-priority operators (=, ==, <=>) are to be surrounded.
            index_op = OP.index
            surrounder_counter = 0
            # GOING LEFT
            for i in reversed(range(index_op)):
                if i == 0:
                    # TODO Do nothing if already surrounded
                    CHAIN[index_op:index_op] = TOKENIZE(")")
                    CHAIN[i:i] = TOKENIZE("(")
                    CHAIN = TOKENIZE(NULL.join(map(str, [x.symbol for x in CHAIN])))
                    for OPE in sorted_operators:
                        if   OPE.index == index_op : OPE.index += 2 # this is our current OPERATOR
                        elif OPE.index >  index_op : OPE.index += 2 # above highest parenthesis +2
                        elif OPE.index >= i        : OPE.index += 1 # above lowest parenthesis  +1
                        # else : untouched
                    break
                if is_surrounder(CHAIN[i]):
                    if   CHAIN[i].action == 'close': surrounder_counter += 1
                    elif CHAIN[i].action == 'open':
                        surrounder_counter -= 1
                    if surrounder_counter == -1 :
                        CHAIN[index_op:index_op] = TOKENIZE(")")
                        CHAIN[i+1:i+1] = TOKENIZE("(")
                        CHAIN = TOKENIZE(NULL.join(map(str, [x.symbol for x in CHAIN])))
                        for OPE in sorted_operators:
                            if   OPE.index == index_op : OPE.index += 2 # this is our current OPERATOR
                            elif OPE.index >  index_op : OPE.index += 2 # above highest parenthesis +2
                            elif OPE.index >= i+1      : OPE.index += 1 # above lowest parenthesis  +1
                        break
                    continue
                if is_operator(CHAIN[i]) and CHAIN[i].precedence == 0 and surrounder_counter == 0 :
                    CHAIN[index_op:index_op] = TOKENIZE(")")
                    CHAIN[i+1:i+1] = TOKENIZE("(")
                    CHAIN = TOKENIZE(NULL.join(map(str, [x.symbol for x in CHAIN])))
                    for OPE in sorted_operators:
                        if   OPE.index == index_op : OPE.index += 2 # this is our current OPERATOR
                        elif OPE.index >  index_op : OPE.index += 2 # above highest parenthesis +2
                        elif OPE.index >= i+1      : OPE.index += 1 # above lowest parenthesis  +1
                    break
            # Reset surrounder_counter
            surrounder_counter = 0
            index_op = OP.index
            # If is the last equal sign : surround its right part
            for OP_INDEXES in sorted_operators:
                if OP_INDEXES.index > index_op:
                    is_last = False
                    break
                is_last = True
            if is_last :
                CHAIN[index_op+1:index_op+1] = TOKENIZE("(")
                CHAIN[len(CHAIN):len(CHAIN)] = TOKENIZE(")")
                CHAIN = TOKENIZE(NULL.join(map(str, [x.symbol for x in CHAIN])))
                for OPE in sorted_operators:
                    if OPE.index >= index_op+1 : OPE.index += 1 # above lowest parenthesis  +1

    silent = NULL.join(map(str,[x.symbol for x in CHAIN]))
    if not EXP == None : EXP.silent = silent
    return silent

def extract_subexpressions(CHAIN: list = [], EXP = None, SECURE_SURROUND = True) -> list :
    ''' WARNING: by default this function `silent_surround` the expression first.'''
    if SECURE_SURROUND: # grab silent silent_surrounding to avoid false positive
        CHAIN = PARSE(EXP.get_silent().silent).tokens
    SUB_EXP = []
    window_size = 1
    for i in range(len(CHAIN)):
        for j in range(len(CHAIN)):
            if j+window_size > len(CHAIN): break
            expression_to_check = NULL.join(map(str,[x.symbol for x in CHAIN[j:j+window_size]]))
            new_exp = PARSE(expression_to_check, ERROR_LOG = False)
            if new_exp.validity and not new_exp in SUB_EXP :
                SUB_EXP.append(new_exp)
                #print(f"Checking '{expression_to_check}'")
        window_size+=1
    EXP.subexp = SUB_EXP
    return EXP

#a = PARSE("helo  +world /2 = 2 ^ 3 - 21")
#print(a.string)
#silent_surrounding(a.tokens,a)
#print(a.get_silent().silent)
#print(a.get_subexp().subexp)
#print([x.symbol for x in a.get_subexp().subexp])

#for sub in a.get_subexp().subexp:
#    print([x.symbol for x in sub.tokens])

#a = PARSE('(  a + b) ="''" [ c ]')
#for token in a.tokens :
#    if is_surrounder(token):
#        print(token.symbol,token.match.symbol)





