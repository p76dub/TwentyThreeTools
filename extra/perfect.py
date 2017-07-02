#!/usr/bin/python3

"""
This module contains everything related to the plugin Perfect.
"""
import sys
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

import src.core.utils
import src.core.widgets.dialog

__version__ = '1.0a1'


class NPerfectNumberModel(object):
    """
    Model for the plugin. Allow testing if a numbers (or many) are n-perfect.
    """

    # CONSTRUCTOR
    def __init__(self, n):
        """
        Create a new NPerfectNumberModel object.
        :param n: prime number
        :throws ValueError: n is not a number
        """
        self._number = int(n)

    # REQUESTS
    def get_number(self):
        """
        Gives the prime number (n)
        """
        return self._number

    # COMMANDS
    def set_number(self, number):
        """
        Change the prime number (n)
        :param number: the new one
        :throws ValueError: n is not a number
        """
        self._number = int(number)

    def is_number_perfect(self, number, ignore=False):
        """
        Test if number is a n-perfect number. Check if the sum of number's splitters is equal
        to n (get_number())
        :param number: the number you want to check
        :param ignore: default is False. If True, ValueError is not thrown and None is returned
        :throws ValueError: number is not a number
        """
        try:
            num = int(number)
        except ValueError as e:
            if not ignore:
                raise e
            return None
        else:
            perfect_sum = 0
            for i in range(1, num):
                if num % i == 0:
                    perfect_sum += i
            return perfect_sum == self._number

    def are_numbers_perfect(self, number_list, ignore=False):
        """
        For each number in number_list, test if number is a n-perfect number. Check if the sum of
        number's splitters is equal to n (get_number())
        :param number_list: the list of numbers you want to check
        :param ignore: default is False. If True, ValueError is not thrown and None is added to
        the result.
        :throws ValueError: number is not a number
        :return: the list of n-perfect number included in number_list
        """
        return [n for n in number_list if self.is_number_perfect(n, ignore)]


class NPerfectNumber(QtWidgets.QWidget):
    """
    The view of the plugin.
    """
    DEFAULT_NUMBER = 23
    DIRECT_INPUT = 0
    RANGE_INPUT = 1
    MAX_INPUT_NUMBER = 2 ** 31 - 1

    def __init__(self, parent=None):
        """
        Create a new view.
        :param parent: the parent of the widget.
        """
        super().__init__(parent=parent, flags=QtCore.Qt.Widget)
        self._create_model()
        self._create_view()
        self._place_components()
        self._create_controller()
        self._refresh()

    def _create_model(self):
        """
        Create the model of the view.
        """
        self._model = NPerfectNumberModel(NPerfectNumber.DEFAULT_NUMBER)

    def _create_view(self):
        """
        Create components in the view.
        """
        self._by_direct_input = QtWidgets.QRadioButton(self, text='By direct input')
        self._by_direct_input.setChecked(True)

        self._by_range_input = QtWidgets.QRadioButton(self, text='By range input')

        self._input_group = QtWidgets.QButtonGroup(self)
        self._input_group.addButton(self._by_direct_input, NPerfectNumber.DIRECT_INPUT)
        self._input_group.addButton(self._by_range_input, NPerfectNumber.RANGE_INPUT)

        self._input_box = QtWidgets.QSpinBox(self)
        self._input_box.setMaximum(NPerfectNumber.MAX_INPUT_NUMBER)

        self._low_input_box = QtWidgets.QSpinBox(self)
        self._low_input_box.setMaximum(NPerfectNumber.MAX_INPUT_NUMBER)

        self._high_input_box = QtWidgets.QSpinBox(self)
        self._high_input_box.setMaximum(NPerfectNumber.MAX_INPUT_NUMBER)

        self._number_spinbox = QtWidgets.QSpinBox(self)
        self._number_spinbox.setMaximum(NPerfectNumber.MAX_INPUT_NUMBER)

        self._output_field = QtWidgets.QTextEdit(self)
        self._output_field.setMaximumWidth(400)
        self._output_field.setReadOnly(True)

        self._analyse_button = QtWidgets.QPushButton(self, text='Analyse')

    def _place_components(self):
        """
        Place components in the view.
        """
        main_layout = QtWidgets.QGridLayout(self)

        input_box = QtWidgets.QGroupBox(self, title='Input Options')
        input_box_layout = QtWidgets.QGridLayout(input_box)

        input_box_layout.addWidget(self._by_direct_input, 0, 0, 1, 5)
        input_box_layout.addWidget(self._input_box, 1, 1, 1, 4)
        input_box_layout.addWidget(self._by_range_input, 2, 0, 1, 5)
        input_box_layout.addWidget(QtWidgets.QLabel(self, text='From'), 3, 1)
        input_box_layout.addWidget(self._low_input_box, 3, 2)
        input_box_layout.addWidget(QtWidgets.QLabel(self, text='to'), 3, 3)
        input_box_layout.addWidget(self._high_input_box, 3, 4)

        input_box_layout.setColumnStretch(2, 1)
        input_box_layout.setColumnStretch(4, 1)

        input_box.setLayout(input_box_layout)

        options_box = QtWidgets.QGroupBox(self, title='Algorith options')
        options_box_layout = QtWidgets.QGridLayout(options_box)

        options_box_layout.addWidget(QtWidgets.QLabel(self, text='Number to reach : '), 0, 0, 1, 2)
        options_box_layout.addWidget(self._number_spinbox, 0, 2)

        options_box.setLayout(options_box_layout)

        output_box = QtWidgets.QGroupBox(self, title='Output')
        output_box_layout = QtWidgets.QGridLayout(output_box)

        output_box_layout.addWidget(self._output_field, 0, 0)

        main_layout.addWidget(input_box, 0, 0)
        main_layout.addWidget(output_box, 0, 1, 3, 1)
        main_layout.addWidget(options_box, 1, 0)
        main_layout.addWidget(self._analyse_button, 2, 0)

        self.setLayout(main_layout)

    def _create_controller(self):
        """
        Connect events and handlers.
        """
        self._analyse_button.clicked.connect(self._on_analyse_click)
        self._input_group.buttonClicked[int].connect(self._switch_field_state)

    def _on_analyse_click(self):
        """
        Called when the user click on analyse button.
        """
        self._model.set_number(self._number_spinbox.value())
        if self._input_group.checkedId() == NPerfectNumber.RANGE_INPUT:
            low = self._low_input_box.value()
            high = self._high_input_box.value()
            if high < low:
                src.core.widgets.dialog.MessageDialog(
                    text='ValueError',
                    info='An error occurs and analyse failed',
                    details='Lowest value ({}) is higher than the highest value ({})'.format(
                        low, high),
                    icon=QtWidgets.QMessageBox.Critical,
                ).exec_()
                return
            result = self._model.are_numbers_perfect([i for i in range(low, high + 1)])
        else:
            result = self._model.is_number_perfect(self._input_box.value())
        self._output_field.setText(str(result))

    def _refresh(self):
        """
        Refresh for the first time the view, in order to have both models and views synchronized.
        """
        self._number_spinbox.setValue(self._model.get_number())
        self._switch_field_state(self._input_group.checkedId())

    def _switch_field_state(self, id):
        """
        Switch fields' state according to id
        :param id: NPerfectNumber.RANGE_INPUT or NPerfectNumber.DIRECT_INPUT
        """
        if id == NPerfectNumber.RANGE_INPUT:
            self._low_input_box.setEnabled(True)
            self._high_input_box.setEnabled(True)
            self._input_box.setEnabled(False)
        else:
            self._input_box.setEnabled(True)
            self._low_input_box.setEnabled(False)
            self._high_input_box.setEnabled(False)

loader = src.core.utils.PluginLoader(
    name='Perfect',
    version=__version__,
    info='Find perfect n-numbers, meaning numbers with their splitters\' sum equals to n',
    authors=('p76dub',),
    plugin=NPerfectNumber,
)
