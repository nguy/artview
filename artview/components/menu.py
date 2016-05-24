"""
menu.py

Class instance used to create menu for ARTview app.
"""
import numpy as np
import pyart

import os
import sys
import glob

from ..core import Variable, Component, common, QtGui, QtCore, componentsList


class Menu(Component):
    '''Class to display the MainMenu.'''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`
    Vfilelist = None  #: see :ref:`shared_variable`

    def __init__(self, pathDir=None, filename=None, Vradar=None, Vgrid=None,
                 Vfilelist=None, mode=["Radar"], name="Menu", parent=None):
        '''
        Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        pathDir : string
            Input directory path to open. If None user current directory
        filename : string, False or None
            File to open as first. None will open file dialog. False will
            open no file.
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable.
            A value of None initializes an empty Variable.
        Vgrid : :py:class:`~artview.core.core.Variable` instance
            Grid signal variable.
            A value of None initializes an empty Variable.
        mode : list
            List with strings "Radar" or "Grid". Determine which type of files
            will be open
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
        if pathDir is None:
            pathDir = os.getcwd()
        self.dirIn = pathDir
        self.fileindex = 0
        self.mode = []
        for m in mode:
            self.mode.append(m.lower())
        self.Vradar = Vradar
        self.current_container = self.Vradar
        self.Vgrid = Vgrid
        self.Vfilelist = Vfilelist
        self.sharedVariables = {"Vradar": None,
                                "Vgrid": None,
                                "Vfilelist": None}

        # Show an "Open" dialog box and return the path to the selected file
        # Just do that if Vradar was not given
        if self.Vradar is None:
            self.Vradar = Variable(None)
        if self.Vgrid is None:
            self.Vgrid = Variable(None)
        if self.Vfilelist is None:
            self.Vfilelist = Variable(None)
        if Vradar is None and Vgrid is None and self.mode:
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
        self.raise_()
#        self.activateWindow()
        self.show()

    def keyPressEvent(self, event):
        '''Change data file with left and right arrow keys.'''
        if event.key() == QtCore.Qt.Key_Right:
            # Menu control the file and open the radar
            resp = True
            if hasattr(self.current_container.value, 'changed') and self.current_container.value.changed:
                resp = common.ShowQuestionYesNo("Save changes before moving to next File?")
                if resp == QtGui.QMessageBox.Yes:
                    self.saveCurrent()
                elif resp != QtGui.QMessageBox.No:
                    return
            self.AdvanceFileSelect(self.fileindex + 1)
        elif event.key() == QtCore.Qt.Key_Left:
            # Menu control the file and open the radar
            if hasattr(self.current_container.value, 'changed') and self.current_container.value.changed:
                resp = common.ShowQuestionYesNo("Save changes before moving to next File?")
                if resp == QtGui.QMessageBox.Yes:
                    self.saveCurrent()
                elif resp != QtGui.QMessageBox.No:
                    return
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
        if sys.version_info < (2, 7, 0):
            self.central_widget = QtGui.QWidget()
            self.setCentralWidget(self.central_widget)
            self.centralLayout = QtGui.QVBoxLayout(self.central_widget)
            self.centralLayout.setSpacing(8)
            self.frames = {}
            self.addLayoutMenu()
        else:
            self.tabWidget = QtGui.QTabWidget()
            self.setCentralWidget(self.tabWidget)
#            self.tabWidget.setAcceptDrops(True)
            self.tabWidget.setTabsClosable(True)
            self.tabWidget.tabCloseRequested.connect(self.removeTab)
            self.tabWidget.tabBar().setMovable(True)

    def removeTab(self, idx):
        widget = self.tabWidget.widget(idx)
        self.tabWidget.removeTab(idx)
        widget.close()

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

    def saveCurrent(self):
        if self.current_container == self.Vradar:
            self.saveRadar()
        elif self.current_container == self.Vgrid:
            self.saveGrid()

    def saveRadar(self):
        '''
        Open a dialog box to save radar file.

        Parameters
        ----------
        input : Vradar instance
            Optional parameter to allow access from
            other ARTView plugins, etc.
        '''
        filename = QtGui.QFileDialog.getSaveFileName(
            self, 'Save Radar File', self.dirIn)
        filename = str(filename)
        if filename == '' or self.Vradar.value is None:
            return
        else:
            pyart.io.write_cfradial(filename, self.Vradar.value)
            print("Saved %s" % (filename))

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
        if sys.version_info < (2, 7, 0):
            frame = QtGui.QFrame()
            frame.setFrameShape(QtGui.QFrame.Box)
            layout = QtGui.QVBoxLayout(frame)
            layout.addWidget(widget)
            self.frames[widget.__repr__()] = widget
            self.centralLayout.addWidget(widget)
            self.addLayoutMenuItem(widget)
            widget.show()
        else:
            self.tabWidget.addTab(widget, widget.name)

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

    def menus(self):
        return (self.menubar, self.subMenus(self.menubar))

    def subMenus(self, menu):
        ''' get submenu list of menu as dictionary. '''
        if menu is None:
            return None
        menus = {}
        for act in menu.actions():
            menus[str(act.text())] = (act.menu(), self.subMenus(act.menu()))
        return menus

    def addMenuAction(self, position, *args):
        menu, menus = self.menus()
        for key in position:
            if key in menus:
                menu, menus = menus[key]
            else:
                menu = menu.addMenu(key)
                menus = {}
        return menu.addAction(*args)

    def addMenuSeparator(self, position, *args):
        menu, menus = self.menus()
        for key in position:
            if key in menus:
                menu, menus = menus[key]
            else:
                menu = menu.addMenu(key)
                menus = {}
        return menu.addSeparator(*args)

    def CreateMenu(self):
        '''Create the main menubar.'''
        self.menubar = self.menuBar()

        self.addFileMenu()

    def addFileMenu(self):
        '''Add the File Menu to menubar.'''
        self.filemenu = self.menubar.addMenu('File')

        # Create Open action
        if self.mode:
            openFile = QtGui.QAction('Open', self)
            openFile.setShortcut('Ctrl+O')
            openFile.setStatusTip('Open new File')
            openFile.triggered.connect(self.showFileDialog)
            self.filemenu.addAction(openFile)

        # Create Save radar and/or grid action
        if "radar" in self.mode:
            saveRadar = QtGui.QAction('Save Radar', self)
            saveRadar.setStatusTip('Save Radar to Cf/Radial NetCDF')
            saveRadar.triggered.connect(self.saveRadar)
            self.filemenu.addAction(saveRadar)
        if "grid" in self.mode:
            saveGrid = QtGui.QAction('Save Grid', self)
            saveGrid.setStatusTip('Save Grid NetCDF')
            saveGrid.triggered.connect(self.saveGrid)
            self.filemenu.addAction(saveGrid)

        # Create About ARTView action
        aboutApp = QtGui.QAction('ARTView...', self)
        aboutApp.setStatusTip('About ARTview')
        aboutApp.triggered.connect(self._about)
        self.filemenu.addAction(aboutApp)

        # Create Plugin Help action
        pluginHelp = QtGui.QAction('Plugin Help', self)
        pluginHelp.setStatusTip('More information about Plugins')
        pluginHelp.triggered.connect(self._get_pluginhelp)
        self.filemenu.addAction(pluginHelp)

        # Create Close ARTView action
        exitApp = QtGui.QAction('Close', self)
        exitApp.setShortcut('Ctrl+Q')
        exitApp.setStatusTip('Exit ARTview')
        exitApp.triggered.connect(self.close)
        self.filemenu.addAction(exitApp)
        self.filemenu.addSeparator()

    def addLayoutMenu(self):
        '''Add Layout Menu to menubar.'''
        self.layoutmenu = self.menubar.addMenu('&Layout')
        self.layoutmenuItems = {}

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
        # XXX this function is broken and need to be removed
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

    def change_mode(self, new_mode):
        ''' Open and connect new components to satisfy mode.

        Parameters
        ----------
        new_mode: see file artview/modes.py for documentation on modes
        '''
        components = new_mode[0][:]
        links = new_mode[1]
        static_comp_list = componentsList[:]
        # find already running components
        for i, component in enumerate(components):
            flag = False
            for j, comp in enumerate(static_comp_list):
                if isinstance(comp, component):
                    components[i] = static_comp_list.pop(j)
                    flag = True
                    break
            if not flag:
                # if there is no component open
                print("starting component: %s" % component.__name__)
                from ..core.core import suggestName
                name = suggestName(components[i])
                components[i] = components[i](name=name, parent=self)
                self.addLayoutWidget(components[i])

        for link in links:
            dest = getattr(components[link[0][0]], link[0][1])
            orin = getattr(components[link[1][0]], link[1][1])
            if dest is orin:
                # already linked
                pass
            else:
                # not linked, link
                print("linking %s.%s to %s.%s" %
                      (components[link[1][0]].name, link[1][1],
                       components[link[0][0]].name, link[0][1]))
                # Disconect old Variable
                components[link[1][0]].disconnectSharedVariable(link[1][1])
                # comp1.var = comp0.var
                setattr(components[link[1][0]], link[1][1], dest)
                # Connect new Variable
                components[link[1][0]].connectSharedVariable(link[1][1])
                # Emit change signal
                dest.update()

    def addFileAdvanceMenu(self):
        '''
        Add menu to advance to next or previous file.
        Or to go to the first or last file in the selected directory.
        '''
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
            lambda findex=(len(self.Vfilelist.value) - 1):
            self.AdvanceFileSelect(findex))

    ######################
    # Help methods #
    ######################

    def _about(self):
        # Add a more extensive about eventually
        text = (
            "<b>About ARTView</b><br><br>"
            "ARTview is a visualization package that leverages the <br>"
            "DoE Py-ART python software to view individual weather <br>"
            "radar data files or to browse a directory of data.<br><br>"
            "<i>Note</i>:<br>"
            "Tooltip information is available if you hover over buttons <br> "
            "and menus with the mouse.<br><br>"
            "<i>Documentation</i>:<br>"
            "<br><br>"
            "For a demonstration, a "
            "<a href='https://rawgit.com/nguy/artview/master/docs/build/"
            "html/index.html'>Software Package Documentation</a><br>"
            )
        common.ShowLongTextHyperlinked(text)

    # XXX Remove once FileDetails is made live
    def _get_RadarLongInfo(self):
        '''Print out the radar info to text box.'''
        # Get the radar info form rada object and print it
        txOut = self.Vradar.value.info()

        print(txOut)
        QtGui.QMessageBox.information(self, "Long Radar Info",
                                      "See terminal window")

    # XXX Remove once FileDetails is made live
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

    def _get_pluginhelp(self):
        '''Print out a short help text box regarding plugins.'''

        text = (
            "<b>Existing Plugins</b><br><br>"
            "Current plugins can be found under the <i>File->Plugins</i> "
            "menu.<br>"
            "Most plugins have a help button for useage information.<br>"
            "<br><br>"
            "<b>Creating a Custom Plugin</b><br><br>"
            "ARTview allows the creation of custom user plugins.<br><br>"
            "Instructions and examples can be found at:<br>"
            "https://rawgit.com/nguy/artview/master/docs/build/html/"
            "plugin_tutorial.html<br><br>"
            "Please consider submitting your plugin for inclusion in "
            "ARTview<br>"
            "  Submit a pull request if you forked the repo on Github or"
            "  Post the code in an Issue:<br>"
            "https://github.com/nguy/artview/issues<br><br>")

        common.ShowLongText(text)

    ########################
    # Selectionion methods #
    ########################

    def AdvanceFileSelect(self, findex):
        '''Captures a selection and open file.'''
        if findex > (len(self.Vfilelist.value)-1):
            print(len(self.Vfilelist.value))
            msg = "End of directory, cannot advance!"
            common.ShowWarning(msg)
            findex = (len(self.Vfilelist.value) - 1)
            return
        if findex < 0:
            msg = "Beginning of directory, must move forward!"
            common.ShowWarning(msg)
            findex = 0
            return
        self.fileindex = findex
        self.filename = self.Vfilelist.value[findex]
        self._openfile()

    ########################
    # Menu display methods #
    ########################

    def _openfile(self, filename=None):
        '''Open a file via a file selection window.'''
        if filename is not None:
            self.filename = filename

        print("Opening file " + self.filename)

        # Update to current directory when file is chosen
        self.dirIn = os.path.dirname(self.filename)

        # Get a list of files (and only files) in the working directory
        filelist = [path for path in glob.glob(os.path.join(self.dirIn, '*'))
                    if os.path.isfile(path)]
        filelist.sort()
        self.Vfilelist.change(filelist)

        if self.filename in self.Vfilelist.value:
            self.fileindex = self.Vfilelist.value.index(
                self.filename)
        else:
            self.fileindex = 0

        # Read the data from file
        radar_warning = False
        grid_warning = False
        if "radar" in self.mode:
            try:
                radar = pyart.io.read(self.filename, delay_field_loading=True)
                # Add the filename for Display
                radar.filename = self.filename
                self.Vradar.change(radar)
                self.current_container = self.Vradar
                return
            except:
                try:
                    radar = pyart.io.read(self.filename)
                    # Add the filename for Display
                    radar.filename = self.filename
                    self.Vradar.change(radar)
                    self.current_container = self.Vradar
                    return
                except:
                    import traceback
                    print(traceback.format_exc())
                    radar_warning = True
        if "grid" in self.mode:
            try:
                grid = pyart.io.read_grid(
                    self.filename, delay_field_loading=True)
                self.Vgrid.change(grid)
                self.current_container = self.Vgrid
                return
            except:
                try:
                    grid = pyart.io.read_grid(self.filename)
                    self.Vgrid.change(grid)
                    self.current_container = self.Vgrid
                    return
                except:
                    import traceback
                    print(traceback.format_exc())
                    grid_warning = True

        if grid_warning or radar_warning:
            msg = "Py-ART didn't recognize this file!"
            common.ShowWarning(msg)
        else:
            msg = "Could not open file, invalid mode!"
            common.ShowWarning(msg)
        return
