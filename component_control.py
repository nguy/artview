"""
field.py

Class instance used for modifying field via Display window.
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial


class ComponentsControl(QtGui.QWidget):
    '''Class to display the Window with Field Buttons'''

    def __init__(self, components, name="ComponentsControl", parent=None):
        '''Initialize the class to create the interface'''
        super(ComponentsControl, self).__init__(parent)
        self.parent = parent
        self.name = name
        self.setWindowTitle(name)

        self.components = components
        self.comp0 = components[0]
        self.comp1 = components[1]
        self._setVariables()
        self.setupUi()
        self._setRadioButtons()

        self.show()

    def _setVariables(self):
        self.variables = []
        for var in self.comp0.sharedVariables:
            if var in self.comp1.sharedVariables:
                self.variables.append(var)

    ########################
    # Button methods #
    ########################

    def setupUi(self):
        # Add layout
        self.layout = QtGui.QGridLayout(self)

        # Select Components buttons
        self.combo0 = QtGui.QComboBox()
        self.combo0.activated[int].connect(self._comp0Action)
        self.combo1 = QtGui.QComboBox()
        self.combo1.activated[int].connect(self._comp1Action)
        self.layout.addWidget(self.combo0, 0, 0)
        self.layout.addWidget(self.combo1, 1, 0)

        # Fill buttons
        for component in self.components:
            self.combo0.addItem(component.name)
            self.combo1.addItem(component.name)


    def _setRadioButtons(self):
        # Radio Buttons
        self.radioLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.radioLayout, 2, 0)
        self.radioLayout.addWidget(QtGui.QLabel("Conect"), 0, 1)
        self.radioLayout.addWidget(QtGui.QLabel("Disconect"), 0, 2)
        
        self.radioBoxes = []
        for idx,var in enumerate(self.variables):
            self._addRadioButton(var, idx)
        

    def _addRadioButton(self, var, idx):
        radioBox = QtGui.QButtonGroup()
        self.radioBoxes.append(radioBox)
        conect = QtGui.QRadioButton()
        disconect = QtGui.QRadioButton()
        QtCore.QObject.connect(conect, QtCore.SIGNAL("clicked()"), \
                               partial(self.conectVar, var))
        QtCore.QObject.connect(disconect, QtCore.SIGNAL("clicked()"), \
                               partial(self.disconectVar, var))
        radioBox.addButton(conect)
        radioBox.addButton(disconect)
        if getattr(self.comp0, var) is getattr(self.comp1, var):
            conect.setChecked(True)
        else:
            disconect.setChecked(True)
        self.radioLayout.addWidget(QtGui.QLabel(var), idx+1, 0)
        self.radioLayout.addWidget(conect, idx+1, 1)
        self.radioLayout.addWidget(disconect, idx+1, 2)

    def _comp0Action(self, idx):
        self.comp0 = self.components[idx]
        self._setVariables()
        self._clearLayout(self.radioLayout)
        self.layout.removeItem(self.radioLayout)
        self._setRadioButtons()

    def _comp1Action(self, idx):
        self.comp1 = self.components[idx]
        self._setVariables()
        self._clearLayout(self.radioLayout)
        self.layout.removeItem(self.radioLayout)
        self._setRadioButtons()

    def conectVar(self, var):
        print "conect var %s of %s with %s"%(var, self.comp1.name, self.comp0.name)

    def disconectVar(self, var):
        print "disconect var %s of %s from %s"%(var, self.comp1.name, self.comp0.name)

    def _clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clearLayout(item.layout())

