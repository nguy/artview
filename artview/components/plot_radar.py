"""
plot_radar.py

Class instance used to make Display.
"""
# Load the needed packages
import numpy as np
import os
import pyart

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as \
    NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import Normalize as mlabNormalize
from matplotlib.colorbar import ColorbarBase as mlabColorbarBase
from matplotlib.pyplot import cm

from ..core import Variable, Component, common, VariableChoose, QtGui, QtCore
from ..core.points import Points

# Save image file type and DPI (resolution)
IMAGE_EXT = 'png'
DPI = 200
# ========================================================================


class RadarDisplay(Component):
    '''
    Class to create a display plot, using a returned Radar structure
    from the PyArt pyart.graph package.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vfield = None  #: see :ref:`shared_variable`
    Vtilt = None  #: see :ref:`shared_variable`
    Vlimits = None  #: see :ref:`shared_variable`
    Vcolormap = None  #: see :ref:`shared_variable`
    Vgatefilter = None  #: see :ref:`shared_variable`
    VplotAxes = None  #: see :ref:`shared_variable` (no internal use)
    VpathInteriorFunc = None  #: see :ref:`shared_variable` (no internal use)

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class'''
        args = _DisplayStart().startDisplay()
        args['parent'] = parent
        return self(**args), True

    def __init__(self, Vradar=None, Vfield=None, Vtilt=None, Vlimits=None,
                 Vcolormap=None, Vgatefilter=None,
                 name="RadarDisplay", parent=None):
        '''
        Initialize the class to create display.

        Parameters
        ----------
        [Optional]
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable. If None start new one with None.
        Vfield : :py:class:`~artview.core.core.Variable` instance
            Field signal variable. If None start new one with empty string.
        Vtilt : :py:class:`~artview.core.core.Variable` instance
            Tilt signal variable. If None start new one with 0.
        Vlimits : :py:class:`~artview.core.core.Variable` instance
            Limits signal variable.
            A value of None will instantiate a limits variable.
        Vcolormap : :py:class:`~artview.core.core.Variable` instance
            Colormap signal variable.
            A value of None will instantiate a colormap variable.
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
        super(RadarDisplay, self).__init__(name=name, parent=parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        # Set up signal, so that DISPLAY can react to
        # external (or internal) changes in radar, field,
        # lims and tilt (expected to be Core.Variable instances)
        # The capital V so people remember using ".value"
        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar
        if Vfield is None:
            self.Vfield = Variable('')
        else:
            self.Vfield = Vfield
        if Vtilt is None:
            self.Vtilt = Variable(0)
        else:
            self.Vtilt = Vtilt
        if Vlimits is None:
            self.Vlimits = Variable(None)
        else:
            self.Vlimits = Vlimits

        if Vcolormap is None:
            self.Vcolormap = Variable(None)
        else:
            self.Vcolormap = Vcolormap

        if Vgatefilter is None:
            self.Vgatefilter = Variable(None)
        else:
            self.Vgatefilter = Vgatefilter

        self.VpathInteriorFunc = Variable(self.getPathInteriorValues)
        self.VplotAxes = Variable(None)
        self.VpyartDisplay = Variable(None)

        self.sharedVariables = {"Vradar": self.NewRadar,
                                "Vfield": self.NewField,
                                "Vtilt": self.NewTilt,
                                "Vlimits": self.NewLims,
                                "Vcolormap": self.NewCmap,
                                "Vgatefilter": self.NewGatefilter,
                                "VpathInteriorFunc": None,
                                "VplotAxes": None,
                                "VpyartDisplay": self.NewDisplay}

        # Connect the components
        self.connectAllVariables()

        self.plot_type = None

        # Set plot title and colorbar units to defaults
        self.title = self._get_default_title()
        self.units = self._get_default_units()

        # Set the default range rings
        self.RngRingList = ["None", "10 km", "20 km", "30 km",
                            "50 km", "100 km"]
        self.RngRing = False

        # Find the PyArt colormap names
#        self.cm_names = [m for m in cm.datad if not m.endswith("_r")]
        self.cm_names = ["pyart_" + m for m in pyart.graph.cm.datad
                         if not m.endswith("_r")]
        self.cm_names.sort()

        # Create tool dictionary
        self.tools = {}

        # Set up Default limits and cmap
        if Vlimits is None:
            self._set_default_limits(strong=False)
        if Vcolormap is None:
            self._set_default_cmap(strong=False)

        # Create a figure for output
        self._set_fig_ax()

        # Launch the GUI interface
        self.LaunchGUI()

        # Initialize radar variable
        self.NewRadar(None, True)

        self.show()

    def keyPressEvent(self, event):
        '''Allow tilt adjustment via the Up-Down arrow keys.'''
        if event.key() == QtCore.Qt.Key_Up:
            self.TiltSelectCmd(self.Vtilt.value + 1)
        elif event.key() == QtCore.Qt.Key_Down:
            self.TiltSelectCmd(self.Vtilt.value - 1)
        else:
            super(RadarDisplay, self).keyPressEvent(event)

    ####################
    # GUI methods #
    ####################

    def LaunchGUI(self):
        '''Launches a GUI interface.'''
        # Create layout
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(8)

        # Create the widget
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self._set_figure_canvas()

        self.central_widget.setLayout(self.layout)

        # Add buttons along display for user control
        self.addButtons()
        self.setUILayout()

        # Set the status bar to display messages
        self.statusbar = self.statusBar()

    ##################################
    # User display interface methods #
    ##################################

    def addButtons(self):
        '''Add a series of buttons for user control over display.'''
        # Create the Display controls
        self._add_displayBoxUI()
        # Create the Tilt controls
        self._add_tiltBoxUI()
        # Create the Field controls
        self._add_fieldBoxUI()
        # Create the Tools controls
        self._add_toolsBoxUI()
        # Create the Informational label at top
        self._add_infolabel()

    def setUILayout(self):
        '''Setup the button/display UI layout.'''
        self.layout.addWidget(self.tiltBox, 0, 0)
        self.layout.addWidget(self.fieldBox, 0, 1)
        self.layout.addWidget(self.dispButton, 0, 2)
        self.layout.addWidget(self.toolsButton, 0, 3)
        self.layout.addWidget(self.infolabel, 0, 4)

    #############################
    # Functionality methods #
    #############################

    def _open_LimsDialog(self):
        '''Open a dialog box to change display limits.'''
        from .limits import limits_dialog
        limits, cmap, aspect, change = limits_dialog(
            self.Vlimits.value, self.Vcolormap.value, self.ax.get_aspect(),
            self.name)
        if aspect != self.ax.get_aspect():
            self.ax.set_aspect(aspect)
        if change == 1:
            self.Vcolormap.change(cmap)
            self.Vlimits.change(limits)


    def _fillTiltBox(self):
        '''Fill in the Tilt Window Box with current elevation angles.'''
        self.tiltBox.clear()
        self.tiltBox.addItem("Tilt Window")
        # Loop through and create each tilt button
        elevs = self.Vradar.value.fixed_angle['data'][:]
        for i, ntilt in enumerate(self.rTilts):
            btntxt = "%2.1f deg (Tilt %d)" % (elevs[i], i+1)
            self.tiltBox.addItem(btntxt)

    def _fillFieldBox(self):
        '''Fill in the Field Window Box with current variable names.'''
        self.fieldBox.clear()
        self.fieldBox.addItem("Field Window")
        # Loop through and create each field button
        for field in self.fieldnames:
            self.fieldBox.addItem(field)

    def _tiltAction(self, text):
        '''Define action for Tilt Button selection.'''
        if text == "Tilt Window":
            self._open_tiltbuttonwindow()
        else:
            ntilt = int(text.split("(Tilt ")[1][:-1])-1
            self.TiltSelectCmd(ntilt)

    def _fieldAction(self, text):
        '''Define action for Field Button selection.'''
        if text == "Field Window":
            self._open_fieldbuttonwindow()
        else:
            self.FieldSelectCmd(str(text))

    def _GateFilterToggleAction(self):
        '''Define action for GateFilterToggle menu selection.'''
        if self.gatefilterToggle.isChecked():
            self.gatefilterToggle.setText("GateFilter On")
        else:
            self.gatefilterToggle.setText("GateFilter Off")
        self._update_plot()

    def _IgnoreEdgesToggleAction(self):
        '''Define action for IgnoreEdgesToggle menu selection.'''
        if self.ignoreEdgesToggle.isChecked():
            self.ignoreEdges = False
        else:
            self.ignoreEdges = True
        self._update_plot()

    def _UseMapToggleAction(self):
        '''Define action for IgnoreEdgesToggle menu selection.'''
        self._check_file_type()
        self._update_display()

    def _title_input(self):
        '''Retrieve new plot title.'''
        val, entry = common.string_dialog_with_reset(
            self.title, "Plot Title", "Title:", self._get_default_title())
        if entry is True:
            self.title = val
            self._update_plot()

    def _units_input(self):
        '''Retrieve new plot units.'''
        val, entry = common.string_dialog_with_reset(
            self.units, "Plot Units", "Units:", self._get_default_units())
        if entry is True:
            self.units = val
            self._update_plot()

    def _open_tiltbuttonwindow(self):
        '''Open a TiltButtonWindow instance.'''
        from .level import LevelButtonWindow
        self.tiltbuttonwindow = LevelButtonWindow(
            self.Vtilt, plot_type=self.plot_type, Vcontainer=self.Vradar,
            name=self.name+" Tilt Selection", parent=self.parent)

    def _open_fieldbuttonwindow(self):
        '''Open a FieldButtonWindow instance.'''
        from .field import FieldButtonWindow
        self.fieldbuttonwindow = FieldButtonWindow(
            self.Vradar, self.Vfield,
            name=self.name+" Field Selection", parent=self.parent)

    def _add_RngRing_to_button(self):
        '''Add a menu to display range rings on plot.'''
        for RngRing in self.RngRingList:
            RingAction = self.dispRngRingmenu.addAction(RngRing)
            RingAction.setStatusTip("Apply Range Rings every %s" % RngRing)
            RingAction.triggered[()].connect(
                lambda RngRing=RngRing: self.RngRingSelectCmd(RngRing))
            self.dispRngRing.setMenu(self.dispRngRingmenu)

    def _add_cmaps_to_button(self):
        '''Add a menu to change colormap used for plot.'''
        for cm_name in self.cm_names:
            cmapAction = self.dispCmapmenu.addAction(cm_name)
            cmapAction.setStatusTip("Use the %s colormap" % cm_name)
            cmapAction.triggered[()].connect(
                lambda cm_name=cm_name: self.cmapSelectCmd(cm_name))
            self.dispCmap.setMenu(self.dispCmapmenu)

    def _add_displayBoxUI(self):
        '''Create the Display Options Button menu.'''
        self.dispButton = QtGui.QPushButton("Display Options")
        self.dispButton.setToolTip("Adjust display properties")
        self.dispButton.setFocusPolicy(QtCore.Qt.NoFocus)
        dispmenu = QtGui.QMenu(self)
        dispLimits = dispmenu.addAction("Adjust Display Limits")
        dispLimits.setToolTip("Set data, X, and Y range limits")
        self.gatefilterToggle = QtGui.QAction(
            'GateFilter On', dispmenu, checkable=True,
            triggered=self._GateFilterToggleAction)
        dispmenu.addAction(self.gatefilterToggle)
        self.gatefilterToggle.setChecked(True)
        self.ignoreEdgesToggle = QtGui.QAction(
            'Ignore Edges', dispmenu, checkable=True,
            triggered=self._IgnoreEdgesToggleAction)
        dispmenu.addAction(self.ignoreEdgesToggle)
        self.ignoreEdgesToggle.setChecked(False)
        self.useMapToggle = QtGui.QAction(
            'use MapDisplay', dispmenu, checkable=True,
            triggered=self._UseMapToggleAction)
        dispmenu.addAction(self.useMapToggle)
        self.useMapToggle.setChecked(False)
        dispTitle = dispmenu.addAction("Change Title")
        dispTitle.setToolTip("Change plot title")
        dispUnit = dispmenu.addAction("Change Units")
        dispUnit.setToolTip("Change units string")
        self.dispRngRing = dispmenu.addAction("Add Range Rings")
        self.dispRngRingmenu = QtGui.QMenu("Add Range Rings")
        self.dispRngRingmenu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.dispCmap = dispmenu.addAction("Change Colormap")
        self.dispCmapmenu = QtGui.QMenu("Change Cmap")
        self.dispCmapmenu.setFocusPolicy(QtCore.Qt.NoFocus)
        dispQuickSave = dispmenu.addAction("Quick Save Image")
        dispQuickSave.setShortcut("Ctrl+D")
        dispQuickSave.setToolTip(
            "Save Image to local directory with default name")
        dispSaveFile = dispmenu.addAction("Save Image")
        dispSaveFile.setShortcut("Ctrl+S")
        dispSaveFile.setStatusTip("Save Image using dialog")

        dispLimits.triggered[()].connect(self._open_LimsDialog)
        dispTitle.triggered[()].connect(self._title_input)
        dispUnit.triggered[()].connect(self._units_input)
        dispQuickSave.triggered[()].connect(self._quick_savefile)
        dispSaveFile.triggered[()].connect(self._savefile)

        self._add_RngRing_to_button()
        self._add_cmaps_to_button()
        self.dispButton.setMenu(dispmenu)

    def _add_tiltBoxUI(self):
        '''Create the Tilt Selection ComboBox.'''
        self.tiltBox = QtGui.QComboBox()
        self.tiltBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tiltBox.setToolTip("Select tilt elevation angle to display.\n"
                                "'Tilt Window' will launch popup.\n"
                                "Up/Down arrow keys Increase/Decrease tilt.")
        self.tiltBox.activated[str].connect(self._tiltAction)

    def _add_fieldBoxUI(self):
        '''Create the Field Selection ComboBox.'''
        self.fieldBox = QtGui.QComboBox()
        self.fieldBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fieldBox.setToolTip("Select variable/field in data file.\n"
                                 "'Field Window' will launch popup.\n")
        self.fieldBox.activated[str].connect(self._fieldAction)

    def _add_toolsBoxUI(self):
        '''Create the Tools Button menu.'''
        self.toolsButton = QtGui.QPushButton("Toolbox")
        self.toolsButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.toolsButton.setToolTip("Choose a tool to apply")
        toolmenu = QtGui.QMenu(self)
        toolZoomPan = toolmenu.addAction("Zoom/Pan")
        toolValueClick = toolmenu.addAction("Click for Value")
        toolSelectRegion = toolmenu.addAction("Select a Region of Interest")
        toolReset = toolmenu.addAction("Reset Tools")
        toolDefault = toolmenu.addAction("Reset File Defaults")
        toolZoomPan.triggered[()].connect(self.toolZoomPanCmd)
        toolValueClick.triggered[()].connect(self.toolValueClickCmd)
        toolSelectRegion.triggered[()].connect(self.toolSelectRegionCmd)
        toolReset.triggered[()].connect(self.toolResetCmd)
        toolDefault.triggered[()].connect(self.toolDefaultCmd)
        self.toolsButton.setMenu(toolmenu)

    def _add_infolabel(self):
        '''Create an information label about the display'''
        self.infolabel = QtGui.QLabel("Radar: \n"
                                      "Field: \n"
                                      "Tilt: ", self)
        self.infolabel.setStyleSheet('color: red; font: italic 10px')
        self.infolabel.setToolTip("Filename not loaded")

    def _update_infolabel(self):
        if self.Vradar.value is None:
            return
        self.infolabel.setText("Radar: %s\n"
                               "Field: %s\n"
                               "Tilt: %d" % (
                                   self.Vradar.value.metadata[
                                       'instrument_name'],
                                   self.Vfield.value,
                                   self.Vtilt.value+1))
        if hasattr(self.Vradar.value, 'filename'):
            self.infolabel.setToolTip(self.Vradar.value.filename)

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
        # test for None
        if self.Vradar.value is None:
            self.fieldBox.clear()
            self.tiltBox.clear()
            return

        # Get the tilt angles
        self.rTilts = self.Vradar.value.sweep_number['data'][:]
        # Get field names
        self.fieldnames = self.Vradar.value.fields.keys()

        # Check the file type and initialize limts
        self._check_file_type()

        # Update field and tilt MenuBox
        self._fillTiltBox()
        self._fillFieldBox()

        self.units = self._get_default_units()
        self.title = self._get_default_title()
        if strong:
            self._update_display()
            self._update_infolabel()

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
        if self.Vcolormap.value['lock'] is False:
            self._set_default_cmap(strong=False)
        self.units = self._get_default_units()
        self.title = self._get_default_title()
        idx = self.fieldBox.findText(self.Vfield.value)
        self.fieldBox.setCurrentIndex(idx)
        if strong:
            self._update_plot()
            self._update_infolabel()

    def NewLims(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vlimits <artview.core.core.Variable>`.

        This will:

        * If strong update: update axes
        '''
        if strong:
            self._update_axes()

    def NewCmap(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vcolormap <artview.core.core.Variable>`.

        This will:

        * If strong update: update plot
        '''
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

    def NewTilt(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vtilt <artview.core.core.Variable>`.

        This will:

        * Update tilt MenuBox
        * If strong update: update plot
        '''
        # +1 since the first one is "Tilt Window"
        self.tiltBox.setCurrentIndex(self.Vtilt.value+1)
        if strong:
            self._update_plot()
            self._update_infolabel()

    def NewDisplay(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`VpyartDisplay <artview.core.core.Variable>`.

        This will:

        * If strong update: update plot
        * redraw canvas
        '''
        if strong:
            self._update_plot()
        else: #  update_plot already redraw
            self.canvas.draw()

    def TiltSelectCmd(self, ntilt):
        '''
        Captures tilt selection and update tilt
        :py:class:`~artview.core.core.Variable`.
        '''
        if ntilt < 0:
            ntilt = len(self.rTilts)-1
        elif ntilt >= len(self.rTilts):
            ntilt = 0
        self.Vtilt.change(ntilt)

    def FieldSelectCmd(self, name):
        '''
        Captures field selection and update field
        :py:class:`~artview.core.core.Variable`.
        '''
        self.Vfield.change(name)

    def RngRingSelectCmd(self, ringSel):
        '''
        Captures Range Ring selection and
        redraws the field with range rings.
        '''
        if ringSel is "None":
            self.RngRing = False
        else:
            self.RngRing = True
            # Find the unambigous range of the radar
            try:
                unrng = int(self.Vradar.value.instrument_parameters[
                    'unambiguous_range']['data'][0]/1000)
            except:
                unrng = int(self.Vlimits.value['xmax'])

            # Set the step
            if ringSel == '10 km':
                ringdel = 10
            if ringSel == '20 km':
                ringdel = 20
            if ringSel == '30 km':
                ringdel = 30
            if ringSel == '50 km':
                ringdel = 50
            if ringSel == '100 km':
                ringdel = 100

            # Calculate an array of range rings
            self.RNG_RINGS = range(ringdel, unrng, ringdel)

        self._update_plot()

    def cmapSelectCmd(self, cm_name):
        '''Captures colormap selection and redraws.'''
        CMAP = cm_name
        self.Vcolormap.value['cmap'] = cm_name
        self.Vcolormap.update()

    def toolZoomPanCmd(self):
        '''Creates and connects to a Zoom/Pan instance.'''
        from .tools import ZoomPan
        scale = 1.1
        self.tools['zoompan'] = ZoomPan(
            self.Vlimits, self.ax,
            base_scale=scale, parent=self.parent)
        self.tools['zoompan'].connect()

    def toolValueClickCmd(self):
        '''Creates and connects to Point-and-click value retrieval'''
        from .tools import ValueClick
        self.tools['valueclick'] = ValueClick(
            self, name=self.name + "ValueClick", parent=self.parent)
        self.tools['valueclick'].connect()

    def toolSelectRegionCmd(self):
        '''Creates and connects to Region of Interest instance'''
        from .display_select_region import DisplaySelectRegion
        self.tools['select_region'] = DisplaySelectRegion(
            self.VplotAxes, self.VpathInteriorFunc, self.Vfield,
            name=self.name + " SelectRegion", parent=self)

    def toolResetCmd(self):
        '''Reset tools via disconnect.'''
        from . import tools
        self.tools = tools.reset_tools(self.tools)

    def toolDefaultCmd(self):
        '''Restore the Display defaults.'''
        for key in self.tools.keys():
            if self.tools[key] is not None:
                self.tools[key].disconnect()
                self.tools[key] = None
        if self.Vcolormap.value['lock'] is False:
            self._set_default_cmap()
        self._set_default_limits()

    def getPathInteriorValues(self, paths):
        '''
        Return the bins values path.

        Parameters
        ----------
        paths : list of :py:class:`matplotlib.path.Path` instances

        Returns
        -------
        points : :py:class`artview.core.points.Points`
            Points object containing all bins of the current radar
            and tilt inside path. Axes : 'x_disp', 'y_disp', 'ray_index',
            'range_index', 'azimuth', 'range'. Fields: just current field

        Notes
        -----
            If Vradar.value is None, returns None
        '''
        from .tools import interior_radar
        radar = self.Vradar.value
        tilt = self.Vtilt.value
        if radar is None or not self.VpyartDisplay.value:
            return None

        try:
            iter(paths)
        except:
            paths = [paths]

        xy = np.empty((0, 2))
        idx = np.empty((0, 2), dtype=np.int)

        for path in paths:
            try:
                x, y, z = self.VpyartDisplay.value._get_x_y_z(
                    tilt, False, True)
            except:
                x, y, z = self.VpyartDisplay.value._get_x_y_z(
                    self.Vfield.value, tilt, False, True)
            if self.plot_type == "radarAirborne":
                _xy = np.empty(shape=(x.size, 2))
                _xy[:, 0] = x.flatten()
                _xy[:, 1] = z.flatten()
                ind = np.nonzero([path.contains_point(p) for p in _xy])[0]

                _xy = _xy[ind]
                ngates = radar.range['data'].size
                rayIndex = (radar.sweep_start_ray_index['data'][tilt] +
                            ind / ngates)
                gateIndex = ind % ngates
                _idx = np.concatenate((rayIndex[np.newaxis],
                                       gateIndex[np.newaxis]), axis=0)
                _idx = _idx.transpose().astype(np.int)
            elif self.plot_type == "radarPpi":
                _xy = np.empty(shape=(x.size, 2))
                _xy[:, 0] = x.flatten()
                _xy[:, 1] = y.flatten()
                ind = np.nonzero([path.contains_point(p) for p in _xy])[0]

                _xy = _xy[ind]
                ngates = radar.range['data'].size
                rayIndex = (radar.sweep_start_ray_index['data'][tilt] +
                            ind / ngates)
                gateIndex = ind % ngates
                _idx = np.concatenate((rayIndex[np.newaxis],
                                       gateIndex[np.newaxis]), axis=0)
                _idx = _idx.transpose().astype(np.int)
            elif self.plot_type == "radarRhi":
                _xy = np.empty(shape=(x.size, 2))
                r = np.sqrt(x ** 2 + y ** 2) * np.sign(y)
                if np.all(r < 1.):
                    r = -r
                _xy[:, 0] = r.flatten()
                _xy[:, 1] = z.flatten()
                ind = np.nonzero([path.contains_point(p) for p in _xy])[0]

                _xy = _xy[ind]
                ngates = radar.range['data'].size
                rayIndex = (radar.sweep_start_ray_index['data'][tilt] +
                            ind / ngates)
                gateIndex = ind % ngates
                _idx = np.concatenate((rayIndex[np.newaxis],
                                       gateIndex[np.newaxis]), axis=0)
                _idx = _idx.transpose().astype(np.int)

            xy = np.concatenate((xy, _xy))
            idx = np.concatenate((idx, _idx))

        xaxis = {'data':  xy[:, 0] * 1000.,
                 'long_name': 'X-coordinate in Cartesian system',
                 'axis': 'X',
                 'units': 'm'}

        yaxis = {'data':  xy[:, 1] * 1000.,
                 'long_name': 'Y-coordinate in Cartesian system',
                 'axis': 'Y',
                 'units': 'm'}

        azi = radar.azimuth.copy()
        azi['data'] = radar.azimuth['data'][idx[:, 0]]

        rng = radar.range.copy()
        rng['data'] = radar.range['data'][idx[:, 1]]

        field = radar.fields[self.Vfield.value].copy()
        field['data'] = radar.fields[self.Vfield.value]['data'][
            idx[:, 0], idx[:, 1]]

        ray_idx = {'data': idx[:, 0],
                   'long_name': 'index in ray dimension'}
        rng_idx = {'data': idx[:, 1],
                   'long_name': 'index in range dimension'}

        axes = {'x_disp': xaxis,
                'y_disp': yaxis,
                'ray_index': ray_idx,
                'range_index': rng_idx,
                'azimuth': azi,
                'range': rng}

        fields = {self.Vfield.value: field}

        points = Points(fields, axes, radar.metadata.copy(), xy.shape[0])

        return points

    ####################
    # Plotting methods #
    ####################

    def _set_fig_ax(self):
        '''Set the figure and axis to plot.'''
        self.XSIZE = 8
        self.YSIZE = 8
        self.fig = Figure(figsize=(self.XSIZE, self.YSIZE))
        self.ax = self.fig.add_axes([0.2, 0.2, 0.7, 0.7])
        self.cax = self.fig.add_axes([0.2, 0.10, 0.7, 0.02])
        self.VplotAxes.change(self.ax)
        # self._update_axes()

    def _update_fig_ax(self):
        '''Set the figure and axis to plot.'''
        if self.plot_type in ("radarAirborne", "radarRhi"):
            self.YSIZE = 5
        else:
            self.YSIZE = 8
        xwidth = 0.7
        yheight = 0.7  # * float(self.YSIZE) / float(self.XSIZE)
        self.ax.set_position([0.2, 0.55-0.5*yheight, xwidth, yheight])
        self.cax.set_position([0.2, 0.10, xwidth, 0.02])
        self._update_axes()

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area.'''
        self.canvas = FigureCanvasQTAgg(self.fig)
        # Add the widget to the canvas
        self.layout.addWidget(self.canvas, 1, 0, 7, 6)

    def _update_display(self):
        if self.plot_type == "radarAirborne":
            from pkg_resources import parse_version
            if parse_version(pyart.__version__) >= parse_version('1.6.0'):
                display = pyart.graph.AirborneRadarDisplay(
                    self.Vradar.value)
        elif self.plot_type == "radarPpiMap":
            display = pyart.graph.RadarMapDisplay(self.Vradar.value)
        elif self.plot_type == "radarPpi":
            display = pyart.graph.RadarDisplay(self.Vradar.value)
        elif self.plot_type == "radarRhi":
            display = pyart.graph.RadarDisplay(self.Vradar.value)
        self.VpyartDisplay.change(display)

    def _update_plot(self):
        '''Draw/Redraw the plot.'''

        if self.Vradar.value is None:
            return

        # Create the plot with PyArt RadarDisplay
        self.ax.cla()  # Clear the plot axes
        self.cax.cla()  # Clear the colorbar axes

        self.VplotAxes.update()

        if self.Vfield.value not in self.Vradar.value.fields.keys():
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

        title = self.title
        limits = self.Vlimits.value
        cmap = self.Vcolormap.value
        display = self.VpyartDisplay.value
        if self.gatefilterToggle.isChecked():
            gatefilter = self.Vgatefilter.value
        else:
            gatefilter = None
        if self.ignoreEdgesToggle.isChecked():
            ignoreEdges = False
        else:
            ignoreEdges = True

        if 'norm' in cmap:
            norm = cmap['norm']
        else:
            norm = None

        if self.plot_type == "radarAirborne":
            self.plot = display.plot_sweep_grid(
                self.Vfield.value, vmin=cmap['vmin'],
                vmax=cmap['vmax'], colorbar_flag=False, cmap=cmap['cmap'],
                norm=norm, mask_outside=True,
                edges=ignoreEdges, gatefilter=gatefilter,
                ax=self.ax, fig=self.fig, title=title)
            display.plot_grid_lines()

        elif self.plot_type == "radarPpi" or self.plot_type == "radarPpiMap":
            # Create Plot
            if self.useMapToggle.isChecked():
                plot_ppi = display.plot_ppi_map
            else:
                plot_ppi = display.plot_ppi

            self.plot = plot_ppi(
                self.Vfield.value, self.Vtilt.value,
                vmin=cmap['vmin'], vmax=cmap['vmax'], norm=norm,
                colorbar_flag=False, cmap=cmap['cmap'], mask_outside=True,
                edges=ignoreEdges, gatefilter=gatefilter,
                ax=self.ax, fig=self.fig, title=title)
            # Add range rings
            if self.RngRing:
                display.plot_range_rings(self.RNG_RINGS, ax=self.ax)
            # Add radar location
            display.plot_cross_hair(5., ax=self.ax)

        elif self.plot_type == "radarRhi":
            # Create Plot
            self.plot = display.plot_rhi(
                self.Vfield.value, self.Vtilt.value,
                vmin=cmap['vmin'], vmax=cmap['vmax'], norm=norm,
                colorbar_flag=False, cmap=cmap['cmap'], mask_outside=True,
                edges=ignoreEdges, gatefilter=gatefilter,
                ax=self.ax, fig=self.fig, title=title)
            # Add range rings
            if self.RngRing:
                display.plot_range_rings(self.RNG_RINGS, ax=self.ax)

        self._update_axes()
        if norm is None:
            norm = mlabNormalize(vmin=cmap['vmin'],
                                 vmax=cmap['vmax'])
        self.cbar = mlabColorbarBase(self.cax, cmap=cmap['cmap'],
                                     norm=norm, orientation='horizontal')
        self.cbar.set_label(self.units)

#        print "Plotting %s field, Tilt %d in %s" % (
#            self.Vfield.value, self.Vtilt.value+1, self.name)
        self.canvas.draw()

    def _update_axes(self):
        '''Change the Plot Axes.'''
        limits = self.Vlimits.value
        self.ax.set_xlim(limits['xmin'], limits['xmax'])
        self.ax.set_ylim(limits['ymin'], limits['ymax'])
        self.ax.figure.canvas.draw()

    #########################
    # Check methods #
    #########################

    def _check_file_type(self):
        '''Check file to see if the file is airborne or rhi.'''
        radar = self.Vradar.value
        old_plot_type = self.plot_type
        if radar.scan_type != 'rhi':
            if self.useMapToggle.isChecked():
                self.plot_type = "radarPpiMap"
            else:
                self.plot_type = "radarPpi"
        else:
            if 'platform_type' in radar.metadata:
                if ('aircraft' in radar.metadata['platform_type'] or
                    'aircraft_tail' in radar.metadata['platform_type']):
                    self.plot_type = "radarAirborne"
                else:
                    self.plot_type = "radarRhi"
            else:
                self.plot_type = "radarRhi"

        if self.plot_type != old_plot_type:
            print("Changed Scan types, reinitializing")
            self.toolResetCmd()
            self._set_default_limits()
            self._update_fig_ax()

    def _set_default_limits(self, strong=True):
        ''' Set limits to pre-defined default.'''
        from .limits import _default_limits
        limits, cmap = _default_limits(
            self.Vfield.value, self.plot_type)
        self.Vlimits.change(limits, strong)

    def _set_default_cmap(self, strong=True):
        ''' Set colormap to pre-defined default.'''
        cmap = pyart.config.get_field_colormap(self.Vfield.value)
        d = {}
        d['cmap'] = cmap
        d['lock'] = False
        lims = pyart.config.get_field_limits(self.Vfield.value,
                                             self.Vradar.value,
                                             self.Vtilt.value)
        if lims != (None, None):
            d['vmin'] = lims[0]
            d['vmax'] = lims[1]
        else:
            d['vmin'] = -10
            d['vmax'] = 65

        # HACK while pyart don't implemt it self
        if (self.Vradar.value is not None and
            self.Vfield.value in self.Vradar.value.fields):
            if 'valid_min' in self.Vradar.value.fields[self.Vfield.value]:
                d['vmin'] = self.Vradar.value.fields[self.Vfield.value][
                    'valid_min']
            if 'valid_max' in self.Vradar.value.fields[self.Vfield.value]:
                d['vmax'] = self.Vradar.value.fields[self.Vfield.value][
                    'valid_max']

        self.Vcolormap.change(d, strong)

    def _get_default_title(self):
        '''Get default title from pyart.'''
        if (self.Vradar.value is None or
            self.Vfield.value not in self.Vradar.value.fields):
            return ''
        return pyart.graph.common.generate_title(self.Vradar.value,
                                                 self.Vfield.value,
                                                 self.Vtilt.value)

    def _get_default_units(self):
        '''Get default units for current radar and field.'''
        if self.Vradar.value is not None:
            try:
                return self.Vradar.value.fields[self.Vfield.value]['units']
            except:
                return ''
        else:
            return ''

    ########################
    # Image save methods #
    ########################
    def _quick_savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display via PyArt interface.'''
        imagename = self.VpyartDisplay.value.generate_filename(
            self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        self.canvas.print_figure(os.path.join(os.getcwd(), imagename), dpi=DPI)
        self.statusbar.showMessage(
            'Saved to %s' % os.path.join(os.getcwd(), imagename))

    def _savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display using PyQt dialog interface.'''
        PBNAME = self.VpyartDisplay.value.generate_filename(
            self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        file_choices = "PNG (*.png)|*.png"
        path = unicode(QtGui.QFileDialog.getSaveFileName(
            self, 'Save file', PBNAME, file_choices))
        if path:
            self.canvas.print_figure(path, dpi=DPI)
            self.statusbar.showMessage('Saved to %s' % path)

    ########################
    #      get methods     #
    ########################

    def getPlotAxis(self):
        '''Get :py:class:`matplotlib.axes.Axes` instance of main plot.'''
        return self.ax

    def getStatusBar(self):
        '''Get :py:class:`PyQt4.QtGui.QStatusBar` instance.'''
        return self.statusbar

    def getField(self):
        '''Get current field.'''
        return self.Vfield.value

    def getUnits(self):
        '''Get current units.'''
        return self.units

    def getRadar(self):
        ''' get current radar '''
        return self.Vradar.value

    def getTilt(self):
        ''' get current tilt '''
        return self.Vtilt.value


class _DisplayStart(QtGui.QDialog):
    '''
    Dialog Class for graphical start of display, to be used in guiStart.
    '''

    def __init__(self):
        '''Initialize the class to create the interface.'''
        super(_DisplayStart, self).__init__()
        self.result = {}
        self.layout = QtGui.QGridLayout(self)
        # set window as modal
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.setupUi()

    def chooseRadar(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vradar"] = getattr(item[1], item[2])

    def chooseField(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vfield"] = getattr(item[1], item[2])

    def chooseTilt(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vtilt"] = getattr(item[1], item[2])

    def chooseLims(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vlimits"] = getattr(item[1], item[2])

    def setupUi(self):

        self.radarButton = QtGui.QPushButton("Find Variable")
        self.radarButton.clicked.connect(self.chooseRadar)
        self.layout.addWidget(QtGui.QLabel("VRadar"), 0, 0)
        self.layout.addWidget(self.radarButton, 0, 1, 1, 3)

        self.fieldButton = QtGui.QPushButton("Find Variable")
        self.fieldButton.clicked.connect(self.chooseField)
        self.layout.addWidget(QtGui.QLabel("Vfield"), 1, 0)
        self.field = QtGui.QLineEdit("")
        self.layout.addWidget(self.field, 1, 1)
        self.layout.addWidget(QtGui.QLabel("or"), 1, 2)
        self.layout.addWidget(self.fieldButton, 1, 3)

        self.tiltButton = QtGui.QPushButton("Find Variable")
        self.tiltButton.clicked.connect(self.chooseTilt)
        self.layout.addWidget(QtGui.QLabel("Vtilt"), 2, 0)
        self.tilt = QtGui.QSpinBox()
        self.layout.addWidget(self.tilt, 2, 1)
        self.layout.addWidget(QtGui.QLabel("or"), 2, 2)
        self.layout.addWidget(self.tiltButton, 2, 3)

        self.limsButton = QtGui.QPushButton("Find Variable")
        self.limsButton.clicked.connect(self.chooseLims)
        self.layout.addWidget(QtGui.QLabel("Vlimits"), 3, 0)
        self.layout.addWidget(self.limsButton, 3, 1, 1, 3)

        self.name = QtGui.QLineEdit("RadarDisplay")
        self.layout.addWidget(QtGui.QLabel("name"), 4, 0)
        self.layout.addWidget(self.name, 4, 1, 1, 3)

        self.closeButton = QtGui.QPushButton("Start")
        self.closeButton.clicked.connect(self.closeDialog)
        self.layout.addWidget(self.closeButton, 5, 0, 1, 5)

    def closeDialog(self):
        self.done(QtGui.QDialog.Accepted)

    def startDisplay(self):
        self.exec_()

        # if no Vradar abort
        if 'Vradar' not in self.result:
            self.result['Vradar'] = Variable(None)
            # common.ShowWarning("Must select a variable for Vradar")
            # I'm allowing this to continue, but this will result in error

        # if Vfield, Vtilt, Vlimits were not select create new
        field = str(self.field.text())
        tilt = self.tilt.value()
        if 'Vfield' not in self.result:
            self.result['Vfield'] = Variable(field)
        if 'Vtilt' not in self.result:
            self.result['Vtilt'] = Variable(tilt)

        self.result['name'] = str(self.name.text())

        return self.result
