# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.2rc1 (tags/v3.7.2rc1:75a402a217, Dec 11 2018, 22:09:03) [MSC v.1916 32 bit (Intel)]
# Embedded file name: ulang\codegen\python.py
import codegen, ast
FUNC_MAP = {'println':'print', 
 'tuple':'', 
 'char':'chr', 
 'isa':'isinstance', 
 'ceil':'math.ceil', 
 'floor':'math.floor', 
 'fabs':'math.fabs', 
 'sqrt':'math.sqrt', 
 'log':'math.log', 
 'log10':'math.log10', 
 'exp':'math.exp', 
 'pow':'math.pow', 
 'sin':'math.sin', 
 'cos':'math.cos', 
 'tan':'math.tan', 
 'asin':'math.asin', 
 'acos':'math.acos'}

class CodeGen(codegen.SourceGenerator):
    __doc__ = '\n    A simple AST-to-Python translator based on \n    codegen.SourceGenerator.\n    '

    def __init__(self):
        codegen.SourceGenerator.__init__(self, '  ', False)

    def visit_arg(self, arg):
        super().write(arg.arg)

    def visit_ImportFrom(self, node):
        self.newline(node)
        if node.module:
            self.write('from %s%s import ' % ('.' * node.level, node.module))
        else:
            self.write('from %s import ' % ('.' * node.level))
        for idx, item in enumerate(node.names):
            if idx:
                self.write(', ')
            self.visit(item)

    def visit_AnnAssign(self, node):
        self.newline(node)
        self.visit(node.target)
        self.write(' : ')
        self.visit(node.annotation)
        self.write(' = ')
        self.visit(node.value)

    def visit_Name(self, node):
        if node.id == 'PI':
            self.write('pi')
        else:
            super().visit_Name(node)

    def visit_NameConstant(self, node):
        if node.value == None:
            self.write('None')
        else:
            if node.value:
                self.write('True')
            else:
                self.write('False')

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in FUNC_MAP:
                node.func.id = FUNC_MAP[node.func.id]
        super().visit_Call(node)

    def visit_With(self, node):
        self.newline(node)
        self.write('with ')
        for idx, item in enumerate(node.items):
            if idx > 0:
                self.write(', ')
            self.visit(item)

        self.write(':')
        self.body(node.body)

    def visit_ExtSlice(self, node):
        for idx, s in enumerate(node.dims):
            if idx != 0:
                self.write(', ')
            self.visit(s)

    def visit_withitem(self, node):
        self.visit(node.context_expr)
        if node.optional_vars is not None:
            self.write(' as ')
            self.visit(node.optional_vars)

    def signature(self, node):
        want_comma = []

        def write_comma():
            if want_comma:
                self.write(', ')
            else:
                want_comma.append(True)

        padding = [None] * (len(node.args) - len(node.defaults))
        for arg, default in zip(node.args, padding + node.defaults):
            write_comma()
            self.visit(arg)
            if default is not None:
                self.write('=')
                self.visit(default)

        if node.vararg is not None:
            write_comma()
            self.write('*' + node.vararg.arg)
        if node.kwarg is not None:
            write_comma()
            self.write('**' + node.kwarg.arg)

    def to_source(self, node):
        self.visit(node)
        self.result.insert(0, 'import sys\nfrom math import *\nARGV = sys.argv[1:]\n')
        return ''.join(self.result)


def dump(node):
    return CodeGen().to_source(node)
# okay decompiling E:\ulang\ulang-0.2.2.exe_extracted\PYZ-00.pyz_extracted\ulang.codegen.python.pyc
