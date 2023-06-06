from typing import (Any, ByteString, Callable, Dict, Generator, Iterable,
                    Iterator, List, NoReturn, Optional, Sequence, Set, Tuple, Type,
                    Union, NewType)

import squ.utils.log as log

# 
def get(path : str) -> Optional[bytes] :
    '''
    get contents of the specified full local file path by binary
    TODO: considering remote ?
    '''
    try :
        with open(path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        log.err(f"TODO this {e}")

def get_text(path : str) -> Optional[str] :
    '''
    get contents of the specified full local file path by text
    '''
    try :
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        log.err(f"TODO this {e}")

# TODO:
def get_full_path(path) :
    ...