#!/usr/bin/env python3

from lexer import *
from parser import *


user_input = Lex("a + b = c")
pattern_to_match = Lex("$A <*> $B")

print(user_input.chain)
print(pattern_to_match.chain)


pattern_to_match.next_token()
print(pattern_to_match.token)
pattern_to_match.next_token()
print(pattern_to_match.token)
pattern_to_match.next_token()
print(pattern_to_match.token)
