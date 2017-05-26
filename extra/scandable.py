#!/usr/bin/python3
"""
This module contains what necessary for the Scandable plugin.
"""
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets


class ScandableModel(QtCore.QObject):
    """
    ScandableModel's instances allow, from a file, what words are n-Scandables.
    Carreful only Latin-1 caracters are allowed.
    :inv:
        get_separators() is not None
        len(get_separators()) >= 1
    """

    def __init__(self, number, file=None, separators=frozenset(' ')):
        """
        Constructor.
        :param number: packet's number
        :param file: name of the file that wil be processed, default is None
        :param separators: words' separators' list
        :pre: separators is not None
            len(separators) >= 1
            number >= 1
        :post: get_separators() == separators
            get_file == file
        """
        super().__init__()
        if separators is None or len(separators) < 1:
            raise AssertionError()
        if number < 1:
            raise AssertionError()

        self._num = number
        self._file = file
        self._offset = 0
        self._separators = set(separators)

    def get_file(self):
        """
        Get path to the file that will be process / has been processed
        :return: a path (str)
        """
        return self._file

    def get_separators(self):
        """
        Get the words' separators' list
        :return: a list (list<str>)
        """
        return self._separators

    def set_file(self, file=None):
        """
        Change the file that should be processed. Default is None
        :param file: path to the file
        """
        self._file = file
        self._offset = 0

    def set_separators(self, separators):
        """
        Change the list of separators.
        :param separators: separators' list (list<str>)
        :pre: separators is not None
            len(separators) >= 1
        :post: get_separators() == separators
        """
        if separators is None or len(separators) < 1:
            raise AssertionError()

        self._separators = separators

    def parse_all(self, sep=None):
        """
        Analyse the entire file. Will give the list of words that are n-scandable
        :param sep: a list of separators (optionnal)
        :return: the list (list<str>)
        :post: parse_all(...) is not None
        :throws: IOError if an error occurs
        """
        if self.get_file() is None:
            raise AssertionError()

        # Reset shift at 0
        self._offset = 0

        # Analysis of the file and prepare the result
        result = []
        with open(self._file, 'r') as file_descriptor:
            for line in file_descriptor:
                result.extend(self._parse(line.strip(), sep))

        return result

    def parse_line(self, sep=None):
        """
        Analyse one line. The shift is set in a way that the next call wil read the next line.
        :param sep: a list of separators (list<str>) (optionnal)
        :return: the list of words that are n-scandable (list<str>)
        :pre: get_file() is not None
        :post: parse_line(...) is not None
        :throws: IOError if an error occurs
        """
        if self.get_file() is None:
            raise AssertionError()

        with open(self._file, 'r') as file_descriptor:
            file_descriptor.seek(self._offset)
            line = file_descriptor.readline()
            self._offset = file_descriptor.tell()

        return self._parse(line.strip(), sep)

    def _parse(self, sentence, sep=None):
        """
        Take a string and parse it in order to find words that are scandable.
        :param sentence: the sentence you want to parse
        :param sep: a list of separators (optionnal)
        :return: a list of words (list<str>)
        """
        # Bild separators
        separators = str.join('', self._separators)
        if sep is not None:
            separators = str.join('', sep)

        # Shift we need to perform to have the order in the alphabet
        shift = ord('a') - 1

        # Slice words according to separators
        sentence_lower = sentence.lower()
        words = sentence_lower.split(separators)

        # Analyse
        result = []
        for word in words:
            value = 0
            i = 0
            recognized = True
            while i < len(word) and recognized:
                value += ord(word[i]) - shift  # number in the alphabet
                if value > self._num:
                    recognized = False  # un paquet ne fait pas 23
                elif value == self._num:
                    value = 0
                i += 1

            if recognized and value == 0:  # verify if last packet has the right size
                result.append(word)

        return result


class Scandable(QtWidgets.QWidget):
    """
    The view of the plugin.
    """

    def __init__(self, parent=None):
        """
        Create a new view of the plugin.
        :param parent: the parent o the widget, default is None
        """
        super().__init__(parent=parent, flags=QtCore.Qt.Widget)
        self._create_model()
        self._create_view()
        self._place_components()
        self._create_controller()

    def _create_model(self):
        """
        Create the model of the plugin.
        """
        self._model = ScandableModel(23)

    def _create_view(self):
        """
        Create components that will be on the view.
        """
        self._file_input_field = QtWidgets.QLineEdit(self)
        self._file_input_button = QtWidgets.QPushButton(self)
        self._file_input_button.setText('Load')

        self._separators_field = QtWidgets.QLineEdit(self)
        self._per_line_box = QtWidgets.QCheckBox(self)
        self._per_line_box.setText('Analyse one line')

    def _place_components(self):
        """
        Place components on the view.
        """
        input_box = QtWidgets.QGroupBox(self)
        input_box.setTitle('Input')

        in_layout = QtWidgets.QGridLayout(input_box)
        in_layout.addWidget(self._file_input_field, 0, 0)
        in_layout.addWidget(self._file_input_button, 0, 1)

        input_box.setLayout(in_layout)

        options_box = QtWidgets.QGroupBox(self)
        options_box.setTitle('Options')

        opt_layout = QtWidgets.QGridLayout(options_box)
        opt_layout.addWidget(QtWidgets.QLabel(text='Separators : '), 0, 0)
        opt_layout.addWidget(self._separators_field, 0, 1)
        opt_layout.addWidget(self._per_line_box, 1, 0)

        options_box.setLayout(opt_layout)

        main_layout = QtWidgets.QGridLayout(self)
        main_layout.addWidget(input_box, 0, 0)
        main_layout.addWidget(options_box, 1, 0)

        self.setLayout(main_layout)

    def _create_controller(self):
        """
        Connect widgets.
        """
        pass

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    disp = Scandable()
    disp.show()

    sys.exit(app.exec_())