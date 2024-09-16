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
class GPURun(Magics):
    @staticmethod
    def compile_and_run(src, out, object_files=[]):
        compiler = 'nvcc'

        # Compile the CUDA code
        try:
            # Include object files for linking
            compile_cmd = [compiler, "-o", out, src] + object_files
            compile_res = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print_out(compile_res.decode("utf8"))
        except subprocess.CalledProcessError as e:
            print("Compilation failed:")
            print_out(e.output.decode("utf8"))
            return

        # Run the compiled executable
        try:
            run_res = subprocess.check_output(f"./{out}", stderr=subprocess.STDOUT, shell=True)
            print_out(run_res.decode("utf8"))
        except subprocess.CalledProcessError as e:
            print("Execution failed:")
            print_out(e.output.decode("utf8"))

    @magic_arguments()
    @argument('-n', '--name', type=str, help='File name that will be produced by the cell.')
    @argument('-a', '--append', help='Should be appended to the same file', action="store_true")
    @argument('-s', '--style', type=str, help='Pygments style name')
    @argument('-o', '--objects', type=str, help='Comma-separated list of additional object files.')
    @cell_magic
    def gpurun(self, line='', cell=None):
        '''
        CUDA syntax highlighting cell magic that compiles, saves, and runs the code.
        '''
        global style
        args = parse_argstring(self.gpurun, line)

        # File extension checking
        if args.name is not None:
            ex = args.name.split('.')[-1]
            if ex not in ['cu', 'h']:
                raise Exception('Name must end with .cu or .h')
        else:
            args.name = 'src.cu'

        # Write mode depending on the append flag
        mode = "a" if args.append else "w"

        # Save the CUDA code to the file
        with open(args.name, mode) as f:
            f.write(cell)

        # Collect additional object files
        object_files = args.objects.split(',') if args.objects else []

        # Compile and run the CUDA code
        self.compile_and_run(args.name, args.name.split('.')[0], object_files)

        # Syntax highlighting for CUDA code
        if args.style is not None:
            displayHTML(highlight(cell, CppLexer(), HtmlFormatter(full=True, nobackground=True, style=args.style)))


def load_ipython_extension(ip):
    os.system('pip install pygments ipywidgets')
    plugin = GPURun(ip)
    ip.register_magics(plugin)
