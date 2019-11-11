import os
import ctypes
import sys
import sublime

if os.name == "nt":
    from _ctypes import FreeLibrary as _dlclose
elif os.name == "posix":
    from _ctypes import dlclose as _dlclose

from .libs import object_files

_module = None
foreign_function = None
path_encoding = 'utf-8'

def count(filename):
    return foreign_function(bytes(filename, encoding=path_encoding))


def set_encoding(encoding):
    global path_encoding
    path_encoding = encoding

def package_path():
    this = os.path.join("Packages", "CodeCounter")
    return this

def cache_path():
    cache = sublime.cache_path()
    this = os.path.join(cache, "CodeCounter")
    os.makedirs(this, exist_ok=True)
    return this


def load_binary():
    global _module, foreign_function
    _nodes = ["lib", "shared-object", object_files[sys.platform]]
    _object = os.path.join(package_path(), *_nodes)
    _bytes = sublime.load_binary_resource(_object)
    _cahce = os.path.join(cache_path(), "lc.so")

    with open(_cahce, "wb+") as file:
        file.write(_bytes)

    _module = ctypes.cdll.LoadLibrary(_cahce)

    foreign_function = _module.lines_count
    foreign_function.argtypes = (ctypes.POINTER(ctypes.c_char),)
    foreign_function.restype = ctypes.c_int

def unload_binary():
    try:
        _dlclose(_module._handle)
    except Exception as e:
        raise IOError("Could not unload shared object library.")
