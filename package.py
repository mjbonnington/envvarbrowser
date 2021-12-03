# -*- coding: utf-8 -*-

name = 'ic_envvar'

version = '1.0.3'

description = 'Environment Variables Browser'

variants = [['python-2.7+']]

requires = ['ic_ui']

authors = ['mjbonnington']

build_command = 'python {root}/build.py {install}'


def commands():
    env.PATH.append("{root}")
    env.PYTHONPATH.append('{root}')
    env.IC_ICONPATH.append('{root}/icons')
