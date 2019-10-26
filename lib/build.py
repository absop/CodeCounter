import sys
import os

libs = {
    "darwin": "osx_lc.so",
    "win32": "win32_lc.so",
    "linux":  "linux_lc.so",
    "cygwin":  "cygwin_lc.so"
}

if sys.platform in libs:
    os.makedirs("shared-object", exist_ok=True)
    lib = "shared-object/" + libs[sys.platform]
    os.system("gcc -fPIC -shared -O2 -DBUILD_SHARED_OBJECT src/lc.c -o " + lib)
