#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Widgets that provide information or ask some to the user. Content :
    - MessageDialog, to display information like errors or warnings
"""
import PyQt5.QtWidgets as QtWidgets


class MessageDialog(QtWidgets.QMessageBox):
    """
    A customizable QMessageBox.
    """

    def __init__(self, **kwargs):
        """
        Create a new MessageDialog
        :param kwargs: a dict that can have this keys:
            - text : the text displayed
            - info : an additional text to inform
            - details : an more precise text
            - std_bts : a union of QMessageBox buttons
            - dft_bt : the default button
            - icon : icon displayed in the dialog
        """
        super().__init__()
        opts = {
            'text': 'default',
        }
        opts.update(kwargs)
        self.setText(opts['text'])
        self.setWindowTitle(opts['text'])

        try:
            self.setInformativeText(opts['info'])
        except:
            pass
        try:
            self.setDetailedText(opts['details'])
        except:
            pass
        try:
            self.setStandardButtons(opts['std_bts'])
        except:
            pass
        try:
            self.setDefaultButton(opts['dft_bt'])
        except:
            pass
        try:
            self.setIcon(opts['icon'])
        except:
            try:
                self.setIconPixmap(opts['icon'])
            except:
                pass
