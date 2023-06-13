from enum import Enum
from typing import (Any, ByteString, Callable, Dict, Generator, Iterable,
                    Iterator, List, NoReturn, Optional, Sequence, Set, Tuple, Type,
                    Union, NewType)
import squ.gdb.file   as file
import squ.gdb.memory as mem
import squ.utils.log  as log
from squ.utils.color import Color
from squ.gdb.address import Address

import gdb

'''
(gdb) !cat /proc/607253/maps
555555554000-555555558000 r--p 00000000 08:05 49939125                   /usr/bin/ls
555555558000-55555556c000 r-xp 00004000 08:05 49939125                   /usr/bin/ls
55555556c000-555555575000 r--p 00018000 08:05 49939125                   /usr/bin/ls
555555576000-555555578000 rw-p 00021000 08:05 49939125                   /usr/bin/ls
555555578000-555555579000 rw-p 00000000 00:00 0                          [heap]
7ffff7fc9000-7ffff7fcd000 r--p 00000000 00:00 0                          [vvar]
7ffff7fcd000-7ffff7fcf000 r-xp 00000000 00:00 0                          [vdso]
7ffff7fcf000-7ffff7fd0000 r--p 00000000 08:05 49939588                   /usr/lib/x86_64-linux-gnu/ld-2.31.so
7ffff7fd0000-7ffff7ff3000 r-xp 00001000 08:05 49939588                   /usr/lib/x86_64-linux-gnu/ld-2.31.so
7ffff7ff3000-7ffff7ffb000 r--p 00024000 08:05 49939588                   /usr/lib/x86_64-linux-gnu/ld-2.31.so
7ffff7ffc000-7ffff7ffe000 rw-p 0002c000 08:05 49939588                   /usr/lib/x86_64-linux-gnu/ld-2.31.so
7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0 
7ffffffdd000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
ffffffffff600000-ffffffffff601000 --xp 00000000 00:00 0                  [vsyscall]
'''

class Page:
    '''
    one page of virtual memory space and page permission and so on
    '''
    class Attribute(Enum):
        stack  = 1
        heap   = 2
        code   = 3
        data   = 4
        rodata = 5 
        # rwx    = 6

    def __init__(
        self, 
        start  : int, 
        end    : int, 
        perm   : int, 
        offset : int, 
        path   : str
    ): 
        # perm = 4 2 1 : rwx
        self.__start  : int        = start
        self.__end    : int        = end
        self.__offset : int        = offset
        self.__path   : str        = path
        self.__rwx    : List[bool] = [perm & 4, perm & 2, perm & 1]

        '''
        NOTE: order here is important
        '''

        if "[stack" in self.__path: 
            self.__attr = self.Attribute.stack
        elif "[heap" in self.__path: 
            self.__attr = self.Attribute.heap
        elif self.rw:
            self.__attr = self.Attribute.data
        elif self.can_execute:
            self.__attr = self.Attribute.code
        else: 
            self.__attr = self.Attribute.rodata

    @property
    def start(self) -> int:
        return self.__start

    @property
    def end(self) -> int:
        return self.__end
    
    @property
    def offset(self) -> int:
        return self.__offset
    
    @property
    def path(self) -> str:
        return self.__path
    
    @property
    def can_read(self) -> bool :
        return self.__rwx[0]
    
    @property
    def can_write(self) -> bool :
        return self.__rwx[1]
    
    @property
    def can_execute(self) -> bool :
        return self.__rwx[2]

    @property
    def rw(self) -> bool :
        return self.can_read and self.can_write

    @property
    def rwx(self) -> bool :
        return self.can_read and self.can_write and self.can_execute

    @property
    def attr(self) -> Attribute :
        return self.__attr

    @property
    def perm_str(self) -> str :
        assert self.__rwx

        return ''.join([
            'r' if self.__rwx[0] else '-',
            'w' if self.__rwx[1] else '-',
            'x' if self.__rwx[2] else '-',
        ])# omit 'p' ,seemings like no use

    def __str__(self) -> str:
        # TODO: considering heap
        # Colorify each page line

        color = None
        if self.can_execute :
            color = "red"

        if "stack" in self.path:
            color = "purple"

        return Color.colorify(" ".join(
            list(map(
                lambda addr : self.fmt_addr(addr),
                [ self.start, self.end, self.offset ] 
            ))+ [ "{:<4s}{}".format(self.perm_str, self.path) ]
        ), color)

    def __contains__(self, addr):
        '''
        for addr in page
        '''
        return self.start <= addr < self.end
        
    def fmt_addr(self, addr : int):
        # format to 0xffffffffffffffff
        # TODO: current only considering 64-bit
        return f"0x{addr:016x}"