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

    def __init__(self, components=None, name="LinkSharedVariables",
                 parent=None):
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

        self.groupBox = QtGui.QGroupBox("Manage how variables are shared"
                                        "between components")
        # self.groupBox.setCheckable(True)
        self.layout.addWidget(self.groupBox, 0, 0, 1, -1)

        self.linkingLayout = QtGui.QGridLayout()
        self.groupBox.setLayout(self.linkingLayout)

        self.helpButton = QtGui.QPushButton("Help")
        self.helpButton.clicked.connect(self._displayHelp)
        self.layout.addWidget(self.helpButton, 1, 0, 1, -1)

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
        self.combo1 = QtGui.QComboBox()

        # Fill buttons
        for component in self.components:
            self.combo0.addItem(component.name)
            self.combo1.addItem(component.name)

        self.combo0.currentIndexChanged[int].connect(self._comp0Action)
        self.combo1.currentIndexChanged[int].connect(self._comp1Action)

        self.combo0.setCurrentIndex(self.components.index(self.comp0))
        self.combo1.setCurrentIndex(self.components.index(self.comp1))

        self._setVariables()
        self._setRadioButtons()

    def _setRadioButtons(self):
        '''Add buttons for control over the variables.'''

        if self.variables:
            for idx, var in enumerate(self.variables):
                self._addRadioButton(var, idx)

            self.linkingLayout.addWidget(QtGui.QLabel('Linking from'),
                                         0, 0, 1, 2)
            self.linkingLayout.addWidget(self.combo1, 0, 2, 1, 1)
            self.linkingLayout.addWidget(QtGui.QLabel('to'), 0, 3, 1, 1)
            self.linkingLayout.addWidget(self.combo0, 0, 4, 1, 1)
        else:
            self.linkingLayout.addWidget(self.combo0, 0, 0)
            self.linkingLayout.addWidget(QtGui.QLabel('and'), 0, 1)
            self.linkingLayout.addWidget(self.combo1, 0, 2)
            self.linkingLayout.addWidget(QtGui.QLabel('have no common shared'
                                                      'variables'), 0, 3)

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

        self.linkingLayout.addWidget(QtGui.QLabel(var[1::] + ' '),
                                     idx+1, 1, 1, 2)
        self.linkingLayout.addWidget(link, idx+1, 3, 1, 2)

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
        self.linkingLayout.removeWidget(self.combo0)
        self.linkingLayout.removeWidget(self.combo1)
        self._clearLayout(self.linkingLayout)
        self._setRadioButtons()

    def _comp1Action(self, idx):
        '''Update Component 1.'''
        self.comp1 = self.components[idx]
        self._setVariables()
        self.linkingLayout.removeWidget(self.combo0)
        self.linkingLayout.removeWidget(self.combo1)
        self._clearLayout(self.linkingLayout)
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
        self._clearLayout(self.linkingLayout)
        self.setupUi()

    def _displayHelp(self):
        ''' Launch pop-up help window.'''
        text = (
            "<b>Using the Link Shared Variables</b><br><br>"
            "The LinkSharedVariables tool change how different "
            "components of ARTView share their variables.<br>"
            "By Selecting the components in the drop-down menu you receive "
            "a list of the variables common to both components together with "
            "a check box signaling if that variable is linked "
            "(i.e. is being shared).<br><br>"
            "<i>Functions</i>:<br>"
            "If a box is not checked, checking it will force those Components "
            "to share that variables, in particular the first one will drops its "
            "variable and use the one from the second.<br>"
            "If a box is checked, unchecking it will unlink the variable. "
            "That means, the first components "
            "will start to use copy of the variable, so it no longer uses the "
            "variable from the second.<br><br>"
            "For an example on changing links of the SelectRegion, a "
            "<a href='https://youtu.be/cd4_OBJ6HnA'>Video Tutorial</a> "
            "has been created.<br>"
            # "For a demonstration, a "
            # "<a href='https://youtu.be/1ehZXbp7000'>Video Tutorial</a> "
            # "has been created.<br>"
            )
        common.ShowLongTextHyperlinked(text)
