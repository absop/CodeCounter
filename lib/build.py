import sys
import os
from libs import object_files

if sys.platform in object_files:
    os.makedirs("shared-object", exist_ok=True)
    obj = "shared-object/" + object_files[sys.platform]
    os.system("gcc -fPIC -shared -O2 -DBUILD_SHARED_OBJECT src/lc.c -o " + obj)
