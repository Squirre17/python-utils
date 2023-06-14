from squ.gdb.config.command import Command
import click

class Rest(Command):

    cmdname = "test"
    syntax = "test [info|sym|addr] ..."
    examples = []
    aliases  = ["aaa", "bbb"]    

    def __init__(self):
        super().__init__(
            aliases=self.aliases,
        )

    @click.group() # self position argument not allow
    def do_invoke():
        pass

rest = Rest()

@rest.do_invoke.command()
@click.argument("name", type=str)
def info(name):
    click.echo(f"info {name}")

@rest.do_invoke.command()
@click.argument("addr", type=int)
@click.argument("num", type=int)
def sym(addr, num):
    click.echo(f"sym {addr} {num}")