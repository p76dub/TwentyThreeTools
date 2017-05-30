# -*- coding :utf-8 -*-
"""
Contain core's models :
    - TwentyThreeToolsModel
"""
import os
import importlib.util
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui


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
            sessions == dict()
            plugins contains available plugins
            locations == set(plugins)
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
        :return: a list of available plugins
        """
        return list(self._plugins.keys())

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


class SessionModel():
    """
    A SessionModel is the model of the widget SessionWidget.
    :inv:
        item_count() >= 0
        get_list_model() is not None
    """

    def __init__(self):
        """
        Create a new empty SessionModel.
        :post:
            item_count() == 0
        """
        self._list_model = QtGui.QStandardItemModel()
        self._sessions = list()

    def item_count(self):
        """
        Give the amount of items in the list.
        :return: a positive integer
        """
        return len(self._sessions)

    def get_list_model(self):
        """
        Get the QStandardItemModel to connect it with the view.
        :return: the model (QStandradItemModel)
        """
        return self._list_model

    def get_value_at(self, index):
        """
        Get the value at position index.
        :param index: the index of the value looked
        :return: the value stored
        """
        if index < 0 or index >= self.item_count():
            raise ValueError('index should be between 0 and {} (inclusive)'
                             .format(self.item_count() - 1))

        return self._sessions[index]

    def add_item(self, value, str_value=None):
        """
        Add an item at the end of the list. If str_value is not provided, str(value) will be used.
        :post:
            item_count() == old item_count() + 1
            get_list_model() == old get_list_model()
            forall i in [0..old item_count()[:
                get_value_at(i) == old get_value_at(i)
            get_value_at(old item_count()) == value
            the correct value is displayed
        :param value: value that can be retrieved
        :param str_value: text displayed in the list view (optional)
        """
        displayed_text = str_value if str_value is not None else str(value)
        item = QtGui.QStandardItem()
        item.setText(displayed_text)
        self._list_model.appendRow(item)
        self._sessions.append(value)

    def remove_item(self, index):
        """
        Remove item at position index
        :pre:
            0 <= index < item_count()
        :post:
            item_count() == old item_count() - 1
            get_list_model() == old get_list_model()
            forall i in [0..item_count()[
                i < index => get_value_at(i) == old get_value_at(i)
                i >= index => get_value_at(i) == ols get_value_at(i + 1)
            texts displayed have shifted after position index - 1
        :param index: item's position that will be removed. Items after that position will be
            shifted
        """
        if index < 0 or index >= self.item_count():
            raise ValueError('index should be between 0 and {} (inclusive)'
                             .format(self.item_count() - 1))

        try:
            self._list_model.removeRow(index)
        except Exception as e:
            print(str(e))
        self._sessions.pop(index)

    def set_text_at(self, index, text):
        """
        Set the list entry text at position index.
        :pre:
            0 <= index < item_count()
        :post:
            item_count() == old item_count()
            get_list_model() == old get_list_model()
            forall i in [0..item_count()[:
                get_value_at(i) == old get_value_at(i)
            text displayed at position index is now text
        :param index: the position
        :param text: the new text
        """
        if index < 0 or index >= self.item_count():
            raise ValueError('index should be between 0 and {} (inclusive)'
                             .format(self.item_count() - 1))

        item = QtGui.QStandardItem()
        item.setText(text)
        self._list_model.setItem(index, item)


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
