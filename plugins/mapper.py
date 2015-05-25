"""

"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial

import core
import common

class Mapper(core.Component):
    @classmethod
    def guiStart(self):
        val, entry = common.string_dialog("Mapper", "Mapper", "Name:")
        return self(name=val)

    def __init__(self, Vradar=None, Vgrid=None, name="Mapper", parent=None):
        '''Initialize the class to create the interface'''
        super(Mapper, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QVBoxLayout(self.central_widget)

        if Vradar is None:
            self.Vradar = core.Variable(None)
        else:
            self.Vradar = Vradar

        if Vgrid is None:
            self.Vgrid = core.Variable(None)
        else:
            self.Vgrid = Vgrid
        self.sharedVariables = {"Vradar": None,
                                "Vfield": None}
        self.connectAllVariables()
        
        self.generalLayout = QtGui.QGridLayout()
        self.especificLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.generalLayout)
        self.layout.addLayout(self.especificLayout)

        self.button = QtGui.QPushButton("Map")
        self.button.clicked.connect(self.grid_from_radars)
        self.layout.addWidget(self.button)

        self.addGeneralOptions()
        self.addEspecificOptions()

        self.show()

    def addGeneralOptions(self):
        self.generalLayout.addWidget(QtGui.QLabel("Z"), 0, 1, 1, 2)
        self.generalLayout.addWidget(QtGui.QLabel("Y"), 0, 3, 1, 2)
        self.generalLayout.addWidget(QtGui.QLabel("X"), 0, 5, 1, 2)

        self.gridShapeZ = QtGui.QSpinBox()
        self.gridShapeZ.setRange(0,1000000)
        self.gridShapeY = QtGui.QSpinBox()
        self.gridShapeY.setRange(0,1000000)
        self.gridShapeX = QtGui.QSpinBox()
        self.gridShapeX.setRange(0,1000000)
        self.generalLayout.addWidget(QtGui.QLabel("grid_shape"), 1, 0)
        self.generalLayout.addWidget(self.gridShapeZ, 1, 1, 1, 2)
        self.generalLayout.addWidget(self.gridShapeY, 1, 3, 1, 2)
        self.generalLayout.addWidget(self.gridShapeX, 1, 5, 1, 2)

        self.gridLimitsZmin = QtGui.QDoubleSpinBox()
        self.gridLimitsZmin.setRange(-41000000,41000000)
        self.gridLimitsZmin.setSingleStep(1000)
        self.gridLimitsZmax = QtGui.QDoubleSpinBox()
        self.gridLimitsZmax.setRange(-41000000,41000000)
        self.gridLimitsZmax.setSingleStep(1000)
        self.gridLimitsYmin = QtGui.QDoubleSpinBox()
        self.gridLimitsYmin.setRange(-41000000,41000000)
        self.gridLimitsYmin.setSingleStep(1000)
        self.gridLimitsYmax = QtGui.QDoubleSpinBox()
        self.gridLimitsYmax.setRange(-41000000,41000000)
        self.gridLimitsYmax.setSingleStep(1000)
        self.gridLimitsXmin = QtGui.QDoubleSpinBox()
        self.gridLimitsXmin.setRange(-41000000,41000000)
        self.gridLimitsXmin.setSingleStep(1000)
        self.gridLimitsXmax = QtGui.QDoubleSpinBox()
        self.gridLimitsXmax.setRange(-41000000,41000000)
        self.gridLimitsXmax.setSingleStep(1000)
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
        self.griddingAlgo.setCurrentIndex(0)
        self.generalLayout.addWidget(QtGui.QLabel("gridding_algo"), 3, 0)
        self.generalLayout.addWidget(self.griddingAlgo, 3, 1, 1, 6)

    def addEspecificOptions(self):
        argo = self.griddingAlgo.currentText()

        self.gridOriginLat = QtGui.QDoubleSpinBox()
        self.gridOriginLat.setRange(-90,90)
        self.gridOriginLon = QtGui.QDoubleSpinBox()
        self.gridOriginLon.setRange(-180,180)
        self.especificLayout.addWidget(QtGui.QLabel("grid_origin"), 0, 0)
        self.especificLayout.addWidget(self.gridOriginLat, 0, 1)
        self.especificLayout.addWidget(self.gridOriginLon, 0, 2)

        self.reflFilterFlag = QtGui.QCheckBox("refl_filter_flag")
        self.reflFilterFlag.setChecked(True)
        self.especificLayout.addWidget(self.reflFilterFlag, 1, 1, 1 ,2)

        self.reflField = QtGui.QLineEdit("reflectivity")
        self.especificLayout.addWidget(QtGui.QLabel("refl_field"), 2, 0)
        self.especificLayout.addWidget(self.reflField, 2, 1, 1 ,2)

        self.maxRefl = QtGui.QDoubleSpinBox()
        self.maxRefl.setRange(-1000,1000)
        self.maxRefl.setValue(100)
        self.especificLayout.addWidget(QtGui.QLabel("max_refl"), 3, 0)
        self.especificLayout.addWidget(self.maxRefl, 3, 1, 1 ,2)

        self.mapRoi = QtGui.QCheckBox("map_roi")
        self.mapRoi.setChecked(True)
        self.especificLayout.addWidget(self.mapRoi, 4, 1, 1 ,2)

        self.weightingFunction = QtGui.QComboBox()
        self.weightingFunction.addItem('Barnes')
        self.weightingFunction.addItem('Cressman')
        self.weightingFunction.setCurrentIndex(0)
        self.especificLayout.addWidget(QtGui.QLabel("weighting_function"), 5, 0)
        self.especificLayout.addWidget(self.weightingFunction, 5, 1, 1 ,2)

        self.toa = QtGui.QDoubleSpinBox()
        self.toa.setRange(0,30000)
        self.toa.setValue(17000)
        self.toa.setSingleStep(1000)
        self.especificLayout.addWidget(QtGui.QLabel("toa"), 6, 0)
        self.especificLayout.addWidget(self.toa, 6, 1, 1 ,2)

        self.roiFunc = QtGui.QComboBox()
        self.roiFunc.addItem('constant')
        self.roiFunc.addItem('dist')
        self.roiFunc.addItem('dist_beam')
        self.roiFunc.setCurrentIndex(2)
        self.especificLayout.addWidget(QtGui.QLabel("roi_func"), 7, 0)
        self.especificLayout.addWidget(self.roiFunc, 7, 1, 1 ,2)

        self.constantRoi = QtGui.QDoubleSpinBox()
        self.constantRoi.setRange(0,30000)
        self.constantRoi.setValue(500)
        self.constantRoi.setSingleStep(100)
        self.especificLayout.addWidget(QtGui.QLabel("constant_roi"), 8, 0)
        self.especificLayout.addWidget(self.constantRoi, 8, 1, 1 ,2)

        self.zFactor = QtGui.QDoubleSpinBox()
        self.zFactor.setRange(0,30000)
        self.zFactor.setValue(0.05)
        self.zFactor.setSingleStep(0.01)
        self.especificLayout.addWidget(QtGui.QLabel("z_factor"), 9, 0)
        self.especificLayout.addWidget(self.zFactor, 9, 1, 1 ,2)

        self.xyFactor = QtGui.QDoubleSpinBox()
        self.xyFactor.setRange(0,30000)
        self.xyFactor.setValue(0.02)
        self.xyFactor.setSingleStep(0.01)
        self.especificLayout.addWidget(QtGui.QLabel("xy_factor"), 10, 0)
        self.especificLayout.addWidget(self.xyFactor, 10, 1, 1 ,2)

        self.minRadius = QtGui.QDoubleSpinBox()
        self.minRadius.setRange(0,30000)
        self.minRadius.setValue(500)
        self.minRadius.setSingleStep(100)
        self.especificLayout.addWidget(QtGui.QLabel("min_radius"), 11, 0)
        self.especificLayout.addWidget(self.minRadius, 11, 1, 1 ,2)

        self.hFactor = QtGui.QDoubleSpinBox()
        self.hFactor.setRange(0,30000)
        self.hFactor.setValue(1.0)
        self.hFactor.setSingleStep(0.1)
        self.especificLayout.addWidget(QtGui.QLabel("h_factor"), 12, 0)
        self.especificLayout.addWidget(self.hFactor, 12, 1, 1 ,2)

        self.nb = QtGui.QDoubleSpinBox()
        self.nb.setRange(0,30000)
        self.nb.setValue(1.5)
        self.nb.setSingleStep(0.1)
        self.especificLayout.addWidget(QtGui.QLabel("nb"), 13, 0)
        self.especificLayout.addWidget(self.nb, 13, 1, 1 ,2)

        self.bsp = QtGui.QDoubleSpinBox()
        self.bsp.setRange(0,30000)
        self.bsp.setValue(1.0)
        self.bsp.setSingleStep(0.1)
        self.especificLayout.addWidget(QtGui.QLabel("bsp"), 14, 0)
        self.especificLayout.addWidget(self.bsp, 14, 1, 1 ,2)

    def grid_from_radars(self):
        print "map"

    def close(self):
        super(Exemple2, self).close()

_plugins=[Mapper]
