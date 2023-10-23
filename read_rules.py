#!/usr/bin/env python3

# Rules are imported from the file "RULES".
# If a rule contains a '=>' (REWRITE_AS) symbol, it is immediately considered a REWRITE RULE.
# Else it is considered an AXIOM.

from read_table import *
from lexer import *
from parser import *
from colors import *

global RULES
RULES = {'AXIOMS'             : [],
         'AXIOMS_NAMES'       : [],
         'REWRITE_RULES'      : [],
         'REWRITE_RULES_NAMES': []}

def IMPORT_RULES(STREAM,RULES_FILE = None,add_rules=True,add_axioms=True):
    global RULES
    if RULES_FILE != None:
        STREAM = []
        #RULES_FILE = "RULES"
        with open(RULES_FILE) as rules:
            for line in rules.readlines():
                if not line == '\n':
                    STREAM.append(line.replace('\n',''))
        rules.close()


    for i in range(len(STREAM)):
            I = STREAM[i]
            #while I[0] == NULL and len(I) > 0:
            while len(I) > 0 and I[0] == NULL:
                I=I[1:]
            if I[0:len(COMMENT)] == COMMENT: continue
            else:
                #RULE = PARSE(TOKENIZE(I))
                RULE = PARSE(I)
                if RULE.validity:
                    invalid = False
                    # Grab name of rule
                    NAME = ""
                    naming_counter = 0
                    #for i in range(len(RULE[1])):
                    for token in RULE.tokens:
                        #if is_operator(token):
                        #if SYMBOLS['OP NAMES'][SYMBOLS['OP'].index(RULE[1][i][1])] == "PROP_ID":
                        if token.name == "PROP_ID":
                            naming_counter += 1
                            #NAME = NULL.join(map(str,[x.symbol for x in token.operands[0]]))
                            NAME = ''.join(map(str,[x.symbol for x in token.operands[0]]))
                    if naming_counter > 1 : invalid = True # it means more than 1 PROP_ID : so multiple names
                    if NAME != "" and invalid == False : # it means that 'PROP_ID' operator was in the expression, so remove it from expression
                        #for i in range(len(RULE[1])):
                        for i in range(len(RULE.tokens)):
                            if is_operator(RULE.tokens[i]) and RULE.tokens[i].name == "PROP_ID":
                                #if SYMBOLS['OP NAMES'][SYMBOLS['OP'].index(RULE[1][i][1])] == "PROP_ID":
                                    for j in range(0,i+1):
                                        RULE.tokens.pop(0)   # pop FIRST element each time!
                                    break
                    # Grab type of rule
                    rewrite = False
                    rewrite_counter = 0
                    for token in RULE.tokens:
                        #if is_operator(token):
                        if token.name == "REWRITE_AS":
                        #if SYMBOLS['OP NAMES'][SYMBOLS['OP'].index(token[1])] == "REWRITE_AS":
                            rewrite = True
                            rewrite_counter += 1
                        if rewrite_counter > 1:
                            invalid = True
                            break
                    if   invalid :
                        print(bcolors.WARNING + "WARNING: invalid rule (too many names or 'rewrite' symbols in file '{}': '{}'".format(RULES_FILE,I) + bcolors.ENDC)
                    elif not rewrite :
                        if add_axioms == False:
                            print(bcolors.FAIL + "ERROR: rules need the rewrite symbol." + bcolors.ENDC)
                            continue
                        if RULE.tokens in RULES['AXIOMS'] :
                            print(bcolors.OKBLUE + "INFO: axiom '{}' already stored.".format(I) + bcolors.ENDC)
                            continue
                        RULES['AXIOMS'].append(RULE.tokens)
                        name_exist = False
                        FNAME = NAME
                        while NAME in RULES['AXIOMS_NAMES'] and NAME != "" : # ignore if name is empty
                            name_exist = True
                            try:
                                RENAME = str(NAME[0:len(NAME)-1]) + str(int(NAME[len(NAME)-1])+1)
                            except :
                                RENAME = NAME + "0"
                            NAME = RENAME
                        if name_exist == True:
                            print(bcolors.DIM + bcolors.WARNING + "INFO: axiom '{}', name '{}' exists. Renamed '{}'.".format(I,FNAME,RENAME) + bcolors.ENDC)
                        RULES['AXIOMS_NAMES'].append(NAME)
                        print(bcolors.DIM + bcolors.OKBLUE + "INFO: imported axiom '{}'.".format(I) + bcolors.ENDC)
                        #counter_rewrite_axioms += 1
                    else :
                        if add_rules == False:
                            print(bcolors.FAIL + "ERROR: rules are not considered axioms. Correct or not? Time to think about it..." + bcolors.ENDC)
                            continue
                        if RULE.tokens in RULES['REWRITE_RULES'] :
                            print(bcolors.DIM + bcolors.OKBLUE + "INFO: rule '{}' already stored.".format(I) + bcolors.ENDC)
                            continue
                        RULES['REWRITE_RULES'].append(RULE.tokens)
                        name_exist = False
                        FNAME = NAME
                        while NAME in RULES['REWRITE_RULES_NAMES'] and NAME != "" : # ignore if name is empty
                            name_exist = True
                            try:
                                RENAME = str(NAME[0:len(NAME)-1]) + str(int(NAME[len(NAME)-1])+1)
                            except :
                                RENAME = NAME + "0"
                            NAME = RENAME
                        if name_exist == True:
                            print(bcolors.DIM + bcolors.WARNING + "INFO: rule '{}', name '{}' exists. Renamed '{}'.".format(I,FNAME,RENAME) + bcolors.ENDC)
                        RULES['REWRITE_RULES_NAMES'].append(NAME)
                        print(bcolors.DIM + bcolors.OKBLUE + "INFO: imported rule '{}'.".format(I) + bcolors.ENDC)
                        #counter_rewrite_rules += 1
                else:
                    if RULES_FILE == None:
                        print(bcolors.WARNING + "WARNING: invalid rule: '{}'".format(I) + bcolors.ENDC)
                    else :
                        print(bcolors.WARNING + "WARNING: invalid rule from file '{}': '{}'".format(RULES_FILE,I,i) + bcolors.ENDC)

#IMPORT_RULES(STREAM,RULES_FILE = "./rules/logic")
#print(SYMBOLS)
#print(RULES)
#for r in RULES['REWRITE_RULES']:
#    print(' '.join(map(str,[x.symbol for x in r])))
