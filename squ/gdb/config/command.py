from typing import (Any, ByteString, Callable, Dict, Generator, Iterable,
                    Iterator, List, NoReturn, Optional, Sequence, Set, Tuple, Type,
                    Union, NewType)

import squ.utils.log as log
from squ.utils.color import Color

# import pwnxy.globals
import collections
import gdb
from loguru import logger

from squ.utils.decorator import handle_exception
from squ.gdb.stdio import stdio
from squ.gdb.sysargv import SysArgvContext


# TODO : ction: Command.complete (text, word) https://sourceware.org/gdb/onlinedocs/gdb/CLI-Commands-In-Python.html

'''APIs:
gdb.execute (command [, from_tty [, to_string]]) ->  str | None
    The `from_tty` flag specifies whether GDB ought to consider this command as having originated from the user invoking it interactively. It must be a boolean value. If omitted, it defaults to False.
    any output produced by command is sent to GDB’s standard output (and to the log output if logging is turned on). If the to_string parameter is True, then output will be collected by gdb.execute and returned as a string. The default is False
'''

'''Cmd:
    This is an abstract class for invoking commands, should not be instantiated
'''
def check_whether_exist(cmd : str) -> bool:
    try:
        gdb.execute(cmd, from_tty=True, to_string=True)
    except gdb.error:
        return False
    else:
        return True

class Command(gdb.Command):
    
    builtin_override_whitelist = {'up', 'down', 'search', 'pwd', 'start'} # TODO: 

    cmdname: str
    syntax: str
    examples: List[str] = [""]

    def __init__(
        self ,
        aliases               = [],
        completer_class : int = gdb.COMPLETE_NONE, 
        command_class  : int  = gdb.COMMAND_NONE):

        syntax  = Color.yellowify("\nSyntax: ") + self.syntax
        example = Color.yellowify("\nExamples: \n\t")
        example += "\n\t".join(self.examples)

        self.__doc__ = " " * 4 + syntax + example

        try:
            gdb.execute(self.cmdname, from_tty=True, to_string=True)
        except gdb.error:
            pass
        else:
            log.fatal("{} command name alreadly used".format(self.cmdname))
            
        
        super().__init__(self.cmdname, command_class, command_class) # TODO:

        for alias in aliases:
            if hasattr(self, "complete"):
                AliasCommand(
                    alias, self.cmdname, command_class, completer_class, self.complete
                )
            else :
                AliasCommand(
                    alias, self.cmdname, command_class, completer_class
                )


    def __init_subclass__(cls, **kvargs):

        super().__init_subclass__(**kvargs)
        attributes = ("cmdname", "examples", "syntax")

        for attr in attributes:
            if not hasattr(cls, attr):
                log.fatal("Notimplement {}".format(attr))
        
        assert type(getattr(cls, "examples")) is list

    @handle_exception
    def invoke(self, args: str, from_tty: bool) -> None:
        with stdio:
            with SysArgvContext(self.cmdname, args):
                try:
                    self.do_invoke()
                except SystemExit:
                    pass

    # def complete(self, arguline: str, last: str):
    #     # https://stackoverflow.com/questions/41704089/programmatic-gdb-completer-interface-via-python
    #     raise NotImplementedError
    

    # @staticmethod
    # def check_whether_recorded() -> bool :
    #     '''
    #     recoding all cmds, TODO: but not know what propose this fn?
    #     '''


    #     '''
    #     (gdb) show commands 
    #         1  q
    #         2  start
    #         3  q
    #         4  python help
    #         5  source ./gdbinit.py 
    #     '''
    #     lines_tmp = gdb.execute("show commands", from_tty = False, to_string = True)
    #     if lines_tmp is not None:
    #         lines = lines_tmp.splitlines()
    #     # empty history
    #     if not lines:
    #         return False

    #     last_line = lines[-1]

    #     '''split api
    #     sep : The delimiter according which to split the string. None means split according to any whitespace
    #     Maximum : number of splits to do. -1 (the default value) means no limit.
    #     ''' 
    #     num, cmd = last_line.split(None ,1)
    #     # TODO: history record this cmd if not executed before
    #     return True

class AliasCommand(gdb.Command):
    """Simple aliasing wrapper because GDB doesn't do what it should."""

    def __init__(
            self,
            alias: str, 
            cmdname : str,
            completer_class: int = gdb.COMPLETE_NONE, 
            command_class: int = gdb.COMMAND_NONE,
            complete = None
        ) -> None:

        if check_whether_exist(alias):
            log.err(f"{alias} already exist")
            return

        self.__command = cmdname
        
        self.__doc__ = f"Alias for '{Color.greenify(alias)}'"

        if complete is not None:
            self.complete = complete

        super().__init__(alias, command_class, completer_class)
        return

    def invoke(self, args: Any, from_tty: bool) -> None:
        gdb.execute(f"{self.__command} {args}", from_tty=from_tty)
        return


# TODO: seemings sloppy : This function should be used as ``argparse.ArgumentParser`` .add_argument method's `type` helper
def gdb_parse(s : str):
    _mask = 0xffffffffffffffff
    _mask_val_type = gdb.Value(_mask).type
    try:
        val = gdb.parse_and_eval(s)
        return int(val.cast(_mask_val_type))
    except Exception as e:
        log.fatal("notimpl")
    
