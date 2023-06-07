import gdb

u64p = gdb.lookup_type('unsigned long').pointer()

i8  = gdb.lookup_type('signed char')
i16 = gdb.lookup_type('short')
i32 = gdb.lookup_type('int')
i64 = gdb.lookup_type('long long')

u8  = gdb.lookup_type('unsigned char')
u16 = gdb.lookup_type('unsigned short')
u32 = gdb.lookup_type('unsigned int')
u64 = gdb.lookup_type('unsigned long long')

i8p  = i8.pointer() 
i16p = i16.pointer()
i32p = i32.pointer()
i64p = i64.pointer()

u8p  = u8.pointer()
u16p = u16.pointer()
u32p = u32.pointer()
u64p = u64.pointer()


assert i8.sizeof == 1
assert i16.sizeof == 2
assert i32.sizeof == 4
assert i64.sizeof == 8

assert u8.sizeof == 1
assert u16.sizeof == 2
assert u32.sizeof == 4
assert u64.sizeof == 8