import parser, compiler, bytecode, objects, errors, prelude

class Interpreter(object):

    def __init__(self):
        self.last_bc = ''
        self.context = compiler.Context()
        self.import_prelude()
    
    def import_prelude(self):
        index = self.context.register_variable("print")
        self.context.variables[index] = objects.Variable("print",objects.ExternalFunction("print",prelude.print_fn,1))
        
        index = self.context.register_variable("readline")
        self.context.variables[index] = objects.Variable("readline",objects.ExternalFunction("readline",prelude.readline,1))
        
    def compile_interpret(self, ast, context=None):
        if not context:
            context = self.context
        byte_code = compiler.compile(ast, context)
        self.last_bc = ''
    
        return self.interpret(byte_code)
    
    def copy_context(self, code_from, code_to):
        source_variables = {}
        for variable in code_from.variables.values():
            source_variables[variable.name] = variable

        for index, variable in list(code_to.variables.items()):
            if variable.name in source_variables:
                source = source_variables[variable.name]
                code_to.variables[index] = objects.Variable(source.name, source.value)

    def bind_function(self, function_value, current_code):
        bound_variables = {}
        for index, variable in function_value.code.variables.items():
            bound_variables[index] = objects.Variable(variable.name, variable.value)

        bound_code = bytecode.Bytecode(
            instructions=list(function_value.code.instructions),
            arguments=list(function_value.code.arguments),
            constants=list(function_value.code.constants),
            variables=bound_variables,
            name=function_value.code.name,
        )
        self.copy_context(current_code, bound_code)
        return objects.Function(function_value.name, bound_code)
    
    def interpret(self, byte_code, args=None):
        if args is None:
            args = []
        
        pc = 0 # program counter
        stack = []
        try_stack = []
        variables = [objects.Null()] * 255
        
        assert(len(args) == len(byte_code.arguments))
        
        #print "(running %s)" % byte_code.name
        
        # copy args into inner context
        for i in range(0,len(args)):
            # TODO: this doesn't make sense, indexes change I think?
            # Make sure these aren't getting overwritten
            index = byte_code.arguments[i]
            #print "(arg %s going into %s)" % (args[i].dump(),index)
            existing_variable = byte_code.variables.get(index, None)
            if isinstance(existing_variable, objects.Variable):
                byte_code.variables[index] = objects.Variable(existing_variable.name, args[i])
            else:
                byte_code.variables[index] = objects.Variable("arg",args[i])
            
        
        self.last_bc += byte_code.dump(True)
        
        while pc < len(byte_code.instructions):
            try:
                opcode, arg = byte_code.instructions[pc]
                pc += 1

                if opcode == bytecode.LOAD_CONST:
                    value = byte_code.constants[arg]
                    stack.append(value)

                elif opcode == bytecode.LOAD_VARIABLE:
                    var = byte_code.variables[arg]
                    assert(isinstance(var,objects.Variable))
                    if isinstance(var.value, objects.Function):
                        stack.append(self.bind_function(var.value, byte_code))
                    else:
                        stack.append(var.value)

                elif opcode == bytecode.STORE_VARIABLE:
                    value = stack.pop()
                    oldvar = byte_code.variables.get(arg,None)
                    if isinstance(oldvar,objects.Variable):
                        byte_code.variables[arg] = objects.Variable(oldvar.name,value)
                    else:
                        byte_code.variables[arg] = objects.Variable("arg",value)
                    stack.append(value)

                elif opcode == bytecode.STORE_ARRAY:
                    values = []
                    for i in range(arg):
                        values.append(stack.pop())
                    stack.append(objects.Array(values))

                elif opcode == bytecode.STORE_DICT:
                    values = objects.r_dict(objects.dict_eq,objects.dict_hash)
                    for i in range(arg):
                        values[stack.pop()] = stack.pop()
                    stack.append(objects.Dict(values))

                elif opcode == bytecode.PRINT:
                    value = stack.pop()
                    print(value.to_string())
                    stack.append(objects.Null())

                elif opcode == bytecode.INDEX:
                    left = stack.pop()
                    right = stack.pop()
                    result = left.index(right)
                    stack.append(result)

                elif opcode == bytecode.BINARY_ADD:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.add(right)
                    stack.append(result)

                elif opcode == bytecode.BINARY_SUB:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.sub(right)
                    stack.append(result)

                elif opcode == bytecode.BINARY_MUL:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.mul(right)
                    stack.append(result)

                elif opcode == bytecode.BINARY_DIV:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.div(right)
                    stack.append(result)

                elif opcode == bytecode.BINARY_NEQ:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.equals(right)
                    result.boolvalue = not result.boolvalue
                    stack.append(result)

                elif opcode == bytecode.BINARY_EQ:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.equals(right)
                    stack.append(result)

                elif opcode == bytecode.BINARY_GT:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.gt(right)
                    stack.append(result)

                elif opcode == bytecode.BINARY_GTE:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.gte(right)
                    stack.append(result)

                elif opcode == bytecode.BINARY_LT:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.lt(right)
                    stack.append(result)

                elif opcode == bytecode.BINARY_LTE:
                    right = stack.pop()
                    left = stack.pop()
                    result = left.lte(right)
                    stack.append(result)

                elif opcode == bytecode.RETURN:
                    if arg == 1:
                        if len(stack) > 0:
                            result = stack.pop()
                            return result
                        return objects.Null()

                elif opcode == bytecode.JUMP_IF_NOT_ZERO:
                    val = stack.pop()
                    assert(isinstance(val,objects.BaseBox))
                    result = val.equals(objects.Boolean(True))
                    assert(isinstance(result,objects.Boolean))
                    if result.value:
                        pc = arg

                elif opcode == bytecode.JUMP_IF_ZERO:
                    val = stack.pop()
                    assert(isinstance(val,objects.BaseBox))
                    result = val.equals(objects.Boolean(True))
                    assert(isinstance(result,objects.Boolean))
                    if not result.value:
                        pc = arg

                elif opcode == bytecode.JUMP:
                    pc = arg

                elif opcode == bytecode.PUSH_TRY:
                    try_stack.append((arg, len(stack)))

                elif opcode == bytecode.POP_TRY:
                    if try_stack:
                        try_stack.pop()

                elif opcode == bytecode.CALL:
                    assert(isinstance(byte_code.variables[arg],objects.Variable))
                    val = byte_code.variables[arg].value
                    if isinstance(val,objects.Function):
                        bound_function = self.bind_function(val, byte_code)
                        func = bound_function.code
                        call_args = []
                        if len(func.arguments) > len(stack):
                            raise Exception("Not enough arguments")

                        for i in range(0,len(func.arguments)):
                            call_args.append(stack.pop())
                        stack.append(self.interpret(func,call_args))
                    elif isinstance(val, objects.ExternalFunction):
                        func = val.fn
                        arglen = val.args
                        call_args = []
                        for i in range(0,arglen):
                            call_args.append(stack.pop())
                        result = func(call_args)
                        stack.append(result)
                    else:
                        raise Exception("Not a function")
            except Exception:
                if try_stack:
                    handler_pc, stack_depth = try_stack.pop()
                    del stack[stack_depth:]
                    pc = handler_pc
                    continue
                raise
        return stack[len(stack) - 1]
        

