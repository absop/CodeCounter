from .logging import Loger
from . import lc


def strsize(bytesize):
    k = 0
    while bytesize >> (k + 10):
        k += 10
    units = ("B", "KB", "MB", "GB")
    size_by_unit = round(bytesize / (1 << k), 2) if k else bytesize
    return str(size_by_unit) + units[k // 10]
