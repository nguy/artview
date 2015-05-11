"""
component_control.py

Class instance for control variables shared between components.
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial

import core

class ComponentsControl(core.Component):
    '''Class instance for control variables shared between components.
    The user select 2 components from a list and a radio menu is added for
    every common sharable variable. The variable in the second one can be
    connect or disconnected from the first one.

    This is a powerfull Component, multiple instances may conflict
    '''

    def __init__(self, components=None, name="ComponentsControl", parent=None):
        '''Initialize the class to create the interface'''
        super(ComponentsControl, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)
        
        if components == None:
            self.components = core.componentsList
            QtCore.QObject.connect(
                self.components, QtCore.SIGNAL("ComponentAppended"),
                self._updateComponentList)
            QtCore.QObject.connect(
                self.components, QtCore.SIGNAL("ComponentRemoved"),
                self._updateComponentList)
        else:
            self.components = components

        self.comp0 = None
        self.comp1 = None
        self.setupUi()

        self.show()

    def _setVariables(self):
        '''Determine which variable are common to both atual components'''
        self.variables = []
        for var in self.comp0.sharedVariables.keys():
            if var in self.comp1.sharedVariables.keys():
                self.variables.append(var)

    ########################
    # Button methods #
    ########################

    def setupUi(self):
        '''Build main layout'''
        if len(self.components) == 0:
            return
        if self.comp0 not in self.components:
            self.comp0 = self.components[0]
        if self.comp1 not in self.components:
            self.comp1 = self.components[0]


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
        self.combo0.setCurrentIndex(self.components.index(self.comp0))
        self.combo1.setCurrentIndex(self.components.index(self.comp1))
        
        self._setVariables()
        self._setRadioButtons()

    def _setRadioButtons(self):
        '''Add radio buttons for control over the variables'''
        # Radio Buttons
        self.radioLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.radioLayout, 2, 0)
        self.radioLayout.addWidget(QtGui.QLabel("Conect"), 0, 1)
        self.radioLayout.addWidget(QtGui.QLabel("Disconect"), 0, 2)
        
        self.radioBoxes = []
        for idx,var in enumerate(self.variables):
            self._addRadioButton(var, idx)

    def _addRadioButton(self, var, idx):
        '''Add radio button for variable in the given index'''
        radioBox = QtGui.QButtonGroup()
        self.radioBoxes.append(radioBox)  # avoid garbage collector

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

        if self.comp0 is self.comp1:
            disconect.setDisabled(True)

        self.radioLayout.addWidget(QtGui.QLabel(var), idx+1, 0)
        self.radioLayout.addWidget(conect, idx+1, 1)
        self.radioLayout.addWidget(disconect, idx+1, 2)

    def _comp0Action(self, idx):
        '''Update Component 0'''
        self.comp0 = self.components[idx]
        self._setVariables()
        self._clearLayout(self.radioLayout)
        self.layout.removeItem(self.radioLayout)
        self._setRadioButtons()

    def _comp1Action(self, idx):
        '''Update Component 1'''
        self.comp1 = self.components[idx]
        self._setVariables()
        self._clearLayout(self.radioLayout)
        self.layout.removeItem(self.radioLayout)
        self._setRadioButtons()

    def conectVar(self, var):
        '''Assign variable in component 0 to component 1'''
        # Disconect old Variable
        self.comp1.disconnectSharedVariable(var)
        # comp1.var = comp0.var
        setattr(self.comp1, var, getattr(self.comp0, var))
        # Connect new Variable
        self.comp1.connectSharedVariable(var)
        # comp1.var.change(comp0.var.value), just to emit signal
        getattr(self.comp1, var).change(getattr(self.comp0, var).value)
        print "connect var %s of %s from %s"%(var, self.comp1.name, self.comp0.name)

    def disconectVar(self, var):
        '''Turn variable in component 1 independente of component 0'''
        # Disconect old Variable
        self.comp1.disconnectSharedVariable(var)
        # comp1.var = Variable()
        setattr(self.comp1, var, core.Variable())
        # Connect new Variable
        self.comp1.connectSharedVariable(var)
        # comp1.var.change(comp0.var.value)
        getattr(self.comp1, var).change(getattr(self.comp0, var).value)
        print "disconnect var %s of %s from %s"%(var, self.comp1.name, self.comp0.name)

    def _clearLayout(self, layout):
        '''recursively remove items from layout'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clearLayout(item.layout())

    def _updateComponentList(self, item):
        self._clearLayout(self.layout)
        self.setupUi()

