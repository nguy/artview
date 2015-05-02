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



# Limits for varioud variable plots
Z_LIMS = (-10., 65.)
VR_LIMS = (-30., 30.)
ZDR_LIMS = (-5., 5.)
RHO_HV_LIMS = (.8, 1.)
KDP_LIMS = (0., 5.)
PHIDP_LIMS =(0., 1.)
NCP_LIMS = (0., 1.)
SW_LIMS = (-1., 10.)
TP_LIMS = (-200., 100.)

# X, Y range and size for airborne file types
AIR_XRNG = (-150., 150.)
AIR_YRNG = (-10., 20.)
AIR_XSIZE = 8
AIR_YSIZE = 5

# X, Y range and size for PPI file types
PPI_XRNG = (-150., 150.)
PPI_YRNG = (-150., 150.)
PPI_XSIZE = 8
PPI_YSIZE = 8

# X, Y range and size for RHI file types
RHI_XRNG = (0., 150.)
RHI_YRNG = (0., 20.)
RHI_XSIZE = 8
RHI_YSIZE = 5

# Save image file type and DPI (resolution)
IMAGE_EXT = 'png'
DPI = 100
#========================================================================
#######################
# BEGIN PARV CODE #
#######################  


class Display(QtGui.QMainWindow):
    '''Class that plots a Radar structure using pyart.graph'''

    def __init__(self, Vradar, Vfield, Vtilt, airborne=False, rhi=False, name="Display", parent=None):
        '''Initialize the class to create the interface'''
        super(Display, self).__init__(parent)
        self.parent = parent
        self.name = name
        self.setWindowTitle(name)
        
        #XXX set up signal, so that DISPLAY can react to external (or internal) changes in radar,field and tilt
        #XXX radar,field and tilt are expected to be Core.Variable instances
        #XXX I use the capital V so people remember using ".value"
        self.Vradar = Vradar
        QtCore.QObject.connect(Vradar,QtCore.SIGNAL("ValueChanged"),self.NewRadar)
        self.Vfield = Vfield
        QtCore.QObject.connect(Vfield,QtCore.SIGNAL("ValueChanged"),self.NewField)
        self.Vtilt = Vtilt
        QtCore.QObject.connect(Vtilt,QtCore.SIGNAL("ValueChanged"),self.NewTilt)
        
        self.airborne = airborne
        self.rhi = rhi
        
        # Set size of plot
        self.XSIZE = PPI_XSIZE
        self.YSIZE = PPI_YSIZE
        self.XRNG = PPI_XRNG
        self.YRNG = PPI_YRNG
        if self.airborne:
            self.XSIZE = AIR_XSIZE
            self.YSIZE = AIR_YSIZE
            self.XRNG = AIR_XRNG
            self.YRNG = AIR_YRNG
        if self.rhi:
            self.XSIZE = RHI_XSIZE
            self.YSIZE = RHI_YSIZE
            self.XRNG = RHI_XRNG
            self.YRNG = RHI_YRNG
        
        # Set plot title and colorbar units to defaults
        self.title = None
        self.units = None
        # Initialize limits
        self._initialize_limits()
            
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
        self.ToolSelect = "No Tools" #XXX this is problably not the right way of doing this
        
        # Launch the GUI interface
        self.LaunchGUI() 
        
        self.NewRadar(None, None) #XXX initialise radar
        
        self.show()
        
        self.pickPoint = self.fig.canvas.mpl_connect('button_press_event', self.onPick)

        
    # Allow advancement via left and right arrow keys
    # and tilt adjustment via the Up-Down arrow keys
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Up:
            self.TiltSelectCmd(self.Vtilt.value + 1) #XXX Display control de tilt, but not the file
        elif event.key()==QtCore.Qt.Key_Down:
            self.TiltSelectCmd(self.Vtilt.value - 1) #XXX Display control de tilt, but not the file
        else:
            if self.parent==None:
                QtGui.QWidget.keyPressEvent(self, event)
            else:
                self.parent.keyPressEvent(event) #XXX send event to parent to handel it, I consider not having a pygt form of doing this a limitation
            
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
        
        # Create the Tools ComboBox
#        self.toolsBoxUI()
        
        self.addButtons()
                    
    ########################
    # Button methods #
    ######################## 
    def addButtons(self):
        '''If not BASIC mode, then add functionality buttons'''
        # Create the button controls
        limsb = QtGui.QPushButton("Adjust Limits")
        limsb.setFocusPolicy(QtCore.Qt.NoFocus)
        limsb.setToolTip("Set data, X, and Y range limits")
        #limsb.clicked.connect(self.showLimsDialog)
        titleb = QtGui.QPushButton("Title")
        titleb.setFocusPolicy(QtCore.Qt.NoFocus)
        titleb.setToolTip("Change plot title")
        titleb.clicked.connect(self._title_input)
        unitsb = QtGui.QPushButton("Units")
        unitsb.setFocusPolicy(QtCore.Qt.NoFocus)
        unitsb.setToolTip("Change units string")
        unitsb.clicked.connect(self._units_input)
        
#        tiltsb = QtGui.QPushButton("Tilt Select")
#        tiltsb.setToolTip("Choose tilt elevation angle")
#        tiltsb.clicked.connect(self._open_tiltbuttonwindow)
        
        
        self.tiltBox = QtGui.QComboBox()
        self.tiltBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tiltBox.setToolTip("Choose tilt elevation angle")
        self.tiltBox.activated[str].connect(self._tiltAction)
        #self._fillTiltBox() XXX will be done by newRadar
        
        self.fieldBox = QtGui.QComboBox()
        self.fieldBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fieldBox.setToolTip("Choose field")
        self.fieldBox.activated[str].connect(self._fieldAction)
        #self._fillFieldBox() XXX will be done by newRadar
        
        self.layout.addWidget(limsb, 0, 0)
#        self.layout.addWidget(self.toolsBox, 0, 1)
        self.layout.addWidget(titleb, 0, 2)
        self.layout.addWidget(unitsb, 0, 3)
        self.layout.addWidget(self.tiltBox, 0, 4)
        self.layout.addWidget(self.fieldBox, 0, 5)
        
    #############################
    # Functionality methods #
    #############################
    
    def _fillTiltBox(self):
        self.tiltBox.clear()
        self.tiltBox.addItem("Tilt Window")
        # Loop through and create each tilt button
        elevs = self.Vradar.value.fixed_angle['data'][:]
        for ntilt in self.rTilts:
            btntxt = "%2.1f deg (Tilt %d)"%(elevs[ntilt], ntilt+1)
            self.tiltBox.addItem(btntxt)
    
    def _fillFieldBox(self):
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

    def _tiltAction(self,text):
        if text == "Tilt Window":
            self._open_tiltbuttonwindow()
        else:
            ntilt=int(text.split("(Tilt ")[1][:-1])-1
            self.TiltSelectCmd(ntilt)

    def _fieldAction(self,text):
        if text == "Field Window":
            self._open_fieldbuttonwindow()
        else:
            self.FieldSelectCmd(str(text))

    def _title_input(self):
        '''Retrieve new plot title'''
        if self.title is None:
            old_val = ''
        else:
            old_val = self.title
        val, entry = QtGui.QInputDialog.getText(self, "Plot Title", \
                  "Title:", 0, old_val)
        if entry is True:
            self.title = val
            self._update_plot()

    def _units_input(self):
        '''Retrieve new plot units'''
        if self.units is None:
            old_val = ''
        else:
            old_val = self.units
        val, entry = QtGui.QInputDialog.getText(self, "Plot Units", \
                  "Units:", 0, old_val)
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
        
    ########################
    # Selectionion methods #
    ########################

    def NewRadar(self,variable,value):
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

    def NewField(self,variable,value):
        self._initialize_limits()
        self.units = None
        idx = self.fieldBox.findText(value)
        self.fieldBox.setCurrentIndex(idx)
        self._update_plot()
    
    def NewTilt(self,variable,value):
        self.tiltBox.setCurrentIndex(value+1)  # +1 since the first one is "Tilt Window"
        self._update_plot()


    def TiltSelectCmd(self, ntilt):
        '''Captures a selection and redraws the field with new tilt'''
        self.Vtilt.change(ntilt)
        #XXX tilt is changed and signal sended, so this and other classes do what they need to do


    def FieldSelectCmd(self, nombre):
        '''Captures a selection and redraws the new field'''
        self.Vfield.change(nombre)


    def RngRingSelectCmd(self, ringSel):
        '''Captures selection and redraws the field with range rings'''
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
        '''Captures selection of new cmap and redraws'''
        self.CMAP = cm_name
        self._update_plot()
        
        
    ####################
    # Plotting methods #
    ####################

    def _set_fig_ax(self, nrows=1, ncols=1):
        '''Set the figure and axis to plot to'''
        self.fig = Figure(figsize=(self.XSIZE, self.YSIZE))
        xwidth = 0.7
        yheight = 0.7 * float(self.YSIZE)/float(self.XSIZE)
        self.ax = self.fig.add_axes([0.2, 0.2, xwidth, yheight])
        self.cax = self.fig.add_axes([0.2,0.10, xwidth, 0.02])
        
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)
        
    def _set_fig_ax_rhi(self):
        '''Change figure size and limits if RHI'''
        if self.rhi:
            self.XSIZE = RHI_XSIZE
            self.YSIZE = RHI_YSIZE
            self.limits['ymin'] = RHI_YRNG[0]
            self.limits['ymax'] = RHI_YRNG[1]
        if self.airborne:
            self.XSIZE = AIR_XSIZE
            self.YSIZE = AIR_YSIZE
            self.limits['xmin'] = AIR_XRNG[0]
            self.limits['xmax'] = AIR_XRNG[1]
            self.limits['ymin'] = AIR_YRNG[0]
            self.limits['ymax'] = AIR_YRNG[1]
        self.fig.set_size_inches(self.XSIZE, self.YSIZE)
        self._set_fig_ax()

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area'''
        self.canvas = FigureCanvasQTAgg(self.fig)
        # Add the widget to the canvas
        self.layout.addWidget(self.canvas, 1, 0, 7, 6)

    def _update_plot(self):
        '''Renew the plot'''
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
        if self.ToolSelect == "Zoom/Pan":
            scale = 1.1
            self.zp = ZoomPan(self.ax, self.limits, base_scale = scale)
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
    # Get and check methods #
    #########################
    def _initialize_limits(self):
        field = self.Vfield.value
        if field == 'reflectivity':
            self.vminmax = (Z_LIMS[0], Z_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif field == 'DBZ' or field == 'DBZH':
            self.vminmax = (Z_LIMS[0], Z_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif field == 'velocity':
            self.vminmax = (VR_LIMS[0], VR_LIMS[1])
            self.CMAP = 'RdBu_r'
        elif field == 'VEL':
            self.vminmax = (VR_LIMS[0], VR_LIMS[1])
            self.CMAP = 'RdBu_r'
        elif field == 'differential_reflectivity':
            self.vminmax = (ZDR_LIMS[0], ZDR_LIMS[1])
            self.CMAP = 'RdYlBu_r'
        elif field == 'cross_correlation_ratio':
            self.vminmax = (RHO_HV_LIMS[0], RHO_HV_LIMS[1])
            self.CMAP = 'cool'
        elif field == 'differential_phase':
            self.vminmax = (KDP_LIMS[0], KDP_LIMS[1])
            self.CMAP = 'YlOrBr'
        elif field == 'normalized_coherent_power':
            self.vminmax = (NCP_LIMS[0], NCP_LIMS[1])
            self.CMAP = 'jet'
        elif field == 'spectrum_width':
            self.vminmax = (SW_LIMS[0], SW_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif field == 'specific_differential_phase':
            self.vminmax = (PHIDP_LIMS[0], PHIDP_LIMS[1]) 
            self.CMAP = 'RdBu_r'
        elif field == 'total_power':
            self.vminmax = (TP_LIMS[0], TP_LIMS[1])
            self.CMAP = 'jet'
           
        limit_strs = ('vmin', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax')
        self.limits = {}
        
        # Now pull the default values
        self.limits['vmin'] = self.vminmax[0]
        self.limits['vmax'] = self.vminmax[1]
        self.limits['xmin'] = self.XRNG[0]
        self.limits['xmax'] = self.XRNG[1]
        self.limits['ymin'] = self.YRNG[0]
        self.limits['ymax'] = self.YRNG[1]
        
# #    def _build_cmap_dict(self):
# #        self.cmap_dict = {}
# #        self.cmap_dict['gist_ncar'] = matcm.get_cmap(name='gist_ncar')
# #        self.cmap_dict['RdBu_r'] = matcm.get_cmap(name='RdBu_r')
# #        self.cmap_dict['RdYlBu_r'] = matcm.get_cmap(name='RdYlBu_r
# #        self.cmap_dict['cool'] = matcm.get_cmap(name='cool
# #        self.cmap_dict['YlOrBr'] = matcm.get_cmap(name='YlOrBr
# #        self.cmap_dict['jet'] = matcm.get_cmap(name='jet
# #        self.cmap_dict['
# #        self.cmap_dict['
        
    def _check_default_field(self):
        '''Hack to perform a check on reflectivity to make it work with 
        a larger number of files
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
            elif 'DBZ_S'in self.fieldnames:
                self.Vfield.change('DBZ_S')
            elif 'reflectivity_horizontal'in self.fieldnames:
                self.Vfield.change('reflectivity_horizontal')

                
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
    # Warning methods #
    ########################
    def _ShowWarning(self, msg):
        '''Show a warning message'''
        flags = QtGui.QMessageBox.StandardButton()
        response = QtGui.QMessageBox.warning(self, "Warning!",
                                             msg, flags)
        if response == 0:
            print msg
        else:
            print "Warning Discarded!"
 
    ########################
    # Image save methods #
    ########################
    def _quick_savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display'''
        PNAME = self.display.generate_filename(self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        print "Creating "+ PNAME
        
    def _savefile(self, PTYPE=IMAGE_EXT):
        PBNAME = self.display.generate_filename(self.Vfield.value, self.Vtilt.value, ext=IMAGE_EXT)
        file_choices = "PNG (*.png)|*.png"
        path = unicode(QtGui.QFileDialog.getSaveFileName(self, 'Save file', '', file_choices))
        if path:
            self.canvas.print_figure(path, dpi=DPI)
            self.statusBar().showMessage('Saved to %s' % path)

###############################
# Limits Dialog Class Methods #
###############################
class Ui_LimsDialog(object):
    '''
    Limits Dialog Class
    Popup window to set various limits
    ''' 
    def __init__(self, LimsDialog, mainLimits):
        self.LimsDialog = LimsDialog
        self.mainLimits = mainLimits
    
    def setupUi(self):
        # Set aspects of Dialog Window
        self.LimsDialog.setObjectName("Limits Dialog")
        self.LimsDialog.setWindowModality(QtCore.Qt.WindowModal)
        self.LimsDialog.setWindowTitle("Limits Entry")
        
        # Setup window layout
        self.gridLayout_2 = QtGui.QGridLayout(self.LimsDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
	
        # Set up the Labels for entry
        self.lab_dmin = QtGui.QLabel("Data Min")
        self.lab_dmax = QtGui.QLabel("Data Max")
        self.lab_xmin = QtGui.QLabel("X Min")
        self.lab_xmax = QtGui.QLabel("X Max")
        self.lab_ymin = QtGui.QLabel("Y Min")
        self.lab_ymax = QtGui.QLabel("Y Max")
	
        # Set up the Entry fields
        self.ent_dmin = QtGui.QLineEdit(self.LimsDialog)
        self.ent_dmax = QtGui.QLineEdit(self.LimsDialog)
        self.ent_xmin = QtGui.QLineEdit(self.LimsDialog)
        self.ent_xmax = QtGui.QLineEdit(self.LimsDialog)
        self.ent_ymin = QtGui.QLineEdit(self.LimsDialog)
        self.ent_ymax = QtGui.QLineEdit(self.LimsDialog)
        
        # Input the current values
        self.ent_dmin.setText(str(self.mainLimits['vmin']))
        self.ent_dmax.setText(str(self.mainLimits['vmax']))
        self.ent_xmin.setText(str(self.mainLimits['xmin']))
        self.ent_xmax.setText(str(self.mainLimits['xmax']))
        self.ent_ymin.setText(str(self.mainLimits['ymin']))
        self.ent_ymax.setText(str(self.mainLimits['ymax']))
	
        # Add to the layout
        self.gridLayout.addWidget(self.lab_dmin, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_dmin, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_dmax, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_dmax, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_xmin, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_xmin, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_xmax, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_xmax, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_ymin, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_ymin, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_ymax, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_ymax, 5, 1, 1, 1)
	
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.LimsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        # Connect the signals from OK and Cancel buttons
        self.buttonBox.accepted.connect(self._pass_lims)
        self.buttonBox.rejected.connect(self.LimsDialog.reject)
	
    def _pass_lims(self):
        entry = {}
        entry['dmin'] = float(self.ent_dmin.text())
        entry['dmax'] = float(self.ent_dmax.text())
        entry['xmin'] = float(self.ent_xmin.text())
        entry['xmax'] = float(self.ent_xmax.text())
        entry['ymin'] = float(self.ent_ymin.text())
        entry['ymax'] = float(self.ent_ymax.text())
	
        Browse._lims_input(main, entry)
        self.LimsDialog.accept()
        
##########################
# Zoom/Pan Class Methods #
##########################
class ZoomPan:
    '''
    Class for Zoom and Pan of plot
    Modified an original answer found here: http://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel
    '''
    def __init__(self, ax, limits, base_scale = 2.):
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
        self.entry['xmin'] = xdata - new_width * (1-relx)
        self.entry['xmax'] = xdata + new_width * (relx)
        self.entry['ymin'] = ydata - new_height * (1-rely)
        self.entry['ymax'] = ydata + new_height * (rely)
	
        # Send the new limits back to the main window
        Browse._lims_input(main, self.entry)
        
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
        self.entry['xmin'], self.entry['xmax'] = self.cur_xlim[0], self.cur_xlim[1]
        self.entry['ymin'], self.entry['ymax'] = self.cur_ylim[0], self.cur_ylim[1]
	
        # Send the new limits back to the main window
        Browse._lims_input(main, self.entry)
    
    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.scrollID)
        self.fig.canvas.mpl_disconnect(self.pressID)
        self.fig.canvas.mpl_disconnect(self.releaseID)
        self.fig.canvas.mpl_disconnect(self.motionID)

