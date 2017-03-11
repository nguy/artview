"""
calculate_attenuation.py
"""

# Load the needed packages
from functools import partial

import pyart
from pyart.config import get_field_name
import time

from ..core import (Component, Variable, common, QtWidgets, QtGui,
                    QtCore, VariableChoose)

import os


class CalculateAttenuation(Component):
    '''
    Interface for executing :py:func:`pyart.correct.calculate_attenuation`
    '''

    Vradar = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class'''
        kwargs, independent = \
            common._SimplePluginStart("CalculateAttenuation").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None,  # Vgatefilter=None,
                 name="CalculateAttenuation", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable.
            A value of None initializes an empty Variable.
        name : string
            Field Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated w/ parent PyQt instance
        '''
        super(CalculateAttenuation, self).__init__(name=name, parent=parent)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QGridLayout(self.central_widget)

        self.despeckleButton = QtWidgets.QPushButton("CalculateAttenuation")
        self.despeckleButton.clicked.connect(self.calculate_attenuation)
        self.layout.addWidget(self.despeckleButton, 0, 0)

        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir))
        config_icon = QtGui.QIcon(os.sep.join([parentdir, 'icons',
                                              "categories-applications-system-icon.png"]))
        self.configButton = QtWidgets.QPushButton(config_icon,"")
        self.layout.addWidget(self.configButton, 0, 1)
        self.configMenu = QtWidgets.QMenu(self)
        self.configButton.setMenu(self.configMenu)

        self.configMenu.addAction(QtWidgets.QAction("Set Parameters", self,
                                                triggered=self.setParameters))
        self.configMenu.addAction(QtWidgets.QAction("Help", self,
                                                triggered=self._displayHelp))
        self.parameters = {
            "radar": None,
            "z_offset": 0,
            "debug": False,
            "doc": 15,
            "fzl": 4000,
            "rhv_min": 0.8,
            "ncp_min": 0.5,
            "a_coef": 0.06,
            "beta": 0.8,
            "refl_field": get_field_name('reflectivity'),
            "ncp_field": get_field_name('normalized_coherent_power'),
            "rhv_field": get_field_name('cross_correlation_ratio'),
            "phidp_field": get_field_name('differential_phase'),
            "spec_at_field": get_field_name('specific_attenuation'),
            "corr_refl_field": get_field_name('corrected_reflectivity'),
            }

        self.parameters_type = [
            ("z_offset", float),
            ("debug", bool),
            ("doc", float),
            ("fzl", float),
            ("rhv_min", float),
            ("ncp_min", float),
            ("a_coef", float),
            ("beta", float),
            ("refl_field", str),
            ("ncp_field", str),
            ("rhv_field", str),
            ("phidp_field", str),
            ("spec_at_field", str),
            ("corr_refl_field", str),
            ]

        self.layout.setColumnStretch(0, 1)

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

        self.sharedVariables = {"Vradar": None}
        self.connectAllVariables()

        self.show()

    def calculate_attenuation(self):
        '''Mount Options and execute
        :py:func:`~pyart.correct.calculate_attenuation`.
        The resulting fields are added to Vradar.
        Vradar is updated, strong or weak depending on overwriting old fields.
        '''
        # test radar
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None, can not perform correction.")
            return
        # mount options
        self.parameters['radar'] = self.Vradar.value

        print(self.parameters)

        # execute
        print("Correcting ..")
        t0 = time.time()
        try:
            spec_at, cor_z = pyart.correct.calculate_attenuation(**self.parameters)
        except:
            import traceback
            error = traceback.format_exc()
            common.ShowLongText("Py-ART fails with following error\n\n" +
                                error)
        t1 = time.time()
        print(("Correction took %fs" % (t1-t0)))

        # verify field overwriting
        spec_at_field_name = self.parameters['spec_at_field']
        corr_refl_field_name = self.parameters['corr_refl_field']

        strong_update = False  # insertion is weak, overwrite strong
        if spec_at_field_name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                spec_at_field_name)
            if resp != QtWidgets.QMessageBox.Ok:
                return
            else:
                strong_update = True

        if corr_refl_field_name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                corr_refl_field_name)
            if resp != QtWidgets.QMessageBox.Ok:
                return
            else:
                strong_update = True

        # add fields and update
        self.Vradar.value.add_field(spec_at_field_name, spec_at, True)
        self.Vradar.value.add_field(corr_refl_field_name, cor_z, True)
        self.Vradar.update(strong_update)
        print("Correction took %fs" % (t1-t0))

    def setParameters(self):
        '''Open set parameters dialog.'''
        parm = common.get_options(self.parameters_type, self.parameters)
        for key in parm.keys():
            self.parameters[key] = parm[key]

    def _displayHelp(self):
        '''Display Py-Art's docstring for help.'''
        common.ShowLongText(pyart.correct.calculate_attenuation.__doc__)


_plugins = [CalculateAttenuation]
