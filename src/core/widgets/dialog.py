#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Widgets that provide information or ask some to the user. Content :
    - MessageDialog, to display information like errors or warnings
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore


class MessageDialog(QtWidgets.QMessageBox):
    """
    A customizable QMessageBox.
    """

    def __init__(self, **kwargs):
        """
        Create a new MessageDialog
        :param kwargs: a dict that can have this keys:
            - text : the text displayed
            - info : an additional text to inform
            - details : an more precise text
            - std_bts : a union of QMessageBox buttons
            - dft_bt : the default button
            - icon : icon displayed in the dialog
        """
        super().__init__()
        opts = {
            'text': 'default',
        }
        opts.update(kwargs)
        self.setText(opts['text'])
        self.setWindowTitle(opts['text'])

        try:
            self.setInformativeText(opts['info'])
        except:
            pass
        try:
            self.setDetailedText(opts['details'])
        except:
            pass
        try:
            self.setStandardButtons(opts['std_bts'])
        except:
            pass
        try:
            self.setDefaultButton(opts['dft_bt'])
        except:
            pass
        try:
            self.setIcon(opts['icon'])
        except:
            try:
                self.setIconPixmap(opts['icon'])
            except:
                pass

class AboutPlugins(QtWidgets.QWidget):
    """
    A dialog gather information about available plugins. Each plugin appears in a list on the
    left and information about it on the right. Use loaders to retrieve them.
    """

    def __init__(self, loaders, parent=None):
        """
        Create a new AboutPlugin Widget. Already populated at the beginning
        :param loaders: a list of loaded plugins (list<PluginLoader>)
        :param parent: parent of the widget
        """
        super().__init__(parent=parent, flags=QtCore.Qt.Widget)
        self._loaders = loaders
        self._create_view()
        self._place_components()
        self._create_controller()
        if len(self._loaders) > 0:
            self._plugin_list.setCurrentRow(0)

    def _create_view(self):
        """
        Create components on the view.
        """
        self._plugin_list = QtWidgets.QListWidget()
        self._plugin_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._plugin_list.setMaximumWidth(200)
        for loader in self._loaders:
            self._plugin_list.addItem(loader.plugin_name)

        self._authors = QtWidgets.QLabel()
        self._version = QtWidgets.QLabel()
        self._info = QtWidgets.QLabel()
        self._plugin_name = QtWidgets.QLabel()

    def _place_components(self):
        """
        Place components in the view.
        """
        main_grid = QtWidgets.QGridLayout(self)
        main_grid.addWidget(self._plugin_list, 0, 0)

        dummy = QtWidgets.QWidget(self)
        dummy_grid = QtWidgets.QGridLayout(dummy)
        dummy_grid.addWidget(self._plugin_name, 0, 0)
        dummy_grid.addWidget(self._version, 1, 0)
        dummy_grid.addWidget(self._authors, 2, 0)
        dummy_grid.addWidget(self._info, 3, 0)
        dummy.setLayout(dummy_grid)

        main_grid.addWidget(dummy, 0, 1)

        main_grid.setColumnStretch(0, 0)
        main_grid.setColumnStretch(1, 1)
        self.setLayout(main_grid)

    def _create_controller(self):
        """
        Connect signals and slots.
        """
        self._plugin_list.currentRowChanged.connect(self._update_info)

    def _update_info(self, row):
        """
        Update label to reflect selected plugin information.
        :param row: the selected row
        """
        loader = self._loaders[row]
        try:
            self._authors.setText('Authors : {}'.format(', '.join(loader.plugin_authors)))
        except Exception as e:
            print(str(e))
        self._version.setText('Version : {}'.format(loader.plugin_version))
        self._plugin_name.setText('Name : {}'.format(loader.plugin_name))
        self._info.setText('Information : {}'.format(loader.plugin_info))