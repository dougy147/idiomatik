#!/usr/bin/env python3

from lexer import *
from read_table import *
from colors import *

''' The PARSER receives TOKENS from the LEXER.
So it takes a LIST of LISTS as INPUT, given a TOKEN takes the following structure : [['str']['op']['str']]
Its job is to evaluate if a TOKEN is a "well formed proposition".
'''


def PARSE(TOKEN,ERROR_LOG=True):
    if len(TOKEN) == 0: return [True, TOKEN]
    if not check_surrounders(TOKEN,ERROR_LOG=ERROR_LOG): return [False, TOKEN]
    if not check_operators(TOKEN,ERROR_LOG=ERROR_LOG): return [False, TOKEN]
    return [True, TOKEN]

def check_surrounders(TOKEN,ERROR_LOG = True):
    SUR = [x for x in filter(lambda y: y[0] == 'SUR',TOKEN)]
    if len(SUR) == 0: return True
    open_count   = NULL.join(map(str, [x[2] for x in SUR])).count("open")
    close_count  = NULL.join(map(str, [x[2] for x in SUR])).count("close")
    wrap_count   = NULL.join(map(str, [x[2] for x in SUR])).count("wrap")
    if open_count != close_count :
        if open_count > close_count: type_missing = "closing"
        else :                       type_missing = "opening"
        if ERROR_LOG :
            print(bcolors.FAIL + "ERROR: missing {} {} parenthesis.".format(abs(open_count-close_count),type_missing) + bcolors.ENDC)
        return False
    if not wrap_count % 2 == 0 :
        if ERROR_LOG : print(bcolors.FAIL + "ERROR: missing one wrapping symbol." + bcolors.ENDC)
        return False
    for i in range(len(SUR)):
        if SUR[i][2][1] == 'open':
            match_found = False
            for j in range(i,len(SUR)):
                if SUR[j][2][2] > SUR[i][2][2]:   continue
                elif SUR[j][2][2] < SUR[i][2][2]:
                    if ERROR_LOG :
                        print(bcolors.FAIL + "ERROR: incorrect nesting." + bcolors.ENDC)
                    return False
                if SUR[j][2][1] == 'close' and \
                        SUR[j][2][0] == SUR[i][2][0]:
                            match_found = True
                            break
            if not match_found :
                if ERROR_LOG :
                    print(bcolors.FAIL + "ERROR: incorrect nesting." + bcolors.ENDC)
                return False
    return True

def check_operators(TOKEN, ERROR_LOG=True):
    OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]
    if len(OPS) == 0 : return True
    for OP in OPS:
        if not check_operands(OP,TOKEN,ERROR_LOG=ERROR_LOG): return False
    return True

def check_operands(OPERATOR,TOKEN,EXTRACT_OPERAND = False,ERROR_LOG = True):
    ''' EXTRACT_OPERAND is here in case we need to extract an operator's operand(s)
    for example in the "silent_surrounding()" function.
    '''
    op_index          = OPERATOR[3]
    operands_position = OPERATOR[2][2]
    last_index        = op_index
    operands          = []
    precedence        = OPERATOR[2][3]
    # LR
    for i in range(len(operands_position)):
        if i != 0:
            if operands_position[i] == operands_position[i-1]:
                last_operand = get_operand(OPERATOR,TOKEN,operands_position[i-1],last_index)
                if operands_position[i] == 'L':
                    last_index = last_operand[1][0][3]
                if operands_position[i] == 'R':
                    last_index = last_operand[1][len(last_operand[1])-1][3]
            else :
                last_index = op_index
        if precedence == 0: last_index = op_index # TODO : test in progress
        if not get_operand(OPERATOR,TOKEN,operands_position[i],last_index)[0] :
            if ERROR_LOG:
                print(bcolors.FAIL + "ERROR: invalid operand for operator '{}' at index '{}'.".format(OPERATOR[1],op_index) + bcolors.ENDC)
            if not EXTRACT_OPERAND: return False
            else :                  return [False, []]
        #print(OPERATOR[1],get_operand(OPERATOR,TOKEN,operands_position[i],last_index))
        if EXTRACT_OPERAND :
            operands.append(get_operand(OPERATOR,TOKEN,operands_position[i],last_index)[1])
    if not EXTRACT_OPERAND:
        return True
    else :
        #print(get_operand(OPERATOR,TOKEN,operands_position[i],last_index)[1])
        return [True, operands]
    #return True


def get_operand(OPERATOR, TOKEN, DIRECTION, index):
    if DIRECTION == "L":
        direction, break_point = -1, -1
        add_surrounder, substract_surrounder = 'close', 'open'

    if DIRECTION == "R":
        direction, break_point = +1, len(TOKEN)
        add_surrounder, substract_surrounder = 'open', 'close'
    ''' Test for operators with 0 precedence '''
    precedence = OPERATOR[2][3]
    if precedence == 0: operator_index = OPERATOR[3]
    else :              index += direction
    #index += direction
    ''''''
    surrounder_counter, operand = 0, []
    found_operand = False

    if index < 0 or index >= len(TOKEN): return [False,[]]

    ''' For 0-precedence operators '''
    if precedence == 0:
        index = 0
        while found_operand == False:
            if index < 0 or index >= len(TOKEN): return [False,[]]
            if DIRECTION == "L" :
                if index >= operator_index: break
                operand_to_test = NULL.join(map(str,[x[1] for x in TOKEN[index:operator_index]]))
            elif DIRECTION == "R" :
                if len(TOKEN) - index <= operator_index + 1: break
                operand_to_test = NULL.join(map(str,[x[1] for x in TOKEN[operator_index+1:len(TOKEN)-index]]))
            if PARSE(TOKENIZE(operand_to_test), ERROR_LOG=False)[0]:
                found_operand = True
                operand_token = PARSE(TOKENIZE(operand_to_test), ERROR_LOG=False)[1]
                for k in range(len(operand_token)):
                    if DIRECTION == "L":
                        operand.append(TOKEN[index+k])
                    elif DIRECTION == "R":
                        operand.append(TOKEN[operator_index+1+k])
                #print(operand)
                return [True, operand]
            index += 1
        return [False,[]]
    ''''''

    if TOKEN[index][0] == 'STR' or \
            (TOKEN[index][0] == 'META' and TOKEN[index][2][0] == 'ANY_STR') or \
            (TOKEN[index][0] == 'META' and TOKEN[index][2][0] == 'ANY_OPERAND') or \
            (TOKEN[index][0] == 'META' and TOKEN[index][2][0] == 'ANY_VALID_EXP') : return [True,[TOKEN[index]]]

    if TOKEN[index][0] == 'OP':
        if DIRECTION != TOKEN[index][2][2]: # if meet operator that doesn't go the same direction (exclusively): False
            return [False,[TOKEN[index]]]

    if TOKEN[index][0] == 'SUR':
        if TOKEN[index][2][1] == substract_surrounder : return [False,[TOKEN[index]]]
        else :
            operand.append(TOKEN[index])
            surrounder_counter+=1
            index += direction

    while found_operand == False or surrounder_counter != 0 :
        if index == break_point :
            if DIRECTION == "L": operand = [x for x in reversed(operand)]
            return [False, operand]

        if not found_operand and TOKEN[index][0] == 'OP':
            if DIRECTION != TOKEN[index][2][2]:
                return [False,[TOKEN[index]]]

        if TOKEN[index][0] == 'SUR':
            found_operand = True
            if TOKEN[index][2][1] == substract_surrounder : surrounder_counter-=1
            if TOKEN[index][2][1] == add_surrounder : surrounder_counter+=1

        if TOKEN[index][0] == 'STR' or \
                (TOKEN[index][0] == 'META' and TOKEN[index][2][0] == 'ANY_STR') or \
                (TOKEN[index][0] == 'META' and TOKEN[index][2][0] == 'ANY_OPERAND') or \
                (TOKEN[index][0] == 'META' and TOKEN[index][2][0] == 'ANY_VALID_EXP') : found_operand = True

        operand.append(TOKEN[index])
        index += direction
    if DIRECTION == "L": operand = [x for x in reversed(operand)]
    return [True, operand]



class Parse:
    def __init__(self,token,ERROR_LOG=True): self.token,self.cursor, self.ERROR_LOG = token, 0, ERROR_LOG
    def validity(self): return PARSE(self.token,self.ERROR_LOG)[0]
    def parsed(self):   return PARSE(self.token,self.ERROR_LOG)[1]
    def populate_operands(self):
        for i in range(len(self.token)):
            if self.is_operator(i):
                get_operands = check_operands(self.token[i],self.token,EXTRACT_OPERAND = True,ERROR_LOG = False)
                if get_operands[0]:
                    for j in range(len(get_operands[1])):
                        self.token[i][2][4][j] = get_operands[1][j]
                else :
                    for j in range(len(self.token[i][2][4])):
                        self.token[i][2][4][j] = False
        return self.token
    def get_operands(self,operator_token):   return check_operands(operator_token,self.token,EXTRACT_OPERAND = True,ERROR_LOG = False)[1]
    def get_index_in_token(self):   return self.token[3]
    def is_operator(self):          return self.token[0] == 'OP'
    def is_surrounder(self):        return self.token[0] == 'SUR'
    def is_meta(self):              return self.token[0] == 'META'
    def is_string(self):            return self.token[0] == 'STR'
    def is_surrounder_open(self):   return self.token[2][1] == 'open'
    def is_surrounder_close(self):  return self.token[2][1] == 'close'
    def is_surrounder_wrap(self):   return self.token[2][1] == 'wrap'
    def is_operator_at_index(self,index):    return self.token[index][0] == 'OP'
    def is_surrounder_at_index(self,index):  return self.token[index][0] == 'SUR'
    def is_meta_at_index(self,index):        return self.token[index][0] == 'META'
    def is_string_at_index(self,index):      return self.token[index][0] == 'STR'
    def is_surrounder_open_at_index(self,index):  return self.token[index][2][1] == 'open'
    def is_surrounder_close_at_index(self,index): return self.token[index][2][1] == 'close'
    def is_surrounder_wrap_at_index(self,index):  return self.token[index][2][1] == 'wrap'
    def is_unary(self):  return self.token[2][1] == 'unary'
    def is_binary(self): return self.token[2][1] == 'binary'
    def has_right_operand(self): return self.token[2][2] == 'R'
    def has_left_operand(self):  return self.token[2][2] == 'L'
    def precedence(self):                   return self.token[2][3]
    def precedence_at_index(self,index):    return self.token[index][2][3]

#x = Lex("a + (b").tokenize()
#a = Parse(x)
#print(a.is_operator_at_index(1))
#b = Parse(x)
#print(b.validity())
