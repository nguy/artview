 
"""
despeckle.py
"""

# Load the needed packages

import pyart
import numpy as np
#from netCDF4 import Dataset
#from matplotlib.colors import LightSource
#from mpl_toolkits.basemap import shiftgrid, cm

#import sys
import os


from ..core import Component, Variable, common, QtGui, QtCore, componentsList


class Despeckle(Component):
    '''
    Despeckle Radar
    '''

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("Despeckle").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None, Vfield=None, Vgatefilter=None,
                 name="Despeckle", parent=None):
        '''Initialize the class to create the interface.
        Parameters
        ----------
        [Optional]
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable. If None start new one with None.
        Vfield : :py:class:`~artview.core.core.Variable` instance
            Field signal variable. If None start new one with empty string.
        Vgatefilter : :py:class:`~artview.core.core.Variable` instance
            Gatefilter signal variable.
            A value of None will instantiate a empty variable.
        name : string
            Component name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(Despeckle, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

#        self.layout.addWidget(QtGui.QLabel("Etopo file:"), 0, 0)

#        self.lineEdit = QtGui.QLineEdit(
#            "http://ferret.pmel.noaa.gov/thredds/dodsC/data/PMEL/etopo5.nc",
#            self)
#        self.layout.addWidget(self.lineEdit, 0, 1)

        self.despeckleButton = QtGui.QPushButton("Despeckle")
        self.despeckleButton.setToolTip("Create gatefilter of speckles")
        self.despeckleButton.clicked.connect(self.despeckle)
        self.layout.addWidget(self.despeckleButton, 0, 0)

        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir))
        config_icon = QtGui.QIcon(os.sep.join([parentdir, 'icons',
                                              "categories-applications-system-icon.png"]))
        self.configButton = QtGui.QPushButton(config_icon,"")
        self.layout.addWidget(self.configButton, 0, 1)
        self.configMenu = QtGui.QMenu(self)
        self.configButton.setMenu(self.configMenu)
        self.fieldMenu = self.configMenu.addMenu("field")

        self.configMenu.addAction(QtGui.QAction("Set Parameters", self,
                                                triggered=self.setParameters))
        self.parameters = {'threshold_min': -100.,
                           'threshold_max': 'Inf',
                           'size': 10,
                           'delta': 5}

        action = QtGui.QAction("Add Object Field", self,
                               triggered=self.addObjectsField)
        action.setToolTip("Identify Object and add as field to radar")
        self.configMenu.addAction(action)

        self.layout.setColumnStretch(0, 1)


#        self.applyButton = QtGui.QPushButton("Apply")
#        self.applyButton.clicked.connect(self.apply)
#        self.layout.addWidget(self.applyButton, 0, 3)

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar
        if Vfield is None:
            self.Vfield = Variable('')
        else:
            self.Vfield = Vfield
        if Vgatefilter is None:
            self.Vgatefilter = Variable(None)
        else:
            self.Vgatefilter = Vgatefilter

        self.sharedVariables = {"Vradar": self.NewRadar,
                                "Vfield": self.NewField,
                                "Vgatefilter": None}

        self.NewRadar(None, True)

        self.show()

    def despeckle(self):
        '''Apply Despeckle.'''
        radar = self.Vradar.value
        field = self.Vfield.value
        if radar is None:
            common.ShowWarning("Radar is None, can not perform despeckle")
            return
        if field not in radar.fields:
            common.ShowWarning(
                "Field %s not in Radar, can not perform despeckle" % field)
            return

        gatefilter = self.Vgatefilter.value
        if self.parameters['threshold_max'] == 'Inf':
            threshold = self.parameters['threshold_min']
        else:
            threshold = (self.parameters['threshold_min'],
                         self.parameters['threshold_max'])
        gatefilter = pyart.correct.despeckle_field(
            radar, field, label_dict=None, threshold=threshold,
            size=self.parameters['size'],
            gatefilter=gatefilter, delta=self.parameters['delta'])
        self.Vgatefilter.change(gatefilter)

    def addObjectsField(self):
        '''Add Objects Field to Radar.'''
        radar = self.Vradar.value
        field = self.Vfield.value
        if radar is None:
            common.ShowWarning("Radar is None, can not perform despeckle")
            return
        if field not in radar.fields:
            common.ShowWarning(
                "Field %s not in Radar, can not perform despeckle" % field)
            return

        gatefilter = self.Vgatefilter.value

        # ask for name
        objects = str(common.string_dialog(
            "objects", "Enter Field Name",
            "This will add a new field to the radar, where bins are numbered\n" +
            "according to the connected component it makes part of." +
            "\n\nEnter Field Name:")[0])
        strong_update = False
        if objects == '':
            return
        if objects in radar.fields:
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                objects)
            if resp != QtGui.QMessageBox.Ok:
                return
            else:
                strong_update = True

        if self.parameters['threshold_max'] == 'Inf':
            threshold = self.parameters['threshold_min']
        else:
            threshold = (self.parameters['threshold_min'],
                         self.parameters['threshold_max'])
        label_dict = pyart.correct.find_objects(
            radar, field, threshold=threshold,
            gatefilter=gatefilter, delta=self.parameters['delta'])
        radar.add_field(objects, label_dict, True)
        self.Vradar.update(strong_update)

    def change_field(self):
        '''Slot from menu to change field.'''
        action = self.field_radio_group.checkedAction()
        if action != 0:
            field = str(action.text())
            self.Vfield.change(field)

    def NewRadar(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vradar <artview.core.core.Variable>`.
        This will:

        * Repopulate field menu
        '''
        if self.Vradar.value is None:
            fields = []
        else:
            fields = self.Vradar.value.fields.keys()
        self.field_radio_group = QtGui.QActionGroup(self, exclusive=True)
        self.field_actions = {}
        self.fieldMenu.clear()
        for field in fields:
            action = self.field_radio_group.addAction(field)
            action.triggered.connect(self.change_field)
            action.setCheckable(True)
            self.fieldMenu.addAction(action)
            self.field_actions[field] = action
        self.NewField(None, True)

    def NewField(self, variable, strong):
        '''
        Slot for 'ValueChanged' signal of
        :py:class:`Vfield <artview.core.core.Variable>`.
        This will:

        * changed checked in field menu
        '''
        field = self.Vfield.value
        if field in self.field_actions:
            self.field_actions[field].setChecked(True)

    def setParameters(self):
        '''Open set parameters dialog.'''
        dialog = QtGui.QDialog()
        dialog.setObjectName("Despeckle Parameters Dialog")
        dialog.setWindowModality(QtCore.Qt.WindowModal)
        dialog.setWindowTitle("Despeckle Parameters Dialog")

        # Setup window layout
        gridLayout_2 = QtGui.QGridLayout(dialog)
        gridLayout = QtGui.QGridLayout()

        # Add to the layout
        gridLayout.addWidget(QtGui.QLabel("threshold min"), 0, 0)
        ent_threshold_min = QtGui.QLineEdit(dialog)
        ent_threshold_min.setToolTip("Minimum data value")
        ent_threshold_min.setText(str(self.parameters['threshold_min']))
        gridLayout.addWidget(ent_threshold_min, 0, 1,)

        gridLayout.addWidget(QtGui.QLabel("threshold max"), 1, 0)
        ent_threshold_max = QtGui.QLineEdit(dialog)
        ent_threshold_max.setToolTip("Maximum data value")
        ent_threshold_max.setText(str(self.parameters['threshold_max']))
        gridLayout.addWidget(ent_threshold_max, 1, 1)

        gridLayout.addWidget(QtGui.QLabel("Speckle size"), 2, 0)
        ent_size = QtGui.QLineEdit(dialog)
        ent_size.setToolTip("Number of contiguous gates in an object,"
                            "below which it is a speckle.")
        ent_size.setText(str(self.parameters['size']))
        gridLayout.addWidget(ent_size, 2, 1)

        gridLayout.addWidget(QtGui.QLabel("delta"), 3, 0)
        ent_delta = QtGui.QLineEdit(dialog)
        ent_delta.setToolTip(
            "Size of allowable gap near PPI edges, in deg")
        ent_delta.setText(str(self.parameters['delta']))
        gridLayout.addWidget(ent_delta, 3, 1)

        gridLayout_2.addLayout(gridLayout, 0, 0, 1, 1)
        buttonBox = QtGui.QDialogButtonBox(dialog)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel |
                                    QtGui.QDialogButtonBox.Ok)
        gridLayout_2.addWidget(buttonBox, 1, 0, 1, 1)

        dialog.setLayout(gridLayout_2)

        # Connect the signals from OK and Cancel buttons
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)
        retval = dialog.exec_()
        if retval == 1:
            self.parameters['threshold_min'] = float(ent_threshold_min.text())
            threshold_max = ent_threshold_max.text()
            if threshold_max=='Inf':
                self.parameters['threshold_max'] = 'Inf'
            else:
                self.parameters['threshold_max'] = str(threshold_max)
            self.parameters['size'] = int(ent_size.text())
            self.parameters['delta'] = float(ent_delta.text())


_plugins = [Despeckle]