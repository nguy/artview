"""
level.py

Class instance used for modifying level via Display window.
"""

# Load the needed packages
from functools import partial

from ..core import Variable, Component, QtGui, QtCore


class LevelButtonWindow(Component):
    '''
    Class to display the Window with Level radio buttons.
    The level can represent either tilts in a native radar file
    or some height level in a gridded data file.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`
    Vtilt = None  \
        #: see :ref:`shared_variable`, used if plot_type starts with "Radar"
    VlevelZ = None \
        #: see :ref:`shared_variable`, used if plot_type="gridZ"
    VlevelY = None \
        #: see :ref:`shared_variable`, used if plot_type="gridY"
    VlevelX = None \
        #: see :ref:`shared_variable`, used if plot_type="gridX"
    Vcolormap = None  #: see :ref:`shared_variable`

    def __init__(self, Vlevel=None, plot_type="Radar", Vcontainer=None,
                 controlType="radio", name="LevelButtons", parent=None):
        '''Initialize the class to create the Level Selection interface.

        Parameters
        ----------
        [Optional]
        Vlevel : :py:class:`~artview.core.core.Variable` instance
            Level signal variable. If None start new one with 0.
        plot_type : string
            One of "radarPpi", "radarRhi", "radarAirborne", "gridZ", "gridY"
            or "gridX". If starting with "radar" Vlevel will be passed to
            Vtilt, otherwise to VlevelZ, VlevelY or VlevelX respectively. This
            can't be changed afterwards.
        Vcontainer : :py:class:`~artview.core.core.Variable` instance
            Radar/Grid signal variable. None will create empty variable.
            Will be passed to Vradar or Vgrid according with plot_type.
        controlType : "radio" or "slider"
            Type of control used, radio button or slider bar.
        name : string
            Level Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to LevelButtonWindow window.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

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
        if Vlevel is None:
            Vlevel = Variable(0)

        self.plot_type = plot_type
        self.controlType = controlType
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

    def LevelSelectCmdSlider(self):
        '''Captures a selection and update level variable.'''
        self.LevelSelectCmd(self.slider.value())

    def showValue(self, value):
        if self.plot_type.startswith("radar"):
            txt = "%.2f deg" % self.elevs[value]
        else:
            txt = "%.2f km" % (self.elevs[value] / 1000.)
        QtGui.QToolTip.showText(QtGui.QCursor.pos(), txt)
        self.Vlevel.change(value, False)

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
        self.elevs = elevs

        if self.controlType == "radio":
            # Loop through, create each level button and connect value when
            # selected
            for nlevel in self.Vradar.value.sweep_number['data'][:]:
                btntxt = "%2.1f deg (Tilt %d)" % (elevs[nlevel], nlevel+1)
                button = QtGui.QRadioButton(btntxt, self.radioBox)
                self.levelbutton.append(button)
                QtCore.QObject.connect(
                    self.levelbutton[nlevel], QtCore.SIGNAL("clicked()"),
                    partial(self.LevelSelectCmd, nlevel))

                self.rBox_layout.addWidget(self.levelbutton[nlevel])
        elif self.controlType == "slider":
            self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
            self.slider.sliderReleased.connect(self.LevelSelectCmdSlider)
            self.slider.valueChanged.connect(self.showValue)
            self.slider.setRange(0, len(elevs) - 1)
            self.slider.setTickPosition(self.slider.TicksRight)
            self.rBox_layout.addWidget(self.slider)
            self.label = QtGui.QLabel("")
            self.rBox_layout.addWidget(self.label)

        # setChecked the current level
        self.NewLevel(self.Vlevel, True)

    def SetLevelRadioButtonsGrid(self):
        '''Set a level selection using radio buttons.'''
        # Instantiate the buttons into a list for future use
        self.levelbutton = []

        # Pull out the level indices and elevations for display
        import pyart
        from pkg_resources import parse_version
        if parse_version(pyart.__version__) >= parse_version('1.6.0'):
            if self.plot_type == "gridZ":
                elevs = self.Vgrid.value.z["data"][:]
            elif self.plot_type == "gridY":
                elevs = self.Vgrid.value.y["data"][:]
            elif self.plot_type == "gridX":
                elevs = self.Vgrid.value.x["data"][:]
        else:
            if self.plot_type == "gridZ":
                elevs = self.Vgrid.value.axes["z_disp"]["data"][:]
            elif self.plot_type == "gridY":
                elevs = self.Vgrid.value.axes["y_disp"]["data"][:]
            elif self.plot_type == "gridX":
                elevs = self.Vgrid.value.axes["x_disp"]["data"][:]
        self.elevs = elevs

        if self.controlType == "radio":
            # Loop through, create each level button and connect value when
            # selected
            for nlevel in range(len(elevs)):
                btntxt = "%2.1f m (level %d)" % (elevs[nlevel], nlevel+1)
                button = QtGui.QRadioButton(btntxt, self.radioBox)
                self.levelbutton.append(button)
                QtCore.QObject.connect(
                    self.levelbutton[nlevel], QtCore.SIGNAL("clicked()"),
                    partial(self.LevelSelectCmd, nlevel))
                self.rBox_layout.addWidget(self.levelbutton[nlevel])

        elif self.controlType == "slider":
            self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
            self.slider.sliderReleased.connect(self.LevelSelectCmdSlider)
            self.slider.valueChanged.connect(self.showValue)
            self.slider.setRange(0, len(elevs) - 1)
            self.slider.setTickPosition(self.slider.TicksRight)
            self.rBox_layout.addWidget(self.slider)
            self.label = QtGui.QLabel("")
            self.rBox_layout.addWidget(self.label)

        # setChecked the current level
        self.NewLevel(self.Vlevel, True)

    def NewLevel(self, variable, strong):
        '''Slot for 'ValueChanged' signal of
        :py:class:`Vlevel <artview.core.core.Variable>`.

        This will:

        * Update radio check
        '''
        if self.controlType == "radio":
            level = self.Vlevel.value
            if level >= 0 and level < len(self.levelbutton):
                self.levelbutton[level].setChecked(True)
        elif self.controlType == "slider":
            level = self.Vlevel.value
            if level >= 0 and level < len(self.elevs):
                self.slider.setValue(level)
                if self.plot_type.startswith("radar"):
                    txt = "%.2f deg (Tilt %i)" % (self.elevs[level], level+1)
                else:
                    txt = "%.2f km (Level %i)" % (self.elevs[level] / 1000.,
                                                  level+1)
                self.label.setText(txt)

    def NewRadar(self, variable, strong):
        '''Slot for 'ValueChanged' signal of
        :py:class:`Vradar <artview.core.core.Variable>`.

        This will:

        * Recreate radio itens
        '''
        # update level list
        self.CreateLevelWidget()
        self.SetLevelRadioButtonsRadar()

    def NewGrid(self, variable, strong):
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
        '''Alias to Vtilt, VlevelZ, VlevelY or VlevelX depending on
        plot_type.'''
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
