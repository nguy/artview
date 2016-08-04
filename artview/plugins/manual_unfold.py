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


class ManualUnfold(Component):
    '''
    Use of Points to Unfold Velocity in Radar
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vpoints = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("ManualUnfold").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None, Vpoints=None, name=" ManualUnfold",
                 parent=None):
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
        name : string
            Field Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(ManualUnfold, self).__init__(name=name, parent=parent)
        self.lockNyquist = False

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

        if Vpoints is None:
            self.Vpoints = Variable(None)
        else:
            self.Vpoints = Vpoints

        self.sharedVariables = {"Vradar": self.NewRadar,
                                "Vpoints": None}
        self.connectAllVariables()

        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        self.velField = QtGui.QLineEdit(
            pyart.config.get_field_name('velocity'))
        self.layout.addWidget(QtGui.QLabel("vel_field"), 0, 0)
        self.layout.addWidget(self.velField, 0, 1)

        self.corrVelField = QtGui.QLineEdit(
            pyart.config.get_field_name('corrected_velocity'))
        self.layout.addWidget(QtGui.QLabel("corr_vel_field"), 1, 0)
        self.layout.addWidget(self.corrVelField, 1, 1)

        self.nyquistVelocity = QtGui.QDoubleSpinBox()
        self.nyquistVelocity.setRange(-1, 1000)
        self.nyquistVelocity.setValue(-1)
        self.layout.addWidget(QtGui.QLabel("nyquist_velocity"), 2, 0)
        self.layout.addWidget(self.nyquistVelocity, 2, 1)

        self.positiveButton = QtGui.QPushButton("Unfold Positive Values")
        self.positiveButton.clicked.connect(self.positiveUnfold)
        self.layout.addWidget(self.positiveButton, 3, 1)

        self.negativeButton = QtGui.QPushButton("Unfold Negative Values")
        self.negativeButton.clicked.connect(self.negativeUnfold)
        self.layout.addWidget(self.negativeButton, 4, 1)

        # list for undoing: (unfold matriz, nyquist_vel)
        self.unfoldList = collections.deque(maxlen=30)
        self.foldButton = QtGui.QPushButton("Fold Back")
        self.foldButton.clicked.connect(self.foldBack)
        self.layout.addWidget(self.foldButton, 5, 1)

        self.buttonHelp = QtGui.QPushButton("Help")
        self.buttonHelp.setToolTip("About using Manual Unfold")
        self.buttonHelp.clicked.connect(self._displayHelp)
        self.layout.addWidget(self.buttonHelp, 6, 1)

        self.NewRadar(None, True)
        self.show()

    def getFieldNames(self):
        vel = str(self.velField.text())
        if vel == '':
            vel = pyart.config.get_field_name('velocity')
        if vel not in self.Vradar.value.fields:
            common.ShowWarning(
                "vel_field not in Radar, can not perform correction")

        corrVel = str(self.corrVelField.text())
        if corrVel == '':
            corrVel = pyart.config.get_field_name('corrected_velocity')

        return vel, corrVel

    def positiveUnfold(self):
        self.unfold('positive')

    def negativeUnfold(self):
        self.unfold('negative')

    def unfold(self, side):
        # test radar
        radar = self.Vradar.value
        points = self.Vpoints.value
        if radar is None:
            common.ShowWarning("Radar is None, can not perform correction")
            return

        if points is None:
            common.ShowWarning("Points is None, can not perform correction")
            return

        if ('ray_index' not in points.axes or
            'range_index' not in points.axes):
            common.ShowWarning(
                "Error: Points must have axes 'ray_index' and 'range_index'")
            return

        vel, corrVel = self.getFieldNames()
        original_data = radar.fields[vel]['data']
        if corrVel in self.Vradar.value.fields.keys():
            data = radar.fields[corrVel]['data'].copy()
        else:
            data = original_data.copy()
        ray = points.axes['ray_index']['data']
        rng = points.axes['range_index']['data']
        nyquist = self.nyquistVelocity.value()
        if side == 'positive':
            data[ray, rng] = np.ma.where(
                original_data[ray, rng] > 0,
                -2 * nyquist + original_data[ray, rng], data[ray, rng])
        elif side == 'negative':
            data[ray, rng] = np.ma.where(
                original_data[ray, rng] < 0,
                2 * nyquist + original_data[ray, rng], data[ray, rng])

        strong_update = False  # insertion is weak, overwrite strong
        if corrVel in self.Vradar.value.fields.keys():
            strong_update = True

        radar.add_field_like(vel, corrVel, data, replace_existing=True)
        if 'valid_min' not in radar.fields[corrVel]:
            radar.fields[corrVel]['valid_min'] = - 1.5 * nyquist
        if 'valid_max' not in radar.fields[corrVel]:
            radar.fields[corrVel]['valid_max'] = 1.5 * nyquist
        self.lockNyquist = True
        self.Vradar.value.changed = True
        self.Vradar.update(strong_update)

        # save for undoing
        unfold = np.zeros_like(original_data, dtype=np.int8)
        if side == 'positive':
            unfold[ray, rng] = np.where(original_data[ray, rng] > 0, -1, 0)
        elif side == 'negative':
            unfold[ray, rng] = np.where(original_data[ray, rng] < 0, 1, 0)

        self.unfoldList.append((unfold, nyquist))

    def foldBack(self):
        '''Undo last unfolding.'''
        vel, corrVel = self.getFieldNames()
        radar = self.Vradar.value
        if len(self.unfoldList) == 0 or corrVel not in radar.fields.keys():
            common.ShowWarning("No folding to be undone")
            return

        unfold, nyquist = self.unfoldList.pop()
        data = radar.fields[corrVel]['data']
        data = data - 2 * unfold * nyquist
        radar.fields[corrVel]['data'] = data
        self.lockNyquist = True
        self.Vradar.value.changed = True
        self.Vradar.update()

    def _displayHelp(self):
        ''' Launch pop-up help window.'''
        text = (
            "<b>Using the Manual Unfold Tool</b><br><br>"
            "The SelectRegion tool is used to select points on an "
            "ARTView Display.<br>"
            "The selected region consists of points loaded into a "
            "Vpoints shared variable.<br>"
            "Operation is performed on these points.<br><br>"
            "<i>Purpose</i>:<br>"
            "Unfold postive and/or negative aliased Doppler velocity <br>"
            "values in a radar file from a selected region (path) <br>"
            "in the display window using the Mouse.<br><br>"
            "<i>Functions</i>:<br>"
            " Primary Mouse Button (e.g. left button)- add vertex<br>"
            " Hold button to draw free-hand path<br>"
            " Secondary Button (e.g. right button)- close path<br><br>"
            "A message 'Closed Region' appears in status bar when "
            "boundary is properly closed.<br><br>"
            "Select the desired unfolding to be performed.<br><br>"
            "For a demonstration, a "
            "<a href='https://youtu.be/B_BmYV7GdCA'>Video Tutorial</a> "
            "has been created.<br>"
            )
        common.ShowLongTextHyperlinked(text)

    def NewRadar(self, variable, strong):
        '''respond to change in radar.'''
        if self.Vradar.value is None:
            return

        if strong and not self.lockNyquist:
            nyquist_vel = self.Vradar.value.get_nyquist_vel(0, True)
            if nyquist_vel > 0:
                self.nyquistVelocity.setValue(nyquist_vel)
        elif self.lockNyquist:
            self.lockNyquist = False

_plugins = [ManualUnfold]
