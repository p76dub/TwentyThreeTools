#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Every extra objects without GUI that is required.
Content :
    - PluginLoader, make your plugin available
"""
import PyQt5.QtWidgets as QtWidgets


class PluginLoader(object):
    """
    Class that every plugin needs to instantiate. This instance should be available in the __init__
    file of the plugin's package.
    """

    def __init__(self, **kwargs):
        """
        Create a new instance of PluginLoader.
        :param kwargs: dictionary that can contain this pairs:
            - name -> str
            - version -> str
            - info -> str
            - authors -> tuple<str>
            - plugin -> PyQt5.QtWidgets.QWidget.__class__
        """
        self._attributes = {
            'name': str(hash(self)),
            'version': 'unknown',
            'info': 'No information',
            'authors': (),
            'plugin': QtWidgets.QWidget,
        }

        self._attributes.update(kwargs)

    @property
    def plugin_name(self):
        """
        Get the plugin's name.
        :return: a name (str)
        """
        return str(self._attributes['name'])

    @property
    def plugin_version(self):
        """
        Get the plugin's version.
        :return: a version number (str)
        """
        return str(self._attributes['version'])

    @property
    def plugin_info(self):
        """
        Get some information about the plugin.
        :return: a description of the plugin (str)
        """
        return str(self._attributes['info'])

    @property
    def plugin_authors(self):
        """
        Get plugin's author(s).
        :return: a tuple of authors (tuple<str>)
        """
        return tuple(map(str, self._attributes['authors']))

    def load(self):
        """
        Load the plugin.
        :return: an instance of PyQt5.QtWidgets.QWidget
        """
        return self._attributes['plugin']()
