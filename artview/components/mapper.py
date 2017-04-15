"""
mapper.py
"""
from __future__ import print_function
# Load the needed packages
from functools import partial

import pyart
from pyart.config import get_field_name
import time
import os

from ..core import (Component, Variable, common, QtWidgets, QtGui,
                    QtCore, VariableChoose, log)

class Mapper(Component):
    '''
    Interface for executing :py:func:`pyart.map.grid_from_radars`
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgrid = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class'''
        kwargs, independent = \
            common._SimplePluginStart("Mapper").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None, Vgrid=None, name="Mapper", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable.
            A value of None initializes an empty Variable.
        Vgrid : :py:class:`~artview.core.core.Variable` instance
            Grid signal variable.
            A value of None initializes an empty Variable.
        name : string
            Field Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated w/ parent PyQt instance
        '''
        super(Mapper, self).__init__(name=name, parent=parent)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QGridLayout(self.central_widget)

        self.mountUI()

        self.parameters = {
            "radars": None,
            "gridshape": (1, 500, 500),
            "grid_limits": (
                (2000, 3000),
                (-250000, 250000),
                (-250000, 250000)),
            "grid_origin": (0, 0),
            "grid_origin_lat": 0,
            "grid_origin_lon": 0,
            "grid_origin_alt": 0,
            "gridding_algo": 'map_gates_to_grid',
            "fields": [],
            "refl_filter_flag": True,
            "refl_field": get_field_name('reflectivity'),
            "max_refl": 100,
            "map_roi": True,
            "weighting_function": "Barnes",
            "toa": 17000,
            "roi_func": "dist_beam",
            "constant_roi": 500,
            "z_factor": 0.05,
            "xy_factor": 0.02,
            "min_radius": 500,
            "bsp": 1,
            "copy_field_data": True,
            "algorithm": "kd_tree",
            "leafsize": 10,
            }

        self.general_parameters_type = [
            ("grid_origin_lat", float),
            ("grid_origin_lon", float),
            ("grid_origin_alt", float),
            ("gridding_algo", ('map_to_grid', 'map_gates_to_grid')),
            ("refl_filter_flag", bool),
            ("refl_field", str),
            ("max_refl", float),
            ("map_roi", bool),
            ("weighting_function", ("Barnes", "Cressman")),
            ("toa", float),
            ]
        self.roi_parameters_type = [
            ("roi_func", ("constant", "dist", "dist_beam")),
            ("constant_roi", float),
            ("z_factor", float),
            ("xy_factor", float),
            ("min_radius", float),
            ("bsp", float)
            ]
        self.gridding_parameters_type = [
            ("copy_field_data", bool),
            ("algorithm", ("kd_tree", "ball_tree")),
            ("leafsize", int),
            ]

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

        if Vgrid is None:
            self.Vgrid = Variable(None)
        else:
            self.Vgrid = Vgrid
        self.sharedVariables = {"Vradar": self.NewRadar,
                                "Vgrid": None}
        self.connectAllVariables()

        self.NewRadar(None, True)
        self.show()

    def mountUI(self):
        '''Mount Options Layout.'''

        self.despeckleButton = QtWidgets.QPushButton("Map")
        self.despeckleButton.clicked.connect(self.grid_from_radars)
        self.layout.addWidget(self.despeckleButton, 7, 0, 1, 2)

        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir))
        config_icon = QtGui.QIcon(os.sep.join(
            [parentdir, 'icons', "categories-applications-system-icon.png"]))
        self.configButton = QtWidgets.QPushButton(config_icon,"")
        self.layout.addWidget(self.configButton, 7, 2)
        self.configMenu = QtWidgets.QMenu(self)
        self.configButton.setMenu(self.configMenu)

        self.configMenu.addAction(QtWidgets.QAction("Set General Parameters", self,
                                                triggered=self.setParameters))
        self.configMenu.addAction(QtWidgets.QAction("Set Radius of Influence Parameters", self,
                                                triggered=self.setRoiParameters))
        self.configMenu.addAction(QtWidgets.QAction("Set map_to_grid Parameters", self,
                                                triggered=self.setGriddingParameters))
        self.fieldMenu = self.configMenu.addMenu("Fields")
        self.configMenu.addAction(QtWidgets.QAction("Help", self,
                                                triggered=self._displayHelp))

        self.layout.addWidget(QtWidgets.QLabel("Z"), 1, 0, 2, 1)
        self.layout.addWidget(QtWidgets.QLabel("Y"), 3, 0, 2, 1)
        self.layout.addWidget(QtWidgets.QLabel("X"), 5, 0, 2, 1)

        self.gridShapeZ = QtWidgets.QSpinBox()
        self.gridShapeZ.setRange(0, 1000000)
        self.gridShapeZ.setValue(1)
        self.gridShapeY = QtWidgets.QSpinBox()
        self.gridShapeY.setRange(0, 1000000)
        self.gridShapeY.setValue(500)
        self.gridShapeX = QtWidgets.QSpinBox()
        self.gridShapeX.setRange(0, 1000000)
        self.gridShapeX.setValue(500)
        self.layout.addWidget(QtWidgets.QLabel("grid_shape"), 0, 1)
        self.layout.addWidget(self.gridShapeZ, 1, 1, 2, 1)
        self.layout.addWidget(self.gridShapeY, 3, 1, 2, 1)
        self.layout.addWidget(self.gridShapeX, 5, 1, 2, 1)

        self.gridLimitsZmin = QtWidgets.QDoubleSpinBox()
        self.gridLimitsZmin.setRange(-41000000, 41000000)
        self.gridLimitsZmin.setSingleStep(1000)
        self.gridLimitsZmin.setValue(2000)
        self.gridLimitsZmax = QtWidgets.QDoubleSpinBox()
        self.gridLimitsZmax.setRange(-41000000, 41000000)
        self.gridLimitsZmax.setSingleStep(1000)
        self.gridLimitsZmax.setValue(3000)
        self.gridLimitsYmin = QtWidgets.QDoubleSpinBox()
        self.gridLimitsYmin.setRange(-41000000, 41000000)
        self.gridLimitsYmin.setSingleStep(1000)
        self.gridLimitsYmin.setValue(-250000)
        self.gridLimitsYmax = QtWidgets.QDoubleSpinBox()
        self.gridLimitsYmax.setRange(-41000000, 41000000)
        self.gridLimitsYmax.setSingleStep(1000)
        self.gridLimitsYmax.setValue(250000)
        self.gridLimitsXmin = QtWidgets.QDoubleSpinBox()
        self.gridLimitsXmin.setRange(-41000000, 41000000)
        self.gridLimitsXmin.setSingleStep(1000)
        self.gridLimitsXmin.setValue(-250000)
        self.gridLimitsXmax = QtWidgets.QDoubleSpinBox()
        self.gridLimitsXmax.setRange(-41000000, 41000000)
        self.gridLimitsXmax.setSingleStep(1000)
        self.gridLimitsXmax.setValue(250000)
        self.layout.addWidget(QtWidgets.QLabel("grid_limits (m)"), 0, 2)
        self.layout.addWidget(self.gridLimitsZmin, 1, 2)
        self.layout.addWidget(self.gridLimitsZmax, 2, 2)
        self.layout.addWidget(self.gridLimitsYmin, 3, 2)
        self.layout.addWidget(self.gridLimitsYmax, 4, 2)
        self.layout.addWidget(self.gridLimitsXmin, 5, 2)
        self.layout.addWidget(self.gridLimitsXmax, 6, 2)

        self.layout.setRowStretch(8, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)

    def grid_from_radars(self):
        '''Mount Options and execute :py:func:`~pyart.correct.grid_from_radars`.
        The resulting grid is update in Vgrid.
        '''
        # test radar
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None, can not perform correction")
            return
        # mount options
        self.parameters['radars'] = (self.Vradar.value,)
        self.parameters['fields'] = []
        for field in self.field_actions.keys():
            if self.field_actions[field].isChecked():
                self.parameters['fields'].append(field)

        self.parameters['grid_shape'] = (self.gridShapeZ.value(),
                                         self.gridShapeY.value(),
                                         self.gridShapeX.value())
        self.parameters['grid_limits'] = (
            (self.gridLimitsZmin.value(), self.gridLimitsZmax.value()),
            (self.gridLimitsYmin.value(), self.gridLimitsYmax.value()),
            (self.gridLimitsXmin.value(), self.gridLimitsXmax.value()))

        self.parameters['grid_origin'] = (self.parameters['grid_origin_lat'],
                                          self.parameters['grid_origin_lon'])

        # execute
        print("mapping ..", file=log.debug)
        t0 = time.time()
        try:
            grid = pyart.map.grid_from_radars(**self.parameters)
        except:
            import traceback
            error = traceback.format_exc()
            common.ShowLongText("Py-ART fails with following error\n\n" +
                                error)
        t1 = time.time()
        print("Mapping took %fs" % (t1-t0), file=log.debug)

        # update
        self.Vgrid.change(grid)

    def setParameters(self):
        '''Open set parameters dialog.'''
        parm = common.get_options(self.general_parameters_type, self.parameters)
        for key in parm.keys():
            self.parameters[key] = parm[key]

    def setGriddingParameters(self):
        '''Open set parameters dialog.'''
        parm = common.get_options(self.gridding_parameters_type, self.parameters)
        for key in parm.keys():
            self.parameters[key] = parm[key]

    def setRoiParameters(self):
        '''Open set parameters dialog.'''
        parm = common.get_options(self.roi_parameters_type, self.parameters)
        for key in parm.keys():
            self.parameters[key] = parm[key]

    def _displayHelp(self):
        '''Display Py-Art's docstring for help.'''
        common.ShowLongText(pyart.map.grid_from_radars.__doc__)

    def NewRadar(self, variable, strong):
        '''Display Py-Art's docstring for help.'''
        if self.Vradar.value is None:
            return

        fields = self.Vradar.value.fields.keys()
        self.field_radio_group = QtWidgets.QActionGroup(self, exclusive=False)
        self.field_actions = {}
        self.fieldMenu.clear()
        for field in fields:
            action = self.field_radio_group.addAction(field)
            action.setCheckable(True)
            action.setChecked(True)
            self.fieldMenu.addAction(action)
            self.field_actions[field] = action

        lat = float(self.Vradar.value.latitude['data'])
        lon = float(self.Vradar.value.longitude['data'])
        alt = float(self.Vradar.value.altitude['data'])
        self.parameters["grid_origin_lat"] = lat
        self.parameters["grid_origin_lon"] = lon
        self.parameters["grid_origin_alt"] = alt



_plugins = [Mapper]
