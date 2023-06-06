from typing import (Any, ByteString, Callable, Dict, Generator, Iterable,
                    Iterator, List, NoReturn, Optional, Sequence, Set, Tuple, Type,
                    Union, NewType)
import gdb
import functools
import squ.utils.log as log

def is_alive() -> bool:
    return gdb.selected_thread() is not None

def only_if_running(func : Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if is_alive():
            return func(*args, **kwargs)
        else:
            log.warn("This program in not running")
    return wrapper