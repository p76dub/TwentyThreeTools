#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import src.core.model
import dummy.dummyPlugin

__version__ = '1.1'

loader = src.core.model.PluginLoader(
    name='DummyPlugin',
    version=__version__,
    info='It\'s just a DummyPlugin, nothing to say !',
    authors=('p76dub'),
    plugin=dummy.dummyPlugin.DummyPlugin(),
)