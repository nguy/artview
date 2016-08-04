"""
core.py

Class instance to create Variables and establish change signals.

"""

# Load the needed packages
# this should the only place with reference to PyQt4
from PyQt4 import QtGui, QtCore
import sys

# lets add some magic for the documentation
QtCore.__doc__ = ("Qt backend to be used all over ARTview, now it is an "
                  "alias to :py:mod:`PyQt4.QtCore`")
QtGui.__doc__ = ("Qt backend to be used all over ARTview, now it is an "
                 "alias to :py:mod:`PyQt4.QtGui`")

# keep track of all components, this is not fundamental, but may be useful
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
        | Vfield    | Name of a Field   | string, preferentially in          |
        |           | in radar file     | radar.fields.keys(), but there is  |
        |           |                   | no guarranty                       |
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
        | Vlimits   | Limits of display | dict containing keys: 'xmin',      |
        |           |                   | 'xmax', 'ymin', 'ymax' and holding |
        |           |                   | float values                       |
        +-----------+-------------------+------------------------------------+
        | Vcolormap | Colormap          | dict containing keys: 'vmin' and   |
        |           |                   | 'vmax' holding float values and key|
        |           |                   | 'cmap' holding colormap string name|
        +-----------+-------------------+------------------------------------+
        |Vgatefilter| Hold pyart        |:py:class:`pyart.filters.GateFilter`|
        |           | GateFilter        |instance or None                    |
        +-----------+-------------------+------------------------------------+
        |VplotAxes  | Hold axes of      |:py:class:`matplotlib.axes.Axes`    |
        |           | Matplotlib figure |instance or None                    |
        +-----------+-------------------+------------------------------------+
        |VPathInte\ | Hold auxillary    |function like :py:func:`~artview.\  |
        |riorFunc   | function          |components.RadarDisplay.\           |
        |           |                   |getPathInteriorValues` or None      |
        +-----------+-------------------+------------------------------------+
        |Vfilelist  | Hold filenames in |list containing paths to files      |
        |           | current working   |(strings)                           |
        |           | directory         |                                    |
        +-----------+-------------------+------------------------------------+
        |VRadarCol\ | Cache radars      |list of :py:class:`pyart.core.Radar`|
        |lection    |                   |instances                           |
        |           |                   |                                    |
        +-----------+-------------------+------------------------------------+
        |VpyartDis\ | Hold pyart display| instance of one of the classes     |
        |play       | instances         | in :py:mod:`pyart.graph`           |
        |           |                   |                                    |
        +-----------+-------------------+------------------------------------+
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
            Define if this is a strong or weak change. This is a somewhat
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
        self.emit(QtCore.SIGNAL("ValueChanged"), self, strong)

    def update(self, strong=True):
        '''
        Emits the 'ValueChanged' signal without changings value. This is
        useful when value is changed in place.

        Parameters
        ----------
        strong : bool, optional
            Define if this is a strong or weak change.
        '''
        self.emit(QtCore.SIGNAL("ValueChanged"), self, strong)


class ComponentsList(QtCore.QObject):
    '''
    Keep track of Components in a list and emit signals.
    Methods 'append' and 'remove' are provided and emit signals,
    direct access to the list is allowed with 'ComponentList.list',
    but not recommended.'''

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

    def __repr__(self):
        return self.list.__repr__()

componentsList = ComponentsList()


def suggestName(comp):
    '''Suggest a unambiguous name for component.'''
    compName = comp.__name__
    name = compName
    i = 0
    names = [c.name for c in componentsList]
    while name in names and i < 1000:
        name = compName + '%i' % i
        i = i + 1
    return name


class Component(QtGui.QMainWindow):
    '''
    Abstract class for an ARTview component.
    '''

    def __init__(self, name="Component", parent=None, flags=QtCore.Qt.Widget):
        '''
        Initialize the class.

        Parameters
        ----------
        [Optional]
        name : string
            Display window name.
        parent : PyQt instance
            Parent instance to associate to Component. If None, then Qt owns,
            otherwise associated with parent PyQt instance.
        '''
        if sys.version_info < (2, 7, 0):
            super(Component, self).__init__()
        else:
            super(Component, self).__init__(parent=parent, flags=flags)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.name = name
        self.parent = parent
        self.setWindowTitle(name)
        self.sharedVariables = {}
        componentsList.append(self)

    def connectAllVariables(self):
        '''Call connectSharedVariable for all keys in sharedVariables.'''
        for var in self.sharedVariables.keys():
            self.connectSharedVariable(var)

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
