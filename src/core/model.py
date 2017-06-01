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
import collections


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
        dirs = [os.path.join(os.getcwd(), dir) for dir in self.locations]

        for dir in dirs:
            for file in os.listdir(dir):
                filename = file.split('.')[0]
                if filename not in TwentyThreeToolsModel.ESCAPED:
                    self._get_loader(filename, dir)

        self.plugins_changed.emit(self.plugins)

    def _get_loader(self, name, dir):
        """
        Try to get the plugin's loader. In case of success, loader is added into self._plugins
        :param name: plugin's name (str)
        :param dir: plugin's location (path)
        """
        spec = importlib.util.spec_from_file_location(
                        name,
                        os.path.join(dir, name + '.py'))
        mod = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(mod)
        except FileNotFoundError:  # Complex plugin
            spec = importlib.util.spec_from_file_location(
                        name,
                        os.path.join(dir, name, '__init__.py'))
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


class SessionModel(QtCore.QObject):
    """
    A SessionModel is the model of the widget SessionWidget.
    :inv:
        item_count() >= 0
        get_list_model() is not None
    """

    item_removed = QtCore.pyqtSignal(int, QtWidgets.QWidget)

    def __init__(self, parent=None):
        """
        Create a new empty SessionModel.
        :parent: owner of the instance
        :post:
            item_count() == 0
        """
        super().__init__(parent=parent)
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

        self._list_model.removeRow(index)
        self.item_removed.emit(index, self._sessions.pop(index))

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

        quit = menu.addAction('&Quit')
        quit.triggered.connect(lambda event: self.close_app.emit())

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


class PluginLoader():
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
            'name' : str(hash(self)),
            'version' : 'unknown',
            'info' : 'No information',
            'authors' : (),
            'plugin' : QtWidgets.QWidget,
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