# -*- coding: utf-8 -*-

name = 'ic_envvar'

version = '1.0.6'

description = 'Environment Variables Browser'

authors = ['mjbonnington']

requires = ['ic_ui-2+']

build_requires = [
    'rezlib', 
]

build_command = 'python -m build {install}'


def commands():
    env.PATH.append("{root}")
    env.PYTHONPATH.append('{root}')
    env.IC_ICONPATH.append('{root}/icons')
