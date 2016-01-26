"""
nav.py
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

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("FileNavigator").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, name="FileNavigator", parent=None):
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
        self.Vradar = Variable(None)
        self.Vgrid = Variable(None)
        self.Vtilt = Variable(0)
        self.sharedVariables = {"Vradar": None,
                                "Vgrid": None,
                                "Vtilt": None}
        # Connect the components
        self.connectAllVariables()
        self.field = None

        self.generalLayout = QtGui.QVBoxLayout()
        # Set the Variable layout
        self.generalLayout.addWidget(self.createDispUI())
        self.generalLayout.addWidget(self.createNavButtonUI())
        self.generalLayout.addWidget(self.createTiltButtonUI())
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

        self.chooseDisplay()
        groupBox.setLayout(gBox_layout)

        return groupBox

    def createNavButtonUI(self):
        '''Mount the Action layout.'''
        groupBox = QtGui.QGroupBox("File Navigation")
        gBox_layout = QtGui.QGridLayout()

##        arrow_icons = icons.get_arrow_icon_dict()
        self.firstbutton = QtGui.QPushButton("First")
        self.firstbutton.setToolTip("Load first file in directory")
##        self.firstbutton.setIcon(arrow_icons['first'])
        self.firstbutton.clicked.connect(
            lambda findex=0: self.parent.AdvanceFileSelect(findex))
        gBox_layout.addWidget(self.firstbutton, 0, 0, 1, 1)

        self.prevbutton = QtGui.QPushButton("Previous")
        self.prevbutton.setToolTip("Load previous file")
##        self.prevbutton.setIcon(arrow_icons['previous'])
        self.prevbutton.setIconSize(QtCore.QSize(32,32))
        self.prevbutton.clicked.connect(
#            lambda findex=self.fileindex - 1: self.AdvanceFileSelect(findex))
            lambda findex=self.parent.fileindex - 1: self.parent.AdvanceFileSelect(findex))
        gBox_layout.addWidget(self.prevbutton, 0, 1, 1, 1)

        self.nextbutton = QtGui.QPushButton("Next")
        self.nextbutton.setToolTip("Load next file")
        self.nextbutton.clicked.connect(
            lambda findex=self.parent.fileindex + 1: self.parent.AdvanceFileSelect(findex))
        gBox_layout.addWidget(self.nextbutton, 0, 2, 1, 1)

        self.lastbutton = QtGui.QPushButton("Last")
        self.lastbutton.setToolTip("Load last file in directory")
        self.lastbutton.clicked.connect(
            lambda findex=(len(self.parent.filelist) - 1):
            self.parent.AdvanceFileSelect(findex))
        gBox_layout.addWidget(self.lastbutton, 0, 3, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def createTiltButtonUI(self):
        '''Mount the Tilt button.'''
        groupBox = QtGui.QGroupBox("Tilt Navigation")
        gBox_layout = QtGui.QGridLayout()

        self.tiltup = QtGui.QPushButton("Up")
        self.tiltup.setToolTip("Load next tilt up")
#        self.tiltup.clicked.connect(self.TiltSelectCmd(self.Vtilt.value + 1))
        gBox_layout.addWidget(self.tiltup, 0, 0, 1, 1)

        self.tiltdn = QtGui.QPushButton("Down")
        self.tiltdn.setToolTip("Load next tilt down")
#        self.tiltdn.clicked.connect(self.TiltSelectCmd(self.Vtilt.value - 1))
        gBox_layout.addWidget(self.tiltdn, 0, 1, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def createInfoUI(self):
        '''Mount the Info layout.'''
        groupBox = QtGui.QGroupBox("File Information")
        gBox_layout = QtGui.QGridLayout()

        self.infodir = QtGui.QLabel("Directory: %s"%(
            os.path.dirname(self.Vradar.value.filename)))
        self.infodir.setStyleSheet('font: italic 10px')
        gBox_layout.addWidget(self.infodir, 0, 0, 1, 1)

        self.infofile = QtGui.QLabel("File: %s"%(
            os.path.basename(self.Vradar.value.filename)))
        self.infofile.setStyleSheet('font: italic 10px')
        gBox_layout.addWidget(self.infofile, 1, 0, 1, 1)

        self.Vradar.value.filename

        groupBox.setLayout(gBox_layout)

        return groupBox

    def _update_InfoUI(self):
        '''Update the info label.'''
        self.infostatus.setText("Directory: %s"%(
            os.path.dirname(self.Vradar.value.filename)))
        self.infofile.setText("File: %s"%(
            os.path.basename(self.Vradar.value.filename)))

    #########################
    #   Selection Methods   #
    #########################

    def chooseDisplay(self):
        '''Get Display.'''
        selection = self.dispCombo.currentIndex()
        Vradar = getattr(self.DispChoiceList[selection], str("Vradar"))

        self.dispCombo.setCurrentIndex(selection)

        self.disconnectAllVariables()
        self.Vradar = Vradar
        self.connectAllVariables()

    def AdvanceFileSelect(self, findex):
        '''Captures a selection and open file.'''
        if findex > (len(self.parent.filelist)-1):
            print(len(self.parent.filelist))
            msg = "End of directory, cannot advance!"
            common.ShowWarning(msg)
            findex = (len(self.parent.filelist) - 1)
            return
        if findex < 0:
            msg = "Beginning of directory, must move forward!"
            common.ShowWarning(msg)
            findex = 0
            return
        self.parent.fileindex = findex
        self.filename = os.path.join(self.parent.dirIn, self.parent.filelist[findex])
        self.parent._openfile()
#        self.menu._openfile()

    def TiltSelectCmd(self, ntilt):
        '''
        Captures tilt selection and update tilt
        :py:class:`~artview.core.core.Variable`.
        '''
        if ntilt < 0:
            ntilt = len(self.rTilts)-1
        elif ntilt >= len(self.rTilts):
            ntilt = 0
        self.Vtilt.change(ntilt)

    def NewRadar(self, variable, value, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vradar <artview.core.core.Variable>`.

        This will:

        * Update fields and tilts lists and MenuBoxes
        * Check radar scan type and reset limits if needed
        * Reset units and title
        * If strong update: update plot
        '''
        # test for None
        if self.Vradar.value is None:
            self.fieldBox.clear()
            self.tiltBox.clear()
            return

        # Get the tilt angles
        self.rTilts = self.Vradar.value.sweep_number['data'][:]
        # Get field names
        self.fieldnames = self.Vradar.value.fields.keys()

        # Check the file type and initialize limts
        self._check_file_type()

        # Update field and tilt MenuBox
        self._fillTiltBox()
        self._fillFieldBox()

        self.units = self._get_default_units()
        self.title = self._get_default_title()
        if strong:
            self._update_plot()
            self._update_infolabel()

    ######################
    #   Filter Methods   #
    ######################


_plugins = [FileNavigator]
