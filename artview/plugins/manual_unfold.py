"""
manual_unfold.py
"""

# Load the needed packages
import code
import pyart

import sys
import os
import numpy as np

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

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

        if Vpoints is None:
            self.Vpoints = Variable(None)
        else:
            self.Vpoints = Vpoints

        self.sharedVariables = {"Vradar": self.newRadar,
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

        self.newRadar(None,None,True)
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
        original_data = radar.fields[vel]['data'].copy()
        if corrVel in self.Vradar.value.fields.keys():
            data = radar.fields[corrVel]['data'].copy()
        else:
            data = original_data
        ray = points.axes['ray_index']['data']
        rng = points.axes['range_index']['data']
        nyquist = self.nyquistVelocity.value()
        if side == 'positive':
            data[ray,rng] = np.where(
                original_data[ray,rng] > 0,
                -2 * nyquist + original_data[ray,rng], data[ray,rng])
        elif side == 'negative':
            data[ray,rng] = np.where(
                original_data[ray,rng] < 0,
                2 * nyquist + original_data[ray,rng], data[ray,rng])

        strong_update = False  # insertion is weak, overwrite strong
        if corrVel in self.Vradar.value.fields.keys():
            strong_update = True

        radar.add_field_like(vel, corrVel, data, replace_existing=True)
        if 'valid_min' not in radar.fields[corrVel]:
                radar.fields[corrVel]['valid_min'] = - 2 * nyquist
        if 'valid_max' not in radar.fields[corrVel]:
                radar.fields[corrVel]['valid_max'] = 2 * nyquist
        self.Vradar.update(strong_update)

    def newRadar(self, variable, value, strong):
        '''respond to change in radar.'''
        if self.Vradar.value is None:
            return

        if strong:
            nyquist_vel = self.Vradar.value.get_nyquist_vel(0, True)
            self.nyquistVelocity.setValue(nyquist_vel)


_plugins = [ManualUnfold]
