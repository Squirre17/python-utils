import sys
import squ.utils.log as log
import squ.gdb.proc as proc
from squ.utils.decorator import handle_exception
from squ.gdb.config.command import Command
from typing import Optional, List, Tuple, TextIO
import squ.gdb.kernel.link as link
from squ.utils.color import Color as C

import click

# import squ.gdb.kernel.link as link

class Fl(Command):

    cmdname = "chain"
    syntax = "chain addr"
    examples = []
    aliases  = []    

    def __init__(self):
        super().__init__(
            aliases=self.aliases,
        )

    @click.command()
    @click.option("--addr", "-a", type=str, required=True, help="head list value")
    @proc.only_if_running
    def do_invoke(addr): # todo: invoke
        addr = int(addr, 16)
        prefix = C.greenify("chain : ")
        click.echo(prefix + link.generate(addr)) # chain -a 0xffff888004020d20

fl = Fl()
