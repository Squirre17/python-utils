import gdb

endianness = ""
if gdb.lookup_type('int').sizeof == 4:
    endianness = "little"
else:
    endianness = "big"