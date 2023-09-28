#!/usr/bin/env python3

from read_table import *
from lexer import *
from parser import *
from read_rules import *
#from checker import *


''' The REWRITER job is to rewrite PROPOSITIONS to another PROPOSITION given a RULE.
PROPOSITIONS are valid TOKENS.
'''

def REWRITE(TOKEN):
    if not PARSE(TOKEN)[0] : return [False, TOKEN, [[]]]
    if len(TOKEN) == 0     : return [True, TOKEN, [RULES]]
    if len(RULES) == 0     : return [True, TOKEN, [RULES]]

'''Think about the way we should define meta characters : _ is any string
but I want to be able to give a rule such as A + B --> B + A (swap)
In this regard, META characters like _ should have properties, and those properties
should be evaluated in the below functions.'''

def silent_surrounding(TOKEN):
    ''' Given precedence of OPERATORS, place "invisibile" parenthesis around
    subexpressions to be solved first.
        TODO special cases :
    - alone minus sign (solve it in parser)
    '''
    operators_in_token = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]
    if operators_in_token == []:
        return TOKEN
    # First sort >=0 operators (priority asc, index asc)
    # Then sort <0 operators (priority desc, index desc)
    positive_sorted_operators = [x for x in filter(lambda y: y[2][3] >= 0, sorted(operators_in_token, key=lambda x: (x[2][3], x[3]) ) )]
    negative_sorted_operators = [x for x in filter(lambda y: y[2][3] < 0, sorted(operators_in_token, key=lambda x: (x[2][3], x[3]), reverse=True ) )]
    # Replace negative values by positive in negative_sorted_operators
    for OP in negative_sorted_operators:
        OP[2][3] = abs(OP[2][3])
    concatenated_positive_negative = sorted(positive_sorted_operators + negative_sorted_operators, key=lambda x: x[2][3])
    sorted_operators = concatenated_positive_negative
    # Go to index of the top priority operator and surround its operands.
    for OP in sorted_operators :
        index_op = OP[3]
        surrounder_counter = 0
        # If priority is NON-NULL, operators are surrounded WITH their operands, EXCEPT for 0 (=, ==, ===)
        if OP[2][3] != 0 :
            cur_operands = check_operands(OP,TOKEN,EXTRACT_OPERAND = True)[1]
            if cur_operands == [] : continue
            lowest_index, highest_index = cur_operands[0][0][3], cur_operands[-1:][0][-1:][0][3]
            # "Special case" for unary operators :
            if OP[2][1] == "unary":
                if OP[2][2] == "R":
                    TOKEN[lowest_index-1:lowest_index-1] = TOKENIZE("(")
                    TOKEN[highest_index+1+1:highest_index+1+1] = TOKENIZE(")")
                if OP[2][2] == "L":
                    TOKEN[lowest_index:lowest_index] = TOKENIZE("(")
                    TOKEN[highest_index+1+1+1:highest_index+1+1+1] = TOKENIZE(")")
            else :
                TOKEN[lowest_index:lowest_index] = TOKENIZE("(")
                TOKEN[highest_index+1+1:highest_index+1+1] = TOKENIZE(")")
            TOKEN = PARSE(TOKENIZE(NULL.join(map(str, [x[1] for x in TOKEN]))))[1]
            for OPE in sorted_operators :
                if OPE[3] < lowest_index: continue
                if OPE[3] <= highest_index: OPE[3] += 1
                if OPE[3] > highest_index: OPE[3] += 2
        else :
            #This is where things could get sketchy ...
            #Here is how 0-priority operators (=, ==, <=>) are to be surrounded.
            index_op = OP[3]
            surrounder_counter = 0
            # GOING LEFT
            for i in reversed(range(index_op)):
                if i == 0:
                    TOKEN[index_op:index_op] = TOKENIZE(")")
                    TOKEN[i:i] = TOKENIZE("(")
                    TOKEN = PARSE(TOKENIZE(NULL.join(map(str, [x[1] for x in TOKEN]))))[1]
                    for OPE in sorted_operators:
                        if OPE[3] == index_op : OPE[3] += 2 # this is our current OPERATOR
                        elif OPE[3] >  index_op : OPE[3] += 2 # above highest parenthesis +2
                        elif OPE[3] >= i        : OPE[3] += 1 # above lowest parenthesis  +1
                        # else : untouched
                    break
                if TOKEN[i][0] == 'SUR':
                    if   TOKEN[i][2][1] == 'close': surrounder_counter += 1
                    elif TOKEN[i][2][1] == 'open':
                        surrounder_counter -= 1
                    if surrounder_counter == -1 :
                        TOKEN[index_op:index_op] = TOKENIZE(")")
                        TOKEN[i+1:i+1] = TOKENIZE("(")
                        TOKEN = PARSE(TOKENIZE(NULL.join(map(str, [x[1] for x in TOKEN]))))[1]
                        for OPE in sorted_operators:
                            if OPE[3] == index_op : OPE[3] += 2 # this is our current OPERATOR
                            elif OPE[3] >  index_op : OPE[3] += 2 # above highest parenthesis +2
                            elif OPE[3] >= i+1      : OPE[3] += 1 # above lowest parenthesis  +1
                        break
                    continue
                if TOKEN[i][0] == 'OP' and TOKEN[i][2][3] == 0 and surrounder_counter == 0 :
                    TOKEN[index_op:index_op] = TOKENIZE(")")
                    TOKEN[i+1:i+1] = TOKENIZE("(")
                    TOKEN = PARSE(TOKENIZE(NULL.join(map(str, [x[1] for x in TOKEN]))))[1]
                    for OPE in sorted_operators:
                        if OPE[3] == index_op : OPE[3] += 2 # this is our current OPERATOR
                        elif OPE[3] >  index_op : OPE[3] += 2 # above highest parenthesis +2
                        elif OPE[3] >= i+1      : OPE[3] += 1 # above lowest parenthesis  +1
                    break
            # Reset surrounder_counter
            surrounder_counter = 0
            index_op = OP[3]
            # If is the last equal sign : surround its right part
            for OP_INDEXES in sorted_operators:
                if OP_INDEXES[3] > index_op:
                    is_last = False
                    break
                is_last = True
            if is_last :
                TOKEN[index_op+1:index_op+1] = TOKENIZE("(")
                TOKEN[len(TOKEN):len(TOKEN)] = TOKENIZE(")")
                TOKEN = PARSE(TOKENIZE(NULL.join(map(str, [x[1] for x in TOKEN]))))[1]
                for OPE in sorted_operators:
                    if OPE[3] >= index_op+1 : OPE[3] += 1 # above lowest parenthesis  +1
    return TOKEN


#def simplify_surrounding(TOKEN):
#    ''' If 2 or more consecutive opening surrounders correspond to the same number of
#    consecutive closing surrounders : overuse of surrounders => simplify by removing
#    total number of surrounders - 1.
#    '''
#    SUR = [x for x in filter(lambda y: y[0] == 'SUR',TOKEN)]
#    if len(SUR) == 0: return TOKEN
#    for i in range(len(TOKEN)):
#        if i >= len(TOKEN) - 1 : break
#        if TOKEN[i][2][1] == 'open' and TOKEN[i+1][2][1] == 'open' :

def split_all_rewrite_rules():
    '''Given all current RULES, returns a list of the form :
    [ [RULE1,LEFT_PATTERN1,RIGHT_PATTERN1], [RULE2,...] ]'''
    REWRITE_RULES = RULES['REWRITE_RULES']
    splitted_rewrite_rules  = []
    for rewrite_rule in REWRITE_RULES:
        rlp = [] # rule, left_pattern, right_pattern
        left_pattern, right_pattern = split_rewrite_rule(rewrite_rule)
        rlp.append(rewrite_rule)
        rlp.append(left_pattern)
        rlp.append(right_pattern)
        splitted_rewrite_rules.append(rlp)
    return splitted_rewrite_rules


def split_rewrite_rule(rewrite_rule):
    '''Given a REWRITE_RULE, returns a TUPLE of its LEFT and RIGHT PATTERNS'''
    REWRITE_AS_sym = SYMBOLS['OPERATORS'][SYMBOLS['OPERATORS NAMES'].index("REWRITE_AS")]

    rewrite_nb_in_rule = NULL.join(map(str, [x[1] for x in rewrite_rule])).count(REWRITE_AS_sym)
    if rewrite_nb_in_rule > 1 :
        print("Multiple rewrites in a single rule not yet supported:\n\tRule '{}'".format(NULL.join(map(str, [x[1] for x in rewrite_rule]))))
        #print("Weird behavior expected!")
        return

    # Grabbing left side pattern
    index = 0
    left_pattern = []
    while rewrite_rule[index][1] != REWRITE_AS_sym:
        left_pattern.append(rewrite_rule[index])
        index+=1
    index+=1
    # Grabbing right side pattern
    right_pattern = []
    while index < len(rewrite_rule):
        right_pattern.append(rewrite_rule[index])
        index+=1
    return (left_pattern,right_pattern)

'''WARNING : functions below allow to recursively check if a rule can be subrewritten.
They might never stop, and I found no way to contourn this issue for the moment (dumb)'''

def combine_all_possible_rewrites(TOKEN,POSSIBLE_REWRITES = None,REWRITES=None,first_time=True,RECURSION=0,RECURSION_EXCEEDED=False):
    '''Returns ALL possible rewrites for ALL TOKENS given ALL rules'''
    '''WARNING : VERY SLOW WITH LOTS OF RULES, AND MIGHT NOT STOP'''
    ''' POSSIBLE_REWRITES : [True/False, [ [TOKEN0, LEFT, RIGHT, RULE_X], [TOKEN1, LEFT, RIGHT,RULE_Y],... ]]'''
    RECURSION_LIMIT=30
    #if RECURSION_EXCEEDED :
    #    print("Recursion limit ({}) exceeded!".format(RECURSION_LIMIT))
    #    return [ POSSIBLE_REWRITES[0], REWRITES ]
    if RECURSION >= RECURSION_LIMIT:
        print("Recursion limit ({}) exceeded in 'combine_all_possible_rewrites()'!".format(RECURSION_LIMIT))
        RECURSION_EXCEEDED = True
        return
    SPLITTED_RULES = split_all_rewrite_rules() # Grab all PUBLIC REWRITE_RULES (left and right patterns)
    #print("SPLITTED RULES:",SPLITTED_RULES)

    if POSSIBLE_REWRITES == None: POSSIBLE_REWRITES = [False, []]
    if REWRITES == None: REWRITES = []

    for splitted in SPLITTED_RULES:
        R  = splitted[0] # rule
        LP = splitted[1] # left pattern
        RP = splitted[2] # right pattern
        #if first_time == True :
        #    REWRITTEN = token_full_rewrites_list(TOKEN,LP,RP,REWRITES=None)
        #else :
        #    REWRITTEN = token_full_rewrites_list(TOKEN,LP,RP,REWRITES=REWRITES)
        #if len(TOKEN) < len(LP) : continue # New : avoid "Rule a + b ::= c" rewrite "Token a" as "c"
        #else:
        REWRITTEN = token_full_rewrites_list(TOKEN,LP,RP)
        if not REWRITTEN[0]: continue

        for TRANSFORMATION in REWRITTEN[1]:
            if NULL.join(map(str,[x[1] for x in TRANSFORMATION])) in REWRITES:
                continue
            else :
                REWRITES.append(NULL.join(map(str,[x[1] for x in TRANSFORMATION])))
                POSSIBLE_REWRITES[0] = True
                POSSIBLE_REWRITES[1].append([TRANSFORMATION,LP,RP,R])
            combine_all_possible_rewrites(TRANSFORMATION,REWRITES=REWRITES,first_time=False,RECURSION=RECURSION+1)
    return [ POSSIBLE_REWRITES[0], REWRITES ]

def token_full_rewrites_list(TOKEN,LEFT_PATTERN,RIGHT_PATTERN,INDEX=0,REWRITES=None,first_time=True,RECURSION=0,RECURSION_EXCEEDED=False):
    '''Returns ALL possibilities for a TOKEN given a SINGLE REWRITE_RULE LEFT and RIGHT PATTERNS'''
    RECURSION_LIMIT=20
    #if RECURSION_EXCEEDED :
    #    print("Recursion limit ({}) exceeded in 'token_full_rewrites_list()' !".format(RECURSION_LIMIT))
    #    return
    if RECURSION >= RECURSION_LIMIT:
        RECURSION_EXCEEDED = True
        return
    if REWRITES is None: REWRITES = []
    for i in range(INDEX,len(TOKEN)):
        if len(TOKEN) - i < len(LEFT_PATTERN) : continue # New : avoid "Rule a + b ::= c" rewrite "Token a" as "c"
        CUR_RIGHT_PATTERN = [x for x in RIGHT_PATTERN]
        pattern_in_token = True
        rewritable_part_of_token = []

        for j in range(len(LEFT_PATTERN)):
            if i+j >= len(TOKEN): break
            rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[i+j+1:]]))

            # TODO : not only for "_", add "$"
            if LEFT_PATTERN[j][2][0] == 'ANY_STR' and TOKEN[i+j][0] == 'STR':
                rewritable_part_of_token.append(TOKEN[i+j])
                for k in range(len(RIGHT_PATTERN)):
                    #if CUR_RIGHT_PATTERN[k][2][0] == 'ANY_STR' :
                    if CUR_RIGHT_PATTERN[k][2][0] == 'ANY_STR' and CUR_RIGHT_PATTERN[k][1] == LEFT_PATTERN[j][1] :
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j]
                        continue
                continue
            #print(TOKEN)
            if TOKEN[i+j][1] != LEFT_PATTERN[j][1]:
                pattern_in_token = False
                break
            rewritable_part_of_token.append(TOKEN[i+j])

        if pattern_in_token :
            if "ANY_STR" in str(CUR_RIGHT_PATTERN) or "OPERAND" in str(CUR_RIGHT_PATTERN) :
                continue
            start_index = i
            end_index   = i+j
            rewritable_part = NULL+NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))
            beginning_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[0:i]]))
            NEW_TOKEN=beginning_of_proposition+rewritable_part+rest_of_proposition
            NEW_TOKEN = PARSE(TOKENIZE(NEW_TOKEN))
            if NEW_TOKEN[0]:
                new_token = NULL.join(map(str,[x[1] for x in NEW_TOKEN[1]]))
                if not new_token in REWRITES:
                    REWRITES.append(new_token)
                    token_full_rewrites_list(NEW_TOKEN[1],LEFT_PATTERN,RIGHT_PATTERN,INDEX=i+j,REWRITES=REWRITES,RECURSION=RECURSION+1,RECURSION_EXCEEDED=RECURSION_EXCEEDED)
    if INDEX != 0 : return
    VALID_REWRITES = [] # VALID_REWRITES are TOKENS
    index = 0
    for rew in REWRITES:
        token = PARSE(TOKENIZE(rew))
        if token[0] and not token[1] in VALID_REWRITES :
            VALID_REWRITES.append(token[1])
        index+=1
    return [True, VALID_REWRITES ]
