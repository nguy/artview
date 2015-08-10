"""
menu.py

Class instance used to create menu for ARTview app.
"""
import numpy as np
import pyart

import os, sys
from PyQt4 import QtGui, QtCore

from ..core import Variable, Component, common


class Menu(Component):
    '''Class to display the MainMenu.'''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`

    def __init__(self, pathDir, filename=None, Vradar=None, Vgrid=None,
                 mode="Radar", name="Menu", parent=None):
        '''
        Initialize the class to create the interface.

        Parameters
        ----------
        pathDir : string
            Input directory path to open.
        [Optional]
        filename : string, False or None
            File to open as first. None will open file dialog. False will
            open no file.
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable.
            A value of None initializes an empty Variable.
        Vgrid : :py:class:`~artview.core.core.Variable` instance
            Grid signal variable.
            A value of None initializes an empty Variable.
        mode : "Radar", "Grid" or "All"
            Determine which type of files will be open
        name : string
            Menu name.
        parent : PyQt instance
            Parent instance to associate to menu.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        Notes
        -----
        This class creates the main application interface and creates
        a menubar for the program.
        '''
        super(Menu, self).__init__(name=name, parent=parent)

        # Set some parameters
        self.dirIn = pathDir
        self.fileindex = 0
        self.filelist = []
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
            elif filename is False:
                pass
            else:
                self.filename = filename
                self._openfile()

        # Launch the GUI interface
        self.LaunchApp()
        self.resize(300, 180)
        self.show()

    def keyPressEvent(self, event):
        '''Change data file with left and right arrow keys.'''
        if event.key() == QtCore.Qt.Key_Right:
            # Menu control the file and open the radar
            self.AdvanceFileSelect(self.fileindex + 1)
        elif event.key() == QtCore.Qt.Key_Left:
            # Menu control the file and open the radar
            self.AdvanceFileSelect(self.fileindex - 1)
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
        if sys.version_info<(2,7,0):
            self.central_widget = QtGui.QWidget()
            self.setCentralWidget(self.central_widget)
            self.centralLayout = QtGui.QVBoxLayout(self.central_widget)
            self.centralLayout.setSpacing(8)
            self.frames = {}
            self.addLayoutMenu()
        else:
            self.mdiArea = QtGui.QMdiArea()
            self.setCentralWidget(self.mdiArea)
            self.mdiArea.setViewMode(1)
            self.mdiArea.setTabsClosable(True)

    def showFileDialog(self):
        '''Open a dialog box to choose file.'''

        filename = QtGui.QFileDialog.getOpenFileName(
            self, 'Open file', self.dirIn)
        filename = str(filename)
        if filename == '':
            return
        else:
            self.filename = filename
            self._openfile()

    def saveRadar(self):
        '''Open a dialog box to save radar file.'''

        filename = QtGui.QFileDialog.getSaveFileName(
                self, 'Save Radar File', self.dirIn)
        filename = str(filename)
        if filename == '' or self.Vradar.value is None:
            return
        else:
            pyart.io.write_cfradial(filename, self.Vradar.value)

    def saveGrid(self):
        '''Open a dialog box to save grid file.'''

        filename = QtGui.QFileDialog.getSaveFileName(
                self, 'Save grid File', self.dirIn)
        filename = str(filename)
        if filename == '' or self.Vgrid.value is None:
            return
        else:
            pyart.io.write_grid(filename, self.Vgrid.value)

    def addLayoutWidget(self, widget):
        '''
        Add a widget to central layout.
        This function is to be called both internal and external.
        '''
        if sys.version_info<(2,7,0):
            frame = QtGui.QFrame()
            frame.setFrameShape(QtGui.QFrame.Box)
            layout = QtGui.QVBoxLayout(frame)
            layout.addWidget(widget)
            self.frames[widget.__repr__()] = widget
            self.centralLayout.addWidget(widget)
            self.addLayoutMenuItem(widget)
        else:
            self.mdiArea.addSubWindow(widget)

    def removeLayoutWidget(self, widget):
        '''Remove widget from central layout.'''
        frame = self.frames[widget.__repr__()]
        self.centralLayout.removeWidget(frame)
        self.removeLayoutMenuItem(widget)
        frame.close()
        widget.close()
        widget.deleteLater()

    def addComponent(self, Comp, label=None):
        '''Add Component Contructor. If label is None, use class name.'''
        # first test the existence of a guiStart
        if not hasattr(Comp, 'guiStart'):
            raise ValueError("Component has no guiStart Method")
            return
        self.addPluginMenuItem(Comp)

    ######################
    # Menu build methods #
    ######################

    def CreateMenu(self):
        '''Create the main menubar.'''
        self.menubar = self.menuBar()

        self.addFileMenu()
        self.addAboutMenu()
        self.addFileAdvanceMenu()
        self.addPluginMenu()

    def addFileMenu(self):
        '''Add the File Menu to menubar.'''
        self.filemenu = self.menubar.addMenu('&File')

        openFile = QtGui.QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showFileDialog)

        if self.mode in ("radar", "all"):
            saveRadar = QtGui.QAction('Save Radar', self)
            saveRadar.setStatusTip('Save Radar to Cf/Radial NetCDF')
            saveRadar.triggered.connect(self.saveRadar)
        if self.mode in ("grid", "all"):
            saveGrid = QtGui.QAction('Save Grid', self)
            saveGrid.setStatusTip('Save Grid NetCDF')
            saveGrid.triggered.connect(self.saveGrid)

        exitApp = QtGui.QAction('Close', self)
        exitApp.setShortcut('Ctrl+Q')
        exitApp.setStatusTip('Exit ARTview')
        exitApp.triggered.connect(self.close)

        self.filemenu.addAction(openFile)
        if self.mode in ("radar", "all"):
            self.filemenu.addAction(saveRadar)
        if self.mode in ("grid", "all"):
            self.filemenu.addAction(saveGrid)
        self.filemenu.addAction(exitApp)

    def addAboutMenu(self):
        '''Add Help menu to menubar.'''
        self.aboutmenu = self.menubar.addMenu('About')

        self._aboutArtview = QtGui.QAction('ARTview', self)
        self._aboutArtview.setStatusTip('About ARTview')
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

    def addLayoutMenu(self):
        '''Add Layout Menu to menubar.'''
        self.layoutmenu = self.menubar.addMenu('&Layout')
        self.layoutmenuItems = {}

    def addPluginMenu(self):
        '''Add Component Menu to menu bar.'''
        self.pluginmenu = self.menubar.addMenu('&Advanced Tools')

    def addLayoutMenuItem(self, widget):
        '''Add widget item to Layout Menu.'''
        if hasattr(widget, 'name'):
            item = self.layoutmenu.addMenu(widget.name)
        else:
            item = self.layoutmenu.addMenu(widget.__str__())
        self.layoutmenuItems[widget.__repr__()] = item
        remove = item.addAction("remove")
        remove.triggered[()].connect(
            lambda widget=widget: self.removeLayoutWidget(widget))

    def removeLayoutMenuItem(self, widget):
        '''Remove widget item from Layout Menu.'''
        rep = widget.__repr__()
        if rep in self.layoutmenuItems:
            self.layoutmenuItems[rep].clear()
            self.layoutmenu.removeAction(
                self.layoutmenuItems[rep].menuAction())
            self.layoutmenuItems[rep].close()
            del self.layoutmenuItems[rep]

    def addPluginMenuItem(self, Comp, label=None):
        '''Add Component item to Component Menu.
        If label is None use class name.'''
        if label is None:
            label = Comp.__name__
        action = self.pluginmenu.addAction(label)
        action.triggered[()].connect(
            lambda Comp=Comp: self.startComponent(Comp))

    def startComponent(self, Comp):
        '''Execute the GUI start of Component and
        add to layout if not independent.'''
        comp, independent = Comp.guiStart(self)
        if not independent:
            self.addLayoutWidget(comp)

    def addFileAdvanceMenu(self):
        '''
        Add menu to advance to next or previous file. 
        Or to go to the first or last file in the selected directory.'''
        self.advancemenu = self.menubar.addMenu("Change file")
        nextAction = self.advancemenu.addAction("Next")
        nextAction.triggered[()].connect(
            lambda findex=self.fileindex + 1: self.AdvanceFileSelect(findex))

        prevAction = self.advancemenu.addAction("Previous")
        prevAction.triggered[()].connect(
            lambda findex=self.fileindex - 1: self.AdvanceFileSelect(findex))

        firstAction = self.advancemenu.addAction("First")
        firstAction.triggered[()].connect(
            lambda findex=0: self.AdvanceFileSelect(findex))

        lastAction = self.advancemenu.addAction("Last")
        lastAction.triggered[()].connect(
            lambda findex=(len(self.filelist) - 1):
            self.AdvanceFileSelect(findex))

    ######################
    # Help methods #
    ######################

    def _about(self):
        # Add a more extensive about eventually
        txOut = """ARTview is a visualization package that leverages the
DoE PyArt python software to view individual weather
radar data files or to browse a directory of data.
                 
If you hover over butttons and menus with the mouse,
more instructions and information are available.
                 
More complete documentation can be found at:
https://rawgit.com/nguy/artview/master/docs/build/html/index.html"""
        QtGui.QMessageBox.about(self, "About ARTview", txOut)

    def _get_RadarLongInfo(self):
        '''Print out the radar info to text box and terminal.'''
        # Get the radar info form rada object and print it
        txOut = self.Vradar.value.info()

        print txOut
        QtGui.QMessageBox.information(self, "Long Radar Info",
                                      "See terminal window")

    def _get_RadarShortInfo(self):
        '''Print out some basic info about the radar.'''
        # For any missing data
        infoNA = "Info not available"
        
        try:
            rname = self.Vradar.value.metadata['instrument_name']
        except:
            rname = infoNA
        try:
            rlon = str(self.Vradar.value.longitude['data'][0])
        except:
            rlon = infoNA
        try:
            rlat = str(self.Vradar.value.latitude['data'][0])
        except:
            rlat = infoNA
        try:
            ralt = str(self.Vradar.value.altitude['data'][0])
            raltu = self.Vradar.value.altitude['units'][0]
        except:
            ralt = infoNA
            raltu = " "
        try:
            maxr = str(self.Vradar.value.instrument_parameters[
                'unambiguous_range']['data'][0])
            maxru = self.Vradar.value.instrument_parameters[
                'unambiguous_range']['units'][0]
        except:
            maxr = infoNA
            maxru = " "
        try:
            nyq = str(self.Vradar.value.instrument_parameters[
                'nyquist_velocity']['data'][0])
            nyqu = self.Vradar.value.instrument_parameters[
                'nyquist_velocity']['units'][0]
        except:
            nyq = infoNA
            nyqu = " "
        try:
            bwh = str(self.Vradar.value.instrument_parameters[
                'radar_beam_width_h']['data'][0])
            bwhu = self.Vradar.value.instrument_parameters[
                'radar_beam_width_h']['units'][0]
        except:
            bwh = infoNA
            bwhu = " "
        try:
            bwv = str(self.Vradar.value.instrument_parameters[
                'radar_beam_width_v']['data'][0])
            bwvu = self.Vradar.value.instrument_parameters[
                'radar_beam_width_v']['units'][0]
        except:
            bwv = infoNA
            bwvu = " "
        try:
            pw = str(self.Vradar.value.instrument_parameters[
                'pulse_width']['data'][0])
            pwu = self.Vradar.value.instrument_parameters[
                'pulse_width']['units'][0]
        except:
            pw = infoNA
            pwu = " "
        try:
            ngates = str(self.Vradar.value.ngates)
        except:
            ngates = infoNA
        try:
            nsweeps = str(self.Vradar.value.nsweeps)
        except:
            nsweeps = infoNA

        txOut = (('Radar Name: %s\n' % rname) +
                 ('Radar longitude: %s\n' % rlon) +
                 ('Radar latitude: %s\n' % rlat) +
                 ('Radar altitude: %s %s\n' % (ralt, raltu)) +
                 ('    \n') +
                 ('Unambiguous range: %s %s\n' % (maxr, maxru)) +
                 ('Nyquist velocity: %s %s\n' % (nyq, nyqu)) +
                 ('    \n') +
                 ('Radar Beamwidth, horiz: %s %s\n' % (bwh, bwhu)) +
                 ('Radar Beamwidth, vert: %s %s\n' % (bwv, bwvu)) +
                 ('Pulsewidth: %s %s \n' % (pw, pwu)) +
                 ('    \n') +
                 ('Number of gates: %s\n' % ngates) +
                 ('Number of sweeps: %s\n' % nsweeps))

        QtGui.QMessageBox.information(self, "Short Radar Info", txOut)

    ########################
    # Selectionion methods #
    ########################

    def AdvanceFileSelect(self, findex):
        '''Captures a selection and open file.'''
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
        self.filename = os.path.join(self.dirIn, self.filelist[findex])
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
        self.filelist.sort()

        if os.path.basename(self.filename) in self.filelist:
            self.fileindex = self.filelist.index(
                os.path.basename(self.filename))
        else:
            self.fileindex = 0

        # Read the data from file
        radar_warning = False
        grid_warning = False
        if self.mode in ("radar", "all"):
            try:
                radar = pyart.io.read(self.filename, delay_field_loading=True)
                #Add the filename for Display
                radar.filename = self.filename
                self.Vradar.change(radar)
                return
            except:
                try:
                    radar = pyart.io.read(self.filename)
                    #Add the filename for Display
                    radar.filename = self.filename
                    self.Vradar.change(radar)
                    return
                except:
                    import traceback
                    print traceback.format_exc()
                    radar_warning = True
        elif self.mode in ("grid", "all"):
            try:
                grid = pyart.io.read_grid(
                    self.filename, delay_field_loading=True)
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
