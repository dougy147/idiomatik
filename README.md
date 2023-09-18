Building my first interpreter with Python. A bit idiotic, partially automatic, fully idiomatic.


| NOTE        |
|:---------------------------|
| _This is rather a practice-oriented than a theoretically-driven learning project. The README is verbose for a simple reason : if I need to come back here after a long time, I don't want to lose too much boot time diving back in. Also, I don't have the vocabulary to be synthetic enough. I hope to keep the code clean and self-explanatory._ |

## Quick launch

```bash
git clone https://github.com/dougy147/idiomatik
cd idiomatik
./idiomatik "a + b = c"
```

## Why?

I was initially writing a simple solving algorithm for the [Muddy Children Puzzle](https://en.wikipedia.org/wiki/Induction_puzzles#Muddy_Children_Puzzle). That led me to some questions about public/private knowledge, inference rules, well-formed formulas and other stuff I had never heard of, seriously thought of, or invested time in. What are those things? how to implement lexemes identification or evaluate syntax? why is model checking so hard?... those are things I'm interested in for now... until the fail ! lol.

So, I'm not reinventing the wheel, and this will be far from original or quality work. Just disorganized trials and errors, and random notes and code.
A lot of things here could be wrong or bad approximations, reflecting my ignorance in CS in general.
But why not share a "work" in progress?

## What it does

`idiomatik` receives input strings (e.g. "A + B = C") that are returned as *tokens*.
A token is a chain of elements extracted from the input by the *lexer*.
The lexer decomposes each input to match its elements (characters, or sequence of characters) to predefined categories of symbols (see `SYMBOL_TABLE`).
When all the elements of an input have been attributed an identity, they are chained together and the construction of the token ends.

Tokens are then sent to the *parser*, whose job is to assess if their *syntax* is valid (i.e. the chain of elements is a well-formed expression) or not.
The parser returns a truth value depending on whether the token is syntactically correct or not.

Syntax is immediately incorrect when one of those axioms is false :

- every closing surrounder (`)`, `]`, `}`) matches an opening opposite at the same level of *nestedness* (an opening surrounder increments the level of nestedness by 1)
- every *operator* has a correct amount of *operands* in proper position

If the token is syntactically valid, then the input is considered to be too.

When an input is a valid expression, `idiomatik` can *rewrite* it as another valid expression given a set of arbitrarly predefined rules (i.e. *rewrite rules*; see `RULES`).
(But for now, this is only true for simple rules. See example below)

For the sake of brevity, I'm not mentionning how `SYMBOLS` and `RULES` tables' are parsed with `idiomatik`, but they are in a quite flexible way.
I also pass for now on how _n_-arity checking for operators is implemented.

### Verbose example...

Giving the following string `(~a) + [(b) / c]` to the lexer will roughly return the following token (_identifiers and nestedness only in this example_) :

```
[PAR_open_1][OP_not][STR][PAR_close_1][OP_plus][BRA_open_1][PAR_open_2][STR][PAR_close_2][OP_div][STR][BRA_close_1]
```

This is a syntactically valid expression as no axiom is refuted :

- `~a` is nested at level 1 in matching parenthesis
- `(b) / c` is nested at level 1 in matching brakets
- `b` is nested at level 2 in matching parenthesis
- `~` defined as right unary operator has a right operand `a`
- `+` defined as left-right binary operator has its left `(~a)` and right `[(b) / c]` operands
- `/` defined as left-right binary operator has its left `(b)` and right `c` operands

Let's now try to define an arbitrary rewrite rule, for example : `(_) --> _`

If we define `_` and `-->` as two *meta* symbols meaning respectively _any string_ and _rewrite as_, the rewrite rule could be understood as "any string between parenthesis can be rewritten without it".


The rewriting process starts by parsing the token and check whether any sequence of its elements matches the left side of the rewrite rule (here `(_)`).
Note that the rewrite rule left side is tokenized too (in fact, rules are valid expressions that can be tokenized too). So we check if the input token contains a sequence matching the pattern `[PAR_open][STR][PAR_close]`.
As it is the case for `(b)`, our input `(~a) + [(b) / c]` can be rewritten as `(~a) + [b / c]` (which we can feed back to the lexer to check if it is a valid expression).

Here is the output of `idiomatik` with this example's input and rule:

```bash
./idiomatik "(~a) + [(b) / c]"

Rewrites as:

( ~ a ) + [ b / c ]  # given the rule ( _ ) --> _
```

Now we have different choices, either we check if the rewrited expression (here ` ( ~ a ) + [ b / c ] `) is also rewritable given the rewrite rules, either we stop.
This question maybe makes more sense when considering rules like this one : `_ --> (_)`. Indeed, that could lead to never ending loops...

For now `idiomatik` exhaustively recomputes every rewritings, given all rules (!) until nothing new can be rewritten (highly resource consuming and potentially never ending...), but I will add simpler behaviors.

Also note that `(~a)` will not be rewritten in this example, because it does not match the pattern.
To unwrap it, we could consider a rule like `(~_) --> ~_`.
However, that could also lead to problems when we will consider solving expressions starting by the most nested sub-expressions. Indeed, we shouldn't unwrap an expression before solving what is inside (that obviously depends on the property we want for the language we build...).
Adding a META operator like `$`, meaning `ANY_OPERAND`, could be helpful.

Rewrite rules put aside, `idiomatik` is by default [PEMDAS](https://en.wikipedia.org/wiki/Order_of_operations#Mnemonics) compliant, solving propositions in the "correct" order, even when parenthesis are missing. This is by default but it is configurable thanks to a priority value given to operators in the `SYMBOL_TABLE`. Some special cases are not consensual when considering the "correct solving order" (e.g. [serial exponentiation](https://en.wikipedia.org/wiki/Order_of_operations#Special_cases)), so choices are to be made, potentially compromising full control. `idiomatik` allows users to chose the direction in which operators are going to be evaluated when solving an expression : in the `SYMBOL_TABLE` negative priority values goes from rigth to left, positive from left to right, while null separates an expression side by side. 

This process of desambiguation is of course of interest to solve expressions, but also to draw trees (a goal of a near future).

That's where `idiomatik` is for now.


# Useful resources

## Vocabulary

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
<Proposition> 	::= <Symbol> | <Proposition> <Symbol>
<Symbol> 	::= <Str> | <Surr> | <Op> | <Meta> | <Number>
<Str> 		::= <char> | <Str> <char>
<Surr> 		::= ( | ) | [ | ] | { | }
<Op> 		::= + | ... | -->
<Meta> 		::= _ | $
<Number> 	::= <digit> | <Number> <digit>
<char> 		::= a | ... | Z
<digit> 	::= 0 | ... | 9
```

### EBNF (Extended Backus Naur Form)

Allow it to be a little more compact.

### Syntax diagram

Less compact.



# Future features

- Allow on-the-fly inputs (interpreted as axioms or rewrite rules)
- Propose rewritings when asked by user (e.g. `:rewrite`)
- Draw trees (on the right track to it)

# TODO

- Implement a tweakable system of precedence for operators. Equality operators (e.g. `=`) should have the complete left part of an expression as first operand (except when there are multiple equal signs) and the complete right part as the second.
- For each rewrite rule, if left and right side are equal, consider it a tautology and ignore (?).




# Resources

- https://en.wikipedia.org/wiki/Lexical_analysis
- https://stackoverflow.com/a/3614928
- https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form
- https://piped.video/watch?v=F25ez8s3AsQ
- https://piped.video/watch?v=f9Mkzbxdjzc
- https://piped.video/watch?v=_C5AHaS1mOA
- https://en.wikipedia.org/wiki/Regular_expression
- https://en.wikipedia.org/wiki/Abstract_syntax_tree
- https://en.wikipedia.org/wiki/Order_of_operations
