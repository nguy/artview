"""
plot_radar.py

Class instance used to make Display.
"""
# Load the needed packages
import numpy as np
import os
import pyart

from matplotlib.backends import pylab_setup
backend = pylab_setup()[0]
FigureCanvasQTAgg = backend.FigureCanvasQTAgg
NavigationToolbar = backend.NavigationToolbar2QT
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as \
#    NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import Normalize as mlabNormalize
from matplotlib.colorbar import ColorbarBase as mlabColorbarBase
from matplotlib.pyplot import cm

from ..core import (Variable, Component, common, VariableChoose, QtCore,
                    QtGui, QtWidgets)
from ..core.points import Points

# Save image file type and DPI (resolution)
IMAGE_EXT = 'png'
DPI = 200
# ========================================================================


class Correlation(Component):
    '''
    Class to create a correlation plot, using a returned Radar structure
    from the PyArt pyart.graph package.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    VfieldVertical = None  #: see :ref:`shared_variable`
    VfieldHorizontal = None  #: see :ref:`shared_variable`
    Vtilt = None  #: see :ref:`shared_variable`
    Vgatefilter = None  #: see :ref:`shared_variable`
    VplotAxes = None  #: see :ref:`shared_variable` (no internal use)

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class'''
        kwargs, independent = \
            common._SimplePluginStart("Correlation").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None, VfieldVertical=None, VfieldHorizontal=None,
                 Vgatefilter=None, name="Correlation", parent=None):
        '''
        Initialize the class to create display.

        Parameters
        ----------
        [Optional]
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable. If None start new one with None.
        VfieldVertical, \
        VfieldHorizontal : :py:class:`~artview.core.core.Variable` instance
            Field signal variable. If None start new one with empty string.
        Vgatefilter : :py:class:`~artview.core.core.Variable` instance
            Gatefilter signal variable.
            A value of None will instantiate a empty variable.
        name : string
            Display window name.
        parent : PyQt instance
            Parent instance to associate to Display window.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        '''
        super(Correlation, self).__init__(name=name, parent=parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        # Set up signal, so that DISPLAY can react to
        # external (or internal) changes in radar, field,
        # lims and tilt (expected to be Core.Variable instances)
        # The capital V so people remember using ".value"
        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar
        if VfieldVertical is None:
            self.VfieldVertical = Variable('')
        else:
            self.VfieldVertical = VfieldVertical
        if VfieldHorizontal is None:
            self.VfieldHorizontal = Variable('')
        else:
            self.VfieldHorizontal = VfieldHorizontal

        if Vgatefilter is None:
            self.Vgatefilter = Variable(None)
        else:
            self.Vgatefilter = Vgatefilter

        self.VplotAxes = Variable(None)

        self.sharedVariables = {"Vradar": self.NewRadar,
                                "VfieldVertical": self.NewField,
                                "VfieldHorizontal": self.NewField,
                                "Vgatefilter": self.NewGatefilter,
                                "VplotAxes": None,}

        # Connect the components
        self.connectAllVariables()

        self.parameters = {
            "marker": 'o',
            "facecolors": "blue",
            "edgecolors": "none",
            "s": 20,
            "color": "red",
            }

        self.parameters_type = [
            ("marker", str, "marker type"),
            ("facecolors", str, "marker color"),
            ("edgecolors", str, "marker edge color"),
            ("s", int, "market size"),
            ("color", str, "line color")
            ]

        # Set plot title and colorbar units to defaults
        self.title = self._get_default_title()
        self.unitsVertical, self.unitsHorizontal = self._get_default_units()

        # Create display image text dictionary
        self.disp_text = {}

        # Create a figure for output
        self._set_fig_ax()

        # Launch the GUI interface
        self.LaunchGUI()

        # Initialize radar variable
        self.NewRadar(None, True)

        self.show()

    ####################
    # GUI methods #
    ####################

    def LaunchGUI(self):
        '''Launches a GUI interface.'''
        # Create layout
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(8)

        # Create the widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self._set_figure_canvas()

        self.central_widget.setLayout(self.layout)

        # Add buttons along display for user control
        self.addButtons()

        # Set the status bar to display messages
        self.statusbar = self.statusBar()

    def setParameters(self):
        '''Open set parameters dialog.'''
        parm = common.get_options(self.parameters_type, self.parameters)
        for key in parm.keys():
            self.parameters[key] = parm[key]
        self._update_plot()

    ##################################
    # User display interface methods #
    ##################################

    def addButtons(self):
        '''Add a series of buttons for user control over display.'''
        # Create the Display controls
        self._add_displayBoxUI()
        # Create the Field controls
        self._add_fieldBoxUI()
        # Create the Tools controls
        #self._add_toolsBoxUI()
        # Create the Informational label at top
        #self._add_infolabel()

        self.layout.addWidget(self.fieldVerticalBox, 0, 0, 1, 2)
        label = QtWidgets.QLabel("VS.")
        self.layout.addWidget(label, 0, 2, 1, 1)
        self.layout.setAlignment(label, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.fieldHorizontalBox, 0, 3, 1, 2)
        self.layout.addWidget(self.dispButton, 0, 6)
        self.layout.setAlignment(self.dispButton, QtCore.Qt.AlignRight)
        #self.layout.addWidget(self.toolsButton, 0, 3)
        #self.layout.addWidget(self.infolabel, 0, 4)

    #############################
    # Functionality methods #
    #############################

    def _fillFieldBox(self):
        '''Fill in the Field Window Box with current variable names.'''
        for box in (self.fieldVerticalBox, self.fieldHorizontalBox):
            box.clear()
            box.addItem("Field Select")
            # Loop through and create each field button
            for field in self.fieldnames:
                box.addItem(field)

    def _fieldVerticalAction(self, text):
        '''Define action for Field Button selection.'''
        if text == "Field Select":
            from .field import FieldButtonWindow
            self.fieldbuttonwindow = FieldButtonWindow(
                self.Vradar, self.VfieldVertical,
                name=self.name+"Vertical Field Selection", parent=self.parent)
        else:
            self.VfieldVertical.change(str(text))

    def _fieldHorizontalAction(self, text):
        '''Define action for Field Button selection.'''
        if text == "Field Select":
            from .field import FieldButtonWindow
            self.fieldbuttonwindow = FieldButtonWindow(
                self.Vradar, self.VfieldHorizontal,
                name=self.name+"Horizontal Field Selection", parent=self.parent)
        else:
            self.VfieldHorizontal.change(str(text))

    def _GateFilterToggleAction(self):
        '''Define action for GateFilterToggle menu selection.'''
        if self.gatefilterToggle.isChecked():
            self.gatefilterToggle.setText("GateFilter On")
        else:
            self.gatefilterToggle.setText("GateFilter Off")
        self._update_plot()

    def _title_input(self):
        '''Retrieve new plot title.'''
        val, entry = common.string_dialog_with_reset(
            self.title, "Plot Title", "Title:", self._get_default_title())
        if entry is True:
            self.title = val
            self._update_plot()

    def _units_input(self):
        '''Retrieve new plot units.'''
        val0, entry0 = common.string_dialog_with_reset(
            self.unitsVertical, "Plot Units", "Vertical Units:",
            self._get_default_units())
        val1, entry1 = common.string_dialog_with_reset(
            self.unitsHorizontal, "Plot Units", "Horizontal Units:",
            self._get_default_units())
        if entry0 is True:
            self.unitsVertical = val0
        if entry1 is True:
            self.unitsHorizontal = val1
        if entry0 is True or entry1 is True:
            self._update_plot()

    def _add_ImageText(self):
        '''Add a text box to display.'''
        from .image_text import ImageTextBox
        itext = ImageTextBox(self, parent=self.parent)
        return itext

    def _add_displayBoxUI(self):
        '''Create the Display Options Button menu.'''
        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir))
        config_icon = QtGui.QIcon(os.sep.join(
            [parentdir, 'icons', "categories-applications-system-icon.png"]))
        self.dispButton = QtWidgets.QPushButton(config_icon, "", self)
        self.dispButton.setToolTip("Adjust display properties")
        self.dispButton.setFocusPolicy(QtCore.Qt.NoFocus)
        dispmenu = QtWidgets.QMenu(self)

        self.sweepMenu = dispmenu.addMenu("sweep")

        vertical_scale_menu = dispmenu.addMenu("vertical scale")
        self.vertical_scale_menu_group = QtWidgets.QActionGroup(self, exclusive=True)
        self.vertical_scale_menu_group.triggered.connect(self._update_plot)
        # linear
        action = self.vertical_scale_menu_group.addAction("linear")
        action.setCheckable(True)
        action.setChecked(True)
        vertical_scale_menu.addAction(action)
        # log
        action = self.vertical_scale_menu_group.addAction("log")
        action.setCheckable(True)
        vertical_scale_menu.addAction(action)

        horizontal_scale_menu = dispmenu.addMenu("horizontal scale")
        self.horizontal_scale_menu_group = QtWidgets.QActionGroup(self, exclusive=True)
        self.horizontal_scale_menu_group.triggered.connect(self._update_plot)
        # linear
        action = self.horizontal_scale_menu_group.addAction("linear")
        action.setCheckable(True)
        action.setChecked(True)
        horizontal_scale_menu.addAction(action)
        # log
        action = self.horizontal_scale_menu_group.addAction("log")
        action.setCheckable(True)
        horizontal_scale_menu.addAction(action)

        dispTitle = dispmenu.addAction("Change Title")
        dispTitle.setToolTip("Change plot title")
        dispUnit = dispmenu.addAction("Change Units")
        dispUnit.setToolTip("Change units string")

        self.gatefilterToggle = QtWidgets.QAction(
            'GateFilter On', dispmenu, checkable=True,
            triggered=self._GateFilterToggleAction)
        dispmenu.addAction(self.gatefilterToggle)
        self.gatefilterToggle.setChecked(True)

        self.regressionLineToggle = QtWidgets.QAction(
            'Regression Line', dispmenu, checkable=True,
            triggered=self._update_plot)
        dispmenu.addAction(self.regressionLineToggle)

        self.dispImageText = dispmenu.addAction("Add Text to Image")
        self.dispImageText.setToolTip("Add Text Box to Image")
        dispQuickSave = dispmenu.addAction("Quick Save Image")
        dispQuickSave.setShortcut("Ctrl+D")
        dispQuickSave.setToolTip(
            "Save Image to local directory with default name")
        dispSaveFile = dispmenu.addAction("Save Image")
        dispSaveFile.setShortcut("Ctrl+S")
        dispSaveFile.setStatusTip("Save Image using dialog")

        dispmenu.addAction(QtWidgets.QAction("Set Parameters", self,
                           triggered=self.setParameters))

        dispTitle.triggered.connect(self._title_input)
        dispUnit.triggered.connect(self._units_input)
        self.dispImageText.triggered.connect(self._add_ImageText)
        dispQuickSave.triggered.connect(self._quick_savefile)
        dispSaveFile.triggered.connect(self._savefile)

        self.dispButton.setMenu(dispmenu)

    def _add_tiltBoxUI(self):
        '''Create the Tilt Selection ComboBox.'''
        self.tiltBox = QtWidgets.QComboBox()
        self.tiltBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tiltBox.setToolTip("Select tilt elevation angle to display.\n"
                                "'Tilt Window' will launch popup.\n"
                                "Up/Down arrow keys Increase/Decrease tilt.")
        self.tiltBox.activated[str].connect(self._tiltAction)

    def _add_fieldBoxUI(self):
        '''Create the Field Selection ComboBox.'''
        self.fieldVerticalBox = QtWidgets.QComboBox()
        self.fieldVerticalBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fieldVerticalBox.setToolTip("Select variable/field in data file.\n"
                                 "'Field Window' will launch popup.\n")
        self.fieldVerticalBox.activated[str].connect(self._fieldVerticalAction)

        self.fieldHorizontalBox = QtWidgets.QComboBox()
        self.fieldHorizontalBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fieldHorizontalBox.setToolTip("Select variable/field in data file.\n"
                                 "'Field Window' will launch popup.\n")
        self.fieldHorizontalBox.activated[str].connect(self._fieldHorizontalAction)

    def _add_toolsBoxUI(self):
        '''Create the Tools Button menu.'''
        self.toolsButton = QtWidgets.QPushButton("Toolbox")
        self.toolsButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.toolsButton.setToolTip("Choose a tool to apply")
        toolmenu = QtWidgets.QMenu(self)
        toolZoomPan = toolmenu.addAction("Zoom/Pan")
        toolValueClick = toolmenu.addAction("Click for Value")
        toolSelectRegion = toolmenu.addAction("Select a Region of Interest")
        toolReset = toolmenu.addAction("Reset Tools")
        toolDefault = toolmenu.addAction("Reset File Defaults")
        toolZoomPan.triggered.connect(self.toolZoomPanCmd)
        toolValueClick.triggered.connect(self.toolValueClickCmd)
        toolSelectRegion.triggered.connect(self.toolSelectRegionCmd)
        toolReset.triggered.connect(self.toolResetCmd)
        toolDefault.triggered.connect(self.toolDefaultCmd)
        self.toolsButton.setMenu(toolmenu)

    def _select_all_sweeps(self):
        ''' Check all sweeps if action 'all sweeps' is checked.'''
        check = self.sweep_actions[0].isChecked()
        for action in self.sweep_actions[1:]:
            action.setChecked(check)
        self._update_plot()

    def _sweep_checked(self, checked):
        if checked is False:
            self.sweep_actions[0].setChecked(False)
        self._update_plot()

    ########################
    # Selectionion methods #
    ########################

    def NewRadar(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vradar <artview.core.core.Variable>`.

        This will:

        * Update fields and tilts lists and MenuBoxes
        * Check radar scan type and reset limits if needed
        * Reset units and title
        * If strong update: update plot
        '''
        if self.Vradar.value is None:
            self.fieldVerticalBox.clear()
            self.fieldHorizontalBox.clear()
            self.sweepMenu.clear()
            return

        # Get the tilt angles
        self.rTilts = self.Vradar.value.sweep_number['data'][:]
        # Get field names
        self.fieldnames = self.Vradar.value.fields.keys()

        # Update field and tilt MenuBox
        self._fillFieldBox()

        self.sweepMenu.clear()
        self.sweep_actions = []

        action = self.sweepMenu.addAction("all sweeps")
        self.sweep_actions.append(action)
        action.triggered.connect(self._select_all_sweeps)
        action.setCheckable(True)
        action.setChecked(True)
        self.sweepMenu.addAction(action)

        for sweep in range(len(self.rTilts)):
            action = self.sweepMenu.addAction("sweep " + str(sweep))
            self.sweep_actions.append(action)
            action.triggered.connect(self._sweep_checked)
            action.setCheckable(True)
            action.setChecked(True)
            self.sweepMenu.addAction(action)

        self.unitsVertical, self.unitsHorizontal = self._get_default_units()
        self.title = self._get_default_title()
        if strong:
            self._update_plot()

    def NewField(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vfield <artview.core.core.Variable>`.

        This will:

        * Reset colormap
        * Reset units
        * Update fields MenuBox
        * If strong update: update plot
        '''
        # XXX diferenciate between vertical and horizontal
        self.unitsVertical, self.unitsHorizontal = self._get_default_units()
        self.title = self._get_default_title()
        #idx = self.fieldBox.findText(variable.value)
        #self.fieldBox.setCurrentIndex(idx)
        if strong:
            self._update_plot()

    def NewGatefilter(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vgatefilter <artview.core.core.Variable>`.

        This will:

        * If strong update: update plot
        '''
        if strong:
            self._update_plot()

    ####################
    # Plotting methods #
    ####################

    def _set_fig_ax(self):
        '''Set the figure and axis to plot.'''
        self.XSIZE = 8
        self.YSIZE = 8
        self.fig = Figure(figsize=(self.XSIZE, self.YSIZE))
        self.ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
        self.VplotAxes.change(self.ax)

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area.'''
        self.canvas = FigureCanvasQTAgg(self.fig)
        # Add the widget to the canvas
        self.layout.addWidget(self.canvas, 1, 0, 8, 7)

    @staticmethod
    def _get_xy_values(radar, field_horizontal, field_vertical,
                       sweeps, gatefilter):
        xvalues = radar.fields[field_horizontal]['data']
        yvalues = radar.fields[field_vertical]['data']

        if gatefilter is None:
            gates = np.ma.getmaskarray(xvalues) | np.ma.getmaskarray(yvalues)
        else:
            gates = gatefilter.gate_excluded

        if sweeps is not None:
            sweep_filter = gates | True
            for sweep, (start, end) in enumerate(radar.iter_start_end()):
                if sweep in sweeps:
                    sweep_filter[start:end+1,:] = False
            gates = gates | sweep_filter

        xvalues = np.ma.MaskedArray(xvalues, mask=gates)
        yvalues = np.ma.MaskedArray(yvalues, mask=gates)

        return xvalues, yvalues

    @staticmethod
    def plot_correlation(radar, field_horizontal, field_vertical,
                         sweeps, gatefilter, ax, title, **kwargs):

        xvalues, yvalues = Correlation._get_xy_values(
            radar, field_horizontal, field_vertical, sweeps, gatefilter)

        ax.scatter(xvalues,yvalues,**kwargs)

        ax.set_title(title)

    @staticmethod
    def plot_regression(radar, field_horizontal, field_vertical,
                        sweeps, gatefilter, ax, vmin, vmax, **kwargs):

        xvalues, yvalues = Correlation._get_xy_values(
            radar, field_horizontal, field_vertical, sweeps, gatefilter)

        m,b = np.polyfit(xvalues[~xvalues.mask], yvalues[~xvalues.mask], 1)

        x=np.linspace(vmin,vmax,50)

        line = ax.plot(x,m * x + b, linestyle="--",
                       label='y = %f x + %f'%(m,b), **kwargs)
        ax.legend()
        return (m,b)

    def _update_plot(self):
        '''Draw/Redraw the plot.'''

        if self.Vradar.value is None:
            return

        # Create the plot with PyArt RadarDisplay
        self.ax.cla()  # Clear the plot axes

        self.VplotAxes.update()

        if ((self.VfieldVertical.value not in self.fieldnames) or
            (self.VfieldHorizontal.value not in self.fieldnames)):
            self.canvas.draw()
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;" +
                                         "background:rgba(255,0,0,255);" +
                                         "color:black;font-weight:bold;}")
            self.statusbar.showMessage("Field not Found in Radar", msecs=5000)
            return
        else:
            self.statusbar.setStyleSheet("QStatusBar{padding-left:8px;" +
                                         "background:rgba(0,0,0,0);" +
                                         "color:black;font-weight:bold;}")
            self.statusbar.clearMessage()

        if self.gatefilterToggle.isChecked():
            gatefilter = self.Vgatefilter.value
        else:
            gatefilter = None

        if self.sweep_actions[0].isChecked():
            sweeps = None
        else:
            sweeps = []
            for sweep, action in enumerate(self.sweep_actions[1:]):
                if action.isChecked():
                    sweeps.append(sweep)

        self.plot_correlation(
            self.Vradar.value, self.VfieldHorizontal.value,
            self.VfieldVertical.value, sweeps, gatefilter, self.ax, self.title,
            **{k: self.parameters[k] for k in
               ('s','facecolors', 'edgecolors', 'marker')}
            )


        self.ax.set_xscale(
            str(self.horizontal_scale_menu_group.checkedAction().text()))
        self.ax.set_yscale(
            str(self.vertical_scale_menu_group.checkedAction().text()))

        self.ax.set_xlabel(self.unitsHorizontal)
        self.ax.set_ylabel(self.unitsVertical)

        if self.regressionLineToggle.isChecked():
            vmin, vmax = self.ax.get_xlim()
            self.plot_regression(
                self.Vradar.value, self.VfieldHorizontal.value,
                self.VfieldVertical.value, sweeps, gatefilter, self.ax,
                vmin + 0.05 * (vmax-vmin), vmax - 0.05 * (vmax-vmin),
                color=self.parameters["color"])

        self.canvas.draw()

    #########################
    # Check methods #
    #########################

    def _get_default_title(self):
        '''Get default title from pyart.'''
        return 'Correlation'

    def _get_default_units(self):
        '''Get default units for current radar and field.'''
        vertical = ' '
        horizontal = ' '
        if self.Vradar.value is not None:
            try:
                vertical += self.Vradar.value.fields[
                    self.VfieldVertical.value]['units']
            except:
                pass
            try:
                horizontal += self.Vradar.value.fields[
                    self.VfieldHorizontal.value]['units']
            except:
                pass

        return (self.VfieldVertical.value + vertical,
                self.VfieldHorizontal.value + horizontal)

    ########################
    # Image save methods #
    ########################
    def _quick_savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display via PyArt interface.'''
        imagename = (str(self.VfieldVertical.value) + "VS." +
                     str(self.VfieldHorizontal.value) + ".png")
        self.canvas.print_figure(os.path.join(os.getcwd(), imagename), dpi=DPI)
        self.statusbar.showMessage(
            'Saved to %s' % os.path.join(os.getcwd(), imagename))

    def _savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display using PyQt dialog interface.'''
        imagename = (str(self.VfieldVertical.value) + "VS." +
                     str(self.VfieldHorizontal.value) + ".png")
        file_choices = "PNG (*.png)|*.png"
        path = unicode(QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save file', imagename, file_choices))
        if path:
            self.canvas.print_figure(path, dpi=DPI)
            self.statusbar.showMessage('Saved to %s' % path)



