"""
level.py

Class instance used for modifying level via Display window.
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial

from ..core import Variable, Component


class LevelButtonWindow(Component):
    '''Class to display the Window with Level Buttons.'''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`
    Vtilt = None  \
    #: see :ref:`shared_variable`, only used if plot_type starts with "Radar"
    VlevelZ = None \
    #: see :ref:`shared_variable`, only used if plot_type="gridZ"
    VlevelY = None \
    #: see :ref:`shared_variable`, only used if plot_type="gridY"
    VlevelX = None \
    #: see :ref:`shared_variable`, only used if plot_type="gridX"
    Vcmap = None #: see :ref:`shared_variable`


    def __init__(self, Vlevel, plot_type, Vcontainer=None, name="LevelButtons",
                 parent=None):
        '''Initialize the class to create the Level Selection interface.

        Parameters
        ----------
        Vlevel : :py:class:`~artview.core.core.Variable` instance
            Level signal variable.
        plot_type : string
            One of "radarPpi", "radarRhi", "radarAirborne", "gridZ", "gridY"
            or "gridX". If starting with "radar" Vlevel will be passed to Vtilt,
            otherwise to VlevelZ, VlevelY or VlevelX respectively. This can't
            be changed afterwards.
        Vcontainer: :py:class:`~artview.core.core.Variable` instance
            Radar/Grid signal variable. None will create empty variable.
            Will be passed to Vradar or Vgrid according with plot_type 
            For correct behavior one and just one of those should be provided
        [Optional]
        name : string
            Level Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to LevelButtonWindow window.
            If None, then Qt owns, otherwise associated w/ parent PyQt instance

        Notes
        -----
        This class records the selected button and passes the
        change value back to variable.
        '''
        super(LevelButtonWindow, self).__init__(name=name, parent=parent)

        # Set up signal, so that DISPLAY can react to external
        # (or internal) changes in level (Core.Variable instances expected)
        # The change is sent through Vlevel
        if Vcontainer is None:
            Vcontainer = Variable(None)

        self.plot_type = plot_type
        self.sharedVariables = {}

        self.CreateLevelWidget()

        if self.plot_type.startswith("radar"):
            self.Vtilt = Vlevel
            self.Vradar = Vcontainer
            self.sharedVariables["Vtilt"] = self.NewLevel
            self.sharedVariables["Vradar"] = self.NewRadar
            self.SetLevelRadioButtonsRadar()
        elif self.plot_type == "gridZ":
            self.VlevelZ = Vlevel
            self.Vgrid = Vcontainer
            self.sharedVariables["VlevelZ"] = self.NewLevel
            self.sharedVariables["Vgrid"] = self.NewGrid
            self.SetLevelRadioButtonsGrid()
        elif self.plot_type == "gridY":
            self.VlevelY = Vlevel
            self.Vgrid = Vcontainer
            self.sharedVariables["VlevelY"] = self.NewLevel
            self.sharedVariables["Vgrid"] = self.NewGrid
            self.SetLevelRadioButtonsGrid()
        elif self.plot_type == "gridX":
            self.VlevelX = Vlevel
            self.Vgrid = Vcontainer
            self.sharedVariables["VlevelX"] = self.NewLevel
            self.sharedVariables["Vgrid"] = self.NewGrid
            self.SetLevelRadioButtonsGrid()
        self.connectAllVariables()

        self.show()

    ########################
    # Button methods #
    ########################

    def LevelSelectCmd(self, nlevel):
        '''Captures a selection and update level variable.'''
        self.Vlevel.change(nlevel)

    def CreateLevelWidget(self):
        '''Create a widget to store radio buttons to control level adjust.'''
        self.radioBox = QtGui.QGroupBox("Level Selection", parent=self)
        self.rBox_layout = QtGui.QVBoxLayout(self.radioBox)
        self.radioBox.setLayout(self.rBox_layout)
        self.setCentralWidget(self.radioBox)

    def SetLevelRadioButtonsRadar(self):
        '''Set a level selection using radio buttons.'''
        # Instantiate the buttons into a list for future use
        self.levelbutton = []

        # Pull out the level indices and elevations for display
        elevs = self.Vradar.value.fixed_angle['data'][:]

        # Loop thru & create each level button & connect value when selected
        for nlevel in self.Vradar.value.sweep_number['data'][:]:
            btntxt = "%2.1f deg (Tilt %d)" % (elevs[nlevel], nlevel+1)
            button = QtGui.QRadioButton(btntxt, self.radioBox)
            self.levelbutton.append(button)
            QtCore.QObject.connect(
                self.levelbutton[nlevel], QtCore.SIGNAL("clicked()"),
                partial(self.LevelSelectCmd, nlevel))

            self.rBox_layout.addWidget(self.levelbutton[nlevel])

        # setChecked the current level
        self.NewLevel(self.Vlevel, self.Vlevel.value, True)

    def SetLevelRadioButtonsGrid(self):
        '''Set a level selection using radio buttons.'''
        # Instantiate the buttons into a list for future use
        self.levelbutton = []

        # Pull out the level indices and elevations for display
        if self.plot_type == "gridZ":
            elevs = self.Vgrid.value.axes["z_disp"]["data"][:]
        elif self.plot_type == "gridY":
            elevs = self.Vgrid.value.axes["y_disp"]["data"][:]
        elif self.plot_type == "gridX":
            elevs = self.Vgrid.value.axes["x_disp"]["data"][:]

        # Loop thru & create each level button & connect value when selected
        for nlevel in range(len(elevs)):
            btntxt = "%2.1f m (level %d)" % (elevs[nlevel], nlevel+1)
            button = QtGui.QRadioButton(btntxt, self.radioBox)
            self.levelbutton.append(button)
            QtCore.QObject.connect(
                self.levelbutton[nlevel], QtCore.SIGNAL("clicked()"),
                partial(self.LevelSelectCmd, nlevel))

            self.rBox_layout.addWidget(self.levelbutton[nlevel])

        # setChecked the current level
        self.NewLevel(self.Vlevel, self.Vlevel.value, True)

    def NewLevel(self, variable, value, strong):
        '''Slot for 'ValueChanged' signal of
        :py:class:`Vlevel <artview.core.core.Variable>`.

        This will:

        * Update radio check
        '''
        level = self.Vlevel.value
        if level >= 0 and level < len(self.levelbutton):
            self.levelbutton[level].setChecked(True)

    def NewRadar(self, variable, value, strong):
        '''Slot for 'ValueChanged' signal of
        :py:class:`Vradar <artview.core.core.Variable>`.

        This will:

        * Recreate radio itens
        '''
        # update level list
        self.CreateLevelWidget()
        self.SetLevelRadioButtonsRadar()

    def NewGrid(self, variable, value, strong):
        '''Slot for 'ValueChanged' signal of
        :py:class:`Vgrid <artview.core.core.Variable>`.

        This will:

        * Recreate radio itens
        '''
        # update level list
        self.CreateLevelWidget()
        self.SetLevelRadioButtonsGrid()

    ########################
    #      Properties      #
    ########################

    @property
    def Vlevel(self):
        ''' Alias to Vtilt, VlevelZ, VlevelY or VlevelX depending on
        plot_type '''
        if self.plot_type.startswith("radar"):
            return self.Vtilt
        elif self.plot_type == "gridZ":
            return self.VlevelZ
        elif self.plot_type == "gridY":
            return self.VlevelY
        elif self.plot_type == "gridX":
            return self.VlevelX
        else:
            return None

