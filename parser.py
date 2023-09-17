#!/usr/bin/env python3

from read_table import *

''' The PARSER receives TOKENS from the LEXER.
So it takes a LIST of LISTS as INPUT, given a TOKEN takes the following structure : [['str']['op']['str']]
Its job is to evaluate if a TOKEN is a "well formed proposition".
'''


def PARSE(TOKEN):
    if len(TOKEN) == 0: return [True, TOKEN]
    if not check_surrounders(TOKEN): return [False, TOKEN]
    if not check_operators(TOKEN): return [False, TOKEN]
    return [True, TOKEN]

def check_surrounders(TOKEN):
    SUR = [x for x in filter(lambda y: y[0] == 'SUR',TOKEN)]
    if len(SUR) == 0: return True
    open_count   = NULL.join(map(str, [x[2] for x in SUR])).count("open")
    close_count  = NULL.join(map(str, [x[2] for x in SUR])).count("close")
    if open_count != close_count : return False
    for i in range(len(SUR)):
        if SUR[i][2][1] == 'open':
            match_found = False
            for j in range(i,len(SUR)):
                if SUR[j][2][2] > SUR[i][2][2]:   continue
                elif SUR[j][2][2] < SUR[i][2][2]: return False
                if SUR[j][2][1] == 'close' and \
                        SUR[j][2][0] == SUR[i][2][0]:
                            match_found = True
                            break
            if not match_found : return False
    return True

def check_operators(TOKEN):
    OPS = [x for x in filter(lambda y: y[0] == 'OP', TOKEN)]
    #print(OPS)
    if len(OPS) == 0 : return True
    for OP in OPS:
        if not check_operands(OP,TOKEN): return False
    return True

def check_operands(OPERATOR,TOKEN,EXTRACT_OPERAND = False):
    ''' EXTRACT_OPERAND is here in case we need to extract an operator's operand(s)
    for example in the "silent_surrounding()" function.
    '''
    op_index          = OPERATOR[3]
    operands_position = OPERATOR[2][2]
    last_index        = op_index
    operands          = []
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
        if not get_operand(OPERATOR,TOKEN,operands_position[i],last_index)[0] :
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
    index += direction
    surrounder_counter, operand = 0, []
    found_operand = False

    if index < 0 or index >= len(TOKEN): return [False,[]]

    if TOKEN[index][0] == 'STR': return [True,[TOKEN[index]]]

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

        if TOKEN[index][0] == 'STR':
            found_operand = True

        operand.append(TOKEN[index])
        index += direction
    if DIRECTION == "L": operand = [x for x in reversed(operand)]
    return [True, operand]




#a = [['SUR', '{', ['open', 'ACCOLADE'], 0], ['SUR', '[', ['open', 'BRAKET'], 1], ['SUR', '(', ['open', 'PARENTHESIS'], 2], ['OP', '~', ['unary', 'R'], 3], ['STR', 'A', 1, 4], ['SUR', ')', ['close', 'PARENTHESIS'], 5], ['SUR', ']', ['close', 'BRAKET'], 6], ['SUR', '}', ['close', 'ACCOLADE'], 7], ['OP', '+', ['binary', 'LR'], 8], ['STR', 'B', 1, 9], ['OP', '<=>', ['binary', 'LR'], 10], ['OP', '*', ['binary', 'LR'], 11], ['STR', 'B', 1, 12], ['OP', '+', ['binary', 'LR'], 13], ['STR', 'A', 1, 14], ['STR', 'C', 1, 15], ['OP', '*', ['binary', 'LR'], 16]]
#a = [['OP', '~', ['unary', 'R'], 0], ['STR', 'A', 1, 1], ['OP', '+', ['binary', 'LR'], 2], ['SUR', '(', ['open', 'PARENTHESIS'], 3], ['STR', 'B', 1, 4], ['OP', '+', ['binary', 'LR'], 5], ['STR', 'C', 1, 6], ['SUR', ')', ['close', 'PARENTHESIS'], 7], ['OP', '?', ['unary', 'L'], 8]]
#print(PARSE(a))
