from elftools.elf.elffile import ELFFile
import gdb
from typing import Tuple
import squ.utils.log as log

# path = "/home/squ/proj/akd-dev/tmp/vmlinux"
# with open(path, "rb") as f:
#     elffile = ELFFile(f)
#     for sec in elffile.iter_sections():
#         s = dict(sec.header)
#         if sec.name == ".text":
#             offset = s["sh_offset"]
#             start_address = s["sh_addr"]

#             print(hex(start_address))
#             print(hex(offset))

def get_text_section_info() -> Tuple[int, int]:
    
    progspace = gdb.current_progspace()
    with open(progspace.filename, "rb") as f:
        elffile = ELFFile(f)

        for sec in elffile.iter_sections():
            s = dict(sec.header)
            if sec.name == ".text":
                offset = s["sh_offset"]
                start  = s["sh_addr"]
            return (start, offset)
            
        log.fatal("can't found .text section in vmlinux {}".format(progspace.filename))