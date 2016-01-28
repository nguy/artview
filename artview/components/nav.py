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

from ..core import Component, Variable, common, QtGui, QtCore, componentsList


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
            self.Vfilelist = Variable(0)
        else:
            self.Vfilelist = Vfilelist

        self.sharedVariables = {"Vradar": None,
                                "Vgrid": None,
                                "Vfilelist": None}
        # Connect the components
        self.connectAllVariables()

        # Initialize variables
        self.get_variables()

        # Set up the Display layout
        self.generalLayout = QtGui.QVBoxLayout()
        self.generalLayout.addWidget(self.createNavToolbar())
        self.generalLayout.addWidget(self.createInfoUI())
        self.generalLayout.addWidget(self.createHelpUI())

        self.layout.addLayout(self.generalLayout, 0, 0, 1, 2)

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
        self.prevbutton.setIconSize(QtCore.QSize(32,32))
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
        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        groupBox = QtGui.QGroupBox("File Navigation")
        gBox_layout = QtGui.QGridLayout()

        self.navtoolbar = QtGui.QToolBar()
        pixfirst = QtGui.QPixmap(os.sep.join([parentdir, 'icons',"arrow_go_first_icon.png"]))
        pixprev = QtGui.QPixmap(os.sep.join([parentdir, 'icons',"arrow_go_previous_icon.png"]))
        pixnext = QtGui.QPixmap(os.sep.join([parentdir, 'icons',"arrow_go_next_icon.png"]))
        pixlast = QtGui.QPixmap(os.sep.join([parentdir, 'icons',"arrow_go_last_icon.png"]))
        self.act_first = self.navtoolbar.addAction(
            QtGui.QIcon(pixfirst),
            "First file: %s"%(self.Vfilelist.value[0]),
            self.goto_first_file)
        self.act_prev = self.navtoolbar.addAction(
            QtGui.QIcon(pixprev),
            "Previous file: %s"%(self.Vfilelist.value[self.fileindex - 1]),
            self.goto_prev_file)
        self.act_next = self.navtoolbar.addAction(
            QtGui.QIcon(pixnext),
            "Next file: %s"%(self.Vfilelist.value[self.fileindex + 1]),
            self.goto_next_file)
        self.act_last = self.navtoolbar.addAction(
            QtGui.QIcon(pixlast),
            "Last file: %s"%(self.Vfilelist.value[-1]),
            self.goto_last_file)

        gBox_layout.addWidget(self.navtoolbar)
        groupBox.setLayout(gBox_layout)

        return groupBox

    def createInfoUI(self):
        '''Mount the information text.'''
        groupBox = QtGui.QGroupBox("File Information")
        gBox_layout = QtGui.QGridLayout()

        self.dirIn = os.path.dirname(self.Vradar.value.filename)
        self.infodir = QtGui.QLabel("Directory: %s"%(self.dirIn))
        self.infodir.setStyleSheet('font: italic 12px')
        gBox_layout.addWidget(self.infodir, 0, 0, 1, 1)

        self.infofile = QtGui.QLabel("File: %s"%(
            os.path.basename(self.Vradar.value.filename)))
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
                    "LinkPlugins menu for various components, you can<br>"
                    "control which Display is navigated."
                    )
        self.help = QtGui.QLabel(helptext)
        self.infodir.setStyleSheet('font: italic 12px')
        gBox_layout.addWidget(self.help, 0, 0, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def _update_InfoUI(self):
        '''Update the info label.'''
        self.dirIn = os.path.dirname(self.Vradar.value.filename)
        self.infodir.setText("Directory: %s"%(self.dirIn))
        self.infofile.setText("File: %s"%(
            os.path.basename(self.Vradar.value.filename)))

    #########################
    #   Selection Methods   #
    #########################

    def get_variables(self):
        '''Initialize variables.'''
        # Set the menu
        self.components = componentsList
        self.menu = self.components[0]
        # Grab shared variables from the Menu instance, always zero
        Vradar = getattr(self.menu, str("Vradar"))
        Vfilelist = getattr(self.menu, str("Vfilelist"))
        self.disconnectAllVariables()
        self.Vradar = Vradar
        self.Vfilelist = Vfilelist

        # Find the file index statring
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None.")
            return
        else:
            filename = os.path.basename(self.Vradar.value.filename)
            if filename in self.Vfilelist.value:
                self.fileindex = self.Vfilelist.value.index(filename)
            else:
                self.fileindex = 0

        self.connectAllVariables()

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
        self.filename = os.path.join(self.dirIn, self.Vfilelist.value[findex])
        self.menu._openfile(filename=self.filename)
        self._update_InfoUI()

    def goto_first_file(self):
        self.fileindex = 0
        self.AdvanceFileSelect(self.fileindex)

    def goto_last_file(self):
        self.fileindex = len(self.Vfilelist.value) - 1
        self.AdvanceFileSelect(self.fileindex)

    def goto_prev_file(self):
        self.fileindex = self.fileindex - 1
        self.act_prev.setToolTip(
            'Previous file: %s'%self.Vfilelist.value[self.fileindex - 1])
        self.act_next.setToolTip(
            'Next file: %s'%self.Vfilelist.value[self.fileindex + 1])
        self.AdvanceFileSelect(self.fileindex)

    def goto_next_file(self):
        self.fileindex = self.fileindex + 1
        self.act_prev.setToolTip(
            'Previous file: %s'%self.Vfilelist.value[self.fileindex - 1])
        self.act_next.setToolTip(
            'Next file: %s'%self.Vfilelist.value[self.fileindex + 1])
        self.AdvanceFileSelect(self.fileindex)

_plugins = [FileNavigator]
