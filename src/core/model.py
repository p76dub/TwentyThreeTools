# -*- coding :utf-8 -*-
"""
Contain core's models :
    - TwentyThreeToolsModel
"""
import os
import importlib.util
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets


class TwentyThreeToolsModel(QtCore.QObject):
    """
    TwentyThreeTools' model. Hold sessions and search for plugins.
    """

    locations_changed = QtCore.pyqtSignal(frozenset)
    plugins_changed = QtCore.pyqtSignal(list)
    sessions_updated = QtCore.pyqtSignal(dict)

    def __init__(self, plugins=frozenset(['extra'])):
        """
        Create a new TwentyThreeToolsModel. At the beginning, no sessions are stored. The list of available
        plugins has been build.
        :arg plugins: a set of folders in which plugins are. Default is set(['extra'])
        :post:
            
        """
        super().__init__()
        self._plugins = dict()
        self._locations = set(plugins)
        self._loaded_modules = set()
        self._sessions = dict()

        self._look_for_plugins()

    @property
    def sessions(self):
        """
        Sessions' dictionnary : name (str) -> session (object)
        :return: dict of sessions 
        """
        return dict(self._sessions)

    @property
    def plugins(self):
        """
        A list of available plugins.
        """
        return list(self._plugins.keys())

    @property
    def locations(self):
        """
        A frozenset of locations where plugins are.
        :return: a frozenset
        """
        return frozenset(self._locations)

    @locations.setter
    def locations(self, paths):
        """
        Set the new locations of plugins
        :param paths: folder names (iterable)
        """
        self._locations = frozenset(paths)
        self.locations_changed.emit(self._locations)

        self._loaded_modules.clear()
        self._plugins.clear()
        self._look_for_plugins()

    def _look_for_plugins(self):
        """
        Load available plugins. Search is based on filename and folders in self.locations
        """
        dirs = [os.path.join(os.getcwd(), dir) for dir in self.locations]

        for dir in dirs:
            for file in os.listdir(dir):
                filename = file.split('.')[0]
                if os.path.isfile(os.path.join(dir, file)) and filename != '__init__':
                    self._plugins[filename] = dir

        self.plugins_changed.emit(self.plugins)

    def load_plugin(self, name):
        """
        Load the plugin at index `index` in self.plugins.
        :param name: the name of the plugin (str)
        :return: an instance of the plugin (object)
        :raise KeyError: plugin with name `name` has not been found
        """
        module_name, dir_path = name, self._plugins[name]

        # If module has been already loaded, return a new instance
        for mod in self._loaded_modules:
            if mod.__name__.split('.')[-1] == module_name:
                plugin = getattr(mod, module_name.capitalize())()
                self._sessions[module_name + str(hash(plugin))] = plugin
                self.sessions_updated.emit(self.sessions)
                return module_name + str(hash(plugin))

        # Else load module, add it to the set and return the instance
        spec = importlib.util.spec_from_file_location(module_name,
                                                      os.path.join(dir_path, module_name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self._loaded_modules.add(mod)

        plugin = getattr(mod, module_name.capitalize())()
        self._sessions[module_name + str(hash(plugin))] = plugin
        self.sessions_updated.emit(self.sessions)
        return module_name + str(hash(plugin))


class TwentyThreeToolsMenuBarModel(QtCore.QObject):
    """
    This model manages the application's menubar. Menus are:
        - File
        - Plugins
    """

    close_app = QtCore.pyqtSignal()
    plugin_selected = QtCore.pyqtSignal(str)

    def __init__(self):
        """
        Create a new instance. At the beginning, File menu contains only one action : quit. 
        Plugins menu is empty.
        """
        super().__init__()
        self._menus = {
            'File': self._create_file_menu(),
            'Plugins': QtWidgets.QMenu('&Plugins'),
        }

    def get_menus(self):
        """
        Get menus.
        :return: A menu list (list<QMenu>)
        """
        rtn = [menu for _, menu in self._menus.items()]
        rtn.sort(key=lambda m: m.title())
        return rtn

    def _create_file_menu(self):
        """
        Create the file menu
        :return: a QMenu instance.
        """
        menu = QtWidgets.QMenu('&File')

        quit = menu.addAction('&Quit')
        quit.triggered.connect(lambda event: self.close_app.emit())

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
