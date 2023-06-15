'''
memory peek poke operations, 
'''
import sys
import gdb
import string

import squ.utils.log  as log
# import squ.gdb.memory as memory
import squ.gdb.arch as arch
import squ.gdb.proc as proc

from loguru import logger
from typing import (List, Optional, Union)

# from squ.gdb.config.param import Parameter

from squ.utils.color import Color
from squ.gdb.address import Address
from squ.utils.decorator import *
from enum import Enum


# from squ.gdb.page import Page
from squ.utils.exit import elegant_exit
# TODO: import ...memory as mem use mem.reader

class MemReader:

    def __init__(self) -> None:
        pass

    # @proc.only_if_running
    # @handle_exception
    def u64(self, addr : Address, size : int = 8) -> int :

        assert size > 0 and size <= 8, "size error"
        
        try :
            val : memoryview = gdb.selected_inferior().read_memory(addr, size)
        except Exception as e :
            raise e
            log.fatal(e)
        
        # do arch convert here ,ease the burden of upstream functions
        return int.from_bytes(bytearray(val), arch.endianness)

    @proc.only_if_running
    def bytes(self, addr : Address, size = 8) -> bytes:
        '''
        internal use ,don't expose it
        '''
        return gdb.selected_inferior().read_memory(addr, size).tobytes()

    # TODO: gdbtype became a enum
    '''GDB API
        Value.cast (type): hat is the result of casting this instance to the type ,type must be a `gdb.Type` object. 
        Value.dereference(): get content of given addr
    '''
    def by_type(self, addr, gdb_type) -> int:
        value = gdb.Value(addr)
        try:
            value = value.cast(gdb_type)
        except gdb.error as e:
            elegant_exit()

        return int(value.dereference())

    max_string_len = 48

    def string(self, addr : int, maxlen = int(max_string_len)) -> Optional[str] :
        '''
        only support ascii encode now
        '''

        try :
            mem_bytes = self.bytes(addr, maxlen)
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
    def write(self, addr : int, size : int, value : Union[int, str, bytes]) -> None :
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
            elegant_exit()

writer = MemWriter()
        
# NOTE: this addr use int rather than Address cuz all Address will
# use this for accessible check
def can_access(addr : int) -> bool:
    '''
    check whether accessible in given memory address
    '''
    try : 
        reader.u64(addr, 1)
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
def deref(addr : int, as_type : gdb.Type) -> gdb.Value:
    """
    Read one ``gdb.Type`` object at the specified address.
    """
    assert type(addr) is int
    return gdb.Value(addr).cast(as_type.pointer()).dereference()

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
