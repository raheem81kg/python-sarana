from errors import *

class BaseBox(object):
    pass

def compute_hash(value):
    return hash(value)

def r_dict(eq, hash_fn):
    del eq, hash_fn
    return {}

def dict_eq(key, other):
    return key._eq(other)

def dict_hash(key):
    return key._hash()

class Null(BaseBox):
    def to_string(self):
        return "<null>"

    def dump(self):
        return "<null>"


class Function(BaseBox):
    def __init__(self, name, code):
        self.name = name
        self.code = code

    def to_string(self):
        return "<function %s>" % self.name

    def dump(self):
        return "<function %s>" % self.name

    def add(self, right):
        raise Exception("Cannot add that to function %s" % self.name)


class ExternalFunction(BaseBox):
    def __init__(self, name, fn, args):
        self.name = name
        self.fn = fn
        self.args = args

    def to_string(self):
        return "<function %s>" % self.name

    def dump(self):
        return "<function %s>" % self.name

    def add(self, right):
        raise Exception("Cannot add that to function %s" % self.name)


class Array(BaseBox):
    def __init__(self, args):
        self.values = args

    def dump(self):
        return self.to_string()

    def push(self, statement):
        self.values.insert(0, statement)

    def append(self, statement):
        self.values.append(statement)

    def index(self, right):
        if isinstance(right, Integer):
            return self.values[right.value]
        raise LogicError("Cannot index with that value")

    def add(self, right):
        if isinstance(right, Array):
            return Array(list(self.values) + list(right.values))
        raise LogicError("Cannot add that to array")

    def sub(self, right):
        if isinstance(right, Integer):
            result = list(self.values)
            del result[right.intvalue]
            return Array(result)
        raise LogicError("Cannot remove that index from array")

    def to_string(self):
        return "[%s]" % ", ".join(value.to_string() for value in self.values)


class Dict(BaseBox):
    def __init__(self, args):
        self.values = args

    def dump(self):
        return self.to_string()

    def update(self, key, val):
        self.values[key] = val

    def index(self, right):
        if isinstance(right, (Integer, String, Float, Boolean)):
            return self.values[right]
        raise LogicError("Cannot index with that value")

    def add(self, right):
        if isinstance(right, Dict):
            result = dict(self.values)
            result.update(right.values)
            return Dict(result)
        raise LogicError("Cannot add that to dict")

    def sub(self, right):
        result = dict(self.values)
        del result[right]
        return Dict(result)

    def to_string(self):
        return "{%s}" % ", ".join(
            "%s: %s" % (key.to_string(), value.to_string())
            for key, value in self.values.items()
        )


class Boolean(BaseBox):
    def __init__(self, value):
        self.boolvalue = bool(value)

    @property
    def value(self):
        return bool(self.boolvalue)

    @value.setter
    def value(self, new_value):
        self.boolvalue = bool(new_value)

    def __hash__(self):
        return compute_hash(self.boolvalue)

    def __eq__(self, other):
        return isinstance(other, Boolean) and self.boolvalue == other.boolvalue

    def _hash(self):
        return compute_hash(self.boolvalue)

    def _eq(self, other):
        return isinstance(other, Boolean) and self.boolvalue == other.boolvalue

    def equals(self, right):
        if isinstance(right, Boolean):
            return Boolean(self.value == right.value)
        if isinstance(right, Integer):
            return Boolean(self.to_int() == right.value)
        if isinstance(right, Float):
            return Boolean(self.to_int() == right.value)
        return Boolean(False)

    def lte(self, right):
        if isinstance(right, Boolean):
            return Boolean(self.value == right.value)
        raise LogicError("Cannot compare that to boolean")

    def lt(self, right):
        raise LogicError("Cannot compare boolean that way")

    def gt(self, right):
        raise LogicError("Cannot compare boolean that way")

    def gte(self, right):
        if isinstance(right, Boolean):
            return Boolean(self.value == right.value)
        raise LogicError("Cannot compare that to boolean")

    def add(self, right):
        raise LogicError("Cannot add that to boolean")

    def sub(self, right):
        raise LogicError("Cannot sub that from boolean")

    def mul(self, right):
        raise LogicError("Cannot mul that to boolean")

    def div(self, right):
        raise LogicError("Cannot div that from boolean")

    def to_string(self):
        return "true" if self.value else "false"

    def to_int(self):
        return 1 if self.value else 0

    def dump(self):
        return self.to_string()


class Integer(BaseBox):
    def __init__(self, value):
        self.intvalue = int(value)

    @property
    def value(self):
        return int(self.intvalue)

    def __hash__(self):
        return compute_hash(self.intvalue)

    def __eq__(self, other):
        return isinstance(other, Integer) and self.intvalue == other.intvalue

    def _hash(self):
        return compute_hash(self.intvalue)

    def _eq(self, other):
        return isinstance(other, Integer) and self.intvalue == other.intvalue

    def to_string(self):
        return str(self.value)

    def dump(self):
        return str(self.value)

    def equals(self, right):
        if isinstance(right, Float):
            return Boolean(float(self.value) == right.value)
        if isinstance(right, Integer):
            return Boolean(self.value == right.value)
        if isinstance(right, Boolean):
            return Boolean(self.value == right.to_int())
        raise LogicError("Cannot compare that to integer")

    def lte(self, right):
        if isinstance(right, Integer):
            return Boolean(self.value <= right.value)
        if isinstance(right, Float):
            return Boolean(float(self.value) <= right.value)
        raise LogicError("Cannot compare that to integer")

    def lt(self, right):
        if isinstance(right, Integer):
            return Boolean(self.value < right.value)
        if isinstance(right, Float):
            return Boolean(float(self.value) < right.value)
        raise LogicError("Cannot compare integer that way")

    def gt(self, right):
        if isinstance(right, Integer):
            return Boolean(self.value > right.value)
        if isinstance(right, Float):
            return Boolean(float(self.value) > right.value)
        raise LogicError("Cannot compare integer that way")

    def gte(self, right):
        if isinstance(right, Integer):
            return Boolean(self.value >= right.value)
        if isinstance(right, Float):
            return Boolean(float(self.value) >= right.value)
        raise LogicError("Cannot compare integer that way")

    def add(self, right):
        if isinstance(right, Integer):
            return Integer(self.value + right.value)
        if isinstance(right, Float):
            return Float(float(self.value) + right.value)
        raise LogicError("Cannot add %s to integer" % str(right.__class__.__name__))

    def sub(self, right):
        if isinstance(right, Integer):
            return Integer(self.value - right.value)
        if isinstance(right, Float):
            return Float(float(self.value) - right.value)
        raise LogicError("Cannot sub from int")

    def mul(self, right):
        if isinstance(right, Integer):
            return Integer(self.value * right.value)
        if isinstance(right, Float):
            return Float(float(self.value) * right.value)
        raise LogicError("Cannot mul that to int")

    def div(self, right):
        if isinstance(right, Integer):
            return Integer(self.value // right.value)
        if isinstance(right, Float):
            return Float(float(self.value) / right.value)
        raise LogicError("Cannot div that with int")


class Float(BaseBox):
    def __init__(self, val):
        self.floatvalue = float(val)

    @property
    def value(self):
        return float(self.floatvalue)

    def __hash__(self):
        return compute_hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Float) and self.value == other.value

    def _hash(self):
        return compute_hash(self.floatvalue)

    def _eq(self, other):
        return isinstance(other, Float) and self.floatvalue == other.floatvalue

    def to_string(self):
        return str(self.value)

    def equals(self, right):
        if isinstance(right, Float):
            return Boolean(self.value == right.value)
        if isinstance(right, Integer):
            return Boolean(self.value == float(right.value))
        if isinstance(right, Boolean):
            return Boolean(self.value == float(right.to_int()))
        raise LogicError("Cannot compare that to float")

    def lte(self, right):
        if isinstance(right, Integer):
            return Boolean(self.value <= float(right.value))
        if isinstance(right, Float):
            return Boolean(self.value <= right.value)
        raise LogicError("Cannot compare that to integer")

    def lt(self, right):
        if isinstance(right, Integer):
            return Boolean(self.value < float(right.value))
        if isinstance(right, Float):
            return Boolean(self.value < right.value)
        raise LogicError("Cannot compare integer that way")

    def gt(self, right):
        if isinstance(right, Integer):
            return Boolean(self.value > float(right.value))
        if isinstance(right, Float):
            return Boolean(self.value > right.value)
        raise LogicError("Cannot compare integer that way")

    def gte(self, right):
        if isinstance(right, Integer):
            return Boolean(self.value >= float(right.value))
        if isinstance(right, Float):
            return Boolean(self.value >= right.value)
        raise LogicError("Cannot compare integer that way")

    def add(self, right):
        if isinstance(right, Integer):
            return Float(self.value + float(right.value))
        if isinstance(right, Float):
            return Float(self.value + right.value)
        raise LogicError("Cannot add that to float")

    def sub(self, right):
        if isinstance(right, Float):
            return Float(self.value - right.value)
        if isinstance(right, Integer):
            return Float(self.value - float(right.value))
        raise LogicError("Cannot sub string")

    def mul(self, right):
        if isinstance(right, Integer):
            return Float(self.value * float(right.value))
        if isinstance(right, Float):
            return Float(self.value * right.value)
        raise LogicError("Cannot mul that to float")

    def div(self, right):
        if isinstance(right, Integer):
            return Float(self.value / float(right.value))
        if isinstance(right, Float):
            return Float(self.value / right.value)
        raise LogicError("Cannot div that with float")

    def dump(self):
        return str(self.value)


class String(BaseBox):
    def __init__(self, value):
        self.value = str(value)

    def __hash__(self):
        return compute_hash(self.value)

    def __eq__(self, other):
        return isinstance(other, String) and self.value == other.value

    def _hash(self):
        return compute_hash(self.value)

    def _eq(self, other):
        return isinstance(other, String) and self.value == other.value

    def to_string(self):
        return str(self.value)

    def equals(self, right):
        if isinstance(right, String):
            return Boolean(self.value == right.value)
        if isinstance(right, Boolean):
            length = int(len(self.value) != 0)
            return Boolean(length == right.to_int())
        raise LogicError("Cannot compare that to string")

    def lte(self, right):
        if isinstance(right, String):
            return Boolean(self.value == right.value)
        raise LogicError("Cannot compare that to string")

    def lt(self, right):
        raise LogicError("Cannot compare string that way")

    def gt(self, right):
        raise LogicError("Cannot compare string that way")

    def gte(self, right):
        if isinstance(right, String):
            return Boolean(self.value == right.value)
        raise LogicError("Cannot compare that to string")

    def add(self, right):
        if isinstance(right, Integer):
            return String(self.value + str(right.value))
        if isinstance(right, Float):
            return String("%s%s" % (self.value, right.value))
        if isinstance(right, String):
            return String(self.value + right.value)
        raise LogicError("Cannot add that to string")

    def sub(self, right):
        if isinstance(right, Integer):
            end = len(self.value) - right.value
            if end < 0:
                raise LogicError("Cannot sub string")
            return String(self.value[:end])
        raise LogicError("Cannot sub string")

    def mul(self, right):
        if isinstance(right, Integer):
            return String(self.value * right.value)
        raise LogicError("Cannot multiply string with that")

    def div(self, right):
        raise LogicError("Cannot divide a string")

    def index(self, right):
        if isinstance(right, Integer) and right.value >= 0:
            return String(str(self.value[right.value]))
        raise LogicError("Cannot index with that")

    def dump(self):
        return str(self.value)


class Variable(BaseBox):
    def __init__(self, name, value):
        self.name = str(name)
        self.value = value

    def dump(self):
        return self.value.dump()
