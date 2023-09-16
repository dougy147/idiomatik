#!/usr/bin/env python3

# Rules are imported from the file "RULES".
# If a rule contains a '=>' (REWRITE_AS) symbol, it is immediately considered a REWRITE RULE.
# Else it is considered an AXIOM.

from read_table import *
from lexer import *
from parser import *

STREAM = []
RULES_FILE = "RULES"
with open(RULES_FILE) as rules:
    for line in rules.readlines():
        if not line == '\n':
            STREAM.append(line.replace('\n',''))
rules.close()

RULES = {'AXIOMS'       : [],
         'REWRITE_RULES': []}

for i in range(len(STREAM)):
        I = STREAM[i]
        while I[0] == NULL and len(I) > 0:
            I=I[1:]
        if I[0:len(COMMENT)] == COMMENT: continue
        else:
            RULE = PARSE(TOKENIZE(I))
            if RULE[0]:
                rewrite = False
                for token in RULE[1]:
                    if token[1] in SYMBOLS['OPERATORS']:
                        if SYMBOLS['OPERATORS NAMES'][SYMBOLS['OPERATORS'].index(token[1])] == "REWRITE_AS":
                            rewrite = True
                            break
                if not rewrite : RULES['AXIOMS'].append(RULE[1])
                else           : RULES['REWRITE_RULES'].append(RULE[1])
            else:
                print("WARNING: Invalid rule in file '{}': '{}'".format(RULES_FILE,I,i))
