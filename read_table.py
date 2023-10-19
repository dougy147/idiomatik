#!/usr/bin/env python3

from colors import *

STREAM = []
TABLE_FILE = "SYMBOLS"
with open(TABLE_FILE) as table:
    for line in table.readlines():
        STREAM.append(line.replace('\n','').replace('\t',' '))
table.close()

SYMBOLS = {}
SYMBOLS['SYMBOLS_CATEGORIES'] = []
#print(len(STREAM))

for i in range(len(STREAM)):
    if i == 0 :
        ''' Use first line to detect syntax inside the file '''
        start_sym, delimitor, end_sym = STREAM[i][0],STREAM[i][1],STREAM[i][2]
        I = STREAM[i][3:]
        while len(I) > 0:
            if not I[0] == start_sym:
                I=I[1:]
                continue
            else:
                I=I[1:]
                DESCRIPTOR_ID = ""
                while not I[0] == delimitor:
                    DESCRIPTOR_ID+=I[0]
                    I=I[1:]
                I=I[1:]
                DESCRIPTOR_VAL = ""
                while not I[0] == end_sym:
                    DESCRIPTOR_VAL+=I[0]
                    I=I[1:]
                vars().__setitem__(DESCRIPTOR_ID,DESCRIPTOR_VAL)
                SYMBOLS[DESCRIPTOR_ID] = DESCRIPTOR_VAL
            I=I[1:]
    else :
        I = STREAM[i]
        if   I[0:len(COMMENT)] == COMMENT or I == "" : continue
        while I[0] == NULL and len(I) > 0:
            I=I[1:]
        instruction = ""
        if I[0:len(ID)] == ID:
            I=I[len(ID):]
            SYMBOL_CATEGORY      = ""
            SUB_CATEGORY_CUR     = ""
            SUB_CATEGORY_COUNTER = 0
            SUB_CATEGORIES       = []
            while I[0:len(NULL)] != NULL and len(I) > 0:
                SYMBOL_CATEGORY+=I[0]
                I=I[1:]
            SYMBOLS['SYMBOLS_CATEGORIES'].append(SYMBOL_CATEGORY)
            SYMBOLS[SYMBOL_CATEGORY] = []
            while len(I) > 0:
                if I[0:len(NULL)] == NULL:
                    I=I[len(NULL):]
                    continue
                else:
                    SUB_CATEGORY_COUNTER += 1
                    SUB_CATEGORY_CUR = SYMBOL_CATEGORY+" "
                    while len(I) > 0:
                        if I[0:len(NULL)] == NULL:
                            I=I[len(NULL):]
                            break
                        SUB_CATEGORY_CUR+=I[0]
                        I=I[1:]
                    SYMBOLS[SUB_CATEGORY_CUR] = []
                    SUB_CATEGORIES.append(SUB_CATEGORY_CUR)
        else:
            while len(I) > 0:
                if I[0:len(NULL)] == NULL:
                    I=I[len(NULL):]
                    continue
                symbol = ""
                while I[0:len(NULL)] != NULL and len(I) > 0 :
                    symbol+=I[0]
                    I=I[1:]
                SYMBOLS[SYMBOL_CATEGORY].append(symbol)
                break
            for j in range(SUB_CATEGORY_COUNTER):
                while len(I) > 0:
                    if I[0:len(NULL)] == NULL:
                        I=I[len(NULL):]
                        continue
                    sub_cat_value = ""
                    while I[0:len(NULL)] != NULL and len(I) > 0 :
                        sub_cat_value+=I[0]
                        I=I[1:]
                    SYMBOLS[SUB_CATEGORIES[j]].append(sub_cat_value)
                    break
                if len(SYMBOLS[SYMBOL_CATEGORY]) != len(SYMBOLS[SUB_CATEGORIES[j]]):
                    print(bcolors.FAIL + "ERROR: missing property for symbol '{}' in file '{}' (line {}).".format(symbol,TABLE_FILE,i+1) + bcolors.ENDC)
                    exit(1)
#print(SYMBOLS)
