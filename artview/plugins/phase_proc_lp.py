"""

"""

# Load the needed packages
from functools import partial

import pyart
import time

from ..core import Component, Variable, common, QtGui, QtCore, VariableChoose


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
        self.button.clicked.connect(self.phase_proc_lp)
        self.button.setToolTip('Execute pyart.correct.phase_proc_lp')
        self.layout.addWidget(self.button, 1, 1, 1, 1)

        self.addGeneralOptions()

        self.show()

    def addGeneralOptions(self):
        '''Mount Options Layout.'''
        self.radarButton = QtGui.QPushButton("Find Variable")
        self.radarButton.clicked.connect(self.chooseRadar)
        self.generalLayout.addWidget(QtGui.QLabel("Radar"), 0, 0)
        self.generalLayout.addWidget(self.radarButton, 0, 1)

        self.offset = QtGui.QDoubleSpinBox()
        self.offset.setRange(-1000, 1000)
        self.generalLayout.addWidget(QtGui.QLabel("offset"), 1, 0)
        self.generalLayout.addWidget(self.offset, 1, 1)

        self.debug = QtGui.QCheckBox("debug")
        self.debug.setChecked(False)
        self.generalLayout.addWidget(self.debug, 2, 1)

        self.selfConst = QtGui.QDoubleSpinBox()
        self.selfConst.setRange(-1000000, 10000000)
        self.selfConst.setValue(60000)
        self.generalLayout.addWidget(QtGui.QLabel("self_const"), 3, 0)
        self.generalLayout.addWidget(self.selfConst, 3, 1)

        self.lowZ = QtGui.QDoubleSpinBox()
        self.lowZ.setRange(-1000000, 10000000)
        self.lowZ.setValue(10)
        self.generalLayout.addWidget(QtGui.QLabel("low_z"), 4, 0)
        self.generalLayout.addWidget(self.lowZ, 4, 1)

        self.highZ = QtGui.QDoubleSpinBox()
        self.highZ.setRange(-1000000, 10000000)
        self.highZ.setValue(53)
        self.generalLayout.addWidget(QtGui.QLabel("high_z"), 5, 0)
        self.generalLayout.addWidget(self.highZ, 5, 1)

        self.minPhidp = QtGui.QDoubleSpinBox()
        self.minPhidp.setRange(-1000000, 10000000)
        self.minPhidp.setValue(0.01)
        self.generalLayout.addWidget(QtGui.QLabel("min_phidp"), 6, 0)
        self.generalLayout.addWidget(self.minPhidp, 6, 1)

        self.minNcp = QtGui.QDoubleSpinBox()
        self.minNcp.setRange(-1000000, 10000000)
        self.minNcp.setValue(0.5)
        self.generalLayout.addWidget(QtGui.QLabel("min_ncp"), 7, 0)
        self.generalLayout.addWidget(self.minNcp, 7, 1)

        self.minRhv = QtGui.QDoubleSpinBox()
        self.minRhv.setRange(-1000000, 10000000)
        self.minRhv.setValue(0.8)
        self.generalLayout.addWidget(QtGui.QLabel("min_rhv"), 8, 0)
        self.generalLayout.addWidget(self.minRhv, 8, 1)

        self.fzl = QtGui.QDoubleSpinBox()
        self.fzl.setRange(-100000, 1000000)
        self.fzl.setValue(4000)
        self.generalLayout.addWidget(QtGui.QLabel("fzl"), 9, 0)
        self.generalLayout.addWidget(self.fzl, 9, 1)

        self.sysPhase = QtGui.QDoubleSpinBox()
        self.sysPhase.setRange(-100000, 1000000)
        self.generalLayout.addWidget(QtGui.QLabel("sys_phase"), 10, 0)
        self.generalLayout.addWidget(self.sysPhase, 10, 1)

        self.overideSysPhase = QtGui.QCheckBox("overide_sys_phase")
        self.overideSysPhase.setChecked(False)
        self.generalLayout.addWidget(self.overideSysPhase, 11, 1)

        self.nowrap = QtGui.QSpinBox()  # XXX must implement deactivation
        self.nowrap.setRange(-1, 1000000)
        self.nowrap.setValue(-1)
        self.generalLayout.addWidget(QtGui.QLabel("nowrap"), 12, 0)
        self.generalLayout.addWidget(self.nowrap, 12, 1)

        self.reallyVerbose = QtGui.QCheckBox("really_verbose")
        self.reallyVerbose.setChecked(False)
        self.generalLayout.addWidget(self.reallyVerbose, 13, 1)

        self.lpSolver = QtGui.QComboBox()
        self.lpSolver.addItem('pyglpk')
        self.lpSolver.addItem('cvxopt')
        self.lpSolver.addItem('cylp')
        self.lpSolver.addItem('cylp_mp')
        self.lpSolver.setCurrentIndex(2)
        self.generalLayout.addWidget(QtGui.QLabel("LP_solver"), 14, 0)
        self.generalLayout.addWidget(self.lpSolver, 14, 1)

        self.reflField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("refl_field"), 15, 0)
        self.generalLayout.addWidget(self.reflField, 15, 1)

        self.ncpField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("ncp_field"), 16, 0)
        self.generalLayout.addWidget(self.ncpField, 16, 1)

        self.rhvField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("rhv_field"), 17, 0)
        self.generalLayout.addWidget(self.rhvField, 17, 1)

        self.phidpField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("phidp_field"), 18, 0)
        self.generalLayout.addWidget(self.phidpField, 18, 1)

        self.kdpField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("kdp_field"), 19, 0)
        self.generalLayout.addWidget(self.kdpField, 19, 1)

        self.unfField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("unf_field"), 20, 0)
        self.generalLayout.addWidget(self.unfField, 20, 1)

        self.windowLen = QtGui.QSpinBox()
        self.windowLen.setRange(0, 1000000)
        self.windowLen.setValue(35)
        self.generalLayout.addWidget(QtGui.QLabel("window_len"), 21, 0)
        self.generalLayout.addWidget(self.windowLen, 21, 1)

        self.proc = QtGui.QSpinBox()
        self.proc.setRange(0, 1000000)
        self.proc.setValue(1)
        self.generalLayout.addWidget(QtGui.QLabel("proc"), 22, 0)
        self.generalLayout.addWidget(self.proc, 22, 1)

        self.reprocPhase = QtGui.QLineEdit("reproc_phase")
        self.generalLayout.addWidget(QtGui.QLabel("reproc_phase"), 23, 0)
        self.generalLayout.addWidget(self.reprocPhase, 23, 1)

        self.sobKdp = QtGui.QLineEdit("sob_kdp")
        self.generalLayout.addWidget(QtGui.QLabel("sob_kdp"), 24, 0)
        self.generalLayout.addWidget(self.sobKdp, 24, 1)

    def chooseRadar(self):
        '''Get Radar with :py:class:`~artview.core.VariableChoose`'''
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.Vradar = getattr(item[1], item[2])

    def _displayHelp(self):
        '''Display Py-Art's docstring for help.'''
        common.ShowLongText(pyart.correct.phase_proc_lp.__doc__)

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
        args = {
            'radar': self.Vradar.value,
            'offset': self.offset.value(),
            'debug': self.debug.isChecked(),
            'self_const': self.selfConst.value(),
            'low_z': self.lowZ.value(),
            'high_z': self.highZ.value(),
            'min_phidp': self.minPhidp.value(),
            'min_ncp': self.minNcp.value(),
            'min_rhv': self.minRhv.value(),
            'fzl': self.fzl.value(),
            'sys_phase': self.sysPhase.value(),
            'overide_sys_phase': self.overideSysPhase.isChecked(),
            'nowrap': [i if i >= 0 else None for i in (
                self.nowrap.value(),)][0],
            'really_verbose': self.reallyVerbose.isChecked(),
            'LP_solver': str(self.lpSolver.currentText()),
            'refl_field': [None if a == "" else a for a in (
                str(self.reflField.text()),)][0],
            'ncp_field': [None if a == "" else a for a in (
                str(self.ncpField.text()),)][0],
            'rhv_field': [None if a == "" else a for a in (
                str(self.rhvField.text()),)][0],
            'phidp_field': [None if a == "" else a for a in (
                str(self.phidpField.text()),)][0],
            'kdp_field': [None if a == "" else a for a in (
                str(self.kdpField.text()),)][0],
            'unf_field': [None if a == "" else a for a in (
                str(self.unfField.text()),)][0],
            'window_len': self.windowLen.value(),
            'proc': self.proc.value(),
        }
        print(args)

        # execute
        print("Correcting ..")
        t0 = time.time()
        try:
            reproc_phase, sob_kdp = pyart.correct.phase_proc_lp(**args)
        except:
            import traceback
            error = traceback.format_exc()
            common.ShowLongText("Py-ART fails with following error\n\n" +
                                error)
        t1 = time.time()
        print(("Correction took %fs" % (t1-t0)))

        # verify field overwriting
        reproc_phase_name = str(self.reprocPhase.text())
        sob_kdp_name = str(self.sobKdp.text())

        strong_update = False  # insertion is weak, overwrite strong
        if reproc_phase_name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                reproc_phase_name)
            if resp != QtGui.QMessageBox.Ok:
                return
            else:
                strong_update = True

        if sob_kdp_name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                sob_kdp_name)
            if resp != QtGui.QMessageBox.Ok:
                return
            else:
                strong_update = True

        # add fields and update
        self.Vradar.value.add_field(reproc_phase_name, reproc_phase, True)
        self.Vradar.value.add_field(sob_kdp_name, sob_kdp, True)
        self.Vradar.value.changed = True
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

_plugins = [PhaseProcLp]
