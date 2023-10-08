#!/usr/bin/env python3

STREAM = []
TABLE_FILE = "SYMBOLS"
with open(TABLE_FILE) as table:
    for line in table.readlines():
        if not line == '\n':
            STREAM.append(line.replace('\n',''))
table.close()

SYMBOLS = {}
for i in range(len(STREAM)):
    if i == 0 :
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
        #SYMBOLS[DESCRIPTOR_ID] = DESCRIPTOR_VAL
        I = STREAM[i]
        while I[0] == NULL and len(I) > 0:
            I=I[1:]
        instruction = ""
        if   I[0:len(COMMENT)]    == COMMENT: continue
        elif I[0:len(ID)] == ID:
            I=I[len(ID):]
            SYMBOL_CATEGORY = ""
            while len(I) > 0:
                SYMBOL_CATEGORY+=I[0]
                I=I[1:]
            LAST_SYMBOL_CATEGORY = SYMBOL_CATEGORY
        elif I[0:len(SUB_ID)] == SUB_ID:
            I=I[len(SUB_ID):]
            SYMBOL_CATEGORY = LAST_SYMBOL_CATEGORY+" "
            while len(I) > 0:
                SYMBOL_CATEGORY+=I[0]
                I=I[1:]
        else:
            CUR_SYMBOLS = []
            while len(I) > 0:
                if I[0:len(NULL)] == NULL:
                    I=I[len(NULL):]
                    continue
                symbol = ""
                while len(I) > 0 and I[0:len(NULL)] != NULL:
                    symbol+=I[0]
                    I=I[1:]
                CUR_SYMBOLS.append(symbol)
                I=I[1:]
            SYMBOLS[SYMBOL_CATEGORY] = CUR_SYMBOLS

#print(SYMBOLS)
