"""

"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial

from .. import core
common = core.common

class Exemple1(core.Component):
    @classmethod
    def guiStart(self, parent=None):
        val, entry = common.string_dialog("Exemple1", "Exemple1", "Name:")
        return self(name=val, parent=parent)

    def __init__(self, name="Exemple1", parent=None):
        '''Initialize the class to create the interface'''
        super(Exemple1, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)
        
        self.layout.addWidget(QtGui.QLabel("Vertical Plugin named: %s"%self.name), 0, 0)
        self.button = QtGui.QPushButton("Close")
        self.button.clicked.connect(self.close)
        self.layout.addWidget(self.button, 1, 0)
        self.show()

    def close(self):
        super(Exemple1, self).close()

_plugins=[Exemple1]
