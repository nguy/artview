"""
core.py

Class instance to create Variables and establish change signals.



"""

# Load the needed packages
from PyQt4 import QtGui, QtCore

# keet track of all components, this is not fundamental, but may be usefull
# for some control utilities



class Variable(QtCore.QObject):
    '''
    Class that holds a value, changing that with change() emits a signal

    There is no mandatory naming for instances of this Class, however ARTview
    components name variable according to the following table, using it is
    recommended:

    .. _shared_variable:
    .. table:: Shared Variables Table

        +-----------+------------------------------+------------------------------------+
        | Name      | Function                     | Valid values                       |
        +===========+==============================+====================================+
        | Vradar    | Hold radar open with pyart   | :py:class:`pyart.core.Radar`       |
        |           |                              | instance                           |
        +-----------+------------------------------+------------------------------------+
        | Vgrid     | Hold grid open or generated  | :py:class:`pyart.core.Grid`        |
        |           | with pyart                   | instance                           |
        +-----------+------------------------------+------------------------------------+
        | Vfield    | Name of a Field in radar file|string in radar.fields.keys()       |
        +-----------+------------------------------+------------------------------------+
        | Vtitl     | Tilt (sweep) of a radar file | int between 0 and                  |
        |           |                              | (number of sweeps)-1               |
        +-----------+------------------------------+------------------------------------+
        | Vlims     | Limits of display            | dict containing keys:'vmin',       |
        |           |                              | 'vmax', 'xmin', 'xmax', 'ymin',    |
        |           |                              | 'ymax' and holding float values    |
        +-----------+------------------------------+------------------------------------+
        |Vgatefilter| Hold pyart GateFilter        |:py:class:`pyart.correct.GateFilter`|
        |           |                              |instance                            |
        +-----------+------------------------------+------------------------------------+

    .. note::
        *  we want to make None a valid value for Vradar, but this need some
           changes in :file:`artview/components/plot_radar.py`
        *  Vlims is deprecated in favor of a not shared variable
    '''

    value = None #: Value of the Variable

    def __init__(self,value=None):
        ''' initialize '''
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
            Define if this is a strong, or a weak change. This is a some what
            subjective decision: strong is default, a weak change should be
            used to indicate to the slot that this change should not trigger
            any costly computation. Reasons for this are: When initialising
            variables, variable is likely to change again shortly, another
            more important variable is being changed as well etc.

            .. note::
                Defining how to respond to strong/weak changes is
                responsibility of the slot, most can just ignore the
                difference, but the costly ones should be aware.

        Notes
        -----
        The arguments of the emitted signal are (self, value, strong).
        '''
        self.value = value
        self.emit(QtCore.SIGNAL("ValueChanged"), self, value, strong)


class ComponentsList(QtCore.QObject):
    '''Keep track of Components in a list and emit signals.
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
    Abstract class for a ART-view component
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
        super(Component, self).__init__(parent=parent, flags=flags)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.name = name
        self.parent = parent
        self.setWindowTitle(name)
        self.sharedVariables = {}
        componentsList.append(self)

    def connectAllVariables(self):
        '''Call connectSharedVariable for all keys in sharedVariables'''
        for var in self.sharedVariables.keys():
            self.connectSharedVariable(var)

    def disconnectAllVariables(self):
        '''Call connectSharedVariable for all keys in sharedVariables'''
        for var in self.sharedVariables.keys():
            self.disconnectSharedVariable(var)

    def connectSharedVariable(self, var):
        '''Connect variable 'var' to its slot as defined in
        sharedVariables dictionary'''
        if var in self.sharedVariables:
            if self.sharedVariables[var] is not None:
                QtCore.QObject.connect(
                    getattr(self, var), QtCore.SIGNAL("ValueChanged"),
                    self.sharedVariables[var])
        else:
            raise ValueError("Variable %s is not a shared variable of %s"
                            %(var,self.name))

    def disconnectSharedVariable(self, var):
        '''Connect variable 'var' to its slot as defined in
        sharedVariables dictionary'''
        if var in self.sharedVariables:
            if self.sharedVariables[var] is not None:
                QtCore.QObject.disconnect(
                    getattr(self, var), QtCore.SIGNAL("ValueChanged"),
                    self.sharedVariables[var])
        else:
            raise ValueError("Variable %s is not a shared variable of %s"
                            %(var,self.name))

    def keyPressEvent(self, event):
        '''Reimplementation, pass keyEvent to parent,
        even if a diferent window'''
        if self.parent == None:
            super(Component, self).keyPressEvent(event)
        else:
            # Send event to parent to handle (Limitation of pyqt not having a 
            # form that does this - AG)
            self.parent.keyPressEvent(event)

    def closeEvent(self, QCloseEvent):
        '''Reimplementation to remove from components list'''
        componentsList.remove(self)
        self.disconnectAllVariables()
        super(Component, self).closeEvent(QCloseEvent)
