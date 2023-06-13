import sys
from rich.console import Console

def elegant_exit() -> None:
    Console().print_exception()
    sys.exit(1)