# Documentation

## Basics

Currently, rickroll supports the following data types.

| Data Type   | Stores                                                        |
|-------------|:-------------------------------------------------------------:|
| INT         | an arbitrary precision integer                                |
| FLOAT       | an arbitrary precision floating point                         |
| BOOL        | TRUE or FALSE                                                 | 
| CHAR        | a character                                                   | 
| ARRAY       | a list of data types (ARRAY is a constant for an empty array) | 

Operators can be used to perform operations on data types. The following operators are supported and evaluated in order.

| Operator | Action                                                      | Precedence    |
|----------|:-----------------------------------------------------------:|:-------------:|
| -        |  unary minus                                                | 0             |
| :        |  array access                                               | 1             |
| !        |  boolean not                                                | 2             |
| *        |  multiplication                                             | 3             |
| /        |  division (integer division if both arguments are integers) | 3             |
| %        |  modulo                                                     | 3             |
| +        |  addition                                                   | 4             |
| -        |  subtraction                                                | 4             |
| >        |  greater than                                               | 5             |
| <        |  less than                                                  | 5             |
| >=       |  greater than or equals                                     | 5             |
| <=       |  less than or equals                                        | 5             |
| ==       |  equals                                                     | 5             |
| !=       |  not equals                                                 | 5             |
| &&       |  boolean AND                                                | 6             |
| \|\|     |  boolean OR                                                 | 6             |

Expressions are formed by combining data types and operators. Expressions may also contain parenthesis for evaluation priority. For example, ```3 + 4 * (6 % 3) > 1``` is a valid expression. It returns ```TRUE```.

A statement is a line in the program. Following are some basic statements.

## Printing to stdout

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

## Variables

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

## Casting

Variables may be casted from one type to the other. To cast variables, use the syntax ```Never gonna make VAR TYPE```, where ```VAR``` is the name of the variable and ```TYPE``` is the type to cast to, one of the data types listed in the table above.

```
Never gonna let a down
Never gonna give 2 + 5 * 1
Never gonna make a FLOAT
Never gonna say a
```

```
7.0
```

## While Loops and If Statements

Both while loops and if statements start with a statement that checks the value of a boolean. If the value is FALSE, the interpreter skips to the end of the statement. If the value provided is not a boolean, the interpreter will try to cast it to a boolean.

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
0
-2
-4
```

```
Inside we both know TRUE
  Never gonna let a down
  Never gonna give a 5
Your heart's been aching but you're too shy to say it
Never gonna say a
```

```
Runtime Error: Variable a not found
```

## Functions

In rickroll, there are "blocks" of code that do different things. Currently, the three different block types are ```[Intro]```, ```[Chorus]```, and ```[Verse]```.

The ```[Intro]``` block indicates that its code should be interpreted in the global context. This means that all variables declared in ```[Intro]``` are global variables. If included, this block must be located before all other blocks.

```
[Intro]
Never gonna let a down
```

The ```[Chorus]``` block is the equivalent of a main function. Its code is interpreted in a separate context that extends the global context. This means that ```[Chorus]``` can see ```[Intro]``` but ```[Intro]``` cannot see ```[Chorus]```

```
[Intro]
Never gonna let a down
Never gonna give a 1.0

[Chorus]
Never gonna say a
```

```
1.0
```

The ```[Verse]``` block is the equivalent of a function or method. Its code is not immediately ran when the interpreter encounters it. It is only ran when it is called by another block. There are special statements that make up a function.

A function declaration starts with ```[Verse NAME]```, where ```NAME``` follows the same conventions as a variable name. A name may be shared between a variable and function. A function has a context that extends the global context. Although ```[Verse]``` blocks may be declared anywhere, only blocks declared before ```[Chorus]``` may be used inside of it.

Following that is the arguments statement, which has syntax ```(Ooh give you ARG1 ARG2 ... ARGN)```, where ```ARG1 ARG2 ... ARGN``` are the names of the arguments of the function (not the types). To indicate that a function has no argument, make ```ARG1``` 'up'.

```
[Verse do_nothing]
(Ooh give you up)
```

Following that may be any amount of code which make up the function. A special statement in the function is the return statement, which returns a value to the caller. The syntax for that is ```(Ooh) Never gonna give, never gonna give (give you EXPR)```, where ```EXPR``` is the expression whose value to return.

```
[Verse add]
(Ooh give you a b)
(Ooh) Never gonna give, never gonna give (give you a + b)
```

To call a function, use the call and call value statements.

To call a function without using its return value, use the call statement with syntax ```Never gonna run FUNC and desert ARG1, ARG2, ..., ARGN```, where ```FUNC``` is the name of the function and ```ARG1, ARG2, ..., ARGN``` are the arguments seprated by ','. To call a function with no arguments, make ```ARG1``` 'you'.

To call a function and use its return value, add ```(Ooh give you NAME)``` before the call statement (where ```NAME``` is the name of the variable the value is assigned to). This is a call value statement.

```
[Verse say_something]
(Ooh give you text)
Never gonna say text

[Chorus]
Never gonna run say_something and desert 123
```

```
123
```

```
[Verse fib]
(Ooh give you i)
Inside we both know i <= 1
  (Ooh) Never gonna give, never gonna give (give you i)
Your heart's been aching but you're too shy to say it
Never gonna let first down
Never gonna let second down
(Ooh give you first) Never gonna run fib and desert i - 1
(Ooh give you second) Never gonna run fib and desert i -2
(Ooh) Never gonna give, never gonna give (give you first + second)

[Chorus]
Never gonna let i down
Never gonna give i 10
(Ooh give you i) Never gonna run fib and desert i
Never gonna say i
```

```
55
```

Rickroll has several built-in functions callable in the same way as regular functions are called.

## Arrayof Function
The arrayof function, callable by ```_arrayof```, takes any number of arguments and makes an array out of them.

```
Never gonna let arr down
(Ooh give you arr) Never gonna run _arrayof and desert 1, TRUE, 3 - 4, 7
Never gonna say arr
```

```
[1, TRUE, -1, 7]
```

## Pop Function

The pop function, callable by ```_pop```, pops the element at a specified index from an array. It takes in two parameters, an array and an index (0-indexed).

```
Never gonna let arr down
(Ooh give you arr) Never gonna run _arrayof and desert 1, TRUE, 3 - 4, 7
(Ooh give you arr) Never gonna run _pop and desert arr, 0
Never gonna say arr

```

```
[TRUE, -1, 7]
```

## Push Function

The push function, callable by ```_push```, pushes an element on the end of the array. It takes two parameters, an array and an element.

```
Never gonna let arr down
(Ooh give you arr) Never gonna run _arrayof and desert 1, TRUE, 3 - 4, 7
(Ooh give you arr) Never gonna run _push and desert arr, UNDEFINED
Never gonna say arr
```

```
[1, TRUE, -1, 7, UNDEFINED]
```

## Replace Function

The replace function, callable by ```_replace```, replaces the element at the index of the array. It takes three parameters, an array, an index, and an element.

```
Never gonna let arr down
(Ooh give you arr) Never gonna run _arrayof and desert 1, TRUE, 3 - 4, 7
(Ooh give you arr) Never gonna run _replace and desert arr, 2, FALSE
Never gonna say arr
```

```
[1, FALSE, -1, 7]
```

## Subarray Function

The subarray function, callable by ```_subarr```, takes the subarray of the array between the given indexes, start and end (start inclusive and end exclusive).

```
Never gonna let arr down
(Ooh give you arr) Never gonna run _arrayof and desert 0, 1, 2, 3
(Ooh give you arr) Never gonna run _subarr and desert arr, 1, 2
Never gonna say arr
```

```
[1, 2]
```

## Getlength Function

The getlength function, callable by ```_getlength```, takes an array as its argument and returns an INT, the length of the array.

```
Never gonna let arr down
Never gonna let length down
(Ooh give you arr) Never gonna run _arrayof and desert 0, 1, 2, 3
(Ooh give you length) Never gonna run _getlength and desert arr
Never gonna say arr
```

```
4
```

## Putchar Function

The putchar function, callable by ```_putchar```, puts one character into stdout. It takes the character as the argument. The backslash character is used as an escape character.

```
Never gonna run putchar and desert 'L'
Never gonna run putchar and desert '\n'
```

```
L
```

## Input Function

The input function, callable by ```_input```, returns an array of characters, one stdin line. It awaits the input before returning and takes no arguments.

```
Never gonna let arr down
(Ooh give you arr) Never gonna run _input and desert you
Never gonna say arr
```

```
stdin: Hello!
```

```
[H, e, l, l, o, !]
```