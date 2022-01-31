# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.2rc1 (tags/v3.7.2rc1:75a402a217, Dec 11 2018, 22:09:03) [MSC v.1916 32 bit (Intel)]
# Embedded file name: ulang\runtime\main.py
import ast, dis, imp, os, sys, getopt, time, threading, trace
from datetime import datetime
from ulang.runtime.env import create_globals
from ulang.runtime.repl import repl
from ulang.parser.core import Parser
from ulang.parser.lexer import lexer
from ulang.codegen import blockly, python, ulgen
import ulang
from pprint import pprint

def usage(prog):
    info = 'usage: %s [-apbcidsDth] input_file\nOptions and arguments:\n --dump-ast,        -a   dump ast info\n --dump-python,     -p   dump python source code\n --dump-blockly,    -b   dump blockly xml (experimental)\n --dump-bytecode,   -c   dump donsok bytecode (experimental)\n --python-to-ulang, -s   convert python to ulang\n --debug,           -D   debug with Pdb (experimental)\n --interact,        -i   inspect interactively after running script\n --disassemble,     -d   disassemble the python bytecode\n --exec-code=<code> -e   run code from cli argument\n --show-backtrace,  -t   show backtrace for errors\n --version,         -v   show the version\n --help,            -h   show this message\n'
    sys.stderr.write(info % os.path.basename(prog))
    sys.exit(-1)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if '/?' in argv or '-?' in argv:
        usage(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], 'hdapbctisDTe:v', [
         'dump-ast',
         'dump-python',
         'dump-blockly',
         'dump-bytecode',
         'dump-tokens',
         'python-to-ulang',
         'exec-code=',
         'debug',
         'disassemble',
         'show-backtrace',
         'help',
         'version',
         'interact'])
    except BaseException as e:
        raise
        try:
            sys.stderr.write(str(e) + '\n')
            usage(argv[0])
        finally:
            e = None
            del e

    input_file = None
    dump_ast = False
    dump_python = False
    dump_blockly = False
    dump_bytecode = False
    dump_tokens = False
    disassemble = False
    trace_exception = False
    interactive = False
    python2ulang = False
    exec_code = None
    debug = False
    for opt, value in opts:
        if opt in ('-i', '--interact'):
            interactive = True
        elif opt in ('-p', '--dump-python'):
            dump_python = True
        elif opt in ('-a', '--dump-ast'):
            dump_ast = True
        elif opt in ('-b', '--dump-blockly'):
            dump_blockly = True
        elif opt in ('-c', '--dump-bytecode'):
            dump_bytecode = True
        elif opt in ('-d', '--disassemble'):
            disassemble = True
        elif opt in ('-s', '--python-to-ulang'):
            python2ulang = True
        elif opt in ('-D', '--debug'):
            debug = True
        elif opt in ('-t', '--show-backtrace'):
            trace_exception = True
        elif opt in ('-T', '--dump-tokens'):
            dump_tokens = True
        elif opt in ('-h', '--help'):
            usage(argv[0])
        elif opt in ('-v', '--version'):
            print(ulang.__version__)
            return
        else:
            if opt in ('-e', '--exec-code'):
                exec_code = value

    if input_file is None:
        if len(args) > 0:
            input_file = args[0]
    if input_file is None:
        if len(argv) == 1:
            sys.exit(repl())
        else:
            usage(argv[0])

    try:
        source = None
        if exec_code:
            source = exec_code
            input_file = '<CLI>'
        else:
            if input_file == '-':
                source = sys.stdin.read()
                input_file = '<STDIN>'
            else:
                with open(input_file, 'r',encoding='utf-8') as (f):
                    source = f.read().strip('\ufeff')

        if not source:
            sys.stderr.write('cannot open file "%s"!\n' % input_file)
            sys.exit(-1)

        if python2ulang:
            nodes = ast.parse(source, input_file)
            print(ulgen.dump(nodes))
            return
            if dump_tokens:
                tokens = lexer.lex(source)
                for token in tokens:
                    print((token.gettokentype()), end=' ')

                return
        else:
            parser = Parser()
            nodes = parser.parse(source, input_file)
            if dump_ast:
                pprint(ast.dump(nodes, True, True))
                return
            if dump_python:
                pprint(python.dump(nodes))
                return
            if dump_blockly:
                pprint(blockly.dump(nodes))
                return
            if dump_bytecode:
                from pygen.compiler import Compiler
                pprint(Compiler().compile(nodes, input_file).dump())
                return

            code = compile(nodes, input_file, 'exec')
            if disassemble:
                dis.dis(code)
                return
            globals = create_globals(argv=(args[1:]),
              fname=input_file)
            if debug:
                import pdb
                while True:
                    try:
                        pdb.run(code, globals, None)
                    except pdb.Restart:
                        pass
                    else:
                        break

            else:
                exec(code, globals)
        if interactive:
            repl(globals=globals)
    except Exception as e:
        try:
            sys.stderr.write('%s: %s\n' % (e.__class__.__name__, str(e)))
            if trace_exception:
                raise e
        finally:
            e = None
            del e

if __name__=="__main__":main()
# okay decompiling E:\ulang\ulang-0.2.2.exe_extracted\PYZ-00.pyz_extracted\ulang.runtime.main.pyc
