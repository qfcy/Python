# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.2rc1 (tags/v3.7.2rc1:75a402a217, Dec 11 2018, 22:09:03) [MSC v.1916 32 bit (Intel)]
# Embedded file name: ulang\codegen\blockly.py
import ast, sys
from copy import deepcopy
import xml.etree.ElementTree as etree
import xml.dom.minidom as minidom
import random, string

def randomString(stringLength=20):
    """
    Generate a random string of fixed length 
    """
    letters = string.ascii_letters
    return ''.join((random.choice(letters) for i in range(stringLength)))


def dump(ast):
    return CodeGen().dump(ast)


class CodeGen(ast.NodeVisitor):
    __doc__ = '\n    A simple python ast to blockly xml converter.\n    '

    def __init__(self):
        self.ast2xml_ = {}
        self.variables_ = {}
        self.functions_ = {}

    def dump(self, ast):
        self.ast2xml_ = {}
        self.variables_ = {}
        self.functions_ = {}
        self.calls_ = set()
        self.visit(ast)
        roots = self.ast2xml_[ast]
        assert isinstance(roots, list)
        for call in self.calls_:
            self.fix_call(call, first_pass=False)

        if len(self.variables_) > 0:
            variables = etree.Element('variables')
            for name, id in self.variables_.items():
                self.add_variable(variables, name, id=id)

            roots.insert(0, variables)
        xml = ''.join((etree.tostring(i).decode('utf-8') for i in roots))
        xml = '<xml xmlns="http://www.w3.org/1999/xhtml">%s</xml>' % xml
        return minidom.parseString(xml).toprettyxml(indent='  ')

    def visit_Module(self, module):
        roots = []
        main = None
        for stmt in module.body:
            self.visit(stmt)
            block = self.ast2xml_.get(stmt)
            if block is None:
                continue
            if not self.has_next(stmt):
                roots.append(block)
            else:
                if main is None:
                    roots.append(block)
                else:
                    self.connect(main, block)
                main = block

        self.ast2xml_[module] = roots

    def visit_FunctionDef(self, func_def):
        root = self.add_block(func_def, 'procedures_defnoreturn')
        self.functions_[func_def.name] = func_def
        if len(func_def.args.args) > 0:
            mutation = self.add_mutation(root)
            for arg in func_def.args.args:
                if arg.arg not in self.variables_:
                    self.variables_[arg.arg] = randomString()
                arg_elem = etree.SubElement(mutation, 'arg')
                arg_elem.set('name', arg.arg)
                arg_elem.set('varid', self.variables_[arg.arg])

        self.add_field(root, 'NAME', func_def.name)
        last = func_def.body[(-1)]
        if isinstance(last, ast.Return) and last.value is not None:
            self.add_statement(root, 'STACK', func_def.body[:-1])
            self.add_value(root, 'RETURN', last)
            root.set('type', 'procedures_defreturn')
        else:
            self.add_statement(root, 'STACK', func_def.body)

    def visit_Name(self, name):
        if name.id not in self.variables_:
            self.variables_[name.id] = randomString()
        block_type = 'variables_get' if isinstance(name.ctx, ast.Load) else 'variables_set'
        root = self.add_block(name, block_type)
        self.add_field(root=root,
          name='VAR',
          text=(name.id),
          id=(self.variables_[name.id]),
          variabletype='')

    def visit_If(self, if_stmt):
        root = self.add_block(if_stmt, 'controls_if')
        if len(if_stmt.orelse) > 0:
            self.add_mutation(root=root,
              elseif='0').set('else', '1')
        self.add_value(root, 'IF0', if_stmt.test)
        self.add_statement(root, 'DO0', if_stmt.body)
        if len(if_stmt.orelse) > 0:
            self.add_statement(root, 'ELSE', if_stmt.orelse)

    def visit_While(self, while_stmt):
        root = self.add_block(while_stmt, 'controls_whileUntil')
        self.add_field(root, 'MODE', 'WHILE')
        self.add_value(root, 'BOOL', while_stmt.test)
        self.add_statement(root, 'DO', while_stmt.body)

    def visit_For(self, for_stmt):
        it = for_stmt.iter
        ty = 'controls_forEach'
        if isinstance(it, ast.Call):
            if isinstance(it.func, ast.Name):
                if it.func.id == 'range':
                    ty = 'controls_for'
        else:
            root = self.add_block(for_stmt, ty)
            var = for_stmt.target
            assert isinstance(var, ast.Name)
            self.visit(var)
            self.add_field(root, 'VAR', var.id)
            if ty == 'controls_for':
                args = it.args
                if len(args) == 1:
                    args.insert(0, ast.Num(n=0))
                else:
                    if len(args) == 2:
                        args.append(ast.Num(n=1))
                    self.add_value(root, 'FROM', args[0])
                    if isinstance(args[1], ast.Num):
                        self.add_value(root, 'TO', ast.Num(args[1].n - 1))
                    else:
                        self.add_value(root, 'TO', ast.BinOp(left=(args[1]),
                          right=ast.Num(n=1),
                          op=(ast.Sub())))
                self.add_value(root, 'BY', args[2])
            else:
                self.add_value(root, 'LIST', it)
        self.add_statement(root, 'DO', for_stmt.body)

    def visit_Break(self, brk):
        root = self.add_block(brk, 'controls_flow_statements')
        self.add_field(root, 'FLOW', 'BREAK')

    def visit_Continue(self, cont):
        root = self.add_block(cont, 'controls_flow_statements')
        self.add_field(root, 'FLOW', 'CONTINUE')

    def visit_Return(self, ret):
        root = self.add_block(ret, 'procedures_ifreturn')
        if ret.value is not None:
            self.add_mutation(root=root,
              value='1')
            self.add_value(root, 'CONDITION', ast.NameConstant(True))
            self.add_value(root, 'VALUE', ret.value)

    def visit_Assign(self, assign):
        if not len(assign.targets) == 1:
            raise AssertionError
        else:
            target = assign.targets[0]
            self.visit(assign.targets[0])
            self.visit(assign.value)
            if isinstance(target, ast.Name):
                block = self.ast2xml_[target]
                self.add_value(block, 'VALUE', assign.value)
                self.ast2xml_[assign] = block
            else:
                if isinstance(target, ast.Tuple):
                    if not (isinstance(assign.value, ast.Tuple) and len(assign.value.elts) == len(target.elts)):
                        raise AssertionError
                    elts = assign.value.elts
                    for i in range(len(target.elts)):
                        name = target.elts[i]
                        assert isinstance(name, ast.Name)
                        block = self.ast2xml_[name]
                        self.add_value(block, 'VALUE', elts[i])
                        if i == 0:
                            self.ast2xml_[assign] = block
                        else:
                            self.connect(self.ast2xml_[target.elts[(i - 1)]], block)

    def visit_AugAssign(self, aug):
        assert isinstance(aug.target, ast.Name)
        assign = ast.Assign(targets=[
         aug.target],
          op=(aug.op),
          value=ast.BinOp(left=ast.Name(id=(aug.target.id),
          ctx=(ast.Load())),
          right=(aug.value),
          op=(aug.op)))
        self.visit(assign)
        self.ast2xml_[aug] = self.ast2xml_[assign]

    def visit_Compare(self, cmp):
        if not (len(cmp.ops) == 1 and len(cmp.comparators) == 1):
            raise AssertionError
        root = self.add_block(cmp, 'logic_compare')
        opc = cmp.ops[0].__class__.__name__.upper()
        if opc == 'NOTEQ':
            opc = 'NEQ'
        self.add_field(root=root,
          name='OP',
          text=opc)
        self.add_value(root, 'A', cmp.left)
        self.add_value(root, 'B', cmp.comparators[0])

    def visit_BinOp(self, binop):
        root = self.add_block(binop, 'math_arithmetic')
        self.add_field(root=root,
          name='OP',
          text=(binop.op.__class__.__name__.upper()))
        self.add_value(root, 'A', binop.left)
        self.add_value(root, 'B', binop.right)

    def visit_UnaryOp(self, uop):
        if isinstance(uop.op, ast.Not):
            root = self.add_block(uop, 'logic_negate')
            self.add_value(root, 'BOOL', uop.operand)
        else:
            if isinstance(uop.op, ast.USub):
                root = self.add_block(uop, 'math_single')
                self.add_field(root, 'OP', 'NEG')
                self.add_value(root, 'NUM', uop.operand)
            else:
                assert False, 'unsupport unary op %s' % str(uop.op)

    def visit_BoolOp(self, boolop):
        root = self.add_block(boolop, 'logic_operation')
        self.add_field(root=root,
          name='OP',
          text=(boolop.op.__class__.__name__.upper()))
        self.add_value(root, 'A', boolop.values[0])
        if len(boolop.values) == 2:
            self.add_value(root, 'B', boolop.values[1])
        else:
            rest = deepcopy.copy(boolop)
            rest.values = rest.values[1:]
            self.add_value(root, 'B', rest)

    def visit_Call(self, call):
        fname, value = (None, None)
        if isinstance(call.func, ast.Name):
            fname = call.func.id
        else:
            if isinstance(call.func, ast.Attribute):
                fname = call.func.attr
                value = call.func.value
            else:
                if fname == 'print' or fname == 'println':
                    root = self.add_block(call, 'text_print')
                    self.add_value(root, 'TEXT', call.args[0])
                    for arg in call.args[1:]:
                        block = self.add_block(None, 'text_print')
                        self.add_value(block, 'TEXT', arg)
                        self.connect(root, block)
                        root = block

        if fname == 'len':
            assert len(call.args) == 1
            root = self.add_block(call, 'lists_length')
            self.add_value(root, 'VALUE', call.args[0])
        else:
            if fname == 'str':
                assert len(call.args) == 1
                self.visit(call.args[0])
                self.ast2xml_[call] = self.ast2xml_[call.args[0]]
            else:
                if fname == 'assert':
                    pass
                elif fname == 'append':
                    if not (len(call.args) == 1 and isinstance(value, ast.Name)):
                        raise AssertionError
                    root = self.add_block(call, 'text_append')
                    self.add_field(root, 'VAR', value.id)
                    self.add_value(root, 'TEXT', call.args[0])
                else:
                    root = self.add_block(call, 'procedures_callreturn')
                    self.add_mutation(root=root,
                      name=fname)
                    self.fix_call(call, first_pass=True)
                    for i in range(len(call.args)):
                        self.add_value(root, 'ARG' + str(i), call.args[i])

    def visit_Expr(self, expr):
        self.visit(expr.value)
        if isinstance(expr.value, ast.Call):
            elem = self.ast2xml_.get(expr.value)
            if elem is not None:
                if elem.get('type') == 'procedures_callreturn':
                    elem.set('type', 'procedures_callnoreturn')
        if expr.value in self.ast2xml_:
            self.ast2xml_[expr] = self.ast2xml_[expr.value]

    def visit_List(self, lst):
        root = self.add_block(lst, 'lists_create_with')
        self.add_mutation(root=root,
          items=(str(len(lst.elts))))
        for i in range(len(lst.elts)):
            self.add_value(root, 'ADD%d' % i, lst.elts[i])

    def visit_Tuple(self, tup):
        self.visit_List(tup)

    def visit_Subscript(self, sub):
        assert isinstance(sub.slice, ast.Index)
        root = self.add_block(sub, 'lists_getIndex')
        self.add_mutation(root=root,
          statement='false',
          at='true')
        self.add_field(root, 'MODE', 'GET')
        self.add_field(root, 'WHERE', 'FROM_START')
        self.add_value(root, 'VALUE', sub.value)
        self.add_value(root, 'AT', sub.slice)

    def visit_Index(self, idx):
        self.visit(idx.value)
        self.ast2xml_[idx] = self.ast2xml_[idx.value]

    def visit_Num(self, num):
        self.add_field(root=(self.add_block(num, 'math_number')),
          name='NUM',
          text=(str(num.n)))

    def visit_Str(self, s):
        self.add_field(root=(self.add_block(s, 'text')),
          name='TEXT',
          text=(s.s))

    def visit_NameConstant(self, c):
        if c.value is None:
            self.add_block(c, 'logic_null')
            return
        root = self.add_block(c, 'logic_boolean')
        self.add_field(root, 'BOOL', str(c.value).upper())

    def visit_IfExp(self, expr):
        root = self.add_block(expr, 'logic_ternary')
        self.add_value(root, 'IF', expr.test)
        self.add_value(root, 'THEN', expr.body)
        self.add_value(root, 'ELSE', expr.orelse)

    def visit_Dict(self, dct):
        self.unimplement(dct)

    def visit_Try(self, tr):
        self.unimplement(tr)

    def visit_Except(self, excpt):
        self.unimplement(excpt)

    def visit_Import(self, imp):
        self.unimplement(imp)

    def visit_ImportFrom(self, imp):
        self.unimplement(imp)

    def visit_Lambda(self, expr):
        self.unimplement(expr)

    def visit_ClassDef(self, cls):
        self.unimplement(cls)

    def unimplement(self, node):
        assert False, 'unimplement ast node "%s"' % node.__class__.__name__

    def add_variable(self, root, name, ty='', id=randomString()):
        var = etree.SubElement(root, 'variable')
        var.set('type', ty)
        var.set('id', id)
        var.text = name
        return var

    def add_block(self, ast, block_type):
        block = etree.Element('block')
        block.set('type', block_type)
        block.set('id', randomString())
        if ast is not None:
            self.ast2xml_[ast] = block
        return block

    def add_field(self, root, name, text='', **kwargs):
        field = etree.SubElement(root, 'field')
        field.set('name', name)
        field.text = text
        for key, value in kwargs.items():
            field.set(key, value)

        return field

    def add_value(self, root, name, stmt=None):
        value = etree.SubElement(root, 'value')
        value.set('name', name)
        if stmt is not None:
            if stmt not in self.ast2xml_:
                self.visit(stmt)
            block = self.ast2xml_[stmt]
            if block is not None:
                value.append(block)
        return value

    def add_statement(self, root, name, stmts=[]):
        statement = etree.SubElement(root, 'statement')
        statement.set('name', name)
        for i in range(len(stmts)):
            stmt = stmts[i]
            if stmt not in self.ast2xml_:
                self.visit(stmt)
            if stmt not in self.ast2xml_:
                continue
            if len(statement) == 0:
                statement.append(self.ast2xml_[stmt])
            else:
                self.connect(self.ast2xml_[stmts[(i - 1)]], self.ast2xml_[stmt])

        return statement

    def add_mutation(self, root, **kwargs):
        mutation = etree.SubElement(root, 'mutation')
        for key, value in kwargs.items():
            mutation.set(key, value)

        return mutation

    def connect(self, prev, block):
        while True:
            next = prev.find('next', None)
            if next == None:
                etree.SubElement(prev, 'next').append(block)
                break
            else:
                prev = next.find('block', None)

    def fix_call(self, call, first_pass=True):
        assert isinstance(call.func, ast.Name)
        assert call in self.ast2xml_
        callee = call.func.id
        call_block = self.ast2xml_[call]
        func_def = self.functions_[callee] if callee in self.functions_ else None
        if func_def is None:
            assert first_pass, 'func "%s" is not defined' % callee
            self.calls_.add(call)
            return
        mutation = call_block.find('mutation')
        assert mutation is not None
        for arg in func_def.args.args:
            arg_elem = etree.SubElement(mutation, 'arg')
            arg_elem.set('name', arg.arg)
            arg_elem.set('id', self.variables_[arg.arg])

    def has_next(self, node):
        if not isinstance(node, ast.stmt) or isinstance(node, ast.FunctionDef):
            return False
        return True
# okay decompiling E:\ulang\ulang-0.2.2.exe_extracted\PYZ-00.pyz_extracted\ulang.codegen.blockly.pyc
