import squ
import squ.utils.log as log
import gdb
from squ.gdb.config.command import Command

class Rest(Command):

    cmdname = "test"
    syntax = "test"
    examples = []
    aliases  = ["aaa", "bbb"]    

    def __init__(self):
        super().__init__(
            aliases=self.aliases,
        )

    def invoke(self, argument: str, from_tty: bool) -> None:
        argv = gdb.string_to_argv(argument)
        argc = len(argv)
        log.info(f"argv {argv} , argc {argc}")

        log.info("success")

Rest()