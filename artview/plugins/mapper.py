"""
mapper.py
"""

# Load the needed packages
from functools import partial

import pyart
import time

from ..core import Component, Variable, common, QtGui, QtCore, VariableChoose


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
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QVBoxLayout(self.central_widget)

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

        self.generalLayout = QtGui.QGridLayout()
        self.especificLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.generalLayout)
        self.layout.addLayout(self.especificLayout)

        self.button = QtGui.QPushButton("Map")
        self.button.clicked.connect(self.grid_from_radars)
        self.button.setToolTip('Execute pyart.map.grid_from_radars')
        self.layout.addWidget(self.button)

        self.addGeneralOptions()

        self.NewRadar(None, True)

        self.show()

    def addGeneralOptions(self):
        '''Mount Options Layout for :py:func:`~pyart.map.grid_from_radars`'''
        self.generalLayout.addWidget(QtGui.QLabel("Z"), 0, 1, 1, 2)
        self.generalLayout.addWidget(QtGui.QLabel("Y"), 0, 3, 1, 2)
        self.generalLayout.addWidget(QtGui.QLabel("X"), 0, 5, 1, 2)

        self.gridShapeZ = QtGui.QSpinBox()
        self.gridShapeZ.setRange(0, 1000000)
        self.gridShapeZ.setValue(1)
        self.gridShapeY = QtGui.QSpinBox()
        self.gridShapeY.setRange(0, 1000000)
        self.gridShapeY.setValue(500)
        self.gridShapeX = QtGui.QSpinBox()
        self.gridShapeX.setRange(0, 1000000)
        self.gridShapeX.setValue(500)
        self.generalLayout.addWidget(QtGui.QLabel("grid_shape"), 1, 0)
        self.generalLayout.addWidget(self.gridShapeZ, 1, 1, 1, 2)
        self.generalLayout.addWidget(self.gridShapeY, 1, 3, 1, 2)
        self.generalLayout.addWidget(self.gridShapeX, 1, 5, 1, 2)

        self.gridLimitsZmin = QtGui.QDoubleSpinBox()
        self.gridLimitsZmin.setRange(-41000000, 41000000)
        self.gridLimitsZmin.setSingleStep(1000)
        self.gridLimitsZmin.setValue(2000)
        self.gridLimitsZmax = QtGui.QDoubleSpinBox()
        self.gridLimitsZmax.setRange(-41000000, 41000000)
        self.gridLimitsZmax.setSingleStep(1000)
        self.gridLimitsZmax.setValue(3000)
        self.gridLimitsYmin = QtGui.QDoubleSpinBox()
        self.gridLimitsYmin.setRange(-41000000, 41000000)
        self.gridLimitsYmin.setSingleStep(1000)
        self.gridLimitsYmin.setValue(-250000)
        self.gridLimitsYmax = QtGui.QDoubleSpinBox()
        self.gridLimitsYmax.setRange(-41000000, 41000000)
        self.gridLimitsYmax.setSingleStep(1000)
        self.gridLimitsYmax.setValue(250000)
        self.gridLimitsXmin = QtGui.QDoubleSpinBox()
        self.gridLimitsXmin.setRange(-41000000, 41000000)
        self.gridLimitsXmin.setSingleStep(1000)
        self.gridLimitsXmin.setValue(-250000)
        self.gridLimitsXmax = QtGui.QDoubleSpinBox()
        self.gridLimitsXmax.setRange(-41000000, 41000000)
        self.gridLimitsXmax.setSingleStep(1000)
        self.gridLimitsXmax.setValue(250000)
        self.generalLayout.addWidget(QtGui.QLabel("grid_limits"), 2, 0)
        self.generalLayout.addWidget(self.gridLimitsZmin, 2, 1)
        self.generalLayout.addWidget(self.gridLimitsZmax, 2, 2)
        self.generalLayout.addWidget(self.gridLimitsYmin, 2, 3)
        self.generalLayout.addWidget(self.gridLimitsYmax, 2, 4)
        self.generalLayout.addWidget(self.gridLimitsXmin, 2, 5)
        self.generalLayout.addWidget(self.gridLimitsXmax, 2, 6)

        self.griddingAlgo = QtGui.QComboBox()
        self.griddingAlgo.addItem('map_to_grid')
        self.griddingAlgo.addItem('map_gates_to_grid')
        self.generalLayout.addWidget(QtGui.QLabel("gridding_algo"), 3, 0)
        self.generalLayout.addWidget(self.griddingAlgo, 3, 1, 1, 6)

        self.griddingAlgo.currentIndexChanged[str].connect(
            self.addEspecificOptions)
        self.griddingAlgo.setCurrentIndex(1)

    def addEspecificOptions(self, item):
        '''Mount Options Layout depending on gridding algorithm.'''
        self._clearLayout(self.especificLayout)
        if item == 'map_gates_to_grid':
            self.mapGatesToGridOptions()
        elif item == 'map_to_grid':
            self.mapToGridOptions()
        self.NewRadar(None, True)

    def mapGatesToGridOptions(self):
        '''Mount Options Layout for :py:func:`~pyart.map.map_gates_to_grid`'''
        self._fieldsOptions()
        self._interpolationOptions()

    def mapToGridOptions(self):
        '''Mount Options Layout for :py:func:`~pyart.map.map_to_grid`'''
        self._fieldsOptions()
        self._interpolationOptions()

        self.copyFieldData = QtGui.QCheckBox("copy_field_data")
        self.copyFieldData.setChecked(True)
        self.especificLayout.addWidget(self.copyFieldData, 11, 1, 1, 2)

        self.algorithm = QtGui.QComboBox()
        self.algorithm.addItem('kd_tree')
        self.algorithm.addItem('ball_tree')
        self.algorithm.setCurrentIndex(0)
        self.especificLayout.addWidget(QtGui.QLabel("algorithm"), 12, 0)
        self.especificLayout.addWidget(self.algorithm, 12, 1, 1, 2)

        self.leafsize = QtGui.QSpinBox()
        self.leafsize.setRange(0, 1000000)
        self.leafsize.setValue(10)
        self.especificLayout.addWidget(QtGui.QLabel("leafsize"), 13, 0)
        self.especificLayout.addWidget(self.leafsize, 13, 1, 1, 2)

    def _fieldsOptions(self):
        '''Mount Options Layout related to field.'''
        self.gridOriginLat = QtGui.QDoubleSpinBox()
        self.gridOriginLat.setRange(-90, 90)
        self.gridOriginLat.setDecimals(8)
        self.gridOriginLon = QtGui.QDoubleSpinBox()
        self.gridOriginLon.setRange(-180, 180)
        self.gridOriginLon.setDecimals(8)
        self.especificLayout.addWidget(QtGui.QLabel("grid_origin"), 0, 0)
        self.especificLayout.addWidget(self.gridOriginLat, 0, 1)
        self.especificLayout.addWidget(self.gridOriginLon, 0, 2)

        self.gridOriginAlt = QtGui.QDoubleSpinBox()
        self.gridOriginAlt.setRange(0, 20000)
        self.especificLayout.addWidget(QtGui.QLabel("grid_origin_alt"), 1, 0)
        self.especificLayout.addWidget(self.gridOriginAlt, 1, 1, 1, 2)

        self.fieldsbutton = QtGui.QToolButton(self)
        self.fieldsbutton.setText('Select Fields')
        self.fieldsmenu = QtGui.QMenu(self)
        self.fieldsbutton.setMenu(self.fieldsmenu)
        self.fieldsbutton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.especificLayout.addWidget(self.fieldsbutton, 2, 1, 1, 2)

        self.reflFilterFlag = QtGui.QCheckBox("refl_filter_flag")
        self.reflFilterFlag.setChecked(True)
        self.especificLayout.addWidget(self.reflFilterFlag, 3, 1, 1, 2)

        self.reflField = QtGui.QLineEdit("reflectivity")
        self.especificLayout.addWidget(QtGui.QLabel("refl_field"), 4, 0)
        self.especificLayout.addWidget(self.reflField, 4, 1, 1, 2)

        self.maxRefl = QtGui.QDoubleSpinBox()
        self.maxRefl.setRange(-1000, 1000)
        self.maxRefl.setValue(100)
        self.especificLayout.addWidget(QtGui.QLabel("max_refl"), 5, 0)
        self.especificLayout.addWidget(self.maxRefl, 5, 1, 1, 2)

    def _interpolationOptions(self):
        '''Mount Options Layout related to interpolation.'''
        self.mapRoi = QtGui.QCheckBox("map_roi")
        self.mapRoi.setChecked(True)
        self.especificLayout.addWidget(self.mapRoi, 6, 1, 1, 2)

        self.weightingFunction = QtGui.QComboBox()
        self.weightingFunction.addItem('Barnes')
        self.weightingFunction.addItem('Cressman')
        self.weightingFunction.setCurrentIndex(0)
        self.especificLayout.addWidget(
            QtGui.QLabel("weighting_function"), 7, 0)
        self.especificLayout.addWidget(self.weightingFunction, 7, 1, 1, 2)

        self.toa = QtGui.QDoubleSpinBox()
        self.toa.setRange(0, 30000)
        self.toa.setValue(17000)
        self.toa.setSingleStep(1000)
        self.especificLayout.addWidget(QtGui.QLabel("toa"), 8, 0)
        self.especificLayout.addWidget(self.toa, 8, 1, 1, 2)

        self.roiFunc = QtGui.QComboBox()
        self.roiFunc.addItem('constant')
        self.roiFunc.addItem('dist')
        self.roiFunc.addItem('dist_beam')
        self.especificLayout.addWidget(QtGui.QLabel("roi_func"), 9, 0)
        self.especificLayout.addWidget(self.roiFunc, 9, 1, 1, 2)

        self.roiFuncLayout = QtGui.QGridLayout()
        self.especificLayout.addLayout(self.roiFuncLayout, 10, 0, 1, 3)

        self.roiFunc.currentIndexChanged[str].connect(self._roiFuncOptions)
        self.roiFunc.setCurrentIndex(2)

    def _roiFuncOptions(self, item):
        '''Mount Options Layout related to radius of influence.'''
        self._clearLayout(self.roiFuncLayout)
        if item == 'constant':
            self.constantRoiOptions()
        elif item == 'dist':
            self.distRoiOptions()
        elif item == 'dist_beam':
            self.distBeamRoiOptions()

    def constantRoiOptions(self):
        '''Mount Options Layout for constant radius of influence.'''
        self.constantRoi = QtGui.QDoubleSpinBox()
        self.constantRoi.setRange(0, 30000)
        self.constantRoi.setValue(500)
        self.constantRoi.setSingleStep(100)
        self.roiFuncLayout.addWidget(QtGui.QLabel("constant_roi"), 0, 0)
        self.roiFuncLayout.addWidget(self.constantRoi, 0, 1, 1, 2)

    def distRoiOptions(self):
        '''Mount Options Layout for dist radius of influence.'''
        self.zFactor = QtGui.QDoubleSpinBox()
        self.zFactor.setRange(0, 30000)
        self.zFactor.setValue(0.05)
        self.zFactor.setSingleStep(0.01)
        self.zFactor.setDecimals(3)
        self.roiFuncLayout.addWidget(QtGui.QLabel("z_factor"), 0, 0)
        self.roiFuncLayout.addWidget(self.zFactor, 0, 1, 1, 2)

        self.xyFactor = QtGui.QDoubleSpinBox()
        self.xyFactor.setRange(0, 30000)
        self.xyFactor.setValue(0.02)
        self.xyFactor.setSingleStep(0.01)
        self.xyFactor.setDecimals(3)
        self.roiFuncLayout.addWidget(QtGui.QLabel("xy_factor"), 1, 0)
        self.roiFuncLayout.addWidget(self.xyFactor, 1, 1, 1, 2)

        self.minRadius = QtGui.QDoubleSpinBox()
        self.minRadius.setRange(0, 30000)
        self.minRadius.setValue(500)
        self.minRadius.setSingleStep(100)
        self.roiFuncLayout.addWidget(QtGui.QLabel("min_radius"), 2, 0)
        self.roiFuncLayout.addWidget(self.minRadius, 2, 1, 1, 2)

    def distBeamRoiOptions(self):
        '''Mount Options Layout for dist beam radius of influence.'''
        self.hFactor = QtGui.QDoubleSpinBox()
        self.hFactor.setRange(0, 30000)
        self.hFactor.setValue(1.0)
        self.hFactor.setSingleStep(0.1)
        self.roiFuncLayout.addWidget(QtGui.QLabel("h_factor"), 0, 0)
        self.roiFuncLayout.addWidget(self.hFactor, 0, 1, 1, 2)

        self.nb = QtGui.QDoubleSpinBox()
        self.nb.setRange(0, 30000)
        self.nb.setValue(1.5)
        self.nb.setSingleStep(0.1)
        self.roiFuncLayout.addWidget(QtGui.QLabel("nb"), 1, 0)
        self.roiFuncLayout.addWidget(self.nb, 1, 1, 1, 2)

        self.bsp = QtGui.QDoubleSpinBox()
        self.bsp.setRange(0, 30000)
        self.bsp.setValue(1.0)
        self.bsp.setSingleStep(0.1)
        self.roiFuncLayout.addWidget(QtGui.QLabel("bsp"), 2, 0)
        self.roiFuncLayout.addWidget(self.bsp, 2, 1, 1, 2)

        self.minRadius = QtGui.QDoubleSpinBox()
        self.minRadius.setRange(0, 30000)
        self.minRadius.setValue(500)
        self.minRadius.setSingleStep(100)
        self.roiFuncLayout.addWidget(QtGui.QLabel("min_radius"), 3, 0)
        self.roiFuncLayout.addWidget(self.minRadius, 3, 1, 1, 2)

    def NewRadar(self, variable, strong):
        '''Display Py-Art's docstring for help.'''
        if self.Vradar.value is None:
            return
        self.fieldsmenu.clear()
        for field in self.Vradar.value.fields.keys():
            action = self.fieldsmenu.addAction(field)
            action.setCheckable(True)
            action.setChecked(True)
        lat = float(self.Vradar.value.latitude['data'])
        lon = float(self.Vradar.value.longitude['data'])
        alt = float(self.Vradar.value.altitude['data'])
        self.gridOriginLat.setValue(lat)
        self.gridOriginLon.setValue(lon)
        self.gridOriginAlt.setValue(alt)

    def grid_from_radars(self):
        '''Mount Options and execute :py:func:`~pyart.correct.grid_from_radars`.
        The resulting grid is update in Vgrid.
        '''
        # test radar
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None, can not perform correction")
            return
        # mount options
        args = {
            'radars': (self.Vradar.value,),
            'grid_shape': (self.gridShapeZ.value(),
                           self.gridShapeY.value(),
                           self.gridShapeX.value()),
            'grid_limits': (
                (self.gridLimitsZmin.value(), self.gridLimitsZmax.value()),
                (self.gridLimitsYmin.value(), self.gridLimitsYmax.value()),
                (self.gridLimitsXmin.value(), self.gridLimitsXmax.value())),
            'grid_origin': (self.gridOriginLat.value(),
                            self.gridOriginLon.value()),
            'gridding_algo': str(self.griddingAlgo.currentText()),
            'grid_origin_alt': self.gridOriginAlt.value(),
            'fields': [str(a.text()) for a in
                       self.fieldsmenu.actions() if a.isChecked()],
            'refl_filter_flag': self.reflFilterFlag.isChecked(),
            'refl_field': str(self.reflField.text()),
            'max_refl': self.maxRefl.value(),
            'map_roi': self.mapRoi.isChecked(),
            'weighting_function': str(self.weightingFunction.currentText()),
            'toa': self.toa.value(),
            'roi_func': str(self.roiFunc.currentText()),
        }

        if args['roi_func'] == 'constant':
            args['constant_roi'] = self.constantRoi.value()
        elif args['roi_func'] == 'dist':
            args['z_factor'] = self.zFactor.value()
            args['xy_factor'] = self.xyFactor.value()
            args['min_radius'] = self.minRadius.value()
        elif args['roi_func'] == 'dist_beam':
            args['h_factor'] = self.hFactor.value()
            args['nb'] = self.nb.value()
            args['bsp'] = self.bsp.value()
            args['min_radius'] = self.minRadius.value()

        if args['gridding_algo'] == 'map_to_grid':
            args['copy_field_data'] = self.copyFieldData.isChecked()
            args['algorithm'] = str(self.algorithm.currentText())
            args['leafsize'] = self.leafsize.value()

        print(args)

        # execute
        print("mapping ..")
        t0 = time.time()
        try:
            grid = pyart.map.grid_from_radars(**args)
        except:
            import traceback
            error = traceback.format_exc()
            common.ShowLongText("Py-ART fails with following error\n\n" +
                                error)
        t1 = time.time()
        print(("Mapping took %fs" % (t1-t0)))

        # update
        self.Vgrid.change(grid)

    def _clearLayout(self, layout):
        '''recursively remove items from layout.'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clearLayout(item.layout())

_plugins = [Mapper]
