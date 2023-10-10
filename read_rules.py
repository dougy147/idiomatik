#!/usr/bin/env python3

# Rules are imported from the file "RULES".
# If a rule contains a '=>' (REWRITE_AS) symbol, it is immediately considered a REWRITE RULE.
# Else it is considered an AXIOM.

from read_table import *
from lexer import *
from parser import *
from colors import *

STREAM = []
RULES_FILE = "RULES"
with open(RULES_FILE) as rules:
    for line in rules.readlines():
        if not line == '\n':
            STREAM.append(line.replace('\n',''))
rules.close()

RULES = {'AXIOMS'             : [],
         'AXIOMS_NAMES'       : [],
         'REWRITE_RULES'      : [],
         'REWRITE_RULES_NAMES': []}

#counter_rewrite_rules  = 0
#counter_rewrite_axioms = 0
def READ_RULES(STREAM,add_rules=True,add_axioms=True):
    for i in range(len(STREAM)):
            I = STREAM[i]
            while I[0] == NULL and len(I) > 0:
                I=I[1:]
            if I[0:len(COMMENT)] == COMMENT: continue
            else:
                RULE = PARSE(TOKENIZE(I))
                if RULE[0]:
                    invalid = False
                    # Grab name of rule
                    NAME = ""
                    naming_counter = 0
                    for i in range(len(RULE[1])):
                        if RULE[1][i][1] in SYMBOLS['OPERATORS']:
                            if SYMBOLS['OPERATORS NAMES'][SYMBOLS['OPERATORS'].index(RULE[1][i][1])] == "PROPOSITION_IDENTIFIER":
                                naming_counter += 1
                                for j in range(0,i):
                                    if j > 0 : NAME += NULL
                                    NAME += str(RULE[1][j][1])
                    if naming_counter > 1 : invalid = True
                    if NAME != "" and invalid == False : # it means that 'PROPOSITION_IDENTIFIER' operator was in the expression, so remove it from expression
                        for i in range(len(RULE[1])):
                            if RULE[1][i][1] in SYMBOLS['OPERATORS']:
                                if SYMBOLS['OPERATORS NAMES'][SYMBOLS['OPERATORS'].index(RULE[1][i][1])] == "PROPOSITION_IDENTIFIER":
                                    for j in range(0,i+1):
                                        RULE[1].pop(0)   # pop FIRST element each time!
                                    break
                    # Grab type of rule
                    rewrite = False
                    rewrite_counter = 0
                    for token in RULE[1]:
                        if token[1] in SYMBOLS['OPERATORS']:
                            if SYMBOLS['OPERATORS NAMES'][SYMBOLS['OPERATORS'].index(token[1])] == "REWRITE_AS":
                                rewrite = True
                                rewrite_counter += 1
                            if rewrite_counter > 1:
                                invalid = True
                                break
                    if   invalid :
                        print(bcolors.WARNING + "WARNING: Invalid rule (too many names or 'rewrite' symbols in file '{}': '{}'".format(RULES_FILE,I) + bcolors.ENDC)
                    elif not rewrite :
                        if add_axioms == False:
                            print(bcolors.FAIL + "Rules need the rewrite symbol." + bcolors.ENDC)
                            continue
                        if RULE[1] in RULES['AXIOMS'] :
                            print(bcolors.WARNING + "Axiom '{}' already stored!".format(I) + bcolors.ENDC)
                            continue
                        RULES['AXIOMS'].append(RULE[1])
                        RULES['AXIOMS_NAMES'].append(NAME)
                        #counter_rewrite_axioms += 1
                    else :
                        if add_rules == False:
                            print(bcolors.FAIL + "Rules are not considered axioms. Correct or not? Time to think about it..." + bcolors.ENDC)
                            continue
                        if RULE[1] in RULES['REWRITE_RULES'] :
                            print(bcolors.WARNING + "Rule '{}' already stored!".format(I) + bcolors.ENDC)
                            continue
                        RULES['REWRITE_RULES'].append(RULE[1])
                        RULES['REWRITE_RULES_NAMES'].append(NAME)
                        #counter_rewrite_rules += 1
                else:
                    print(bcolors.WARNING + "WARNING: Invalid rule in file '{}': '{}'".format(RULES_FILE,I,i) + bcolors.ENDC)

READ_RULES(STREAM)
