#!/usr/bin/env python3

from read_table import *
from lexer import *
from parser import *
from read_rules import *
from rewriter import *

''' The CHECKER job is to assess a correspondance between a RULE and TOKENS it receives.
RULES are already VALID propositions stored as LISTS (eg. [STR][OP][STR]).
If the token is FALSE it returns [False, TOKEN, [] ].
If RULES is an empty list the CHECKER returns [True, TOKEN, [RULE]]
If a TOKEN corresponds to RULE_x, we append [True, TOKEN, RULE_x] to MATCHES.
If the TOKEN contradicts RULE_y, we append [False, TOKEN, RULE_y] to MATCHES.
MATCHES are then of the structure [ [Bool,TOKEN=[Bool,List],[RULE_x]], [Bool,[Bool,List],[RULE_y]], ... ]

From now it will make call to the REWRITER
'''

def CHECK(TOKEN):
    if not PARSE(TOKEN)[0] : return [False, TOKEN, [[]]]
    if len(TOKEN) == 0     : return [True, TOKEN, [RULES]]
    if len(RULES) == 0     : return [True, TOKEN, [RULES]]

def check_axiom(TOKEN):
    ''' For AXIOMS in RULES, check if AXIOM is equivalent to a TOKEN'''
    # should also check when token is rewritten by compatible REWRITE_RULES
    for axiom in RULES['AXIOMS']:
        if axiom == TOKEN:
            print("Axiom '{}' = token '{}'".format([x[1] for x in axiom], [x[1] for x in TOKEN]))
            return [True, axiom, TOKEN]
    return [False, [], TOKEN]



#a = "(((((((c))))))) + b => (~ a)"
#a = "~ (A) + (B) + (c) + (d)"
#a = "p => q"
##print("-----------------------")
#print("PROP: {}\n".format(a))
#print(CHECK(PARSE(TOKENIZE(a))))
