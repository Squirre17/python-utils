'''
copy from pwndbg
'''

import gdb
import squ.gdb.types as types
from loguru import logger
from typing import Generator
import squ.utils.log as log

def offset_of(typename: str, fieldname: str) -> int:
    ptr_type = gdb.lookup_type(typename).pointer()
    dummy = gdb.Value(0).cast(ptr_type)
    return int(dummy[fieldname].address)


def container_of(ptr : gdb.Value, typename: str, fieldname: str) -> gdb.Value:
    '''
    return a object_ptr by a ptr with field point to it's middle

    struct obj {
        int a
        ···
        struct list_head list;
    }
    --------     --------   ——
    | ···  |     | ···  | <- offset
    | list | --> | list |   --
    | ···  |     | ···  |
    '''
    ptr_type = gdb.lookup_type(typename).pointer()
    obj_addr = ptr.cast(types.u64) - offset_of(typename, fieldname)
    return gdb.Value(obj_addr).cast(ptr_type)

# e.g. for_each_entry(slab_caches, "struct kmem_cache", "list")
def for_each_entry(head : gdb.Value, typename: str, field, skip_head = True) -> Generator["gdb.Value", None, None]:

    addr = head

    if skip_head:
        addr = head["next"]
        if addr == 0:
            return
    
    while True:
        yield container_of(addr, typename, field)
        addr = addr.dereference()["next"]

        if int(addr) == 0:
            break
        if addr == head.address:
            break

# e.g. for_each_entry(slab_caches, "struct kmem_cache", "list")
def for_each_entry_no_head(objptr : gdb.Value, typename: str, field) -> Generator["gdb.Value", None, None]:

    yield objptr
    addr = objptr["next"]

    while int(addr) != 0 and addr != objptr.address:
        yield addr
        addr = addr.dereference()["next"]

def traverse_freelist(freelist : gdb.Value, maxdepth = 6) -> Generator["gdb.Value", None, None]:
    '''
    assume the position freelist point to is "next" field
    '''
    while maxdepth and (freelist is not None) and (int(freelist) != 0) :
        yield freelist
        freelist = freelist.cast(types.voidp.pointer()).dereference()


