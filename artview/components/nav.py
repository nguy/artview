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
from ..icons import icons
#from .. import menu


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
##        if Vtilt is None:
##            self.Vtilt = Variable(0)
##        else:
##            self.Vtilt = Vtilt

        self.sharedVariables = {"Vradar": None,
                                "Vgrid": None,
                                "Vfilelist": None}
        # Connect the components
        self.connectAllVariables()

        self.get_variables()

        # Set up the Display layout
        self.generalLayout = QtGui.QVBoxLayout()
##        self.generalLayout.addWidget(self.createDispUI())
        self.generalLayout.addWidget(self.createNavButtonUI())
        self.generalLayout.addWidget(self.createNavToolbar())
##        self.generalLayout.addWidget(self.createTiltButtonUI())
        self.generalLayout.addWidget(self.createInfoUI())

        self.layout.addLayout(self.generalLayout, 0, 0, 1, 2)

        self.show()

    ######################
    #   Layout Methods   #
    ######################

    def createDispUI(self):
        '''
        Mount the Display layout.
        User may select another Display.
        '''
        groupBox = QtGui.QGroupBox("File Navigation")
        gBox_layout = QtGui.QGridLayout()

        self.dispCombo = QtGui.QComboBox()
        gBox_layout.addWidget(QtGui.QLabel("Select Display Link"), 0, 0)
        gBox_layout.addWidget(self.dispCombo, 0, 1, 1, 1)

        self.DispChoiceList = []
        self.components = componentsList
        for component in self.components:
            self.dispCombo.addItem(component.name)
            self.DispChoiceList.append(component)
        self.dispCombo.setCurrentIndex(0)

        self.menu = self.components[0]
        self.chooseDisplay()
        groupBox.setLayout(gBox_layout)

        return groupBox

    def createNavButtonUI(self):
        '''Mount the file navigation buttons.'''
        groupBox = QtGui.QGroupBox("File Navigation")
        gBox_layout = QtGui.QGridLayout()

##        arrow_icons = icons.get_arrow_icon_dict()
        self.firstbutton = QtGui.QPushButton("First")
        self.firstbutton.setToolTip("Load first file in directory")
##        self.firstbutton.setIcon(arrow_icons['first'])
        self.firstbutton.clicked.connect(self.goto_first_file)
        gBox_layout.addWidget(self.firstbutton, 0, 0, 1, 1)

        self.prevbutton = QtGui.QPushButton("Previous")
        self.prevbutton.setToolTip("Load previous file")
##        self.prevbutton.setIcon(arrow_icons['previous'])
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
        '''Mount the file navigation buttons.'''
        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        groupBox = QtGui.QGroupBox("File Navigation")
        gBox_layout = QtGui.QGridLayout()

     #   arrow_icons = icons.get_arrow_icon_dict()
        self.navtoolbar = QtGui.QToolBar()
##        pixfirst = QtGui.QPixmap('icons/player_play.png')
        pixfirst = QtGui.QPixmap(os.sep.join([parentdir, 'icons',"arrow_go_first_icon.png"]))
        pixprev = QtGui.QPixmap(os.sep.join([parentdir, 'icons',"arrow_go_previous_icon.png"]))
        pixnext = QtGui.QPixmap(os.sep.join([parentdir, 'icons',"arrow_go_next_icon.png"]))
        pixlast = QtGui.QPixmap(os.sep.join([parentdir, 'icons',"arrow_go_last_icon.png"]))
        self.act_first = self.navtoolbar.addAction(
            QtGui.QIcon(pixfirst), 'First', self.goto_first_file)
        self.act_prev = self.navtoolbar.addAction(
            QtGui.QIcon(pixprev), 'Previous', self.goto_prev_file)
        self.act_next = self.navtoolbar.addAction(
            QtGui.QIcon(pixnext), 'Next', self.goto_next_file)
        self.act_las = self.navtoolbar.addAction(
            QtGui.QIcon(pixlast), 'Last', self.goto_last_file)

        gBox_layout.addWidget(self.navtoolbar)
        groupBox.setLayout(gBox_layout)

        return groupBox

#     def createTiltButtonUI(self):
#         '''Mount the Tilt button.'''
#         groupBox = QtGui.QGroupBox("Tilt Navigation")
#         gBox_layout = QtGui.QGridLayout()
#
#         self.tiltupbutton = QtGui.QPushButton("Up")
#         self.tiltupbutton.setToolTip("Load next tilt up")
#         self.tiltupbutton.clicked.connect(self.go_tilt_up)
#         gBox_layout.addWidget(self.tiltupbutton, 0, 0, 1, 1)
#
#         self.tiltdnbutton = QtGui.QPushButton("Down")
#         self.tiltdnbutton.setToolTip("Load next tilt down")
#         self.tiltdnbutton.clicked.connect(self.go_tilt_down)
#         gBox_layout.addWidget(self.tiltdnbutton, 0, 1, 1, 1)
#
#         groupBox.setLayout(gBox_layout)

        return groupBox

    def createInfoUI(self):
        '''Mount the Info layout.'''
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

    def _update_InfoUI(self):
        '''Update the info label.'''
        self.dirIn = os.path.dirname(self.Vradar.value.filename)
        self.infodir.setText("Directory: %s"%(self.dirIn))
        self.infofile.setText("File: %s"%(
            os.path.basename(self.Vradar.value.filename)))

    #########################
    #   Selection Methods   #
    #########################

    def chooseDisplay(self):
        '''Get Display.'''
        selection = self.dispCombo.currentIndex()
        Vradar = getattr(self.DispChoiceList[0], str("Vradar"))

        # Grab shared variables from the Menu instance, always zero
        Vfilelist = getattr(self.DispChoiceList[0], str("Vfilelist"))

        self.dispCombo.setCurrentIndex(selection)

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

    def get_variables(self):
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
        self.AdvanceFileSelect(self.fileindex)

    def goto_next_file(self):
        self.fileindex = self.fileindex + 1
        self.AdvanceFileSelect(self.fileindex)

#     def TiltSelectCmd(self, ntilt):
#         '''
#         Captures tilt selection and update tilt
#         :py:class:`~artview.core.core.Variable`.
#         '''
#         if ntilt < 0:
#             ntilt = len(self.Vradar.value.sweep_number['data'][:]) - 1
#         elif ntilt >= len(self.Vradar.value.sweep_number['data'][:]):
#             ntilt = 0
#         self.Vtilt.change(ntilt)
#         self.menu._openfile()
#
#     def go_tilt_up(self):
#         self.TiltSelectCmd(self.Vtilt.value + 1)
#
#     def go_tilt_down(self):
#         self.TiltSelectCmd(self.Vtilt.value -1)

_plugins = [FileNavigator]
