"""
plot_radar.py

Class instance used to make Display.
"""
# Load the needed packages
import numpy as np
import pyart

from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import Normalize as mlabNormalize
from matplotlib.colorbar import ColorbarBase as mlabColorbarBase
from matplotlib.pyplot import cm



from ..core import Variable, Component, common, VariableChoose

# Save image file type and DPI (resolution)
IMAGE_EXT = 'png'
DPI = 100
#========================================================================

class Display(Component):
    '''
    Class that creates a display plot, using a returned Radar structure 
    from the PyArt pyart.graph package.
    '''

    Vradar = None #: see :ref:`shared_variable`
    Vfield = None #: see :ref:`shared_variable`
    Vtilt = None #: see :ref:`shared_variable`
    Vlims = None #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Grafical Interface for Starting this Class'''
        args = _DisplayStart().startDisplay()
        return self(**args), True

    def __init__(self, Vradar, Vfield, Vtilt, Vlims=None, \
                 name="Display", parent=None):
        '''
        Initialize the class to create display.

        Parameters
        ----------
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable.
        Vfield : :py:class:`~artview.core.core.Variable` instance
            Field signal variable.
        Vtilt : :py:class:`~artview.core.core.Variable` instance
            Tilt signal variable.
        [Optional]
        Vlims : :py:class:`~artview.core.core.Variable` instance
            Limits signal variable.
            A value of None will instantiate a limits variable.
        name : string
            Display window name.
        parent : PyQt instance
            Parent instance to associate to Display window.
            If None, then Qt owns, otherwise associated with parent PyQt instance.

        Notes
        -----
        This class records the selected button and passes the 
        change value back to variable.
        '''
        super(Display, self).__init__(name=name, parent=parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        # Set up signal, so that DISPLAY can react to external (or internal) changes 
        # in radar, field, lims and tilt (expected to be Core.Variable instances)
        # The capital V so people remember using ".value"
        self.Vradar = Vradar
        self.Vfield = Vfield
        self.Vtilt = Vtilt
        if Vlims is None:
            self.Vlims = Variable(None)
        else:
            self.Vlims = Vlims

        self.sharedVariables = {"Vradar": self.NewRadar,
                                "Vfield": self.NewField,
                                "Vtilt": self.NewTilt,
                                "Vlims": self.NewLims}

        # Connect the components
        self.connectAllVariables()

        self.scan_type = None

        # Set plot title and colorbar units to defaults
        self.title = None
        self.units = None

        # Set the default range rings
        self.RngRingList = ["None", "10 km", "20 km", "30 km", "50 km", "100 km"]
        self.RngRing = False

        # Find the PyArt colormap names
        self.cm_names = [m for m in cm.datad if not m.endswith("_r")]
        self.cm_names.sort()

        # Create tool dictionary
        self.tools = {}
        
        # Set up Default limits
        self._set_default_limits()

        # Create a figure for output
        self._set_fig_ax()

        # Launch the GUI interface
        self.LaunchGUI()

        # Initialize radar variable
        self.NewRadar(None, None, True)

        # Update Vlims variable if empty
        if self.Vlims.value is None:
            self.Vlims.change(self.limits, strong=False)

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
        #Create the Field controls
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
        self.limits, change = limits_dialog(self.limits, self.name)     
        if change == 1:
            self._update_plot()

    def _fillTiltBox(self):
        '''Fill in the Tilt Window Box with current elevation angles.'''
        self.tiltBox.clear()
        self.tiltBox.addItem("Tilt Window")
        # Loop through and create each tilt button
        elevs = self.Vradar.value.fixed_angle['data'][:]
        for ntilt in self.rTilts:
            btntxt = "%2.1f deg (Tilt %d)"%(elevs[ntilt], ntilt+1)
            self.tiltBox.addItem(btntxt)

    def _fillFieldBox(self):
        '''Fill in the Field Window Box with current variable names.'''
        self.fieldBox.clear()
        self.fieldBox.addItem("Field Window")
        # Loop through and create each field button
        for field in self.fieldnames:
            self.fieldBox.addItem(field)

    def _lims_input(self, entry):
        '''Retrieve new limits input.'''
        if entry['dmin'] is not None:
            self.limits['vmin'] = entry['dmin']
        if entry['dmax'] is not None:
            self.limits['vmax'] = entry['dmax']
        if entry['xmin'] is not None:
            self.limits['xmin'] = entry['xmin']
        if entry['xmax'] is not None:
            self.limits['xmax'] = entry['xmax']
        if entry['ymin'] is not None:
            self.limits['ymin'] = entry['ymin']
        if entry['ymax'] is not None:
            self.limits['ymax'] = entry['ymax']
        self._update_plot()

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
        self.tiltbuttonwindow = TiltButtonWindow(self.Vtilt, self.Vradar, \
                            name=self.name+" Tilt Selection", parent=self.parent)

    def _open_fieldbuttonwindow(self):
        '''Open a FieldButtonWindow instance.'''
        from .field import FieldButtonWindow
        self.fieldbuttonwindow = FieldButtonWindow(self.Vradar, self.Vfield, \
                            name=self.name+" Field Selection", parent=self.parent)

    def _add_RngRing_to_button(self):
        '''Add a menu to display range rings on plot.'''
        for RngRing in self.RngRingList:
            RingAction = self.dispRngRingmenu.addAction(RngRing)
            RingAction.setStatusTip("Apply Range Rings every %s"%RngRing)
            RingAction.triggered[()].connect(lambda RngRing=RngRing: self.RngRingSelectCmd(RngRing))
            self.dispRngRing.setMenu(self.dispRngRingmenu)

    def _add_cmaps_to_button(self):
        '''Add a menu to change colormap used for plot.'''
        for cm_name in self.cm_names:
            cmapAction = self.dispCmapmenu.addAction(cm_name)
            cmapAction.setStatusTip("Use the %s colormap"%cm_name)
            cmapAction.triggered[()].connect(lambda cm_name=cm_name: self.cmapSelectCmd(cm_name))
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
        self.dispRngRing = dispmenu.addAction("Add Range Rings")
        self.dispRngRingmenu = QtGui.QMenu("Add Range Rings")
        self.dispRngRingmenu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.dispCmap = dispmenu.addAction("Change Colormap")
        self.dispCmapmenu = QtGui.QMenu("Change Cmap")
        self.dispCmapmenu.setFocusPolicy(QtCore.Qt.NoFocus)
        dispQuickSave = dispmenu.addAction("Quick Save Image")
        dispQuickSave.setShortcut("Ctrl+D")
        dispQuickSave.setStatusTip("Save Image to local directory with default name")
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
        toolValueClick = toolmenu.addAction("Click for Value")
        toolROI = toolmenu.addAction("Select a Region of Interest")
        toolCustom = toolmenu.addAction("Use Custom Tool")
        toolDefault = toolmenu.addAction("Reset File Defaults")
        toolZoomPan.triggered[()].connect(self.toolZoomPanCmd)
        toolValueClick.triggered[()].connect(self.toolValueClickCmd)
        toolROI.triggered[()].connect(self.toolROICmd)
        toolCustom.triggered[()].connect(self.toolCustomCmd)
        toolDefault.triggered[()].connect(self.toolDefaultCmd)
        self.toolsButton.setMenu(toolmenu)

    ########################
    # Selectionion methods #
    ########################

    def NewRadar(self, variable, value, strong):
        '''Slot for 'ValueChanged' signal of :py:class:`Vradar <artview.core.core.Variable>`.

        This will:

        * Update fields and tilts lists and MenuBoxes
        * Check radar scan type and reset limits if needed
        * Reset units and title
        * If strong update: update plot
        '''
        # Get the tilt angles
        self.rTilts = self.Vradar.value.sweep_number['data'][:] 
        # Get field names
        self.fieldnames = self.Vradar.value.fields.keys()

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
        '''Slot for 'ValueChanged' signal of :py:class:`Vfield <artview.core.core.Variable>`.

        This will:

        * Reset limits
        * Reset units
        * Update fields MenuBox
        * If strong update: update plot
        '''
        self._set_default_limits()
        self.units = None
        idx = self.fieldBox.findText(value)
        self.fieldBox.setCurrentIndex(idx)
        if strong and self.Vradar.value is not None:
            self._update_plot()

    def NewLims(self, variable, value, strong):
        '''Slot for 'ValueChanged' signal of :py:class:`Vlims <artview.core.core.Variable>`.

        This will:

        * If strong update: update plot
        '''
        if strong and self.Vradar.value is not None:
            self._update_plot()

    def NewTilt(self, variable, value, strong):
        '''Slot for 'ValueChanged' signal of :py:class:`Vtilt <artview.core.core.Variable>`.

        This will:

        * Update tilt MenuBox
        * If strong update: update plot
        '''
        # +1 since the first one is "Tilt Window"
        self.tiltBox.setCurrentIndex(value+1)  
        if strong and self.Vradar.value is not None:
            self._update_plot()

    def TiltSelectCmd(self, ntilt):
        '''Captures tilt selection and update tilt :py:class:`~artview.core.core.Variable`.'''
        if ntilt < 0:
            ntilt = len(self.rTilts)-1
        elif ntilt >= len(self.rTilts):
            ntilt = 0
        self.Vtilt.change(ntilt)

    def FieldSelectCmd(self, name):
        '''Captures field selection and update field :py:class:`~artview.core.core.Variable`.'''
        self.Vfield.change(name)

    def RngRingSelectCmd(self, ringSel):
        '''Captures Range Ring selection and redraws the field with range rings.'''
        if ringSel is "None":
            self.RngRing = False
        else:
            self.RngRing = True
            # Find the unambigous range of the radar
            try:
                unrng = int(self.Vradar.value.instrument_parameters['unambiguous_range']['data'][0]/1000)
            except:
                unrng = int(self.limits['xmax'])

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

        if self.Vradar.value is not None:
            self._update_plot()

    def cmapSelectCmd(self, cm_name):
        '''Captures colormap selection and redraws.'''
        self.CMAP = cm_name
        if self.Vradar.value is not None:
            self._update_plot()


    def toolZoomPanCmd(self):
        '''Creates and connects to a Zoom/Pan instance.'''
        from .tools import ZoomPan
        scale = 1.1
        self.tools['zoompan'] = ZoomPan(self.Vlims, self.ax, self.limits, \
                          base_scale = scale, parent=self.parent)
        self.tools['zoompan'].connect()

    def toolValueClickCmd(self):
        '''Creates and connects to Point-and-click value retrieval'''
        from .tools import ValueClick
        self.tools['valueclick'] = ValueClick(self.Vradar, self.Vtilt, self.Vfield, \
                                   self.units, self.ax, self.statusbar, parent=self.parent)
        self.tools['valueclick'].connect()

    def toolROICmd(self):
        '''Creates and connects to Region of Interest instance'''
        from .tools import ROI
        self.tools['roi'] = ROI(self.Vradar, self.Vtilt, self.Vfield, self.statusbar, \
                                self.ax, self.display, parent=self.parent)
        self.tools['roi'].connect()

    def toolCustomCmd(self):
        '''Allow user to activate self-defined tool.'''
        from . import tools
        tools.custom_tool(self.tools)

    def toolDefaultCmd(self):
        '''Restore the Display defaults.'''
        from . import tools
        self.tools, self.limits, self.CMAP = tools.restore_default_display(self.tools, \
                                          self.Vfield.value, self.scan_type)
        if self.Vradar.value is not None:
            self._update_plot()

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
            for all bin of the current radar and tilt inside path.

        Notes
        -----
            If Vradar.value is None, returns None
        '''
        from .tools import interior
        radar = self.Vradar.value
        if radar is None:
            return (np.array([]),)*7

        xy, idx = interior(path, radar, self.Vtilt.value)
        aux = (xy[:, 0], xy[:, 1], radar.azimuth['data'][idx[:, 0]],
               radar.range['data'][idx[:, 1]] / 1000.,
               radar.fields[self.Vfield.value]['data'][idx[:, 0], idx[:, 1]],
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
        self.cax = self.fig.add_axes([0.2,0.10, 0.7, 0.02])

    def _update_fig_ax(self):
        '''Set the figure and axis to plot.'''
        if self.scan_type in ("airborne", "rhi"):
            self.YSIZE = 5
        else:
            self.YSIZE = 8
        xwidth = 0.7
        yheight = 0.7 * float(self.YSIZE)/float(self.XSIZE)
        self.ax.set_position([0.2, 0.55-0.5*yheight, xwidth, yheight])
        self.cax.set_position([0.2,0.10, xwidth, 0.02])

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area.'''
        self.canvas = FigureCanvasQTAgg(self.fig)
        # Add the widget to the canvas
        self.layout.addWidget(self.canvas, 1, 0, 7, 6)

    def _update_plot(self):
        '''Draw/Redraw the plot.'''
        self._check_default_field()

        if self.Vfield.value not in self.Vradar.value.fields.keys():
            return

        # Create the plot with PyArt RadarDisplay 
        self.ax.cla() # Clear the plot axes
        self.cax.cla() # Clear the colorbar axes

        # Reset to default title if user entered nothing w/ Title button
        if self.title == '':
            title = None
        else:
            title = self.title

        if self.scan_type == "airborne":
            self.display = pyart.graph.RadarDisplay_Airborne(self.Vradar.value)
            
            self.plot = self.display.plot_sweep_grid(self.Vfield.value, \
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax, fig=self.fig, title=title)
            self.display.set_limits(xlim=(self.limits['xmin'], self.limits['xmax']),\
                                    ylim=(self.limits['ymin'], self.limits['ymax']),\
                                    ax=self.ax)
            self.display.plot_grid_lines()

        elif self.scan_type == "ppi":
            self.display = pyart.graph.RadarDisplay(self.Vradar.value)
            # Create Plot
            self.plot = self.display.plot_ppi(self.Vfield.value, self.Vtilt.value,\
                            vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                            colorbar_flag=False, cmap=self.CMAP,\
                            ax=self.ax, fig=self.fig, title=self.title)
            # Set limits
            self.display.set_limits(xlim=(self.limits['xmin'], self.limits['xmax']),\
                                    ylim=(self.limits['ymin'], self.limits['ymax']),\
                                    ax=self.ax)
            # Add range rings
            if self.RngRing:
                self.display.plot_range_rings(self.RNG_RINGS, ax=self.ax)
            # Add radar location
            self.display.plot_cross_hair(5., ax=self.ax)

        elif self.scan_type == "rhi":
            self.display = pyart.graph.RadarDisplay(self.Vradar.value)
            # Create Plot
            self.plot = self.display.plot_rhi(self.Vfield.value, self.Vtilt.value,\
                            vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                            colorbar_flag=False, cmap=self.CMAP,\
                            ax=self.ax, fig=self.fig, title=self.title)
            self.display.set_limits(xlim=(self.limits['xmin'], self.limits['xmax']),\
                                    ylim=(self.limits['ymin'], self.limits['ymax']),\
                                    ax=self.ax)
            # Add range rings
            if self.RngRing:
                self.display.plot_range_rings(self.RNG_RINGS, ax=self.ax)

        norm = mlabNormalize(vmin=self.limits['vmin'],\
                                           vmax=self.limits['vmax'])
        self.cbar=mlabColorbarBase(self.cax, cmap=self.CMAP,\
                                                norm=norm, orientation='horizontal')
        # colorbar - use specified units or default depending on
        # what has or has not been entered
        if self.units is None or self.units == '':
            try:
                self.units = self.Vradar.value.fields[self.field]['units']
            except:
                self.units = ''
        self.cbar.set_label(self.units)

        print "Plotting %s field, Tilt %d in %s" % (self.Vfield.value, self.Vtilt.value+1, self.name)
        self.canvas.draw()

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

    def _set_default_limits(self):
        ''' Set limits and CMAP to pre-defined default.'''
        from .limits import _default_limits
        self.limits, self.CMAP = _default_limits(self.Vfield.value, \
                                 self.scan_type)

    def _check_file_type(self):
        '''Check file to see if the file is airborne or rhi.'''
        radar = self.Vradar.value
        old_scan_type = self.scan_type
        if radar.scan_type != 'rhi':
            self.scan_type = "ppi"
        else:
            if 'platform_type' in radar.metadata:
                if (radar.metadata['platform_type'] == 'aircraft_tail' or
                    radar.metadata['platform_type'] == 'aircraft'):
                    self.scan_type = "airborne"
                else:
                    self.scan_type = "rhi"
            else:
                self.scan_type = "rhi"

        if self.scan_type != old_scan_type:
            print "Changed Scan types, reinitializing"
            self._check_default_field()
            self._set_default_limits()
            self._update_fig_ax()

    ########################
    # Image save methods #
    ########################
    def _quick_savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display via PyArt interface.'''
        PNAME = self.display.generate_filename(self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        print "Creating "+ PNAME

    def _savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display using PyQt dialog interface.'''
        PBNAME = self.display.generate_filename(self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        file_choices = "PNG (*.png)|*.png"
        path = unicode(QtGui.QFileDialog.getSaveFileName(self, 'Save file', '', file_choices))
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

    def chooseRadar(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vradar"] = getattr(item[1],item[2])

    def chooseField(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vfield"] = getattr(item[1],item[2])

    def chooseTilt(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vtilt"] = getattr(item[1],item[2])

    def chooseLims(self):
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.result["Vlims"] = getattr(item[1],item[2])

    def setupUi(self):

        self.radarButton = QtGui.QPushButton("Find Variable")
        self.radarButton.clicked.connect(self.chooseRadar)
        self.layout.addWidget(QtGui.QLabel("VRadar"), 0, 0)
        self.layout.addWidget(self.radarButton, 0, 1, 1, 3)

        self.fieldButton = QtGui.QPushButton("Find Variable")
        self.fieldButton.clicked.connect(self.chooseField)
        self.layout.addWidget(QtGui.QLabel("Vfield"), 1, 0)
        self.field = QtGui.QLineEdit("")
        self.layout.addWidget(self.field , 1, 1)
        self.layout.addWidget(QtGui.QLabel("or"), 1, 2)
        self.layout.addWidget(self.fieldButton, 1, 3)

        self.tiltButton = QtGui.QPushButton("Find Variable")
        self.tiltButton.clicked.connect(self.chooseTilt)
        self.layout.addWidget(QtGui.QLabel("Vtilt"), 2, 0)
        self.tilt = QtGui.QSpinBox()
        self.layout.addWidget(self.tilt , 2, 1)
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

        # if no Vradar abort
        if 'Vradar' not in self.result:
            common.ShowWarning("Must select a variable for Vradar")
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
