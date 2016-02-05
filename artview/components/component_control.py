"""
component_control.py

Class instance for control variables shared between components.
"""

# Load the needed packages
from functools import partial

from ..core import Variable, Component, QtGui, QtCore, common, componentsList


class LinkSharedVariables(Component):
    '''
    Class instance for control variables shared between components.

    The user may select two components from a list. A radio menu is
    added for every common sharable variable. Each variable may be unlinked
    from similar instance in the other component.

    This is a powerful Component, multiple instances may conflict.
    '''

    @classmethod
    def guiStart(self, parent=None):
        kwargs, independent = \
            common._SimplePluginStart("LinkSharedVariables").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, components=None, name="LinkSharedVariables", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        components : list of :py:class:`~artview.core.core.Component` instance
            Components to control. If None will use the global list present in
            artview.core.core.componentsList
        name : string
            Field Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        '''
        super(LinkSharedVariables, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        self.radioLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.radioLayout, 2, 0)

        if components is None:
            self.components = componentsList
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
        '''Determine common variables to both components.'''
        self.variables = []
        for var in self.comp0.sharedVariables.keys():
            if var in self.comp1.sharedVariables.keys():
                self.variables.append(var)

    ########################
    # Button methods #
    ########################

    def setupUi(self):
        '''Build main layout.'''
        if len(self.components) == 0:
            return
        if self.comp0 not in self.components:
            self.comp0 = self.components[0]
        if self.comp1 not in self.components:
            self.comp1 = self.components[0]

        # Select Components buttons
        self.combo0 = QtGui.QComboBox()
        self.combo0.currentIndexChanged[int].connect(self._comp0Action)
        self.combo1 = QtGui.QComboBox()
        self.combo1.currentIndexChanged[int].connect(self._comp1Action)
        #self.layout.addWidget(self.combo0, 0, 0)
        #self.layout.addWidget(self.combo1, 1, 0)

        # Fill buttons
        for component in self.components:
            self.combo0.addItem(component.name)
            self.combo1.addItem(component.name)
        self.combo0.setCurrentIndex(self.components.index(self.comp0))
        self.combo1.setCurrentIndex(self.components.index(self.comp1))

        self._setVariables()
        self._setRadioButtons()

    def _setRadioButtons(self):
        '''Add radio buttons for control over the variables.'''
        # Radio Buttons
        #self.radioLayout = QtGui.QGridLayout()
        #self.layout.addLayout(self.radioLayout, 2, 0)
        #self.radioLayout.addWidget(QtGui.QLabel("Link"), 0, 1)
        #self.radioLayout.addWidget(QtGui.QLabel("Unlink"), 0, 2)

        self.radioBoxes = []
        for idx, var in enumerate(self.variables):
            self._addRadioButton(var, idx)

        self.layout.addWidget(QtGui.QLabel('from'), 0, 1, -1, 1)
        self.layout.addWidget(self.combo0, 0, 2, -1, 1)
        self.layout.addWidget(QtGui.QLabel('to'), 0, 4, -1, 1)
        self.layout.addWidget(self.combo1, 0, 5, -1, 1)

    def linking(self, var, state):
        if state == 0:
            self.disconnectVar(var)
        else:
            self.connectVar(var)

    def _addRadioButton(self, var, idx):
        '''Add radio button for variable in the given index.'''

        link = QtGui.QCheckBox('is linked')

        if getattr(self.comp0, var) is getattr(self.comp1, var):
            link.setChecked(True)
        else:
            link.setChecked(False)

        if self.comp0 is self.comp1:
            link.setDisabled(True)


        self.layout.addWidget(QtGui.QLabel(var[1::] + ' '), idx, 0)
        #self.radioLayout.addWidget(QtGui.QLabel('from ' + self.comp1.name + ' '), idx+1, 1)
        self.layout.addWidget(link, idx, 3)
        #self.radioLayout.addWidget(QtGui.QLabel('to ' + self.comp0.name), idx, 4)

        link.stateChanged.connect(partial(self.linking, var))

        return
        radioBox = QtGui.QButtonGroup()
        self.radioBoxes.append(radioBox)  # avoid garbage collector

        link = QtGui.QRadioButton()
        unlink = QtGui.QRadioButton()
        QtCore.QObject.connect(link, QtCore.SIGNAL("clicked()"),
                               partial(self.connectVar, var))
        QtCore.QObject.connect(unlink, QtCore.SIGNAL("clicked()"),
                               partial(self.disconnectVar, var))
        radioBox.addButton(link)
        radioBox.addButton(unlink)

        if getattr(self.comp0, var) is getattr(self.comp1, var):
            link.setChecked(True)
        else:
            unlink.setChecked(True)

        if self.comp0 is self.comp1:
            unlink.setDisabled(True)

        self.radioLayout.addWidget(QtGui.QLabel(var[1::]), idx+1, 0)
        self.radioLayout.addWidget(QtGui.QLabel(), idx+1, 0)
        self.radioLayout.addWidget(link, idx+1, 1)
        self.radioLayout.addWidget(unlink, idx+1, 2)

    def setComponent0(self, name):
        '''Set current component in first dropdown menu.'''
        for idx, comp in enumerate(self.components):
            if name == comp.name:
                self.combo0.setCurrentIndex(idx)
                return

        import warnings
        warnings.warn("Component not in Component list, ignoring.")

    def setComponent1(self, name):
        '''Set current component in second dropdown menu.'''
        for idx, comp in enumerate(self.components):
            if name == comp.name:
                self.combo1.setCurrentIndex(idx)
                return

        import warnings
        warnings.warn("Component not in Component list, ignoring.")

    def _comp0Action(self, idx):
        '''Update Component 0.'''
        self.comp0 = self.components[idx]
        self._setVariables()
        self.layout.removeWidget(self.combo0)
        self.layout.removeWidget(self.combo1)
        self._clearLayout(self.layout)
        #self.layout.removeItem(self.radioLayout)
        self._setRadioButtons()

    def _comp1Action(self, idx):
        '''Update Component 1.'''
        self.comp1 = self.components[idx]
        self._setVariables()
        self.layout.removeWidget(self.combo0)
        self.layout.removeWidget(self.combo1)
        self._clearLayout(self.layout)
        #self.layout.removeItem(self.radioLayout)
        self._setRadioButtons()

    def connectVar(self, var):
        '''Assign variable in component 0 to component 1.'''
        # Disconect old Variable
        self.comp1.disconnectSharedVariable(var)
        # comp1.var = comp0.var
        setattr(self.comp1, var, getattr(self.comp0, var))
        # Connect new Variable
        self.comp1.connectSharedVariable(var)
        # emit signal
        getattr(self.comp1, var).update()
        print("connect var %s of %s from %s" % (
            var, self.comp1.name, self.comp0.name))

    def disconnectVar(self, var):
        '''Turn variable in component 1 independente of component 0.'''
        # Disconect old Variable
        self.comp1.disconnectSharedVariable(var)
        # comp1.var = Variable()
        setattr(self.comp1, var, Variable())
        # Connect new Variable
        self.comp1.connectSharedVariable(var)
        # emit signal
        getattr(self.comp1, var).update()
        print("disconnect var %s of %s from %s" % (
            var, self.comp1.name, self.comp0.name))

    def _clearLayout(self, layout):
        '''Recursively remove items from layout.'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clearLayout(item.layout())

    def _updateComponentList(self, item):
        '''Rebuild main layout.'''
        self._clearLayout(self.layout)
        self.setupUi()
