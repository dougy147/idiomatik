#!/usr/bin/env python3

from read_table import *
from lexer import *
from parser import *
from read_rules import *
from checker import *
from rewriter import *

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

    # Remove cells that are empty on same index for every row (remove empty columns)
    columns_to_ignore = []
    for i in range(len(FINAL_MATRICE[0])):  # number of columns
        are_all_empty = True
        for j in range(len(FINAL_MATRICE)): # number of raws
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

    #print("+------------ tree of {}".format([x[1] for x in TOKEN]))
    print("-+++----------- tree -----------+")
    index = 0
    for line in ULTIMATE_MATRICE:
        print("#{} | {}".format(index,line))
        index+=1
    print("\n")



def display_all_possible_rewritings(INPUT):
    '''Temporary function to show ALL possible rewrites
     for an INPUT (proposition) given the set of RULES'''
    token = TOKENIZE(INPUT)
    #print(token)
    parse = PARSE(token)
    if not parse[0] :
        print("Invalid proposition")
        exit(0)
    #check = CHECK(parse)
    check = combine_all_possible_rewrites(token)
    if not check[0] :
        print("No matching rewritings rule for '{}'".format(NULL.join(map(str,[x[1] for x in token]))))
    #for y in [x for x in check[1]] :
    #    print(y[0])
    REWRITES = [y[0] for y in [x for x in check[1]]] # Storing tokens of possible rewritings
    counter = 0
    redundant = 0
    STR_REWRITES = []
    #print("REWRITES:",REWRITES)
    for rew in REWRITES:
        str_rewrite = NULL.join(map(str,[x[1] for x in rew])) # Transform tokens to human readable string
        if not str_rewrite in STR_REWRITES :
            STR_REWRITES.append(rew)
        else :
            redundant+=1
            continue
        print(str_rewrite)
        counter+=1
    #print("\n{} possible rewritings".format(counter))
    if redundant > 0: print("{} redundancies...".format(redundant))

def display_axioms_and_rules():
    #print(len(RULES['AXIOMS']), "axioms in RULES:\n")
    print("+----- AXIOMS -----+")
    index = 0
    for axioms in RULES['AXIOMS']:
        print("\t(A{}) \t {}".format(index,NULL.join(map(str,[x[1] for x in axioms]))))
        index += 1
    print("\n")
    index = 0
    #print(len(RULES['REWRITE_RULES']), "transformation rules in RULES:\n")
    print("+----- RULES ------+")
    for rules in RULES['REWRITE_RULES']:
        print("\t(R{}) \t {}".format(index,NULL.join(map(str,[x[1] for x in rules]))))
        index += 1



#a = "(((((((c))))))) + b => (~ a)"
#a = "~ (A) + (B) + (c) + (d)"
#a = "p => q"
##print("-----------------------")
#print("PROP: {}\n".format(a))
#print(CHECK(PARSE(TOKENIZE(a))))
