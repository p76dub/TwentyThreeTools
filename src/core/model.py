# -*- coding :utf-8 -*-
"""
Contain core's models :
    - TwentyThreeToolsModel
"""
import importlib.util
import PyQt5.QtCore as QtCore


class TwentyThreeToolsModel(QtCore.QObject):
    """
    TwentyThreeTools' model. Hold sessions and search for plugins.
    """

    def __init__(self):
        """
        Create a new TwentyThreeToolsModel. At the beginning, no sessions are stored. The list of available
        plugins has been build.
        """
        self._plugins = []
        self._sessions = []

    @QtCore.pyqtProperty(list)
    def plugins(self):
        """
        A list of available plugins.
        """
        return list(self._plugins)

    @QtCore.pyqtProperty(list)
    def session(self):
        """
        Get the active session.
        """
        return list(self._sessions)

    def _load_plugins(self):
        """
        Load available plugins.
        """
        pass
