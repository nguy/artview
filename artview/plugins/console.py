"""
console.py
"""

# Load the needed packages
import code
import pyart

import sys
import os

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '...')
sys.path.insert(0, path)

import artview

from ..core import Component, Variable, common, QtGui, QtCore, componentsList


class AccessTerminal(Component):
    '''
    Open an interactive python console so the direct manipulation
    '''

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("AccessTerminal").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, name="AccessTerminal", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        name : string
            Field Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(AccessTerminal, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)
        self.button = QtGui.QPushButton("Interactive Console")
        self.button.clicked.connect(self.runCode)
        self.layout.addWidget(self.button, 0, 0)
        self.layout.addWidget(
            QtGui.QLabel("WARNING: never run this if you don't\n" +
                         "have acess to the running terminal."), 1, 0)
        self.show()

    def runCode(self):
        '''Use :py:func:`code.interact` to acess python terminal'''
        # separe in thread to allow conflict with running Qt Application
        import threading
        banner = (
            "\nHELLO: this is an iteractive python console so you can\n"
            "access ARTview functions while running the GUI and manipulate "
            "the data directly.\n\n"
            " You have acess to three variables:\n"
            "    'components': A list of all running components\n"
            "    'pyart': Python-ARM Radar Toolkit.\n"
            "    'artview': ARM Radar Toolkit Viewer\n\n"
            "To leave and go back to graphical ARTview press ctrl+D\n"
            "in Unix/OXS or ctrl+Z in Windows.")
        self.thread = threading.Thread(
            target=code.interact,
            kwargs={'banner': banner,
                    'readfunc': None,
                    'local': {'components': componentsList, 'pyart': pyart,
                              'artview': artview}}
            )
        self.thread.start()
        # thread.join()


_plugins = [AccessTerminal]
