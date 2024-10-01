import gdb
import inspect

def traverse_frames(callback, *args):
	frame = gdb.newest_frame()
	while not frame is None:
		cf = frame
		frame = frame.older()

		if callback(*args, cf):
			break


def print_bt_if_has_parent(parent_name):
	def bt_if_parent(parent_name, frame : gdb.Frame):
		if frame.name() is None:
			return False

		if parent_name in frame.name():
			gdb.write(f"print_bt_if_has_parent found {parent_name} in callstack\n")
			btout = gdb.execute("bt", to_string=True)
			gdb.write(f"{btout}\n")
			return True

		return False

	traverse_frames(bt_if_parent, parent_name)

def print_bt_if_has_file(filename):
	def bt_if_file(fileName, frame: gdb.Frame):
		sal = frame.find_sal()
		if sal.symtab is None or sal.symtab.filename is None:
			return False

		if fileName in sal.symtab.filename:
			gdb.write(f"print_bt_if_has_file found {filename} in callstack\n")
			btout = gdb.execute("bt", to_string=True)
			gdb.write(f"{btout}\n")
			return True

		return False

	traverse_frames(bt_if_file, filename)




def create_gdb_command(name, function, description=""):
	"""
	Creates a GDB command with less boilerplate.

	:param name: Name of the command (the name you'll type in GDB).
	:param description: Command description.
	:param function: Python function to link to the command.
	"""
	class CustomGDBCommand(gdb.Command):
		def __init__(self):
			super(CustomGDBCommand, self).__init__(name, gdb.COMMAND_USER)

		def invoke(self, arg, from_tty):
			args = arg.split(",")
			if len(inspect.signature(function).parameters) == 0:
				function()
			else:
				function(*args)

	CustomGDBCommand.__doc__ = description  # Set the command description
	CustomGDBCommand()  # Register the command


create_gdb_command(name="atrue", function=always_true)
create_gdb_command(name="afalse", function=always_false)
create_gdb_command(name="print_bt_if_has_parent", function=print_bt_if_has_parent)
create_gdb_command(name="print_bt_if_has_file", function=print_bt_if_has_file)
