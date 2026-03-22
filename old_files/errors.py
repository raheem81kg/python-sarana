

class LogicError(Exception):
    # Base class for logic violations detected during parsing or interpretation.
    
    def __str__(self):
        return self.message


class UnexpectedEndError(Exception):
    # Raised when the parser reaches input end before completing a statement.
    
    message = 'Unexpected end of statement'
    
    def __str__(self):
        return "Unexpected end of statement"


class UnexpectedTokenError(Exception):
    # Raised when the parser encounters a token that does not fit the grammar.

    def __init__(self, token):
        self.token = token

    def __str__(self):
        return self.token


class ImmutableError(Exception):
    # Raised when attempting to reassign an immutable binding.
    
    message = 'Cannot assign to immutable variable %s'

    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return self.message % self.name
