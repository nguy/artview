"""

"""

# Load the needed packages
from functools import partial

import pyart
from pyart.config import get_field_name
import time
import os

from ..core import (Component, Variable, common, QtGui, QtWidgets,
                    QtCore, VariableChoose)


class DealiasRegionBased(Component):
    '''
    Interface for executing :py:func:`pyart.correct.dealias_region_based`
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgatefilter = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class'''
        kwargs, independent = \
            common._SimplePluginStart("DealiasRegionBased").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None, Vgatefilter=None,
                 name="DealiasRegionBased", parent=None):
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
        super(DealiasRegionBased, self).__init__(name=name, parent=parent)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QGridLayout(self.central_widget)

        self.despeckleButton = QtWidgets.QPushButton("DealiasRegionBased")
        self.despeckleButton.clicked.connect(self.dealias_region_based)
        self.layout.addWidget(self.despeckleButton, 0, 0)

        parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir))
        config_icon = QtGui.QIcon(os.sep.join(
            [parentdir, 'icons', "categories-applications-system-icon.png"]))
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
            "gatefilter": None,
            "interval_splits": 3,
            "interval_limits": None,
            "skip_between_rays": 100,
            "skip_along_ray": 100,
            "centered": True,
            "nyquist_velocity": "",
            "check_nyquist_uniform": False,
            "rays_wrap_around": True,
            "keep_original": False,
            "vel_field": get_field_name('velocity'),
            "corr_vel_field": get_field_name('corrected_velocity'),
            }


        self.parameters_type = [
            ("interval_splits", int),
            ("skip_between_rays", int),
            ("skip_along_ray", int),
            ("centered", bool),
            ("nyquist_velocity", common.float_or_none),
            ("check_nyquist_uniform", bool),
            ("rays_wrap_around", bool),
            ("keep_original", bool),
            ("vel_field", str),
            ("corr_vel_field", str),
            ]

        self.layout.setColumnStretch(0, 1)

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

        if Vgatefilter is None:
            self.Vgatefilter = Variable(None)
        else:
            self.Vgatefilter = Vgatefilter

        self.sharedVariables = {"Vradar": None,
                                "Vgatefilter": None}
        self.connectAllVariables()

        self.show()

    def dealias_region_based(self):
        '''Mount Options and execute.
        :py:func:`~pyart.correct.dealias_region_based`.
        The resulting fields are added to Vradar.
        Vradar is updated, strong or weak depending on overwriting old fields.
        '''
        # test radar
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None, can not perform correction.")
            return
        self.parameters['radar'] = self.Vradar.value
        self.parameters['gatefilter'] = self.Vgatefilter.value
        print(self.parameters)

        # execute
        print("Correcting ..")
        t0 = time.time()
        try:
            field = pyart.correct.dealias_region_based(**self.parameters)
        except:
            import traceback
            error = traceback.format_exc()
            common.ShowLongText("Py-ART fails with following error\n\n" +
                                error)
        t1 = time.time()
        print(("Correction took %fs" % (t1-t0)))

        # verify field overwriting
        name = self.parameters['corr_vel_field']

        strong_update = False  # insertion is weak, overwrite strong
        if name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                name)
            if resp != QtWidgets.QMessageBox.Ok:
                return
            else:
                strong_update = True

        # add fields and update
        self.Vradar.value.add_field(name, field, True)
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
        common.ShowLongText(pyart.correct.dealias_region_based.__doc__)


_plugins = [DealiasRegionBased]
