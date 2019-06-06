from ast import parse
from distutils.sysconfig import get_python_lib
from functools import partial
from os import path, listdir, makedirs, environ
from platform import python_version_tuple, linux_distribution
from shutil import copy

from setuptools import setup, find_packages

if python_version_tuple()[0] == '3':
    imap = map
    ifilter = filter
else:
    from itertools import imap, ifilter

listfiles = lambda dir_join: filter(
    lambda p: path.isfile(dir_join(p)) and path.splitext(p)[1] not in frozenset(
        ('.pyc', '.pyd', '.so', '.pyo')), listdir(dir_join())
)
slatteryit_pkg_join = partial(path.join, path.join(get_python_lib(
    plat_specific=True,
    prefix='/usr/local' if not environ.get('VIRTUAL_ENV') and linux_distribution()[0] == 'Ubuntu'
    else environ.get('VIRTUAL_ENV')), ))

if __name__ == '__main__':
    package_name = 'alpha_scraper'

    with open(path.join(package_name, '__init__.py')) as f:
        __author__, __version__ = imap(
            lambda buf: next(imap(lambda e: e.value.s, parse(buf).body)),
            ifilter(lambda line: line.startswith('__version__') or line.startswith('__author__'), f)
        )

    to_funcs = lambda *paths: (partial(path.join, path.dirname(__file__), package_name, *paths),
                               partial(path.join, get_python_lib(prefix=''), package_name, *paths))
    _data_join, _ = to_funcs('_data')

    slatteryit_data_join = partial(path.join, _data_join(), 'slatteryit')

    _data_install_dir = partial(path.join, slatteryit_pkg_join(), package_name, '_data')
    slatteryit_install_dir = partial(path.join, slatteryit_pkg_join(), package_name, '_data', 'slatteryit')

    if not path.isdir(slatteryit_install_dir()):
        makedirs(slatteryit_install_dir())
    tuple(imap(lambda fname: copy(slatteryit_data_join(fname), slatteryit_install_dir(fname)),
               listfiles(slatteryit_data_join)))

    tuple(imap(lambda fname: copy(_data_join(fname), _data_install_dir(fname)),
               listfiles(_data_join)))

    setup(
        name=package_name,
        author=__author__,
        version=__version__,
        description='Crappy spider scraper: Django edition',
        classifiers=[
            'Development Status :: 7 - Inactive',
            'Intended Audience :: Developers',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: MIT License',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 2 :: Only'
        ],
        install_requires=['pyyaml'],
        test_suite=package_name + '.tests',
        packages=find_packages(),
        package_dir={package_name: package_name},
        data_files=[
            # (_data_install_dir(), listfiles(_data_join)),
            # (slatteryit_install_dir(), ),
            # ('scrapy.cfg', 'scrapy.cfg')
        ]
    )
