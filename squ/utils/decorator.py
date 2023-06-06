import time
import functools
import squ.utils.log as log
import squ.gdb.proc as proc

from squ.utils.color import (Color)
from typing          import (Callable, Any)

def deprecated(func : Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        print(Color.redify(f"WARNING : this function `{func}` have been deprecated"))
        return func(*args, **kwargs)
    return wrapper

def timer(func : Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args , **kwargs) -> Any:
        start = time.time()
        ret = func(*args, **kwargs)
        end   = time.time()
        log.note("function {} spend {:0.8f} ms".format(func.__name__, (end - start) * 1000))
        return ret
    return wrapper

def debug_wrapper(func : Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args , **kwargs) -> Any:
        log.dbg(f"function -> {func.__name__} : START")
        ret = func(*args, **kwargs)
        log.dbg(f"function -> {func.__name__} : END")
        return ret
    return wrapper

import traceback
def handle_exception(func : Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args , **kwargs) -> Any:
        try :
            return func(*args, **kwargs)
        except Exception as e :
            log.err("Exception occur!")
            print(traceback.format_exc())
    return wrapper
