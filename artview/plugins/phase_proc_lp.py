"""

"""

# Load the needed packages
from functools import partial

import pyart
from pyart.config import get_field_name
import time
import os

from ..core import (Component, Variable, common, QtWidgets, QtGui,
                    QtCore, VariableChoose)


class PhaseProcLp(Component):
    '''
    Interface for executing :py:func:`pyart.correct.phase_proc_lp`
    '''

    Vradar = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("PhaseProcLp").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None,  # Vgatefilter=None,
                 name="PhaseProcLp", parent=None):
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
        super(PhaseProcLp, self).__init__(name=name, parent=parent)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QGridLayout(self.central_widget)

        self.despeckleButton = QtWidgets.QPushButton("PhaseProcLp")
        self.despeckleButton.clicked.connect(self.phase_proc_lp)
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
            "self_const": 60000,
            "low_z": 10,
            "high_z": 53,
            "min_phidp": 0.01,
            "min_ncp": 0.5,
            "min_rhv": 0.8,
            "fzl": 4000,
            "sys_phase": 0,
            "overide_sys_phase": False,
            "nowrap": None,
            "really_verbose": False,
            "LP_solver": "cylp",
            "refl_field": get_field_name('reflectivity'),
            "ncp_field": get_field_name('normalized_coherent_power'),
            "rhv_field": get_field_name('cross_correlation_ratio'),
            "phidp_field": get_field_name('differential_phase'),
            "kdp_field": get_field_name('specific_differential_phase'),
            "unf_field": get_field_name('unfolded_differential_phase'),
            "window_len": 35,
            "proc": 1,
            "reproc_phase": "repro_phase",
            "sob_kdp": "sob_kdp",
            }

        self.parameters_type = [
            ("z_offset", float),
            ("debug", bool),
            ("self_const", float),
            ("low_z", float),
            ("high_z", float),
            ("min_phidp", float),
            ("min_ncp", float),
            ("min_rhv", float),
            ("fzl", float),
            ("sys_phase", float),
            ("overide_sys_phase", bool),
            ("nowrap", int, None),
            ("really_verbose", bool),
            ("LP_solver", ("pyglpk", "cvxopt", "cylp", "cylp_mp")),
            ("refl_field", str),
            ("ncp_field", str),
            ("rhv_field", str),
            ("phidp_field", str),
            ("kdp_field", str),
            ("unf_field", str),
            ("window_len", int),
            ("proc", int),
            ("reproc_phase", str),
            ("sob_kdp", str),
            ]

        self.layout.setColumnStretch(0, 1)

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

        self.sharedVariables = {"Vradar": None}
        self.connectAllVariables()

        self.show()

    def phase_proc_lp(self):
        '''Mount Options and execute :py:func:`~pyart.correct.phase_proc_lp`.
        The resulting fields are added to Vradar.
        Vradar is updated, strong or weak depending on overwriting old fields.
        '''
        # test radar
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None, can not perform correction.")
            return
        # mount options
        self.parameters['radar'] = self.Vradar.value
        parameters = self.parameters.copy()
        del parameters["reproc_phase"]
        del parameters["sob_kdp"]

        print(parameters)

        # execute
        print("Correcting ..")
        t0 = time.time()
        try:
            reproc_phase, sob_kdp = pyart.correct.phase_proc_lp(**parameters)
        except:
            import traceback
            error = traceback.format_exc()
            common.ShowLongText("Py-ART fails with following error\n\n" +
                                error)
        t1 = time.time()
        print(("Correction took %fs" % (t1-t0)))

        # verify field overwriting
        reproc_phase_name = self.parameters["reproc_phase"]
        sob_kdp_name = self.parameters["sob_kdp"]

        strong_update = False  # insertion is weak, overwrite strong
        if reproc_phase_name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                reproc_phase_name)
            if resp != QtWidgets.QMessageBox.Ok:
                return
            else:
                strong_update = True

        if sob_kdp_name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                sob_kdp_name)
            if resp != QtWidgets.QMessageBox.Ok:
                return
            else:
                strong_update = True

        # add fields and update
        self.Vradar.value.add_field(reproc_phase_name, reproc_phase, True)
        self.Vradar.value.add_field(sob_kdp_name, sob_kdp, True)
        self.Vradar.value.changed = True
        self.Vradar.update(strong_update)
        print("Correction took %fs" % (t1-t0))

    def setParameters(self):
        '''Open set parameters dialog.'''
        parm = common.get_options(self.parameters_type, self.parameters)
        for key in parm.keys():
            self.parameters[key] = parm[key]

    def _displayHelp(self):
        '''Display Py-Art's docstring for help.'''
        common.ShowLongText(pyart.correct.phase_proc_lp.__doc__)


_plugins = [PhaseProcLp]
