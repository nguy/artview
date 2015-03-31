#! /usr/bin/env python
#******************************
#  artview.py - PyArt Radar Viewer using Qt Gui interface
#******************************
'''
ARTview - The ARM Radar Toolkit Viewer

Allow a graphical interface to be employed as a quick browse through 
a radar data file opened using the PyArt software package

Author::
------
Nick Guy - University of Wyoming
Timothy Lang - NASA Marshall Flight Center
Paul Hein - Colorado State University

History::
-------
30 Sep 2014  -  Created
30 Oct 2014  -  Various updates over the last month.
                Improved performance.
19 Feb 2015  -  Replaced Tk GUI backend with Qt GUI backend.
                Minor bug fixes.
10 Mar 2015  -  Title and Units adjustable by user.
23 Mar 2015  -  Zoom/Pan functionality added.  Condensed limits into a
                single popup dialog window.
                Added a Tools ComboBox to choose none, Zoom/Pan, or Default Scaling


Usage::
-----
artview.py /some/directory/path/to/look/in

TODO::
----
Improve error handling. May be some loose ends not supported yet...
File check for zipped files.
Add ability to reconfigure layout switching from scan types,
  i.e. PPI to RHI.


Speed up interaction.  

Possibly replace Data/Axes min/max dialog boxes with fields?

Use PyArt colormaps, currently only Matplotlib

KNOWN BUGS::
----------
Some crashes after some number of left and right keystrokes.
'''
#-------------------------------------------------------------------
# Load the needed packages
import numpy as np
import pyart

from glob import glob
import sys
import os
import argparse
from functools import partial

from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import Normalize as mlabNormalize
from matplotlib.colorbar import ColorbarBase as mlabColorbarBase
from matplotlib.pyplot import cm

#use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
#if use_pyside:
#    from PySide import QtGui, QtCore
#else:
#    from PyQt4 import QtGui, QtCore
#===============================================================
# Initialization defaults for variables

VERSION = '0.1.6'
MAINWINDOWTITLE = 'ARTView - ARM Radar Toolkit Viewer'

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

class Browse(QtGui.QMainWindow):
    '''Class to hold the GUI browse method'''

    def __init__(self, pathDir=None, airborne=False, rhi=False):
        '''Initialize the class to create the interface'''
        super(Browse, self).__init__()
        
        # Set some parameters
        self.dirIn = pathDir
        
        # Default field and tilt angle to plot
        self.field = 'reflectivity'
        self.tilt = 0
    
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
        self.ToolSelect = "No Tools"
                        
        # Launch the GUI interface
        self.LaunchGUI()      
                
        # Show an "Open" dialog box and return the path to the selected file
        self.showFileDialog()
        
        self.central_widget.setLayout(self.layout)
   
        self.show()
        
        self.pickPoint = self.fig.canvas.mpl_connect('button_press_event', self.onPick)
        
    # Allow advancement via left and right arrow keys
    # and tilt adjustment via the Up-Down arrow keys
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Right:
            #self.slider.setValue(self.slider.value() + 1)
            self.AdvanceFileSelect(self.fileindex + 1)
        elif event.key()==QtCore.Qt.Key_Left:
            #self.slider.setValue(self.slider.value() - 1)
            self.AdvanceFileSelect(self.fileindex - 1)
        elif event.key()==QtCore.Qt.Key_Up:
            #self.slider.setValue(self.slider.value() - 1)
            self.TiltSelectCmd(self.tilt + 1)
        elif event.key()==QtCore.Qt.Key_Down:
            #self.slider.setValue(self.slider.value() - 1)
            self.TiltSelectCmd(self.tilt - 1)
        else:
            QtGui.QWidget.keyPressEvent(self, event)
            
    def onPick(self, event):
        '''Get value at the point selected by mouse click'''
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        az = np.arctan2(xdata, ydata)*180./np.pi
        if az < 0:
            az = az + 360.
        rng = np.sqrt(xdata*xdata+ydata*ydata)
        azindex = np.argmin(np.abs(self.radar.azimuth['data'][self.radar.sweep_start_ray_index['data'][self.tilt]:self.radar.sweep_end_ray_index['data'][self.tilt]]-az))+self.radar.sweep_start_ray_index['data'][self.tilt]
        rngindex = np.argmin(np.abs(self.radar.range['data']-rng*1000.))
        msg = 'x = %4.2f, y = %4.2f, Azimuth = %4.2f deg., Range = %4.2f km, %s = %4.2f %s'\
        %(xdata, ydata, self.radar.azimuth['data'][azindex], self.radar.range['data'][rngindex]/1000., self.field, self.radar.fields[self.field]['data'][azindex][rngindex], self.units)
        self.statusBar().showMessage(msg)

    ####################
    # GUI methods #
    ####################

    def LaunchGUI(self):
        '''Launches a GUI interface.'''
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
     
        # Initiate a counter, used so that Tilt and Field menus are 
        # not increased every time there is a selection
        # Might be a more elegant way
        self.counter = 0

        # Create the widget
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.statusBar()
        
        # Create the menus
        self.CreateMenu()
        
        # Create the button controls
        limsb = QtGui.QPushButton("Adjust Limits")
        limsb.setToolTip("Set data, X, and Y range limits")
        limsb.clicked.connect(self.showLimsDialog)
        titleb = QtGui.QPushButton("Title")
        titleb.setToolTip("Change plot title")
        titleb.clicked.connect(self._title_input)
        unitsb = QtGui.QPushButton("Units")
        unitsb.setToolTip("Change units string")
        unitsb.clicked.connect(self._units_input)
        
        # Create the Tools ComboBox
        self.toolsBoxUI()
        
        # Create layout
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(8)
        
        self.layout.addWidget(limsb, 0, 0)
        self.layout.addWidget(self.toolsBox, 0, 1)
        self.layout.addWidget(titleb, 0, 2)
        self.layout.addWidget(unitsb, 0, 3)

        # Create the Tilt buttons
        self.CreateTiltWidget()
                
    def showFileDialog(self):
        '''Open a dialog box to choose file'''    
        self.qfilename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                self.dirIn)
        self.filename = str(self.qfilename)
        self._openfile()
        
    def showLimsDialog(self):
        self.limsDialog = QtGui.QDialog()
        u = Ui_LimsDialog(self.limsDialog, self.limits)
        u.setupUi()#self.limsDialog, self.limits

        self.limsDialog.exec_()
        
    def LaunchTiltButton(self):
        if self.windowTilt is None:
            self.windowTilt = TiltButtons(tilts=self.rTilts)
        self.windowTilt.show()
            
    def toolsBoxUI(self):
        self.toolsBox = QtGui.QComboBox()
        self.toolsBox.setToolTip("Choose a tool to apply")
        self.toolsBox.addItem("No Tools")
        self.toolsBox.addItem("Zoom/Pan")
        self.toolsBox.addItem("Reset file defaults")
        
        self.toolsBox.activated[str].connect(self.comboAction)
        
    def comboAction(self, text):
        # Check to see if Zoom/Pan was selected, if so disconnect 
        if self.ToolSelect == "Zoom/Pan":
            print "IN DISCONNECT"
            self.zp.disconnect()
        # Set the Tool to use
        self.ToolSelect = text
        
        if self.ToolSelect == "Reset file defaults":
            self._initialize_limits()
        self._update_plot()
        
    ######################
    # Help methods #
    ######################

    def _about(self):
        txOut = "This is a simple radar file browser to allow \
                 quicklooks using the DoE PyArt software"
        QtGui.QMessageBox.about(self, "About ARTView", txOut)
 
    def _get_RadarLongInfo(self):
        '''Print out the radar info to text box'''
 
        # Get the radar info form rada object and print it
        txOut = self.radar.info()
        print txOut
            
#        QtGui.QMessageBox.information(self, "Long Radar Info", str(txOut)) 
        QtGui.QMessageBox.information(self, "Long Radar Info", "See terminal window") 

    def _get_RadarShortInfo(self):
        '''Print out some basic info about the radar'''
        try:
            rname = self.radar.metadata['instrument_name']
        except:
            rname = "Info not available"
        try:
            rlon = str(self.radar.longitude['data'][0])
        except:
            rlon = "Info not available"
        try:
            rlat = str(self.radar.latitude['data'][0])
        except:
            rlat = "Info not available"
        try:
            ralt = str(self.radar.altitude['data'][0])
            raltu = self.radar.altitude['units'][0]
        except:
            ralt = "Info not available"
        try:
            maxr = str(self.radar.instrument_parameters['unambiguous_range']['data'][0])
            maxru = self.radar.instrument_parameters['unambiguous_range']['units'][0]
        except:
            maxr = "Info not available"
            maxru = " "
        try:
            nyq = str(self.radar.instrument_parameters['nyquist_velocity']['data'][0])
            nyqu = self.radar.instrument_parameters['nyquist_velocity']['units'][0]
        except:
            nyq =  "Info not available"
            nyqu = " "
        try:
            bwh = str(self.radar.instrument_parameters['radar_beam_width_h']['data'][0])
            bwhu = self.radar.instrument_parameters['radar_beam_width_h']['units'][0]
        except:
            bwh = "Info not available"
            bwhu = " "
        try:
            bwv = str(self.radar.instrument_parameters['radar_beam_width_v']['data'][0])
            bwvu = self.radar.instrument_parameters['radar_beam_width_v']['units'][0]
        except:
            bwv = "Info not available"
            bwvu = " "
        try:
            pw = str(self.radar.instrument_parameters['pulse_width']['data'][0])
            pwu = self.radar.instrument_parameters['pulse_width']['units'][0]
        except:
            pw = "Info not available"
            pwu = " "
        try:
            ngates = str(self.radar.ngates)
        except:
            ngates = "Info not available"
        try:
            nsweeps = str(self.radar.nsweeps)
        except:
            nsweeps = "Info not available"
        
        txOut = (('Radar Name: %s\n'% rname) +\
        ('Radar longitude: %s\n'% rlon) + \
        ('Radar latitude: %s\n'% rlat) + \
        ('Radar altitude: %s %s\n'% (ralt, raltu)) + \
        ('    \n') + \
        ('Unambiguous range: %s %s\n'% (maxr, maxru)) + \
        ('Nyquist velocity: %s %s\n'% (nyq, nyqu)) + \
        ('    \n') + \
        ('Radar Beamwidth, horiz: %s %s\n'% (bwh, bwhu)) + \
        ('Radar Beamwidth, vert: %s %s\n'% (bwv, bwvu)) + \
        ('Pulsewidth: %s %s \n'% (pw, pwu)) + \
        ('    \n') + \
        ('Number of gates: %s\n'% ngates) + \
        ('Number of sweeps: %s\n'% nsweeps))
        
        QtGui.QMessageBox.information(self, "Short Radar Info", txOut) 
        
    ######################
    # Menu build methods #
    ######################
 
    def CreateMenu(self):
        '''Create a selection menu'''
        self.menubar = self.menuBar()
        
        self.AddFileMenu()
        self.AddAboutMenu()
        self.AddPlotMenu()
        self.AddFileAdvanceMenu()
        

    def AddFileMenu(self):
        self.filemenu = self.menubar.addMenu('&File')
               
        openFile = QtGui.QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showFileDialog)
        
        quicksaveImage = QtGui.QAction('Quick Save Image', self)  
        quicksaveImage.setShortcut('Ctrl+D')
        quicksaveImage.setStatusTip('Save Image to local directory with default name')
        quicksaveImage.triggered.connect(self._quick_savefile)
                
        saveImage = QtGui.QAction('Save Image', self)  
        saveImage.setShortcut('Ctrl+S')
        saveImage.setStatusTip('Save Image using dialog')
        saveImage.triggered.connect(self._savefile)
                
        exitApp = QtGui.QAction('Close', self)  
        exitApp.setShortcut('Ctrl+Q')
        exitApp.setStatusTip('Exit ARTView')
        exitApp.triggered.connect(self.close)
        
        self.filemenu.addAction(openFile)
        self.filemenu.addAction(quicksaveImage)
        self.filemenu.addAction(saveImage)
        self.filemenu.addAction(exitApp)
        
    def AddAboutMenu(self):
        '''Add Help item to menu bar'''
        self.aboutmenu = self.menubar.addMenu('About')

        self._aboutArtview = QtGui.QAction('ARTView', self)
        self._aboutArtview.setStatusTip('About ARTView')
        self._aboutArtview.triggered.connect(self._about)
        
        self.RadarShort = QtGui.QAction('Radar Short', self)
        self.RadarShort.setStatusTip('Print Short Radar Structure Info')
        self.RadarShort.triggered.connect(self._get_RadarShortInfo)
        
        self.RadarLong = QtGui.QAction('Radar Long', self)
        self.RadarLong.setStatusTip('Print Long Radar Structure Info')
        self.RadarLong.triggered.connect(self._get_RadarLongInfo)
        
        self.aboutmenu.addAction(self._aboutArtview)
        self.aboutmenu.addAction(self.RadarShort)
        self.aboutmenu.addAction(self.RadarLong)
        
 
    def AddPlotMenu(self):
        '''Add Plot item to menu bar'''
        self.plotmenu = self.menubar.addMenu('&Plot')
        
        # Add submenus
        self.fieldmenu = self.plotmenu.addMenu('Field')
        if self.airborne or self.rhi:
            pass
        else:
            self.tiltmenu = self.plotmenu.addMenu('Tilt')
            self.rngringmenu = self.plotmenu.addMenu('Set Range Rings')
        self.cmapmenu = self.plotmenu.addMenu('Colormap')


    def AddFileAdvanceMenu(self):
        '''Add an option to advance to next or previous file'''
        self.advancemenu = self.menubar.addMenu("Advance file")

    def AddTiltMenu(self):
        '''Add a menu to change tilt angles of current plot'''
        for ntilt in self.rTilts:
            TiltAction = self.tiltmenu.addAction("Tilt %d"%(ntilt+1))
            TiltAction.triggered[()].connect(lambda ntilt=ntilt: self.TiltSelectCmd(ntilt))

    def AddFieldMenu(self):
        '''Add a menu to change current plot field'''
        for nombre in self.fieldnames:
            FieldAction = self.fieldmenu.addAction(nombre)
            FieldAction.triggered[()].connect(lambda nombre=nombre: self.FieldSelectCmd(nombre))
            
    def AddRngRingMenu(self):
        '''Add a menu to set range rings'''
        for RngRing in self.RngRingList:
            RingAction = self.rngringmenu.addAction(RngRing)
            RingAction.triggered[()].connect(lambda RngRing=RngRing: self.RngRingSelectCmd(RngRing))
    
    def AddNextPrevMenu(self):
        '''Add an option to advance to next or previous file'''
        nextAction = self.advancemenu.addAction("Next")
        nextAction.triggered[()].connect(lambda findex=self.fileindex + 1: self.AdvanceFileSelect(findex))
        
        prevAction = self.advancemenu.addAction("Previous")
        prevAction.triggered[()].connect(lambda findex=self.fileindex - 1: self.AdvanceFileSelect(findex))
        
        firstAction = self.advancemenu.addAction("First")
        firstAction.triggered[()].connect(lambda findex=0: self.AdvanceFileSelect(findex))
        
        lastAction = self.advancemenu.addAction("Last")
        lastAction.triggered[()].connect(lambda findex=(len(self.filelist) - 1): self.AdvanceFileSelect(findex))
         
    def AddCmapMenu(self):
        '''Add a menu to change colormap used for plot'''
        for cm_name in self.cm_names:
            cmapAction = self.cmapmenu.addAction(cm_name)
            cmapAction.setStatusTip("Use the %s colormap"%cm_name)
            cmapAction.triggered[()].connect(lambda cm_name=cm_name: self.cmapSelectCmd(cm_name))
    
    ########################
    # Button methods #
    ########################

    def CreateTiltWidget(self):
        '''Create a widget to store radio buttons to control tilt adjust'''
        self.radioBox = QtGui.QGroupBox("Tilt Selection")
        self.rBox_layout = QtGui.QVBoxLayout(self.radioBox)
        
    def SetTiltRadioButtons(self):
        '''Set a tilt selection using radio buttons'''
        # Need to first create each tilt button and connect a value when selected
        for ntilt in self.rTilts:
            tiltbutton = QtGui.QRadioButton("Tilt %d"%(ntilt+1), self.radioBox)
            QtCore.QObject.connect(tiltbutton, QtCore.SIGNAL("clicked()"), \
                         partial(self.TiltSelectCmd, ntilt))

            self.rBox_layout.addWidget(tiltbutton)
		
        self.radioBox.setLayout(self.rBox_layout)
		
        return self.radioBox

    #############################
    # Limit entry methods #
    #############################
            
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
        
    ########################
    # Selectionion methods #
    ########################
    
    def TiltSelectCmd(self, ntilt):
        '''Captures a selection and redraws the field with new tilt'''
        print ntilt
        self.tilt = ntilt
        self._update_plot()

    def FieldSelectCmd(self, nombre):
        '''Captures a selection and redraws the new field'''
        self.field = nombre
        self._initialize_limits()
        self.units = None
        self._update_plot()
        
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
        
    def AdvanceFileSelect(self, findex):
        '''Captures a selection and redraws figure with new file'''
        if findex > len(self.filelist):
            print len(self.filelist)
            msg = "End of directory, cannot advance"
            self._ShowWarning(msg)
            findex = (len(self.filelist) - 1)
            return
        if findex < 0:
            msg = "Beginning of directory, must move forward"
            self._ShowWarning(msg)
            findex = 0
            return
        self.fileindex = findex
        self.filename = self.dirIn + "/" + self.filelist[findex]
        self._openfile()

    ########################
    # Menu display methods #
    ########################
 
    def _openfile(self):
        '''Open a file via a file selection window'''
        print "Opening file " + self.filename
        
        # Update to  current directory when file is chosen
        self.dirIn = os.path.dirname(self.filename)
        
        # Get a list of files in the working directory
        self.filelist = os.listdir(self.dirIn)
        
        self.fileindex = self.filelist.index(os.path.basename(self.filename))
     
        # Read the data from file
        try:
            self.radar = pyart.io.read(self.filename)
        except:
            msg = "This is not a recognized radar file"
            self._ShowWarning(msg)
            return
         
        # In case the flags were not used at startup
        # Check to see if this is an aircraft or rhi file
        if self.counter == 0:
            self._check_file_type()
            self._set_figure_canvas()

        # Increment counter to know whether to renew Tilt and field menus
        # If > 1 then remove the pre-existing menus before redrawing
        self.counter += 1
        
        if self.counter > 1:
            self.fieldmenu.clear()
            self.advancemenu.clear()
           
            if self.airborne or self.rhi:
                pass
            else:
                self.tiltmenu.clear()
                self.rngringmenu.clear()
                self.radioBox.deleteLater()

        # Get the tilt angles
        self.rTilts = self.radar.sweep_number['data'][:]
        # Get field names
        self.fieldnames = self.radar.fields.keys()

        # Set up the menus associated with scanning ground radars
        if self.airborne or self.rhi:
            pass
        else:
            self.CreateTiltWidget()
            self.layout.addWidget(self.SetTiltRadioButtons(), 1, 6, 6, 1)
            self.AddRngRingMenu()
            self.AddTiltMenu()
        self.AddFieldMenu()
        self.AddNextPrevMenu()
        self.AddCmapMenu()
        self.units = None
        self.title = None
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
            self.display = pyart.graph.RadarDisplay_Airborne(self.radar)
            
            self.plot = self.display.plot_sweep_grid(self.field, \
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax, title=self.title)
            self.display.set_limits(xlim=(self.limits['xmin'], self.limits['xmax']),\
                                    ylim=(self.limits['ymin'], self.limits['ymax']),\
                                    ax=self.ax)
            self.display.plot_grid_lines()
        else:
            self.display = pyart.graph.RadarDisplay(self.radar)
            if self.radar.scan_type != 'rhi':
                # Create Plot
                if self.tilt < len(self.rTilts):
                    pass
                else:
                    self.tilt = 0
                self.plot = self.display.plot_ppi(self.field, self.tilt,\
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
                self.plot = self.display.plot_rhi(self.field, self.tilt,\
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
                self.units = self.radar.fields[self.field]['units']
            except:
                self.units = ''
        self.cbar.set_label(self.units)
        
        print "Plotting %s field, Tilt %d" % (self.field, self.tilt+1)
        self.canvas.draw()
 
    #########################
    # Get and check methods #
    #########################
    def _initialize_limits(self):
        if self.field == 'reflectivity':
            self.vminmax = (Z_LIMS[0], Z_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif self.field == 'DBZ':
            self.vminmax = (Z_LIMS[0], Z_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif self.field == 'velocity':
            self.vminmax = (VR_LIMS[0], VR_LIMS[1])
            self.CMAP = 'RdBu_r'
        elif self.field == 'VEL':
            self.vminmax = (VR_LIMS[0], VR_LIMS[1])
            self.CMAP = 'RdBu_r'
        elif self.field == 'differential_reflectivity':
            self.vminmax = (ZDR_LIMS[0], ZDR_LIMS[1])
            self.CMAP = 'RdYlBu_r'
        elif self.field == 'cross_correlation_ratio':
            self.vminmax = (RHO_HV_LIMS[0], RHO_HV_LIMS[1])
            self.CMAP = 'cool'
        elif self.field == 'differential_phase':
            self.vminmax = (KDP_LIMS[0], KDP_LIMS[1])
            self.CMAP = 'YlOrBr'
        elif self.field == 'normalized_coherent_power':
            self.vminmax = (NCP_LIMS[0], NCP_LIMS[1])
            self.CMAP = 'jet'
        elif self.field == 'spectrum_width':
            self.vminmax = (SW_LIMS[0], SW_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif self.field == 'specific_differential_phase':
            self.vminmax = (PHIDP_LIMS[0], PHIDP_LIMS[1]) 
            self.CMAP = 'RdBu_r'
        elif self.field == 'total_power':
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
        if self.field == 'reflectivity':
            if self.field in self.fieldnames:
                pass
            elif 'CZ' in self.fieldnames:
                self.field = 'CZ'
            elif 'DZ' in self.fieldnames:
                self.field = 'DZ'
            elif 'dbz' in self.fieldnames:
                self.field = 'dbz'
            elif 'DBZ' in self.fieldnames:
                self.field = 'DBZ'
            elif 'dBZ' in self.fieldnames:
                self.field = 'dBZ'
            elif 'Z' in self.fieldnames:
                self.field = 'Z'
            elif 'DBZ_S'in self.fieldnames:
                self.field = 'DBZ_S'
            elif 'reflectivity_horizontal'in self.fieldnames:
                self.field = 'reflectivity_horizontal'

                
    def _check_file_type(self):
        '''Check file to see if the file is airborne or rhi'''
        if self.radar.scan_type != 'rhi':
            pass
        else:
            try:
                (self.radar.metadata['platform_type'] == 'aircraft_tail') or \
                (self.radar.metadata['platform_type'] == 'aircraft')
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
        PNAME = self.display.generate_filename(self.field, self.tilt, ext=IMAGE_EXT)
        print "Creating "+ PNAME
        
    def _savefile(self, PTYPE=IMAGE_EXT):
        PBNAME = self.display.generate_filename(self.field, self.tilt, ext=IMAGE_EXT)
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
           
###################################
if __name__ == '__main__':
    # Check for directory
    
    parser = argparse.ArgumentParser(
              description="Start ARTview - the ARM Radar Toolkit Viewer.")
 
    igroup = parser.add_argument_group(
             title="Set input platform, optional",
             description=(""
                          "The ingest method for various platfoms can be chosen. "
                          "If not chosen, an assumption of a ground-based "
                          "platform is made. "
                          "The following flags may be used to display"
                          "RHI or airborne sweep data."
                          " "))
  
    igroup.add_argument('--airborne', action='store_true',
                          help='Airborne radar file')
                          
    igroup.add_argument('--rhi', action='store_true',
                          help='RHI scan')
 
    igroup.add_argument('-v', '--version', action='version',
                         version='ARTview version %s' % (VERSION))
    
    #Directory argument now optional
    igroup.add_argument('-d', '--directory', type=str, help='directory to open', default='./')
    
    # Parse the args
    args = parser.parse_args()
    # Check if there is an input directory
    if args.directory:
        fDirIn = args.directory
    else: 
        fDirIn = "./"
        
    # Set airborne flag off and change if airborne called
    airborne, rhi = False, False
    if args.airborne:
        airborne = True
    if args.rhi:
        rhi = True
    
    app = QtGui.QApplication(sys.argv)
    
    main = Browse(pathDir=fDirIn, airborne=airborne, rhi=rhi)
    
    main.setWindowTitle(MAINWINDOWTITLE)
    main.show()
 
    sys.exit(app.exec_())
    
