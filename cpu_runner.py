import subprocess
import os
import shlex
from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.display import display, HTML

def print_out(out: str):
    """Prints the output line by line."""
    for l in out.split('\n'):
        print(l)

def displayHTML(html_code):
    """Displays HTML in notebook."""
    display(HTML(html_code))

@magics_class
class CPP(Magics):
    @staticmethod
    def compile_and_link(src, obj_file, executable, objects=[], compile_flags=[], link_flags=[]):
        """Compiles the source file into an object file and links it into an executable with additional flags."""
        compiler = 'g++'

        # Compile the source file to an object file with additional flags
        compile_cmd = [compiler] + compile_flags + ['-c', src, '-o', obj_file]
        # print("Compilation command:", " ".join(compile_cmd))  # Debugging line
        try:
            res = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print_out(res.decode("utf8"))
        except subprocess.CalledProcessError as e:
            print_out(e.output.decode("utf8"))
            raise

        # Link the object files to create the executable
        link_cmd = [compiler] + link_flags + ['-o', executable] + [obj_file] + objects
        # print("Linking command:", " ".join(link_cmd))  # Debugging line
        try:
            res = subprocess.check_output(link_cmd, stderr=subprocess.STDOUT)
            print_out(res.decode("utf8"))
        except subprocess.CalledProcessError as e:
            print_out(e.output.decode("utf8"))
            raise

    @staticmethod
    def compile(src, executable, compile_flags=[]):
        """Compiles the source file into an executable with additional flags."""
        compiler = 'g++'

        # Compile the source file to an executable with additional flags
        compile_cmd = [compiler] + compile_flags + [src, '-o', executable]
        # print("Compilation command:", " ".join(compile_cmd))  # Debugging line
        try:
            res = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
            print_out(res.decode("utf8"))
        except subprocess.CalledProcessError as e:
            print_out(e.output.decode("utf8"))
            raise

    @staticmethod
    def run(executable):
        """Runs the executable."""
        try:
            res = subprocess.check_output(['./' + executable], stderr=subprocess.STDOUT)
            print_out(res.decode("utf8"))
        except subprocess.CalledProcessError as e:
            print_out(e.output.decode("utf8"))

    @magic_arguments()
    @argument('-n', '--name', type=str, help='File name that will be produced by the cell.')
    @argument('-o', '--objects', type=str, help='Comma-separated list of object files to link.')
    @argument('-f', '--flags', type=str, help='Comma-separated list of compiler flags.')
    @cell_magic
    def cpurun(self, line='', cell=None):
        """C++ cell magic that compiles and runs the code with additional compiler flags."""
        args = parse_argstring(self.cpurun, line)
        if args.name:
            if not args.name.endswith(('.cpp', '.c')):
                raise Exception('Name must end with .cpp or .c')
        else:
            args.name = 'src.cpp'

        # Save code to file
        with open(args.name, 'w') as f:
            f.write(cell)

        # Define output files and objects
        executable = args.name.rsplit('.', 1)[0]
        obj_file = executable + '.o'
        objects = args.objects.split(',') if args.objects else []

        # Handle flags passed as a single argument
        if args.flags:
            # Use shlex.split to correctly handle quoted flags
            compile_flags = shlex.split(args.flags)
        else:
            compile_flags = []

        link_flags = []  # Assuming no additional link flags needed

        try:
            if args.objects:
                # Compile the source file and link the object files with additional flags
                self.compile_and_link(args.name, obj_file, executable, objects, compile_flags, link_flags)
            else:
                # Compile the source file into an executable with additional flags
                self.compile(args.name, executable, compile_flags)
        except subprocess.CalledProcessError as e:
            print_out(e.output.decode("utf8"))
            return

        # Run the executable
        self.run(executable)

def load_ipython_extension(ip):
    """Load the IPython extension."""
    os.system('pip install pygments ipywidgets')
    ip.register_magics(CPP(ip))
