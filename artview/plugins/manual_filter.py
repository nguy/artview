"""
manual_unfold.py
"""

# Load the needed packages
import code
import pyart

import sys
import os
import numpy as np
import collections

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '...')
sys.path.insert(0, path)

import artview

from ..core import Component, Variable, common, QtGui, QtCore, componentsList


class ManualFilter(Component):
    '''
    Use of Points to remove data from Radar.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vpoints = None  #: see :ref:`shared_variable`
    Vfield = None  #: see :ref:`shared_variable`
    Vgatefilter = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("ManualFilter").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None, Vpoints=None, Vfield=None,
                 Vgatefilter=None, name=" ManualFilter", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable.
            A value of None will instantiate a empty variable.
        Vpoints : :py:class:`~artview.core.core.Variable` instance
            Points signal variable.
            A value of None will instantiate a empty variable.
        Vfield : :py:class:`~artview.core.core.Variable` instance
            Field signal variable. If None start new one with empty string.
        Vgatefilter : :py:class:`~artview.core.core.Variable` instance
            Gatefilter signal variable.
            A value of None will instantiate a empty variable.
        name : string
            Field Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(ManualFilter, self).__init__(name=name, parent=parent)

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

        if Vpoints is None:
            self.Vpoints = Variable(None)
        else:
            self.Vpoints = Vpoints

        if Vfield is None:
            self.Vfield = Variable('')
        else:
            self.Vfield = Vfield

        if Vgatefilter is None:
            self.Vgatefilter = Variable(None)
        else:
            self.Vgatefilter = Vgatefilter

        self.sharedVariables = {"Vradar": self.NewRadar,
                                "Vpoints": None,
                                "Vfield": self.NewField,
                                "Vgatefilter": None, }
        self.connectAllVariables()

        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        self.fieldBox = QtGui.QComboBox()
        self.fieldBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fieldBox.setToolTip("Select variable/field in data file.\n"
                                 "'Field Window' will launch popup.\n")
        self.fieldBox.activated[str].connect(self._fieldAction)
        self.layout.addWidget(QtGui.QLabel("Current field"), 0, 0)
        self.layout.addWidget(self.fieldBox, 0, 1)

        self.filterButton = QtGui.QPushButton("Filter Gates in the GateFilter")
        self.filterButton.clicked.connect(self.removeFromFilter)
        self.layout.addWidget(self.filterButton, 1, 1)

        self.fieldButton = QtGui.QPushButton(
            "Filter Gates in the Current Field")
        self.fieldButton.clicked.connect(self.removeFromField)
        self.layout.addWidget(self.fieldButton, 2, 1)

        self.radarButton = QtGui.QPushButton("Filter Gates in the Radar")
        self.radarButton.clicked.connect(self.removeFromRadar)
        self.layout.addWidget(self.radarButton, 3, 1)

        self.resetButton = QtGui.QPushButton("Reset GateFilter")
        self.resetButton.clicked.connect(self.reset)
        self.layout.addWidget(self.resetButton, 4, 1)

        self.buttonHelp = QtGui.QPushButton("Help")
        self.buttonHelp.setToolTip("About using Manual Filter")
        self.buttonHelp.clicked.connect(self._displayHelp)
        self.layout.addWidget(self.buttonHelp, 6, 1)

        self.show()

    def removeFromFilter(self):
        '''Filter selected gates.'''
        if self.Vpoints.value is None:
            return
        mask_ray = self.Vpoints.value.axes['ray_index']['data'][:]
        mask_range = self.Vpoints.value.axes['range_index']['data'][:]

        if self.Vgatefilter.value is None:
            if self.Vradar.value is None:
                print("Error can not creat mask from none radar")
                return
            gatefilter = pyart.filters.GateFilter(self.Vradar.value)
            mask = gatefilter.gate_excluded
            mask[mask_ray, mask_range] = True
            gatefilter._merge(mask, 'or', True)
            self.Vgatefilter.change(gatefilter)
        else:
            mask = self.Vgatefilter.value.gate_excluded
            mask[mask_ray, mask_range] = True
            self.Vgatefilter.value._merge(mask, 'or', True)
            self.Vgatefilter.update()

    def removeFromField(self):
        '''Remove selected points from current field in Radar.'''
        if (self.Vpoints.value is None or
            self.Vradar.value is None or
            self.Vfield.value not in self.Vradar.value.fields):
            return

        mask_ray = self.Vpoints.value.axes['ray_index']['data'][:]
        mask_range = self.Vpoints.value.axes['range_index']['data'][:]

        data = self.Vradar.value.fields[self.Vfield.value]['data']
        mask = np.ma.getmaskarray(data)
        mask[mask_ray, mask_range] = True
        self.Vradar.value.fields[self.Vfield.value]['data'] = np.ma.array(data,
                                                                    mask=mask)

        self.Vradar.value.changed = True
        self.Vradar.update()

    def removeFromRadar(self):
        '''Remove selected points from all fields in Radar.'''
        if (self.Vpoints.value is None or
            self.Vradar.value is None):
            return

        mask_ray = self.Vpoints.value.axes['ray_index']['data'][:]
        mask_range = self.Vpoints.value.axes['range_index']['data'][:]

        for field in self.Vradar.value.fields.keys():
            data = self.Vradar.value.fields[field]['data']
            mask = np.ma.getmaskarray(data)
            mask[mask_ray, mask_range] = True
            self.Vradar.value.fields[field]['data'] = np.ma.array(data,
                                                                  mask=mask)

        self.Vradar.value.changed = True
        self.Vradar.update()

    def reset(self):
        '''Reset Getafilter to a empty one.'''
        if self.Vgatefilter.value is not None:
            self.Vgatefilter.value.include_all()
            self.Vgatefilter.update()

    def _fillFieldBox(self):
        '''Fill in the Field Window Box with current variable names.'''
        self.fieldBox.clear()
        # Loop through and create each field button
        if self.Vradar.value is not None:
            for field in self.Vradar.value.fields.keys():
                self.fieldBox.addItem(field)

    def _fieldAction(self, text):
        '''Define action for Field Button selection.'''
        self.Vfield.change(str(text))

    def _displayHelp(self):
        ''' Launch pop-up help window.'''
        text = (
            "<b>Using the Manual Filter Tool</b><br><br>"
            "The SelectRegion tool is used to select points on an "
            "ARTView Display.<br>"
            "The selected region consists of points loaded into <br>"
            "a Vpoints shared variable.<br>"
            "Operation is performed on these points.<br><br>"
            "<i>Purpose</i>:<br>"
            "Filter a selected region through GateFilter, individual "
            "fields, or remove values in a radar file.<br><br>"
            "<i>Functions</i>:<br>"
            " Primary Mouse Button (e.g. left button)- add vertex<br>"
            " Hold button to draw free-hand path<br>"
            " Secondary Button (e.g. right button)- close path<br><br>"
            "A message 'Closed Region' appears in status bar when "
            "boundary is properly closed.<br><br>"
            "Select the desired action to be performed.<br><br>"
            "For a demonstration, a "
            "<a href='https://youtu.be/VXUZBiA3HfU'>Video Tutorial</a> "
            "has been created.<br>"
            )
        common.ShowLongTextHyperlinked(text)

    def NewRadar(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vradar <artview.core.core.Variable>`.
        '''
        # test for None
        if self.Vradar.value is None:
            self.fieldBox.clear()
            return

        self._fillFieldBox()

    def NewField(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vfield <artview.core.core.Variable>`.

        '''
        idx = self.fieldBox.findText(self.Vfield.value)
        self.fieldBox.setCurrentIndex(idx)


_plugins = [ManualFilter]
