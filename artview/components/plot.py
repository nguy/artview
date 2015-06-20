"""
plot.py

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



from ..core import Variable, Component, common

# Save image file type and DPI (resolution)
IMAGE_EXT = 'png'
DPI = 100
#========================================================================
#######################
# BEGIN PARV CODE #
#######################  


class Display(Component):
    '''
    Class that creates a display plot, using a returned Radar structure 
    from the PyArt pyart.graph package.
    '''

    def __init__(self, Vradar, Vfield, Vtilt, Vlims=None, \
                 airborne=False, rhi=False, name="Display", parent=None):
        '''
        Initialize the class to create display.

        Parameters::
        ----------
        Vradar - Variable instance
            Radar signal variable to be used.
        Vfield - Variable instance
            Field signal variable to be used.
        Vtilt - Variable instance
            Tilt signal variable to be used.

        [Optional]
        Vlims - Variable instance
            Limits signal variable to be used.
            A value of None will instantiate a limits variable.
        airborne - boolean
            Set True to display airborne type radar files (assumes tail radar setup such as NOAA P-3).
        rhi - boolean
            Set True to display RHI type radar files.
        name - string
            Display window name.
        parent - PyQt instance
            Parent instance to associate to Display window.
            If None, then Qt owns, otherwise associated with parent PyQt instance.

        Notes::
        -----
        This class records the selected button and passes the 
        change value back to variable.
        '''
        super(Display, self).__init__(name=name, parent=parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        #AG set up signal, so that DISPLAY can react to external (or internal) changes in radar,field and tilt
        #AG radar,field and tilt are expected to be Core.Variable instances
        #AG I use the capital V so people remember using ".value"
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
        self.connectAllVariables()

        self.airborne = airborne
        self.rhi = rhi

        # Set plot title and colorbar units to defaults
        self.title = None
        self.units = None

        # Initialize limits   
        self._set_default_limits()

        if self.Vlims.value is None:
            self.Vlims.change(self.limits, strong=False)

        # Set the default range rings
        self.RngRingList = ["None", "10 km", "20 km", "30 km", "50 km", "100 km"]
        self.RngRing = False

        # Find the PyArt colormap names
        self.cm_names = [m for m in cm.datad if not m.endswith("_r")]
        self.cm_names.sort()

        # Create a figure for output
        self._set_fig_ax(nrows=1, ncols=1)

        # Create tool dictionary
        self.tools = {}
        self.tools['zoompan'] = None

        # Launch the GUI interface
        self.LaunchGUI()

        # AG - Initialize radar
        self.NewRadar(None, None, True)

        self.show()

#        self.pickPoint = self.fig.canvas.mpl_connect('button_press_event', self.onPick)

    def keyPressEvent(self, event):
        '''Allow tilt adjustment via the Up-Down arrow keys.'''
        if event.key() == QtCore.Qt.Key_Up:
            self.TiltSelectCmd(self.Vtilt.value + 1)
        elif event.key() == QtCore.Qt.Key_Down:
            self.TiltSelectCmd(self.Vtilt.value - 1)
        else:
            super(Display, self).keyPressEvent(event)

#     def onPick(self, event):
#         '''Get value at the point selected by mouse click.'''
#         xdata = event.xdata # get event x location
#         ydata = event.ydata # get event y location
#         az = np.arctan2(xdata, ydata)*180./np.pi
#         radar = self.Vradar.value #keep equantions clean
#         if az < 0:
#             az = az + 360.
#         rng = np.sqrt(xdata*xdata+ydata*ydata)
#         azindex = np.argmin(np.abs(radar.azimuth['data'][radar.sweep_start_ray_index['data'][self.Vtilt.value]:radar.sweep_end_ray_index['data'][self.Vtilt.value]]-az))+radar.sweep_start_ray_index['data'][self.Vtilt.value]
#         rngindex = np.argmin(np.abs(radar.range['data']-rng*1000.))
#         msg = 'x = %4.2f, y = %4.2f, Azimuth = %4.2f deg., Range = %4.2f km, %s = %4.2f %s'\
#         %(xdata, ydata, radar.azimuth['data'][azindex], radar.range['data'][rngindex]/1000., self.Vfield.value, radar.fields[self.Vfield.value]['data'][azindex][rngindex], self.units)
#         self.statusBar().showMessage(msg)

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
#        self.statusBar()

        self.central_widget.setLayout(self.layout)
        #self.setLayout(self.layout)
        # Create the Tilt buttons
        #self.CreateTiltWidget()

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

#        tiltsb = QtGui.QPushButton("Tilt Select")
#        tiltsb.setToolTip("Choose tilt elevation angle")
#        tiltsb.clicked.connect(self._open_tiltbuttonwindow)

        #self._fillFieldBox() AG will be done by newRadar

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
        self.tiltbuttonwindow = TiltButtonWindow(self.Vradar, self.Vtilt, \
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
        #self._fillTiltBox() AG will be done by newRadar

    def _add_fieldBoxUI(self):
        '''Create the Field Selection ComboBox.'''
        self.fieldBox = QtGui.QComboBox()
        self.fieldBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fieldBox.setToolTip("Choose variable/field")
        self.fieldBox.activated[str].connect(self._fieldAction)
        #self._fillFieldBox() AG will be done by newRadar

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
        '''Display changes after radar Variable class is altered.'''
        # In case the flags were not used at startup
        self._check_file_type()

        # Get the tilt angles
        self.rTilts = self.Vradar.value.sweep_number['data'][:] 
        # Get field names
        self.fieldnames = self.Vradar.value.fields.keys()

        # Update field and tilt MenuBox
        self._fillTiltBox()
        self._fillFieldBox()

        self.units = None
        self.title = None
        if strong:
            self._update_plot()

    def NewField(self, variable, value, strong):
        '''Display changes after field in Variable class is altered.'''
        self._set_default_limits()
        self.units = None
        idx = self.fieldBox.findText(value)
        self.fieldBox.setCurrentIndex(idx)
        if strong:
            self._update_plot()

    def NewLims(self, variable, value, strong):
        '''Display changes after limits in Variable class is altered.'''
        if strong:
            self._update_plot()

    def NewTilt(self, variable, value, strong):
        '''Display changes after tilt in Variable class is altered.'''
        # +1 since the first one is "Tilt Window"
        self.tiltBox.setCurrentIndex(value+1)  
        if strong:
            self._update_plot()

    def TiltSelectCmd(self, ntilt):
        '''Captures tilt selection and redraws the field with new tilt.'''
        self.Vtilt.change(ntilt)
        #AG tilt is changed and signal sent, so this and other classes do what they need to do

    def FieldSelectCmd(self, nombre):
        '''Captures field selection and redraws the new field.'''
        self.Vfield.change(nombre)

    def RngRingSelectCmd(self, ringSel):
        '''Captures Range Ring selection and redraws the field with range rings.'''
        if ringSel is "None":
            self.RngRing = False
        else:
            self.RngRing = True
            # Find the unambigous range of the radar
            try:
                unrng = int(self.radar.instrument_parameters['unambiguous_range']['data'][0]/1000)
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

        self._update_plot()

    def cmapSelectCmd(self, cm_name):
        '''Captures colormap selection and redraws.'''
        self.CMAP = cm_name
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
        self.tools['roi'] = ROI(self.Vradar, self.Vtilt, self.ax, self.display, parent=self.parent)
        self.tools['roi'].connect()

    def toolCustomCmd(self):
        '''Allow user to activate self-defined tool.'''
        from . import tools
        tools.custom_tool(self.tools)

    def toolDefaultCmd(self):
        '''Restore the Display defaults.'''
        from . import tools
        self.tools['zoompan'], self.limits, self.CMAP = tools.restore_default_display(self.tools, \
                                          self.Vfield.value, self.airborne, self.rhi)
        self._update_plot()

    ####################
    # Plotting methods #
    ####################

    def _set_fig_ax(self, nrows=1, ncols=1):
        '''Set the figure and axis to plot.'''
        self.fig = Figure(figsize=(self.limits['xsize'], self.limits['ysize']))
        xwidth = 0.7
        yheight = 0.7 * float(self.limits['ysize'])/float(self.limits['xsize'])
        self.ax = self.fig.add_axes([0.2, 0.2, xwidth, yheight])
        self.cax = self.fig.add_axes([0.2,0.10, xwidth, 0.02])
        
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)

    def _set_fig_ax_rhi(self):
        '''Change figure size and limits if RHI.'''
        self._set_default_limits()
        self.fig.set_size_inches(self.limits['xsize'], self.limits['ysize'])
        self._set_fig_ax()

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area.'''
        self.canvas = FigureCanvasQTAgg(self.fig)
        # Add the widget to the canvas
        self.layout.addWidget(self.canvas, 1, 0, 7, 6)

    def _update_plot(self):
        '''Draw/Redraw the plot.'''
        self._check_default_field()

        # Create the plot with PyArt RadarDisplay 
        self.ax.cla() # Clear the current axes

        # Reset to default title if user entered nothing w/ Title button
        if self.title == '':
            self.title = None

        # If Zoom/Pan selected, Set up the zoom/pan functionality
#        if self.zp != None:
#            scale = 1.1
#            self.zp = ZoomPan(self.Vlims, self.ax, self.limits, \
#                              base_scale = scale, parent=self.parent)
#            self.zp.connect()

        if self.airborne:
            self.display = pyart.graph.RadarDisplay_Airborne(self.Vradar.value)
            
            self.plot = self.display.plot_sweep_grid(self.Vfield.value, \
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax, title=self.title)
            self.display.set_limits(xlim=(self.limits['xmin'], self.limits['xmax']),\
                                    ylim=(self.limits['ymin'], self.limits['ymax']),\
                                    ax=self.ax, fig=self.fig)
            self.display.plot_grid_lines()
        else:
            self.display = pyart.graph.RadarDisplay(self.Vradar.value)
            if self.Vradar.value.scan_type != 'rhi':
                # Create Plot
                if self.Vtilt.value < len(self.rTilts):
                    pass
                else:
                    self.Vtilt.change(0)
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
            else:
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

        print "Plotting %s field, Tilt %d" % (self.Vfield.value, self.Vtilt.value+1)
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
        if self.Vfield.value == 'reflectivity':
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
        from .limits import initialize_limits
        self.limits, self.CMAP = initialize_limits(self.Vfield.value, \
                                 airborne=self.airborne, rhi=self.rhi)

    def _check_file_type(self):
        '''Check file to see if the file is airborne or rhi.'''
        radar = self.Vradar.value
        if radar.scan_type != 'rhi':
            return
        else:
            if 'platform_type' in radar.metadata:
                if (radar.metadata['platform_type'] == 'aircraft_tail' or
                    radar.metadata['platform_type'] == 'aircraft'):
                    self.airborne = True
                else:
                    self.rhi = True
            else:
                self.rhi = True
            #XXX this has only one effect: self._set_default_limits()
            self._set_fig_ax_rhi()

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
#            self.statusBar().
            self.statusbar.showMessage('Saved to %s' % path)
