#!/usr/bin/env python3

from read_table import *
from lexer import *
from parser import *
from read_rules import *
from rewriter import *
from colors import *

'''The DISPLAYER is just a script that combines functions from IDIOMATIK
to output "proper" results to the user, given the INPUT.
'''

def render_tree(CHAIN: list):
    ''' Beta function to visualize trees. But there are troubles with long
    variables' names, etc.
    '''
    SUR_EXP    = PARSE(silent_surrounding(CHAIN)).tokens
    highest_nestedness_score = max([token.nestedness for token in SUR_EXP])
    # Build template tree
    cols       = len(SUR_EXP)
    rows       = highest_nestedness_score + 1 + 1
    empty_line = [[] for x in range(cols)]
    TREE = [empty_line]
    for i in range(rows):
        TREE.append([ [] for x in range(cols) ])
    # Populate template tree given nestedness
    for i in range(rows):
        for j in range(cols):
            if SUR_EXP[j].nestedness == i :
                if is_surrounder(SUR_EXP[j]) : continue
                if is_operator(SUR_EXP[j]) :
                    TREE[i][j] = SUR_EXP[j].symbol
                else :
                    TREE[i+1][j] = SUR_EXP[j].symbol
    ## Pop empty lines if any
    indexes_to_pop = []
    for i in range(len(TREE)):
        pop = True
        for j in range(cols):
            if TREE[i][j] != [] : pop = False
        if pop : indexes_to_pop.append(i)
    for index in reversed(indexes_to_pop): TREE.pop(index)

    #For columns, populate by length of non-empty value
    for j in range(cols):
        length = -1
        for i in range(len(TREE)):
            if TREE[i][j] != []:
                length = len(TREE[i][j])
                break
        if length >= 0:
            for i in range(len(TREE)):
                if TREE[i][j] == []:
                    #TREE[i][j] = int(length)
                    TREE[i][j] = NULL * length

    ## Replace lists by strings : if [] = "", elif isinstance(x,int) = NULL*x, else = str(x)
    for i in range(len(TREE)):
        for j in range(cols):
            if   TREE[i][j] == []: TREE[i][j] = ""

    # Print tree
    index = 0
    for line in TREE:
        line_string = ''.join(map(str,[x for x in line]))
        print(f"{index}| {bcolors.OKGREEN}{line_string}{bcolors.ENDC}")
        index+=1
    return

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
    parse = PARSE(INPUT,ERROR_LOG = False)
    CHAIN = parse.tokens
    if not parse.validity :
        print(bcolors.FAIL + "Invalid proposition" + bcolors.ENDC)
        return
    # Grab rewritable parts!
    if RULE_TO_MATCH != None:
        if MATCH_INDEX != None :
            REWRITES = token_rewritable_parts(CHAIN,RULE_INDEX=RULE_TO_MATCH,MATCH_INDEX=MATCH_INDEX)
        else :
            REWRITES = token_rewritable_parts(CHAIN,RULE_INDEX=RULE_TO_MATCH)
        if not REWRITES[0]: return
        REWRITES = REWRITES[1]
    else :
        if MATCH_INDEX != None :
            REWRITES = token_all_rewritable_parts(CHAIN,MATCH_INDEX=MATCH_INDEX)
        else :
            REWRITES = token_all_rewritable_parts(CHAIN)
    if len(REWRITES) == 0 :
        #print("No matching pattern.")
        print(bcolors.DIM + "No matching pattern." + bcolors.ENDC)
        return
    counter = 0
    redundant = 0
    STR_REWRITES = []
    last_rule_name = None
    for rew in REWRITES:
        rule_name_general = rew[1]
        rew = rew[0]
        str_rewrite = rew
        if not (str_rewrite,rule_name_general) in STR_REWRITES :
            STR_REWRITES.append((rew,rule_name_general))
        else :
            redundant+=1
            continue
        indexes_in_part = []
        for i in range(len(rew)):
            indexes_in_part.append(rew[i].index)
        beautiful_rewrite = ""
        for i in range(len(CHAIN)):
            if CHAIN[i].index in indexes_in_part :
                if CHAIN[i].index == indexes_in_part[len(indexes_in_part)-1]:
                    if indexes_in_part[0] == 0 :
                        beautiful_rewrite = bcolors.BOLD + bcolors.OKGREEN + human_readable(str_rewrite) + bcolors.ENDC
                    else :
                        beautiful_rewrite = beautiful_rewrite + NULL + bcolors.BOLD + bcolors.OKGREEN + human_readable(str_rewrite) + bcolors.ENDC
            else :
                if i == 0:
                    beautiful_rewrite = str(CHAIN[i].symbol)
                else :
                    beautiful_rewrite = beautiful_rewrite + NULL + str(CHAIN[i].symbol)
        for i in range(len(RULES['REWRITE_RULES'])):
            if rule_name_general == RULES['REWRITE_RULES'][i]:
                # test
                if last_rule_name != None:
                    rule_name_general = "R"+str(i)
                    if last_rule_name != rule_name_general:
                        rule_counter = 0
                        last_rule_name = rule_name_general
                    else :
                        rule_counter += 1
                else :
                    rule_name_general = "R"+str(i)
                    rule_counter = 0
                    last_rule_name = rule_name_general
                rule_name = RULES['REWRITE_RULES_NAMES'][i]
                break
        # Print it
        if MATCH_INDEX != None and MATCH_INDEX != counter :
            counter+=1
            continue
        symbol_prop_id = SYMBOLS['OP'][SYMBOLS['OP NAMES'].index("PROP_ID")]
        rewrite = str_rewrites_given_a_rule(CHAIN,RULE_INDEX=i,MATCH_INDEX=rule_counter)
        if len(rewrite) == 1:
            rewrite = rewrite[0]
        elif len(rewrite) == 0:
            continue
        max_rule_name_length = max(map(int,(len(x) for x in RULES['REWRITE_RULES_NAMES'])))
        if rule_name == "" :
            print("{} | ".format(counter) + beautiful_rewrite + "\t" + bcolors.OKBLUE + "(" + rule_name_general + ")" +bcolors.ENDC + NULL * max_rule_name_length + NULL * len(symbol_prop_id) +  "  \t {}".format(symbol_prop_id) + bcolors.FAIL+ " {}".format(rewrite) + bcolors.ENDC)
        else :
            cur_rule_name_length = len(rule_name)
            print("{} | ".format(counter) + beautiful_rewrite + "\t" + bcolors.OKBLUE +"(" + rule_name_general + " " + str(symbol_prop_id) + " " + rule_name + ")" +bcolors.ENDC+ NULL * (max_rule_name_length - cur_rule_name_length) + "\t {}". format(symbol_prop_id) + bcolors.FAIL + " {}".format(rewrite) + bcolors.ENDC)
        counter+=1
    if counter == 0 :
        print(bcolors.DIM + "No matching pattern." + bcolors.ENDC)

# rewrite full
def display_all_possible_rewritings(INPUT,MATCH_INDEX=None):
    '''Temporary function to show ALL possible rewrites
     for an INPUT (proposition) given the set of RULES'''
    parse = PARSE(INPUT,ERROR_LOG = False)
    CHAIN = parse.tokens
    if not parse.validity :
        print(bcolors.FAIL + "Invalid proposition" + bcolors.ENDC)
        return
    check = combine_all_possible_rewrites(CHAIN,MATCH_INDEX=MATCH_INDEX)
    if not check[0] :
        print(bcolors.DIM + "No matching pattern." + bcolors.ENDC)
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
    if counter == 0:
        print(bcolors.DIM + "No matching pattern." + bcolors.ENDC)

def display_given_a_rule(INPUT,RULE_INDEX=None,MATCH_INDEX=None):
    CHAIN = PARSE(INPUT,ERROR_LOG = False).tokens
    counter = 0
    for rew in str_rewrites_given_a_rule(CHAIN,RULE_INDEX,MATCH_INDEX):
        print(rew)
        counter+=1
    if counter == 0:
        print(bcolors.DIM + "No matching pattern." + bcolors.ENDC)

def display_axioms_and_rules(choice=False):
    if choice == False or choice == "axioms":
        index = 0
        for i in range(len(RULES['AXIOMS'])):
            axiom_name = RULES['AXIOMS_NAMES'][i]
            max_axiom_name_length = max(map(int,(len(x) for x in RULES['AXIOMS_NAMES'])))
            cur_axiom_name_length = len(axiom_name)
            axiom = NULL.join(map(str,[x.symbol for x in RULES['AXIOMS'][i]]))
            symbol_prop_id = SYMBOLS['OP'][SYMBOLS['OP NAMES'].index("PROP_ID")]
            if axiom_name == "" :
                #print("\t(A{})".format(index) + NULL * max_axiom_name_length + NULL * len(symbol_prop_id) + "  \t {}".format(axiom))
                print(bcolors.OKBLUE + "\tA{}  ".format(index) + NULL * max_axiom_name_length + NULL * len(symbol_prop_id) + "  \t {}".format(axiom) + bcolors.ENDC)
            else :
                #print("\t(A{} ".format(index) + str(symbol_prop_id) + " {})".format(axiom_name) + NULL * (max_axiom_name_length - cur_axiom_name_length) + "\t {}".format(axiom))
                print(bcolors.OKBLUE + "\tA{} ".format(index) + str(symbol_prop_id) + " {}".format(axiom_name) + NULL * (max_axiom_name_length - cur_axiom_name_length) + " \t{}".format(axiom) + bcolors.ENDC)
            index += 1
        if index == 0:
            print(bcolors.DIM + "No axioms in memory." + bcolors.ENDC)
    if choice == False or choice == "rules":
        index = 0
        for i in range(len(RULES['REWRITE_RULES'])):
            rule_name = RULES['REWRITE_RULES_NAMES'][i]
            max_rule_name_length = max(map(int,(len(x) for x in RULES['REWRITE_RULES_NAMES'])))
            cur_rule_name_length = len(rule_name)
            rule = NULL.join(map(str,[x.symbol for x in RULES['REWRITE_RULES'][i]]))
            symbol_prop_id = SYMBOLS['OP'][SYMBOLS['OP NAMES'].index("PROP_ID")]
            if rule_name == "" :
                #print("\t(R{})".format(index) + NULL * max_rule_name_length + NULL * len(symbol_prop_id) + "  \t {}".format(rule))
                print(bcolors.OKBLUE + "\tR{}  ".format(index) + NULL * max_rule_name_length + NULL * len(symbol_prop_id) + "  \t{}".format(rule) + bcolors.ENDC)
            else :
                #print("\t(R{} ".format(index) + str(symbol_prop_id) + " {})".format(rule_name) + NULL * (max_rule_name_length - cur_rule_name_length) + "\t {}".format(rule))
                print(bcolors.OKBLUE + "\tR{} ".format(index) + str(symbol_prop_id) + " {}".format(rule_name) + NULL * (max_rule_name_length - cur_rule_name_length) + " \t{}".format(rule) + bcolors.ENDC)
            index += 1
        if index == 0:
            print(bcolors.DIM + "No rules in memory." + bcolors.ENDC)

def human_readable(CHAIN):
    return NULL.join(map(str,[x.symbol for x in CHAIN]))
