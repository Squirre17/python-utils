import squ

import gdb
import sys
import squ.utils.log as log
from squ.utils.decorator import handle_exception
from squ.gdb.config.command import Command
from typing import Optional, List, Tuple, TextIO

class Stdio:
    queue: List[Tuple[TextIO, TextIO, TextIO]] = []

    def __enter__(self, *a, **kw) -> None:
        self.queue.append((sys.stdin, sys.stdout, sys.stderr))

        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def __exit__(self, *a, **kw) -> None:
        sys.stdin, sys.stdout, sys.stderr = self.queue.pop()


stdio = Stdio()
import click
# with stdio:
#     import click

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
        
class Rest(Command):

    cmdname = "test"
    syntax = "test -x [aa|bb] -o [out_name]"
    examples = []
    aliases  = ["aaa", "bbb"]    

    def __init__(self):
        super().__init__(
            aliases=self.aliases,
        )

    @click.command()
    @click.option("--extended", "-x", type=str, required=False, help='echo content.')
    @click.option("--out", "-o", type=str, required=True, default="out", help='echo object.')
    def do_invoke(extended: Optional[str], out: str):
        if extended:
            log.info(f"{extended} -> {out}")
        else:
            log.info(f"    <- {out}")


Rest()