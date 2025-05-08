# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.2rc1 (tags/v3.7.2rc1:75a402a217, Dec 11 2018, 22:09:03) [MSC v.1916 32 bit (Intel)]
# Embedded file name: ulang\parser\core.py
from rply import Token
from rply.token import SourcePosition
from rply.errors import LexingError
from ulang.parser.lexer import RULES, lexer
from ulang.parser.error import SyntaxError
from ulang.parser.lrparser import LRParser
from ulang.parser.parsergenerator import ParserGenerator
from ulang.codegen.blockly import randomString
import ast
from copy import deepcopy

class NameFixPass(ast.NodeTransformer):
    __doc__ = "\n    A python NodeVisitor which traverses the generated ast\n    to fix the signature of class methods by adding the\n    implicit argument 'self' and also convert the function\n    name of the class constructors..\n    "

    def __init__(self, filename):
        self.filename = filename
        self.cls = ['']

    def visit_FunctionDef(self, func):
        if func.name.startswith('$'):
            func.name = func.name.replace('$', '')
            if func.name == self.cls[(-1)]:
                func.name = '__init__'
            func.args.args.insert(0, ast.arg(arg='self',
              annotation=None,
              lineno=(func.lineno),
              col_offset=(func.col_offset)))
        else:
            if self.cls[(-1)]:
                if not func.args.args or func.args.args[0].arg != 'self':
                    decorator = ast.Name(id='staticmethod',
                      ctx=(ast.Load()),
                      lineno=(func.lineno),
                      col_offset=(func.col_offset))
                    func.decorator_list.append(decorator)
        self.cls.append(None)
        func = self.generic_visit(func)
        self.cls.pop(-1)
        return func

    def visit_ClassDef(self, cls):
        self.cls.append(cls.name)
        cls = self.generic_visit(cls)
        self.cls.pop(-1)
        return cls

    def visit_Call(self, call):
        func = call.func
        if isinstance(func, ast.Name):
            if func.id == 'super' and len(call.args) > 0:
                func = ast.Call(func=func,
                  args=[],
                  keywords=[],
                  starargs=None,
                  kwargs=None,
                  lineno=(func.lineno),
                  col_offset=(func.col_offset))
                call.func = ast.Attribute(value=func,
                  attr='__init__',
                  ctx=(ast.Load()),
                  lineno=(func.lineno),
                  col_offset=(func.col_offset))
                if len(call.args) == 1 and call.args[0] is None:
                    call.args = []
            elif func.id == 'assert':
                if len(call.args) == 1:
                    call.args.append(ast.Str(s=('@ "%s" line %d:%d' % (
                     self.filename,
                     call.args[0].lineno,
                     call.args[0].col_offset)),
                      lineno=(call.args[0].lineno),
                      col_offset=(call.args[0].col_offset)))
        return call


class AnnoFuncInsertPass(ast.NodeTransformer):
    __doc__ = '\n    Visit all ast to insert each anonymous function\n    just before where it has been referenced.\n    '

    def __init__(self, anonfuncs):
        self.anonfuncs_ = anonfuncs

    def generic_visit(self, node):
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                if len(old_value) > 0:
                    if isinstance(old_value[0], ast.stmt):
                        old_value[:] = self.visit_stmts(old_value)
                        continue
                    new_values = []
                    for value in old_value:
                        if isinstance(value, ast.AST):
                            value = self.visit(value)
                            if value is None:
                                continue
                            else:
                                if not isinstance(value, ast.AST):
                                    new_values.extend(value)
                                    continue
                        new_values.append(value)

                    old_value[:] = new_values
            if isinstance(old_value, ast.AST):
                new_value = self.visit(old_value)
                if new_value is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_value)

        return node

    def visit_stmts(self, stmts):
        new_stmts = []
        for stmt in stmts:
            stmt = self.visit(stmt)
            for node in ast.walk(stmt):
                if isinstance(node, ast.Name) and node in self.anonfuncs_:
                    new_stmts.append(self.anonfuncs_[node])
                    del self.anonfuncs_[node]

            new_stmts.append(stmt)

        return new_stmts


class Parser:
    __doc__ = '\n    A simple LR(1) parser to parse the source code of µ\n    and yield the python ast for later using..\n    '

    def __init__(self, lexer=lexer):
        self.lexer_ = lexer
        self.filename_ = ''
        self.anonfuncs_ = {}
        self.source_ = None

    def parse(self, source, filename=''):
        self.filename_ = filename
        self.source_ = source.split('\n')
        try:
            tokens = self.lexer_.lex(source)
            nodes = self.parser_.parse(tokens, state=self)
        except LexingError as e:
            try:
                raise SyntaxError(message='unknown token is found here',
                  filename=(self.filename_),
                  lineno=(e.getsourcepos().lineno),
                  colno=(e.getsourcepos().colno),
                  source=(self.source_))
            finally:
                e = None
                del e

        nodes = AnnoFuncInsertPass(self.anonfuncs_).visit(nodes)
        nodes = NameFixPass(filename).visit(nodes)
        return nodes

    def getsourcepos(self, p):
        if isinstance(p, list):
            if len(p) > 0:
                p = p[0]
        if isinstance(p, Token):
            if p.gettokentype() == '$end':
                return self.getendpos()
            return p.getsourcepos()
        if isinstance(p, ast.stmt) or isinstance(p, ast.expr):
            return SourcePosition(0, p.lineno, p.col_offset)
        return SourcePosition(0, 0, 0)

    def getendpos(self):
        idx = -1
        line = len(self.source_)
        column = len(self.source_[(-1)])
        return SourcePosition(idx, line, column)

    def getlineno(self, p):
        try:
            return self.getsourcepos(p).lineno
        except:
            return 0

    def getcolno(self, p):
        try:
            return self.getsourcepos(p).colno
        except:
            return 0

    pg_ = ParserGenerator(RULES,
      precedence=[
     (
      'nonassoc', ['YIELD', 'SUPER', 'IDENTIFIER']),
     (
      'right', ['->']),
     (
      'right', ['?', ':']),
     (
      'left', ['OR']),
     (
      'left', ['AND']),
     (
      'left', ['<<', '>>']),
     (
      'nonassoc', ['>', '<', '>=', '<=', '!==', '===']),
     (
      'left', ['!=', '==']),
     (
      'nonassoc', ['BY']),
     (
      'nonassoc', ['DOTDOT', 'DOTDOTLT']),
     (
      'nonassoc', ['(']),
     (
      'left', ['&', '|']),
     (
      'left', ['+', '-']),
     (
      'left', ['*', '/', '%']),
     (
      'left', ['!']),
     (
      'right', ['^'])],
      cache_id='ulang_grammar')

    @pg_.production('start : stmt_list')
    def start(self, p):
        return ast.Module(body=(p[0]),
          type_ignores=[])

    @pg_.production('block : ;')
    @pg_.production('block : LBRACE stmt_list RBRACE')
    def block(self, p):
        if len(p) == 3:
            if p[1]:
                return p[1]
        return [
         ast.Pass(lineno=(self.getlineno(p)),
           col_offset=(self.getcolno(p)))]

    @pg_.production('stmt_list : ')
    @pg_.production('stmt_list : stmt_list_')
    @pg_.production('stmt_list : stmt_list_ NEWLINE')
    @pg_.production('stmt_list : stmt_list_ ;')
    def stmt_list(self, p):
        if len(p) > 0:
            return p[0]
        return []

    @pg_.production('stmt_list_ : stmt')
    @pg_.production('stmt_list_ : stmt_list_ NEWLINE stmt')
    @pg_.production('stmt_list_ : stmt_list_ ; stmt')
    def stmt_list_(self, p):
        if len(p) == 1:
            return [
             p[0]]
        p[0].append(p[(-1)])
        return p[0]

    @pg_.production('stmt : type_define')
    @pg_.production('stmt : function')
    @pg_.production('stmt : if_stmt')
    @pg_.production('stmt : while_stmt')
    @pg_.production('stmt : for_stmt')
    @pg_.production('stmt : declaration')
    def compound_stmt(self, p):
        return p[0]

    @pg_.production('type_define : TYPE name bases type_body')
    def type_define(self, p):
        return ast.ClassDef(name=(p[1].id),
          bases=(p[2]),
          keywords=[],
          body=(p[(-1)]),
          decorator_list=[],
          starargs=None,
          kwargs=None,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('bases :')
    @pg_.production('bases : : prefix_expr')
    @pg_.production('bases : : prefix_exprs')
    def bases(self, p):
        if len(p) == 0:
            return []
        if isinstance(p[1], list):
            return p[1]
        return [
         p[1]]

    @pg_.production('type_body : LBRACE type_stmts RBRACE')
    def type_body(self, p):
        return p[1]

    @pg_.production('type_stmts : ')
    @pg_.production('type_stmts : type_stmts type_stmt')
    def type_stmts(self, p):
        if len(p) == 0:
            return []
        elif isinstance(p[1], list):
            p[0] += p[1]
        else:
            p[0].append(p[1])
        return p[0]

    @pg_.production('type_stmt : block')
    @pg_.production('type_stmt : type_define')
    @pg_.production('type_stmt : operator')
    @pg_.production('type_stmt : function')
    @pg_.production('type_stmt : property')
    def type_stmt(self, p):
        return p[0]

    @pg_.production('property : ATTR IDENTIFIER block')
    @pg_.production('property : ATTR IDENTIFIER ( ) block')
    @pg_.production('property : ATTR IDENTIFIER = ( param ) block')
    def property(self, p):
        name = p[1].getstr()
        func = ast.FunctionDef(name=name,
          args=(self.param_list()),
          body=(p[(-1)]),
          decorator_list=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        if len(p) == 7:
            func.args.args.append(p[4])
            func.decorator_list.append(ast.Attribute(value=ast.Name(id=(name.replace('$', '')),
              ctx=(ast.Load()),
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p))),
              attr='setter',
              ctx=(ast.Load()),
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p))))
        else:
            func.decorator_list.append(ast.Name(id='property',
              ctx=(ast.Load()),
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p))))
        return func

    @pg_.production('operator : OPERATOR binop ( param , param ) block')
    def operator_setitem(self, p):
        if p[1] != '__getitem__':
            raise SyntaxError(message='param number mismatched for the operator',
              filename=(self.filename_),
              lineno=(self.getlineno(p[1])),
              colno=(self.getcolno(p[1])),
              source=(self.source_))
        args = self.param_list()
        args.args += [p[3], p[5]]
        args.args.insert(0, ast.arg(arg='self',
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p))))
        return ast.FunctionDef(name='__setitem__',
          args=args,
          body=(p[(-1)]),
          decorator_list=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('operator : OPERATOR binop op_arg block')
    @pg_.production('operator : OPERATOR uop op_none block')
    @pg_.production('operator : OPERATOR - op_none block')
    def operator(self, p):
        if isinstance(p[1], Token):
            p[1] = '__neg__'
        return ast.FunctionDef(name=(p[1]),
          args=(p[2]),
          body=(p[(-1)]),
          decorator_list=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('op_arg : ( param )')
    @pg_.production('op_arg : param')
    @pg_.production('op_none : ( )')
    @pg_.production('op_none : ')
    def op_arg(self, p):
        args = self.param_list()
        args.args.append(ast.arg(arg='self',
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p))))
        [args.args.append(arg) for arg in p if isinstance(arg, ast.arg)]
        return args

    @pg_.production('binop : [ ]')
    def bin_getitem(self, p):
        return '__getitem__'

    @pg_.production('binop : <<')
    def bin_lshift(self, p):
        return '__lshift__'

    @pg_.production('binop : <<=')
    def bin_ilshift(self, p):
        return '__ilshift__'

    @pg_.production('binop : >>')
    def bin_rshift(self, p):
        return '__rshift__'

    @pg_.production('binop : >>=')
    def bin_irshift(self, p):
        return '__irshift__'

    @pg_.production('binop : +')
    def binop_add(self, p):
        return '__add__'

    @pg_.production('binop : +=')
    def binop_iadd(self, p):
        return '__iadd__'

    @pg_.production('binop : -')
    def binop_add(self, p):
        return '__sub__'

    @pg_.production('binop : -=')
    def binop_isub(self, p):
        return '__isub__'

    @pg_.production('binop : *')
    def binop_mult(self, p):
        return '__mul__'

    @pg_.production('binop : *=')
    def binop_imult(self, p):
        return '__imul__'

    @pg_.production('binop : /')
    def binop_div(self, p):
        return '__truediv__'

    @pg_.production('binop : /=')
    def binop_idiv(self, p):
        return '__idiv__'

    @pg_.production('binop : %')
    def binop_mod(self, p):
        return '__mod__'

    @pg_.production('binop : %=')
    def binop_mod(self, p):
        return '__imod__'

    @pg_.production('binop : ^')
    def binop_pow(self, p):
        return '__pow__'

    @pg_.production('binop : ^=')
    def binop_ipow(self, p):
        return '__ipow__'

    @pg_.production('binop : >')
    def binop_gt(self, p):
        return '__gt__'

    @pg_.production('binop : >=')
    def binop_ge(self, p):
        return '__ge__'

    @pg_.production('binop : <')
    def binop_lt(self, p):
        return '__lt__'

    @pg_.production('binop : <=')
    def binop_le(self, p):
        return '__le__'

    @pg_.production('binop : ==')
    def binop_eq(self, p):
        return '__eq__'

    @pg_.production('binop : !=')
    def binop_ne(self, p):
        return '__ne__'

    @pg_.production('uop : !')
    def uop_neg(self, p):
        return '__not__'

    @pg_.production('uop : ~')
    def uop_invert(self, p):
        return '__invert__'

    @pg_.production('uop : #')
    def uop_len(self, p):
        return '__len__'

    @pg_.production('stmt : using_stmt')
    @pg_.production('stmt : expr_stmt')
    @pg_.production('stmt : assignment')
    @pg_.production('stmt : aug_assign')
    @pg_.production('stmt : anno_assign')
    @pg_.production('stmt : break_stmt')
    @pg_.production('stmt : continue_stmt')
    @pg_.production('stmt : try_stmt')
    @pg_.production('stmt : throw_stmt')
    @pg_.production('stmt : ret_stmt')
    def stmt(self, p):
        return p[0]

    @pg_.production('throw_stmt : THROW expr')
    def throw_stmt(self, p):
        return ast.Raise(exc=(p[1]),
          cause=None,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('withitem : prefix_exprs = expr')
    @pg_.production('withitem : prefix_expr = expr')
    @pg_.production('withitem : expr')
    def withitem(self, p):
        item = ast.withitem(context_expr=(p[(-1)]),
          optional_vars=None,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        if len(p) == 3:
            if isinstance(p[0], list):
                item.optional_vars = ast.Tuple(elts=(p[0]),
                  ctx=(ast.Store()),
                  lineno=(self.getlineno(p[0])),
                  col_offset=(self.getcolno(p[0])))
            else:
                p[0].ctx = ast.Store()
                item.optional_vars = p[0]
        return item

    @pg_.production('try_stmt : TRY withitem block')
    def with_stmt(self, p):
        return ast.With(items=[
         p[1]],
          body=(p[2]),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('try_stmt : TRY withitem block catch_stmts')
    @pg_.production('try_stmt : TRY withitem block catch_stmts final_stmt')
    @pg_.production('try_stmt : TRY withitem block final_stmt')
    def with_stmt_(self, p):
        withstmt = self.with_stmt(p[:3])
        trystmt = ast.Try(body=(withstmt.body),
          handlers=[],
          orelse=[],
          finalbody=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        withstmt.body = [
         trystmt]
        if isinstance(p[3][0], ast.ExceptHandler):
            trystmt.handlers = p[3]
        if not isinstance(p[(-1)][0], ast.ExceptHandler):
            trystmt.finalbody = p[(-1)]
        return withstmt

    @pg_.production('try_stmt : TRY block catch_stmts')
    def try_stmt(self, p):
        return ast.Try(body=(p[1]),
          handlers=(p[(-1)]),
          orelse=[],
          finalbody=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('try_stmt : TRY block catch_stmts final_stmt')
    @pg_.production('try_stmt : TRY block final_stmt')
    def try_stmt_with_final(self, p):
        try_stmt = self.try_stmt(p[:-1])
        try_stmt.finalbody = p[(-1)]
        return try_stmt

    @pg_.production('catch_stmts : catch_stmt')
    @pg_.production('catch_stmts : catch_stmts catch_stmt')
    def catch_stmts(self, p):
        if len(p) == 1:
            return [
             p[0]]
        p[0].append(p[1])
        return p[0]

    @pg_.production('catch_stmt : CATCH name : expr block')
    @pg_.production('catch_stmt : CATCH name block')
    @pg_.production('catch_stmt : CATCH block')
    def catch_stmt(self, p):
        name, ty = (None, None)
        if len(p) == 3:
            name = p[1].id
        else:
            if len(p) == 5:
                name = p[1].id
                ty = p[3]
        return ast.ExceptHandler(type=ty,
          name=name,
          body=(p[(-1)]),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('final_stmt : FINALLY block')
    def final_stmt(self, p):
        return p[(-1)]

    @pg_.production('module_name_ : module_name')
    @pg_.production('module_name_ : DOTDOT')
    @pg_.production('module_name_ : DOT')
    def module_name_(self, p):
        return p[0]

    @pg_.production('using_stmt : USING module_names IN module_name_')
    @pg_.production('using_stmt : USING * IN module_name_')
    def import_from(self, p):
        module, level = p[(-1)], 0
        if isinstance(p[(-1)], Token):
            module = None
            level = 1 if p[(-1)].getstr() == '.' else 2
        else:
            node = ast.ImportFrom(module=module,
              names=[],
              level=level,
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p)))
            if isinstance(p[1], list):
                node.names += p[1]
            else:
                node.names.append(ast.alias(name='*',
                  asname=None,
                  lineno=(self.getlineno(p[1])),
                  col_offset=(self.getcolno(p[1]))))
        return node

    @pg_.production('using_stmt : USING module_names')
    def import_stmt(self, p):
        return ast.Import(names=(p[1]),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('module_names : module_name')
    @pg_.production('module_names : module_names , module_name')
    def module_names(self, p):
        alias = ast.alias(name=(p[(-1)]),
          asname=None,
          lineno=(self.getlineno(p[(-1)])),
          col_offset=(self.getcolno(p[(-1)])))
        if len(p) == 1:
            return [
             alias]
        p[0].append(alias)
        return p[0]

    @pg_.production('module_name : module_name DOT name')
    @pg_.production('module_name : name')
    def module_name(self, p):
        if len(p) == 1:
            return p[0].id
        return '%s.%s' % (p[0], p[2].id)

    @pg_.production('expr_stmt : prefix_expr')
    @pg_.production('expr_stmt : yield_expr')
    def expr_stmt(self, p):
        if not isinstance(p[0], ast.Call):
            if not isinstance(p[0], ast.Yield):
                if not isinstance(p[0], ast.Str):
                    p[0] = ast.Call(func=(p[0]),
                      args=[],
                      keywords=[],
                      starargs=None,
                      kwargs=None,
                      lineno=(self.getlineno(p)),
                      col_offset=(self.getcolno(p)))
        return ast.Expr(value=(p[0]),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('ret_stmt : RETURN')
    @pg_.production('ret_stmt : RETURN exprs')
    def ret_stmt(self, p):
        value = None
        if len(p) == 2:
            if len(p[1]) == 1:
                value = p[1][0]
            else:
                value = ast.Tuple(elts=(p[1]),
                  ctx=(ast.Load()),
                  lineno=(self.getlineno(p[1])),
                  col_offset=(self.getcolno(p[1])))
        return ast.Return(value=value,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('aug_assign : prefix_expr += expr')
    @pg_.production('aug_assign : prefix_expr -= expr')
    @pg_.production('aug_assign : prefix_expr *= expr')
    @pg_.production('aug_assign : prefix_expr ^= expr')
    @pg_.production('aug_assign : prefix_expr |= expr')
    @pg_.production('aug_assign : prefix_expr &= expr')
    @pg_.production('aug_assign : prefix_expr <<= expr')
    @pg_.production('aug_assign : prefix_expr >>= expr')
    def aug_assign(self, p):
        operator = p[1].getstr()
        if operator == '+=':
            operator = ast.Add()
        else:
            if operator == '-=':
                operator = ast.Sub()
            else:
                if operator == '*=':
                    operator = ast.Mult()
                else:
                    if operator == '|=':
                        operator = ast.BitOr()
                    else:
                        if operator == '&=':
                            operator = ast.BitAnd()
                        else:
                            if operator == '<<=':
                                operator = ast.LShift()
                            else:
                                if operator == '>>=':
                                    operator = ast.RShift()
                                else:
                                    operator = ast.Pow()
        p[0].ctx = ast.Store()
        return ast.AugAssign((p[0]),
          operator, (p[2]), lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('aug_assign : prefix_expr /= expr')
    @pg_.production('aug_assign : prefix_expr %= expr')
    def divrem_aug_assign(self, p):
        operator = '__div__' if p[1].getstr() == '/=' else '__rem__'
        call = ast.Call(func=ast.Name(id=operator,
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p))),
          args=[
         p[0], p[2]],
          keywords=[],
          starargs=None,
          kwargs=None,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        target = deepcopy(p[0])
        target.ctx = ast.Store()
        return ast.Assign(targets=[
         target],
          value=call,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('assignment : prefix_expr = expr')
    def assignment(self, p):
        p[0].ctx = ast.Store()
        p[2] = self.convert_to_tuple(p[2])
        return ast.Assign([
         p[0]],
          (p[2]), lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('anno_assign : name : type_name = expr')
    def anno_assign(self, p):
        p[0].ctx = ast.Store()
        return ast.AnnAssign(target=(p[0]),
          annotation=(p[2]),
          value=(p[(-1)]),
          simple=1,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('declaration : EXTERN names')
    def declaration(self, p):
        return ast.Global([name.id for name in p[1]],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('prefix_exprs : prefix_exprs , prefix_expr')
    @pg_.production('prefix_exprs : prefix_expr , prefix_expr')
    def prefix_exprs(self, p):
        if isinstance(p[0], list):
            p[0].append(p[2])
            return p[0]
        return [p[0], p[2]]

    @pg_.production('assignment : prefix_exprs = exprs')
    def tuple_assignment(self, p):
        for pe in p[0]:
            pe.ctx = ast.Store()

        lhs = ast.Tuple(elts=(p[0]),
          ctx=(ast.Store()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        if len(p[2]) > 1:
            rhs = ast.Tuple(elts=(p[2]),
              ctx=(ast.Load()),
              lineno=(self.getlineno(p[2])),
              col_offset=(self.getcolno(p[2])))
        else:
            rhs = p[2][0]
        return ast.Assign(targets=[
         lhs],
          value=rhs,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('break_stmt : BREAK')
    def break_stmt(self, p):
        return ast.Break(lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('continue_stmt : CONTINUE')
    def continue_stmt(self, p):
        return ast.Continue(lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('bin_expr : expr + expr')
    @pg_.production('bin_expr : expr - expr')
    @pg_.production('bin_expr : expr * expr')
    @pg_.production('bin_expr : expr >> expr')
    @pg_.production('bin_expr : expr << expr')
    @pg_.production('bin_expr : expr ^ expr')
    @pg_.production('bin_expr : expr & expr')
    @pg_.production('bin_expr : expr | expr')
    def bin_expr(self, p):
        operator = p[1].getstr()
        if operator == '+':
            operator = ast.Add()
        else:
            if operator == '-':
                operator = ast.Sub()
            else:
                if operator == '*':
                    operator = ast.Mult()
                else:
                    if operator == '<<':
                        operator = ast.LShift()
                    else:
                        if operator == '>>':
                            operator = ast.RShift()
                        else:
                            if operator == '&':
                                operator = ast.BitAnd()
                            else:
                                if operator == '|':
                                    operator = ast.BitOr()
                                else:
                                    operator = ast.Pow()
        return ast.BinOp((p[0]),
          operator, (p[2]), lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('bin_expr : expr / expr')
    @pg_.production('bin_expr : expr % expr')
    def divrem_expr(self, p):
        operator = '__div__' if p[1].getstr() == '/' else '__rem__'
        return ast.Call(func=ast.Name(id=operator,
          ctx=(ast.Load()),
          starargs=None,
          kwargs=None,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p))),
          args=[
         p[0], p[2]],
          keywords=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('bin_expr : expr > expr')
    @pg_.production('bin_expr : expr >= expr')
    @pg_.production('bin_expr : expr < expr')
    @pg_.production('bin_expr : expr <= expr')
    @pg_.production('bin_expr : expr == expr')
    @pg_.production('bin_expr : expr != expr')
    @pg_.production('bin_expr : expr === expr')
    @pg_.production('bin_expr : expr !== expr')
    def compare_expr(self, p):
        operator = p[1].getstr()
        if operator == '>':
            operator = ast.Gt()
        else:
            if operator == '>=':
                operator = ast.GtE()
            else:
                if operator == '<':
                    operator = ast.Lt()
                else:
                    if operator == '<=':
                        operator = ast.LtE()
                    else:
                        if operator == '==':
                            operator = ast.Eq()
                        else:
                            if operator == '!=':
                                operator = ast.NotEq()
                            else:
                                if operator == '===':
                                    operator = ast.Is()
                                else:
                                    operator = ast.IsNot()
        return ast.Compare((p[0]),
          [operator], [p[2]], lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('bin_expr : expr AND expr')
    @pg_.production('bin_expr : expr OR expr')
    def bool_expr(self, p):
        if p[1].getstr() == 'and':
            return ast.BoolOp(op=(ast.And()),
              values=[
             p[0], p[2]],
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p)))
        return ast.BoolOp(op=(ast.Or()),
          values=[
         p[0], p[2]],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('range_expr : expr DOTDOT expr')
    @pg_.production('range_expr : expr DOTDOTLT expr')
    @pg_.production('range_expr : range_expr BY expr')
    def range_expr_(self, p):
        op = p[1].getstr()
        if op != 'by':
            start = p[0]
            end = p[2]
            if op == '..':
                end = ast.BinOp(end,
                  (ast.Add()),
                  ast.Num(1,
                  lineno=(self.getlineno(p[2])),
                  col_offset=(self.getcolno(p[2]))),
                  lineno=(self.getlineno(p[2])),
                  col_offset=(self.getcolno(p[2])))
                end.fixed = True
            return ast.Call(func=ast.Name(id='range',
              ctx=(ast.Load()),
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p))),
              args=[
             start, end],
              keywords=[],
              starargs=None,
              kwargs=None,
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p)))
        assert isinstance(p[0], ast.Call)
        args = p[0].args
        if len(args) == 3:
            raise SyntaxError(message=('unexpected token "%s"' % p[1].getstr()),
              filename=(self.filename_),
              lineno=(self.getlineno(p[1])),
              colno=(self.getcolno(p[1])),
              source=(self.source_))
        else:
            args.append(p[2])
            end = args[1]
            if hasattr(end, 'fixed'):
                if isinstance(p[2], ast.Num):
                    if p[2].n < 0:
                        end.op = ast.Sub()
                else:
                    inc = ast.IfExp(test=ast.Compare(left=(p[2]),
                      ops=[
                     ast.Gt()],
                      comparators=[
                     ast.Num(0, lineno=(self.getlineno(p[2])),
                       col_offset=(self.getcolno(p[2])))],
                      lineno=(self.getlineno(p[2])),
                      col_offset=(self.getcolno(p[2]))),
                      body=(end.right),
                      orelse=ast.Num((-1),
                      lineno=(self.getlineno(p[2])),
                      col_offset=(self.getcolno(p[2]))),
                      lineno=(self.getlineno(p)),
                      col_offset=(self.getcolno(p)))
                    end.right = inc
                delattr(end, 'fixed')
            return p[0]

    @pg_.production('unary_expr : - expr', precedence='!')
    @pg_.production('unary_expr : ! expr', precedence='!')
    @pg_.production('unary_expr : # expr', precedence='!')
    @pg_.production('unary_expr : ~ expr', precedence='!')
    def unary_expr(self, p):
        operator = p[0].getstr()
        if operator == '-':
            operator = ast.USub()
        else:
            if operator == '!':
                operator = ast.Not()
            else:
                if operator == '~':
                    operator = ast.Invert()
                else:
                    return ast.Call(func=ast.Name('len',
                      ctx=(ast.Load()), lineno=(self.getlineno(p)),
                      col_offset=(self.getcolno(p))),
                      args=[
                     p[1]],
                      keywords=[],
                      starargs=None,
                      kwargs=None,
                      lineno=(self.getlineno(p)),
                      col_offset=(self.getcolno(p)))
        return ast.UnaryOp(operator,
          (p[1]), lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('ternary_expr : expr ? expr : expr')
    def ternary_expr(self, p):
        return ast.IfExp(test=(p[0]),
          body=(p[2]),
          orelse=(p[(-1)]),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('primary_expr : ( expr )')
    def primary_expr(self, p):
        return p[1]

    @pg_.production('primary_expr : ( name : type_name )')
    @pg_.production('primary_expr : ( name : type_name , param_list_not_empty )')
    @pg_.production('primary_expr : ( name , param_list_not_empty )')
    def primary_expr_(self, p):
        args = ast.arguments(args=[], kwonlyargs=[], kw_defaults=[], defaults=[], vararg=None,
          kwarg=None,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        if len(p) == 2:
            return args
        arg0 = ast.arg(arg=(p[1].id),
          lineno=(self.getlineno(p[1])),
          col_offset=(self.getcolno(p[1])))
        args.args = [
         arg0]
        if p[2].getstr() == ':':
            arg0.annotation = p[3]
        if p[(-3)].getstr() == ',':
            args.args += p[(-2)].args
            args.vararg = p[(-2)].vararg
        return self.legalize_arguments(args)

    @pg_.production('prefix_expr : call')
    @pg_.production('prefix_expr : var')
    @pg_.production('prefix_expr : lambda_func')
    @pg_.production('prefix_expr : strlit')
    @pg_.production('prefix_expr : list_expr')
    @pg_.production('prefix_expr : dict_expr')
    def prefix_expr(self, p):
        return p[0]

    @pg_.production('slice : expr')
    def slice_index(self, p):
        return ast.Index(value=(p[0]),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('slice : expr : expr ')
    @pg_.production('slice : expr : ')
    @pg_.production('slice : : expr')
    @pg_.production('slice : : ')
    def slice_presentation(self, p):
        lower, upper = p[0], p[(-1)]
        if isinstance(lower, Token):
            lower = None
        if isinstance(upper, Token):
            upper = None
        return ast.Slice(lower=lower,
          upper=upper,
          step=None,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('slice : exprs , expr')
    def slice_indeces(self, p):
        p[0].append(p[2])
        return ast.ExtSlice(dims=[self.slice_index([e]) for e in p[0]],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('var : prefix_expr [ slice ]')
    def slice_expr(self, p):
        return ast.Subscript(value=(p[0]),
          slice=(p[2]),
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('var : prefix_expr DOT name')
    def attribute_expr(self, p):
        return ast.Attribute(value=(p[0]),
          attr=(p[2].id),
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('var : name')
    def var_expr(self, p):
        return p[0]

    @pg_.production('arguments : ( args )')
    @pg_.production('arguments : ( )')
    def arguments(self, p):
        if len(p) != 3:
            return []
        return p[1]

    @pg_.production('call : prefix_expr arguments')
    def call(self, p):
        args = []
        keywords = []
        for v, k in p[1]:
            if k is None:
                args.append(v)
            else:
                keywords.append(ast.keyword(arg=k,
                  value=v))

        return ast.Call(func=(p[0]),
          args=args,
          keywords=keywords,
          starargs=None,
          kwargs=None,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('call : super')
    @pg_.production('call : prefix_expr DOT super')
    def call_super(self, p):
        if len(p) == 1:
            return p[0]
        attr = ast.Attribute(value=(p[0]),
          attr='super',
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        p[2].func = attr
        return p[2]

    @pg_.production('super : SUPER arguments')
    @pg_.production('super : SUPER')
    def super_(self, p):
        np = [
         ast.Name(id='super',
           ctx=(ast.Load()),
           lineno=(self.getlineno(p[0])),
           col_offset=(self.getcolno(p[0])))]
        if len(p) == 2:
            np.append(p[1] if len(p[1]) > 0 else [(None, None)])
        else:
            np.append([])
        return self.call(np)

    @pg_.production('lambda_param : name')
    @pg_.production('lambda_param : varargs_expr')
    @pg_.production('lambda_param : primary_expr')
    @pg_.production('lambda_param : ( )')
    def lambda_param(self, p):
        if isinstance(p[0], ast.Starred):
            p[0] = p[0].value
        if isinstance(p[0], ast.Name):
            args = ast.arguments(args=[], kwonlyargs=[], kw_defaults=[], defaults=[], vararg=None,
              kwarg=None,
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p)))
            arg = ast.arg(arg=(p[0].id),
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p)))
            if p[0].id != '__varargs__':
                args.args = [
                 arg]
            else:
                args.vararg = arg
            return args
        if isinstance(p[0], ast.arguments):
            return p[0]
        if len(p) == 2:
            return self.primary_expr_(p)
        raise SyntaxError(message='expect an identifier here',
          filename=(self.filename_),
          lineno=(self.getlineno(p)),
          colno=(self.getcolno(p)),
          source=(self.source_))

    @pg_.production('lambda_body : -> expr')
    @pg_.production('lambda_body : -> block')
    def lambda_body(self, p):
        return p[1]

    @pg_.production('lambda_expr : lambda_param lambda_body')
    def lambda_expr(self, p):
        if len(p) == 1:
            return p[0]
        if isinstance(p[(-1)], ast.expr):
            return ast.Lambda(args=(p[0]),
              body=(p[(-1)]),
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p)))
        return self.create_anon_func(p, p[0], p[(-1)])

    @pg_.production('lambda_func : FUNC ( param_list ) block')
    @pg_.production('lambda_func : FUNC block')
    def lambda_func(self, p):
        args = p[2] if len(p) == 5 else []
        return self.create_anon_func(p, args, p[(-1)])

    @pg_.production('lambda_func : FUNC ( param_list ) : type_name block')
    def lambda_func_with_type(self, p):
        args, body, returns = p[2], p[(-1)], p[(-2)]
        return self.create_anon_func(p, args, body, returns)

    @pg_.production('type_name : name')
    @pg_.production('type_name : type_name [ type_list ]')
    def type_name(self, p):
        return p[0]

    @pg_.production('type_list : type_name')
    @pg_.production('type_list : type_list , type_name')
    def type_list(self, p):
        if len(p) == 1:
            return [
             p[0]]
        p[0].append(p[2])
        return p[0]

    def create_anon_func(self, p, args, body, returns=None):
        func_name = ast.Name(id=(randomString()),
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        func = ast.FunctionDef(name=(func_name.id),
          args=args,
          body=body,
          decorator_list=[],
          returns=returns,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        self.anonfuncs_[func_name] = func
        return func_name

    @pg_.production('number : HEX_LITERAL')
    @pg_.production('number : INTEGER_LITERAL')
    @pg_.production('number : FLOAT_LITERAL')
    def number(self, p):
        try:
            return ast.Num((int(p[0].getstr(), 0)),
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p)))
        except ValueError:
            return ast.Num((float(p[0].getstr())),
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p)))

    @pg_.production('strlit : STRING_LITERAL')
    @pg_.production('strlit : STRING_LITERAL_II')
    def strlit(self, p):
        string = p[0].getstr()
        if string.startswith('"'):
            string = string.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\(', '(').replace('\\\\)', ')').replace('\\\\', '\\').replace('\\"', '"')
        else:
            string = string.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\(', '(').replace('\\\\)', ')').replace('\\\\', '\\').replace("\\'", "'")
        string = string[1:-1]
        ret = self.parse_format_str(string, p)
        if ret is not None:
            return ret
        return ast.Str(string,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    def parse_format_str(self, string, p):
        import re
        pattern = re.compile('\\\\\\(([^\\\\\\)]*)\\\\\\)|\\`([^\\`]*)\\`')
        format_string = string
        exprs = []
        pos = 0
        while True:
            match = pattern.search(string=string,
              pos=pos)
            if match is None:
                break
            pos = match.span()[1]
            expr = match.group(1)
            if expr is None:
                expr = match.group(2)
            submo = Parser().parse('str(%s)' % expr)
            exprs.append(submo.body[0].value)
            format_string = format_string.replace(match.group(0), '%s')

        if len(exprs) == 0:
            return
        return ast.BinOp(left=ast.Str(s=format_string,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p))),
          op=(ast.Mod()),
          right=ast.Tuple(elts=exprs,
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p))),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('name_const : TRUE')
    def const_true(self, p):
        return ast.NameConstant(value=True,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('name_const : FALSE')
    def const_false(self, p):
        return ast.NameConstant(value=False,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('name_const : NIL')
    def const_nil(self, p):
        return ast.NameConstant(value=None,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('name_const : DOLLAR')
    def dollar(self, p):
        return ast.Name(id='self',
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('expr : factor_expr')
    @pg_.production('expr : yield_expr')
    @pg_.production('expr : bin_expr')
    @pg_.production('expr : unary_expr')
    @pg_.production('expr : prefix_expr')
    @pg_.production('expr : primary_expr')
    @pg_.production('expr : lambda_expr')
    @pg_.production('expr : ternary_expr')
    @pg_.production('expr : number', precedence='==')
    @pg_.production('expr : name_const')
    @pg_.production('expr : range_expr', precedence='==')
    def expr(self, p):
        p=p[0]
        if isinstance(p,ast.Call):
            p.__dict__.setdefault('starargs')
            p.__dict__.setdefault('kwargs')
        return p

    @pg_.production('expr : varargs_expr')
    def varargs_expr(self, p):
        return ast.Starred(value=(p[0]),
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('varargs_expr : DOTDOTDOT')
    def varargs(self, p):
        return ast.Name(id='__varargs__',
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('factor_expr : number prefix_expr')
    @pg_.production('factor_expr : number primary_expr')
    def factor_expr(self, p):
        p[1] = self.convert_to_tuple(p[1])
        return ast.BinOp((p[0]),
          (ast.Mult()), (p[1]), lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('yield_expr : YIELD expr')
    @pg_.production('yield_expr : YIELD')
    def yield_expr(self, p):
        value = p[1] if len(p) == 2 else None
        return ast.Yield(value=value,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('dict_expr : LBRACE : RBRACE')
    @pg_.production('dict_expr : LBRACE kv_pairs RBRACE')
    def dict_expr(self, p):
        keys = []
        values = []
        if isinstance(p[1], list):
            keys = [pair[0] for pair in p[1]]
            values = [pair[1] for pair in p[1]]
        return ast.Dict(keys=keys,
          values=values,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('kv_pairs : kv_pair')
    @pg_.production('kv_pairs : kv_pairs , kv_pair')
    def kv_pairs(self, p):
        if len(p) < 3:
            return [
             p[0]]
        p[0].append(p[(-1)])
        return p[0]

    @pg_.production('kv_pair : expr : expr')
    def kv_pair(self, p):
        return (p[(-3)], p[(-1)])

    @pg_.production('list_expr : [ ]')
    @pg_.production('list_expr : [ exprs ]')
    def list_expr(self, p):
        elts = p[1] if len(p) == 3 else []
        return ast.List(elts=elts,
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('names : name')
    @pg_.production('names : names , name')
    @pg_.production('args : arg')
    @pg_.production('args : args , arg')
    @pg_.production('exprs : expr')
    @pg_.production('exprs : exprs , expr')
    def exprs(self, p):
        if len(p) == 3:
            p[0].append(p[2])
            return p[0]
        return [p[0]]

    @pg_.production('arg : expr')
    @pg_.production('arg : IDENTIFIER = expr')
    def arg(self, p):
        if len(p) == 1:
            return (
             p[0], None)
        return (p[(-1)], p[0].getstr())

    @pg_.production('param_list : ')
    @pg_.production('param_list : param_list_not_empty')
    def param_list(self, p=[]):
        if not p:
            return ast.arguments(args=[], kwonlyargs=[], kw_defaults=[], defaults=[], vararg=None,
              kwarg=None)
        return self.legalize_arguments(p[0])

    @pg_.production('param_list_not_empty : param')
    @pg_.production('param_list_not_empty : param_list_not_empty , param')
    def param_list_not_empty(self, p):
        if len(p) == 1:
            args = self.param_list()
        else:
            args = p[0]
        args.args.append(p[(-1)])
        return args

    @pg_.production('param_list_not_empty : DOTDOTDOT')
    @pg_.production('param_list_not_empty : param_list_not_empty , DOTDOTDOT')
    def param_list_with_varargs(self, p):
        args = p[0] if len(p) == 3 else self.param_list()
        args.vararg = ast.arg(arg='__varargs__',
          annotation=None,
          lineno=(self.getlineno(p[(-1)])),
          col_offset=(self.getcolno(p[(-1)])))
        return args

    @pg_.production('param : name : type_name')
    @pg_.production('param : name')
    def param(self, p):
        return ast.arg(arg=(p[0].id),
          annotation=(None if len(p) == 1 else p[(-1)]),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('param : name = expr')
    def param_with_init(self, p):
        arg = self.param(p[:1])
        arg.default = p[2]
        return arg

    @pg_.production('function : FUNC IDENTIFIER ( param_list ) block')
    @pg_.production('function : FUNC IDENTIFIER block')
    def function(self, p):
        return ast.FunctionDef(name=(p[1].getstr()),
          args=(p[3] if len(p) == 6 else self.param_list()),
          body=(p[(-1)]),
          decorator_list=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('function : FUNC IDENTIFIER ( param_list ) : type_name block')
    @pg_.production('function : FUNC IDENTIFIER : type_name block')
    def function_with_type(self, p):
        return ast.FunctionDef(name=(p[1].getstr()),
          args=(p[3] if len(p) == 8 else self.param_list()),
          body=(p[(-1)]),
          returns=(p[(-2)]),
          decorator_list=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('if_stmt : IF expr block elif_stmt')
    @pg_.production('if_stmt : IF expr block ELSE block')
    @pg_.production('elif_stmt : ')
    @pg_.production('elif_stmt : ELIF expr block elif_stmt')
    @pg_.production('elif_stmt : ELIF expr block ELSE block')
    def if_stmt(self, p):
        if len(p) == 0:
            return []
        else:
            if len(p) == 5:
                return ast.If(test=(p[1]),
                  body=(p[2]),
                  orelse=(p[(-1)]),
                  lineno=(self.getlineno(p)),
                  col_offset=(self.getcolno(p)))
            p[-1] = p[-1] if isinstance(p[(-1)], list) else [p[(-1)]]
        return ast.If(test=(p[1]),
          body=(p[2]),
          orelse=(p[(-1)]),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('if_stmt : stmt IF expr')
    def single_if(self, p):
        return ast.If(test=(p[(-1)]),
          body=[
         p[0]],
          orelse=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('stmt : block')
    def single_block(self, p):
        return ast.If(test=ast.NameConstant(value=True,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p))),
          body=(p[0]),
          orelse=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('while_stmt : WHILE expr block')
    def while_stmt(self, p):
        return ast.While(test=(p[1]),
          body=(p[2]),
          orelse=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('while_stmt : LOOP block')
    def loop_stmt(self, p):
        return ast.While(test=ast.NameConstant(value=True,
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p))),
          body=(p[1]),
          orelse=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('iterator : prefix_expr')
    @pg_.production('iterator : prefix_exprs')
    def iterator(self, p):
        return p[0]

    @pg_.production('loop_range : expr')
    def loop_range(self, p):
        p[0] = self.convert_to_tuple(p[0])
        if isinstance(p[0], ast.Starred):
            p[0] = p[0].value
        return p[0]

    @pg_.production('for_stmt : FOR iterator IN loop_range block')
    @pg_.production('for_stmt : FOR iterator : loop_range block')
    def for_stmt(self, p):
        target = p[1]
        if isinstance(target, list):
            for e in target:
                if hasattr(e, 'ctx'):
                    e.ctx = ast.Store()

            target = ast.Tuple(elts=target,
              ctx=(ast.Store()),
              lineno=(self.getlineno(p)),
              col_offset=(self.getcolno(p)))
        else:
            target.ctx = ast.Store()
        return ast.For(target=target,
          iter=(p[3]),
          body=(p[4]),
          orelse=[],
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.production('for_stmt : stmt FOR iterator IN loop_range')
    @pg_.production('for_stmt : stmt FOR iterator : loop_range')
    def single_for_stmt(self, p):
        np = p[1:]
        np.append([p[0]])
        return self.for_stmt(np)

    @pg_.production('name : IDENTIFIER')
    def identifier(self, p):
        id = p[0].getstr()
        name = ast.Name(id=id,
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))
        if not id.startswith('$'):
            return name
        name.id = 'self'
        return ast.Attribute(value=name,
          attr=(id.replace('$', '')),
          ctx=(ast.Load()),
          lineno=(self.getlineno(p)),
          col_offset=(self.getcolno(p)))

    @pg_.error
    def error_handler(self, token):
        if token.getstr() == '\n':
            return
        raise SyntaxError(message=('unexpected token "%s"' % token.gettokentype()),
          filename=(self.filename_),
          lineno=(self.getlineno(token)),
          colno=(self.getcolno(token)),
          source=(self.source_))

    def legalize_arguments(self, arguments):
        hasDefaults = False
        for arg in arguments.args:
            if hasattr(arg, 'default'):
                if arg.default:
                    hasDefaults = True
                    arguments.defaults.append(arg.default)
            if hasDefaults:
                raise SyntaxError(message='no default expr is provided here',
                  filename=(self.filename_),
                  lineno=(arg.lineno),
                  colno=(arg.col_offset),
                  source=(self.source_))

        return arguments

    def convert_to_tuple(self, args):
        if not isinstance(args, ast.arguments):
            return args
        return ast.Tuple(ctx=(ast.Load()),
          elts=[ast.Name((arg.arg), (ast.Load()), lineno=(arg.lineno), col_offset=(arg.col_offset)) for arg in args.args],
          lineno=(self.getlineno(args)),
          col_offset=(self.getcolno(args)))

    parser_ = LRParser(pg_.build())
    if len(parser_.lr_table.rr_conflicts) > 0:
        print(parser_.lr_table.rr_conflicts)
    if len(parser_.lr_table.sr_conflicts) > 0:
        print(parser_.lr_table.sr_conflicts)
# okay decompiling E:\ulang\ulang-0.2.2.exe_extracted\PYZ-00.pyz_extracted\ulang.parser.core.pyc
