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

## What it does

### Lexing : from raw input to tokens

`idiomatik` receives input strings (e.g. `a + b = c`) that are returned as **tokens**.
A token is a chain of elements built from the input by the **lexer**.
The lexer decomposes the input into *atomistic* elements (characters, or sequences of characters) that correspond to predefined categories (strings, operators, surrounders, meta characters, etc.). (Those categories are defined in the `SYMBOLS` table.)
When all the elements of an input have been attributed an identity (to which category they belong, and eventually what are their properties), they are chained together and the construction of the token ends.

### Parsing : checking syntax

Tokens are then sent to the **parser** whose job is to assess **syntax** (i.e. is the chain of elements in the token a well-formed expression?).
The parser returns a truth value depending on the token being syntactically correct or not.

Syntax is immediately incorrect when one of those axioms is false :

- every closing surrounder (`)`, `]`, `}`) matches an opening opposite, at the same level of **nestedness** (opening a surrounder increments the level of nestedness by 1; closing decrements it)
- every **operator** has a correct amount of **operands** in proper position

If the token is syntactically valid, the input was a well-formed expression (whatever that could mean).

### Rewriting : transforming expressions

When an input is a well-formed expression, `idiomatik` can **rewrite** it as another valid expression.
This transformation depends on a set of **rewrite rules** that the user can arbitrarly define and send on-the-fly :

```bash
|> contraposition :: A => B --> ~B => ~A
INFO: imported rule 'contraposition :: A => B --> ~B => ~A'.

|> p => q

|> rewrite contraposition
~q => ~p
```

Rules can also be imported from files (see `rules/example`) with the `load` command) :

```bash
|> load ./rules/addition
INFO: imported rule 'add_commutativity :: A + B --> B + A'.
INFO: imported rule 'add_associativity :: A + (B + C) --> (A + B) + C'.
INFO: imported rule 'add_neutral :: A + 0 --> A'.
> Successfully imported rules in file 'rules/addition'.
```

Rewrite rules put aside, `idiomatik` is gonna be used to solve expressions (work in progress).
It is by default [PEMDAS](https://en.wikipedia.org/wiki/Order_of_operations#Mnemonics) compliant, solving propositions in the "correct" order, even when parenthesis are missing. 
This is by default but it is configurable thanks to a precedence value given to operators in the `SYMBOLS` table.
If some special cases are not consensual when considering the "correct solving order" (e.g. [serial exponentiation](https://en.wikipedia.org/wiki/Order_of_operations#Special_cases)), `idiomatik` allows users to set the associative direction of operators as we stated above. In the `SYMBOLS` table negative priority values give right-to-left associativity, positive left-to-right, while null oppose their operands by "splitting" expressions. 

This process of desambiguation is also of interest to draw trees.

### Visualizing : drawing trees

`idiomatik` can draw basic trees (really basic trees) representing any given expression with `tree` or `draw`:

```bash
|> a + b * c / d

|> draw
0 |  +
1 | a    /
2 |    *  d
3 |   b c
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

Tokens are not simple to read for humans but as `idiomatik` returns no error, this is definitely a syntactically valid expression (just keep in mind that this depends on how symbols are defined in `SYMBOLS`!). To check it ourself, let's observe that no syntax axiom is refuted :

- `~a` is nested at level 1 in matching parenthesis
- `(b) / c` is nested at level 1 in matching brakets
- `b` is nested at level 2 in matching parenthesis
- `~` defined as right unary operator has a right operand `a`
- `+` defined as left-right binary operator has its left `(~a)` and right `[(b) / c]` operands
- `/` defined as left-right binary operator has its left `(b)` and right `c` operands

Let's now define an arbitrary rewrite rule, for example : `(_) --> _`, by feeding it to our program :

```bash
|> unparenthesize :: (_) --> _
INFO: imported rule 'unparenthesize :: (_) --> _'.

|> rules
    (R0 :: unparenthesize)     ( _ ) --> _
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

### Matches

The `rewrite full` command is not always what we need to get fine control.
Use `match <rule index>` or `match <rule name>` to check if the current proposition can be rewritten by a specific rule.
If multiples matches are possible, index are displayed on the left.
Use `rewrite <rule index> <match index>` (or `rewrite <rule name> <match index>`) to transform the current proposition to the desired one.

```bash
|> match R0
0 | ( ~ a ) + [ ( b ) / c ]     (R0 :: unparenthesize)   :: ( ~ a ) + [ b / c ]

|> rewrite R0 0
( ~ a ) + [ b / c ]  
```

### Meta characters

Note that in the example above, `(~a)` is not unparenthesized.
It does not match the pattern `(_)` because of the operator `~`.
To unwrap it, we could consider a rule like `(~_) --> ~_`, or maybe better `(¤_ $) --> ¤_ $`.
`$` symbolizes *any operand*, while `¤_` means *any right unary operator*. 
Other meta symbols are to be implemented (e.g. any surrounder, rules, etc.).

Upper case letters (`A`...`Z`) are the same as `_`, they represent *any string* but allow flexibility in the assignement of which variable in the left hand side of the rewrite rule (the pattern to match) corresponds to which variable in the right hand side. 
To illustrate this, consider a rule like : `A (B + C) --> A * B + B * C`.
When applied to the expression `2 ( 3 + 4 )` it will match `A` to `2`, `B` to `3` and `C` to `4`, ending in this rewrite : `2 * 3 + 2 * 4`.

Here is a quick summary of current meta characters in `idiomatik`:

| Symbol    | Meaning                                                  |
|-----------|----------------------------------------------------------|
|   `_`     | Any string                                               |
|   `_1`    | Any *identified* string (same as `_2`, `_3`..., `_10`)   |
|   `A`     | Any *identified* string (same as `B`, `C`..., `Z`)       |
|   `$`     | Any operand                                              |
|   `$1`    | Any *identified* operand (same as `$2`, `$3`..., `$10`)  |
|   `¤`     | Any left-right (binary) operator                         |
|   `_¤`    | Any right (unary) operator                               |
|   `¤_`    | Any left (unary) operator                                |

### Troubles with rewrite rules

We have various choices when applying transformation rules to an expression.
For example, we may want to check again if the rewrited expression is itself rewritable given our rules.
We may also want to stop after just one transformation.
This reflexion is not trivial when considering rules leading to never ending loops (e.g. `_ --> (_)`).

The `rewrite full` command apply all combinations of all rules (!) to an input and all its transformations (!!).
But `idiomatik` as a recursive limit of 50 calls to that command.
The `rewrite <rule> <match index>` command is safer.

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

- (!!) Allow saving a succession of steps and use it as a new transformation rule
- (!!) Allow chaining multiple transformation rules
- (!) Use silent surrounders when transforming some expressions, then delete those surrounders (useful for unary operators exp?).
- Check if rule already exists before importing
- Better handling of "last_proposition"
- Draw better trees
- Transform tree to its linear form (to check if two trees are equals)
- Undo command
- Save logs/transformations
- Improve rewrite system

# Doing

- Meta character for ANY_OPERAND (to check)

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
- https://github.com/tsoding/Noq

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
<Rewrite rule> 	::= <Proposition> --> <Proposition>
<Proposition> 	::= <Symbol> | <Symbol> <Proposition>
<Symbol> 	::= <Str> | <Surr> | <Op> | <Meta>
<Str> 		::= <char> | <char> <Str>
<Surr> 		::= ( | ) | [ | ] | { | }
<Op> 		::= + | ... | -->
<Meta> 		::= _ | $ | ¤ | ...
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


## Why?

I initially wanted to write a solving algorithm for the [Muddy Children Puzzle](https://en.wikipedia.org/wiki/Induction_puzzles#Muddy_Children_Puzzle). That led me to some questions about public/private knowledge, inference rules, well-formed formulas and other stuff I had never heard of, seriously thought of, or invested time in. How to implement lexemes identification, evaluate syntax, do model checking, ...? 
Topics or concepts derivating from these questions are covered in the resources section.

So, I'm not reinventing the wheel, and this will be far from original or quality work. Just disorganized trials and errors, and random notes and code.
A lot of things here could be wrong or bad approximations, reflecting my ignorance in CS in general.
But why not share a "work" in progress?

Thanks to [tsoding](https://twitch.tv/tsoding) for the great source of inspiration and stimulation.
