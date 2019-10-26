import sys
import os

libs = {
    "win32": "win_lc.so",
    "linux":  "linux_lc.so",
    "darwin": "osx_lc.so",
    "cygwin":  "linux_lc.so"
}

if sys.platform in libs:
    os.makedirs("shared-object", exist_ok=True)
    lib = "shared-object/" + libs[sys.platform]
    os.system("gcc -fPIC -shared -O2 -DBUILD_SHARED_OBJECT src/lc.c -o " + lib)
