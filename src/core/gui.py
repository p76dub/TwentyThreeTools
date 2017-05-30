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
        self._plugin_view.setMinimumSize(400, 400)

        self._sessions = SessionWidget()

        self._main_view = QtWidgets.QSplitter(self)
        self._main_view.setStretchFactor(0, 1)
        self._main_view.setStretchFactor(1, 3)

        for menu in self._menu_model.get_menus():
            self.menuBar().addMenu(menu)

        self.setWindowTitle('TwentyThreeTools')
        self.setMinimumSize(600, 400)

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
        self._sessions.row_changed.connect(self._plugin_view.setCurrentIndex)
        self._sessions.row_removed.connect(self._remove_widget)

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
            self._sessions.get_model().add_item(self._model.sessions[name], name)
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

    @QtCore.pyqtSlot(int, name='_remove_widget')
    def _remove_widget(self, index):
        """
        Remove widget in QStackedWidget at position index
        :param index: int
        """
        widget = self._plugin_view.widget(index)
        self._plugin_view.removeWidget(widget)


class SessionWidget(QtWidgets.QWidget):
    """
    The session widget is a list of sessions with some extra features like a popup menu.
    """

    row_removed = QtCore.pyqtSignal(int)
    row_changed = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, flags=QtCore.Qt.Widget, model=src.core.model.SessionModel()):
        """
        Create a new SessionModel.
        :param parent: parent widget
        :param flags: a Qt flag about widget status
        :param model: SessionWidget model
        """
        super().__init__(parent=parent, flags=flags)
        if not isinstance(model, src.core.model.SessionModel):
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
        self.row_removed.emit(index.row())

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

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = SessionWidget(flags=QtCore.Qt.Window)
    model = widget.get_model()
    model.add_item('plop')
    model.add_item('plic')
    print(model.get_value_at(0))

    widget.show()
    sys.exit(app.exec_())