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
                #print(">> Unary right OP found in left pattern: '{}'".format(LEFT_PATTERN[j]))
                #print(">> Unary right OP found in TOKEN: '{}'".format(TOKEN[i+j+distance_to_jump]))
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                continue

            ''' Add ANY_OPERAND '''
            if LEFT_PATTERN[j][2][0] == 'ANY_OPERAND':
                #OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN[i+j:])]
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
                if found_operand :
                    for potential in potential_operands:
                        if [TOKEN[i+j+distance_to_jump]] == potential : # notice the [] around TOKEN : [TOKEN]
                            found_operand = True
                            rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                            #print("potential : '{}'".format(potential))
                            #print("rewritable_part_of_token : '{}'".format(rewritable_part_of_token))
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
            #if rewritable_part_of_token == []:
            #    print("rewritable_part_of_token is EMPTY")
            #    pattern_in_token = False
            if i+j+distance_to_jump >= len(TOKEN) :
                #print("i+j+distance_to_jump too HIGH ")
                pattern_in_token = False
                break
            if TOKEN[i+j+distance_to_jump][1] != LEFT_PATTERN[j][1]:
                #print("unmatching characters '{}' and '{}'".format(TOKEN[i+j+distance_to_jump][1], LEFT_PATTERN[j][1]))
                pattern_in_token = False
                break
            #print(TOKEN[i+j+distance_to_jump])
            #print("'{}' == '{}'".format(TOKEN[i+j+distance_to_jump][1],LEFT_PATTERN[j][1]))
            rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
            #print("pattern_in_token : '{}'".format(pattern_in_token))
            #print("rewritable_part_of_token : '{}'".format(rewritable_part_of_token))
        if pattern_in_token :
            #print("--> WRITING rewritable_part_of_token : '{}'".format(rewritable_part_of_token))
            REWRITABLE_PARTS.append([rewritable_part_of_token,R])
        distance_to_jump = 0
    return [True, REWRITABLE_PARTS]

##print(TOKENIZE("1 + 2 = 3"))
#print(token_rewritable_parts(TOKENIZE("1 + 2 + 2 + 3 + 2= 3 + 2"), TOKENIZE("_ + 2")))
#exit

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
                ''' Add ANY_OPERAND '''
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
                ''' Add ANY_OPERAND '''
                if LEFT_PATTERN[j][2][0] == 'ANY_OPERAND':
                    #OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN[i+j:])]
                    OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]
                    for OP in OPS:
                        operands_from_this_point_in_token = check_operands(OP,TOKEN,EXTRACT_OPERAND = True,ERROR_LOG = False)[1]
                        for operands in operands_from_this_point_in_token:
                            potential_operands.append(operands)
                    if not TOKEN[i+j+distance_to_jump] in map(list,[x[0] for x in potential_operands]) :
                        found_operand = False
                    else :
                        found_operand = True
                    if found_operand :
                        for potential in potential_operands:
                            if [TOKEN[i+j+distance_to_jump]] == potential : # notice the [] around TOKEN : [TOKEN]
                                found_operand = True
                                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                                #print("potential : '{}'".format(potential))
                                #print("rewritable_part_of_token : '{}'".format(rewritable_part_of_token))
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
                #if rewritable_part_of_token == []:
                #    pattern_in_token = False
                if i+j+distance_to_jump >= len(TOKEN) :
                    pattern_in_token = False
                    break
                if TOKEN[i+j+distance_to_jump][1] != LEFT_PATTERN[j][1]:
                    pattern_in_token = False
                    break
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
            if pattern_in_token:
                REWRITABLE_PARTS.append([rewritable_part_of_token,R])
            distance_to_jump = 0
    return REWRITABLE_PARTS

###print(TOKENIZE("1 + 2 = 3"))
#print(token_all_rewritable_parts(TOKENIZE("1 + 2 + 2 + 3 + 2= 3 + 2")))
#exit

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
    #print("REWRITTEN:",REWRITTEN)
    #print("MATCH_index:",MATCH_INDEX)
    if not REWRITTEN[0]: return [ POSSIBLE_REWRITES, REWRITES ]

    for TRANSFORMATION in REWRITTEN[1]:
        #if NULL.join(map(str,[x[1] for x in TRANSFORMATION])) in REWRITES:
        if TRANSFORMATION in REWRITES:
            continue
        else :
            #REWRITES.append(NULL.join(map(str,[x[1] for x in TRANSFORMATION])))
            REWRITES.append(TRANSFORMATION)
            POSSIBLE_REWRITES[0] = True
            POSSIBLE_REWRITES[1].append([PARSE(TOKENIZE(TRANSFORMATION))[1],LP,RP,R])
        #combine_all_possible_rewrites(TRANSFORMATION,REWRITES=REWRITES,first_time=False,RECURSION=RECURSION+1)
    #print("PW: {} ".format(POSSIBLE_REWRITES))
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
    #found_operand = False
    if RECURSION >= RECURSION_LIMIT:
        RECURSION_EXCEEDED = True
        return
    if REWRITES is None: REWRITES = []
    #for i in range(INDEX + distance_to_jump,len(TOKEN)):
    for i in range(INDEX,len(TOKEN)):
        if len(TOKEN) - i < len(LEFT_PATTERN) : continue # New : avoid "Rule a + b ::= c" rewrite "Token a" as "c"
        CUR_RIGHT_PATTERN = [x for x in RIGHT_PATTERN]
        pattern_in_token = True
        rewritable_part_of_token = []
        distance_to_jump = 0 # when adding an operand with more than 1 character, it needs to be jumped
        found_operand = False

        for j in range(len(LEFT_PATTERN)):
            #if i+j >= len(TOKEN):
            if i+j+distance_to_jump >= len(TOKEN):
                if found_operand : break
                pattern_in_token = False
                break
            #rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[i+j+1:]]))
            rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[i+j+1+distance_to_jump:]]))

            ''' For ANY_STR '''
            #if LEFT_PATTERN[j][2][0] == 'ANY_STR' and TOKEN[i+j][0] == 'STR':
            if LEFT_PATTERN[j][2][0] == 'ANY_STR' and TOKEN[i+j+distance_to_jump][0] == 'STR':
                #rewritable_part_of_token.append(TOKEN[i+j])
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                #for k in range(len(RIGHT_PATTERN)):
                for k in range(len(CUR_RIGHT_PATTERN)):
                    if CUR_RIGHT_PATTERN[k][2][0] == 'ANY_STR' and CUR_RIGHT_PATTERN[k][1] == LEFT_PATTERN[j][1] :
                        #CUR_RIGHT_PATTERN[k] = TOKEN[i+j]
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
                        continue
                continue

            ''' For ANY_OP '''
            ''' LR '''
            if LEFT_PATTERN[j][2][0] == 'ANY_LR_OP' and \
                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                    TOKEN[i+j+distance_to_jump][2][2] == 'LR':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                for k in range(len(CUR_RIGHT_PATTERN)):
                    if CUR_RIGHT_PATTERN[k][1] == LEFT_PATTERN[j][1] :
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
                        break # break?
                continue
            ''' L (unary) '''
            if LEFT_PATTERN[j][2][0] == 'ANY_L_OP' and \
                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                    TOKEN[i+j+distance_to_jump][2][2] == 'L':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                for k in range(len(CUR_RIGHT_PATTERN)):
                    if CUR_RIGHT_PATTERN[k][1] == LEFT_PATTERN[j][1] :
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
                        break # break?
                continue
            ''' R (unary) '''
            if LEFT_PATTERN[j][2][0] == 'ANY_R_OP' and \
                    TOKEN[i+j+distance_to_jump][0] == 'OP' and \
                    TOKEN[i+j+distance_to_jump][2][2] == 'R':
                rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                for k in range(len(CUR_RIGHT_PATTERN)):
                    if CUR_RIGHT_PATTERN[k][1] == LEFT_PATTERN[j][1] :
                        CUR_RIGHT_PATTERN[k] = TOKEN[i+j+distance_to_jump]
                        break # break?
                continue

            # TODO: check if everything is right !!!!!!
            ''' For ANY_OPERAND '''
            ''' if current_token is INSIDE an operand (needs to find all operands for token) :
                    - if is a complete operand : OPERAND == current_token
                    - if not complete operand  :
                            - if one operand starts exactly with current_token : OPERAND == this_operand
                            - else : current_token is not an operand
            '''
            if LEFT_PATTERN[j][2][0] == 'ANY_OPERAND':
                rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))
                #print("0) found operand in LEFT_PATTERN : {}".format(LEFT_PATTERN[j]))
                #print("0) current 'found_operand' var : '{}'".format(found_operand))
                #print("0) current 'distance_to_jump' var : '{}'".format(distance_to_jump))
                ##OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN[i+j:])]
                OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]
                #print("OPS : {}".format(OPS))
                for OP in OPS:
                    #operands_from_this_point_in_token = check_operands(OP,TOKEN[i+j:],EXTRACT_OPERAND = True,ERROR_LOG = False)[1]
                    operands_from_this_point_in_token = check_operands(OP,TOKEN,EXTRACT_OPERAND = True,ERROR_LOG = False)[1]
                    for operands in operands_from_this_point_in_token:
                        potential_operands.append(operands)
                #print("potential operands : '{}'".format(potential_operands))
                if not TOKEN[i+j+distance_to_jump] in map(list,[x[0] for x in potential_operands]) :
                    #print("9) token {} not operand ".format(TOKEN[i+j+distance_to_jump]))
                    found_operand = False
                    break # If current token not in any operand, break
                found_operand = False
                for potential in potential_operands:
                    #print("potential: '{}'".format(potential))
                    if [TOKEN[i+j+distance_to_jump]] == potential : # notice the [] around TOKEN : [TOKEN]
                        #print("2) Yes, I am equal! token: {} i: {} j: {}".format(TOKEN[i+j+distance_to_jump],i,j))
                        found_operand = True
                        #rewritable_part_of_token.append(TOKEN[i+j])
                        rewritable_part_of_token.append(TOKEN[i+j+distance_to_jump])
                        #for l in range(len(RIGHT_PATTERN)):
                        for l in range(len(CUR_RIGHT_PATTERN)):
                            if CUR_RIGHT_PATTERN[l][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[l][1] == LEFT_PATTERN[j][1] :
                                CUR_RIGHT_PATTERN[l] = TOKEN[i+j+distance_to_jump]
                                break
                        break
                if found_operand: continue
                for potential in potential_operands:
                    if TOKEN[i+j+distance_to_jump] == potential[0] :
                        #print("3) Yes, I start an operand! token: {} i: {} j: {}".format(TOKEN[i+j+distance_to_jump],i,j))
                        #print("3) The operand is '{}'".format(''.join(map(str,[x[1] for x in potential]))))
                        distance_to_jump += (len(potential) - 1)
                        rest_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[distance_to_jump+i+j+1:]]))
                        found_operand = True
                        for elem in potential:
                            #print("check that : {}".format(elem))
                            rewritable_part_of_token.append(elem)
                        #for m in range(len(RIGHT_PATTERN)):
                        for m in range(len(CUR_RIGHT_PATTERN)):
                            if CUR_RIGHT_PATTERN[m][2][0] == 'ANY_OPERAND' and CUR_RIGHT_PATTERN[m][1] == LEFT_PATTERN[j][1] :
                                #print("Found '{}'".format(CUR_RIGHT_PATTERN[m][1]))
                                CUR_RIGHT_PATTERN.pop(m)
                                for elem in reversed(potential):
                                    CUR_RIGHT_PATTERN[m:m] = [elem]
                                #print("3) CUR_RIGHT_PATTERN : '{}'".format(''.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))))
                                break
                        break
                if found_operand: continue
            ''' ----------------------- '''

            if i+j+distance_to_jump >= len(TOKEN) :
                pattern_in_token = False
                break
            #print("4) next comparaison  : '{}' <=> '{}'".format(TOKEN[i+j+distance_to_jump][1], LEFT_PATTERN[j][1]))
            #print("5) CUR_RIGHT_PATTERN : '{}'".format(''.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))))
            #print("6) i={}, j={}, distance_to_jump={}, len(TOKEN)={}, len(LEFT_PATTERN)={}".format(i,j,distance_to_jump,len(TOKEN),len(LEFT_PATTERN)))
            if TOKEN[i+j+distance_to_jump][1] != LEFT_PATTERN[j][1] : # and was not ANY_OPERAND?
                pattern_in_token = False
                break
            if found_operand == False:
                rewritable_part_of_token.append(TOKEN[i+j])


        if pattern_in_token :
            if "ANY_STR" in str(CUR_RIGHT_PATTERN) or "ANY_OPERAND" in str(CUR_RIGHT_PATTERN) :
                #print("7) ANY_OPERAND in CUR_RIGHT_PATTERN '{}'".format(NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))))
                continue
            #print("10) Should add CUR_RIGHT_PATTERN '{}' as rewrite here!".format(NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))))
            start_index = i
            end_index   = i+j
            rewritable_part = NULL+NULL.join(map(str,[x[1] for x in CUR_RIGHT_PATTERN]))
            beginning_of_proposition = NULL+NULL.join(map(str,[x[1] for x in TOKEN[0:start_index]]))
            #print("11) beginning_of_proposition: {}".format(beginning_of_proposition))
            #print("11) rewritable_part: {}".format(rewritable_part))
            #print("11) rest_of_proposition: {}".format(rest_of_proposition))
            #print("12) RESETING distance_to_jump from '{}' to 0.".format(distance_to_jump))
            distance_to_jump = 0

            NEW_TOKEN=beginning_of_proposition+rewritable_part+rest_of_proposition
            #print("12) NEW_TOKEN: {}".format(NEW_TOKEN))
            ''' check for problems here '''
            NEW_TOKEN = PARSE(TOKENIZE(NEW_TOKEN),ERROR_LOG = False)
            ''' check for problems above (no log) '''
            if NEW_TOKEN[0]:
                new_token = NULL.join(map(str,[x[1] for x in NEW_TOKEN[1]]))
                if not new_token in REWRITES:
                    # ...new func
                    counter += 1
                    if MATCH_INDEX != None and MATCH_INDEX != counter :
                        continue
                    # ...
                    REWRITES.append(new_token)
                    # ...new func
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
