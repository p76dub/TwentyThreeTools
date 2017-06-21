#!/usr/bin/python3
"""
This module contains what necessary for the Scandable plugin.
"""
import string

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

import src.core.utils
import src.core.widgets.dialog

__version__ = '1.2'


class ScandableModel(QtCore.QObject):
    """
    ScandableModel's instances allow, from a file, what words are n-Scandables.
    Careful only Latin-1 characters are allowed.
    :inv:
        get_separators() is not None
        len(get_separators()) >= 1
    """
    # Shift we need to perform to have the order in the alphabet
    _SHIFT = ord('a') - 1

    def __init__(self, number, file=None, separators=frozenset(string.whitespace)):
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
            get_options() == {'no-repeat':False, 'no-blank':True}
        """
        super().__init__()
        if separators is None or len(separators) < 1:
            raise AssertionError('No separators provided')
        if number < 1:
            raise AssertionError('Positive number expected')

        self._num = int(number)
        self._file = file
        self._offset = 0
        self._separators = set(separators)
        self._options = {
            'no-blank' : True,
            'no-repeat' : False,
            'sort-output' : False
        }

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

    def get_options(self):
        """
        Retrieve options associated with the model.
        :return: a dictionary containing the following keys:
            - no-blank : if True, no blanks in the result
            - no-repeat : if True, words in the result are unique
        """
        return dict(self._options)

    def set_file(self, file=None):
        """
        Change the file that should be processed. Default is None
        :param file: path to the file
        """
        self._file = file
        self._offset = 0

    def get_num(self):
        """
        Get the number that letters' packets must reach.
        :return: (int)
        """
        return self._num

    def set_num(self, number):
        """
        Set the number that letters' packets must reach.
        :param number: the new number (positive integer)
        """
        if number < 1:
            raise AssertionError('Positive number expected')

        self._num = int(number)

    def set_options(self, options):
        """
        Set options associated with the model.
        Authorized keys are :
            - no-repeat : words in the result are unique
            - no-blank : no empty strings in the result
            - sort-output : sort the output
        :param options: the dictionary
        """
        self._options.update(options)

    def set_separators(self, separators):
        """
        Change the list of separators.
        :param separators: separators' list (list<str>)
        :pre: separators is not None
            len(separators) >= 1
        :post: get_separators() == separators
        """
        if separators is None or len(separators) < 1:
            raise AssertionError('No separators provided')

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
            raise AssertionError('No file provided')

        # Reset shift at 0
        self._offset = 0

        # Analysis of the file and prepare the result
        result = []
        with open(self._file, 'r') as file_descriptor:
            for line in file_descriptor:
                result.extend(self._parse(line.strip(), sep))

        return self._format(result)

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
            raise AssertionError('No file provided')

        with open(self._file, 'r') as file_descriptor:
            file_descriptor.seek(self._offset)
            line = file_descriptor.readline()
            self._offset = file_descriptor.tell()

        return self._format(self._parse(line.strip(), sep))

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

        # Slice words according to separators and analyse
        sentence_lower = sentence.lower()
        result = []
        start = 0
        for end in range(len(sentence_lower)):
            word = None
            # Slicing
            if sentence_lower[end] in separators:
                word = sentence_lower[start:end]
                start = end + 1
            elif  end == len(sentence_lower) - 1:
                word = sentence_lower[start:end + 1]

            # Run analysis
            if word is not None and self._analyse_word(word):
                result.append(word)

        return result

    def _analyse_word(self, word):
        """
        Analyse word and return True if it is scandable, else False
        :param word: the word that will be analyzed
        :return: True our False
        """
        value = 0
        i = 0
        recognized = True
        while i < len(word) and recognized:
            value += ord(word[i]) - self._SHIFT  # number in the alphabet
            if value > self._num:
                recognized = False  # One packet is not self._num
            elif value == self._num:
                value = 0
            i += 1
        return recognized and value == 0

    def _format(self, result):
        """
        Format a list of strings according to options. Careful, result is formatted in place !
        :param result: the list
        :return: the formatted result
        """
        if self._options['no-blank']:
            result = [r for r in result if r != '']
        if self._options['no-repeat']:
            result = list(set(result))
        if self._options['sort-output']:
            result.sort()

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
        self._refresh()

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

        self._sort_output_box = QtWidgets.QCheckBox(self)
        self._sort_output_box.setText('Sort the output')

        self._separators_field = QtWidgets.QLineEdit(self)
        self._per_line_box = QtWidgets.QCheckBox(self)
        self._per_line_box.setText('Analyse one line')
        self._no_blank_box = QtWidgets.QCheckBox(self)
        self._no_blank_box.setText('Remove empty strings in result')
        self._no_repeat_box = QtWidgets.QCheckBox(self)
        self._no_repeat_box.setText('Remove duplicates in the result')
        self._parse_number = QtWidgets.QSpinBox(self)
        self._parse_number.setMinimum(0)

        self._analyse_button = QtWidgets.QPushButton(self)
        self._analyse_button.setText('Analyse')

        self._output_field = QtWidgets.QTextEdit(self)
        self._output_field.setMaximumWidth(400)
        self._output_field.setReadOnly(True)

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

        output_opts_box = QtWidgets.QGroupBox(self)
        output_opts_box.setTitle('Output Options')

        out_opts_layout = QtWidgets.QGridLayout(output_opts_box)
        out_opts_layout.addWidget(self._sort_output_box, 0, 0)
        out_opts_layout.addWidget(self._no_repeat_box, 1, 0)
        out_opts_layout.addWidget(self._no_blank_box, 2, 0)

        output_opts_box.setLayout(out_opts_layout)

        options_box = QtWidgets.QGroupBox(self)
        options_box.setTitle('Algorithm Options')

        opt_layout = QtWidgets.QGridLayout(options_box)
        opt_layout.addWidget(QtWidgets.QLabel(text='Separators : '), 0, 0)
        opt_layout.addWidget(self._separators_field, 0, 1)
        opt_layout.addWidget(QtWidgets.QLabel(text='Parse number : '), 1, 0)
        opt_layout.addWidget(self._parse_number, 1, 1)
        opt_layout.addWidget(self._per_line_box, 2, 0, 1, 2)

        options_box.setLayout(opt_layout)

        output_box = QtWidgets.QGroupBox(self)
        output_box.setTitle('Output')

        out_layout = QtWidgets.QGridLayout(output_box)
        out_layout.addWidget(self._output_field, 0, 0)

        output_box.setLayout(out_layout)

        main_layout = QtWidgets.QGridLayout(self)
        main_layout.addWidget(input_box, 0, 0)
        main_layout.addWidget(output_opts_box, 1, 0)
        main_layout.addWidget(options_box, 2, 0)
        main_layout.addWidget(self._analyse_button, 3, 0)
        main_layout.addWidget(output_box, 0, 1, 4, 1)

        self.setLayout(main_layout)

    def _create_controller(self):
        """
        Connect widgets.
        """
        self._file_input_button.clicked.connect(self._open_file)
        self._analyse_button.clicked.connect(self._run_analysis)
        self._no_blank_box.clicked.connect(self._on_no_blank_click)
        self._no_repeat_box.clicked.connect(self._on_no_repeat_click)
        self._sort_output_box.clicked.connect(self._on_sort_output_click)

    def _refresh(self):
        """
        Refresh the view for the first time.
        """
        options = self._model.get_options()
        self._no_repeat_box.setChecked(options['no-repeat'])
        self._no_blank_box.setChecked(options['no-blank'])
        self._sort_output_box.setChecked(options['sort-output'])

        self._parse_number.setValue(self._model.get_num())

    def _on_no_repeat_click(self):
        """
        Called when the user click on checkbox no_repeat_box. Control the 'no-repeat' option in the
        model.
        """
        self._model.set_options({'no-repeat': self._no_repeat_box.isChecked()})

    def _on_no_blank_click(self):
        """
        Called when the user click on checkbox no_blank_box. Control the 'no-blank' option in the
        model.
        """
        self._model.set_options({'no-blank': self._no_blank_box.isChecked()})

    def _on_sort_output_click(self):
        """
        Called when the user click on checkbox sort_output. Controls the 'sort-output' option in the
        model.
        """
        self._model.set_options({'sort-output' : self._sort_output_box.isChecked()})

    def _open_file(self):
        """
        Open a popup window asking a file to read. File path is set in file_input_field.
        """
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self,
            caption='Open file',
            filter='Text files (*.txt);;All files (*.*)',
        )
        self._file_input_field.setText(filename)
        self._model.set_file(filename)

    def _set_separators(self):
        """
        Set separators from separators_field into the model only if not empty.
        """
        seps = [sep for sep in self._separators_field.text()]
        if len(seps) > 0:
            self._model.set_separators(seps)

    def _run_analysis(self):
        """
        Run analysis. Show an error message if something went wrong.
        """
        per_line = self._per_line_box.isChecked()
        self._set_separators()
        self._model.set_num(self._parse_number.value())

        try:
            if per_line:
                result = self._model.parse_line()
            else:
                result = self._model.parse_all()
        except Exception as e:
            src.core.widgets.dialog.MessageDialog(
                text='An error occurs',
                info='An error occurs and the file has not been parsed. Please see error below.',
                details='Error : {}'.format(str(e)),
                icon=QtWidgets.QMessageBox.Critical,
            ).exec_()
        else:
            self._output_field.setText(str(result))


loader = src.core.utils.PluginLoader(
    name='Scandable',
    version=__version__,
    info='This plugin allows testing words',
    authors=('p76dub',),
    plugin=Scandable,
)
