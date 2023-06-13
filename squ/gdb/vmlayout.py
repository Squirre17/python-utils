from enum import Enum
from typing import (Any, ByteString, Callable, Dict, Generator, Iterable,
                    Iterator, List, NoReturn, Optional, Sequence, Set, Tuple, Type,
                    Union, NewType)

import squ.gdb.file   as file
import squ.gdb.memory as mem
import squ.utils.log  as log
import squ.gdb.proc   as proc

# from squ.gdb.cmds import (Cmd, register)

from squ.gdb.page    import (Page)
from squ.utils.color import (Color)
from squ.gdb.address import (Address)

import gdb
'''GDB API
Programs which are being run under GDB are called inferiors
Python scripts can access information about and manipulate inferiors controlled by GDB via objects of the gdb.Inferior class.
'''

# NOTE: vmmap must be executed after program run
@proc.only_if_running
def show(whether_print = True):

    pid = gdb.selected_inferior().pid

    vmmap_path = '/proc/%s/maps' % pid

    data : ByteString = file.get(vmmap_path)
    if data is None:
        raise NotImplementedError

    lines = [line for line in data.decode().split('\n') if line != '' ]

    headers = ["Start", "End", "Offset", "Perm", "Path"]
    print(
        Color.blueify(
            "{:<{w}s}{:<{w}s}{:<{w}s}{:<4s} {:s}"
                        .format(*headers, w = 19)
        ))
    for ln in lines:
        # TODO: understand dev and inode 
        # dev => master:slave dev number
        # inode => TODO:
        # NOTE: can have some lines missing path
        maps, perm, offset, dev, inode_path = ln.split(None ,4)
        inode_path = inode_path.split()
        if len(inode_path) == 1:
            path = ''
            inode = inode_path[0]
        else:
            inode, path = inode_path[0], inode_path[1]

        flag : int = 0
        if 'r' in perm : flag |= 4
        if 'w' in perm : flag |= 2
        if 'x' in perm : flag |= 1

        start, end = maps.split('-')
        start  = int(start, 16)
        end    = int(end, 16)
        offset = int(offset, 16)
        page : Type["Page"] = Page(start, end, flag, offset, path)
        
        pm.add(page)

        if whether_print: # TODO: simply update
            print(page)


    '''
    ideal output like gef :

    Start              End                Offset             Perm Path
    0x0000000000400000 0x0000000000401000 0x0000000000000000 r-- /home/squ/prac/a.out
    '''

    # TODO: colorify it


class PageManager:

    def __init__(self):
        self.pages : List[Page] = []
        
        
    def add(self, page : Page):
        self.pages.append(page)
    

pm = PageManager()

# TODO: I think all memory operation should be called by pwnxy.memory rather than vmmap
def find(addr : Address) -> Optional[Page] :
    '''
    find whether a address is belong to a page and return it
    '''
    addr = int(addr)
    show(False) # TODO: simply update

    for page in pm.pages:
        if addr in page:
            return page
    
    # custom page?
    return None