from typing import (Any, ByteString, Callable, Dict, Generator, Iterable,
                    Iterator, List, NoReturn, Optional, Sequence, Set, Tuple, Type,
                    Union, NewType)
import squ.gdb.file
import squ.utils.log as log
import gdb
import squ.gdb.types as types
from squ.utils.color import Color
import squ.gdb.kernel.utils as utils


def get_current_cpu() -> int:
    assert utils.probe_qemu()
    return gdb.selected_thread().num - 1

'''
pwndbg> p/x __per_cpu_offset
$7 = {0xffff88800f400000, 0xffffffff82b01000 <repeats 63 times>}
'''
def per_cpu(var_ptr : gdb.Value, cpu = -1) -> gdb.Value:
    '''
    pass in a per-cpu ptr, and return a derefered value
    '''
    if cpu == -1:
        cpu = get_current_cpu()

    try:
        offset = gdb.parse_and_eval(
            "__per_cpu_offset[{0}]".format(str(cpu)))
    except gdb.error:
        # !CONFIG_SMP case
        offset = 0

    pointer = var_ptr.cast(types.u64) + offset
    return pointer.cast(var_ptr.type).dereference()

# TODO: modify to cmd and provide interface
# TODO: use selfr-wrappered Argument to register this
class PerCpu(gdb.Function):
    """Return per-cpu variable.

    $lx_per_cpu("VAR"[, CPU]): Return the per-cpu variable called VAR for the
    given CPU number. If CPU is omitted, the CPU of the current context is used.
    Note that VAR has to be quoted as string."""

    def __init__(self):
        super(PerCpu, self).__init__("lx_per_cpu")

    def invoke(self, var_name, cpu=-1):
        var_ptr = gdb.parse_and_eval("&" + var_name.string())
        return per_cpu(var_ptr, cpu)

PerCpu()

