"""
menu.py

Class instance used to create menu for ARTView app.
"""
import numpy as np
import pyart

import os
from PyQt4 import QtGui, QtCore

from ..core import Variable, Component, common

class Menu(Component):
    '''Class to display the MainMenu'''

    def __init__(self, pathDir, filename=None, Vradar=None, Vgrid=None, mode="Radar", name="Menu", parent=None):
        '''
        Initialize the class to create the interface.

        Parameters
        ----------
        pathDir - string
            Input directory path to open.
        filename - string
            File to open as first, this will skip the open file dialog.
        [Optional]
        Vradar - Variable instance
            Radar signal variable. 
            A value of None initializes with this class.
        Vgrid - Variable instance
            Grid signal variable. 
            A value of None initializes with this class.
        mode - "Radar", "Grid" or "All"
            Determine witch files will be open
        name - string
            Menu name.
        parent - PyQt instance
            Parent instance to associate to menu.
            If None, then Qt owns, otherwise associated with parent PyQt instance.

        Notes
        -----
        This class creates the main application interface and creates
        a menubar for the program.
        '''
        super(Menu, self).__init__(name=name, parent=parent)

        # Set some parameters
        self.dirIn = pathDir
        self.mode = mode.lower()
        self.Vradar = Vradar
        self.Vgrid = Vgrid
        self.sharedVariables = {"Vradar": None,
                                "Vgrid": None}

        # Show an "Open" dialog box and return the path to the selected file
        # Just do that if Vradar was not given
        if self.Vradar is None:
            self.Vradar = Variable(None)
        if self.Vgrid is None:
            self.Vgrid = Variable(None)
        if Vradar is None and Vgrid is None:
            if filename is None:
                self.showFileDialog()
            else:
                self.filename = filename
                self._openfile()

        # Launch the GUI interface
        self.LaunchApp()
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

        # Create layout
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.centralLayout = QtGui.QVBoxLayout(self.central_widget)
        self.centralLayout.setSpacing(8)
        self.frames = {}

        # Create the menus
        self.CreateMenu()

    def showFileDialog(self):
        '''Open a dialog box to choose file.'''

        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                self.dirIn)
        filename = str(filename)
        if filename == '':
            return
        else:
            self.filename = filename
            self._openfile()

    def addLayoutWidget(self, widget):
        '''
        Add a widget to central layout.
        This function is to be called both internal and external
        '''
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.Box)
        layout = QtGui.QVBoxLayout(frame)
        layout.addWidget(widget)
        self.frames[widget.__repr__()] = frame
        self.centralLayout.addWidget(frame)
        self.addLayoutMenuItem(widget)


    def removeLayoutWidget(self, widget):
        '''Remove widget from central layout.'''
        frame = self.frames[widget.__repr__()]
        self.centralLayout.removeWidget(frame)
        self.removeLayoutMenuItem(widget)
        frame.close()
        widget.close()
        widget.deleteLater()

    def addComponent(self, Comp):
        '''Add Component Contructor.'''
        # first test the existence of a guiStart
        if not hasattr(Comp,'guiStart'):
            raise ValueError("Component has no guiStart Method")
            return
        self.addComponentMenuItem(Comp)

        
    ######################
    # Menu build methods #
    ######################
 
    def CreateMenu(self):
        '''Create the main menubar.'''
        self.menubar = self.menuBar()
        
        self.addFileMenu()
        self.addAboutMenu()
#        self.AddPlotMenu()
        self.addFileAdvanceMenu()
        self.addLayoutMenu()
        self.addComponentMenu()

    def addFileMenu(self):
        '''Add the File item to menubar.'''
        self.filemenu = self.menubar.addMenu('&File')
               
        openFile = QtGui.QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showFileDialog)
                
        exitApp = QtGui.QAction('Close', self)  
        exitApp.setShortcut('Ctrl+Q')
        exitApp.setStatusTip('Exit ARTView')
        exitApp.triggered.connect(self.close)
        
        self.filemenu.addAction(openFile)
        self.filemenu.addAction(exitApp)
        
    def addAboutMenu(self):
        '''Add Help item to menubar.'''
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
        
    def addPlotMenu(self):
        '''Add Plot item to menubar.'''
        self.plotmenu = self.menubar.addMenu('&Plot')
        
        # Add submenus
        self.fieldmenu = self.plotmenu.addMenu('Field')
        self.tiltmenu = self.plotmenu.addMenu('Tilt')
        self.rngringmenu = self.plotmenu.addMenu('Set Range Rings')
        self.cmapmenu = self.plotmenu.addMenu('Colormap')

    def addLayoutMenu(self):
        '''Add Layout item to menu bar.'''
        self.layoutmenu = self.menubar.addMenu('&Layout')
        self.layoutmenuItems = {}

    def addComponentMenu(self):
        '''Add Component item to menu bar.'''
        self.componentmenu = self.menubar.addMenu('&Components')

    def addLayoutMenuItem(self, widget):
        '''Add widget item to Layout Menu.'''
        if hasattr(widget,'name'):
            item = self.layoutmenu.addMenu(widget.name)
        else:
            item = self.layoutmenu.addMenu(widget.__str__())
        self.layoutmenuItems[widget.__repr__()] = item
        remove = item.addAction("remove")
        remove.triggered[()].connect(lambda widget=widget: self.removeLayoutWidget(widget))

    def removeLayoutMenuItem(self, widget):
        '''Remove widget item to Layout Menu.'''
        rep = widget.__repr__()
        if rep in self.layoutmenuItems:
            self.layoutmenuItems[rep].clear()
            self.layoutmenu.removeAction(self.layoutmenuItems[rep].menuAction())
            self.layoutmenuItems[rep].close()
            del self.layoutmenuItems[rep]

    def addComponentMenuItem(self, Comp):
        '''Add Component item to Component Menu.'''
        action = self.componentmenu.addAction(Comp.__name__)
        action.triggered[()].connect(lambda Comp=Comp: self.startComponent(Comp))

    def startComponent(self, Comp):
        '''GUI start a Component and add to layout.'''
        comp, independent = Comp.guiStart(self)
        if not independent:
            self.addLayoutWidget(comp)

    def addFileAdvanceMenu(self):
        '''Add an option to advance to next or previous file.'''
        self.advancemenu = self.menubar.addMenu("Advance file")
        nextAction = self.advancemenu.addAction("Next")
        nextAction.triggered[()].connect(lambda findex=self.fileindex + 1: self.AdvanceFileSelect(findex))

        prevAction = self.advancemenu.addAction("Previous")
        prevAction.triggered[()].connect(lambda findex=self.fileindex - 1: self.AdvanceFileSelect(findex))

        firstAction = self.advancemenu.addAction("First")
        firstAction.triggered[()].connect(lambda findex=0: self.AdvanceFileSelect(findex))

        lastAction = self.advancemenu.addAction("Last")
        lastAction.triggered[()].connect(lambda findex=(len(self.filelist) - 1): self.AdvanceFileSelect(findex))

    ######################
    # Help methods #
    ######################

    def _about(self):
        # Add a more extensive about eventually
        txOut = "This is a simple radar file browser to allow \
                 quicklooks using the DoE PyArt software"
        QtGui.QMessageBox.about(self, "About ARTView", txOut)

    def _get_RadarLongInfo(self):
        '''Print out the radar info to text box and terminal.'''
        # Get the radar info form rada object and print it
        txOut = self.Vradar.value.info()
        common.ShowLongText(txOut, modal=False)
        
        print txOut
#        QtGui.QMessageBox.information(self, "Long Radar Info", "See terminal window") 

    def _get_RadarShortInfo(self):
        '''Print out some basic info about the radar.'''
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
        '''Captures a selection and redraws figure with new file.'''
        if findex > (len(self.filelist)-1):
            print len(self.filelist)
            msg = "End of directory, cannot advance!"
            common.ShowWarning(msg)
            findex = (len(self.filelist) - 1)
            return
        if findex < 0:
            msg = "Beginning of directory, must move forward!"
            common.ShowWarning(msg)
            findex = 0
            return
        self.fileindex = findex
        self.filename = self.dirIn + "/" + self.filelist[findex]
        self._openfile()

    ########################
    # Menu display methods #
    ########################

    def _openfile(self):
        '''Open a file via a file selection window.'''
        print "Opening file " + self.filename

        # Update to current directory when file is chosen
        self.dirIn = os.path.dirname(self.filename)

        # Get a list of files in the working directory
        self.filelist = os.listdir(self.dirIn)

        if os.path.basename(self.filename) in self.filelist:
            self.fileindex = self.filelist.index(os.path.basename(self.filename))
        else:
            self.fileindex = 0

        # Read the data from file
        radar_warning = False
        grid_warning = False
        if self.mode in ("radar","all"):
            try:
                radar = pyart.io.read(self.filename, delay_field_loading=True)
                self.Vradar.change(radar)
                return
            except:
                try:
                    radar = pyart.io.read(self.filename)
                    self.Vradar.change(radar)
                    return
                except:
                    import traceback
                    print traceback.format_exc()
                    radar_warning = True
        elif self.mode in ("grid","all"):
            try:
                grid = pyart.io.read_grid(self.filename, delay_field_loading=True)
                self.Vgrid.change(grid)
                return
            except:
                try:
                    grid = pyart.io.read_grid(self.filename)
                    self.Vgrid.change(grid)
                    return
                except:
                    import traceback
                    print traceback.format_exc()
                    grid_warning = True

        if grid_warning or radar_warning:
            msg = "Py-ART didn't recognize this file!"
            common.ShowWarning(msg)
        else:
            msg = "Could not open file, invalid mode!"
            common.ShowWarning(msg)
        return

