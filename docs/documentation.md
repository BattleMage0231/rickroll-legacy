# Documentation

## Basics

Currently, rickroll supports the following data types.

| Data Type   |      Stores      |
|----------|:-------------:|
| INT |  an arbitrary precision integer|
| FLOAT |    an arbitrary precision floating point   |
| BOOL | TRUE or FALSE | 
| CHAR | a character | 
| ARRAY | a list of data types | 

Operators can be used to perform operations on data types. The following operators are supported and evaluated in order.

| Operator   |      Action      |  Precedence |
|----------|:-------------:|:-------------:|
| - |  unary minus | 0 |
| : |  array access | 1 |
| ! |  boolean not | 2 |
| * |  multiplication |  3 |
| / |  division (integer division if both arguments are integers) |  3 |
| % |  modulo |  3 |
| + |  addition |  4 |
| - |  subtraction |  4 |
| > |  greater than|  5 |
| < |  less than |  5 |
| >= |  greater than or equals |  5 |
| <= |  less than or equals |  5 |
| == |  equals |  5 |
| != |  not equals |  5 |
| && |  boolean AND |  6 |
| \|\| |  boolean OR |  6 |

Expressions are formed by combining data types and operators. Expressions may also contain parenthesis for evaluation priority. For example, ```3 + 4 * (6 % 3) > 1``` is a valid expression. It returns ```TRUE```.

A statement is a line in the program. Following are some basic statements.

### Printing to stdout

A print statement writes to stdout the result of evaluating its argument ended by a newline. If its argument is exactly ```goodbye```, it will exit the program.

Its syntax is ```Never gonna say ARG```.

```
Never gonna say 1 + 2
Never gonna say TRUE || FALSE
```

```
3
TRUE
```

### Variables

Rickroll is a weakly and dynamically typed language. This means that variable types are inferred at runtime and variables may be assigned a value of a different type.

To declare a variable, the syntax is ```Never gonna let VAR down```, where ```VAR``` can only have letters and underscores.

The initial value of a variable is UNDEFINED, a special data type.

```
Never gonna let a down
Never gonna let b down
Never gonna say a
```

```
UNDEFINED
```

To assign value to variables, the syntax is ```Never gonna give VAR EXPR```, where ```VAR``` is the variable name and ```EXPR``` is the expression.

```
Never gonna let a down
Never gonna let b down
Never gonna give a 3 + 4
Never gonna give b a < 3
Never gonna say a
Never gonna say b
```

```
7
FALSE
```

### While Loops and If Statements

Both while loops and if statements start with a statement that checks the value of a boolean. If the value is FALSE, the interpreter skips to the end of the statement.

The syntax to check the boolean is ```Inside we both know EXPR```, where ```EXPR``` is an expression returning a boolean.

A while loop terminates with the statement ```We know the game and we're gonna play it``` where as an if statement terminates with ```Your heart's been aching but you're too shy to say it```. A while loop executes as long as the expression is true where as an if statement only executes once.

Inside a while loop of if statement, local variables may be declared. These variables will not be in the scope of the entire block.

```
Never gonna let a down
Never gonna let b down
Never gonna give a 0
Never gonna give b 5
Inside we both know a < b
  Inside we both know a % 2 == 0
    Never gonna say -a
  Your heart's been aching but you're too shy to say it
  Never gonna give a a + 1
We know the game and we're gonna play it
```

```
