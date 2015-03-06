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

History::
-------
30 Sep 2014  -  Created
30 Oct 2014  -  Various updates over the last month.
                Improved performance.
19 Feb 2015  -  Replaced Tk GUI backend with Qt GUI backend.
                Minor bug fixes.

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

#from PySide import QtGui
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

VERSION = '0.1.3'
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
                        
        # Launch the GUI interface
        self.LaunchGUI()       
                
        # Show an "Open" dialog box and return the path to the selected file
        self.showDialog()
        
        self.central_widget.setLayout(self.layout)
   
        self.show()
        
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
            #QtGui.QMainWindow.keyPressEvent(self, event)

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
                 
        datminb = QtGui.QPushButton("Data Min")
        datminb.clicked.connect(self._data_min_input)
        datmaxb = QtGui.QPushButton("Data Max")
        datmaxb.clicked.connect(self._data_max_input)
        xminb = QtGui.QPushButton("X Min")
        xminb.clicked.connect(self._x_min_input)
        xmaxb = QtGui.QPushButton("X Max")
        xmaxb.clicked.connect(self._x_max_input)
        yminb = QtGui.QPushButton("Y Min")
        yminb.clicked.connect(self._y_min_input)
        ymaxb = QtGui.QPushButton("Y Max")
        ymaxb.clicked.connect(self._y_max_input)
        titleb = QtGui.QPushButton("Title")
        titleb.clicked.connect(self._title_input)
        unitsb = QtGui.QPushButton("Units")
        unitsb.clicked.connect(self._units_input)
        
        # Create layout
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(8)
        
        self.layout.addWidget(datminb, 0, 0)
        self.layout.addWidget(datmaxb, 0, 1)
        self.layout.addWidget(xminb, 0, 2)
        self.layout.addWidget(xmaxb, 0, 3)
        self.layout.addWidget(yminb, 0, 4)
        self.layout.addWidget(ymaxb, 0, 5)
        self.layout.addWidget(titleb, 0, 6)
        self.layout.addWidget(unitsb, 0, 7)

        self.CreateTiltWidget()
                
    def showDialog(self):
        '''Open a dialog box to choose file'''    
        self.qfilename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                self.dirIn)
        self.filename = str(self.qfilename)
        self._openfile()
        
    def LaunchTiltButton(self):
        if self.windowTilt is None:
            self.windowTilt = TiltButtons(tilts=self.rTilts)
        self.windowTilt.show()
        
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
        openFile.triggered.connect(self.showDialog)
                
        saveImage = QtGui.QAction('Save Image', self)  
        saveImage.setShortcut('Ctrl+S')
        saveImage.setStatusTip('Save Image')
        saveImage.triggered.connect(self._savefile)
                
        exitApp = QtGui.QAction('Close', self)  
        exitApp.setShortcut('Ctrl+Q')
        exitApp.setStatusTip('Exit ARTView')
        exitApp.triggered.connect(self.close)
        
        self.filemenu.addAction(openFile)
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
        
    def _data_min_input(self):
        '''Retrieve new data lim input'''
        val, entry = QtGui.QInputDialog.getDouble(self, "Minimum data value to display", \
                  "Data Min:", self.limits['vmin'])
        if entry is True:
            self.limits['vmin'] = val
            self._update_plot()
            
    def _data_max_input(self):
        '''Retrieve new data lim input'''
        val, entry = QtGui.QInputDialog.getDouble(self, "Maximum data value to display", \
                  "Data Max:", self.limits['vmax'])
        if entry is True:
            self.limits['vmax'] = val
            self._update_plot()
        
    def _x_min_input(self):
        '''Retrieve new data lim input'''
        val, entry = QtGui.QInputDialog.getDouble(self, "Minimum X-axis value", \
                  "X Min:", self.limits['xmin'])
        if entry is True:
            self.limits['xmin'] = val
            self._update_plot()
            
    def _x_max_input(self):
        '''Retrieve new data lim input'''
        val, entry = QtGui.QInputDialog.getDouble(self, "Maximum X-axis value", \
                  "X Max:", self.limits['xmax'])
        if entry is True:
            self.limits['xmax'] = val
            self._update_plot()
        
    def _y_min_input(self):
        '''Retrieve new data lim input'''
        val, entry = QtGui.QInputDialog.getDouble(self, "Minimum Y-axis value", \
                  "Y Min:", self.limits['ymin'])
        if entry is True:
            self.limits['ymin'] = val
            self._update_plot()
            
    def _y_max_input(self):
        '''Retrieve new data lim input'''
        val, entry = QtGui.QInputDialog.getDouble(self, "Maximum Y-axis value", \
                  "Y Max:", self.limits['ymax'])
        if entry is True:
            self.limits['ymax'] = val
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

    def _openLimsDialog(self):
        '''Make Entry boxes to modify variable and axis limits'''
        dialog = QtGui.QDialog(self)
        dialog.ui = QtGui.Ui_Dialog_popup()
        dialog.ui.setupUi(dialog)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.show()
        
        text1, ent1 = QtGui.QInputDialog.getText(self, "Limits Adjustment", \
                      "Data Min:")
        
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
#                 self._remove_tilt_radiobutton()

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

        #Reset to default title if user entered nothing w/ Title button
        if self.title == '':
            self.title = None
        
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

#        self.update()
 
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
    # Popup methods #
    ########################
    def _ShowWarning(self, msg):
        '''Show a warning message'''
        flags = QtGui.QMessageBox.StandardButton()
#        flags |= QtGui.QMessageBox.StandardButton()
        response = QtGui.QMessageBox.warning(self, "Warning!",
                                             msg, flags)
        if response == 0:
            print msg
        else:
            print "Warning Discarded!"
 
     ########################
     # Image save methods #
     ########################

    def _savefile(self, PTYPE=IMAGE_EXT):
        '''Save the current display'''
        PNAME = self.display.generate_filename(self.field, self.tilt, ext=IMAGE_EXT)
        print "Creating "+ PNAME

        self.canvas.print_figure(PNAME, dpi=DPI)
#        self.fig.savefig(PNAME)
           
###################################
if __name__ == '__main__':
    # Check for directory
    
    parser = argparse.ArgumentParser(
              description="Start ARTview - the ARM Radar Toolkit Viewer.")
    parser.add_argument('searchstring', type=str, help='directory to open')
 
    igroup = parser.add_argument_group(
             title="Set input platform, optional",
             description=(""
                          "The ingest method for various platfoms can be chosen. "
                          "If not chosen, an assumption of a ground-based "
                          "platform is made. "
                          "The following flags may be used to  display" 
                          "RHI or airborne sweep data."
                          " "))
  
    igroup.add_argument('--airborne', action='store_true',
                          help='Airborne radar file')
                          
    igroup.add_argument('--rhi', action='store_true',
                          help='RHI scan')
 
    parser.add_argument('-v', '--version', action='version',
                         version='ARTview version %s' % (VERSION))
    
    # Parse the args                     
    args = parser.parse_args()
    
    # Check if there is an input directory
    if args.searchstring:
        fDirIn = args.searchstring
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
    