# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.2rc1 (tags/v3.7.2rc1:75a402a217, Dec 11 2018, 22:09:03) [MSC v.1916 32 bit (Intel)]
# Embedded file name: ulang\parser\lexer.py
from rply import LexerGenerator
import rply, re
RULES = [
 'FLOAT_LITERAL',
 'INTEGER_LITERAL',
 'HEX_LITERAL',
 'STRING_LITERAL',
 'STRING_LITERAL_II',
 'LBRACE',
 'RBRACE',
 'NIL',
 'TRUE',
 'FALSE',
 'AND',
 'OR',
 'IF',
 'ELIF',
 'ELSE',
 'WHILE',
 'LOOP',
 'FOR',
 'BREAK',
 'CONTINUE',
 'RETURN',
 'FUNC',
 'TYPE',
 'USING',
 'IN',
 'TRY',
 'CATCH',
 'FINALLY',
 'THROW',
 'YIELD',
 'IDENTIFIER',
 'DOT',
 'DOTDOT',
 'DOTDOTDOT',
 'DOTDOTLT',
 'OPERATOR',
 'DOLLAR',
 'NEWLINE',
 'BY',
 'EXTERN',
 'ATTR',
 'SUPER',
 '[',
 ']',
 '(',
 ')',
 '===',
 '!==',
 '==',
 '=',
 '!=',
 '->',
 '>',
 '<',
 '>=',
 '<=',
 '+',
 '-',
 '*',
 '/',
 '%',
 '+=',
 '-=',
 '*=',
 '/=',
 '%=',
 '^=',
 '^',
 ',',
 ';',
 '#',
 '!',
 '?',
 ':',
 '>>',
 '<<',
 '>>=',
 '<<=',
 '|=',
 '&=',
 '~',
 '|',
 '&']
lg = LexerGenerator()
lg.add('HEX_LITERAL', '0[xX][0-9A-Fa-f]+')
lg.add('FLOAT_LITERAL', '\\d+\\.\\d+')
lg.add('INTEGER_LITERAL', '\\d+')
lg.add('STRING_LITERAL', '(\\")((?<!\\\\)\\\\\\1|.)*?\\1')
lg.add('STRING_LITERAL_II', "(\\')((?<!\\\\)\\\\\\1|.)*?\\1")
lg.add('LBRACE', '{\\r*\\n*', flags=(re.DOTALL))
lg.add('RBRACE', '\\r*\\n*}', flags=(re.DOTALL))
lg.add('NIL', '\\bnil\\b')
lg.add('TRUE', '\\btrue\\b')
lg.add('FALSE', '\\bfalse\\b')
lg.add('AND', '\\band\\b')
lg.add('OR', '\\bor\\b')
lg.add('XOR', '\\bxor\\b')
lg.add('IF', '\\bif\\b')
lg.add('ELIF', '\\r*\\n*\\s*elif\\s*\\r*\\n*', flags=(re.DOTALL))
lg.add('ELSE', '\\r*\\n*\\s*else\\s*\\r*\\n*', flags=(re.DOTALL))
lg.add('WHILE', '\\bwhile\\b')
lg.add('LOOP', '\\bloop\\b')
lg.add('FOR', '\\bfor\\b')
lg.add('RETURN', '\\breturn\\b')
lg.add('BREAK', '\\bbreak\\b')
lg.add('CONTINUE', '\\bcontinue\\b')
lg.add('FUNC', '\\bfunc\\b')
lg.add('TYPE', '\\btype\\b')
lg.add('USING', '\\busing\\b')
lg.add('MODULE', '\\bmodule\\b')
lg.add('IN', '\\bin\\b')
lg.add('TRY', '\\btry\\b')
lg.add('CATCH', '\\r*\\n*\\s*catch\\s*\\r*\\n*', flags=(re.DOTALL))
lg.add('FINALLY', '\\r*\\n*\\s*finally\\s*\\r*\\n*', flags=(re.DOTALL))
lg.add('THROW', '\\bthrow\\b')
lg.add('OPERATOR', '\\boperator\\b')
lg.add('YIELD', '\\byield\\b')
lg.add('BY', '\\bby\\b')
lg.add('EXTERN', '\\bextern\\b')
lg.add('SUPER', '\\bsuper\\b')
lg.add('ATTR', '\\battr\\b')
lg.add('IDENTIFIER', '\\$?[_a-zA-Z][_a-zA-Z0-9]*')
lg.add('DOTDOTDOT', '\\.\\.\\.')
lg.add('DOTDOTLT', '\\.\\.<')
lg.add('DOTDOT', '\\.\\.')
lg.add('DOT', '\\.')
lg.add('DOLLAR', '\\$')
lg.add('[', '\\[')
lg.add(']', '\\]')
lg.add('(', '\\(')
lg.add(')', '\\)')
lg.add('===', '===')
lg.add('!==', '!==')
lg.add('==', '==')
lg.add('!=', '!=')
lg.add('>>=', '>>=')
lg.add('<<=', '<<=')
lg.add('>=', '>=')
lg.add('<=', '<=')
lg.add('>>', '>>')
lg.add('<<', '<<')
lg.add('->', '->')
lg.add('>', '>')
lg.add('<', '<')
lg.add('=', '=')
lg.add(',', ',')
lg.add('+=', '\\+=')
lg.add('-=', '-=')
lg.add('*=', '\\*=')
lg.add('/=', '/=')
lg.add('%=', '%=')
lg.add('^=', '\\^=')
lg.add('|=', '\\|=')
lg.add('&=', '&=')
lg.add('+', '\\+')
lg.add('-', '-')
lg.add('*', '\\*')
lg.add('/', '/')
lg.add('%', '%')
lg.add('^', '\\^')
lg.add(',', ',')
lg.add(';', ';')
lg.add('#', '#')
lg.add('!', '!')
lg.add('?', '\\?')
lg.add(':', ':')
lg.add('~', '~')
lg.add('&', '&')
lg.add('|', '\\|')
lg.add('NEWLINE', '\n')
lg.ignore('^#!.*')
lg.ignore('[ \t\r]+')
lg.ignore('//[^\n]*')
lg.ignore('/\\*.*?\\*/', flags=(re.DOTALL))
lexer = lg.build()
# okay decompiling E:\ulang\ulang-0.2.2.exe_extracted\PYZ-00.pyz_extracted\ulang.parser.lexer.pyc
