# -*- coding :utf-8 -*-
"""
Contain core's models :
    - TwentyThreeToolsModel
"""
import os
import importlib.util
import collections

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

import src.core.utils
import src.core.widgets.dialog
import src.core.widgets.session


class TwentyThreeToolsModel(QtCore.QObject):
    """
    TwentyThreeTools' model. Hold sessions and search for plugins.
    """

    ESCAPED = ['__init__', '__pycache__']
    locations_changed = QtCore.pyqtSignal(frozenset)
    plugins_changed = QtCore.pyqtSignal(list)

    def __init__(self, plugins=frozenset(['extra'])):
        """
        Create a new TwentyThreeToolsModel. At the beginning, no sessions are stored. The list
        of available plugins has been build.
        :arg plugins: a set of folders in which plugins are. Default is set(['extra'])
        :post:
            plugins contains available plugins
            locations == set(plugins)
        """
        super().__init__()
        self._plugins = dict()
        self._locations = set(plugins)
        self._loaded_modules = set()

        self._look_for_plugins()

    @property
    def plugins(self):
        """
        A list of available plugins.
        :return: a list of available plugins
        """
        return list(self._plugins.keys())

    @property
    def loaders(self):
        """
        A list of available loaders.
        :return: a list of loader (src.core.utils.PluginLoader)
        """
        return list(self._plugins.values())

    @property
    def locations(self):
        """
        A frozenset of locations where plugins are.
        :return: a frozenset of locations
        """
        return frozenset(self._locations)

    @locations.setter
    def locations(self, paths):
        """
        Set the new locations of plugins
        :param paths: folder names (iterable)
        :post:
            locations == set(paths)

        """
        self._locations = set(paths)
        self.locations_changed.emit(self._locations)

        self._plugins.clear()
        self._look_for_plugins()

    def _look_for_plugins(self):
        """
        Load available plugins. Search is based on filename and folders in self.locations
        """
        dirs = [os.path.join(os.getcwd(), directory) for directory in self.locations]

        for directory in dirs:
            for file in os.listdir(directory):
                filename = file.split('.')[0]
                if filename not in TwentyThreeToolsModel.ESCAPED:
                    self._get_loader(filename, directory)

        self.plugins_changed.emit(self.plugins)

    def _get_loader(self, name, directory):
        """
        Try to get the plugin's loader. In case of success, loader is added into self._plugins
        :param name: plugin's name (str)
        :param directory: plugin's location (path)
        """
        spec = importlib.util.spec_from_file_location(
                        name,
                        os.path.join(directory, name + '.py'))
        mod = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(mod)
        except FileNotFoundError:  # Complex plugin
            spec = importlib.util.spec_from_file_location(
                        name,
                        os.path.join(directory, name, '__init__.py'))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

        self._plugins[mod.loader.plugin_name] = mod.loader

    def load_plugin(self, name):
        """
        Load the plugin with the name 'name' in self.plugins
        :param name: the name of the plugin (str)
        :return: an instance of the plugin (PyQt5.QtWidgets.QWidget)
        :raise KeyError: plugin with name 'name' has not been found
        """
        return self._plugins[name].load()


class TwentyThreeToolsMenuBarModel(QtCore.QObject):
    """
    This model manages the application's menubar. Menus are:
        - File
        - Plugins
    """

    close_app = QtCore.pyqtSignal()
    about_plugins = QtCore.pyqtSignal()
    plugin_selected = QtCore.pyqtSignal(str)

    def __init__(self):
        """
        Create a new instance. At the beginning, File menu contains only one action : quit. 
        Plugins menu is empty.
        """
        super().__init__()
        self._menus = collections.OrderedDict()
        self._menus['File'] = self._create_file_menu()
        self._menus['Plugins'] = QtWidgets.QMenu('&Plugins')
        self._menus['About'] = self._create_about_menu()

    def get_menus(self):
        """
        Get menus.
        :return: A menu list (list<QMenu>)
        """
        rtn = [menu for _, menu in self._menus.items()]
        return rtn

    def _create_file_menu(self):
        """
        Create the file menu
        :return: a QMenu instance.
        """
        menu = QtWidgets.QMenu('&File')

        quit_a = menu.addAction('&Quit')
        quit_a.triggered.connect(lambda event: self.close_app.emit())

        return menu

    def _create_about_menu(self):
        """
        Create the about menu
        :return: a QMenu instance
        """
        menu = QtWidgets.QMenu('&About')

        plugins = menu.addAction('&Plugins')
        plugins.triggered.connect(lambda event: self.about_plugins.emit())

        return menu

    @QtCore.pyqtSlot(list, name='plugins')
    def plugins(self, plugins_list):
        """
        These slot accept a list<str> object and updates the plugins menu in consequence.
        :param plugins_list: the list of plugins (list<str>)
        """
        menu = self._menus['Plugins']
        menu.clear()

        for plugin in plugins_list:
            action = self._create_plugin_action(plugin)
            action.setParent(menu)
            menu.addAction(action)

    def _create_plugin_action(self, plugin):
        """
        Create the action for the plugin `plugin`
        :param plugin: name of the plugin
        :return: a QAction
        """
        action = QtWidgets.QAction()
        action.setText(plugin)
        action.triggered.connect(lambda e: self.plugin_selected.emit(plugin))

        return action


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
        self._model = TwentyThreeToolsModel()
        self._menu_model = TwentyThreeToolsMenuBarModel()

    def _create_view(self):
        """
        Create each graphical component.
        """
        self._plugin_view = QtWidgets.QStackedWidget()
        self._plugin_view.setMinimumSize(600, 500)

        self._sessions = src.core.widgets.session.SessionWidget()

        for menu in self._menu_model.get_menus():
            self.menuBar().addMenu(menu)

        self._about_plugins_dialog = src.core.widgets.dialog.AboutPlugins(self._model.loaders)

        self.setWindowTitle('TwentyThreeTools')

    def _place_components(self):
        """
        Place components on the widget.
        """
        layout = QtWidgets.QGridLayout()
        main_widget = QtWidgets.QWidget(self, flags=QtCore.Qt.Widget)

        layout.addWidget(self._sessions, 0, 0)
        layout.addWidget(self._plugin_view, 0, 1)

        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def _create_controller(self):
        """
        Create links between models and graphical components.
        """
        self._menu_model.close_app.connect(self.close)
        self._menu_model.plugin_selected.connect(self._add_plugin_to_session)
        self._menu_model.about_plugins.connect(self._about_plugins)

        self._model.plugins_changed.connect(self._menu_model.plugins)

        self._sessions.row_changed.connect(self._plugin_view.setCurrentIndex)
        self._sessions.row_removed.connect(self._remove_widget)

    def _add_plugin_to_session(self, plugname):
        """
        Add the plugin with name `plugname` to the list of opened sessions and select it.
        :param plugname: the name of the desired plugin (str)
        """
        try:
            plugin = self._model.load_plugin(plugname)
        except Exception as e:
            src.core.widgets.dialog.MessageDialog(
                text='An error occurs',
                info='The plugin {} can\'t be loaded, please check your extra folder.'
                    .format(plugname),
                details='Error : {}'.format(str(e)),
                icon=QtWidgets.QMessageBox.Critical,
            ).exec_()
        else:
            self._sessions.get_model().add_item(plugin, plugname)
            self._plugin_view.addWidget(plugin)

    def _about_plugins(self):
        """
        Show a window with information about detected plugins.
        """
        self._about_plugins_dialog.show()

    def _first_update(self):
        """
        Updates view according to models state (also update some models according to others)
        """
        self._menu_model.plugins(self._model.plugins)

    @QtCore.pyqtSlot(int, name='_remove_widget')
    def _remove_widget(self, index):
        """
        Remove widget in QStackedWidget at position index
        :param index: int
        """
        widget = self._plugin_view.widget(index)
        self._plugin_view.removeWidget(widget)
