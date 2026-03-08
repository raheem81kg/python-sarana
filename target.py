import lexer, parser, interpreter, repl, sarana

def entry_point(argv):
    sarana.begin(argv[1:])
    return 0

def target(*args):
    return entry_point, None
