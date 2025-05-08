# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.2rc1 (tags/v3.7.2rc1:75a402a217, Dec 11 2018, 22:09:03) [MSC v.1916 32 bit (Intel)]
# Embedded file name: ulang\runtime\repl.py
import sys, cmd
from ulang.parser.core import Parser
from ulang.parser.lexer import lexer
from ulang.runtime.env import create_globals

def is_close(source):
    """
    Check if the given source code is closed,
    which means each '{' has a matched '}' 
    """
    keywords = {
     'FUNC', 'OPERATOR', 'ATTR', 'TYPE',
     'FOR', 'LOOP', 'WHILE',
     'IF', 'ELIF', 'ELSE',
     'TRY', 'CATCH', 'FINALLY'}
    if len(source) > 1:
        if source[(-2)] == '\\':
            return False
    tokens = lexer.lex(source)
    unclosed = []
    unmatched = [
     0, 0, 0]
    last = 2 * ['']
    for tok in tokens:
        c = tok.gettokentype()
        last[0], last[1] = last[1], c
        if c in keywords:
            unclosed.append(c)
        else:
            if c == 'LBRACE':
                unmatched[0] += 1
        if c == 'RBRACE':
            unmatched[0] -= 1
            if len(unclosed):
                unclosed.pop(-1)
            elif c == '(':
                unmatched[1] += 1
            elif c == ')':
                unmatched[1] -= 1
            elif c == '[':
                unmatched[2] += 1
            elif c == ']':
                unmatched[2] -= 1

    unmatched_sum = sum(unmatched)
    unclosed_sum = len(unclosed)
    if unclosed_sum > 0 and unmatched_sum == 0 and last[1] == 'NEWLINE' and not last[0] == 'NEWLINE':
        if last[0] == ';':
            return True
    return unclosed_sum == 0 and unmatched_sum == 0


def input_swallowing_interrupt(_input):

    def _input_swallowing_interrupt(*args):
        try:
            return _input(*args)
        except KeyboardInterrupt:
            print('^C')
            return '\n'

    return _input_swallowing_interrupt


class Repl(cmd.Cmd):
    __doc__ = '\n    A simple wrapper for REPL using the python cmd module.\n    '

    def __init__(self, ps1='> ', ps2='>> ', globals=None, locals=None):
        super().__init__()
        self.ps1 = ps1
        self.ps2 = ps2
        self.globals = globals
        self.locals = locals
        self.parser = Parser()
        self.prompt = ps1
        self.stmt = ''

    def do_help(self, arg):
        self.default('help(%s)' % arg)

    def do_quit(self, arg):
        self.default('quit(%s)' % arg)

    def do_EOF(self, arg):
        self.default('quit()')

    def onecmd(self, line):
        if line == 'EOF':
            return self.do_EOF(line)
        try:self.default(line)
        except Exception as err:
            print(type(err).__name__+": ",str(err))
            self.stmt=''
        self.prompt = self.ps1 if len(self.stmt) == 0 else self.ps2

    def default(self, line):
        if line is not None:
            self.stmt += '%s\n' % line
            if not self.is_close():
                return
            try:
                try:
                    try:
                        node = self.parser.parse('___=(%s);__print__(___)' % self.stmt, '<STDIN>')
                    except Exception:
                        node = self.parser.parse(self.stmt, '<STDIN>')

                    code = compile(node, '<STDIN>', 'exec')
                    exec(code, self.globals, self.locals)
                except SystemExit:
                    sys.exit()
                except BaseException as e:
                    try:
                        sys.stderr.write('%s: %s\n' % (e.__class__.__name__, str(e)))
                    finally:
                        e = None
                        del e

            finally:
                self.stmt = ''

    def is_close(self):
        return is_close(self.stmt)

    def cmdloop(self, *args, **kwargs):
        orig_input_func = cmd.__builtins__['input']
        cmd.__builtins__['input'] = input_swallowing_interrupt(orig_input_func)
        try:
            (super().cmdloop)(*args, **kwargs)
        finally:
            cmd.__builtins__['input'] = orig_input_func


def repl(ps1='> ', ps2='>> ', globals=None):
    """
    A simple read-eval-print-loop for the µLang program
    """
    info = [
     '\tglobals: to list all builtins',
     '\tquit: to quit the REPL',
     '\thelp: to show this message']
    if not globals:
        globals = create_globals(fname='<STDIN>')
    globals['globals'] = lambda : print('\n'.join([' %s (%s)' % (k, v.__class__.__name__) for k, v in globals.items() if k != '__builtins__' if k != '___']))

    # Avoid dead code: help(*args)
    def _help(*args):
        if not args:print('\n'.join(info))
    globals['help'] = _help
    Repl(ps1, ps2, globals).cmdloop("Welcome to ulang's REPL..\nType 'help' for more informations.")
    sys.exit(0)
# okay decompiling E:\ulang\ulang-0.2.2.exe_extracted\PYZ-00.pyz_extracted\ulang.runtime.repl.pyc
