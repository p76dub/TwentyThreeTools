#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Contains everything related to the bean SessionWidget :
    - SessionWidget, the view
    - SessionWidgetModel, the model
    - _SessionHandler, the controller
"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui


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


class SessionWidget(QtWidgets.QWidget):
    """
    The session widget is a list of sessions with some extra features like a popup menu.
    """

    row_removed = QtCore.pyqtSignal(int, QtWidgets.QWidget)
    row_changed = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, flags=QtCore.Qt.Widget, model=SessionModel()):
        """
        Create a new SessionModel.
        :param parent: parent widget
        :param flags: a Qt flag about widget status
        :param model: SessionWidget model
        """
        super().__init__(parent=parent, flags=flags)
        if not isinstance(model, SessionModel):
            raise TypeError('model is supposed to be a SessionModel instance')

        self._model = model
        self._create_view()
        self._place_components()
        self._create_controller()

    def get_model(self):
        """
        Get the model currently used by the widget.
        :return: an instance of SessionModel
        """
        return self._model

    def _create_view(self):
        """
        Create the components in the final widget.
        """
        self._list = QtWidgets.QListView()
        self._list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._list.setModel(self._model.get_list_model())

    def _place_components(self):
        """
        Place children widgets in the main view.
        """
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self._list, 0, 0)

        self.setLayout(layout)

    def _create_controller(self):
        """
        Create links between components and models.
        """
        list_handler = _SessionListEventHandler(self)
        list_handler.right_click.connect(self._show_popup_menu)
        self._list.installEventFilter(list_handler)
        self._list.selectionModel().currentRowChanged.connect(self._emit_row_changed)
        self._model.item_removed.connect(self.row_removed.emit)

    @QtCore.pyqtSlot(QtCore.QPoint, name='_show_popup_menu')
    def _show_popup_menu(self, point):
        """
        Right click show a popup menu.
        :param point: location of the click
        """
        index = self._list.selectionModel().currentIndex()
        if index.isValid():
            menu = QtWidgets.QMenu(self._list)
            remove = QtWidgets.QAction('Remove', menu)
            remove.triggered.connect(lambda b: self._remove_session(index))
            menu.addAction(remove)
            menu.exec_(point)

    def _remove_session(self, index):
        """
        Remove entry at index `index`
        :param index: index of the entry (QModelIndex)
        """
        self._model.remove_item(index.row())

    def _emit_row_changed(self, new_index, old_index):
        """
        Emit signal row_changed with new_index.row() as parameter.
        :param new_index: a QModelIndex
        :param old_index: a QModelIndex
        """
        self.row_changed.emit(new_index.row())


class _SessionListEventHandler(QtCore.QObject):
    """
    EventFilter for the list widget SessionWidget. Filtered events are :
        - ContextMenu
    """

    right_click = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ContextMenu:
            self.right_click.emit(event.globalPos())
            return True
        return super().eventFilter(obj, event)
