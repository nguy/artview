"""
core.py

Class instance to create Variables and establish change signals.

"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
import sys
import pickle

from . import common

# keet track of all components, this is not fundamental, but may be usefull
# for some control utilities


class Variable(QtCore.QObject):
    '''
    Class that holds a value, using change() emits a signal.

    There is no mandatory naming for instances of this Class, however ARTview
    components name variable according to the following table, using it is
    recommended:

    .. _shared_variable:
    .. table:: Shared Variables Table

        +-----------+-------------------+------------------------------------+
        | Name      | Function          | Valid values                       |
        +===========+===================+====================================+
        | Vradar    | Hold radar open   | :py:class:`pyart.core.Radar`       |
        |           | with pyart        | instance                           |
        +-----------+-------------------+------------------------------------+
        | Vgrid     | Hold grid open or | :py:class:`pyart.core.Grid`        |
        |           | generated with    | instance                           |
        |           | pyart             |                                    |
        +-----------+-------------------+------------------------------------+
        | Vcontainer| Alias to Vradar or| Radar, Grid or None                |
        |           | Vgrid             |                                    |
        +-----------+-------------------+------------------------------------+
        | Vfield    | Name of a Field   |string in radar.fields.keys()       |
        |           | in radar file     |                                    |
        +-----------+-------------------+------------------------------------+
        | Vtilt     | Tilt (sweep) of   | int between 0 and                  |
        |           | a radar file      | (number of sweeps) - 1             |
        +-----------+-------------------+------------------------------------+
        | VlevelZ   | Vertical level of | int between 0 and                  |
        |           | a grid file       | nz - 1                             |
        +-----------+-------------------+------------------------------------+
        | VlevelY   | Latitudinal level | int between 0 and                  |
        |           | of a grid file    | ny - 1                             |
        +-----------+-------------------+------------------------------------+
        | VlevelX   | Longitudinal level| int between 0 and                  |
        |           | of a grid file    | nx - 1                             |
        +-----------+-------------------+------------------------------------+
        | Vlevel    | Alias to Vtilt,   | positive integer                   |
        |           | VlevelZ, VlevelY  |                                    |
        |           | or VlevelX        |                                    |
        +-----------+-------------------+------------------------------------+
        | Vlims     | Limits of display | dict containing keys: 'xmin',      |
        |           |                   | 'xmax', 'ymin', 'ymax' and holding |
        |           |                   | float values                       |
        +-----------+-------------------+------------------------------------+
        | Vcmap     | Colormap          | dict containing keys: 'vmin' and   |
        |           |                   | 'vmax' holding float values and key|
        |           |                   | 'cmap' holding colormap string name|
        +-----------+-------------------+------------------------------------+
        |Vgatefilter| Hold pyart        |:py:class:`pyart.correct.GateFilter`|
        |           | GateFilter        |instance                            |
        +-----------+-------------------+------------------------------------+

    .. note::
        *  we want to make None a valid value for Vradar, but this need some
           changes in :file:`artview/components/plot_radar.py`
        *  Vlims is deprecated in favor of a not shared variable
    '''

    value = None  #: Value of the Variable

    def __init__(self, value=None):
        QtCore.QObject.__init__(self)
        self.value = value

    def change(self, value, strong=True):
        '''
        Change the Variable value and emit 'ValueChanged' signal.

        Parameters
        ----------
        value :
            New Value to be assigned to the variable.
        [Optional]
        strong : bool, optional
            Define if this is a strong, or a weak change. This is a somewhat
            subjective decision: strong is default.
            
            A weak change should be used to indicate to the slot that the 
            change should not trigger any costly computation. 
            Reasons for this are: When initializing a variable, it is likely 
            to change again shortly, or another more important variable is 
            being changed as well etc.

            .. note::
                Defining how to respond to strong/weak changes is the
                responsibility of the slot, most can just ignore the
                difference, but the costly ones should be aware.

        Notes
        -----
        The arguments of the emitted signal are (self, value, strong).
        '''
        self.value = value
        self.emit(QtCore.SIGNAL("ValueChanged"), self, value, strong)


class ComponentsList(QtCore.QObject):
    '''
    Keep track of Components in a list and emit signals.
    Methods append and remove are provided and emit signals,
    direct acess to the list is allowed with 'ComponentList.list',
    but not recomended.'''

    def __init__(self):
        super(ComponentsList, self).__init__()
        self.list = []

    def append(self, item):
        self.list.append(item)
        self.emit(QtCore.SIGNAL("ComponentAppended"), item)

    def remove(self, item):
        self.list.remove(item)
        self.emit(QtCore.SIGNAL("ComponentRemoved"), item)

    def index(self, item):
        return self.list.index(item)

    def __delitem__(self, key):
        self.list.__delitem__(key)

    def __getitem__(self, key):
        return self.list.__getitem__(key)

    def __setitem__(self, key, value):
        self.list.__setitem__(key, value)

    def __len__(self):
        return len(self.list)

componentsList = ComponentsList()


class Component(QtGui.QMainWindow):
    '''
    Abstract class for an ART-view component.
    '''

    def __init__(self, name="Component", parent=None, flags=QtCore.Qt.Widget):
        '''
        Initialize the class

        Parameters
        ----------
        [Optional]
        name : string
            Display window name.
        parent : PyQt instance
            Parent instance to associate to Component. If None, then Qt owns,
            otherwise associated with parent PyQt instance.
        '''
        if sys.version_info<(2,7,0):
            super(Component, self).__init__()
        else:
            super(Component, self).__init__(parent=parent, flags=flags)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.name = name
        self.parent = parent
        self.setWindowTitle(name)
        self.sharedVariables = {}
        componentsList.append(self)

        # build Bar
        self.menubar = self.menuBar()
        self.variableBar = QtGui.QWidget()
        self.variableBar.setToolTip('Drag-Drop Bar')
        self.variableBarLayout = QtGui.QVBoxLayout()
        self.variableBarLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.variableBar.setLayout(self.variableBarLayout)
        self.variableBar.hide()
        self.variableBarLayout.addWidget(QtGui.QLabel("Drag-Drop\nVariables\n   here. "))
        self.action = self.menubar.addAction("Variables")
        self.action.triggered.connect(self.variablesShowHide)

        # Create GUI for Variables Bar
        self.componentCentralWidget = QtGui.QWidget()
        super(Component, self).setCentralWidget(self.componentCentralWidget)
        self.componentCentralLayout = QtGui.QHBoxLayout(self.componentCentralWidget)
        self.componentCentralLayout.setSpacing(0)
        self.componentCentralLayout.setMargin(0)
        self.componentCentralLayout.addWidget(self.variableBar)
        self.componentCentralLayout.setAlignment(self.variableBar, QtCore.Qt.AlignTop)

    def setCentralWidget(self, widget):
        self.componentCentralLayout.addWidget(widget)

    def variablesShowHide(self):
        print ("haha")
        if self.variableBar.isVisible():
            self.variableBar.hide()
        else:
            self.variableBar.show()

    def connectAllVariables(self):
        '''Call connectSharedVariable for all keys in sharedVariables.'''
        for var in self.sharedVariables.keys():
            self.connectSharedVariable(var)
            button = VariableButton(var, self)
            self.variableBarLayout.addWidget(button)

    def disconnectAllVariables(self):
        '''Call connectSharedVariable for all keys in sharedVariables.'''
        for var in self.sharedVariables.keys():
            self.disconnectSharedVariable(var)

    def connectSharedVariable(self, var):
        '''Connect variable 'var' to its slot as defined in
        sharedVariables dictionary.'''
        if var in self.sharedVariables:
            if self.sharedVariables[var] is not None:
                QtCore.QObject.connect(
                    getattr(self, var), QtCore.SIGNAL("ValueChanged"),
                    self.sharedVariables[var])
        else:
            raise ValueError("Variable %s is not a shared variable of %s"
                             % (var, self.name))

    def disconnectSharedVariable(self, var):
        '''Connect variable 'var' to its slot as defined in
        sharedVariables dictionary.'''
        if var in self.sharedVariables:
            if self.sharedVariables[var] is not None:
                QtCore.QObject.disconnect(
                    getattr(self, var), QtCore.SIGNAL("ValueChanged"),
                    self.sharedVariables[var])
        else:
            raise ValueError("Variable %s is not a shared variable of %s"
                             % (var, self.name))

    def keyPressEvent(self, event):
        '''Reimplementation, pass keyEvent to parent,
        even if a diferent window.'''
        if self.parent is None:
            super(Component, self).keyPressEvent(event)
        else:
            # Send event to parent to handle (Limitation of pyqt not having a
            # form that does this - AG)
            self.parent.keyPressEvent(event)

    def closeEvent(self, QCloseEvent):
        '''Reimplementation to remove from components list.'''
        componentsList.remove(self)
        self.disconnectAllVariables()
        super(Component, self).closeEvent(QCloseEvent)


class QMenuWithLayout(QtGui.QMenu):
    '''Create a Menu with a layout attribute.'''

    def __init__(self, *args, **kwargs):
        super(QMenuWithLayout, self).__init__(*args, **kwargs)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.setLayout(self.layout)


class VariableButton(QtGui.QPushButton):

    def __init__(self, varName, parent):
        super(VariableButton, self).__init__(varName[1::], parent)
        print (varName)
        self.variableName = varName
        self.component = parent

        self.setAcceptDrops(True)
        self.pressed.connect(self.startDrag)

    def startDrag(self):
        drag = QtGui.QDrag(self)
        mimeData = QtCore.QMimeData()
        data = (self.variableName, componentsList.index(self.component))
        mimeData.setData('MoveQLabel', QtCore.QByteArray(pickle.dumps(data)))

        drag.setMimeData(mimeData)
        drag.start(QtCore.Qt.LinkAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('MoveQLabel'):
            event.accept()
        else:
            event.reject()


    def dropEvent(self, event):
        serial = event.mimeData().data('MoveQLabel')
        data = pickle.loads(serial)
        component = componentsList[data[1]]
        variableName = data[0]
        print (self.component.name, self.variableName,
                     component.name , variableName)
        if component != self.component or variableName != self.variableName:
            newVar = getattr(component, variableName)
            myVar = getattr(self.component, self.variableName)
            if myVar != newVar:
                aux = common.ShowQuestion(
                    "Current Variable: %s::%s\n" %
                    (self.component.name, self.variableName) +
                    "New Variable:     %s::%s\n" %
                    (component.name , variableName) +
                    "Replace Current Variable with New One?")
                if aux == QtGui.QMessageBox.Ok:
                    # Disconect old Variable
                    self.component.disconnectSharedVariable(self.variableName)
                    # my = new
                    setattr(self.component, self.variableName, newVar)
                    # Connect new Variable
                    self.component.connectSharedVariable(self.variableName)
                    # just to emit signal
                    newVar.change(newVar.value)
            else:
                aux = common.ShowQuestion(
                    "Current Variable: %s::%s\n" %
                    (self.component.name, self.variableName) +
                    "New Variable:     %s::%s\n" %
                    (component.name , variableName) +
                    "Variable are the same, unlink them?")
                if aux == QtGui.QMessageBox.Ok:
                    # Disconect old Variable
                    self.component.disconnectSharedVariable(self.variableName)
                    # my = new
                    var = Variable()
                    setattr(self.component, self.variableName, var)
                    # Connect new Variable
                    self.component.connectSharedVariable(self.variableName)
                    # just to emit signal
                    var.change(myVar.value)
