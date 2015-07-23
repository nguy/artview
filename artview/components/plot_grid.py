"""
plot_grid.py

Class instance used to make Display.
"""
# Load the needed packages
import numpy as np
import pyart

from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as \
    NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import Normalize as mlabNormalize
from matplotlib.colorbar import ColorbarBase as mlabColorbarBase
from matplotlib.pyplot import cm

from ..core import Variable, Component, common, VariableChoose

# Save image file type and DPI (resolution)
IMAGE_EXT = 'png'
DPI = 100
# ========================================================================


class Display(Component):
    '''
    Class that creates a display plot, using a returned grid structure
    from the PyArt pyart.graph package.
    '''

    Vgrid = None #: see :ref:`shared_variable`
    Vfield = None #: see :ref:`shared_variable`
    Vtilt = None #: see :ref:`shared_variable`
    Vlims = None #: see :ref:`shared_variable`
    Vcmap = None #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Grafical Interface for Starting this Class'''
        args = _DisplayStart().startDisplay()
        return self(**args), True

    def __init__(self, Vgrid, Vfield, Vtilt, Vlims=None, Vcmap=None,
                 name="Display", parent=None):
        '''
        Initialize the class to create display.

        Parameters
        ----------
        Vgrid : :py:class:`~artview.core.core.Variable` instance
            grid signal variable.
        Vfield : :py:class:`~artview.core.core.Variable` instance
            Field signal variable.
        Vtilt : :py:class:`~artview.core.core.Variable` instance
            Tilt signal variable.
        [Optional]
        Vlims : :py:class:`~artview.core.core.Variable` instance
            Limits signal variable.
            A value of None will instantiate a limits variable.
        Vcmap : :py:class:`~artview.core.core.Variable` instance
            Colormap signal variable.
            A value of None will instantiate a colormap variable.
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
        super(Display, self).__init__(name=name, parent=parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        # Set up signal, so that DISPLAY can react to
        # external (or internal) changes in grid, field,
        # lims and tilt (expected to be Core.Variable instances)
        # The capital V so people remember using ".value"
        self.Vgrid = Vgrid
        self.Vfield = Vfield
        self.Vtilt = Vtilt
        if Vlims is None:
            self.Vlims = Variable(None)
        else:
            self.Vlims = Vlims

        if Vcmap is None:
            self.Vcmap = Variable(None)
        else:
            self.Vcmap = Vcmap

        self.sharedVariables = {"Vgrid": self.Newgrid,
                                "Vfield": self.NewField,
                                "Vtilt": self.NewTilt,
                                "Vlims": self.NewLims,
                                "Vcmap": self.NewCmap,}

        # Connect the components
        self.connectAllVariables()

        self.scan_type = "gridZ"

        # Set plot title and colorbar units to defaults
        # TODO convert title to grid
        #self.title = None
        self.units = None

        # set default latlon lines
        self.lat_lines = np.linspace(-90, 90, num=181)
        self.lon_lines = np.linspace(-180, 180, num=361)

        # Find the PyArt colormap names
#        self.cm_names = [m for m in cm.datad if not m.endswith("_r")]
        self.cm_names = ["pyart_" + m for m in pyart.graph.cm.datad
                         if not m.endswith("_r")]
        self.cm_names.sort()

        # Create tool dictionary
        self.tools = {}

        # Set up Default limits and cmap
        if Vlims is None:
            self._set_default_limits(strong=False)
        if Vcmap is None:
            self._set_default_cmap(strong=False)

        # Create a figure for output
        self._set_fig_ax()

        # Launch the GUI interface
        self.LaunchGUI()

        # Initialize grid variable
        self.Newgrid(None, None, True)

        self.show()

    def keyPressEvent(self, event):
        '''Reimplementation, allow tilt adjustment via the Up-Down arrow keys.'''
        if event.key() == QtCore.Qt.Key_Up:
            self.TiltSelectCmd(self.Vtilt.value + 1)
        elif event.key() == QtCore.Qt.Key_Down:
            self.TiltSelectCmd(self.Vtilt.value - 1)
        else:
            super(Display, self).keyPressEvent(event)

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

    def setUILayout(self):
        '''Setup the button/display UI layout.'''
        self.layout.addWidget(self.tiltBox, 0, 0)
        self.layout.addWidget(self.fieldBox, 0, 1)
        self.layout.addWidget(self.dispButton, 0, 2)
        self.layout.addWidget(self.toolsButton, 0, 3)

    #############################
    # Functionality methods #
    #############################

    def _open_LimsDialog(self):
        '''Open a dialog box to change display limits.'''
        from .limits import limits_dialog
        limits, cmap, change = limits_dialog(self.Vlims.value, self.Vcmap.value, self.name)
        if change == 1:
            self.Vcmap.change(cmap)
            self.Vlims.change(limits)

    def _fillTiltBox(self):
        '''Fill in the Tilt Window Box with current elevation angles.'''
        self.tiltBox.clear()
        self.tiltBox.addItem("Tilt Window")
        # Loop through and create each tilt button
        elevs = self.Vgrid.value.axes['z_disp']['data']
        for ntilt in self.rTilts:
            btntxt = "%2.1f m (Tilt %d)"%(elevs[ntilt], ntilt+1)
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

    def _title_input(self):
        '''Retrieve new plot title.'''
        val, entry = common.string_dialog(self.title, "Plot Title", "Title:")
        if entry is True:
            self.title = val
            self._update_plot()

    def _units_input(self):
        '''Retrieve new plot units.'''
        val, entry = common.string_dialog(self.units, "Plot Units", "Units:")
        if entry is True:
            self.units = val
            self._update_plot()

    def _open_tiltbuttonwindow(self):
        '''Open a TiltButtonWindow instance.'''
        from .tilt import TiltButtonWindow
        self.tiltbuttonwindow = TiltButtonWindow(
            self.Vtilt, self.Vgrid,
            name=self.name+" Tilt Selection", parent=self.parent)

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
        # TODO convert me to grid
        #dispTitle = dispmenu.addAction("Change Title")
        #dispTitle.setToolTip("Change plot title")
        dispUnit = dispmenu.addAction("Change Units")
        dispUnit.setToolTip("Change units string")
        self.dispCmap = dispmenu.addAction("Change Colormap")
        self.dispCmapmenu = QtGui.QMenu("Change Cmap")
        self.dispCmapmenu.setFocusPolicy(QtCore.Qt.NoFocus)
        #dispQuickSave = dispmenu.addAction("Quick Save Image")
        #dispQuickSave.setShortcut("Ctrl+D")
        #dispQuickSave.setStatusTip(
        #    "Save Image to local directory with default name")
        #dispSaveFile = dispmenu.addAction("Save Image")
        #dispSaveFile.setShortcut("Ctrl+S")
        #dispSaveFile.setStatusTip("Save Image using dialog")

        dispLimits.triggered[()].connect(self._open_LimsDialog)
        #dispTitle.triggered[()].connect(self._title_input)
        dispUnit.triggered[()].connect(self._units_input)
        #dispQuickSave.triggered[()].connect(self._quick_savefile)
        #dispSaveFile.triggered[()].connect(self._savefile)

        self._add_cmaps_to_button()
        self.dispButton.setMenu(dispmenu)

    def _add_tiltBoxUI(self):
        '''Create the Tilt Selection ComboBox.'''
        self.tiltBox = QtGui.QComboBox()
        self.tiltBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tiltBox.setToolTip("Choose tilt elevation angle")
        self.tiltBox.activated[str].connect(self._tiltAction)

    def _add_fieldBoxUI(self):
        '''Create the Field Selection ComboBox.'''
        self.fieldBox = QtGui.QComboBox()
        self.fieldBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fieldBox.setToolTip("Choose variable/field")
        self.fieldBox.activated[str].connect(self._fieldAction)

    def _add_toolsBoxUI(self):
        '''Create the Tools Button menu.'''
        self.toolsButton = QtGui.QPushButton("Toolbox")
        self.toolsButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.toolsButton.setToolTip("Choose a tool to apply")
        toolmenu = QtGui.QMenu(self)
        toolZoomPan = toolmenu.addAction("Zoom/Pan")
        #toolValueClick = toolmenu.addAction("Click for Value")
        #toolROI = toolmenu.addAction("Select a Region of Interest")
        toolCustom = toolmenu.addAction("Use Custom Tool")
        toolDefault = toolmenu.addAction("Reset File Defaults")
        toolZoomPan.triggered[()].connect(self.toolZoomPanCmd)
        #toolValueClick.triggered[()].connect(self.toolValueClickCmd)
        #toolROI.triggered[()].connect(self.toolROICmd)
        toolCustom.triggered[()].connect(self.toolCustomCmd)
        toolDefault.triggered[()].connect(self.toolDefaultCmd)
        self.toolsButton.setMenu(toolmenu)

    ########################
    # Selectionion methods #
    ########################

    def Newgrid(self, variable, value, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vgrid <artview.core.core.Variable>`.

        This will:

        * Update fields and tilts lists and MenuBoxes
        * Check grid scan type and reset limits if needed
        * Reset units and title
        * If strong update: update plot
        '''
        # test for None
        if self.Vgrid.value is None:
            self.fieldBox.clear()
            self.tiltBox.clear()
            return

        # Get the tilt angles
        self.rTilts = range(len(self.Vgrid.value.axes['z_disp']['data']))
        # Get field names
        self.fieldnames = self.Vgrid.value.fields.keys()

        # Check the file type and initialize limts
        self._check_file_type()

        # Update field and tilt MenuBox
        self._fillTiltBox()
        self._fillFieldBox()

        self.units = None
        self.title = None
        if strong:
            self._update_plot()

    def NewField(self, variable, value, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vfield <artview.core.core.Variable>`.

        This will:

        * Reset colormap
        * Reset units
        * Update fields MenuBox
        * If strong update: update plot
        '''
        self._set_default_cmap(strong=False)
        self.units = None
        idx = self.fieldBox.findText(value)
        self.fieldBox.setCurrentIndex(idx)
        if strong and self.Vgrid.value is not None:
            self._update_plot()

    def NewLims(self, variable, value, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vlims <artview.core.core.Variable>`.

        This will:

        * If strong update: update axes
        '''
        if strong:
            self._update_axes()

    def NewCmap(self, variable, value, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vcmap <artview.core.core.Variable>`.

        This will:

        * If strong update: update plot
        '''
        if strong and self.Vgrid.value is not None:
            self._update_plot()


    def NewTilt(self, variable, value, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vtilt <artview.core.core.Variable>`.

        This will:

        * Update tilt MenuBox
        * If strong update: update plot
        '''
        # +1 since the first one is "Tilt Window"
        self.tiltBox.setCurrentIndex(value+1)
        if strong and self.Vgrid.value is not None:
            self._update_plot()

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

    def cmapSelectCmd(self, cm_name):
        '''Captures colormap selection and redraws.'''
        CMAP = cm_name
        self.Vcmap.value['cmap'] = cm_name
        self.Vcmap.change(self.Vcmap.value)

    def toolZoomPanCmd(self):
        '''Creates and connects to a Zoom/Pan instance.'''
        from .tools import ZoomPan
        scale = 1.1
        self.tools['zoompan'] = ZoomPan(
            self.Vlims, self.ax,
            base_scale=scale, parent=self.parent)
        self.tools['zoompan'].connect()

    def toolValueClickCmd(self):
        '''Creates and connects to Point-and-click value retrieval'''
        # TODO convert me to grid
        from .tools import ValueClick
        self.tools['valueclick'] = ValueClick(
            self.Vgrid, self.Vtilt, self.Vfield,
            self.units, self.ax, self.statusbar, parent=self.parent)
        self.tools['valueclick'].connect()

    def toolROICmd(self):
        '''Creates and connects to Region of Interest instance'''
        from .roi import ROI
        self.tools['roi'] = ROI(self, name=self.name + " ROI", parent=self)

    def toolCustomCmd(self):
        '''Allow user to activate self-defined tool.'''
        from . import tools
        tools.custom_tool(self.tools)

    def toolDefaultCmd(self):
        '''Restore the Display defaults.'''
        from . import tools
        self.tools, limits, cmap = tools.restore_default_display(
            self.tools, self.Vfield.value, self.scan_type)
        self.Vcmap.change(cmap)
        self.Vlims.change(limits)

    def getPathInteriorValues(self, path):
        '''
        Return the bins values path.

        Parameters
        ----------
        path : Matplotlib Path instance

        Returns
        -------
        x, y, azi, range, value, ray_idx, range_inx: ndarray
            Truplet of 1arrays containing x,y coordinate, azimuth,
            range, current field value, ray index and range index
            for all bin of the current grid and tilt inside path.

        Notes
        -----
            If Vgrid.value is None, returns None
        '''
        # TODO convert me to grid
        from .tools import interior
        grid = self.Vgrid.value
        if grid is None:
            return (np.array([]),)*7

        xy, idx = interior(path, grid, self.Vtilt.value)
        aux = (xy[:, 0], xy[:, 1], grid.azimuth['data'][idx[:, 0]],
               grid.range['data'][idx[:, 1]] / 1000.,
               grid.fields[self.Vfield.value]['data'][idx[:, 0], idx[:, 1]],
               idx[:, 0], idx[:, 1])
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
        #self._update_axes()

    def _update_fig_ax(self):
        '''Set the figure and axis to plot.'''
        if self.scan_type in ("airborne", "rhi"):
            self.YSIZE = 5
        else:
            self.YSIZE = 8
        xwidth = 0.7
        yheight = 0.7 * float(self.YSIZE) / float(self.XSIZE)
        self.ax.set_position([0.2, 0.55-0.5*yheight, xwidth, yheight])
        self.cax.set_position([0.2, 0.10, xwidth, 0.02])
        self._update_axes()

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area.'''
        self.canvas = FigureCanvasQTAgg(self.fig)
        # Add the widget to the canvas
        self.layout.addWidget(self.canvas, 1, 0, 7, 6)

    def _update_plot(self):
        '''Draw/Redraw the plot.'''
        self._check_default_field()

        if self.Vfield.value not in self.Vgrid.value.fields.keys():
            return

        # Create the plot with PyArt GridMapDisplay
        self.ax.cla()  # Clear the plot axes
        self.cax.cla()  # Clear the colorbar axes

        # Reset to default title if user entered nothing w/ Title button
        # TODO convert title to grid
        #if self.title == '':
        #    title = None
        #else:
        #    title = self.title

        limits = self.Vlims.value
        cmap = self.Vcmap.value

        self.display = pyart.graph.GridMapDisplay(self.Vgrid.value)
        # Create Plot
        self.display.plot_basemap(self.lat_lines, self.lon_lines, ax=self.ax)
        self.plot = self.display.plot_grid(
                self.Vfield.value, self.Vtilt.value, vmin=cmap['vmin'],
                vmax=cmap['vmax'],cmap=cmap['cmap'])

        limits = self.Vlims.value
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
                                     norm=norm, orientation='horizontal')
        # colorbar - use specified units or default depending on
        # what has or has not been entered
        if self.units is None or self.units == '':
            try:
                self.units = self.Vgrid.value.fields[self.field]['units']
            except:
                self.units = ''
        self.cbar.set_label(self.units)

        print "Plotting %s field, Tilt %d in %s" % (
            self.Vfield.value, self.Vtilt.value+1, self.name)
        self.canvas.draw()

    def _update_axes(self):
        '''Change the Plot Axes.'''
        limits = self.Vlims.value
        self.ax.set_xlim(limits['xmin'], limits['xmax'])
        self.ax.set_ylim(limits['ymin'], limits['ymax'])
        self.ax.figure.canvas.draw()

    #########################
    # Check methods #
    #########################

    def _check_default_field(self):
        '''
        Hack to perform a check on reflectivity to make it work with
        a larger number of files as there are many nomenclature is the
        weather radar world.

        This should only occur upon start up with a new file.
        '''
        if self.Vfield.value == pyart.config.get_field_name('reflectivity'):
            if self.Vfield.value in self.fieldnames:
                pass
            elif 'CZ' in self.fieldnames:
                self.Vfield.change('CZ', False)
            elif 'DZ' in self.fieldnames:
                self.Vfield.change('DZ', False)
            elif 'dbz' in self.fieldnames:
                self.Vfield.change('dbz', False)
            elif 'DBZ' in self.fieldnames:
                self.Vfield.change('DBZ', False)
            elif 'dBZ' in self.fieldnames:
                self.Vfield.change('dBZ', False)
            elif 'Z' in self.fieldnames:
                self.Vfield.change('Z', False)
            elif 'DBZ_S' in self.fieldnames:
                self.Vfield.change('DBZ_S', False)
            elif 'reflectivity_horizontal'in self.fieldnames:
                self.Vfield.change('reflectivity_horizontal', False)
            elif 'DBZH' in self.fieldnames:
                self.Vfield.change('DBZH', False)
            else:
                msg = "Could not find the field name.\n\
                      You can add an additional name by modifying the\n\
                      'check_default_field' function in plot.py\n\
                      Please send a note to ARTView folks to add this name\n\
                      Thanks!"
                common.ShowWarning(msg)

    def _set_default_limits(self, strong=True):
        ''' Set limits to pre-defined default.'''
        from .limits import _default_limits
        limits, cmap = _default_limits(
            self.Vfield.value, self.scan_type)
        self.Vlims.change(limits, strong)

    def _set_default_cmap(self, strong=True):
        ''' Set colormap to pre-defined default.'''
        from .limits import _default_limits
        limits, cmap = _default_limits(
            self.Vfield.value, self.scan_type)
        self.Vcmap.change(cmap, strong)

    def _check_file_type(self):
        '''Check file to see if the file type'''
        return

    ########################
    # Image save methods #
    ########################
    def _quick_savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display via PyArt interface.'''
        # TODO convert me to grid
        PNAME = self.display.generate_filename(
            self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        print "Creating " + PNAME

    def _savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display using PyQt dialog interface.'''
        # TODO convert me to grid
        PBNAME = self.display.generate_filename(
            self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        file_choices = "PNG (*.png)|*.png"
        path = unicode(QtGui.QFileDialog.getSaveFileName(
            self, 'Save file', '', file_choices))
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


class _DisplayStart(QtGui.QDialog):
    '''
    Dialog Class for graphical Start of Display, to be used in guiStart
    '''

    def __init__(self):
        '''Initialize the class to create the interface'''
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
            self.result["Vlims"] = getattr(item[1], item[2])

    def setupUi(self):

        self.gridButton = QtGui.QPushButton("Find Variable")
        self.gridButton.clicked.connect(self.chooseGrid)
        self.layout.addWidget(QtGui.QLabel("Vgrid"), 0, 0)
        self.layout.addWidget(self.gridButton, 0, 1, 1, 3)

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
        self.layout.addWidget(QtGui.QLabel("Vlims"), 3, 0)
        self.layout.addWidget(self.limsButton, 3, 1, 1, 3)

        self.name = QtGui.QLineEdit("Display")
        self.layout.addWidget(QtGui.QLabel("name"), 4, 0)
        self.layout.addWidget(self.name, 4, 1, 1, 3)

        self.closeButton = QtGui.QPushButton("Start")
        self.closeButton.clicked.connect(self.closeDialog)
        self.layout.addWidget(self.closeButton, 5, 0, 1, 5)

    def closeDialog(self):
        self.done(QtGui.QDialog.Accepted)

    def startDisplay(self):
        self.exec_()

        # if no Vgrid abort
        if 'Vgrid' not in self.result:
            common.ShowWarning("Must select a variable for Vgrid")
            # I'm allowing this to continue, but this will result in error

        # if Vfield, Vtilt, Vlims were not select create new
        field = str(self.field.text())
        tilt = self.tilt.value()
        if 'Vfield' not in self.result:
            self.result['Vfield'] = Variable(field)
        if 'Vtilt' not in self.result:
            self.result['Vtilt'] = Variable(tilt)

        self.result['name'] = str(self.name.text())

        return self.result
