"""
menu.py - Class to create menu for ARTView app
"""
import numpy as np
import pyart

import os
from PyQt4 import QtGui, QtCore

class Menu(QtGui.QMainWindow):
    '''Class to display the MainMenu'''

    def __init__(self, Vradar, pathDir, name="Menu", parent=None):
        '''Initialize the class to create the interface'''
        super(Menu, self).__init__(parent)
        self.name = name
        self.parent = parent
        self.setWindowTitle(name)
        
        # Set some parameters
        self.dirIn = pathDir
        self.Vradar = Vradar
        
        # Launch the GUI interface
        self.LaunchApp()      
                
        # Show an "Open" dialog box and return the path to the selected file
        self.showFileDialog()
        
        self.show()
        
    # Allow advancement via left and right arrow keys
    # and tilt adjustment via the Up-Down arrow keys
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Right:
            self.AdvanceFileSelect(self.fileindex + 1) #Menu control the file and open the radar
        elif event.key()==QtCore.Qt.Key_Left:
            self.AdvanceFileSelect(self.fileindex - 1) #Menu control the file and open the radar
        else:
            QtGui.QWidget.keyPressEvent(self, event)
            

    ####################
    # GUI methods #
    ####################

    def LaunchApp(self):
        '''Launches a GUI interface.'''
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
     
        # Create the menus
        self.CreateMenu()
        
        # Create layout
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(8)
                    
    def showFileDialog(self):
        '''Open a dialog box to choose file'''    
        self.qfilename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                self.dirIn)
        self.filename = str(self.qfilename)
        self._openfile()
        
    ######################
    # Menu build methods #
    ######################
 
    def CreateMenu(self):
        '''Create a selection menu'''
        self.menubar = self.menuBar()
        
        self.AddFileMenu()
        self.AddAboutMenu()
#        self.AddPlotMenu()
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
        #quicksaveImage.triggered.connect(self._quick_savefile) #XXX Turn off
                
        saveImage = QtGui.QAction('Save Image', self)  
        saveImage.setShortcut('Ctrl+S')
        saveImage.setStatusTip('Save Image using dialog')
        #saveImage.triggered.connect(self._savefile) #XXX Turn off
                
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
        self.tiltmenu = self.plotmenu.addMenu('Tilt')
        self.rngringmenu = self.plotmenu.addMenu('Set Range Rings')
        self.cmapmenu = self.plotmenu.addMenu('Colormap')

    def AddFileAdvanceMenu(self):
        '''Add an option to advance to next or previous file'''
        self.advancemenu = self.menubar.addMenu("Advance file")

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
        txOut = self.Vradar.value.info()
        print txOut
            
#        QtGui.QMessageBox.information(self, "Long Radar Info", str(txOut)) 
        QtGui.QMessageBox.information(self, "Long Radar Info", "See terminal window") 

    def _get_RadarShortInfo(self):
        '''Print out some basic info about the radar'''
        try:
            rname = self.Vradar.value.metadata['instrument_name']
        except:
            rname = "Info not available"
        try:
            rlon = str(self.Vradar.value.longitude['data'][0])
        except:
            rlon = "Info not available"
        try:
            rlat = str(self.Vradar.value.latitude['data'][0])
        except:
            rlat = "Info not available"
        try:
            ralt = str(self.Vradar.value.altitude['data'][0])
            raltu = self.Vradar.value.altitude['units'][0]
        except:
            ralt = "Info not available"
            raltu = " "
        try:
            maxr = str(self.Vradar.value.instrument_parameters['unambiguous_range']['data'][0])
            maxru = self.Vradar.value.instrument_parameters['unambiguous_range']['units'][0]
        except:
            maxr = "Info not available"
            maxru = " "
        try:
            nyq = str(self.Vradar.value.instrument_parameters['nyquist_velocity']['data'][0])
            nyqu = self.Vradar.value.instrument_parameters['nyquist_velocity']['units'][0]
        except:
            nyq =  "Info not available"
            nyqu = " "
        try:
            bwh = str(self.Vradar.value.instrument_parameters['radar_beam_width_h']['data'][0])
            bwhu = self.Vradar.value.instrument_parameters['radar_beam_width_h']['units'][0]
        except:
            bwh = "Info not available"
            bwhu = " "
        try:
            bwv = str(self.Vradar.value.instrument_parameters['radar_beam_width_v']['data'][0])
            bwvu = self.Vradar.value.instrument_parameters['radar_beam_width_v']['units'][0]
        except:
            bwv = "Info not available"
            bwvu = " "
        try:
            pw = str(self.Vradar.value.instrument_parameters['pulse_width']['data'][0])
            pwu = self.Vradar.value.instrument_parameters['pulse_width']['units'][0]
        except:
            pw = "Info not available"
            pwu = " "
        try:
            ngates = str(self.Vradar.value.ngates)
        except:
            ngates = "Info not available"
        try:
            nsweeps = str(self.Vradar.value.nsweeps)
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
        
    ########################
    # Selectionion methods #
    ########################
    
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
            radar = pyart.io.read(self.filename)
            self.Vradar.change(radar)
        except:
            msg = "This is not a recognized radar file"
            self._ShowWarning(msg)
            return

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

