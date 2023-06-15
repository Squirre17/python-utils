from enum import Enum
from typing import (Any, ByteString, Callable, Dict, Generator, Iterable,
                    Iterator, List, NoReturn, Optional, Sequence, Set, Tuple, Type,
                    Union, NewType)

import squ.utils.log as log
# import squ.gdb.arch  as arch
# import squ.gdb.types as types

# from squ.gdb.config.command import Command
# from squ.utils.color        import Color
# from squ.utils.decorator    import handle_exception
from squ.gdb.address        import Address
# from squ.gdb.page           import Page
# import squ.gdb.kernel.elf     as kelf


# import squ.gdb.highlight as hl
import gdb
# import squ.gdb.file
# import squ.gdb.memory as mem
import squ.gdb.vmlayout as vmlayout
# import squ.gdb.symbol 
from squ.gdb.symbol import Symbol
from squ.gdb.instruction import Instruction


from collections import defaultdict

backward_num =  5
# Parameter(
#     argname      = "disasm-backward-num",
#     default_val  = 5,
#     docdesc      = "disassembly instruction backward count in DISASM context"
# )

forward_num = 5
# Parameter(
    # argname      = "disasm-forward-num",
    # default_val  = 8,
    # docdesc      = "disassembly instruction forward count in DISASM context"
# )

# TODO: internel use , add underscore
# instantiate it to object
class InstructionCache:
    '''
    instruction cache manager : map addr -> previous instruction
    '''
    addr2previnst : "defaultdict[int, Instruction]"
    def __init__(self) :
        self.addr2previnst = defaultdict(lambda : None)

    def push2cache(self, insts : List[Instruction] = None) -> None:
        '''
        push a list of instruction into InstCacheMngr
        '''
        if len(insts) == 0 or len(insts) == 1 :
            return 

        prev_inst = insts[0]
        for inst in insts[1:] :
            self.addr2previnst[inst.addr] = prev_inst
            prev_inst = inst

        next_addr = prev_inst.addr + prev_inst.length
        self.addr2previnst[next_addr] = prev_inst

    def backward_fetch(self, addr : int, count = 3) -> List[Instruction]:
        '''
        backward fetch instructions except instruction in addr
        '''
        insts : Instruction = []
        prev_inst = self.addr2previnst[addr]

        while count != 0 and prev_inst != None :
            insts.append(prev_inst)
            prev_inst = self.addr2previnst[prev_inst.addr]
            count -= 1
            
        return insts
    
class Disassembler(InstructionCache):
    '''
    interactive with gdb or externel disassembler
    In charge of instruction read 
    TODO: capstone
    '''
    def __init__(self) :
        super().__init__()

    def get(self, addr : Address, count : int = 1) -> Union[List[Instruction], Instruction] :
        '''
        `get` can take in data of Address obj,
        temporary use gdb internal disassembler
        if count not specify(default to 1), return a Instruction rather than a List
        '''
        addr = int(addr)
        
        # try to set flavor to intel
        try :
            gdb.execute("set disassembly-flavor intel")
        except gdb.error :
            log.err("TODO: intel flavor")
        try :
            arch = gdb.selected_frame().architecture()
        except Exception as e :
            log.fatal(e)

        '''arch.disassemble return List[Dict[str, obj]]
        [
            {'addr': 4198742, 'asm': 'endbr64 ', 'length': 4},
            {'addr': 4198746, 'asm': 'push   %rbp', 'length': 1},
            {'addr': 4198747, 'asm': 'mov    %rsp,%rbp', 'length': 3}, 
            {'addr': 4198750, 'asm': 'mov    $0x8,%edx', 'length': 5}
        ]
        '''
        instructions : List[Type["Instruction"]] = []
        # + 10 for cache need
        for ins in arch.disassemble(start_pc = addr, count = count + 10):
            addr = ins["addr"]
            '''
            The rstrip() method removes any trailing characters (characters at the end a string), space is the default trailing character to remove.
            '''
            asm = ins["asm"].rstrip().split(None, 1)
            if len(asm) > 1:
                mnem, operand = asm
            else :
                mnem, operand = asm[0], ""
            length = ins["length"]
            # IDEA: maybe can create a address obj
            instructions.append(Instruction(addr, mnem, operand, length))
        
        self.push2cache(instructions)
        if count == 1:
            return instructions[0]
        return instructions[0 : count]
        
    def nearpc(self) -> List[Instruction]:
        '''
        get instructions near the PC, backward is executed instructions
        forward
        '''
        # TODO: check the pc validity
        # TODO: maybe pc can directly obtain don't need of arg
        try:
            pc = int(gdb.selected_frame().pc())
        except Exception as e:
            log.fatal(e)
        '''
        NOTE: pwndbg use unicore to emulate execute for branch predict which I don't support now
              so I only get branch instruction in call
        '''
        passed_insts = self.backward_fetch(pc, int(backward_num))
        cur : Instruction = self.get(pc)
        fwd_insts : List[Instruction] = [cur]

        for _ in range(int(forward_num)):
            if cur.is_call and cur.dest is not None:
                log.dbg(f"cur.dest = {str(cur.dest)}")
                cur = self.get(cur.dest)
            cur = self.get(cur.next_addr)
            fwd_insts.append(cur)
        
        return passed_insts + fwd_insts


disassembler = Disassembler()


