import subprocess
import os
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from IPython.display import display, HTML

def print_out(out: str):
    for l in out.split('\n'):
        print(l)

def displayHTML(html_code):
    '''
    Display HTML in notebook
    '''
    display(HTML(html_code))

@magics_class
class CPP(Magics):
    @staticmethod
    def compile(src, out):
        compiler = 'g++'
        res = subprocess.check_output(
            [compiler, "-o", out, src], stderr=subprocess.STDOUT)
        print_out(res.decode("utf8"))

    @staticmethod
    def custom_compile(arg_list):
        res = subprocess.check_output(
            arg_list, stderr=subprocess.STDOUT)
        print_out(res.decode("utf8"))

    @staticmethod
    def run(executable):
        try:
            res = subprocess.check_output([f'./{executable}'], stderr=subprocess.STDOUT)
            print_out(res.decode("utf8"))
        except subprocess.CalledProcessError as e:
            print_out(e.output.decode("utf8"))

    @magic_arguments()
    @argument('-n', '--name', type=str, help='File name that will be produced by the cell.')
    @argument('-c', '--compile', type=str, help='Compile command. Use true for default command or specify command in single quotes.')
    @cell_magic
    def cpp(self, line='', cell=None):
        '''
        C++ syntax highlighting cell magic.
        '''
        args = parse_argstring(self.cpp, line)
        if args.name is not None:
            ex = args.name.split('.')[-1]
            if ex not in ['c', 'cpp', 'h', 'hpp']:
                raise Exception('Name must end with .cpp, .c, .hpp, or .h')
        else:
            args.name = 'src.cpp'

        mode = "a" if args.append else "w"

        with open(args.name, mode) as f:
            f.write(cell)

        if args.compile is not None:
            try:
                if args.compile == 'true':
                    self.compile(args.name, args.name.split('.')[0])
                else:
                    # Ensure args.compile is a string and properly split
                    if isinstance(args.compile, str):
                        self.custom_compile(args.compile.replace("'", "").split(' '))
                    else:
                        raise ValueError("Compile argument must be a string")
            except subprocess.CalledProcessError as e:
                print_out(e.output.decode("utf8"))

        if args.style is not None:
            displayHTML(highlight(cell, CppLexer(), HtmlFormatter(full=True, nobackground=True, style=args.style)))

    @magic_arguments()
    @argument('-n', '--name', type=str, help='File name that will be produced by the cell.')
    @argument('-c', '--compile', type=str, help='Compile command. Use true for default command or specify command in single quotes.')
    @cell_magic
    def cpurun(self, line='', cell=None):
        '''
        C++ cell magic that compiles and runs the code.
        '''
        args = parse_argstring(self.cpurun, line)
        if args.name is not None:
            ex = args.name.split('.')[-1]
            if ex not in ['c', 'cpp']:
                raise Exception('Name must end with .cpp or .c')
        else:
            args.name = 'src.cpp'

        # Save code to file
        with open(args.name, 'w') as f:
            f.write(cell)

        # Compile the code
        executable = args.name.split('.')[0]
        try:
            if args.compile is None or args.compile == 'true':
                self.compile(args.name, executable)
            else:
                # Ensure args.compile is a string and properly split
                if isinstance(args.compile, str):
                    self.custom_compile(args.compile.replace("'", "").split(' '))
                else:
                    raise ValueError("Compile argument must be a string")
        except subprocess.CalledProcessError as e:
            print_out(e.output.decode("utf8"))
            return

        # Run the executable
        self.run(executable)

def load_ipython_extension(ip):
    os.system('pip install pygments ipywidgets')
    plugin = CPP(ip)
    ip.register_magics(plugin)
