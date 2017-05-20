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

    def __init__(self, plugins=frozenset(['extra'])):
        """
        Create a new TwentyThreeToolsModel. At the beginning, no sessions are stored. The list of available
        plugins has been build.
        :arg plugins: a set of folders in which plugins are. Default is set(['extra'])
        """
        super().__init__()
        self._plugins = set()
        self._locations = set(plugins)
        self._loaded_modules = set()

        self._look_for_plugins()

    @property
    def plugins(self):
        """
        A list of available plugins.
        """
        return [cpl[0] for cpl in self._plugins]

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
                if filename != '__init__':
                    self._plugins.add((filename, dir))

        self.plugins_changed.emit(self.plugins)

    def load_plugin(self, index):
        """
        Load the plugin at index `index` in self.plugins.
        :param index: the index of the plugin (int)
        :return: an instance of the plugin (object) or None if not found
        """
        if 0 > index >= len(self._plugins):
            return None

        module_name, dir_path = self._plugins[index]

        # If module has been already loaded, return a new instance
        for mod in self._loaded_modules:
            if mod.__name__.split('.')[-1] == module_name:
                return getattr(mod, module_name.capitalize())()

        # Else load module, add it to the set and return the instance
        spec = importlib.util.spec_from_file_location(module_name,
                                                      os.path.join(dir_path, module_name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        self._loaded_modules.add(mod)
        return getattr(mod, module_name.capitalize())()


class TwentyThreeToolsMenuBarModel(QtCore.QObject):
    """
    This model manages the application's menubar. Menus are:
        - File
        - Plugins
    """

    close_app = QtCore.pyqtSignal()

    def __init__(self):
        """
        Create a new instance. At the beginning, File menu contains only one action : quit. 
        Plugins menu is empty.
        """
        super().__init__()
        self._menus = {
            'File' : self._create_file_menu(),
            'Plugins' : QtWidgets.QMenu('&Plugins'),
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
            menu.addAction(plugin)