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

import limits
import common
from core import Variable, Component
from limits import Ui_LimsDialog

# Save image file type and DPI (resolution)
IMAGE_EXT = 'png'
DPI = 100
#========================================================================
#######################
# BEGIN PARV CODE #
#######################  


class Display(Component):
    '''Class that plots a Radar structure using pyart.graph'''

    def __init__(self, Vradar, Vfield, Vtilt, Vlims=None, airborne=False, rhi=False, name="Display", parent=None):
        '''Initialize the class to create the interface'''
        super(Display, self).__init__(name=name, parent=parent)
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
           
        self.limits, self.CMAP = limits.initialize_limits(self.Vfield.value, \
                                         airborne=self.airborne, rhi=self.rhi)
        
        if self.Vlims.value is None:
            self.Vlims.change(self.limits)
        
        # Set the default range rings
        self.RngRingList = ["None", "10 km", "20 km", "30 km", "50 km", "100 km"]
        self.RngRing = False
        
        # Find the PyArt colormap names
#        self.cm_names = pyart.graph.cm._cmapnames
        self.cm_names = [m for m in cm.datad if not m.endswith("_r")]
        self.cm_names.sort()
  
        # Create a figure for output
        self._set_fig_ax(nrows=1, ncols=1)
        
        # Initiate no tool useage
#        self.ToolSelect = "No Tools" #AG this is problably not the right way of doing this
        self.zp = None
        
        # Launch the GUI interface
        self.LaunchGUI() 
        
        # AG - Initialize radar
        self.NewRadar(None, None)
        
        self.show()
        
        self.pickPoint = self.fig.canvas.mpl_connect('button_press_event', self.onPick)

    def keyPressEvent(self, event):
        '''Allow tilt adjustment via the Up-Down arrow keys'''
        if event.key() == QtCore.Qt.Key_Up:
            self.TiltSelectCmd(self.Vtilt.value + 1)
        elif event.key() == QtCore.Qt.Key_Down:
            self.TiltSelectCmd(self.Vtilt.value - 1)
        else:
            super(Display, self).keyPressEvent(event)

    def onPick(self, event):
        '''Get value at the point selected by mouse click'''
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        az = np.arctan2(xdata, ydata)*180./np.pi
        radar = self.Vradar.value #keep equantions clean
        if az < 0:
            az = az + 360.
        rng = np.sqrt(xdata*xdata+ydata*ydata)
        azindex = np.argmin(np.abs(radar.azimuth['data'][radar.sweep_start_ray_index['data'][self.Vtilt.value]:radar.sweep_end_ray_index['data'][self.Vtilt.value]]-az))+radar.sweep_start_ray_index['data'][self.Vtilt.value]
        rngindex = np.argmin(np.abs(radar.range['data']-rng*1000.))
        msg = 'x = %4.2f, y = %4.2f, Azimuth = %4.2f deg., Range = %4.2f km, %s = %4.2f %s'\
        %(xdata, ydata, radar.azimuth['data'][azindex], radar.range['data'][rngindex]/1000., self.Vfield.value, radar.fields[self.Vfield.value]['data'][azindex][rngindex], self.units)
        self.statusBar().showMessage(msg)

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
#        self.statusBar()
        
        self.central_widget.setLayout(self.layout)
        #self.setLayout(self.layout)
        # Create the Tilt buttons
        #self.CreateTiltWidget()
        
        # Add buttons along display for user control
        self.addButtons()
        self.setUILayout()
                    
    ##################################
    # User display interface methods #
    ##################################
    def addButtons(self):
        '''Add a series of buttons for user control over display'''
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
        '''Setup the button/display UI layout'''
        self.layout.addWidget(self.tiltBox, 0, 0)
        self.layout.addWidget(self.fieldBox, 0, 1)
        self.layout.addWidget(self.dispButton, 0, 2)
        self.layout.addWidget(self.toolsButton, 0, 3)
        
    #############################
    # Functionality methods #
    #############################
        
    def _open_LimsDialog(self):
#        self.limsDialog = QtGui.QDialog()
#        self.limsDialog = Ui_LimsDialog(self.Vradar, self.Vlims, self.limits, \
#                          name=self.name+" Limts Adjustment", parent=self.parent)
        self.limits = limits.limits_dialog(self.limits, self.name)     
        self._update_plot()
    
    def _fillTiltBox(self):
        '''Fill in the Tilt Window Box with current elevation angles'''
        self.tiltBox.clear()
        self.tiltBox.addItem("Tilt Window")
        # Loop through and create each tilt button
        elevs = self.Vradar.value.fixed_angle['data'][:]
        for ntilt in self.rTilts:
            btntxt = "%2.1f deg (Tilt %d)"%(elevs[ntilt], ntilt+1)
            self.tiltBox.addItem(btntxt)
    
    def _fillFieldBox(self):
        '''Fill in the Field Window Box with current variable names'''
        self.fieldBox.clear()
        self.fieldBox.addItem("Field Window")
        # Loop through and create each field button
        for field in self.fieldnames:
            self.fieldBox.addItem(field)
    
    def _lims_input(self, entry):
        '''Retrieve new limits input'''
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
        '''Define action for Tilt Button selection'''
        if text == "Tilt Window":
            self._open_tiltbuttonwindow()
        else:
            ntilt = int(text.split("(Tilt ")[1][:-1])-1
            self.TiltSelectCmd(ntilt)

    def _fieldAction(self, text):
        '''Define action for Field Button selection'''
        if text == "Field Window":
            self._open_fieldbuttonwindow()
        else:
            self.FieldSelectCmd(str(text))

    def _title_input(self):
        '''Retrieve new plot title'''
#        if self.title is None:
#            old_val = ''
#        else:
#            old_val = self.title
#        val, entry = QtGui.QInputDialog.getText(self, "Plot Title", \
#                  "Title:", 0, old_val)
        val, entry = common.string_dialog(self.title, "Plot Title", "Title:")
        if entry is True:
            self.title = val
            self._update_plot()

    def _units_input(self):
        '''Retrieve new plot units'''
#        if self.units is None:
#            old_val = ''
#        else:
#            old_val = self.units
#        val, entry = QtGui.QInputDialog.getText(self, "Plot Units", \
#                  "Units:", 0, old_val)
        val, entry = common.string_dialog(self.units, "Plot Units", "Units:")
        if entry is True:
            self.units = val
            self._update_plot()
            
    def _open_tiltbuttonwindow(self):
        '''Open a TiltButtonWindow instance'''
        from tilt import TiltButtonWindow
        self.tiltbuttonwindow = TiltButtonWindow(self.Vradar, self.Vtilt, \
                            name=self.name+" Tilt Selection", parent=self.parent)
        
    def _open_fieldbuttonwindow(self):
        '''Open a FieldButtonWindow instance'''
        from field import FieldButtonWindow
        self.fieldbuttonwindow = FieldButtonWindow(self.Vradar, self.Vfield, \
                            name=self.name+" Field Selection", parent=self.parent)
        
    def _add_RngRing_to_button(self):
        '''Add a menu to display range rings on plot'''
        for RngRing in self.RngRingList:
            RingAction = self.dispRngRingmenu.addAction(RngRing)
            RingAction.setStatusTip("Apply Range Rings every %s"%RngRing)
            RingAction.triggered[()].connect(lambda RngRing=RngRing: self.RngRingSelectCmd(RngRing))
            self.dispRngRing.setMenu(self.dispRngRingmenu)
        
    def _add_cmaps_to_button(self):
        '''Add a menu to change colormap used for plot'''
        for cm_name in self.cm_names:
            cmapAction = self.dispCmapmenu.addAction(cm_name)
            cmapAction.setStatusTip("Use the %s colormap"%cm_name)
            cmapAction.triggered[()].connect(lambda cm_name=cm_name: self.cmapSelectCmd(cm_name))
            self.dispCmap.setMenu(self.dispCmapmenu)
            
    def _add_displayBoxUI(self):
        '''Create the Display Options Button menu'''
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
        '''Create the Tilt Selection ComboBox'''
        self.tiltBox = QtGui.QComboBox()
        self.tiltBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tiltBox.setToolTip("Choose tilt elevation angle")
        self.tiltBox.activated[str].connect(self._tiltAction)
        #self._fillTiltBox() AG will be done by newRadar

    def _add_fieldBoxUI(self):
        '''Create the Field Selection ComboBox'''
        self.fieldBox = QtGui.QComboBox()
        self.fieldBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fieldBox.setToolTip("Choose variable/field")
        self.fieldBox.activated[str].connect(self._fieldAction)
        #self._fillFieldBox() AG will be done by newRadar
                   
    def _add_toolsBoxUI(self):
        '''Create the Tools Button menu'''
        self.toolsButton = QtGui.QPushButton("Toolbox")
        self.toolsButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.toolsButton.setToolTip("Choose a tool to apply")
        toolmenu = QtGui.QMenu(self)
        toolZoomPan = toolmenu.addAction("Zoom/Pan")
        toolCustom = toolmenu.addAction("Use Custom Tool")
        toolDefault = toolmenu.addAction("Reset file defaults")
        toolZoomPan.triggered[()].connect(self.toolZoomPanCmd)
        toolCustom.triggered[()].connect(self.toolCustomCmd)
        toolDefault.triggered[()].connect(self.toolDefaultCmd)
        self.toolsButton.setMenu(toolmenu)
        
    ########################
    # Selectionion methods #
    ########################

    def NewRadar(self, variable, value):
        '''Display changes after radar Variable class is altered'''
        # In case the flags were not used at startup
        self._check_file_type()
        self._set_figure_canvas()

        # Get the tilt angles
        self.rTilts = self.Vradar.value.sweep_number['data'][:] 
        # Get field names
        self.fieldnames = self.Vradar.value.fields.keys()

        # Update field and tilt MenuBox
        self._fillTiltBox()
        self._fillFieldBox()

        # Set up the menus associated with scanning ground radars
        if self.airborne or self.rhi:
            pass
        else:
            pass
        self.units = None
        self.title = None
        self._update_plot()

    def NewField(self, variable, value):
        '''Display changes after field in Variable class is altered'''
        self.limits, self.CMAP = limits.initialize_limits(self.Vfield.value, \
                                         airborne=self.airborne, rhi=self.rhi)
        self.units = None
        idx = self.fieldBox.findText(value)
        self.fieldBox.setCurrentIndex(idx)
        self._update_plot()

    def NewLims(self, variable, value):
        '''Display changes after limits in Variable class is altered'''
        self._update_plot()

    def NewTilt(self,variable,value):
        '''Display changes after tilt in Variable class is altered'''
        # +1 since the first one is "Tilt Window"
        self.tiltBox.setCurrentIndex(value+1)  
        self._update_plot()

    def TiltSelectCmd(self, ntilt):
        '''Captures tilt selection and redraws the field with new tilt'''
        self.Vtilt.change(ntilt)
        #AG tilt is changed and signal sent, so this and other classes do what they need to do

    def FieldSelectCmd(self, nombre):
        '''Captures field selection and redraws the new field'''
        self.Vfield.change(nombre)

    def RngRingSelectCmd(self, ringSel):
        '''Captures Range Ring selection and redraws the field with range rings'''
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
        '''Captures colormap selection and redraws'''
        self.CMAP = cm_name
        self._update_plot()
        
    def toolZoomPanCmd(self):
        '''Creates and connects to a Zoom/Pan instance'''
        scale = 1.1
        self.zp = ZoomPan(self.Vlims, self.ax, self.limits, \
                          base_scale = scale, parent=self.parent)
        self.zp.connect()
        
    def toolCustomCmd(self):
        '''Allow user to activate self-defined tool'''
        if self.zp != None:
            self.zp.disconnect()
            self.zp = None
        msg = "This feature is inactive at present"
        print msg
        warn = common.ShowWarning(msg)
                
    def toolDefaultCmd(self):
        '''Restore the Display defaults'''
        if self.zp != None:
            self.zp.disconnect()
            self.zp = None
        self.limits, self.CMAP = limits.initialize_limits(self.Vfield.value, \
                                         airborne=self.airborne, rhi=self.rhi)
        self._update_plot()
         
    ####################
    # Plotting methods #
    ####################

    def _set_fig_ax(self, nrows=1, ncols=1):
        '''Set the figure and axis to plot'''
        self.fig = Figure(figsize=(self.limits['xsize'], self.limits['ysize']))
        xwidth = 0.7
        yheight = 0.7 * float(self.limits['ysize'])/float(self.limits['xsize'])
        self.ax = self.fig.add_axes([0.2, 0.2, xwidth, yheight])
        self.cax = self.fig.add_axes([0.2,0.10, xwidth, 0.02])
        
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)
        
    def _set_fig_ax_rhi(self):
        '''Change figure size and limits if RHI'''
        self.limits, self.CMAP = limits.initialize_limits(self.Vfield.value, \
                                         airborne=self.airborne, rhi=self.rhi)
        self.fig.set_size_inches(self.limits['xsize'], self.limits['ysize'])
        self._set_fig_ax()

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area'''
        self.canvas = FigureCanvasQTAgg(self.fig)
        # Add the widget to the canvas
        self.layout.addWidget(self.canvas, 1, 0, 7, 6)

    def _update_plot(self):
        '''Draw/Redraw the plot'''
        # This is a bit of a hack to ensure that the viewer works with files
        # withouth "standard" output as defined by PyArt
        # Check to see if the field 'reflectivity' exists for the initial open
        self._check_default_field()
    
        # Create the plot with PyArt RadarDisplay 
        # Always intitiates at lowest elevation angle
        self.ax.cla()

        # Reset to default title if user entered nothing w/ Title button
        if self.title == '':
            self.title = None
        
        # If Zoom/Pan selected, Set up the zoom/pan functionality
        if self.zp != None:
            scale = 1.1
            self.zp = ZoomPan(self.Vlims, self.ax, self.limits, \
                              base_scale = scale, parent=self.parent)
            #figZoom = self.zp.zoom()
            #figPan = self.zp.pan_factory(self.limits)
            self.zp.connect()

        if self.airborne:
            self.display = pyart.graph.RadarDisplay_Airborne(self.Vradar.value)
            
            self.plot = self.display.plot_sweep_grid(self.Vfield.value, \
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax, title=self.title)
            self.display.set_limits(xlim=(self.limits['xmin'], self.limits['xmax']),\
                                    ylim=(self.limits['ymin'], self.limits['ymax']),\
                                    ax=self.ax)
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
                                ax=self.ax, title=self.title)
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
                                ax=self.ax, title=self.title)
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
        '''Hack to perform a check on reflectivity to make it work with 
        a larger number of files as there are many nomenclature is the
        weather radar world.
        
        This should only occur upon start up with a new file'''
        if self.Vfield.value == 'reflectivity':
            if self.Vfield.value in self.fieldnames:
                pass
            elif 'CZ' in self.fieldnames:
                self.Vfield.change('CZ')
            elif 'DZ' in self.fieldnames:
                self.Vfield.change('DZ')
            elif 'dbz' in self.fieldnames:
                self.Vfield.change('dbz')
            elif 'DBZ' in self.fieldnames:
                self.Vfield.change('DBZ')
            elif 'dBZ' in self.fieldnames:
                self.Vfield.change('dBZ')
            elif 'Z' in self.fieldnames:
                self.Vfield.change('Z')
            elif 'DBZ_S' in self.fieldnames:
                self.Vfield.change('DBZ_S')
            elif 'reflectivity_horizontal'in self.fieldnames:
                self.Vfield.change('reflectivity_horizontal')
            elif 'DBZH' in self.fieldnames:
                self.Vfield.change('DBZH')
            else:
                msg = "Could not find the field name.\n\
                      You can add an additional name by modifying the\n\
                      'check_default_field' function in plot.py\n\
                      Please send a note to ARTView folks to add this name\n\
                      Thanks!"
                common.ShowWarning(msg)

                
    def _check_file_type(self):
        '''Check file to see if the file is airborne or rhi'''
        if self.Vradar.value.scan_type != 'rhi':
            pass
        else:
            try:
                (self.Vradar.value.metadata['platform_type'] == 'aircraft_tail') or \
                (self.Vradar.value.metadata['platform_type'] == 'aircraft')
                self.airborne = True
            except:
                self.rhi = True
            
            self._set_fig_ax_rhi()
 
    ########################
    # Image save methods #
    ########################
    def _quick_savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display via PyArt'''
        PNAME = self.display.generate_filename(self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        print "Creating "+ PNAME
        
    def _savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display using PyQt dialog'''
        PBNAME = self.display.generate_filename(self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        file_choices = "PNG (*.png)|*.png"
        path = unicode(QtGui.QFileDialog.getSaveFileName(self, 'Save file', '', file_choices))
        if path:
            self.canvas.print_figure(path, dpi=DPI)
            self.statusBar().showMessage('Saved to %s' % path)
        
##########################
# Zoom/Pan Class Methods #
##########################
class ZoomPan(QtGui.QMainWindow):
    '''
    Class for Zoom and Pan of plot
    Modified an original answer found here: http://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
    '''
    def __init__(self, Vlims, ax, limits, base_scale = 2., name="ZoomPan", parent=None):
        super(ZoomPan, self).__init__(parent)
        self.parent = parent
        self.name = name
        
        # Set up signal, so that DISPLAY can react to external 
        # (or internal) changes in limits (Core.Variable instances expected)
        # Send the new limits back to the main window
#        self.Vradar = Vradar
#        QtCore.QObject.connect(Vradar, QtCore.SIGNAL("ValueChanged"), self.NewRadar)
        self.Vlims = Vlims
        QtCore.QObject.connect(Vlims, QtCore.SIGNAL("ValueChanged"), self.NewLimits)
        
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None
        self.entry = {}
        self.entry['dmin'] = None
        self.entry['dmax'] = None
        #self.connect()
        self.ax = ax
        self.limits = limits
        self.base_scale = base_scale
        self.fig = ax.get_figure() # get the figure of interest
        
    def connect(self):
        self.scrollID = self.fig.canvas.mpl_connect('scroll_event', self.onZoom)
        self.pressID = self.fig.canvas.mpl_connect('button_press_event',self.onPress)
        self.releaseID = self.fig.canvas.mpl_connect('button_release_event',self.onRelease)
        self.motionID = self.fig.canvas.mpl_connect('motion_notify_event',self.onMotion)

    def onZoom(self, event):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location

        if event.button == 'down':
            # deal with zoom in
            scale_factor = 1 / self.base_scale
        elif event.button == 'up':
            # deal with zoom out
            scale_factor = self.base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print event.button

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
        self.ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
        self.ax.figure.canvas.draw()
            
        # Record the new limits and pass them to main window
        self.limits['xmin'] = xdata - new_width * (1-relx)
        self.limits['xmax'] = xdata + new_width * (relx)
        self.limits['ymin'] = ydata - new_height * (1-rely)
        self.limits['ymax'] = ydata + new_height * (rely)
        
    def onPress(self, event):
        if event.inaxes != self.ax: return
        self.cur_xlim = self.ax.get_xlim()
        self.cur_ylim = self.ax.get_ylim()
        self.press = self.x0, self.y0, event.xdata, event.ydata
        self.x0, self.y0, self.xpress, self.ypress = self.press

    def onRelease(self, event):
        self.press = None
        self.ax.figure.canvas.draw()

    def onMotion(self, event):
        if self.press is None: return
        if event.inaxes != self.ax: return
        dx = event.xdata - self.xpress
        dy = event.ydata - self.ypress
        self.cur_xlim -= dx
        self.cur_ylim -= dy
        self.ax.set_xlim(self.cur_xlim)
        self.ax.set_ylim(self.cur_ylim)

        self.ax.figure.canvas.draw()
            
        # Record the new limits and pass them to main window
        self.limits['xmin'], self.limits['xmax'] = self.cur_xlim[0], self.cur_xlim[1]
        self.limits['ymin'], self.limits['ymax'] = self.cur_ylim[0], self.cur_ylim[1]
    
    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.scrollID)
        self.fig.canvas.mpl_disconnect(self.pressID)
        self.fig.canvas.mpl_disconnect(self.releaseID)
        self.fig.canvas.mpl_disconnect(self.motionID)
        
    def _pass_lims(self):
        self.limits['xmin'] = self.entry['xmin']
        self.limits['xmax'] = self.entry['xmax']
        self.limits['ymin'] = self.entry['ymin']
        self.limits['ymax'] = self.entry['ymax']
        
        self.LimsDialog.accept()
        self.Vlims.change(self.limits)
             
    def NewLimits(self, variable, value):
        '''Retrieve new limits input'''
        #self._pass_lims()
        print "In NewLims"
    
    def NewRadar(self, variable, value):
        # update Limits
        #self._pass_lims()
        print "In NewRadar"

