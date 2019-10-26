import os
import ctypes
import sys
import sublime

libs = {
    "win32": "win_lc.so",
    "linux":  "linux_lc.so",
    "darwin": "osx_lc.so",
    "cygwin":  "linux_lc.so"
}

# Try to locate the .so file in the same directory as this file
_file = "shared-object/" + libs[sys.platform]
_path = os.path.join(*(os.path.split(__file__)[:-1] + (_file,)))
_module = ctypes.cdll.LoadLibrary(_path)

# int lines_count(const char *filename)
lc = _module.lines_count
lc.argtypes = (ctypes.POINTER(ctypes.c_char),)
lc.restype = ctypes.c_int


lc_path_encoding = 'utf-8'


def set_encoding(encoding):
    global lc_path_encoding
    lc_path_encoding = encoding


def count(filename):
    return lc(bytes(filename, encoding=lc_path_encoding))
