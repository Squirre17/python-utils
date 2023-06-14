import sys
import gdb

class SysArgvContext:

    cache = None

    def __init__(self, cmd: str, args: str) -> None:
        self.cmd = cmd
        self.args = args

    def __enter__(self, *a, **kw) -> None:
        self.cache = sys.argv

        argv = gdb.string_to_argv(self.args)
        argv = [self.cmd] + argv

        sys.argv = argv

    def __exit__(self, *a, **kw) -> None:
        sys.argv = self.cache