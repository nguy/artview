"""
plot_grid.py

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


class GridDisplay(Component):
    '''
    Class to create a display plot, using a Grid structure.
    '''

    Vgrid = None  #: see :ref:`shared_variable`
    Vfield = None  #: see :ref:`shared_variable`
    VlevelZ = None \
        #: see :ref:`shared_variable`, only used if plot_type="gridZ"
    VlevelY = None \
        #: see :ref:`shared_variable`, only used if plot_type="gridY"
    VlevelX = None \
        #: see :ref:`shared_variable`, only used if plot_type="gridX"
    Vcolormap = None  #: see :ref:`shared_variable`
    VplotAxes = None  #: see :ref:`shared_variable` (no internal use)
    VpathInteriorFunc = None  #: see :ref:`shared_variable` (no internal use)

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class'''
        args = _DisplayStart().startDisplay()
        args['parent'] = parent
        return self(**args), True

    def __init__(self, Vgrid=None, Vfield=None, VlevelZ=None, VlevelY=None,
                 VlevelX=None, Vlimits=None, Vcolormap=None, plot_type="gridZ",
                 name="Display", parent=None):
        '''
        Initialize the class to create display.

        Parameters
        ----------
        [Optional]
        Vgrid : :py:class:`~artview.core.core.Variable` instance
            grid signal variable. If None start new one with None.
        Vfield : :py:class:`~artview.core.core.Variable` instance
            Field signal variable. If None start new one with empty string.
        VlevelZ : :py:class:`~artview.core.core.Variable` instance
            Signal variable for vertical level, only used if
            plot_type="gridZ". If None start with value zero.
        VlevelY : :py:class:`~artview.core.core.Variable` instance
            Signal variable for latitudinal level, only used if
            plot_type="gridY". If None start with value zero.
        VlevelX : :py:class:`~artview.core.core.Variable` instance
            Signal variable for longitudinal level, only used if
            plot_type="gridX". If None start with value zero.
        Vlimits : :py:class:`~artview.core.core.Variable` instance
            Limits signal variable.
            A value of None will instantiate a limits variable.
        Vcolormap : :py:class:`~artview.core.core.Variable` instance
            Colormap signal variable.
            A value of None will instantiate a colormap variable.
        plot_type : "gridZ", "gridY" or "gridX"
            Define plot type, "gridZ" will plot a Z level, that is a XY
            plane. Analog for "gridY" and "gridZ"
        name : string
            Display window name.
        parent : PyQt instance
            Parent instance to associate to Display window.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        Notes
        -----
        This class records the selected button and passes the
        change value back to variable.
        '''
        super(GridDisplay, self).__init__(name=name, parent=parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.basemap = None
        # Set up signal, so that DISPLAY can react to
        # external (or internal) changes in grid, field,
        # lims and level (expected to be Core.Variable instances)
        # The capital V so people remember using ".value"
        if Vgrid is None:
            self.Vgrid = Variable(None)
        else:
            self.Vgrid = Vgrid
        if Vfield is None:
            self.Vfield = Variable('')
        else:
            self.Vfield = Vfield

        if VlevelZ is None:
            self.VlevelZ = Variable(0)
        else:
            self.VlevelZ = VlevelZ
        if VlevelY is None:
            self.VlevelY = Variable(0)
        else:
            self.VlevelY = VlevelY
        if VlevelX is None:
            self.VlevelX = Variable(0)
        else:
            self.VlevelX = VlevelX
        if Vlimits is None:
            self.Vlimits = Variable(None)
        else:
            self.Vlimits = Vlimits

        if Vcolormap is None:
            self.Vcolormap = Variable(None)
        else:
            self.Vcolormap = Vcolormap

        self.VpathInteriorFunc = Variable(self.getPathInteriorValues)
        self.VplotAxes = Variable(None)

        self.sharedVariables = {"Vgrid": self.NewGrid,
                                "Vfield": self.NewField,
                                "Vlimits": self.NewLimits,
                                "Vcolormap": self.NewColormap,
                                "VpathInteriorFunc": None,
                                "VplotAxes": None}

        self.change_plot_type(plot_type)

        # Connect the components
        self.connectAllVariables()

        # Set plot title and colorbar units to defaults
        self.title = self._get_default_title()
        self.units = self._get_default_units()

        # set default latlon lines
        self.lat_lines = np.linspace(-90, 90, num=181)
        self.lon_lines = np.linspace(-180, 180, num=361)

        # Find the PyArt colormap names
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

        # Initialize grid variable
        self.NewGrid(None, True)
        self._update_fig_ax()
        self.show()

    def keyPressEvent(self, event):
        '''Allow level adjustment via the Up-Down arrow keys.'''
        if event.key() == QtCore.Qt.Key_Up:
            self.LevelSelectCmd(self.Vlevel.value + 1)
        elif event.key() == QtCore.Qt.Key_Down:
            self.LevelSelectCmd(self.Vlevel.value - 1)
        else:
            super(GridDisplay, self).keyPressEvent(event)

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
        # Create the Level controls
        self._add_levelBoxUI()
        # Create the Field controls
        self._add_fieldBoxUI()
        # Create the Tools controls
        self._add_toolsBoxUI()
        # Create the Informational label at top
        self._add_infolabel()

    def setUILayout(self):
        '''Setup the button/display UI layout.'''
        self.layout.addWidget(self.levelBox, 0, 0)
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

    def _fillLevelBox(self):
        '''Fill in the Level Window Box with current levels.'''
        self.levelBox.clear()
        self.levelBox.addItem("Level Window")
        # Loop through and create each level button
        if self.plot_type == "gridZ":
            levels = self.Vgrid.value.axes['z_disp']['data']
        elif self.plot_type == "gridY":
            levels = self.Vgrid.value.axes['y_disp']['data']
        elif self.plot_type == "gridX":
            levels = self.Vgrid.value.axes['x_disp']['data']

        for nlevel in range(len(levels)):
            btntxt = "%2.1f m (level %d)" % (levels[nlevel], nlevel+1)
            self.levelBox.addItem(btntxt)

    def _fillFieldBox(self):
        '''Fill in the Field Window Box with current variable names.'''
        self.fieldBox.clear()
        self.fieldBox.addItem("Field Window")
        # Loop through and create each field button
        for field in self.fieldnames:
            self.fieldBox.addItem(field)

    def _levelAction(self, text):
        '''Define action for Level Button selection.'''
        if text == "Level Window":
            self._open_levelbuttonwindow()
        else:
            nlevel = int(text.split("(level ")[1][:-1])-1
            self.LevelSelectCmd(nlevel)

    def _fieldAction(self, text):
        '''Define action for Field Button selection.'''
        if text == "Field Window":
            self._open_fieldbuttonwindow()
        else:
            self.FieldSelectCmd(str(text))

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

    def _open_levelbuttonwindow(self):
        '''Open a LevelButtonWindow instance.'''
        from .level import LevelButtonWindow
        if self.plot_type == "gridZ":
            self.levelbuttonwindow = LevelButtonWindow(
                self.Vlevel, self.plot_type, Vcontainer=self.Vgrid,
                controlType="radio", name=self.name+" Level Selection",
                parent=self.parent)
        else:
            self.levelbuttonwindow = LevelButtonWindow(
                self.Vlevel, self.plot_type, Vcontainer=self.Vgrid,
                controlType="slider", name=self.name+" Level Selection",
                parent=self.parent)

    def _open_fieldbuttonwindow(self):
        '''Open a FieldButtonWindow instance.'''
        from .field import FieldButtonWindow
        self.fieldbuttonwindow = FieldButtonWindow(
            self.Vgrid, self.Vfield,
            name=self.name+" Field Selection", parent=self.parent)

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
        dispTitle = dispmenu.addAction("Change Title")
        dispTitle.setToolTip("Change plot title")
        dispUnit = dispmenu.addAction("Change Units")
        dispUnit.setToolTip("Change units string")
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

        self._add_cmaps_to_button()
        self.dispButton.setMenu(dispmenu)

    def _add_levelBoxUI(self):
        '''Create the Level Selection ComboBox.'''
        self.levelBox = QtGui.QComboBox()
        self.levelBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.levelBox.setToolTip(
            "Select level slice to display.\n"
            "'Level Window' will launch popup.\n"
            "Up/Down arrow keys Increase/Decrease level.")

        self.levelBox.activated[str].connect(self._levelAction)

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
        self.infolabel = QtGui.QLabel("Grid: \n"
                                      "Field: \n"
                                      "Level: ", self)
        self.infolabel.setStyleSheet('color: red; font: italic 10px')
        self.infolabel.setToolTip("Filename not loaded")

    def _update_infolabel(self):
        if self.Vgrid.value is None:
            return
        self.infolabel.setText(
            "Grid: %s\n"
            "Field: %s\n"
            "Level: %d" % (self.Vgrid.value.metadata['instrument_name'],
                           self.Vfield.value,
                           self.Vlevel.value+1))
        if hasattr(self.Vgrid.value, 'filename'):
            self.infolabel.setToolTip(self.Vgrid.value.filename)

    ########################
    # Selectionion methods #
    ########################

    def NewGrid(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vgrid <artview.core.core.Variable>`.

        This will:

        * Update fields and levels lists and MenuBoxes
        * Check grid scan type and reset limits if needed
        * Reset units and title
        * If strong update: update plot
        '''
        # test for None
        if self.Vgrid.value is None:
            self.fieldBox.clear()
            self.levelBox.clear()
            return

        # Get field names
        self.fieldnames = self.Vgrid.value.fields.keys()

        # Check the file type and initialize limts
        self._check_file_type()

        # Update field and level MenuBox
        self._fillLevelBox()
        self._fillFieldBox()

        self.units = self._get_default_units()
        self.title = self._get_default_title()
        if strong:
            self._update_plot()
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

    def NewLimits(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vlimits <artview.core.core.Variable>`.

        This will:

        * If strong update: update axes
        '''
        if strong:
            self._update_axes()

    def NewColormap(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vcolormap <artview.core.core.Variable>`.

        This will:

        * If strong update: update plot
        '''
        if strong:
            self._update_plot()

    def NewLevel(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vlevel* <artview.core.core.Variable>`.

        This will:

        * Update level MenuBox
        * If strong update: update plot
        '''
        # +1 since the first one is "Level Window"
        self.levelBox.setCurrentIndex(self.Vlevel.value + 1)
        if strong:
            self._update_plot()
            self._update_infolabel()

    def LevelSelectCmd(self, nlevel):
        '''
        Captures Level selection and update Level
        :py:class:`~artview.core.core.Variable`.
        '''
        if nlevel < 0:
            nlevel = len(self.levels)-1
        elif nlevel >= len(self.levels):
            nlevel = 0
        self.Vlevel.change(nlevel)

    def FieldSelectCmd(self, name):
        '''
        Captures field selection and update field
        :py:class:`~artview.core.core.Variable`.
        '''
        self.Vfield.change(name)

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
        from .pick_value import ValueClick
        self.tools['valueclick'] = ValueClick(
            self, name=self.name + "ValueClick", parent=self)

    def toolSelectRegionCmd(self):
        '''Creates and connects to Region of Interest instance.'''
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
        self._set_default_limits()
        if self.Vcolormap.value['lock'] is False:
            self._set_default_cmap()

    def getPathInteriorValues(self, paths):
        '''
        Return the bins values path.

        Parameters
        ----------
        paths : list of :py:class:`matplotlib.path.Path` instances

        Returns
        -------
        points : :py:class`artview.core.points.Points`

            Points object containing all bins of the current grid
            and level inside path. Axes : 'x_disp', 'y_disp', 'x_disp',
            'x_index', 'y_index', 'z_index'. Fields: just current field

        Notes
        -----
            If Vgrid.value is None, returns None
        '''
        from .tools import interior_grid
        grid = self.Vgrid.value
        if grid is None:
            return None

        try:
            iter(paths)
        except:
            paths = [paths]

        xy = np.empty((0, 2))
        idx = np.empty((0, 2), dtype=np.int)

        for path in paths:
            _xy, _idx = interior_grid(path, grid, self.basemap,
                                      self.Vlevel.value, self.plot_type)
            xy = np.concatenate((xy, _xy))
            idx = np.concatenate((idx, _idx))

        if self.plot_type == "gridZ":
            x = xy[:, 0]
            y = xy[:, 1]
            z = np.ones_like(xy[:, 0]) * self.levels[self.VlevelZ.value]
            x_idx = idx[:, 0]
            y_idx = idx[:, 1]
            z_idx = np.ones_like(idx[:, 0]) * self.VlevelZ.value
        elif self.plot_type == "gridY":
            x = xy[:, 0] * 1000.
            z = xy[:, 1] * 1000.
            y = np.ones_like(xy[:, 0]) * self.levels[self.VlevelY.value]
            x_idx = idx[:, 0]
            z_idx = idx[:, 1]
            y_idx = np.ones_like(idx[:, 0]) * self.VlevelY.value
        elif self.plot_type == "gridX":
            z = xy[:, 0] * 1000.
            y = xy[:, 1] * 1000.
            x = np.ones_like(xy[:, 0]) * self.levels[self.VlevelX.value]
            z_idx = idx[:, 0]
            y_idx = idx[:, 1]
            x_idx = np.ones_like(idx[:, 0]) * self.VlevelX.value

        xaxis = {'data':  x,
                 'long_name': 'X-coordinate in Cartesian system',
                 'axis': 'X',
                 'units': 'm'}

        yaxis = {'data':  y,
                 'long_name': 'Y-coordinate in Cartesian system',
                 'axis': 'Y',
                 'units': 'm'}

        zaxis = {'data':  z,
                 'long_name': 'Z-coordinate in Cartesian system',
                 'axis': 'Z',
                 'units': 'm'}

        field = grid.fields[self.Vfield.value].copy()
        field['data'] = grid.fields[self.Vfield.value]['data'][
            z_idx, y_idx, x_idx]

        x_idx = {'data': x_idx,
                 'long_name': 'index in nx dimension'}
        y_idx = {'data': y_idx,
                 'long_name': 'index in ny dimension'}
        z_idx = {'data': z_idx,
                 'long_name': 'index in nz dimension'}

        axes = {'x_disp': xaxis,
                'y_disp': yaxis,
                'z_disp': zaxis,
                'x_index': x_idx,
                'y_index': y_idx,
                'z_index': z_idx, }

        fields = {self.Vfield.value: field}

        points = Points(fields, axes, grid.metadata.copy(), xy.shape[0])

        return points

    def getNearestPoints(self, xdata, ydata):
        '''
        Return the bins values nearest to point.

        Parameters
        ----------
        xdata, ydata : float

        Returns
        -------
        x, y, z, value, x_idx, y_idx, z_idx: ndarray
            Truplet of 1arrays containing x,y,z coordinate, current field
            value, x, y and z index.

        Notes
        -----
            If Vgrid.value is None, returns None
        '''
        from .tools import nearest_point_grid
        grid = self.Vgrid.value

        # map center
        lat0 = self.Vgrid.value.axes['lat']['data'][0]
        lon0 = self.Vgrid.value.axes['lon']['data'][0]

        if grid is None:
            return (np.array([]),)*7

        if self.plot_type == "gridZ":
            idx = nearest_point_grid(
                grid, self.basemap, self.levels[self.VlevelZ.value], ydata,
                xdata)
        elif self.plot_type == "gridY":
            idx = nearest_point_grid(
                grid, self.basemap, ydata * 1000.,
                self.levels[self.VlevelY.value], xdata * 1000.)
        elif self.plot_type == "gridX":
            idx = nearest_point_grid(
                grid, self.basemap, ydata * 1000., xdata * 1000.,
                self.levels[self.VlevelX.value])
        aux = (grid.axes['x_disp']['data'][idx[:, 2]],
               grid.axes['y_disp']['data'][idx[:, 1]],
               grid.axes['z_disp']['data'][idx[:, 0]],
               grid.fields[self.Vfield.value]['data'][idx[:, 0], idx[:, 1],
                                                      idx[:, 2]],
               idx[:, 2], idx[:, 1], idx[:, 0])
        return aux

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
        if self.plot_type in ("gridX", "gridY"):
            self.YSIZE = 5
        else:
            self.YSIZE = 8
        xwidth = 0.7
        yheight = 0.7
        self.ax.set_position([0.15, 0.15, xwidth, yheight])
        self.cax.set_position([0.15+xwidth, 0.15, 0.02, yheight])
        self._update_axes()

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area.'''
        self.canvas = FigureCanvasQTAgg(self.fig)
        # Add the widget to the canvas
        self.layout.addWidget(self.canvas, 1, 0, 7, 6)

    def _update_plot(self):
        '''Draw/Redraw the plot.'''

        if self.Vgrid.value is None:
            return

        # Create the plot with PyArt GridMapDisplay
        self.ax.cla()  # Clear the plot axes
        self.cax.cla()  # Clear the colorbar axes

        if self.Vfield.value not in self.Vgrid.value.fields.keys():
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

        self.display = pyart.graph.GridMapDisplay(self.Vgrid.value)
        # Create Plot
        if self.plot_type == "gridZ":
            self.display.plot_basemap(
                self.lat_lines, self.lon_lines, ax=self.ax)
            self.basemap = self.display.get_basemap()
            self.plot = self.display.plot_grid(
                self.Vfield.value, self.VlevelZ.value, vmin=cmap['vmin'],
                vmax=cmap['vmax'], cmap=cmap['cmap'], colorbar_flag=False,
                title=title, ax=self.ax, fig=self.fig)
        elif self.plot_type == "gridY":
            self.basemap = None
            self.plot = self.display.plot_latitudinal_level(
                self.Vfield.value, self.VlevelY.value, vmin=cmap['vmin'],
                vmax=cmap['vmax'], cmap=cmap['cmap'], colorbar_flag=False,
                title=title, ax=self.ax, fig=self.fig)
        elif self.plot_type == "gridX":
            self.basemap = None
            self.plot = self.display.plot_longitudinal_level(
                self.Vfield.value, self.VlevelX.value, vmin=cmap['vmin'],
                vmax=cmap['vmax'], cmap=cmap['cmap'], colorbar_flag=False,
                title=title, ax=self.ax, fig=self.fig)

        limits = self.Vlimits.value
        x = self.ax.get_xlim()
        y = self.ax.get_ylim()
        limits['xmin'] = x[0]
        limits['xmax'] = x[1]
        limits['ymin'] = y[0]
        limits['ymax'] = y[1]

        self._update_axes()
        norm = mlabNormalize(vmin=cmap['vmin'],
                             vmax=cmap['vmax'])
        self.cbar = mlabColorbarBase(self.cax, cmap=cmap['cmap'],
                                     norm=norm, orientation='vertical')
        self.cbar.set_label(self.units)

        if self.plot_type == "gridZ":
            print("Plotting %s field, Z level %d in %s" % (
                self.Vfield.value, self.VlevelZ.value+1, self.name))
        elif self.plot_type == "gridY":
            print("Plotting %s field, Y level %d in %s" % (
                self.Vfield.value, self.VlevelY.value+1, self.name))
        elif self.plot_type == "gridX":
            print("Plotting %s field, X level %d in %s" % (
                self.Vfield.value, self.VlevelX.value+1, self.name))

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

    def _set_default_limits(self, strong=True):
        '''Set limits to pre-defined default.'''
        limits = self.Vlimits.value
        if limits is None:
            limits = {}
        if self.Vgrid.value is None:
            limits['xmin'] = 0
            limits['xmax'] = 1
            limits['ymin'] = 0
            limits['ymax'] = 1
        elif self.plot_type == "gridZ":
            if self.basemap is not None:
                limits['xmin'] = self.basemap.llcrnrx
                limits['xmax'] = self.basemap.urcrnrx
                limits['ymin'] = self.basemap.llcrnry
                limits['ymax'] = self.basemap.urcrnry
            else:
                limits['xmin'] = -150
                limits['xmax'] = 150
                limits['ymin'] = -150
                limits['ymax'] = 150
        elif self.plot_type == "gridY":
            limits['xmin'] = (self.Vgrid.value.axes['x_disp']['data'][0] /
                              1000.)
            limits['xmax'] = (self.Vgrid.value.axes['x_disp']['data'][-1] /
                              1000.)
            limits['ymin'] = (self.Vgrid.value.axes['z_disp']['data'][0] /
                              1000.)
            limits['ymax'] = (self.Vgrid.value.axes['z_disp']['data'][-1] /
                              1000.)
        elif self.plot_type == "gridX":
            limits['xmin'] = (self.Vgrid.value.axes['y_disp']['data'][0] /
                              1000.)
            limits['xmax'] = (self.Vgrid.value.axes['y_disp']['data'][-1] /
                              1000.)
            limits['ymin'] = (self.Vgrid.value.axes['z_disp']['data'][0] /
                              1000.)
            limits['ymax'] = (self.Vgrid.value.axes['z_disp']['data'][-1] /
                              1000.)
        self.Vlimits.change(limits, strong)

    def _set_default_cmap(self, strong=True):
        '''Set colormap to pre-defined default.'''
        cmap = pyart.config.get_field_colormap(self.Vfield.value)
        d = {}
        d['cmap'] = cmap
        d['lock'] = False
        lims = pyart.config.get_field_limits(self.Vfield.value,
                                             self.Vgrid.value)
        if lims != (None, None):
            d['vmin'] = lims[0]
            d['vmax'] = lims[1]
        else:
            d['vmin'] = -10
            d['vmax'] = 65
        self.Vcolormap.change(d, strong)

    def _get_default_title(self):
        '''Get default title from pyart.'''
        if (self.Vgrid.value is None or
            self.Vfield.value not in self.Vgrid.value.fields):
            return ''
        if self.plot_type == "gridZ":
            return pyart.graph.common.generate_grid_title(self.Vgrid.value,
                                                          self.Vfield.value,
                                                          self.Vlevel.value)
        elif self.plot_type == "gridY":
            return pyart.graph.common.generate_latitudinal_level_title(
                self.Vgrid.value, self.Vfield.value, self.Vlevel.value)
        elif self.plot_type == "gridX":
            return pyart.graph.common.generate_longitudinal_level_title(
                self.Vgrid.value, self.Vfield.value, self.Vlevel.value)

    def _get_default_units(self):
        '''Get default units for current grid and field.'''
        if self.Vgrid.value is not None:
            try:
                return self.Vgrid.value.fields[self.Vfield.value]['units']
            except:
                return ''
        else:
            return ''

    def _check_file_type(self):
        '''Check file to see if the file type.'''
        # self._update_fig_ax()
        return

    def change_plot_type(self, plot_type):
        '''Change plot type.'''
        # remove shared variables
        for key in ("VlevelZ", "VlevelY", "VlevelX"):
            if key in self.sharedVariables.keys():
                del self.sharedVariables[key]
        if plot_type == "gridZ":
            self.sharedVariables["VlevelZ"] = self.NewLevel
        elif plot_type == "gridY":
            self.sharedVariables["VlevelY"] = self.NewLevel
        elif plot_type == "gridX":
            self.sharedVariables["VlevelX"] = self.NewLevel
        else:
            import warnings
            warnings.warn('Invalid Plot type %s, reseting to gridZ' %
                          plot_type)
            self.sharedVariables["VlevelZ"] = self.NewLevel
            plot_type = "gridZ"
        self.plot_type = plot_type

    ########################
    # Image save methods #
    ########################

    def _quick_savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display via PyArt interface.'''
        imagename = self.display.generate_filename(
            self.Vfield.value, self.Vlevel.value, ext=IMAGE_EXT)
        self.canvas.print_figure(os.path.join(os.getcwd(), imagename),
                                 dpi=DPI)
        self.statusbar.showMessage('Saved to %s' % os.path.join(os.getcwd(),
                                                                imagename))

    def _savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display using PyQt dialog interface.'''
        imagename = self.display.generate_filename(
            self.Vfield.value, self.Vlevel.value, ext=IMAGE_EXT)
        file_choices = "PNG (*.png)|*.png"
        path = unicode(QtGui.QFileDialog.getSaveFileName(
            self, 'Save file', imagename, file_choices))
        if path:
            self.canvas.print_figure(path, dpi=DPI)
            self.statusbar.showMessage('Saved to %s' % path)

    ########################
    #      get methods     #
    ########################

    def getPlotAxis(self):
        ''' get :py:class:`matplotlib.axes.Axes` instance of main plot '''
        return self.ax

    def getStatusBar(self):
        ''' get :py:class:`PyQt4.QtGui.QStatusBar` instance'''
        return self.statusbar

    def getField(self):
        ''' get current field '''
        return self.Vfield.value

    def getUnits(self):
        ''' get current units '''
        return self.units

    ########################
    #      Properties      #
    ########################

    @property
    def Vlevel(self):
        '''Alias to VlevelZ, VlevelY or VlevelX depending on plot_type.'''
        if self.plot_type == "gridZ":
            return self.VlevelZ
        elif self.plot_type == "gridY":
            return self.VlevelY
        elif self.plot_type == "gridX":
            return self.VlevelX
        else:
            return None

    @property
    def levels(self):
        '''Values from the axes of grid, depending on plot_type.'''
        if self.plot_type == "gridZ":
            return self.Vgrid.value.axes['z_disp']['data'][:]
        elif self.plot_type == "gridY":
            return self.Vgrid.value.axes['y_disp']['data'][:]
        elif self.plot_type == "gridX":
            return self.Vgrid.value.axes['x_disp']['data'][:]
        else:
            return None


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

    def chooseGrid(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vgrid"] = getattr(item[1], item[2])

    def chooseField(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vfield"] = getattr(item[1], item[2])

    def chooseLevel(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["VlevelZ"] = getattr(item[1], item[2])

    def chooseLims(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vlimits"] = getattr(item[1], item[2])

    def setupUi(self):

        self.gridButton = QtGui.QPushButton("Find Variable")
        self.gridButton.clicked.connect(self.chooseGrid)
        self.layout.addWidget(QtGui.QLabel("Vgrid"), 0, 0)
        self.layout.addWidget(self.gridButton, 0, 1, 1, 3)

        self.plot_type = QtGui.QLineEdit("gridZ")
        self.layout.addWidget(QtGui.QLabel("plot_type"), 1, 0)
        self.layout.addWidget(self.plot_type, 1, 1, 1, 3)

        self.fieldButton = QtGui.QPushButton("Find Variable")
        self.fieldButton.clicked.connect(self.chooseField)
        self.layout.addWidget(QtGui.QLabel("Vfield"), 2, 0)
        self.field = QtGui.QLineEdit("")
        self.layout.addWidget(self.field, 2, 1)
        self.layout.addWidget(QtGui.QLabel("or"), 2, 2)
        self.layout.addWidget(self.fieldButton, 2, 3)

        self.levelButton = QtGui.QPushButton("Find Variable")
        self.levelButton.clicked.connect(self.chooseLevel)
        self.layout.addWidget(QtGui.QLabel("Vlevel"), 3, 0)
        self.level = QtGui.QSpinBox()
        self.layout.addWidget(self.level, 3, 1)
        self.layout.addWidget(QtGui.QLabel("or"), 3, 2)
        self.layout.addWidget(self.levelButton, 3, 3)

        self.limsButton = QtGui.QPushButton("Find Variable")
        self.limsButton.clicked.connect(self.chooseLims)
        self.layout.addWidget(QtGui.QLabel("Vlimits"), 4, 0)
        self.layout.addWidget(self.limsButton, 4, 1, 1, 3)

        self.name = QtGui.QLineEdit("GridDisplay")
        self.layout.addWidget(QtGui.QLabel("name"), 5, 0)
        self.layout.addWidget(self.name, 5, 1, 1, 3)

        self.closeButton = QtGui.QPushButton("Start")
        self.closeButton.clicked.connect(self.closeDialog)
        self.layout.addWidget(self.closeButton, 6, 0, 1, 5)

    def closeDialog(self):
        self.done(QtGui.QDialog.Accepted)

    def startDisplay(self):
        self.exec_()

        # if no Vgrid abort
        if 'Vgrid' not in self.result:
            self.result['Vgrid'] = Variable(None)
            # common.ShowWarning("Must select a variable for Vgrid.")
            # I'm allowing this to continue, but this will result in error

        # if Vfield, Vlevel, Vlimits were not select create new
        field = str(self.field.text())
        level = self.level.value()
        if 'Vfield' not in self.result:
            self.result['Vfield'] = Variable(field)
        if 'VlevelZ' not in self.result:
            self.result['VlevelZ'] = Variable(level)

        self.result['name'] = str(self.name.text())
        self.result['plot_type'] = str(self.plot_type.text())

        return self.result
