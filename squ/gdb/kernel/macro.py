'''
copy from pwndbg
'''

import gdb
import squ.gdb.types as types

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
def for_each_entry(head : gdb.Value, typename: str, field):
    addr = head["next"]
    while addr != head.address:
        yield container_of(addr, typename, field)
        addr = addr.dereference()["next"]

