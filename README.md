# python-sarana

Repository: `git@github.com:raheem81kg/python-sarana.git`

**Learning to build a language interpreter on plain Python with PLY**

The code uses standard Python and PLY for lexing/parsing.

## Installing

`pip install -r requirements.txt`

## Running

`python sarana.py` for REPL, `python sarana.py [filename].sa` for interpreting a file

`:a` gives you the AST of the last statement, `:e` to list environment variables, `:q` or Ctrl-C to quit. The REPL now supports multi-line input too — it'll just keep appending code and trying to interpret it until it's valid (eg. you closed the block or whatever), or you break it ;)

## Status

Basic arithmetic, floats, integers, booleans, and strings, variable assignment, if expressions, and a display() function.

```
>>> 5 == 5
= true
>>> 5 != 5
= false
>>> let a = 5
= 5
>>> display(a)
5
>>> display(a + 25)
30
>>> "hi" + 'hi'
= hihi
>>> "hi" * 5 - 1
= hihihihih

# if expressions
>>> if false: display("no") else: display("yes") end
yes
>>> let a = (if true: 1 else: 5 end)
= 1

let a = 50
if a == 50 and true:
  display("doing stuff")
else:
  display("not this though")
end

>>> 5 >= 6
= false

# assignment via if
>>> let a = if true: 5 end
= 5
>>> :a
Program(BinaryOp(Variable('a'), If(Boolean(True))Then(Integer(5))Else(None)))

# arrays
>>> [5, 6, ["hi", 7.0]]
= [5, 6, [hi, 7.0]]

# functions
func a(b):
 b + 1
end

>>> b(1)
= 2

# immutability means loops become recursion
func p_message(msg, n):
  if n > 0:
    display(msg)
    p_message(msg, n - 1)
  end
end

>>> p_message("hellooo",2)
hellooo
hellooo

# functions can be passed around
func a():
  1
end

>>> let b = a
>>> b()
= 1
```

## Compiling

You will need pypy so you can use RPython's compiler. Then, like so:

`python path/to/rpython/bin/rpython target.py`

This will provide a `target-c` binary which you can use as a compiled substitute for `main.py`.

## Goals

A language which can do things I find interesting, and the tools necessary to execute it.

- [x] Define the language (ongoing)
- [x] Lexer
- [x] Parser
- [x] Bytecode compiler
- [x] Interpreter/VM
- [x] Compiles to RPython (mostly but sometimes broken)
- [ ] JIT
- [x] Immutability (initial support anyway)
- [x] First-class functions (sort of)
- [ ] Structs and traits
- [ ] FP concepts like map/reduce
- [ ] Pattern matching
- [ ] Concurrency via message passing
- [ ] Standard library
