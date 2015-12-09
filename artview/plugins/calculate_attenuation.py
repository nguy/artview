"""
calculate_attenuation.py
"""

# Load the needed packages
from functools import partial

import pyart
import time

from ..core import Component, Variable, common, QtGui, QtCore, VariableChoose


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
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

        self.sharedVariables = {"Vradar": None}
        self.connectAllVariables()

        self.generalLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.generalLayout, 0, 0, 1, 2)

        self.helpButton = QtGui.QPushButton("Help")
        self.helpButton.clicked.connect(self._displayHelp)
        self.layout.addWidget(self.helpButton, 1, 0, 1, 1)

        self.button = QtGui.QPushButton("Correct")
        self.button.clicked.connect(self.calculate_attenuation)
        self.button.setToolTip('Execute pyart.correct.calculate_attenuation')
        self.layout.addWidget(self.button, 1, 1, 1, 1)

        self.addGeneralOptions()

        self.show()

    def addGeneralOptions(self):
        '''Mount Options Layout.'''

        self.radarButton = QtGui.QPushButton("Find Variable")
        self.radarButton.clicked.connect(self.chooseRadar)
        self.generalLayout.addWidget(QtGui.QLabel("Radar"), 0, 0)
        self.generalLayout.addWidget(self.radarButton, 0, 1)

        self.zOffset = QtGui.QDoubleSpinBox()
        self.zOffset.setRange(-1000, 1000)
        self.generalLayout.addWidget(QtGui.QLabel("z_offset"), 1, 0)
        self.generalLayout.addWidget(self.zOffset, 1, 1)

        self.debug = QtGui.QCheckBox("debug")
        self.debug.setChecked(False)
        self.generalLayout.addWidget(self.debug, 2, 1)

        self.doc = QtGui.QDoubleSpinBox()
        self.doc.setRange(-1000, 1000)
        self.doc.setValue(15)
        self.generalLayout.addWidget(QtGui.QLabel("doc"), 3, 0)
        self.generalLayout.addWidget(self.doc, 3, 1)

        self.fzl = QtGui.QDoubleSpinBox()
        self.fzl.setRange(-100000, 1000000)
        self.fzl.setValue(4000)
        self.generalLayout.addWidget(QtGui.QLabel("fzl"), 4, 0)
        self.generalLayout.addWidget(self.fzl, 4, 1)

        self.rhvMin = QtGui.QDoubleSpinBox()
        self.rhvMin.setRange(-100000, 1000000)
        self.rhvMin.setValue(0.8)
        self.generalLayout.addWidget(QtGui.QLabel("rhv_min"), 5, 0)
        self.generalLayout.addWidget(self.rhvMin, 5, 1)

        self.ncpMin = QtGui.QDoubleSpinBox()
        self.ncpMin.setRange(-100000, 1000000)
        self.ncpMin.setValue(0.5)
        self.generalLayout.addWidget(QtGui.QLabel("ncp_min"), 6, 0)
        self.generalLayout.addWidget(self.ncpMin, 6, 1)

        self.aCoef = QtGui.QDoubleSpinBox()
        self.aCoef.setRange(-100000, 1000000)
        self.aCoef.setValue(0.06)
        self.generalLayout.addWidget(QtGui.QLabel("a_coef"), 7, 0)
        self.generalLayout.addWidget(self.aCoef, 7, 1)

        self.beta = QtGui.QDoubleSpinBox()
        self.beta.setRange(-100000, 1000000)
        self.beta.setValue(0.8)
        self.generalLayout.addWidget(QtGui.QLabel("beta"), 8, 0)
        self.generalLayout.addWidget(self.beta, 8, 1)

        self.reflField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("refl_field"), 9, 0)
        self.generalLayout.addWidget(self.reflField, 9, 1)

        self.ncpField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("ncp_field"), 10, 0)
        self.generalLayout.addWidget(self.ncpField, 10, 1)

        self.rhvField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("rhv_field"), 11, 0)
        self.generalLayout.addWidget(self.rhvField, 11, 1)

        self.phidpField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("phidp_field"), 12, 0)
        self.generalLayout.addWidget(self.phidpField, 12, 1)

        self.specAtField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("spec_at_field"), 13, 0)
        self.generalLayout.addWidget(self.specAtField, 13, 1)

        self.corrReflField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("corr_refl_field"), 14, 0)
        self.generalLayout.addWidget(self.corrReflField, 14, 1)

    def chooseRadar(self):
        '''Get Radar with :py:class:`~artview.core.VariableChoose`'''
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.Vradar = getattr(item[1], item[2])

    def _displayHelp(self):
        '''Display Py-Art's docstring for help.'''
        common.ShowLongText(pyart.correct.calculate_attenuation.__doc__)

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
        args = {
            'radar': self.Vradar.value,
            'z_offset': self.zOffset.value(),
            'debug': self.debug.isChecked(),
            'doc': self.doc.value(),
            'fzl': self.fzl.value(),
            'rhv_min': self.rhvMin.value(),
            'ncp_min': self.ncpMin.value(),
            'a_coef': self.aCoef.value(),
            'beta': self.beta.value(),
            'refl_field': [None if a == "" else a for a in (
                str(self.reflField.text()),)][0],
            'ncp_field': [None if a == "" else a for a in (
                str(self.ncpField.text()),)][0],
            'rhv_field': [None if a == "" else a for a in (
                str(self.rhvField.text()),)][0],
            'phidp_field': [None if a == "" else a for a in (
                str(self.phidpField.text()),)][0],
            'spec_at_field': [None if a == "" else a for a in (
                str(self.specAtField.text()),)][0],
            'corr_refl_field': [None if a == "" else a for a in (
                str(self.corrReflField.text()),)][0],
        }
        print(args)

        # execute
        print("Correcting ..")
        t0 = time.time()
        try:
            spec_at, cor_z = pyart.correct.calculate_attenuation(**args)
        except:
            import traceback
            error = traceback.format_exc()
            common.ShowLongText("Py-ART fails with following error\n\n" +
                                error)
        t1 = time.time()
        print(("Correction took %fs" % (t1-t0)))

        # verify field overwriting
        if args['spec_at_field'] is None:
            spec_at_field_name = "specific_attenuation"
        else:
            spec_at_field_name = args['spec_at_field']

        if args['corr_refl_field'] is None:
            corr_refl_field_name = "corrected_reflectivity"
        else:
            corr_refl_field_name = args['corr_refl_field']

        strong_update = False  # insertion is weak, overwrite strong
        if spec_at_field_name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                spec_at_field_name)
            if resp != QtGui.QMessageBox.Ok:
                return
            else:
                strong_update = True

        if corr_refl_field_name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                corr_refl_field_name)
            if resp != QtGui.QMessageBox.Ok:
                return
            else:
                strong_update = True

        # add fields and update
        self.Vradar.value.add_field(spec_at_field_name, spec_at, True)
        self.Vradar.value.add_field(corr_refl_field_name, cor_z, True)
        self.Vradar.update(strong_update)
        print("Correction took %fs" % (t1-t0))

    def _clearLayout(self, layout):
        '''recursively remove items from layout.'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clearLayout(item.layout())

_plugins = [CalculateAttenuation]
