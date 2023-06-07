import gdb

def probe_qemu():
    try:
        return gdb.execute("monitor info version", to_string=True) != ""
    except gdb.error:
        return False
    

def get_gdbserver_type():
    if probe_qemu():
        return