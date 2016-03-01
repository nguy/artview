"""
nav.py

Icons used in this script were created by
oxygenicons (http://www.oxygen-icons.org/)
and distributed at the IconArchive (http://www.iconarchive.com) under
the GNU Lesser General Public License.

"""

# Load the needed packages
from functools import partial
import os
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
        super(FileNavigator, self).__init__(name=name, parent=parent)
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
            self.Vradar.change(radar)
            return
        except:
            try:
                radar = pyart.io.read(filename)
                # Add the filename for Display
                radar.filename = filename
                self.Vradar.change(radar)
                return
            except:
                import traceback
                print(traceback.format_exc())
                radar_warning = True

        try:
            grid = pyart.io.read_grid(
                filename, delay_field_loading=True)
            self.Vgrid.change(grid)
            return
        except:
            try:
                grid = pyart.io.read_grid(filename)
                self.Vgrid.change(grid)
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


_plugins = [FileNavigator]
