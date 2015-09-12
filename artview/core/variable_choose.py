"""
variable_choose.py

Class instance for finding and choosing shared variable
    from other components.
"""

# Load the needed packages
from functools import partial

from .core import componentsList, QtGui, QtCore
from . import common


class VariableChoose(QtGui.QDialog):
    '''
    Class instance for finding and choosing component and shared variable
    from other components.
    '''

    @classmethod
    def guiStart(self, parent=None):
        return self(parent=parent)

    def __init__(self, components=None, compSelect=False, varSelect=True,
                 name="VariableChoose", parent=None):
        '''Initialize the class to create the interface'''
        super(VariableChoose, self).__init__(parent=parent)
        self.result = None
        self.compSelect = compSelect
        self.varSelect = varSelect
        # self.central_widget = QtGui.QWidget()
        # self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self)
        # set window as modal
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        if components is None:
            self.components = componentsList[:]
#            QtCore.QObject.connect(
#                self.components, QtCore.SIGNAL("ComponentAppended"),
#                self._updateComponentList)
#            QtCore.QObject.connect(
#                self.components, QtCore.SIGNAL("ComponentRemoved"),
#                self._updateComponentList)
        else:
            self.components = components[:]

        self.setupUi()

    def chooseVariable(self):

        self.exec_()
        return self.result

#    def _setVariables(self):
#        '''Determine which variable are common to both atual components'''
#        self.variables = []
#        for var in self.comp0.sharedVariables.keys():
#            if var in self.comp1.sharedVariables.keys():
#                self.variables.append(var)

    ########################
    # Button methods #
    ########################

    def setupUi(self):
        '''Build main layout.'''

        self.model = QtGui.QStandardItemModel()
        self.addItems()

        self.treeView = QtGui.QTreeView()
        self.treeView.setModel(self.model)
        self.treeView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeView.setHeaderHidden(True)
        self.layout.addWidget(self.treeView, 0, 0, 1, 2)

        self.button = QtGui.QPushButton("Cancel")
        self.button.clicked.connect(self.cancel)
        self.layout.addWidget(self.button, 1, 0)

        self.button = QtGui.QPushButton("Select")
        self.button.clicked.connect(self.select)
        self.layout.addWidget(self.button, 1, 1)

    def addItems(self):
        for component in self.components:
            item = QtGui.QStandardItem(component.name)
            item.setSelectable(self.compSelect)
            self.model.appendRow(item)
            for var in component.sharedVariables.keys():
                item_var = QtGui.QStandardItem(var)
                item_var.setSelectable(self.varSelect)
                item.appendRow(item_var)

    def cancel(self):
        self.result = None
        self.done(QtGui.QDialog.Rejected)

    def select(self):
        selection = self.treeView.selectedIndexes()
        if selection:
            item = selection[0]
            row = item.parent().row()
            if row >= 0:
                variable = item.data().toString()
                component = item.parent().data().toString()
                self.result = (
                    str(component), self.components[row], str(variable))
            else:
                row = item.row()
                component = item.data().toString()
                self.result = (str(component), self.components[row], None)
            self.done(QtGui.QDialog.Accepted)
        else:
            self.cancel()

    def _clearLayout(self, layout):
        '''Recursively remove items from layout.'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clearLayout(item.layout())
