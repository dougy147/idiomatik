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

def display_all_possible_rewritings(INPUT):
    '''Temporary function to show ALL possible rewrites
     for an INPUT (proposition) given the set of RULES'''
    token = TOKENIZE(INPUT)
    parse = PARSE(token)
    if not parse[0] :
        print("Invalid proposition")
        exit(0)
    #check = CHECK(parse)
    check = combine_all_possible_rewrites(token)
    if not check[0] :
        print("No matching rewritings rule for '{}'".format(NULL.join(map(str,[x[1] for x in token]))))
    REWRITES = [y[0] for y in [x for x in check[1]]]
    counter = 0
    redundant = 0
    STR_REWRITES = []
    for rew in REWRITES:
        str_rewrite = NULL.join(map(str,[x[1] for x in rew]))
        if not str_rewrite in STR_REWRITES :
            STR_REWRITES.append(rew)
        else :
            redundant+=1
            continue
        print(str_rewrite)
        counter+=1
    print("\n{} possible rewritings".format(counter))
    if redundant > 0: print("{} redundancies...".format(redundant))



#a = "(((((((c))))))) + b => (~ a)"
#a = "~ (A) + (B) + (c) + (d)"
#a = "p => q"
##print("-----------------------")
#print("PROP: {}\n".format(a))
#print(CHECK(PARSE(TOKENIZE(a))))
