#!/usr/bin/env python3
"""
generate_parse_tree.py
======================
Generates a visual parse tree diagram for Sarana code.

This shows the hierarchical structure of how the parser
derives the program from the grammar rules.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import tokenize
from parser import parse


def generate_tree_ascii(node, prefix='', is_last=True):
    """
    Generate ASCII art tree representation of AST.
    
    Args:
        node: AST node to visualize
        prefix: String prefix for indentation
        is_last: Whether this is the last child
        
    Returns:
        str: ASCII art representation
    """
    lines = []
    
    # Node connector
    connector = '└── ' if is_last else '├── '
    
    # Node name and value
    node_name = node.__class__.__name__
    
    # Add node-specific details
    details = ''
    if hasattr(node, 'name'):
        details = f' "{node.name}"'
    elif hasattr(node, 'value'):
        details = f' = {node.value}'
    elif hasattr(node, 'operator'):
        details = f' "{node.operator}"'
    
    lines.append(prefix + connector + node_name + details)
    
    # Extension for children
    extension = '    ' if is_last else '│   '
    
    # Get children
    children = []
    
    if node_name == 'Program':
        children = node.statements
    elif node_name == 'BloomStatement':
        children = [('name', node.name), ('value', node.value)]
    elif node_name == 'EchoStatement':
        children = node.expressions
    elif node_name == 'BinaryOp':
        children = [node.left, node.right]
    elif node_name == 'UnaryOp':
        children = [node.operand]
    elif node_name == 'FunctionCall':
        children = node.arguments
    elif node_name == 'WhenStatement':
        children = [('condition', node.condition)]
        if node.then_body:
            children.append(('then', node.then_body))
        if node.otherwise_body:
            children.append(('otherwise', node.otherwise_body))
    elif node_name == 'CycleStatement':
        children = [('condition', node.condition), ('body', node.body)]
    elif node_name == 'CraftStatement':
        children = [('params', node.params), ('body', node.body)]
    elif node_name == 'TryKetchStatement':
        children = [('try', node.try_body), ('ketch', node.ketch_body)]
    elif node_name == 'ReturnStatement':
        if node.value:
            children = [node.value]
    
    # Process children
    for i, child in enumerate(children):
        is_last_child = (i == len(children) - 1)
        
        if isinstance(child, tuple):
            # Labeled child (e.g., 'condition', node)
            label, child_node = child
            
            if isinstance(child_node, str):
                # Simple string value
                lines.append(prefix + extension + ('└── ' if is_last_child else '├── ') + f'{label}: "{child_node}"')
            elif isinstance(child_node, list):
                # List of nodes
                lines.append(prefix + extension + ('└── ' if is_last_child else '├── ') + f'{label}:')
                for j, item in enumerate(child_node):
                    is_last_item = (j == len(child_node) - 1)
                    lines.extend(generate_tree_ascii(item, prefix + extension + ('    ' if is_last_child else '│   '), is_last_item).split('\n'))
            else:
                # Single node
                lines.append(prefix + extension + ('└── ' if is_last_child else '├── ') + f'{label}:')
                lines.extend(generate_tree_ascii(child_node, prefix + extension + ('    ' if is_last_child else '│   '), True).split('\n'))
        else:
            # Direct child node
            lines.extend(generate_tree_ascii(child, prefix + extension, is_last_child).split('\n'))
    
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════════
# Example 1: Simple Expression (for PEMDAS demonstration)
# ═══════════════════════════════════════════════════════════════════════

print('\n' + '='*70)
print('PARSE TREE EXAMPLE 1: Simple Expression (PEMDAS)')
print('='*70)
print()

code1 = 'bloom C = A + B * B;'
print(f'Sarana Code: {code1}')
print()

ast1 = parse(code1)
tree1 = generate_tree_ascii(ast1)

print('Parse Tree:')
print(tree1)
print()
print('Explanation:')
print('  - The root is "Program" containing all statements')
print('  - BloomStatement declares variable "C"')
print('  - The expression "A + B * B" shows PEMDAS:')
print('    - The "+" is the root operator (lower precedence)')
print('    - The right child is "B * B" (higher precedence)')
print('    - This means: C = A + (B * B), not (C = A + B) * B')
print()


# ═══════════════════════════════════════════════════════════════════════
# Example 2: Full Required Sample
# ═══════════════════════════════════════════════════════════════════════

print('='*70)
print('PARSE TREE EXAMPLE 2: Required Assignment Sample')
print('='*70)
print()

REQUIRED_SAMPLE = """bloom A = 20;
bloom B = 40;
bloom C = A + B * B;
try {
    bloom D = C / 0;
}
ketch {
    echo "Error: Division by zero attempted but not allowed.";
}
echo "The result is " C;"""

print('Sarana Code:')
print(REQUIRED_SAMPLE)
print()

ast2 = parse(REQUIRED_SAMPLE)
tree2 = generate_tree_ascii(ast2)

print('Parse Tree:')
print(tree2)
print()


# ═══════════════════════════════════════════════════════════════════════
# Example 3: Function with Conditional
# ═══════════════════════════════════════════════════════════════════════

print('='*70)
print('PARSE TREE EXAMPLE 3: Function with Conditional')
print('='*70)
print()

code3 = """craft max(a, b) {
    when (a > b) {
        return a;
    } otherwise {
        return b;
    }
}"""

print('Sarana Code:')
print(code3)
print()

ast3 = parse(code3)
tree3 = generate_tree_ascii(ast3)

print('Parse Tree:')
print(tree3)
print()


# ═══════════════════════════════════════════════════════════════════════
# Save detailed diagram to file
# ═══════════════════════════════════════════════════════════════════════

print('='*70)
print('Saving parse tree diagrams to file...')
print('='*70)
print()

with open('PARSE_TREE_DIAGRAMS.txt', 'w') as f:
    f.write('SARANA PARSE TREE DIAGRAMS\n')
    f.write('='*70 + '\n')
    f.write('Generated by: generate_parse_tree.py\n')
    f.write('\n')
    f.write('A parse tree shows the hierarchical structure of a program\n')
    f.write('as derived from the grammar rules. Each node represents either\n')
    f.write('a grammar rule or a terminal symbol (token).\n')
    f.write('\n')
    
    f.write('='*70 + '\n')
    f.write('EXAMPLE 1: Simple Expression (PEMDAS)\n')
    f.write('='*70 + '\n')
    f.write(f'\nSarana Code: {code1}\n\n')
    f.write('Parse Tree:\n')
    f.write(tree1 + '\n\n')
    f.write('Key Observations:\n')
    f.write('- The "+" operator is the root of the expression\n')
    f.write('- The "*" operator is deeper in the tree (higher precedence)\n')
    f.write('- This structure enforces PEMDAS: C = A + (B * B)\n')
    f.write('\n')
    
    f.write('='*70 + '\n')
    f.write('EXAMPLE 2: Required Assignment Sample\n')
    f.write('='*70 + '\n')
    f.write('\nSarana Code:\n')
    f.write(REQUIRED_SAMPLE + '\n\n')
    f.write('Parse Tree:\n')
    f.write(tree2 + '\n\n')
    f.write('Key Observations:\n')
    f.write('- Program has 5 top-level statements\n')
    f.write('- Three BloomStatements (A, B, C)\n')
    f.write('- One TryKetchStatement with nested blocks\n')
    f.write('- One EchoStatement with multiple expressions\n')
    f.write('\n')
    
    f.write('='*70 + '\n')
    f.write('EXAMPLE 3: Function with Conditional\n')
    f.write('='*70 + '\n')
    f.write('\nSarana Code:\n')
    f.write(code3 + '\n\n')
    f.write('Parse Tree:\n')
    f.write(tree3 + '\n\n')
    f.write('Key Observations:\n')
    f.write('- CraftStatement defines a function\n')
    f.write('- Function body contains a WhenStatement\n')
    f.write('- WhenStatement has both "then" and "otherwise" branches\n')
    f.write('- Each branch contains a ReturnStatement\n')
    f.write('\n')

print('✓ Parse tree diagrams saved to: PARSE_TREE_DIAGRAMS.txt')
print()
print('You can view the file to see detailed ASCII art parse trees')
print('for various Sarana programs, showing how the parser interprets')
print('the code according to the grammar rules.')
print()
