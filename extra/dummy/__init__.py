#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import src.core.utils
import dummy.dummyPlugin

__version__ = '1.1'

loader = src.core.utils.PluginLoader(
    name='Test',  # No reason module's name is the same as plugin's name
    version=__version__,
    info='It\'s just a DummyPlugin, nothing to say !',
    authors=('p76dub'),
    plugin=dummy.dummyPlugin.DummyPlugin,
)