Building my first interpreter with Python. A bit idiotic, partially automatic, fully idiomatic.


| NOTE        |
|:---------------------------|
| _This is rather a practice-oriented than a theoretically-driven learning project. The README is verbose for a simple reason : if I need to come back here after a long time, I don't want to lose too much boot time diving back in. Also, I don't have the vocabulary to be synthetic enough. I hope to keep the code clean and self-explanatory._ |

## Quick launch

```bash
git clone https://github.com/dougy147/idiomatik
cd idiomatik
./idiomatik
```

## Why?

I initially wanted to write a solving algorithm for the [Muddy Children Puzzle](https://en.wikipedia.org/wiki/Induction_puzzles#Muddy_Children_Puzzle). That led me to some questions about public/private knowledge, inference rules, well-formed formulas and other stuff I had never heard of, seriously thought of, or invested time in. What are those things? how to implement lexemes identification or evaluate syntax? why is model checking so hard?... those are things I'm interested in for now... until the fail ! lol.

So, I'm not reinventing the wheel, and this will be far from original or quality work. Just disorganized trials and errors, and random notes and code.
A lot of things here could be wrong or bad approximations, reflecting my ignorance in CS in general.
But why not share a "work" in progress?

## What it does

### Lexing : Raw input to tokens

`idiomatik` receives input strings (e.g. `a + b = c`) that are returned as *tokens*.
A token is a chain of elements extracted from the input by the *lexer*.
The lexer decomposes the input into individual elements (characters, or sequences of characters) corresponding to predefined categories (strings, operators, surrounders, etc.). (These *atomistic* categories and their elements are defined in the `SYMBOLS` table.)
When all the elements of an input have been attributed an identity (to what category they belong and eventually what are their properties), they are chained together and the construction of the token ends.

### Parsing : checking syntax

Tokens are then sent to the *parser* whose job is to assess *syntax* (i.e. is the chain of elements in the token a well-formed expression?).
The parser returns a truth value depending on the token being syntactically correct or not.

Syntax is immediately incorrect when one of those axioms is false :

- every closing surrounder (`)`, `]`, `}`) matches an opening opposite, at the same level of *nestedness* (opening a surrounder increments the level of nestedness by 1; closing decrements it)
- every *operator* has a correct amount of *operands* in proper position

If the token is syntactically valid, then the input is considered to be too.

### Rewriting : transforming expressions

When an input is a valid expression, `idiomatik` can *rewrite* it as another valid expression.
This transformation depends on a set of arbitrarly rules (i.e. *rewrite rules*) that the user can predefine (see `RULES`) or send on-the-fly :

```bash
./idiomatik
|> A => B --> ~A V B
|> add rule
|> p => q
|> rewrite full
~p V q
```

Rewrite rules put aside, `idiomatik` is gonna be used to solve expressions (work in progress).
It is by default [PEMDAS](https://en.wikipedia.org/wiki/Order_of_operations#Mnemonics) compliant, solving propositions in the "correct" order, even when parenthesis are missing. 
This is by default but it is configurable thanks to a precedence value given to operators in the `SYMBOLS` table.
If some special cases are not consensual when considering the "correct solving order" (e.g. [serial exponentiation](https://en.wikipedia.org/wiki/Order_of_operations#Special_cases)), `idiomatik` allows users to set the associative direction of operators as we stated above. In the `SYMBOLS` table negative priority values give right-to-left associativity, positive left-to-right, while null oppose their operands by "splitting" expressions. 

This process of desambiguation is of course of interest to solve expressions, but also to draw trees.

### Visualizing : drawing trees

`idiomatik` can draw basic trees (really basic trees) representing any given expression with `tree` or `draw`:

```bash
./idiomatik
|> a + b * c / d
|> draw
-+++----------+
#0 |  +
#1 | a    /
#2 |    *  d
#3 |   b c
```

## Control how `idiomatik` speaks and think

The file `SYMBOLS` contains a list of special characters and operators that play a role in `idiomatik`.
You can modify this file and add your own symbols, operators, and set their properties.

Operators' n-arity is set by signaling the position of their operands.
For example, giving an operator the `LR` property for it operands makes `idiomatik` consider it a binary operator. 
When parsing an expression it will be known that this specific operator requires one left and one right operands (without them, syntax would be invalid). 
(You can build as many operators you want with as many operands you want.)

Determining the solving order of an expression depends on surrounders and operators' precedence.
Precedence is set with relative values. To the exception of `0`, the lowest the |absolute value| of precedence, the highest the priority. Operators with a precedence of `1` or `-1` are the first to be evaluated when solving an expression. Positive values represent left-to-right associativity (e.g. operator `+` with precedence `3` : `a + b + c` = `((a + b) + c)`), while negative right-to-left (e.g. `^` and `-2` : `a ^ b ^ c` = `(a ^ (b ^ c))`). Null values are for special cases, like comparative operators (`=`, `==`, `<`, etc.). I'm not sure what to do with them for now.

## Try it yourself

Give the following string `(~a) + [(b) / c]` to the lexer, and check the token with the command `token`:

```bash
./idiomatik
|> (~a) + [(b) / c]
|> token
    [['SUR', '(', ['PARENTHESIS', 'open', 1], 0], \
    ['OP', '~', ['NOT', 'unary', 'R', 1], 1], \
    ['STR', 'a', ['variable', 1], 2], \
    ['SUR', ')', ['PARENTHESIS', 'close', 1], 3], \
    ['OP', '+', ['PLUS', 'binary', 'LR', 4], 4], \
    ['SUR', '[', ['BRAKET', 'open', 1], 5], \
    ['SUR', '(', ['PARENTHESIS', 'open', 2], 6], \
    ['STR', 'b', ['variable', 1], 7], \
    ['SUR', ')', ['PARENTHESIS', 'close', 2], 8], \
    ['OP', '/', ['DIV', 'binary', 'LR', 3], 9], \
    ['STR', 'c', ['variable', 1], 10], \
    ['SUR', ']', ['BRAKET', 'close', 1], 11]]
```
<!--
```
[PAR_open_1][OP_not][STR][PAR_close_1][OP_plus][BRA_open_1][PAR_open_2][STR][PAR_close_2][OP_div][STR][BRA_close_1]
```
-->

Tokens are hard to read for humans, but as `idiomatik` does not return an error, we can conclude this is a syntactically valid expression. This is because none of our axioms is refuted :

- `~a` is nested at level 1 in matching parenthesis
- `(b) / c` is nested at level 1 in matching brakets
- `b` is nested at level 2 in matching parenthesis
- `~` defined as right unary operator has a right operand `a`
- `+` defined as left-right binary operator has its left `(~a)` and right `[(b) / c]` operands
- `/` defined as left-right binary operator has its left `(b)` and right `c` operands

Let's now define an arbitrary rewrite rule, for example : `(_) --> _`, by feeding it to our program :

```bash
|> (_) --> _
|> add r
|> rules
    (R0)     ( _ ) --> _
```

`_` and `-->` are two *meta* symbols, meaning respectively _any string_ and _rewrite as_. This rewrite rule could be understood as "any string between parenthesis can be rewritten without it".
(Note that you can see which rules `idiomatik` will consider for rewrites with the command `rules`).

The rewriting process starts by parsing the token and check whether any sequence of its elements matches the left side of the rewrite rule (here `(_)`).
Note that the rewrite rule left side is tokenized too (in fact, rules are valid expressions that can be tokenized too). So we check if the input token contains a sequence matching the pattern `[PAR_open][STR][PAR_close]`.
As it is the case for `(b)`, our input `(~a) + [(b) / c]` can be rewritten as `(~a) + [b / c]` (which we can feed back to the lexer and the parser to check if it is a valid expression).

Now ask `idiomatik` to try to match our rule with our proposition and eventually rewrite it :

```bash
|> rewrite full
( ~ a ) + [ b / c ]  
```

That's it! `(b)` became `b`, and that's all we wanted to do in this example.
Now try adding rules and try them on different expressions.

### Meta characters

Note that `(~a)` is not rewritten in this example, because it does not match the pattern.
To unwrap it, we could consider a rule like `(~_) --> ~_`.
Adding a meta operator like `$`, symbolizing any couple operator-operand(s), could be helpful : `($) --> $`.
Other meta symbols are to be implemented (e.g. any surrounder, rules, etc.).

Upper case letters (`A`...`Z`) are the same as `_`, they represent *any string* but allow flexibility in the assignement of which variable in the left hand side of the rewrite rule (the pattern to match) corresponds to which variable in the right hand side. 
To illustrate this, consider a rule like : `A (B + C) --> A * B + B * C`.
When applied to the expression `2 ( 3 + 4 )` it will match `A` to `2`, `B` to `3` and `C` to `4`, ending in this rewrite : `2 * 3 + 2 * 4`.

### Troubles with rewrite rules

We have various choices when applying transformation rules to an expression. For example checking if the rewrited expression (here ` ( ~ a ) + [ b / c ] `) is also rewritable given our rules, or stopping.
This is not trivial when considering rules leading to never ending loops (e.g. `_ --> (_)`).
There is no optimal choice for now in `idiomatik` as it exhaustively recomputes every rewritings, given all rules (!) until nothing new can be rewritten (highly resource consuming and potentially never ending...), but I will add simpler behaviors (forbid infinite use of expanding rules?).

### Derivating

`idiomatik` can be used to derive *true* propositions from axioms and rewrite rules.
Here is an example with [Peano's definition of addition](https://en.wikipedia.org/wiki/Peano_axioms#Addition):

```bash
|> add rules
    > A + 0 --> 0
    > A + s(B) --> s(A + B)
    
|> a + 1 = a + s(0)
|> rewrite full
a + 1 = s ( a + 0 )
a + 1 = s ( 0 )
```

### More to come?

That's where `idiomatik` is for now.


# TODO

- For some commands (match, etc.) do not reset last_proposition
- Do not allow empty axioms
- Meta character for ANY_OPERAND
- Draw better trees
- Specify rules' names
- Undo command
- Save logs/transformation
- Display rules combined in full rewrites

# Resources

## Links

- https://en.wikipedia.org/wiki/Lexical_analysis
- https://stackoverflow.com/a/3614928
- https://en.wikipedia.org/wiki/Chomsky_hierarchy
- https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form
- https://yewtu.be/watch?v=F25ez8s3AsQ
- https://yewtu.be/watch?v=f9Mkzbxdjzc
- https://yewtu.be/watch?v=_C5AHaS1mOA
- https://en.wikipedia.org/wiki/Regular_expression
- https://en.wikipedia.org/wiki/Abstract_syntax_tree
- https://en.wikipedia.org/wiki/Order_of_operations
- https://plato.stanford.edu/entries/dynamic-epistemic/appendix-B-solutions.html#muddy
- https://yewtu.be/JO_0e9mPofY
- https://en.wikipedia.org/wiki/Computer_algebra_system

## Raw pasting

### Lexer/Tokenizer 

Classify lexemes (strings of symbols from the input).
The lexer scans the input and produces the matching tokens.
Lexers produce tokens, which are sentences of the regular language they recognize. Each token can have an inner syntax (though level 3, not level 2), but that doesn't matter for the output data and for the one which reads them.
"A lexer (or tokenizer) is generally combined with a parser, which together analyze the syntax of programming language [...]"

### Parser

Classify strings of token (from the input; sentences).
Analyze strings to "build" trees...
Parsers produce syntax trees, which are representations of sentences of the context-free language they recognize.

### Lexeme

String of symbols (from the input).

### Syntax

Structure of a language.
Syntax impacts semantics.

### Grammar

Helps to express the structure of a language formally.

### Semantic

Wrong syntax results in no meaning.
Correct syntax could result in a meaningless thing (Colorless green ideas sleep furiously)

### Terminal / Terminal symbol

Base tokens of a language.
Keywords, operators, other symbols...
The characters that can be used in identifiers, numbers or other program elements.

### Nonterminal / Nonterminal symbol

Used to represent pieces of the structure of the language.
(noun, verb, sentence, etc.)

### Productions / Production rule

Rules that make up the grammar.
Translate a nonterminal to a sequence of one or more nonterminals or terminals.
(e.g. : a sentence is a noun phrase followed by a verb phrase,
      : a verb phrase is a verb or a verb followed by a noun phrase,
      : a verb is one of a list of words (the terminals that can be used as verbs))

### Lexical vs Phrase Structure

Lexical structure : structure of a valid token

Phrase structure : larger structure of sentences and programs.

We usually separate grammars to handle these because grammars for both get very complex.

Compilers and interpreters usually handle these separately.
(For the moment that seems to be what I have naively done)

### Parse trees (concrete syntax tree or derivation tree)

Diagram of the structure of a language fragment, given a grammar.
It's a way to demonstrate how a fragment of a language is structured given a grammar.

A parse tree represents the syntactic structure of a language with nodes corresponding to the elements of that language (e.g. operators, strings...).
It is different from AST because details such as identifiers, characters, etc. are not abstracted away.
So parse trees usually contain all the informations about the input string being parsed and syntactically checked.

### Abstract syntax tree (AST)

Tree representation of the "abstract syntactic structure of text written in a formal language". 
Abstract because some informations aren't necessary (e.g. surrounders). 
An AST is usually derived and built from a parse tree (a "concrete syntax tree").

### Ambiguity

Multiple trees for a same expression.

Check associativity : for most it is left to right. Right to left (assignment (a=b) and exponentiation (2^4))

Check precedence : operators' priority

### Backus-Naur Form

It is a metasyntax notation for context-free grammars. A context-free grammar production rules' can be applied regardless of the context.
That might not be my case (for example if `$` represents `any operand`), but the notation is relatively straightforward to be humanly understandable.

`<Xxxxx>` : non terminal

`|` : alternative

* Example : 

```
<integer> ::= <digit> | <digit> <integer>
<float>   ::= <integer> . <integer>
```

Idiomatik in BNF notation (might be wrong)...
```
<Input> 	::= <Token>
<Token> 	::= <Proposition> | <Rule>
<Rule> 		::= <Axiom> | <Rewrite rule>
<Axiom>         ::= <Proposition>
<Rewrite rule> 	::= <Token> --> <Token>
<Proposition> 	::= <Symbol> | <Symbol> <Proposition>
<Symbol> 	::= <Str> | <Surr> | <Op> | <Meta> | <Number>
<Str> 		::= <char> | <char> <Str>
<Surr> 		::= ( | ) | [ | ] | { | }
<Op> 		::= + | ... | -->
<Meta> 		::= _ | $
<Number> 	::= <digit> | <digit> <Number>
<char> 		::= a | ... | Z
<digit> 	::= 0 | ... | 9
```

### EBNF (Extended Backus Naur Form)

Allow it to be a little more compact.

### Syntax diagram

Less compact.

### Left/Right recursive

In BNF notation `<exp> ::= <exp> <term> | <term>` is an example of left-recursion (so left associativity) because `... ::= <exp> <term> | ...` sees `<exp>` on the left side, meaning recursion will happen on the left side.
To the contrary `<exp> ::= <term> <exp> | <term>` would be right recursive, therefore right associative.
See [this video](https://piped.video/JO_0e9mPofY?t=1115).
