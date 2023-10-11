#!/usr/bin/env python3

from read_table import *
from lexer import *
from parser import *
from read_rules import *
from checker import *
from rewriter import *
from colors import *

'''The DISPLAYER is just a script that combines functions from IDIOMATIK
to output "proper" results to the user, given the INPUT.
'''

def render_tree(TOKEN):
    surrounded_expression_token = silent_surrounding(TOKEN)
    if 'SUR' in [x[0] for x in surrounded_expression_token]:
        highest_nestedness_score = max([x[2][2] for x in filter(lambda y: y[0] == 'SUR', surrounded_expression_token)])
    else :
        highest_nestedness_score = 0
    #print("Nestedness max : {}".format(highest_nestedness_score))
    #print("\n")
    TREE_MATRICE = []
    occupied_indexes = []
    for i in reversed(range(highest_nestedness_score+1)):
        TMP_MATRICE = [[] for x in surrounded_expression_token]
        found_nest = False
        if i == 0 :
            for k in range(len(surrounded_expression_token)):
                if str(k) in occupied_indexes:
                    continue
                else :
                    TMP_MATRICE[k] = str(surrounded_expression_token[k][1])
            TREE_MATRICE.append(TMP_MATRICE)
            break
        for j in range(0,len(surrounded_expression_token)):
            if found_nest :
                if surrounded_expression_token[j][0] == 'SUR' and surrounded_expression_token[j][2][2] == i and surrounded_expression_token[j][2][1] == 'close':
                    found_nest = False
                    TMP_MATRICE[j] = str(surrounded_expression_token[j][1])
                    occupied_indexes.append(str(j))
                    continue
                else:
                    TMP_MATRICE[j] = str(surrounded_expression_token[j][1])
                    occupied_indexes.append(str(j))
            elif surrounded_expression_token[j][0] == 'SUR' and surrounded_expression_token[j][2][2] == i:
                found_nest = True
                TMP_MATRICE[j] = str(surrounded_expression_token[j][1])
                occupied_indexes.append(str(j))
                continue
        TREE_MATRICE.append(TMP_MATRICE)

    LAST_MATRICE = []
    for i in reversed(range(len(TREE_MATRICE))):
        #print(NULL.join(map(str,[x for x in TREE_MATRICE[i]])))
        STRING = ""
        index = 0
        for element in TREE_MATRICE[i]:
            if   element == []: STRING += NULL
            #for sur in SYMBOLS['SURROUNDERS']:
            elif i != 0 and element == TREE_MATRICE[i-1][index] : STRING += NULL
            else :
                #if str(element) == str(sur[0]) or str(element) == str(sur[1]) :
                if str(element) in list(map(str,[x[0] for x in SYMBOLS['SURROUNDERS']])) or \
                        str(element) in list(map(str,[x[1] for x in SYMBOLS['SURROUNDERS']])):
                            STRING += NULL
                            index += 1
                            continue
                STRING += str(element)
            index += 1
        #print(len(TREE_MATRICE) - (i+1), "\t",STRING,"\n")
        LAST_MATRICE.append(STRING)

    # Place operators on line ABOVE (except for i = 0) and remove empty lines
    FINAL_MATRICE = []
    max_length = max([len(x) for x in LAST_MATRICE])
    for i in range(len(LAST_MATRICE)):
        if i == len(LAST_MATRICE)-1:
            #print(i, "\t",LAST_MATRICE[i],"\n")
            FINAL_MATRICE.append(list(LAST_MATRICE[i]))
            continue
        index = 0
        if i == 0 :
            STRING = ""
            is_non_null = False
            has_op = False
            NEW_LINE = ""
            for char in LAST_MATRICE[i]:
                if char == NULL:
                    STRING += NULL
                    index+=1
                    continue
                char_token = TOKENIZE(char)
                if char_token[0][0] == 'OP':
                    has_op = True
                    STRING += char
                    NEW_LINE = ""
                    for j in range(len(LAST_MATRICE[i])):
                        if j == index :
                            NEW_LINE+=NULL
                        else:
                            NEW_LINE += LAST_MATRICE[i][j]
                    LAST_MATRICE[i] = list(NEW_LINE)
                else:
                    is_non_null = True
                    STRING += NULL
                index+=1
            if has_op or is_non_null :
                FINAL_MATRICE.append(list(STRING))

        index = 0
        for char in LAST_MATRICE[i+1]:
            if char == NULL:
                index+=1
                continue
            char_token = TOKENIZE(char)
            if char_token[0][0] == 'OP':
                list_cur_line = list(LAST_MATRICE[i])
                list_cur_line[index] = char
                LAST_MATRICE[i] = ''.join(map(str,list_cur_line)) + (max_length - len(list_cur_line)) * NULL
                list_next_line = list(LAST_MATRICE[i+1])
                list_next_line[index] = NULL
                LAST_MATRICE[i+1] = ''.join(map(str,list_next_line)) + (max_length - len(list_next_line)) * NULL
            index+=1
        FINAL_MATRICE.append(list(LAST_MATRICE[i]))
    #for line in FINAL_MATRICE:
    #    print(line)
    #print("-----------------------")

    # Remove cells that are empty on same index for every row (remove empty columns)
    columns_to_ignore = []
    for i in range(len(FINAL_MATRICE[0])):  # number of columns
        are_all_empty = True
        for j in range(len(FINAL_MATRICE)): # number of raws
            if i >= len(FINAL_MATRICE[j]):continue
            if FINAL_MATRICE[j][i] != NULL :
                are_all_empty = False
                break
        if not are_all_empty : continue
        else : # remove all cells on that column i
            columns_to_ignore.append(i)

    # Rebuild MATRICE
    ULTIMATE_MATRICE = []
    for i in range(len(FINAL_MATRICE)): # raws
        STRING = ""
        for j in range(len(FINAL_MATRICE[0])):
            if j in columns_to_ignore:
                continue
            STRING += FINAL_MATRICE[i][j]
        if STRING.replace(' ','') != "" : ULTIMATE_MATRICE.append(STRING)

    #print("-+++----------- tree -----------+")
    index = len(FINAL_MATRICE)-1
    for line in ULTIMATE_MATRICE:
        #print("{} | {}".format(index,line))
        print("{} |".format(index) + bcolors.OKGREEN + " {}".format(line) + bcolors.ENDC)
        index-=1
    #print("\n")

def display_rewritable_parts(INPUT,RULE_TO_MATCH=None,MATCH_INDEX=None):
    '''Temporary function to show possible rewritable
     parts of a token for ALL RULES if no RULE_TO_MATCH specified.
     It also can dispay a specified matching index (0 for the first match...)'''
    if RULE_TO_MATCH != None:
        # Find name of rule
        found_name = False
        # If user gave the exact name rule : grab its index
        for i in range(len(RULES['REWRITE_RULES_NAMES'])):
            if RULE_TO_MATCH == RULES['REWRITE_RULES_NAMES'][i] :
                found_name = True
                RULE_TO_MATCH = i
                break
        if found_name == False:
            if not "r" in str(RULE_TO_MATCH) and not "R" in str(RULE_TO_MATCH) :
                print(bcolors.FAIL + "ERROR: please provide a rule to match (e.g. 'match r0 [index]')" + bcolors.ENDC)
                return
            RULE_TO_MATCH = RULE_TO_MATCH.replace('R','').replace('r','')
    # Check if token is valid (is that useful? too many checks before I guess)
    token = TOKENIZE(INPUT)
    parse = PARSE(token)
    if not parse[0] :
        print("Invalid proposition")
        return
    # Grab rewritable parts!
    if RULE_TO_MATCH != None:
        if MATCH_INDEX != None :
            REWRITES = token_rewritable_parts(token,RULE_INDEX=RULE_TO_MATCH,MATCH_INDEX=MATCH_INDEX)
        else :
            REWRITES = token_rewritable_parts(token,RULE_INDEX=RULE_TO_MATCH)
        if not REWRITES[0]: return
        REWRITES = REWRITES[1]
    else :
        if MATCH_INDEX != None :
            REWRITES = token_all_rewritable_parts(token,MATCH_INDEX=MATCH_INDEX)
        else :
            REWRITES = token_all_rewritable_parts(token)
    if len(REWRITES) == 0 :
        print("No matching pattern.")
        return
    #REWRITES = check[1] # Storing tokens of possible rewritings
    counter = 0
    redundant = 0
    STR_REWRITES = []
    for rew in REWRITES:
        # ...
        rule_name_general = rew[1]
        rew = rew[0]
        # ...
        str_rewrite = rew
        if not (str_rewrite,rule_name_general) in STR_REWRITES :
            STR_REWRITES.append((rew,rule_name_general))
        else :
            redundant+=1
            continue
        indexes_in_part = []
        for i in range(len(rew)):
            indexes_in_part.append(rew[i][3])
        beautiful_rewrite = ""
        for i in range(len(parse[1])):
            if parse[1][i][3] in indexes_in_part :
                if parse[1][i][3] == indexes_in_part[len(indexes_in_part)-1]:
                    if indexes_in_part[0] == 0 :
                        beautiful_rewrite = bcolors.BOLD + bcolors.OKGREEN + human_readable(str_rewrite) + bcolors.ENDC
                    else :
                        beautiful_rewrite = beautiful_rewrite + NULL + bcolors.BOLD + bcolors.OKGREEN + human_readable(str_rewrite) + bcolors.ENDC
            else :
                if i == 0:
                    beautiful_rewrite = str(parse[1][i][1])
                else :
                    beautiful_rewrite = beautiful_rewrite + NULL + str(parse[1][i][1])
        for i in range(len(RULES['REWRITE_RULES'])):
            if rule_name_general == RULES['REWRITE_RULES'][i]:
                rule_name_general = "R"+str(i)
                rule_name = RULES['REWRITE_RULES_NAMES'][i]
                break
        # Print it
        if MATCH_INDEX != None and MATCH_INDEX != counter :
            counter+=1
            continue
        if rule_name == "" :
            print("{} | ".format(counter) + beautiful_rewrite + "\t" + "(" + rule_name_general + ")")
        else :
            symbol_prop_id = SYMBOLS['OPERATORS'][SYMBOLS['OPERATORS NAMES'].index("PROPOSITION_IDENTIFIER")]
            print("{} | ".format(counter) + beautiful_rewrite + "\t" + "(" + rule_name_general + " " + str(symbol_prop_id) + " " + rule_name + ")")
        counter+=1



def display_all_possible_rewritings(INPUT,MATCH_INDEX=None):
    '''Temporary function to show ALL possible rewrites
     for an INPUT (proposition) given the set of RULES'''
    token = TOKENIZE(INPUT)
    parse = PARSE(token)
    if not parse[0] :
        print("Invalid proposition")
        return
    check = combine_all_possible_rewrites(token,MATCH_INDEX=MATCH_INDEX)
    if not check[0] :
        print("No matching pattern.")
        return
    REWRITES = check[1] # Storing tokens of possible rewritings
    counter = 0
    redundant = 0
    STR_REWRITES = []
    for rew in REWRITES:
        str_rewrite = rew
        if not str_rewrite in STR_REWRITES :
            STR_REWRITES.append(rew)
        else :
            redundant+=1
            continue
        print(str_rewrite)
        counter+=1

def display_given_a_rule(INPUT,RULE_INDEX=None,MATCH_INDEX=None):
    token = TOKENIZE(INPUT)
    parse = PARSE(token)
    if not parse[0] :
        print("Invalid proposition")
        return
    RULE = RULES['REWRITE_RULES'][int(RULE_INDEX)]
    #print("rule: ",RULE)
    check = rewrite_given_a_rule(token,RULE,MATCH_INDEX=MATCH_INDEX)
    #print("check: rewrite_given_a_rule = {}".format(check))
    if not check[0] :
        print("No matching pattern.")
        return
    REWRITES = check[1] # Storing tokens of possible rewritings
    counter = 0
    redundant = 0
    STR_REWRITES = []
    for rew in REWRITES:
        str_rewrite = rew
        if not str_rewrite in STR_REWRITES :
            STR_REWRITES.append(rew)
        else :
            redundant+=1
            continue
        print(str_rewrite)
        counter+=1

def display_axioms_and_rules(choice=False):
    if choice == False or choice == "axioms":
        index = 0
        #for axioms in RULES['AXIOMS']:
        for i in range(len(RULES['AXIOMS'])):
            axiom_name = RULES['AXIOMS_NAMES'][i]
            max_axiom_name_length = max(map(int,(len(x) for x in RULES['AXIOMS_NAMES'])))
            cur_axiom_name_length = len(axiom_name)
            axiom = NULL.join(map(str,[x[1] for x in RULES['AXIOMS'][i]]))
            symbol_prop_id = SYMBOLS['OPERATORS'][SYMBOLS['OPERATORS NAMES'].index("PROPOSITION_IDENTIFIER")]
            if axiom_name == "" :
                #print("\t(A{}) \t {}".format(index,axiom))
                print("\t(A{})".format(index) + NULL * max_axiom_name_length + NULL * len(symbol_prop_id) + "  \t {}".format(axiom))
            else :
                #print("\t(A{} :: {}) \t {}".format(index,axiom_name,axiom))
                print("\t(A{} ".format(index) + str(symbol_prop_id) + " {})".format(axiom_name) + NULL * (max_axiom_name_length - cur_axiom_name_length) + "\t {}".format(axiom))
            index += 1
    if choice == False or choice == "rules":
        index = 0
        #for rules in RULES['REWRITE_RULES']:
        for i in range(len(RULES['REWRITE_RULES'])):
            rule_name = RULES['REWRITE_RULES_NAMES'][i]
            #print(max(map(int,(len(x) for x in RULES['REWRITE_RULES_NAMES']))))
            max_rule_name_length = max(map(int,(len(x) for x in RULES['REWRITE_RULES_NAMES'])))
            cur_rule_name_length = len(rule_name)
            rule = NULL.join(map(str,[x[1] for x in RULES['REWRITE_RULES'][i]]))
            symbol_prop_id = SYMBOLS['OPERATORS'][SYMBOLS['OPERATORS NAMES'].index("PROPOSITION_IDENTIFIER")]
            if rule_name == "" :
                #print("\t(R{}) \t {}".format(index,NULL.join(map(str,[x[1] for x in RULES['REWRITE_RULES'][i]]))))
                print("\t(R{})".format(index) + NULL * max_rule_name_length + NULL * len(symbol_prop_id) + "  \t {}".format(rule))
            else :
                #print("\t(R{} :: {}) \t {}".format(index,rule_name,NULL.join(map(str,[x[1] for x in RULES['REWRITE_RULES'][i]]))))
                print("\t(R{} ".format(index) + str(symbol_prop_id) + " {})".format(rule_name) + NULL * (max_rule_name_length - cur_rule_name_length) + "\t {}".format(rule))
            index += 1

def human_readable(TOKEN):
    return NULL.join(map(str,[x[1] for x in TOKEN]))

#a = "(((((((c))))))) + b => (~ a)"
#a = "~ (A) + (B) + (c) + (d)"
#a = "p => q"
##print("-----------------------")
#print("PROP: {}\n".format(a))
#print(CHECK(PARSE(TOKENIZE(a))))
