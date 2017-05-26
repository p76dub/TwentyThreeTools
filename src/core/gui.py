#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Module that contains everything related to the Graphical User Interface of the main application.
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import src.core.model


class TwentyThreeTools(QtWidgets.QMainWindow):
    """
    The GUI of the main application.
    """

    def __init__(self):
        """
        Create a new TwentyThreeTools widget.
        :return: a new instance of TwentyThreeTools
        """
        super().__init__(flags=QtCore.Qt.Window)
        self._create_model()
        self._create_view()
        self._place_components()
        self._create_controller()
        self._first_update()

    def _create_model(self):
        """
        Create the model associated to the graphical interface.
        """
        self._model = src.core.model.TwentyThreeToolsModel()
        self._menu_model = src.core.model.TwentyThreeToolsMenuBarModel()

    def _create_view(self):
        """
        Create each graphical component.
        """
        self._plugin_view = QtWidgets.QStackedWidget()

        self._sessions = QtWidgets.QListWidget()

        self._main_view = QtWidgets.QSplitter(self)
        self._main_view.setStretchFactor(0, 1)
        self._main_view.setStretchFactor(1, 3)

        for menu in self._menu_model.get_menus():
            self.menuBar().addMenu(menu)

        self.setWindowTitle('TwentyThreeTools')

    def _place_components(self):
        """
        Place components on the widget.
        """
        self._main_view.addWidget(self._sessions)
        self._main_view.addWidget(self._plugin_view)

        self.setCentralWidget(self._main_view)

    def _create_controller(self):
        """
        Create links between models and graphical components.
        """
        self._menu_model.close_app.connect(self.close)
        self._model.plugins_changed.connect(self._menu_model.plugins)
        self._menu_model.plugin_selected.connect(self._add_plugin_to_session)
        self._sessions.currentRowChanged.connect(self._plugin_view.setCurrentIndex)

    def _add_plugin_to_session(self, plugname):
        """
        Add the plugin with name `plugname` to the list of opened sessions and select it.
        :param plugname: the name of the desired plugin (str)
        """
        try:
            name = self._model.load_plugin(plugname)
        except Exception as e:
            self._show_message(
                text='An error occurs',
                info='The plugin {} can\'t be loaded, please check your extra folder.'
                    .format(plugname),
                details='Error : {}'.format(str(e)),
                icon=QtWidgets.QMessageBox.Critical,
            )
        else:
            self._sessions.addItem(name)
            self._plugin_view.addWidget(self._model.sessions[name])


    def _first_update(self):
        """
        Updates view according to models state (also update some models according to others)
        """
        self._menu_model.plugins(self._model.plugins)

    def _show_message(self, **options):
        """
        Show a dialog to inform the client that something append.
        :param options: a dict that can have this keys:
            - text : the text displayed
            - info : an additional text to inform
            - details : an more precise text
            - std_bts : a union of QMessageBox buttons
            - dft_bt : the default button
            - icon : icon displayed in the dialog
        :return: return value of the dialog execution 
        """
        opts = {
            'text': 'default',
        }
        opts.update(options)

        dialog = QtWidgets.QMessageBox()
        dialog.setText(opts['text'])
        dialog.setWindowTitle(opts['text'])

        try:
            dialog.setInformativeText(opts['info'])
        except:
            pass

        try:
            dialog.setDetailedText(opts['details'])
        except:
            pass

        try:
            dialog.setStandardButtons(opts['std_bts'])
        except:
            pass

        try:
            dialog.setDefaultButton(opts['dft_bt'])
        except:
            pass

        try:
            dialog.setIcon(opts['icon'])
        except:
            try:
                dialog.setIconPixmap(opts['icon'])
            except:
                pass

        return dialog.exec_()
