from typing import (Any, ByteString, Callable, Dict, Generator, Iterable,
                    Iterator, List, NoReturn, Optional, Sequence, Set, Tuple, Type,
                    Union, NewType)
import enum
from squ.gdb.address import Address
import squ.gdb.symbol
import squ.utils.log as log

class inst_type(enum.Enum): # TEMP:
    COND_BRA = 1 # conditional branch
    DIRE_BRA = 2 # directly branch
    RET      = 2
    CALL     = 3
    OTHER    = 4
class Instruction:
    __bra_grp = [ inst_type.COND_BRA,
                  inst_type.DIRE_BRA, 
                  inst_type.RET     ,
                  inst_type.CALL    , ]
                  
    def __init__(self, addr    : int, 
                       mnem    : str, 
                       operand : str, 
                       length  : int):

        self.__addr              = addr
        self.__mnem              = mnem
        self.__operand           = operand
        self.__length            = length
        self.__insttype          = self.gettype()
        self.__dest    : Address = None             # e.g. jmp destination...  

        # automatous get instruction symbol rather than outer argu pass
        symbol = squ.gdb.symbol(addr)
        self.__symbol = str(symbol) or ""


        
    # TEMP
    def gettype(self) -> inst_type:
        if self.mnem.startswith("j"):
            if self.mnem.startswith("jmp"):
                return inst_type.DIRE_BRA
            return inst_type.COND_BRA
        elif self.mnem == "ret":
            return inst_type.RET
        elif self.mnem == "call":
            return inst_type.CALL
        else:
            return inst_type.OTHER
    @property
    def is_taken(self) -> bool:
        # TODO:
        return False
    @property
    def addr(self) :
        return self.__addr

    # '''
    # must lazy fetch destination
    # '''
    # @property
    # def dest(self) -> Optional[Address]:
    #     '''
    #     WARN: dest only can be invoked in current frame
    #           if mnem is `ret`, dest
    #     '''
    #     if self.is_branch :# b *0x401262
    #         # TODO: `call $rax` not consider
    #         log.dbg(f"mnem = {self.mnem} ,branch operand = {self.operand}")
    #         if self.is_ret:
    #             self.__dest = Address(pwnxy.reg.get_ra())
    #         else: # dire jmp ,cond jmp , call
    #             '''
    #             NOTE: but `call QWORD PTR [rip+0x2f12]` can't work well,
    #                   simply drop it
    #             '''
                
    #             # NOTE: dest can be None even if is_branch is True
    #             tmp = self.__operand.split()[0].strip()
    #             if all(x in "x1234567890abcdef" for x in tmp):# TEMP: remedy 
    #                 self.__dest = Address(self.__operand.split()[0].strip())

    #     return self.__dest
        
    @property
    def mnem(self) :
        return self.__mnem

    @property
    def operand(self) :
        return self.__operand

    @property
    def length(self) :
        return self.__length

    @property
    def symbol(self) :
        return self.__symbol
    
    @property
    def is_branch(self) -> bool :
        return self.__insttype in self.__bra_grp
    @property
    def next_addr(self) -> Address:
        '''
        return address of next instruction
        '''
        return Address(self.__addr + self.__length)
    @property
    def is_cond_branch(self) -> bool :
        '''
        whether is a conditional branch instruction
        '''
        return self.__insttype == inst_type.COND_BRA
    @property
    def is_dire_branch(self) -> bool :
        '''
        whether is a direct branch instruction
        '''
        return self.__insttype == inst_type.DIRE_BRA

    @property
    def is_call(self) -> bool :
        '''
        whether is a call instruction
        '''
        return self.__insttype == inst_type.CALL
    @property
    def is_ret(self) -> bool :
        '''
        whether is a ret instruction
        '''
        return self.__insttype == inst_type.RET    
    @property
    def branch_dest(self) -> Address :
        '''
        return a branch destination
        '''
        if self.is_cond_branch or self.is_dire_branch:
            return Address(self.__operand)
        elif self.is_call:
            log.err(f"not impl yet ,operand is {self.__operand}")
        elif self.is_ret :
            log.err(f"not impl ret yet ,operand is {self.__operand}")

    @addr.setter
    def addr(self, addr : int) :
        self.__addr = addr