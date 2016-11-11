"""
nav.py

Icons used in this script were created by
oxygenicons (http://www.oxygen-icons.org/)
and distributed at the IconArchive (http://www.iconarchive.com) under
the GNU Lesser General Public License.

"""

# Load the needed packages
from functools import partial
import os, glob
import numpy as np
import pyart
import time

from ..core import Component, Variable, common, QtGui, QtCore

class FileNavigator(Component):
    '''
    Interface for executing :py:class:`pyart.filters.GateFilter`.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`
    Vfilelist = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("FileNavigator").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, pathDir=None, filename=None, Vradar=None, Vgrid=None,
                 Vfilelist=None, name="FileNavigator", parent=None):
        '''Initialize the class to create the interface.

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
        '''
        super(FileNavigator, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        if pathDir is None:
            pathDir = os.getcwd()
        self.fileindex = 0

        # Set up signal, so that DISPLAY can react to
        # changes in radar or gatefilter shared variables
        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar
        if Vgrid is None:
            self.Vgrid = Variable(None)
        else:
            self.Vgrid = Vgrid
        if Vfilelist is None:
            self.Vfilelist = Variable([])
        else:
            self.Vfilelist = Vfilelist

        self.sharedVariables = {"Vradar": self.NewFile,
                                "Vgrid": self.NewFile,
                                "Vfilelist": self.NewFilelist}
        # Connect the components
        self.connectAllVariables()

        # Set up the Display layout
        self.createUI()

        self.filename = ''
        if Vradar is None and Vgrid is None:
            if filename is None:
                self._openfile(filename)
            elif filename is not False:
                self._openfile(filename)

        self.directoryAction.setText(pathDir)

        self.NewFile(self.Vradar, True)
        self.NewFilelist(self.Vfilelist, True)

        self.raise_()
        self.setWindowState(QtCore.Qt.WindowActive)
        self.show()

    ######################
    #   Layout Methods   #
    ######################

    def createUI(self):
        '''Mount the navigation layout.'''
        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir))

        pixfirst = QtGui.QPixmap(os.sep.join([parentdir, 'icons',
                                              "arrow_go_first_icon.png"]))
        pixprev = QtGui.QPixmap(os.sep.join([parentdir, 'icons',
                                             "arrow_go_previous_icon.png"]))
        pixnext = QtGui.QPixmap(os.sep.join([parentdir, 'icons',
                                             "arrow_go_next_icon.png"]))
        pixlast = QtGui.QPixmap(os.sep.join([parentdir, 'icons',
                                             "arrow_go_last_icon.png"]))
        pixconfig = QtGui.QPixmap(os.sep.join(
            [parentdir, 'icons',
            "save_icon.png"]))

        self.configButton = QtGui.QPushButton(QtGui.QIcon(pixconfig),"")
        self.layout.addWidget(self.configButton, 0, 0)

        self.act_first = QtGui.QToolButton()
        self.act_first.setIcon(QtGui.QIcon(pixfirst))
        self.act_first.clicked.connect(self.goto_first_file)
        self.layout.addWidget(self.act_first, 0, 1)

        self.act_prev = QtGui.QToolButton()
        self.act_prev.setIcon(QtGui.QIcon(pixprev))
        self.act_prev.clicked.connect(self.goto_prev_file)
        self.layout.addWidget(self.act_prev, 0, 2)

        self.act_next = QtGui.QToolButton()
        self.act_next.setIcon(QtGui.QIcon(pixnext))
        self.act_next.clicked.connect(self.goto_next_file)
        self.layout.addWidget(self.act_next, 0, 3)

        self.act_last = QtGui.QToolButton()
        self.act_last.setIcon(QtGui.QIcon(pixlast))
        self.act_last.clicked.connect(self.goto_last_file)
        self.layout.addWidget(self.act_last, 0, 4)

        self.configMenu = QtGui.QMenu()
        self.configButton.setMenu(self.configMenu)
        self.directoryMenu = self.configMenu.addMenu("Directory:")
        self.directoryAction = self.directoryMenu.addAction("")
        self.fileMenu = self.configMenu.addMenu("File:")
        self.fileAction = self.fileMenu.addAction("")

        action = QtGui.QAction("Open", self,
                               triggered=lambda: self._openfile())
        self.configMenu.addAction(action)

        self.saveRadarAction = QtGui.QAction("Save Radar", self,
                                             triggered=self.saveRadar)
        if self.Vradar.value is None:
            self.saveRadarAction.setEnabled(False)
        self.configMenu.addAction(self.saveRadarAction)

        self.saveGridAction = QtGui.QAction("Save Grid", self,
                                            triggered=self.saveGrid)
        if self.Vgrid.value is None:
            self.saveGridAction.setEnabled(False)
        self.configMenu.addAction(self.saveGridAction)

        action = QtGui.QAction("Help", self,
                               triggered=self._show_help)
        self.configMenu.addAction(action)

        self.layout.addItem(QtGui.QSpacerItem(
            0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding),
                            0, 5)

    ######################
    #   Update Methods   #
    ######################

    def _show_help(self):
        helptext = ("Use Icons above for navigation.<br>"
                    "By linking/unliking the radar variables in the<br>"
                    "LinkSharedVariables menu for various components, "
                    "you can<br>"
                    "control which Display is navigated."
                    )
        common.ShowLongText(helptext)

    def _update_tools(self):
        '''Update the navigation button.'''
        filelist = self.Vfilelist.value
        if filelist is None:
            return

        if self.filename in filelist:
            self.fileindex = filelist.index(self.filename)
        else:
            self.fileindex = 0

        if self.fileindex > 0 and self.fileindex < len(filelist):
            self.act_prev.setEnabled(True)
            self.act_prev.setToolTip(
                'Previous file: %s' %
                os.path.basename(filelist[self.fileindex - 1]))
        else:
            self.act_prev.setEnabled(False)
            self.act_prev.setToolTip('Previous file:')

        if self.fileindex >= 0 and self.fileindex < len(filelist) - 1:
            self.act_next.setEnabled(True)
            self.act_next.setToolTip(
                'Next file: %s' %
                os.path.basename(filelist[self.fileindex + 1]))
        else:
            self.act_next.setEnabled(False)
            self.act_next.setToolTip('Next file:')

        if filelist:
            self.act_first.setEnabled(True)
            self.act_first.setToolTip(
                "First file: %s" %
                os.path.basename(filelist[0]))

            self.act_last.setEnabled(True)
            self.act_last.setToolTip(
                "Last file: %s" %
                os.path.basename(filelist[-1]))
        else:
            self.act_first.setEnabled(False)
            self.act_first.setToolTip("First file:")

            self.act_last.setEnabled(False)
            self.act_last.setToolTip("Last file:")

    #########################
    #   Selection Methods   #
    #########################

    def AdvanceFileSelect(self, findex):
        '''Captures a selection and open file.'''
        if findex > (len(self.Vfilelist.value) - 1):
            print(len(self.Vfilelist.value))
            msg = "End of directory, cannot advance!"
            common.ShowWarning(msg)
            findex = (len(self.Vfilelist.value) - 1)
            return
        elif findex < 0:
            msg = "Beginning of directory, must move forward!"
            common.ShowWarning(msg)
            findex = 0
            return
        self.fileindex = findex
        self.filename = self.Vfilelist.value[findex]
        self._openfile(self.filename)

    def goto_first_file(self):
        self.fileindex = 0
        self.AdvanceFileSelect(self.fileindex)

    def goto_last_file(self):
        self.fileindex = len(self.Vfilelist.value) - 1
        self.AdvanceFileSelect(self.fileindex)

    def goto_prev_file(self):
        self.fileindex = self.fileindex - 1
        self.AdvanceFileSelect(self.fileindex)

    def goto_next_file(self):
        self.fileindex = self.fileindex + 1
        self.AdvanceFileSelect(self.fileindex)

    def _openfile(self, filename=None):
        '''Open a file via a file selection window.'''
        if filename is None:
            dirIn = str(self.directoryAction.text())
            filename = str(QtGui.QFileDialog.getOpenFileName(
                None, 'Open file', dirIn))
            if filename == '':
                return
            self.filename = filename
        print("Opening file " + filename)

        # Read the data from file
        radar_warning = False
        grid_warning = False

        try:
            radar = pyart.io.read(filename, delay_field_loading=True)
            # Add the filename for Display
            radar.filename = filename
            self.replaceRadar(radar)
            return
        except:
            try:
                radar = pyart.io.read(filename)
                # Add the filename for Display
                radar.filename = filename
                self.replaceRadar(radar)
                return
            except:
                import traceback
                print(traceback.format_exc())
                radar_warning = True

        try:
            grid = pyart.io.read_grid(
                filename, delay_field_loading=True)
            self.replaceGrid(grid)
            return
        except:
            try:
                grid = pyart.io.read_grid(filename)
                self.replaceGrid(grid)
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

    def NewFilelist(self, variable, strong):
        '''respond to change in filelist.'''
        if strong:
            self._update_tools()

    def NewFile(self, variable, strong):
        '''Respond to change in a container (radar or grid).'''
        if hasattr(variable.value, 'filename'):
            # Update the info label.'''
            self.filename = variable.value.filename
            dirIn = os.path.dirname(self.filename)
            self.directoryAction.setText(dirIn)
            self.fileAction.setText(os.path.basename(self.filename))
            if (self.Vfilelist.value is None or
                self.filename not in self.Vfilelist.value):
                filelist = [path for path in glob.glob(os.path.join(dirIn, '*'))
                            if os.path.isfile(path)]
                filelist.sort()
                self.fileindex = filelist.index(self.filename)
                self.Vfilelist.change(filelist)
            else:
                self.fileindex = self.Vfilelist.value.index(self.filename)
                self._update_tools()
        if variable == self.Vradar:
            self.saveRadarAction.setEnabled(variable.value is not None)
        else:
            self.saveGridAction.setEnabled(variable.value is not None)

    def replaceRadar(self, radar):
        '''Replace current radar, warning for data lost.'''
        if hasattr(self.Vradar.value, 'changed') and self.Vradar.value.changed:
            resp = common.ShowQuestionYesNo("Save changes before moving to next File?")
            if resp == QtGui.QMessageBox.Yes:
                self.Vradar.change(radar)
            elif resp != QtGui.QMessageBox.No:
                return
        else:
            self.Vradar.change(radar)

    def replaceGrid(self, grid):
        '''Replace current grid, warning for data lost.'''
        if hasattr(self.Vgrid.value, 'changed') and self.Vgrid.value.changed:
            resp = common.ShowQuestionYesNo("Save changes before moving to next File?")
            if resp == QtGui.QMessageBox.Yes:
                self.Vgrid.change(grid)
            elif resp != QtGui.QMessageBox.No:
                return
        else:
            self.Vgrid.change(grid)

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
            self, 'Save Radar File', str(self.directoryAction.text()))
        filename = str(filename)
        if filename == '' or self.Vradar.value is None:
            return
        else:
            pyart.io.write_cfradial(filename, self.Vradar.value)
            print("Saved %s" % (filename))

    def saveGrid(self):
        '''Open a dialog box to save grid file.'''

        filename = QtGui.QFileDialog.getSaveFileName(
            self, 'Save grid File', str(self.directoryAction.text()))
        filename = str(filename)
        if filename == '' or self.Vgrid.value is None:
            return
        else:
            pyart.io.write_grid(filename, self.Vgrid.value)


class FileNavigator_old(Component):
    '''
    Interface for executing :py:class:`pyart.filters.GateFilter`.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`
    Vfilelist = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("FileNavigator").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None, Vgrid=None, Vfilelist=None,
                 name="FileNavigator", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        name : string
            FileNavigator instance window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated w/ parent PyQt instance
        '''
        super(FileNavigator_old, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        # Set up signal, so that DISPLAY can react to
        # changes in radar or gatefilter shared variables
        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar
        if Vgrid is None:
            self.Vgrid = Variable(None)
        else:
            self.Vgrid = Vgrid
        if Vfilelist is None:
            self.Vfilelist = Variable([])
        else:
            self.Vfilelist = Vfilelist
        self.filename = ""
        self.fileindex = 0

        self.sharedVariables = {"Vradar": self.NewFile,
                                "Vgrid": self.NewFile,
                                "Vfilelist": self.NewFilelist}
        # Connect the components
        self.connectAllVariables()

        # Set up the Display layout
        self.generalLayout = QtGui.QVBoxLayout()
        self.generalLayout.addWidget(self.createNavToolbar())
        self.generalLayout.addWidget(self.createInfoUI())
        self.generalLayout.addWidget(self.createHelpUI())

        self.layout.addLayout(self.generalLayout, 0, 0, 1, 2)

        self.NewFile(self.Vradar, True)
        self.NewFilelist(self.Vfilelist, True)

        self.raise_()
        self.setWindowState(QtCore.Qt.WindowActive)
        self.show()

    ######################
    #   Layout Methods   #
    ######################

    def createNavButtonUI(self):
        '''Mount the file navigation buttons.'''
        groupBox = QtGui.QGroupBox("File Navigation")
        gBox_layout = QtGui.QGridLayout()

        self.firstbutton = QtGui.QPushButton("First")
        self.firstbutton.setToolTip("Load first file in directory")
        self.firstbutton.clicked.connect(self.goto_first_file)
        gBox_layout.addWidget(self.firstbutton, 0, 0, 1, 1)

        self.prevbutton = QtGui.QPushButton("Previous")
        self.prevbutton.setToolTip("Load previous file")
        self.prevbutton.setIconSize(QtCore.QSize(32, 32))
        self.prevbutton.clicked.connect(self.goto_prev_file)
        gBox_layout.addWidget(self.prevbutton, 0, 1, 1, 1)

        self.nextbutton = QtGui.QPushButton("Next")
        self.nextbutton.setToolTip("Load next file")
        self.nextbutton.clicked.connect(self.goto_next_file)
        gBox_layout.addWidget(self.nextbutton, 0, 2, 1, 1)

        self.lastbutton = QtGui.QPushButton("Last")
        self.lastbutton.setToolTip("Load last file in directory")
        self.lastbutton.clicked.connect(self.goto_last_file)
        gBox_layout.addWidget(self.lastbutton, 0, 3, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def createNavToolbar(self):
        '''Mount the file navigation toolbar.'''
        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir))
        groupBox = QtGui.QGroupBox("File Navigation")
        gBox_layout = QtGui.QGridLayout()

        self.navtoolbar = QtGui.QToolBar()
        pixfirst = QtGui.QPixmap(os.sep.join([parentdir, 'icons',
                                              "arrow_go_first_icon.png"]))
        pixprev = QtGui.QPixmap(os.sep.join([parentdir, 'icons',
                                             "arrow_go_previous_icon.png"]))
        pixnext = QtGui.QPixmap(os.sep.join([parentdir, 'icons',
                                             "arrow_go_next_icon.png"]))
        pixlast = QtGui.QPixmap(os.sep.join([parentdir, 'icons',
                                             "arrow_go_last_icon.png"]))
        self.act_first = self.navtoolbar.addAction(
            QtGui.QIcon(pixfirst),
            "First file:",
            self.goto_first_file)
        self.act_prev = self.navtoolbar.addAction(
            QtGui.QIcon(pixprev),
            "Previous file:",
            self.goto_prev_file)
        self.act_next = self.navtoolbar.addAction(
            QtGui.QIcon(pixnext),
            "Next file:",
            self.goto_next_file)
        self.act_last = self.navtoolbar.addAction(
            QtGui.QIcon(pixlast),
            "Last file:",
            self.goto_last_file)

        gBox_layout.addWidget(self.navtoolbar)
        groupBox.setLayout(gBox_layout)

        return groupBox

    def createInfoUI(self):
        '''Mount the information text.'''
        groupBox = QtGui.QGroupBox("File Information")
        gBox_layout = QtGui.QGridLayout()

        self.infodir = QtGui.QLabel("Directory:")
        self.infodir.setStyleSheet('font: italic 12px')
        gBox_layout.addWidget(self.infodir, 0, 0, 1, 1)

        self.infofile = QtGui.QLabel("File:")
        self.infofile.setStyleSheet('font: italic 12px')
        gBox_layout.addWidget(self.infofile, 1, 0, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def createHelpUI(self):
        '''Mount the help text.'''
        groupBox = QtGui.QGroupBox("Help")
        gBox_layout = QtGui.QGridLayout()

        helptext = ("Use Icons above for navigation.<br>"
                    "By linking/unliking the radar variables in the<br>"
                    "LinkSharedVariables menu for various components, "
                    "you can<br>"
                    "control which Display is navigated."
                    )
        self.help = QtGui.QLabel(helptext)
        self.infodir.setStyleSheet('font: italic 12px')
        gBox_layout.addWidget(self.help, 0, 0, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    ######################
    #   Update Methods   #
    ######################

    def _update_tools(self):
        '''Update the navigation button.'''
        filelist = self.Vfilelist.value
        if self.filename in filelist:
            self.fileindex = filelist.index(self.filename)
        else:
            self.fileindex = 0

        if self.fileindex > 0 and self.fileindex < len(filelist):
            self.act_prev.setEnabled(True)
            self.act_prev.setToolTip(
                'Previous file: %s' %
                os.path.basename(filelist[self.fileindex - 1]))
        else:
            self.act_prev.setEnabled(False)
            self.act_prev.setToolTip('Previous file:')

        if self.fileindex >= 0 and self.fileindex < len(filelist) - 1:
            self.act_next.setEnabled(True)
            self.act_next.setToolTip(
                'Next file: %s' %
                os.path.basename(filelist[self.fileindex + 1]))
        else:
            self.act_next.setEnabled(False)
            self.act_next.setToolTip('Next file:')

        if filelist:
            self.act_first.setEnabled(True)
            self.act_first.setToolTip(
                "First file: %s" %
                os.path.basename(filelist[0]))

            self.act_last.setEnabled(True)
            self.act_last.setToolTip(
                "Last file: %s" %
                os.path.basename(filelist[-1]))
        else:
            self.act_first.setEnabled(False)
            self.act_first.setToolTip("First file:")

            self.act_last.setEnabled(False)
            self.act_last.setToolTip("Last file:")

    #########################
    #   Selection Methods   #
    #########################

    def AdvanceFileSelect(self, findex):
        '''Captures a selection and open file.'''
        if findex > (len(self.Vfilelist.value) - 1):
            print(len(self.Vfilelist.value))
            msg = "End of directory, cannot advance!"
            common.ShowWarning(msg)
            findex = (len(self.Vfilelist.value) - 1)
            return
        elif findex < 0:
            msg = "Beginning of directory, must move forward!"
            common.ShowWarning(msg)
            findex = 0
            return
        self.fileindex = findex
        self.filename = self.Vfilelist.value[findex]
        self._openfile(self.filename)
        self._update_tools()

    def goto_first_file(self):
        self.fileindex = 0
        self.AdvanceFileSelect(self.fileindex)

    def goto_last_file(self):
        self.fileindex = len(self.Vfilelist.value) - 1
        self.AdvanceFileSelect(self.fileindex)

    def goto_prev_file(self):
        self.fileindex = self.fileindex - 1
        self.AdvanceFileSelect(self.fileindex)

    def goto_next_file(self):
        self.fileindex = self.fileindex + 1
        self.AdvanceFileSelect(self.fileindex)

    def _openfile(self, filename=None):
        '''Open a file via a file selection window.'''
        print("Opening file " + filename)

        # Read the data from file
        radar_warning = False
        grid_warning = False

        try:
            radar = pyart.io.read(filename, delay_field_loading=True)
            # Add the filename for Display
            radar.filename = filename
            self.replaceGrid(radar)
            return
        except:
            try:
                radar = pyart.io.read(filename)
                # Add the filename for Display
                radar.filename = filename
                self.replaceGrid(radar)
                return
            except:
                import traceback
                print(traceback.format_exc())
                radar_warning = True

        try:
            grid = pyart.io.read_grid(
                filename, delay_field_loading=True)
            self.replaceGrid(grid)
            return
        except:
            try:
                grid = pyart.io.read_grid(filename)
                self.replaceGrid(grid)
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

    def NewFilelist(self, variable, strong):
        '''respond to change in filelist.'''
        if strong:
            self._update_tools()

    def NewFile(self, variable, strong):
        '''Respond to change in a container (radar or grid).'''
        if hasattr(variable.value, 'filename'):
            # Update the info label.'''
            self.filename = variable.value.filename
            dirIn = os.path.dirname(self.filename)
            self.infodir.setText("Directory: %s" % dirIn)
            self.infofile.setText("File: %s" %
                                  os.path.basename(self.filename))


_plugins = [FileNavigator, FileNavigator_old]
