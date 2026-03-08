#! /usr/bin/python
import sys
import repl, interpreter, parser
import os

# Allow calling files without typing the .sa suffix.
def resolve_filename(filename):
    if os.path.exists(filename):
        return filename

    if not filename.endswith('.sa'):
        candidate = filename + '.sa'
        if os.path.exists(candidate):
            return candidate

    return filename

def compile_file(filename):
    filename = resolve_filename(filename)
    fd = os.open(filename,os.O_RDONLY,0o777)
    contents = ''
    while True:
        buf = os.read(fd, 16)
        if not buf:
            # we're done
            break
        contents += buf.decode()
    
    itpr = interpreter.Interpreter()
    contents = contents
    return itpr.compile_interpret(parser.parse(contents)).to_string()


def begin(args):
    if len(args) == 1:
        print(args[0])
        print(compile_file(args[0]))
        
    elif len(args) == 0:
        repl.main()
    else:
        print("I don't understand these arguments")


if __name__ == '__main__':
    
    begin(sys.argv[1:])
