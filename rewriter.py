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


def silent_surrounding(TOKEN):
    ''' Given precedence of OPERATORS, place "invisibile" parenthesis around
    subexpressions to be solved first.
        TODO special cases :
    - alone minus sign (solve it in parser)
    '''
    operators_in_token = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]
    if operators_in_token == []:
        return TOKEN
    '''Sorting OPERATORS in 2 major steps :
        - OPERATORS with POSITIVE or NULL precedence are sorted :
            * in ASCENDING order for precedence, THEN in ASCENDING order for index (meaning left to right associativity)
        - OPERATORS with NEGATIVE precedence are sorted :
            * in DESCENDING order for precedence, THEN in DESCENDING order for index (meaning right to left associativity)
    '''
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
        # If priority is NON-NULL, operators are surrounded WITH their operands, (so, EXCEPTION for 0 (=, ==, ===))
        if OP[2][3] != 0 :
            cur_operands = check_operands(OP,TOKEN,EXTRACT_OPERAND = True)[1]
            if cur_operands == [] : continue
            lowest_index, highest_index = cur_operands[0][0][3], cur_operands[-1:][0][-1:][0][3]
            # "Special case" for unary operators :
            if OP[2][1] == "unary":
                if OP[2][2] == "R":
                    # Ignore if already surrounded!
                    #print("Current operands:",cur_operands,lowest_index,highest_index)
                    if lowest_index > 0 and highest_index < len(TOKEN) - 1:
                        if  TOKEN[lowest_index-1-1][0] == 'SUR'        and \
                                TOKEN[lowest_index-1-1][2][1] == 'open' and \
                                TOKEN[highest_index+1][0] == 'SUR'       and \
                                TOKEN[highest_index+1][2][1] == 'close' :
                                    #print("Already surrounded :)")
                                    continue
                    TOKEN[lowest_index-1:lowest_index-1] = TOKENIZE("(")
                    TOKEN[highest_index+1+1:highest_index+1+1] = TOKENIZE(")")
                if OP[2][2] == "L":
                    # Ignore if already surrounded!
                    #print("Current operands:",cur_operands,lowest_index,highest_index)
                    if lowest_index > 0 and highest_index < len(TOKEN) - 1:
                        if  TOKEN[lowest_index-1][0] == 'SUR'        and \
                                TOKEN[lowest_index-1][2][1] == 'open' and \
                                TOKEN[highest_index+1+1][0] == 'SUR'   and \
                                TOKEN[highest_index+1+1][2][1] == 'close' :
                                    #print("Already surrounded :)")
                                    continue
                    TOKEN[lowest_index:lowest_index] = TOKENIZE("(")
                    TOKEN[highest_index+1+1+1:highest_index+1+1+1] = TOKENIZE(")")
            else :
                # Ignore if already surrounded!
                #print("Current operands:",cur_operands,lowest_index,highest_index)
                if lowest_index > 0 and highest_index < len(TOKEN) - 1:
                    if  TOKEN[lowest_index-1][0] == 'SUR'        and \
                            TOKEN[lowest_index-1][2][1] == 'open' and \
                            TOKEN[highest_index+1][0] == 'SUR'     and \
                            TOKEN[highest_index+1][2][1] == 'close' :
                                #print("Already surrounded :)")
                                continue
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
                    # TODO Do nothing if already surrounded
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


def split_rewrite_rule(RULE):
    '''Given a REWRITE_RULE, returns a TUPLE of its LEFT and RIGHT PATTERNS'''
    REWRITE_AS_sym = SYMBOLS['OPERATORS'][SYMBOLS['OPERATORS NAMES'].index("REWRITE_AS")]

    rewrite_nb_in_rule = NULL.join(map(str, [x[1] for x in RULE])).count(REWRITE_AS_sym)
    if rewrite_nb_in_rule > 1 :
        print("Multiple rewrites in a single rule not yet supported:\n\tRule '{}'".format(NULL.join(map(str, [x[1] for x in RULE]))))
        #print("Weird behavior expected!")
        return

    # Grabbing left side pattern
    index = 0
    left_pattern = []
    while RULE[index][1] != REWRITE_AS_sym:
        left_pattern.append(RULE[index])
        index+=1
    index+=1
    # Grabbing right side pattern
    right_pattern = []
    while index < len(RULE):
        right_pattern.append(RULE[index])
        index+=1
    return (left_pattern,right_pattern)

def token_rewritable_parts(TOKEN,RULE_INDEX=None,MATCH_INDEX=None):
    '''Returns parts of the token that can be rewritten given ONE rule
    MATCH_INDEX corresponds to the Xth occurrence of a match'''
    REWRITABLE_PARTS = []
    if RULE_INDEX == None :
        print("Please provide a rule to check token rewritable parts.")
        return [False, REWRITABLE_PARTS]
    found_rule = False
    for i in range(len(RULES['REWRITE_RULES'])):
        if str(RULE_INDEX) == str(i) :
            R = RULES['REWRITE_RULES'][i]
            found_rule = True
            break
    if not found_rule :
        print("No rule with index '{}'.".format(RULE_INDEX))
        return [False, REWRITABLE_PARTS] # return False...
    LEFT_PATTERN = split_rewrite_rule(R)[0]
    potential_operands = []
    distance_to_jump = 0 # when adding an operand with more than 1 character, it needs to be jumped
    for i in range(0,len(TOKEN)):
        if len(TOKEN) - i < len(LEFT_PATTERN) : continue # New : avoid "Rule a + b --> c" rewrite "Token a" as "c"
        pattern_in_token = True
        rewritable_part_of_token = []
        found_operand = False
        for j in range(len(LEFT_PATTERN)):
            if i+j+distance_to_jump >= len(TOKEN): break
            #rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[i+j+1+distance_to_jump:]]))
            ''' For ANY_SUR '''
            if LEFT_PATTERN[j][2][0] == 'ANY_OPENING_SUR' and TOKEN[i+j+distance_to_jump][0] == 'SUR':
                if TOKEN[i+j+distance_to_jump][2][1] == 'open':
                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                    continue
                continue
            if LEFT_PATTERN[j][2][0] == 'ANY_CLOSING_SUR' and TOKEN[i+j+distance_to_jump][0] == 'SUR':
                if TOKEN[i+j+distance_to_jump][2][1] == 'close':
                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                    continue
                continue

            ''''''
            ''' ANY STR '''
            if LEFT_PATTERN[j][2][0] == 'ANY_STR' and TOKEN[i+j+distance_to_jump][0] == 'STR':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                continue
            ''' ANY OP '''
            if LEFT_PATTERN[j][2][0] == 'ANY_LR_OP' and \
                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                    TOKEN[i+j+distance_to_jump][2][2] == 'LR':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                continue
            if LEFT_PATTERN[j][2][0] == 'ANY_L_OP' and \
                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                    TOKEN[i+j+distance_to_jump][2][2] == 'L':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                continue
            if LEFT_PATTERN[j][2][0] == 'ANY_R_OP' and \
                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                    TOKEN[i+j+distance_to_jump][2][2] == 'R':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                continue
            ''' ANY_OPERAND '''
            if LEFT_PATTERN[j][2][0] == 'ANY_OPERAND':
                OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]
                for OP in OPS:
                    operands_from_this_point_in_token = check_operands(OP,TOKEN,EXTRACT_OPERAND = True,ERROR_LOG = False)[1]
                    for operands in operands_from_this_point_in_token:
                        potential_operands.append(operands)
                if not TOKEN[i+j+distance_to_jump] in map(list,[x[0] for x in potential_operands]) :
                    break
                    found_operand = False
                else :
                    found_operand = True
                #--------------------------
                # Check if next OR prev in LEFT_PATTERN is 0-precedence operator
                next_is_zero_precedence_op = False
                prev_is_zero_precedence_op = False
                if j+1 < len(LEFT_PATTERN) and \
                        LEFT_PATTERN[j+1][0] == 'OP' and \
                        LEFT_PATTERN[j+1][2][3] == 0:
                            next_is_zero_precedence_op = True
                if j-1 >= 0 and \
                        LEFT_PATTERN[j-1][0] == 'OP' and \
                        LEFT_PATTERN[j-1][2][3] == 0:
                            prev_is_zero_precedence_op = True
                # Check if we are looking for a 0-precedence operator's operand
                if next_is_zero_precedence_op: 
                    for potential in potential_operands:
                        end_potential_index_in_token = potential[len(potential)-1][3]
                        if end_potential_index_in_token + 1 >= len(TOKEN):
                            continue
                        elif TOKEN[end_potential_index_in_token + 1][0] == 'OP' and   \
                                TOKEN[end_potential_index_in_token + 1][2][3] == 0 and \
                                TOKEN[i+j+distance_to_jump] in potential:
                            distance_to_jump += (len(potential) - 1)
                            found_operand = True
                            for elem in potential:
                                rewritable_part_of_token.append(elem)
                            break
                        else: continue
                    if found_operand: continue
                if prev_is_zero_precedence_op:
                    for potential in potential_operands:
                        start_potential_index_in_token = potential[0][3]
                        if start_potential_index_in_token - 1 < 0 :
                            continue
                        elif TOKEN[start_potential_index_in_token - 1][0] == 'OP' and   \
                                TOKEN[start_potential_index_in_token - 1][2][3] == 0 and \
                                TOKEN[i+j+distance_to_jump] in potential:
                            distance_to_jump += (len(potential) - 1)
                            found_operand = True
                            for elem in potential:
                                rewritable_part_of_token.append(elem)
                            break
                        else: continue
                    if found_operand: continue
                ## -------------------------------------------------------------
                if found_operand :
                    for potential in potential_operands:
                        if [TOKEN[i+j+distance_to_jump]] == potential : # notice the [] around TOKEN : [TOKEN]
                            found_operand = True
                            rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                            break
                        else :
                            found_operand = False
                    if found_operand == False :
                        for potential in potential_operands:
                            if TOKEN[i+j+distance_to_jump] == potential[0] :
                                distance_to_jump += (len(potential) - 1)
                                found_operand = True
                                for elem in potential:
                                    rewritable_part_of_token.append(elem)
                                break
                if found_operand: continue
            ''''''
            if i+j+distance_to_jump >= len(TOKEN) :
                break
            if TOKEN[i+j+distance_to_jump][1] != LEFT_PATTERN[j][1]:
                pattern_in_token = False
                break
            rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
        if pattern_in_token and rewritable_part_of_token != [] :
            REWRITABLE_PARTS.append([rewritable_part_of_token,R])
        distance_to_jump = 0
    return [True, REWRITABLE_PARTS]

def token_all_rewritable_parts(TOKEN,MATCH_INDEX=None):
    '''Returns parts of the token that can be rewritten given ALL rules LEFT_PATTERN'''
    REWRITABLE_PARTS=[]
    SPLITTED_RULES = split_all_rewrite_rules() # Grab all PUBLIC REWRITE_RULES (left and right patterns)
    counter = -1
    for splitted in SPLITTED_RULES:
        counter += 1
        # ... allow skeeping index
        if MATCH_INDEX != None :
            if counter != MATCH_INDEX: continue
        # ...
        R  = splitted[0] # rule
        LEFT_PATTERN = splitted[1] # left pattern
        potential_operands = []
        distance_to_jump = 0 # when adding an operand with more than 1 character, it needs to be jumped
        for i in range(0,len(TOKEN)):
            if len(TOKEN) - i < len(LEFT_PATTERN) : continue # New : avoid "Rule a + b --> c" rewrite "Token a" as "c"
            pattern_in_token = True
            rewritable_part_of_token = []
            for j in range(len(LEFT_PATTERN)):
                if i+j+distance_to_jump >= len(TOKEN): break
                rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[i+j+1+distance_to_jump:]]))
                ''' For ANY_SUR '''
                if LEFT_PATTERN[j][2][0] == 'ANY_OPENING_SUR' and TOKEN[i+j+distance_to_jump][0] == 'SUR':
                    if TOKEN[i+j+distance_to_jump][2][1] == 'open':
                        rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                        continue
                    continue
                if LEFT_PATTERN[j][2][0] == 'ANY_CLOSING_SUR' and TOKEN[i+j+distance_to_jump][0] == 'SUR':
                    if TOKEN[i+j+distance_to_jump][2][1] == 'close':
                        rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                        continue
                    continue
                ''''''
                ''' ANY_STR '''
                if LEFT_PATTERN[j][2][0] == 'ANY_STR' and TOKEN[i+j+distance_to_jump][0] == 'STR':
                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                    continue
                ''' ANY OP '''
                if LEFT_PATTERN[j][2][0] == 'ANY_LR_OP' and \
                        TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                        TOKEN[i+j+distance_to_jump][2][2] == 'LR':
                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                    continue
                if LEFT_PATTERN[j][2][0] == 'ANY_L_OP' and \
                        TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                        TOKEN[i+j+distance_to_jump][2][2] == 'L':
                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                    continue
                if LEFT_PATTERN[j][2][0] == 'ANY_R_OP' and \
                        TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                        TOKEN[i+j+distance_to_jump][2][2] == 'R':
                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                    continue
                ''' ANY_OPERAND '''
                if LEFT_PATTERN[j][2][0] == 'ANY_OPERAND':
                    OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]
                    for OP in OPS:
                        operands_from_this_point_in_token = check_operands(OP,TOKEN,EXTRACT_OPERAND = True,ERROR_LOG = False)[1]
                        for operands in operands_from_this_point_in_token:
                            potential_operands.append(operands)
                    if not TOKEN[i+j+distance_to_jump] in map(list,[x[0] for x in potential_operands]) :
                        found_operand = False
                    else :
                        found_operand = True
                    #--------------------------
                    # Check if next OR prev in LEFT_PATTERN is 0-precedence operator
                    next_is_zero_precedence_op = False
                    prev_is_zero_precedence_op = False
                    if j+1 < len(LEFT_PATTERN) and \
                            LEFT_PATTERN[j+1][0] == 'OP' and \
                            LEFT_PATTERN[j+1][2][3] == 0:
                                next_is_zero_precedence_op = True
                    if j-1 >= 0 and \
                            LEFT_PATTERN[j-1][0] == 'OP' and \
                            LEFT_PATTERN[j-1][2][3] == 0:
                                prev_is_zero_precedence_op = True
                    # Check if we are looking for a 0-precedence operator's operand
                    if next_is_zero_precedence_op: 
                        for potential in potential_operands:
                            end_potential_index_in_token = potential[len(potential)-1][3]
                            if end_potential_index_in_token + 1 >= len(TOKEN):
                                continue
                            elif TOKEN[end_potential_index_in_token + 1][0] == 'OP' and   \
                                    TOKEN[end_potential_index_in_token + 1][2][3] == 0 and \
                                    TOKEN[i+j+distance_to_jump] in potential:
                                distance_to_jump += (len(potential) - 1)
                                found_operand = True
                                for elem in potential:
                                    rewritable_part_of_token.append(elem)
                                break
                            else: continue
                        if found_operand: continue
                    if prev_is_zero_precedence_op:
                        for potential in potential_operands:
                            start_potential_index_in_token = potential[0][3]
                            if start_potential_index_in_token - 1 < 0 :
                                continue
                            elif TOKEN[start_potential_index_in_token - 1][0] == 'OP' and   \
                                    TOKEN[start_potential_index_in_token - 1][2][3] == 0 and \
                                    TOKEN[i+j+distance_to_jump] in potential:
                                distance_to_jump += (len(potential) - 1)
                                found_operand = True
                                for elem in potential:
                                    rewritable_part_of_token.append(elem)
                                break
                            else: continue
                        if found_operand: continue
                    ## -------------------------------------------------------------
                    if found_operand :
                        for potential in potential_operands:
                            if [TOKEN[i+j+distance_to_jump]] == potential : # notice the [] around TOKEN : [TOKEN]
                                found_operand = True
                                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                                break
                            else :
                                found_operand = False
                        if found_operand == False :
                            for potential in potential_operands:
                                if TOKEN[i+j+distance_to_jump] == potential[0] :
                                    distance_to_jump += (len(potential) - 1)
                                    found_operand = True
                                    for elem in potential:
                                        rewritable_part_of_token.append(elem)
                                    break
                    if found_operand: continue
                ''''''
                if i+j+distance_to_jump >= len(TOKEN) :
                    break
                if TOKEN[i+j+distance_to_jump][1] != LEFT_PATTERN[j][1]:
                    pattern_in_token = False
                    break
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
            if pattern_in_token and rewritable_part_of_token != [] :
                REWRITABLE_PARTS.append([rewritable_part_of_token,R])
            distance_to_jump = 0
    return REWRITABLE_PARTS

def str_rewrites_given_a_rule(TOKEN,RULE_INDEX=None,MATCH_INDEX=None):
    STR_REWRITES = []
    token = TOKEN
    parse = PARSE(token)
    if not parse[0] :
        return STR_REWRITES
    RULE = RULES['REWRITE_RULES'][int(RULE_INDEX)]
    check = rewrite_given_a_rule(token,RULE,MATCH_INDEX=MATCH_INDEX)
    if not check[0] :
        return STR_REWRITES
    REWRITES = check[1]
    for rew in REWRITES:
        str_rewrite = rew
        if not str_rewrite in STR_REWRITES :
            STR_REWRITES.append(rew)
    return STR_REWRITES

def rewrite_given_a_rule(TOKEN,RULE,MATCH_INDEX=None):
    '''Returns ALL possible rewrites for a SINGLE rule
    or rewrite for specific index (match number)'''
    POSSIBLE_REWRITES = [False, []]
    REWRITES = []
    R = RULE
    LP, RP = split_rewrite_rule(R)
    REWRITTEN = combine_all_possible_rewrites(TOKEN,RULE=R,MATCH_INDEX=MATCH_INDEX)
    if not REWRITTEN[0]: return [ POSSIBLE_REWRITES, REWRITES ]

    for TRANSFORMATION in REWRITTEN[1]:
        if TRANSFORMATION in REWRITES:
            continue
        else :
            REWRITES.append(TRANSFORMATION)
            POSSIBLE_REWRITES[0] = True
            POSSIBLE_REWRITES[1].append([PARSE(TOKENIZE(TRANSFORMATION))[1],LP,RP,R])
    return [ POSSIBLE_REWRITES[0], REWRITES ]


'''WARNING : functions below allow to recursively check if a rule can be subrewritten.
They might never stop, and I found no way to contourn this issue for the moment (dumb)'''

def combine_all_possible_rewrites(TOKEN,RULE = None,POSSIBLE_REWRITES = None,REWRITES=None,first_time=True,RECURSION=0,RECURSION_EXCEEDED=False,MATCH_INDEX=None):
    '''Returns ALL possible rewrites for ALL TOKENS given ALL rules'''
    '''WARNING : VERY SLOW WITH LOTS OF RULES, AND MIGHT NOT STOP'''
    ''' POSSIBLE_REWRITES : [True/False, [ [TOKEN0, LEFT, RIGHT, RULE_X], [TOKEN1, LEFT, RIGHT,RULE_Y],... ]]'''
    RECURSION_LIMIT=50
    if RECURSION >= RECURSION_LIMIT:
        print("Recursion limit ({}) exceeded in 'combine_all_possible_rewrites()'!".format(RECURSION_LIMIT))
        RECURSION_EXCEEDED = True
        return

    if RULE == None :
        SPLITTED_RULES = split_all_rewrite_rules() # Grab all PUBLIC REWRITE_RULES (left and right patterns)
    else :
        SPLITTED_RULES = [[RULE,split_rewrite_rule(RULE)[0],split_rewrite_rule(RULE)[1]]]

    if POSSIBLE_REWRITES == None: POSSIBLE_REWRITES = [False, []]
    if REWRITES == None: REWRITES = []

    for splitted in SPLITTED_RULES:
        R  = splitted[0] # rule
        LP = splitted[1] # left pattern
        RP = splitted[2] # right pattern
        REWRITTEN = token_full_rewrites_list(TOKEN,LP,RP,MATCH_INDEX=MATCH_INDEX)
        if not REWRITTEN[0]: continue

        for TRANSFORMATION in REWRITTEN[1]:
            if NULL.join(map(str,[x[1] for x in TRANSFORMATION])) in REWRITES:
                continue
            else :
                REWRITES.append(NULL.join(map(str,[x[1] for x in TRANSFORMATION])))
                POSSIBLE_REWRITES[0] = True
                POSSIBLE_REWRITES[1].append([TRANSFORMATION,LP,RP,R])
            if RULE == None:
                combine_all_possible_rewrites(TRANSFORMATION,REWRITES=REWRITES,first_time=False,RECURSION=RECURSION+1)
    return [ POSSIBLE_REWRITES[0], REWRITES ]


def token_full_rewrites_list(TOKEN,LEFT_PATTERN,RIGHT_PATTERN,INDEX=0,REWRITES=None,first_time=True,RECURSION=0,RECURSION_EXCEEDED=False,MATCH_INDEX=None):
    '''Returns ALL possibilities for a TOKEN given a SINGLE REWRITE_RULE LEFT and RIGHT PATTERNS'''
    counter = -1
    RECURSION_LIMIT=50
    potential_operands = []
    if RECURSION >= RECURSION_LIMIT:
        RECURSION_EXCEEDED = True
        return
    if REWRITES is None: REWRITES = []

    i = INDEX - 1
    #for i in range(INDEX,len(TOKEN)):
    while i < len(TOKEN) :
        i+=1

        number_of_optional_characters_in_left_pattern = NULL.join(map(str, [x[2][0] for x in LEFT_PATTERN])).count("OPTIONAL")
        if len(TOKEN) - i + number_of_optional_characters_in_left_pattern < len(LEFT_PATTERN) :
            continue # New : avoid "Rule a + b ::= c" rewrite "Token a" as "c"

        CUR_RIGHT_PATTERN = [x for x in RIGHT_PATTERN]
        CUR_LEFT_PATTERN = [x for x in LEFT_PATTERN]
        pattern_in_token = True
        rewritable_part_of_token = []
        distance_to_jump = 0 # when adding an operand with more than 1 character, it needs to be jumped
        found_operand = False

        ''' Create a dictionnary of replacable variables in rule to check if they are equal in some cases '''
        any_str_dict      = {}
        any_operands_dict = {}
        any_exp_dict      = {}

        j = -1
        #for j in range(len(CUR_LEFT_PATTERN)):
        while j < len(CUR_LEFT_PATTERN):
            j+=1
            if j >= len(CUR_LEFT_PATTERN) : continue
            if i+j+distance_to_jump >= len(TOKEN):
                #print("Leaving here... ADIOS!")
                #print(f"i={i}, j={j}, distance_to_jump={distance_to_jump}, len(TOKEN)={len(TOKEN)}")
                if found_operand : break
                pattern_in_token = False
                break
            rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[i+j+1+distance_to_jump:]]))

            #''' For OPTIONAL '''
            #print(f"{TOKEN[i+j+distance_to_jump]}")
            #print(f"{CUR_LEFT_PATTERN[j]}")
            #if CUR_LEFT_PATTERN[j][2][0] == 'OPTIONAL_OPENING_SUR' :
            #    print("OPTIONAL_OPENING_SUR")
            #    if TOKEN[i+j+distance_to_jump][0] == 'SUR':
            #        if TOKEN[i+j+distance_to_jump][2][1] == 'open':
            #            rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
            #            continue
            #    else:
            #        CUR_LEFT_PATTERN.pop(j)
            #        print(CUR_LEFT_PATTERN)
            #        j-=1
            #        continue
            #if CUR_LEFT_PATTERN[j][2][0] == 'OPTIONAL_CLOSING_SUR' :
            #    print("OPTIONAL_CLOSING_SUR")
            #    if TOKEN[i+j+distance_to_jump][0] == 'SUR':
            #        if TOKEN[i+j+distance_to_jump][2][1] == 'close':
            #            rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
            #            continue
            #    else:
            #        CUR_LEFT_PATTERN.pop(j)
            #        print(CUR_LEFT_PATTERN)
            #        j-=1
            #        continue
            #''''''

            ''' For ANY_SUR '''
            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_OPENING_SUR' and TOKEN[i+j+distance_to_jump][0] == 'SUR':
                if TOKEN[i+j+distance_to_jump][2][1] == 'open':
                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                    continue
                continue
            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_CLOSING_SUR' and TOKEN[i+j+distance_to_jump][0] == 'SUR':
                if TOKEN[i+j+distance_to_jump][2][1] == 'close':
                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                    continue
                continue

            ''''''

            ''' For ANY_STR '''
            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_STR' and TOKEN[i+j+distance_to_jump][0] == 'STR':
                if not CUR_LEFT_PATTERN[j][1] in any_str_dict :
                    any_str_dict[CUR_LEFT_PATTERN[j][1]] = TOKEN[i+j+distance_to_jump][1]
                else :
                    if TOKEN[i+j+distance_to_jump][1] != any_str_dict[CUR_LEFT_PATTERN[j][1]] :
                        pattern_in_token = False
                        break
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                for k in range(len(CUR_RIGHT_PATTERN)):
                    if CUR_RIGHT_PATTERN[k][2][0] == 'ANY_STR' and CUR_RIGHT_PATTERN[k][1] == CUR_LEFT_PATTERN[j][1] :
                        #CUR_RIGHT_PATTERN[k] = TOKEN[i+j]
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
                        continue
                continue

            ''' For ANY_OPERATOR '''
            ''' LR '''
            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_LR_OP' and \
                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                    TOKEN[i+j+distance_to_jump][2][2] == 'LR':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                for k in range(len(CUR_RIGHT_PATTERN)):
                    if CUR_RIGHT_PATTERN[k][1] == CUR_LEFT_PATTERN[j][1] :
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
                        break # break?
                continue
            ''' L (unary) '''
            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_L_OP' and \
                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                    TOKEN[i+j+distance_to_jump][2][2] == 'L':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                for k in range(len(CUR_RIGHT_PATTERN)):
                    if CUR_RIGHT_PATTERN[k][1] == CUR_LEFT_PATTERN[j][1] :
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
                        break # break?
                continue
            ''' R (unary) '''
            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_R_OP' and \
                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                    TOKEN[i+j+distance_to_jump][2][2] == 'R':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                for k in range(len(CUR_RIGHT_PATTERN)):
                    if CUR_RIGHT_PATTERN[k][1] == CUR_LEFT_PATTERN[j][1] :
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
                        break # break?
                continue

            ''' For ANY_OPERAND '''
            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_OPERAND':
                #--------------------------
                # Check if next OR prev in CUR_LEFT_PATTERN is 0-precedence operator
                next_is_zero_precedence_op = False
                prev_is_zero_precedence_op = False
                if j+1 < len(CUR_LEFT_PATTERN) and \
                        CUR_LEFT_PATTERN[j+1][0] == 'OP' and \
                        CUR_LEFT_PATTERN[j+1][2][3] == 0:
                            next_is_zero_precedence_op = True
                if j-1 >= 0 and \
                        CUR_LEFT_PATTERN[j-1][0] == 'OP' and \
                        CUR_LEFT_PATTERN[j-1][2][3] == 0:
                            prev_is_zero_precedence_op = True
                #--------------------------

                rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))
                OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]

                for OP in OPS:
                    operands_from_this_point_in_token = check_operands(OP,TOKEN,EXTRACT_OPERAND = True,ERROR_LOG = False)[1]
                    for operands in operands_from_this_point_in_token:
                        potential_operands.append(operands)
                if not TOKEN[i+j+distance_to_jump] in map(list,[x[0] for x in potential_operands]) :
                    found_operand = False
                    break # If current token not in any operand, break

                found_operand = False
                unmatched = False

                # -------------------------------------------------------------
                # Check if we are looking for a 0-precedence operator's operand
                if next_is_zero_precedence_op: 
                    for potential in potential_operands:
                        #print("----------")
                        #print(f"potential : {potential}")
                        #print(f"TOKEN[i+j+distance_to_jump] : {TOKEN[i+j+distance_to_jump]}")
                        #start_potential_index_in_token = potential[0][3]
                        end_potential_index_in_token = potential[len(potential)-1][3]
                        if end_potential_index_in_token + 1 >= len(TOKEN):
                            #found_operand = False
                            continue
                        elif TOKEN[end_potential_index_in_token + 1][0] == 'OP' and   \
                                TOKEN[end_potential_index_in_token + 1][2][3] == 0 and \
                                TOKEN[i+j+distance_to_jump] in potential:
                            distance_to_jump += (len(potential) - 1)
                            rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))
                            found_operand = True
                            str_potential = NULL.join(map(str,[x[1] for x in potential]))
                            if not CUR_LEFT_PATTERN[j][1] in any_operands_dict :
                                any_operands_dict[CUR_LEFT_PATTERN[j][1]] = str_potential
                            else :
                                if str_potential != any_operands_dict[CUR_LEFT_PATTERN[j][1]] :
                                    distance_to_jump -= (len(potential) - 1)
                                    pattern_in_token = False
                                    unmatched = True
                                    #print("(next) unmatch")
                                    continue
                            #print(f"(next) Would be that one : {str_potential}")
                            for elem in potential:
                                rewritable_part_of_token.append(elem)
                            m = -1
                            while m < len(CUR_RIGHT_PATTERN):
                                m+=1
                                if m >= len(CUR_RIGHT_PATTERN) : break
                                if CUR_RIGHT_PATTERN[m][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[m][1] == CUR_LEFT_PATTERN[j][1] :
                                    CUR_RIGHT_PATTERN.pop(m)
                                    for elem in reversed(potential):
                                        CUR_RIGHT_PATTERN[m:m] = [elem]
                            #print(f"(next) did it : CUR_RIGHT_PATTERN = {CUR_RIGHT_PATTERN}")
                            break
                        else: continue

                if prev_is_zero_precedence_op:
                    #print("prev is zero precedence")
                    for potential in potential_operands:
                        start_potential_index_in_token = potential[0][3]
                        if start_potential_index_in_token - 1 < 0 :
                            continue
                        elif TOKEN[start_potential_index_in_token - 1][0] == 'OP' and   \
                                TOKEN[start_potential_index_in_token - 1][2][3] == 0 and \
                                TOKEN[i+j+distance_to_jump] in potential:
                            distance_to_jump += (len(potential) - 1)
                            rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))
                            found_operand = True
                            str_potential = NULL.join(map(str,[x[1] for x in potential]))
                            #print(f"(prev) Would be that one : {str_potential}")
                            if not CUR_LEFT_PATTERN[j][1] in any_operands_dict :
                                any_operands_dict[CUR_LEFT_PATTERN[j][1]] = str_potential
                            else :
                                if str_potential != any_operands_dict[CUR_LEFT_PATTERN[j][1]] :
                                    #print("(prev) unmatch")
                                    distance_to_jump -= (len(potential) - 1)
                                    pattern_in_token = False
                                    unmatched = True
                                    continue
                            for elem in potential:
                                rewritable_part_of_token.append(elem)
                            m = -1
                            while m < len(CUR_RIGHT_PATTERN):
                                m+=1
                                if m >= len(CUR_RIGHT_PATTERN) : break
                                if CUR_RIGHT_PATTERN[m][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[m][1] == CUR_LEFT_PATTERN[j][1] :
                                    CUR_RIGHT_PATTERN.pop(m)
                                    for elem in reversed(potential):
                                        CUR_RIGHT_PATTERN[m:m] = [elem]
                            #print(f"(prev) did it : CUR_RIGHT_PATTERN = {CUR_RIGHT_PATTERN}")
                            break
                        else: continue

                if found_operand: continue
                ## -------------------------------------------------------------

                for potential in potential_operands:
                    ''' For TOKEN[i+j+distance_to_jump] that are EQUAL to an OPERAND '''
                    if [TOKEN[i+j+distance_to_jump]] == potential : # notice the [] around TOKEN : [TOKEN]
                        found_operand = True

                        str_potential = NULL.join(map(str,[x[1] for x in potential]))
                        if not CUR_LEFT_PATTERN[j][1] in any_operands_dict :
                            any_operands_dict[CUR_LEFT_PATTERN[j][1]] = str_potential
                        else :
                            if str_potential != any_operands_dict[CUR_LEFT_PATTERN[j][1]] :
                                pattern_in_token = False
                                unmatched = True
                                break
                        if unmatched : break

                        rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                        for l in range(len(CUR_RIGHT_PATTERN)):
                            if CUR_RIGHT_PATTERN[l][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[l][1] == CUR_LEFT_PATTERN[j][1] :
                                CUR_RIGHT_PATTERN[l] = TOKEN[i+j+distance_to_jump]
                        break

                if found_operand: continue

                for potential in potential_operands:
                    ''' For TOKEN[i+j+distance_to_jump] that START an OPERAND '''
                    if TOKEN[i+j+distance_to_jump] == potential[0] :
                        distance_to_jump += (len(potential) - 1)
                        rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))

                        found_operand = True

                        str_potential = NULL.join(map(str,[x[1] for x in potential]))
                        if not CUR_LEFT_PATTERN[j][1] in any_operands_dict :
                            any_operands_dict[CUR_LEFT_PATTERN[j][1]] = str_potential
                        else :
                            if str_potential != any_operands_dict[CUR_LEFT_PATTERN[j][1]] :
                                pattern_in_token = False
                                unmatched = True
                                break
                        if unmatched : break

                        for elem in potential:
                            rewritable_part_of_token.append(elem)

                        m = -1
                        #for m in range(len(CUR_RIGHT_PATTERN)):
                        while m < len(CUR_RIGHT_PATTERN):
                            m+=1
                            if m >= len(CUR_RIGHT_PATTERN) : break
                            if CUR_RIGHT_PATTERN[m][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[m][1] == CUR_LEFT_PATTERN[j][1] :
                                CUR_RIGHT_PATTERN.pop(m)
                                for elem in reversed(potential):
                                    CUR_RIGHT_PATTERN[m:m] = [elem]
                        #print(f">> CUR_RIGHT_PATTERN : {NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))}")
                        break
                #print(f"CUR_RIGHT_PATTERN : {NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))}")
                if found_operand: continue

            ''' '''
            ''' ----------------------- '''
            ''' Add ANY_EXPRESSION (test)'''
            #if CUR_LEFT_PATTERN[j][2][0] == 'ANY_VALID_EXP':
            #    print("Investigating 'ANY_VALID_EXP'")
            #    # Investigating forward
            #    token_end_index = len(TOKEN) + 1
            #    #time_to_check_backward = False
            #    while token_end_index >= 0 :
            #        token_end_index -= 1
            #        if token_end_index < 0 :
            #            print("No valid expression found in the rest of the token.")
            #            #pattern_in_token = False
            #            time_to_check_backward = True
            #            break
            #        exp_token = NULL.join(map(str,[x[1] for x in TOKEN[i+j+distance_to_jump:token_end_index]]))
            #        print(f"exp_token: {exp_token}")
            #        if PARSE(TOKENIZE(exp_token))[0] and exp_token != "" :
            #            print("Testing token : '{}'".format(exp_token))
            #            print("Valid expression from index '{}' to '{}'.".format(i+j+distance_to_jump,token_end_index))
            #            print("Accepted token : '{}'".format(exp_token))
            #            if i+j+distance_to_jump+token_end_index+1 >= len(TOKEN):
            #                print("whole rest of token taken")
            #                if j == len(CUR_LEFT_PATTERN) - 1 :
            #                    print("cool, the whole rest of the token is accepted.")
            #                    for x in range(i+j+distance_to_jump,token_end_index):
            #                        if x >= len(TOKEN): continue
            #                        print("Appending '{}'".format(TOKEN[x]))
            #                        rewritable_part_of_token.append(TOKEN[x])
            #                    pattern_in_token = True
            #                    distance_to_jump += token_end_index
            #                    rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:token_end_index]]))
            #                    #rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1+token_end_index:]]))
            #                    break
            #                elif j != len(CUR_LEFT_PATTERN)-1 :
            #                    print("not reached the end of CUR_LEFT_PATTERN")
            #                    pattern_in_token = True
            #                    for x in range(i+j+distance_to_jump,token_end_index):
            #                        if x >= len(TOKEN): continue
            #                        print("Appending '{}'".format(TOKEN[x]))
            #                        rewritable_part_of_token.append(TOKEN[x])
            #                    distance_to_jump += token_end_index
            #                    rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:token_end_index]]))
            #                    #rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1+token_end_index:]]))
            #                    print(f"rewritable_part_of_token: {rewritable_part_of_token}")
            #                    #print(f"rest_of_proposition: {rest_of_proposition}")
            #                    break
            #                else :
            #                    print("PERFECT!")
            #            elif i+j+distance_to_jump+token_end_index+1 >= len(TOKEN) or j + 1 >= len(CUR_LEFT_PATTERN):
            #                print("too big of an index!")
            #                continue
            #            elif TOKEN[i+j+distance_to_jump+token_end_index+1][1] != CUR_LEFT_PATTERN[j+1][1]:
            #                print("No match for next index!")
            #                continue
            #            #break
            #        else: continue
            #    #if pattern_in_token == False: continue
            #    continue
            ''''''

            #print(f"rewritable_part_of_token: {rewritable_part_of_token}")

            if i+j+distance_to_jump >= len(TOKEN) :
                #print("breaking here")
                break

            if TOKEN[i+j+distance_to_jump][1] != CUR_LEFT_PATTERN[j][1] : # and was not ANY_OPERAND?
                #print("breaking there")
                pattern_in_token = False
                break

            if found_operand == False:
                #print("operand not found : appending ")
                rewritable_part_of_token.append(TOKEN[i+j])

        ''' End of j range . Inside of i range .'''

        if i+j+distance_to_jump >= (len(TOKEN) - 1) and j < len(CUR_LEFT_PATTERN) - 1:
            pattern_in_token = False
            continue

        if pattern_in_token and rewritable_part_of_token != [] :
            #if "ANY_STR" in str(CUR_RIGHT_PATTERN) or "ANY_OPERAND" in str(CUR_RIGHT_PATTERN) or "ANY_VALID_EXP" in str(CUR_RIGHT_PATTERN) : continue
            if "ANY_STR" in str(CUR_RIGHT_PATTERN) or "ANY_OPERAND" in str(CUR_RIGHT_PATTERN) : continue

            rewritable_part = NULL+NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))
            beginning_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[0:i]]))
            distance_to_jump = 0

            NEW_TOKEN=beginning_of_proposition+rewritable_part+rest_of_proposition
            NEW_TOKEN = PARSE(TOKENIZE(NEW_TOKEN),ERROR_LOG = False)

            if NEW_TOKEN[0]:
                new_token = NULL.join(map(str,[x[1] for x in NEW_TOKEN[1]]))
                if not new_token in REWRITES:
                    counter += 1
                    if MATCH_INDEX != None and MATCH_INDEX != counter : continue # ignore if asked another index
                    REWRITES.append(new_token)
                    if MATCH_INDEX != None : continue
                    token_full_rewrites_list(NEW_TOKEN[1],LEFT_PATTERN,RIGHT_PATTERN,INDEX=i+j,REWRITES=REWRITES,RECURSION=RECURSION+1,RECURSION_EXCEEDED=RECURSION_EXCEEDED)
    if INDEX != 0 : return
    VALID_REWRITES = [] # VALID_REWRITES are TOKENS
    index = 0
    for rew in REWRITES:
        #counter += 1
        token = PARSE(TOKENIZE(rew))
        if token[0] and not token[1] in VALID_REWRITES :
            VALID_REWRITES.append(token[1])
        index+=1
    return [True, VALID_REWRITES ]


# Saved function 18.10.2023
#def token_full_rewrites_list(TOKEN,LEFT_PATTERN,RIGHT_PATTERN,INDEX=0,REWRITES=None,first_time=True,RECURSION=0,RECURSION_EXCEEDED=False,MATCH_INDEX=None):
#    '''Returns ALL possibilities for a TOKEN given a SINGLE REWRITE_RULE LEFT and RIGHT PATTERNS'''
#    counter = -1
#    RECURSION_LIMIT=50
#    potential_operands = []
#    if RECURSION >= RECURSION_LIMIT:
#        RECURSION_EXCEEDED = True
#        return
#    if REWRITES is None: REWRITES = []
#    #for i in range(INDEX,len(TOKEN)):
#    ''' Create a dictionnary of replacable variables in rule to check if they are equal in some cases '''
#    any_str_dict      = {}
#    any_operands_dict = {}
#    any_exp_dict      = {}
#
#    i = INDEX - 1
#    while i < len(TOKEN):
#        i+=1
#        number_optionals_left_pattern = NULL.join(map(str, [x[2][0] for x in LEFT_PATTERN])).count("OPTIONAL") # nb of optionals in left_pattern
#        if len(TOKEN) - i + number_optionals_left_pattern < len(LEFT_PATTERN) :
#            print(f"skeeping. i={i}")
#            continue # New : avoid "Rule a + b ::= c" rewrite "Token a" as "c"
#        print(f"checking TOKEN[{i}]: {TOKEN[i]}")
#
#        CUR_RIGHT_PATTERN = [x for x in RIGHT_PATTERN]
#        CUR_LEFT_PATTERN  = [x for x in LEFT_PATTERN]
#        pattern_in_token  = True
#        rewritable_part_of_token = []
#        distance_to_jump = 0 # when adding an operand with more than 1 character, it needs to be jumped
#        found_operand = False
#
#        #''' Create a dictionnary of replacable variables in rule to check if they are equal in some cases '''
#        #any_str_dict      = {}
#        #any_operands_dict = {}
#        #any_exp_dict      = {}
#
#        j = -1
#        while j < len(CUR_LEFT_PATTERN):
#            j+=1
#            if j >= len(CUR_LEFT_PATTERN): break
#            if "OPTIONAL" in CUR_LEFT_PATTERN[j][2][0] and i+j+distance_to_jump >= len(TOKEN): break
#            if i+j+distance_to_jump >= len(TOKEN) :
#                #print("Leaving here... ADIOS!")
#                #print(f"i={i}, j={j}, distance_to_jump={distance_to_jump}, len(TOKEN)={len(TOKEN)}")
#                if found_operand : break
#                pattern_in_token = False
#                break
#
#            rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[i+j+1+distance_to_jump:]]))
#
#            ''' For OPTIONAL '''
#            # Start again...
#            ''''''
#
#            ''' For ANY_SUR '''
#            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_OPENING_SUR' and TOKEN[i+j+distance_to_jump][0] == 'SUR':
#                if TOKEN[i+j+distance_to_jump][2][1] == 'open':
#                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
#                    continue
#                continue
#            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_CLOSING_SUR' and TOKEN[i+j+distance_to_jump][0] == 'SUR':
#                if TOKEN[i+j+distance_to_jump][2][1] == 'close':
#                    rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
#                    continue
#                continue
#
#            ''''''
#
#            ''' For ANY_STR '''
#            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_STR' and TOKEN[i+j+distance_to_jump][0] == 'STR':
#                if not CUR_LEFT_PATTERN[j][1] in any_str_dict :
#                    any_str_dict[CUR_LEFT_PATTERN[j][1]] = TOKEN[i+j+distance_to_jump][1]
#                else :
#                    if TOKEN[i+j+distance_to_jump][1] != any_str_dict[CUR_LEFT_PATTERN[j][1]] :
#                        pattern_in_token = False
#                        break
#                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
#                for k in range(len(CUR_RIGHT_PATTERN)):
#                    if CUR_RIGHT_PATTERN[k][2][0] == 'ANY_STR' and CUR_RIGHT_PATTERN[k][1] == CUR_LEFT_PATTERN[j][1] :
#                        #CUR_RIGHT_PATTERN[k] = TOKEN[i+j]
#                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
#                        continue
#                continue
#
#            ''' For ANY_OPERATOR '''
#            ''' LR '''
#            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_LR_OP' and \
#                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
#                    TOKEN[i+j+distance_to_jump][2][2] == 'LR':
#                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
#                any_op_in_remaining_left_pattern  = NULL.join(map(str, [x[2][0] for x in CUR_LEFT_PATTERN[j:]])).count("ANY_LR_OP") - 1
#                for k in range(len(CUR_RIGHT_PATTERN)):
#                    if CUR_RIGHT_PATTERN[k][1] == CUR_LEFT_PATTERN[j][1] :
#                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
#                        if any_op_in_remaining_left_pattern <= 0 : continue
#                        break
#                continue
#            ''' L (unary) '''
#            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_L_OP' and \
#                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
#                    TOKEN[i+j+distance_to_jump][2][2] == 'L':
#                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
#                any_op_in_remaining_left_pattern  = NULL.join(map(str, [x[2][0] for x in CUR_LEFT_PATTERN[j:]])).count("ANY_L_OP") - 1
#                for k in range(len(CUR_RIGHT_PATTERN)):
#                    if CUR_RIGHT_PATTERN[k][1] == CUR_LEFT_PATTERN[j][1] :
#                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
#                        if any_op_in_remaining_left_pattern <= 0 : continue
#                        break
#                continue
#            ''' R (unary) '''
#            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_R_OP' and \
#                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
#                    TOKEN[i+j+distance_to_jump][2][2] == 'R':
#                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
#                any_op_in_remaining_left_pattern  = NULL.join(map(str, [x[2][0] for x in CUR_LEFT_PATTERN[j:]])).count("ANY_R_OP") - 1
#                for k in range(len(CUR_RIGHT_PATTERN)):
#                    if CUR_RIGHT_PATTERN[k][1] == CUR_LEFT_PATTERN[j][1] :
#                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
#                        if any_op_in_remaining_left_pattern <= 0 : continue
#                        break
#                continue
#
#            ''' For ANY_OPERAND '''
#            ''' - if next symbol in left_pattern is a 0-precedence operator:
#                    -> next_is_zero_precedence_op = True
#                - if current_token is INSIDE an operand (needs to find all operands for token) :
#                    - if next_is_zero_precedence_op == True:
#                        - if there is an operand where current_token is in AND after operand == 0-precedence operator: this_operand
#                    - if is a complete operand : OPERAND == current_token
#                    - if not complete operand  :
#                            - if one operand starts exactly with current_token : OPERAND == this_operand
#                            - else : current_token is not an operand
#            '''
#            if CUR_LEFT_PATTERN[j][2][0] == 'ANY_OPERAND':
#                #--------------------------
#                # Check if next OR prev in LEFT_PATTERN is 0-precedence operator
#                next_is_zero_precedence_op = False
#                prev_is_zero_precedence_op = False
#                if j+1 < len(CUR_LEFT_PATTERN) and \
#                        CUR_LEFT_PATTERN[j+1][0] == 'OP' and \
#                        CUR_LEFT_PATTERN[j+1][2][3] == 0:
#                            next_is_zero_precedence_op = True
#                if j-1 >= 0 and \
#                        CUR_LEFT_PATTERN[j-1][0] == 'OP' and \
#                        CUR_LEFT_PATTERN[j-1][2][3] == 0:
#                            prev_is_zero_precedence_op = True
#                #--------------------------
#
#                rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))
#                OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]
#
#                for OP in OPS:
#                    operands_from_this_point_in_token = check_operands(OP,TOKEN,EXTRACT_OPERAND = True,ERROR_LOG = False)[1]
#                    for operands in operands_from_this_point_in_token:
#                        potential_operands.append(operands)
#                if not TOKEN[i+j+distance_to_jump] in map(list,[x[0] for x in potential_operands]) :
#                    found_operand = False
#                    break # If current token not in any operand, break
#
#                found_operand = False
#                unmatched = False
#
#                # -------------------------------------------------------------
#                # Check if we are looking for a 0-precedence operator's operand
#                if next_is_zero_precedence_op: 
#                    for potential in potential_operands:
#                        #print("----------")
#                        #print(f"potential : {potential}")
#                        #print(f"TOKEN[i+j+distance_to_jump] : {TOKEN[i+j+distance_to_jump]}")
#                        #start_potential_index_in_token = potential[0][3]
#                        end_potential_index_in_token = potential[len(potential)-1][3]
#                        if end_potential_index_in_token + 1 >= len(TOKEN):
#                            #found_operand = False
#                            continue
#                        elif TOKEN[end_potential_index_in_token + 1][0] == 'OP' and   \
#                                TOKEN[end_potential_index_in_token + 1][2][3] == 0 and \
#                                TOKEN[i+j+distance_to_jump] in potential:
#                            distance_to_jump += (len(potential) - 1)
#                            rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))
#                            found_operand = True
#                            str_potential = NULL.join(map(str,[x[1] for x in potential]))
#                            if not CUR_LEFT_PATTERN[j][1] in any_operands_dict :
#                                any_operands_dict[CUR_LEFT_PATTERN[j][1]] = str_potential
#                            else :
#                                if str_potential != any_operands_dict[CUR_LEFT_PATTERN[j][1]] :
#                                    distance_to_jump -= (len(potential) - 1)
#                                    pattern_in_token = False
#                                    unmatched = True
#                                    #print("(next) unmatch")
#                                    continue
#                            #print(f"(next) Would be that one : {str_potential}")
#                            for elem in potential:
#                                rewritable_part_of_token.append(elem)
#                            m = -1
#                            while m < len(CUR_RIGHT_PATTERN):
#                                m+=1
#                                if m >= len(CUR_RIGHT_PATTERN) : break
#                                if CUR_RIGHT_PATTERN[m][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[m][1] == CUR_LEFT_PATTERN[j][1] :
#                                    CUR_RIGHT_PATTERN.pop(m)
#                                    for elem in reversed(potential):
#                                        CUR_RIGHT_PATTERN[m:m] = [elem]
#                            #print(f"(next) did it : CUR_RIGHT_PATTERN = {CUR_RIGHT_PATTERN}")
#                            break
#                        else: continue
#
#                if prev_is_zero_precedence_op:
#                    #print("prev is zero precedence")
#                    for potential in potential_operands:
#                        start_potential_index_in_token = potential[0][3]
#                        if start_potential_index_in_token - 1 < 0 :
#                            continue
#                        elif TOKEN[start_potential_index_in_token - 1][0] == 'OP' and   \
#                                TOKEN[start_potential_index_in_token - 1][2][3] == 0 and \
#                                TOKEN[i+j+distance_to_jump] in potential:
#                            distance_to_jump += (len(potential) - 1)
#                            rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))
#                            found_operand = True
#                            str_potential = NULL.join(map(str,[x[1] for x in potential]))
#                            #print(f"(prev) Would be that one : {str_potential}")
#                            if not CUR_LEFT_PATTERN[j][1] in any_operands_dict :
#                                any_operands_dict[CUR_LEFT_PATTERN[j][1]] = str_potential
#                            else :
#                                if str_potential != any_operands_dict[CUR_LEFT_PATTERN[j][1]] :
#                                    #print("(prev) unmatch")
#                                    distance_to_jump -= (len(potential) - 1)
#                                    pattern_in_token = False
#                                    unmatched = True
#                                    continue
#                            for elem in potential:
#                                rewritable_part_of_token.append(elem)
#                            m = -1
#                            while m < len(CUR_RIGHT_PATTERN):
#                                m+=1
#                                if m >= len(CUR_RIGHT_PATTERN) : break
#                                if CUR_RIGHT_PATTERN[m][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[m][1] == CUR_LEFT_PATTERN[j][1] :
#                                    CUR_RIGHT_PATTERN.pop(m)
#                                    for elem in reversed(potential):
#                                        CUR_RIGHT_PATTERN[m:m] = [elem]
#                            #print(f"(prev) did it : CUR_RIGHT_PATTERN = {CUR_RIGHT_PATTERN}")
#                            break
#                        else: continue
#
#                if found_operand: continue
#                ## -------------------------------------------------------------
#
#                for potential in potential_operands:
#                    ''' For TOKEN[i+j+distance_to_jump] that are EQUAL to an OPERAND '''
#                    if [TOKEN[i+j+distance_to_jump]] == potential : # notice the [] around TOKEN : [TOKEN]
#                        found_operand = True
#
#                        str_potential = NULL.join(map(str,[x[1] for x in potential]))
#                        if not CUR_LEFT_PATTERN[j][1] in any_operands_dict :
#                            any_operands_dict[CUR_LEFT_PATTERN[j][1]] = str_potential
#                        else :
#                            if str_potential != any_operands_dict[CUR_LEFT_PATTERN[j][1]] :
#                                pattern_in_token = False
#                                unmatched = True
#                                break
#                        if unmatched : break
#
#                        rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
#                        for l in range(len(CUR_RIGHT_PATTERN)):
#                            if CUR_RIGHT_PATTERN[l][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[l][1] == CUR_LEFT_PATTERN[j][1] :
#                                CUR_RIGHT_PATTERN[l] = TOKEN[i+j+distance_to_jump]
#                        break
#
#                if found_operand: continue
#
#                for potential in potential_operands:
#                    ''' For TOKEN[i+j+distance_to_jump] that START an OPERAND '''
#                    if TOKEN[i+j+distance_to_jump] == potential[0] :
#                        distance_to_jump += (len(potential) - 1)
#                        rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))
#
#                        found_operand = True
#
#                        str_potential = NULL.join(map(str,[x[1] for x in potential]))
#                        if not CUR_LEFT_PATTERN[j][1] in any_operands_dict :
#                            any_operands_dict[CUR_LEFT_PATTERN[j][1]] = str_potential
#                        else :
#                            if str_potential != any_operands_dict[CUR_LEFT_PATTERN[j][1]] :
#                                pattern_in_token = False
#                                unmatched = True
#                                break
#                        if unmatched : break
#
#                        for elem in potential:
#                            rewritable_part_of_token.append(elem)
#
#                        m = -1
#                        #for m in range(len(CUR_RIGHT_PATTERN)):
#                        while m < len(CUR_RIGHT_PATTERN):
#                            m+=1
#                            if m >= len(CUR_RIGHT_PATTERN) : break
#                            if CUR_RIGHT_PATTERN[m][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[m][1] == CUR_LEFT_PATTERN[j][1] :
#                                CUR_RIGHT_PATTERN.pop(m)
#                                for elem in reversed(potential):
#                                    CUR_RIGHT_PATTERN[m:m] = [elem]
#                        #print(f">> CUR_RIGHT_PATTERN : {NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))}")
#                        break
#                #print(f"CUR_RIGHT_PATTERN : {NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))}")
#                if found_operand: continue
#            ''' ----------------------- '''
#
#            ''' ----------------------- '''
#            #''' Add ANY_EXPRESSION (test)'''
#            #if CUR_LEFT_PATTERN[j][2][0] == 'ANY_VALID_EXP':
#            #    print("Investigating 'ANY_VALID_EXP'")
#            #    # Investigating forward
#            #    token_end_index = len(TOKEN) + 1
#            #    #time_to_check_backward = False
#            #    while token_end_index >= 0 :
#            #        token_end_index -= 1
#            #        if token_end_index < 0 :
#            #            print("No valid expression found in the rest of the token.")
#            #            pattern_in_token = False
#            #            time_to_check_backward = True
#            #            break
#            #        exp_token = NULL.join(map(str,[x[1] for x in TOKEN[i+j+distance_to_jump:token_end_index]]))
#            #        if PARSE(TOKENIZE(exp_token))[0] and exp_token != "" :
#            #            print("Testing token : '{}'".format(exp_token))
#            #            print("Valid expression from index '{}' to '{}'.".format(i+j+distance_to_jump,token_end_index))
#            #            print("Accepted token : '{}'".format(exp_token))
#            #            if i+j+distance_to_jump+token_end_index+1 >= len(TOKEN):
#            #                print("whole rest of token taken")
#            #                if j == len(CUR_LEFT_PATTERN) - 1 :
#            #                    print("cool, the whole rest of the token is accepted.")
#            #                    for x in range(i+j+distance_to_jump,token_end_index):
#            #                        if x >= len(TOKEN): continue
#            #                        print("Appending '{}'".format(TOKEN[x]))
#            #                        rewritable_part_of_token.append(TOKEN[x])
#            #                    distance_to_jump += token_end_index
#            #                    rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:token_end_index]]))
#            #                    break
#            #                elif j != len(CUR_LEFT_PATTERN)-1 :
#            #                    print("not reached the end of CUR_LEFT_PATTERN")
#            #                    pattern_in_token = True
#            #                    for x in range(i+j+distance_to_jump,token_end_index):
#            #                        if x >= len(TOKEN): continue
#            #                        print("Appending '{}'".format(TOKEN[x]))
#            #                        rewritable_part_of_token.append(TOKEN[x])
#            #                    distance_to_jump += token_end_index
#            #                    rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:token_end_index]]))
#            #                    break
#            #                else :
#            #                    print("PERFECT!")
#            #            elif i+j+distance_to_jump+token_end_index+1 >= len(TOKEN) or j + 1 >= len(CUR_LEFT_PATTERN):
#            #                print("too big of an index!")
#            #                continue
#            #            elif TOKEN[i+j+distance_to_jump+token_end_index+1][1] != CUR_LEFT_PATTERN[j+1][1]:
#            #                print("No match for next index!")
#            #                continue
#            #            #break
#            #        else: continue
#            #    if pattern_in_token == False: continue
#            #''''''
#
#
#            if i+j+distance_to_jump >= len(TOKEN) : break
#
#            if TOKEN[i+j+distance_to_jump][1] != CUR_LEFT_PATTERN[j][1] : # and was not ANY_OPERAND?
#                pattern_in_token = False
#                break
#
#            if found_operand == False:
#                rewritable_part_of_token.append(TOKEN[i+j])
#
#        ''' End of j range . Inside of i range .'''
#
#        if i+j+distance_to_jump >= (len(TOKEN) - 1) and j < len(CUR_LEFT_PATTERN) - 1:
#            pattern_in_token = False
#            continue
#
#        #print(f"beginning_of_proposition: {beginning_of_proposition}")
#
#        if pattern_in_token and rewritable_part_of_token != [] :
#            #if "ANY_STR" in str(CUR_RIGHT_PATTERN) or "ANY_OPERAND" in str(CUR_RIGHT_PATTERN) or "ANY_VALID_EXP" in str(CUR_RIGHT_PATTERN) : continue
#            if "ANY_STR" in str(CUR_RIGHT_PATTERN) or "ANY_OPERAND" in str(CUR_RIGHT_PATTERN) : continue
#
#            rewritable_part = NULL+NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))
#            beginning_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[0:i]]))
#            distance_to_jump = 0
#
#            #print(f"rest_of_proposition: {rest_of_proposition}")
#            #print(f"pattern_in_token: {pattern_in_token}")
#            #print(f"rewritable_part_of_token: {rewritable_part_of_token}")
#            #print(f"rewritable_part: {rewritable_part}")
#
#            NEW_TOKEN=beginning_of_proposition+rewritable_part+rest_of_proposition
#            NEW_TOKEN = PARSE(TOKENIZE(NEW_TOKEN),ERROR_LOG = False)
#
#            if NEW_TOKEN[0]:
#                new_token = NULL.join(map(str,[x[1] for x in NEW_TOKEN[1]]))
#                if not new_token in REWRITES:
#                    counter += 1
#                    if MATCH_INDEX != None and MATCH_INDEX != counter : continue # ignore if asked another index
#                    REWRITES.append(new_token)
#                    if MATCH_INDEX != None : continue
#                    token_full_rewrites_list(NEW_TOKEN[1],LEFT_PATTERN,RIGHT_PATTERN,INDEX=i+j,REWRITES=REWRITES,RECURSION=RECURSION+1,RECURSION_EXCEEDED=RECURSION_EXCEEDED)
#
#    ''' End of i range. Token has been checked '''
#    if INDEX != 0 : return
#    VALID_REWRITES = [] # VALID_REWRITES are TOKENS
#    index = 0
#    for rew in REWRITES:
#        #counter += 1
#        token = PARSE(TOKENIZE(rew))
#        if token[0] and not token[1] in VALID_REWRITES :
#            VALID_REWRITES.append(token[1])
#        index+=1
#    return [True, VALID_REWRITES ]






