#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import os
import PyQt5.QtWidgets as Qtwidgets

class Launcher(object):
    """
    A launcher prepares the application : change current work directory, add source folder in 
    PYTHONPATH ...
    """

    def __init__(self):
        """
        Create a new Launcher. PYTHONPATH is set and current work directory has changed.
        :return: a new Launcher's instance
        """
        self._app_path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
        self._app = None
        self._main_widget = None

        # Change work directory
        os.chdir(self._app_path)

        # Add project to PYTHONPATH
        sys.path.append(self._app_path)

        # Add plugin folder to PYTHONPATH
        sys.path.append(os.path.join(self._app_path, 'extra'))

    @property
    def app_path(self):
        """
        Give the path to the application's main folder
        :return: a path (str)
        """
        return str(self._app_path)

    @property
    def main_app(self):
        """
        Give the main widget of the application. If the application is not started yet, return None.
        :return: src.core.gui.TwentyThreeTools' instance or None
        """
        return self._main_widget

    def launch_app(self):
        """
        Launch the application.
        :return: exit code of the application (int)
        """
        import src.core.app

        self._app = Qtwidgets.QApplication(sys.argv)
        self._main_widget = src.core.app.TwentyThreeTools()

        self._main_widget.show()
        return self._app.exec_()

if __name__ == '__main__':
    LAUNCHER = Launcher()
    sys.exit(LAUNCHER.launch_app())
