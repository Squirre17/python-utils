'''
memory peek poke operations, 
'''
import gdb
import string
import traceback

import squ.utils.log  as log
import squ.gdb.memory as memory
import squ.gdb.arch as arch
import squ.gdb.proc as proc

from loguru import logger
from typing import (List, Optional, Union)

from squ.gdb.config.param import Parameter

from squ.utils.color import Color
from squ.gdb.address import Address
from squ.utils.decorator import *
from enum import Enum

# from squ.gdb.page import Page
from squ.backtrace import err_print_exc
# TODO: import ...memory as mem use mem.reader

class MemReader:

    @proc.only_if_running
    def int(addr : Address, size : int = 8) -> int :

        assert size > 0 and size <= 8, "size error"
        
        try :
            val : memoryview = gdb.selected_inferior().read_memory(addr, size)
        except Exception as e :
            log.err(f"TODO {e}")
            traceback.print_exc()
        
        # do arch convert here ,ease the burden of upstream functions
        return int.from_bytes(bytearray(val), arch.endianness)

    @proc.only_if_running
    def bytes(addr : Address, size = 8) -> bytes:
        '''
        internal use ,don't expose it
        '''
        return gdb.selected_inferior().read_memory(addr, size).tobytes()

    # TODO: gdbtype became a enum
    '''GDB API
        Value.cast (type): hat is the result of casting this instance to the type ,type must be a `gdb.Type` object. 
        Value.dereference(): get content of given addr
    '''
    def by_type(addr, gdb_type) -> int:
        value = gdb.Value(addr)
        try:
            value = value.cast(gdb_type)
        except gdb.error as e:
            err_print_exc(e)

        return int(value.dereference())

    max_string_len = 48

    def string(addr : int, maxlen = int(max_string_len)) -> Optional[str] :
        '''
        only support ascii encode now
        '''

        try :
            mem_bytes = reader.bytes(addr, maxlen)
        except gdb.error:
            logger.error(f"Can't read at '{addr:#x}'")
            return None
        
        mem_bytes = mem_bytes.split(b'\x00', 1)[0].replace(b'\n', b"\\n").replace(b'\r', b"\\r").replace(b'\t', b"\\t")

        if mem_bytes == b'':
            return None
            
        try :
            mem_str = mem_bytes.decode('ascii')
        except UnicodeDecodeError as e :
            return None

        if len(mem_bytes) > maxlen :
            raise NotImplementedError
        
        if all(c in string.printable for c in mem_str):
            return mem_str

        return None

reader = MemReader()

class MemWriter:
    def write(addr : int, size : int, value : Union[int, str, bytes]) -> None :
        assert size > 0 and size <= 8, "size error"
        if isinstance(value, int) :
            # TODO: Considering byte order according to arch
            assert value <= 0xffffffffffffffff
            data = int.to_bytes(value, byteorder = "little")
        elif isinstance(value, str) :
            assert len(value) <= 8
            data = bytes(value, "utf-8")
        elif isinstance(value, bytes) :
            assert len(value) <= 8
            data = value
        else :
            log.err("TypeError")
        try :
            gdb.selected_inferior().write_memory(addr, data, size)
        except Exception as e :
            err_print_exc(e)

writer = MemWriter()
        
# NOTE: this addr use int rather than Address cuz all Address will
# use this for accessible check
def can_access(addr : int) -> bool:
    '''
    check whether accessible in given memory address
    '''
    try : 
        reader.int(addr, 1)
        return True
    except : 
        return False

# TODO
# max_string_len = theme.InnerParameter(
#     argname      = "max-string-length" ,
#     default_val  = 48,
#     docdesc      = "the max of string length which memory read"
# )




# write a bytes
def poke():
    ...

@proc.only_if_running
# TODO: experimental
def deref(addr : int, type : gdb.Type) -> gdb.Value:
    """
    Read one ``gdb.Type`` object at the specified address.
    """
    return gdb.Value(addr).cast(type.pointer()).dereference()

def page_align():
    raise NotImplementedError

'''
    if page is None:                 color = normal
    elif '[stack' in page.objfile:   color = stack
    elif '[heap'  in page.objfile:   color = heap
    elif page.execute:               color = code
    elif page.rw:                    color = data
    else:                            color = rodata
'''
# @deprecated
# class Page:
#     '''
#     one page of virtual memory space and page permission and so on
#     '''
#     class Attribute(Enum):
#         stack  = 1
#         heap   = 2
#         code   = 3
#         data   = 4
#         rodata = 5 
#         # rwx    = 6

#     def __init__(
#         self, start : int, end : int, 
#         perm : int, offset : int, path : str
#     ): 
#         # perm = 4 2 1 : rwx
#         self.__start  : int        = start
#         self.__end    : int        = end
#         self.__offset : int        = offset
#         self.__path   : str        = path
#         self.__rwx    : List[bool] = [perm & 4, perm & 2, perm & 1]

#         '''
#         NOTE: order here is important
#         '''

#         if "[stack" in self.__path: 
#             self.__attr = self.Attribute.stack
#         elif "[heap" in self.__path: 
#             self.__attr = self.Attribute.heap
#         elif self.rw:
#             self.__attr = self.Attribute.data
#         elif self.can_execute:
#             self.__attr = self.Attribute.code
#         else: 
#             self.__attr = self.Attribute.rodata

#     @property
#     def start(self) -> int:
#         return self.__start

#     @property
#     def end(self) -> int:
#         return self.__end
    
#     @property
#     def offset(self) -> int:
#         return self.__offset
    
#     @property
#     def path(self) -> str:
#         return self.__path
    
#     @property
#     def can_read(self) -> bool :
#         return self.__rwx[0]
    
#     @property
#     def can_write(self) -> bool :
#         return self.__rwx[1]
    
#     @property
#     def can_execute(self) -> bool :
#         return self.__rwx[2]

#     @property
#     def rw(self) -> bool :
#         return self.can_read and self.can_write

#     @property
#     def rwx(self) -> bool :
#         return self.can_read and self.can_write and self.can_execute

#     @property
#     def attr(self) -> Attribute :
#         return self.__attr

#     @property
#     def perm_str(self) -> str :
#         assert self.__rwx

#         return ''.join([
#             'r' if self.__rwx[0] else '-',
#             'w' if self.__rwx[1] else '-',
#             'x' if self.__rwx[2] else '-',
#         ])# omit 'p' ,seemings like no use

#     def __str__(self) -> str:
#         # TODO: considering heap
#         # Colorify each page line

#         color = None
#         if self.can_execute :
#             color = "red"

#         if "stack" in self.path:
#             color = "purple"

#         return Color.colorify(" ".join(
#             list(map(
#                 lambda addr : self.fmt_addr(addr),
#                 [ self.start, self.end, self.offset ] 
#             ))+ [ "{:<4s}{}".format(self.perm_str, self.path) ]
#         ), color)

#     def __contains__(self, addr):
#         '''
#         for addr in page
#         '''
#         return self.start <= addr < self.end
        
#     def fmt_addr(self, addr : int):
#         # format to 0xffffffffffffffff
#         # TODO: current only considering 64-bit
#         return f"0x{addr:016x}"
        
        
        
        
