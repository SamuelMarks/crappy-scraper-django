from distutils.sysconfig import get_python_lib
from functools import partial
from os import path, listdir, environ
from platform import linux_distribution

listfiles = lambda dir_join: filter(
    lambda p: path.isfile(dir_join(p)) and path.splitext(p)[1] not in frozenset(
        ('.pyc', '.pyd', '.so', '.pyo')), listdir(dir_join())
)

