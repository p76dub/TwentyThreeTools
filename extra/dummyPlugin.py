#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import src.core.model
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

__version__ = '1.1'


class DummyPlugin(QtWidgets.QWidget):
    """
    A dummy plugin, with nothing to show except a nice label.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent, flags=QtCore.Qt.Widget)
        self._create_view()
        self._place_components()

    def _create_view(self):
        """
        Create the poor label alone.
        """
        self._poor_label = QtWidgets.QLabel(text='Poor label here', parent=self)

    def _place_components(self):
        """
        Place the poor label in the view.
        """
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self._poor_label, 1, 1)


loader = src.core.model.PluginLoader(
    name='DummyPlugin',
    version=__version__,
    info='It\'s just a DummyPlugin, nothing to say !',
    authors=('p76dub'),
    plugin=DummyPlugin(),
)