import sys
import squ.gdb.stdio
from rich.console import Console


with squ.gdb.stdio.stdio:
    __rich_console = Console(highlight=True)

def elegant_exit() -> None:
    __rich_console.print_exception(show_locals=True)
    sys.exit(1)