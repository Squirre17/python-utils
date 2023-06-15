from enum import Enum
from typing import (Any, ByteString, Callable, Dict, Generator, Iterable,
                    Iterator, List, NoReturn, Optional, Sequence, Set, Tuple, Type,
                    Union, NewType)

import squ.utils.log as log
# import squ.gdb.arch  as arch
import squ.gdb.types as types

# from squ.gdb.config.command import Command
from squ.utils.color        import Color
from squ.utils.decorator    import handle_exception
from squ.gdb.disasm         import disassembler
from squ.gdb.instruction         import Instruction
from squ.gdb.address        import Address
# from squ.gdb.page           import Page
import squ.gdb.kernel.elf     as kelf

import squ.gdb.highlight as hl
import gdb
import squ.gdb.file
import squ.gdb.memory as mem
import squ.gdb.vmlayout as vmlayout
import squ.gdb.symbol 
from squ.gdb.symbol import Symbol

R = Color.redify



arrow_left = Color.purpleify('←')

arrow_right = Color.purpleify('→'),

recur_depth = 3



def __last_entry(addr_or_data : int) -> str:
    '''
    if a address is last entry of chain, 
    use left arrow and data or disasm or string.
    With prefix.
    ◂— mov    edi, eax
    ◂— '/home/squ/prac/a.out'
    ◂— 0x100000000
    '''
    symbol : Symbol = squ.gdb.symbol.get(addr_or_data) 

    readable = mem.can_access(addr_or_data)
    
    # if non-readable, `addr_or_data` is a only data
    if not readable:
        data = mem.reader.u64(addr_or_data)
        return str(arrow_left) + " %#x" %(data)
    
    else:
        addr = Address(addr_or_data)
        #  string 
        '''
        0x7fffffffd993 ◂— '/home/squ/prac/a.out'
              ↑
        '''
        string = mem.reader.string(addr)
        if string is not None:
            return str(arrow_left) + " " + '\'' + Color.boldify(string) + '\''

        # instruction
        # like : 0x4012dc <main+0> ← endbr64
        start, scope = kelf.get_text_section_info()
        if (start <= int(addr)) and (int(addr) < start + scope):
            # in .text section
            inst : Instruction = disassembler.get(addr)
            if inst:
                log.dbg("%s %s" % (inst.mnem, inst.operand))
            else:
                raise NotImplementedError
            return str(arrow_left) + " " + hl.asm("%s %s" % (inst.mnem, inst.operand))
        
        # simply data
        data = mem.reader.u64(addr_or_data)
        return str(arrow_left) + " %#x" %(data)


'''
input  : 0x7fffffffd938
return : [0x7ffff7de2083]

because : 0x7fffffffd938 → 0x7ffff7de2083
'''
def __recur_deref(addr : int, depth = recur_depth) -> List[int]:
    '''
    recursively dereference a address, return a list of addresses.
    don't including head currently.
    '''

    result = []
    for i in range(depth):

        # cycle refer
        if result.count(addr) >= 2:
            break
        
        try :
            
            addr = int(mem.deref(addr, types.voidpp))
            # TODO: if xor logic exist in hign version (tcache) ,handle it

            # cuz derefered result is either data or address, if it's data, handle it latter in __last_entry
            # if not pwnxy.vmmap.find(Address(addr)):
            #     logger.debug("not pwnxy.vmmap.find(%#x)" %addr)
            #     break

            # TODO: addr &= pwnxy.arch.ptrmask
            mask = ((1 << (64)) - 1)
            addr &= mask
            result.append(addr)

        except gdb.MemeoryError:
            # TODO: gdb.MemeoryError
            break
        except Exception as e:
            log.fatal(e)
    
    return result

# IDEA: latter can support multi addr pass in upstream 
'''
input 0x7fffffffd938 
0x7fffffffd938 → 0x7ffff7de2083 <__libc_start_main+243> ← mov edi,eax
'''
def generate(addr, depth = int(recur_depth)) -> str:
    '''
    generate a line of address chain, don't with prefix.
    '''
    '''
    0x7fffffffd578 —▸ 0x7ffff7de4083 (__libc_start_main+243) ◂— mov    edi, eax
    0x7fffffffd580 —▸ 0x7ffff7ffc620 (_rtld_global_ro) ◂— 0x50f5300000000
    0x7fffffffd588 —▸ 0x7fffffffd668 —▸ 0x7fffffffd993 ◂— '/home/squ/prac/a.out'
    0x7fffffffd590 ◂— 0x100000000
    '''
    addrs  : List[int] = __recur_deref(addr ,depth) # tuple is more proper??
    result : List[str] = [R("{:#x}".format(addr))]

    for addr in addrs:

        symbol : Symbol = squ.gdb.symbol.get(addr)
        if symbol :
            res = "%s %s" %(addr, str(symbol))
            # res = M.dyetext(res, addr)
        else:
            res = "{:#x}".format(addr)
        
        result.append(res)
        
        # TODO: colorify it
        
    result : str = (" " + str(arrow_right) + " ").join(result)

    if len(addrs) == 0:
        padding = __last_entry(addr)
    else:
        padding = __last_entry(addrs[-1])

    return result + " " + padding

