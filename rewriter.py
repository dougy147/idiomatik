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

#def rewrite_token_given_all_rules(TOKEN):
#    rewrite_rules, LEFT_PATTERNS, RIGHT_PATTERNS = split_rewrite() # Grab all PUBLIC REWRITE_RULES (left and right patterns)
#    for i in range(len(rewrite_rules)):
#        full_rewrite_token(TOKEN,LEFT_PATTERN[i],RIGHT_PATTERN[i])
#
#def full_rewrite_token(TOKEN,LEFT_PATTERN,RIGHT_PATTERN,INDEX=0,REWRITES=[]):
#    '''Apply a RULE to ALL element of the token matching that specific RULE'''
#    for i in range(INDEX,len(TOKEN)):
#        CUR_RIGHT_PATTERN = [x for x in RIGHT_PATTERN]
#        pattern_in_token = True
#        rewritable_part_of_token = []
#
#        for j in range(len(LEFT_PATTERN)):
#            if i+j >= len(TOKEN): break
#            rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[i+j+1:]]))
#            if LEFT_PATTERN[j][2][0] == 'ANY_STR' and TOKEN[i+j][0] == 'STR':
#                rewritable_part_of_token.append(TOKEN[i+j])
#                for k in range(len(RIGHT_PATTERN)):
#                    if CUR_RIGHT_PATTERN[k][2][0] == 'ANY_STR':
#                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j]
#                        break
#                continue
#            #print(TOKEN)
#            if TOKEN[i+j][1] != LEFT_PATTERN[j][1]:
#                pattern_in_token = False
#                break
#            rewritable_part_of_token.append(TOKEN[i+j])
#
#        if pattern_in_token :
#            if "ANY_STR" in str(CUR_RIGHT_PATTERN) or "OPERAND" in str(CUR_RIGHT_PATTERN) :
#                continue
#                ##return [False, [TOKEN, LEFT_PATTERN, RIGHT_PATTERN] ]
#                #return [False, [TOKEN] ]
#            start_index = i
#            end_index   = i+j
#            rewritable_part = NULL+NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))
#            beginning_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[0:i]]))
#            NEW_TOKEN=beginning_of_proposition+rewritable_part+rest_of_proposition
#            NEW_TOKEN = PARSE(TOKENIZE(NEW_TOKEN))
#            if NEW_TOKEN[0]:
#                new_token = NULL.join(map(str,[x[1] for x in NEW_TOKEN[1]]))
#                if not new_token in REWRITES:
#                    REWRITES.append(new_token)
#                    rewrite_all(NEW_TOKEN[1],LEFT_PATTERN,RIGHT_PATTERN,INDEX=i+j,REWRITES=REWRITES)
#    if INDEX != 0 : return
#    VALID_REWRITES = []
#    index = 0
#    for rew in REWRITES:
#        token = PARSE(TOKENIZE(rew))
#        if token[0] and not token[1] in VALID_REWRITES :
#            VALID_REWRITES.append(token[1])
#        index+=1
#    return [True, VALID_REWRITES ]
#    pass
#
#def parts_rewrite_token(TOKEN,RULE):
#    pass

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

def combine_all_possible_rewrites(TOKEN,POSSIBLE_REWRITES = [False, []],REWRITES=[]):
    '''Returns ALL possible rewrites of a TOKEN given ALL rules'''
    '''WARNING : VERY SLOW WITH LOTS OF RULES, AND MIGHT NOT STOP'''
    ''' POSSIBLE_REWRITES : [True/False, [ [TOKEN0, LEFT, RIGHT, RULE_X], [TOKEN1, LEFT, RIGHT,RULE_Y],... ]]'''
    SPLITTED_RULES = split_all_rewrite_rules() # Grab all PUBLIC REWRITE_RULES (left and right patterns)

    for splitted in SPLITTED_RULES:
        R  = splitted[0] # rule
        LP = splitted[1] # left pattern
        RP = splitted[2] # right pattern
        REWRITTEN = token_full_rewrites_list(TOKEN,LP,RP)
        if not REWRITTEN[0]: continue

        for TRANSFORMATION in REWRITTEN[1]:
            if NULL.join(map(str,[x[1] for x in TRANSFORMATION])) in REWRITES:
                continue
            else :
                REWRITES.append(NULL.join(map(str,[x[1] for x in TRANSFORMATION])))
                POSSIBLE_REWRITES[0] = True
                POSSIBLE_REWRITES[1].append([TRANSFORMATION,LP,RP,R])
            combine_all_possible_rewrites(TRANSFORMATION,REWRITES=REWRITES)
    return POSSIBLE_REWRITES

def token_full_rewrites_list(TOKEN,LEFT_PATTERN,RIGHT_PATTERN,INDEX=0,REWRITES=[]):
    '''Returns ALL possibilities for a TOKEN given a SINGLE REWRITE_RULE LEFT and RIGHT PATTERNS'''
    for i in range(INDEX,len(TOKEN)):
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
                    if CUR_RIGHT_PATTERN[k][2][0] == 'ANY_STR':
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j]
                        break
                continue
            #print(TOKEN)
            if TOKEN[i+j][1] != LEFT_PATTERN[j][1]:
                pattern_in_token = False
                break
            rewritable_part_of_token.append(TOKEN[i+j])

        if pattern_in_token :
            if "ANY_STR" in str(CUR_RIGHT_PATTERN) or "OPERAND" in str(CUR_RIGHT_PATTERN) :
                continue
                ##return [False, [TOKEN, LEFT_PATTERN, RIGHT_PATTERN] ]
                #return [False, [TOKEN] ]
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
                    token_full_rewrites_list(NEW_TOKEN[1],LEFT_PATTERN,RIGHT_PATTERN,INDEX=i+j,REWRITES=REWRITES)
    if INDEX != 0 : return
    VALID_REWRITES = [] # VALID_REWRITES are TOKENS
    index = 0
    for rew in REWRITES:
        token = PARSE(TOKENIZE(rew))
        if token[0] and not token[1] in VALID_REWRITES :
            VALID_REWRITES.append(token[1])
        index+=1
        #print(NULL.join(map(str,[x[1] for x in token[1]])))
    return [True, VALID_REWRITES ]



a = "(((((((c))))))) + b => (~ a)"
a = "~ (A) + (B) + (c) + (d)"
#a = "p => q"
#print("-----------------------")
#print("PROP: {}\n".format(a))
