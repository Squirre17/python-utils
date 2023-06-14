from loguru import logger
from squ.utils.color import Color
import sys
import traceback
from squ.utils.exit import elegant_exit


def info(msg, end = "\n"):
    prompt = Color.colorify("[+]" ,"green")
    body   = " INFO  : "
    print(prompt + body, end = "")
    print(msg, end = end)

in_debug = True

# def dbg(msg, end = "\n"):
#     if in_debug:
#         prompt = Color.colorify("[#]" ,"purple")
#         body   = " DBG   : "
#         print(prompt + body, end = "")
#         print(msg, end = end)
#     else : pass

import squ.gdb.stdio
with squ.gdb.stdio.stdio:
    dbg = logger.debug

def err(msg, end = "\n"):
    prompt = Color.colorify("[$]" ,"red")
    body   = " ERR   : "
    print(prompt + body, end = "")
    print(msg, end = end)

def warn(msg, end = "\n"):
    prompt = Color.colorify("[-]" ,"yellow")
    body   = " WARN  : "
    print(prompt + body, end = "")
    print(msg, end = end)

def note(msg, end = "\n"):
    prompt = Color.colorify("[*]" ,"blue")
    body   = " NOTE  : "
    print(prompt + body, end = "")
    print(msg, end = end)

def fatal(msg):
    '''
    fatal err by program
    '''
    prompt = Color.boldify(Color.colorify("[!]" ,"red"))
    body   = " FATAL : "
    print(prompt + body, end = "")
    print(msg)
    sys.exit(1)

def err_print_exc(msg):
    err(msg)
    traceback.print_exc()

if __name__ == "__main__":
    s = "123"
    info(s)
    dbg(s)
    err(s)
    note(s)
    fatal(s)