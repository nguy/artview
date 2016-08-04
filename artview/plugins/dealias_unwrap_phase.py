"""

"""

# Load the needed packages
from functools import partial

import pyart
import time

from ..core import Component, Variable, common, QtGui, QtCore, VariableChoose


class DealiasUnwrapPhase(Component):
    '''
    Interface for executing :py:func:`pyart.correct.dealias_unwrap_phase`
    '''

    Vradar = None  #: see :ref:`shared_variable`
#    Vgatefilter = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("DealiasUnwrapPhase").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None,  # Vgatefilter=None,
                 name="DealiasUnwrapPhase", parent=None):
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

#        Vgatefilter : :py:class:`~artview.core.core.Variable` instance
#           Gatefilter signal variable.
#            A value of None initializes an empty Variable.
#            [Not Implemented]

        super(DealiasUnwrapPhase, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

#        if Vgatefilter is None:
#            self.Vgatefilter = Variable(None)
#        else:
#            self.Vgatefilter = Vgatefilter

        self.sharedVariables = {"Vradar": self.NewRadar, }
#                                "Vgatefilter": None}
        self.connectAllVariables()

        self.generalLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.generalLayout, 0, 0, 1, 2)

        self.helpButton = QtGui.QPushButton("Help")
        self.helpButton.clicked.connect(self._displayHelp)
        self.layout.addWidget(self.helpButton, 1, 0, 1, 1)

        self.button = QtGui.QPushButton("Correct")
        self.button.clicked.connect(self.dealias_unwrap_phase)
        self.button.setToolTip('Execute pyart.correct.dealias_unwrap_phase')
        self.layout.addWidget(self.button, 1, 1, 1, 1)

        self.addGeneralOptions()

        self.NewRadar(None, True)

        self.show()

    def addGeneralOptions(self):
        '''Mount Options Layout.'''
        self.radarButton = QtGui.QPushButton("Find Variable")
        self.radarButton.clicked.connect(self.chooseRadar)
        self.generalLayout.addWidget(QtGui.QLabel("Radar"), 0, 0)
        self.generalLayout.addWidget(self.radarButton, 0, 1)

        self.unwrapUnit = QtGui.QComboBox()
        self.unwrapUnit.addItem('ray')
        self.unwrapUnit.addItem('sweep')
        self.unwrapUnit.addItem('volume')
        self.unwrapUnit.setCurrentIndex(1)
        self.generalLayout.addWidget(QtGui.QLabel("unwrap_unit"), 1, 0)
        self.generalLayout.addWidget(self.unwrapUnit, 1, 1)

        # XXX must implement deactivation
        self.nyquistVelocity = QtGui.QDoubleSpinBox()
        self.nyquistVelocity.setRange(-1, 1000)
        self.nyquistVelocity.setValue(-1)
        self.generalLayout.addWidget(QtGui.QLabel("nyquist_velocity"), 2, 0)
        self.generalLayout.addWidget(self.nyquistVelocity, 2, 1)

        self.checkNyquistUniform = QtGui.QCheckBox("check_nyquist_uniform")
        self.checkNyquistUniform.setChecked(False)
        self.generalLayout.addWidget(self.checkNyquistUniform, 3, 1)

#        self.generalLayout.addWidget(QtGui.QLabel("gatefilter"), 4, 0)
        # XXX NotImplemented
#        self.generalLayout.addWidget(QtGui.QLabel("NotImplemented"), 4, 1)

        self.raysWrapAround = QtGui.QCheckBox("rays_wrap_around")
        self.raysWrapAround.setChecked(True)
        self.generalLayout.addWidget(self.raysWrapAround, 5, 1)

        self.keepOriginal = QtGui.QCheckBox("keep_original")
        self.keepOriginal.setChecked(False)
        self.generalLayout.addWidget(self.keepOriginal, 6, 1)

        self.velField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("vel_field"), 7, 0)
        self.generalLayout.addWidget(self.velField, 7, 1)

        self.corrVelField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("corr_vel_field"), 8, 0)
        self.generalLayout.addWidget(self.corrVelField, 8, 1)

        self.skipChecks = QtGui.QCheckBox("skip_checks")
        self.skipChecks.setChecked(False)
        self.generalLayout.addWidget(self.skipChecks, 9, 1)

    def chooseRadar(self):
        '''Get Radar with :py:class:`~artview.core.VariableChoose`'''
        item = VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            # disconnect old
            self.disconnectSharedVariable('Vradar')
            self.Vradar = getattr(item[1], item[2])
            # connect new
            self.connectSharedVariable('Vradar')

    def NewRadar(self, variable, strong):
        '''respond to change in radar.'''
        if self.Vradar.value is None:
            return

        if self.Vradar.value.scan_type == 'ppi':
            self.raysWrapAround.setChecked(True)
        else:
            self.raysWrapAround.setChecked(False)

    def _displayHelp(self):
        '''Display Py-Art's docstring for help.'''
        common.ShowLongText(pyart.correct.dealias_unwrap_phase.__doc__)

    def dealias_unwrap_phase(self):
        '''Mount Options and execute
        :py:func:`~pyart.correct.dealias_unwrap_phase`.
        The resulting fields are added to Vradar.
        Vradar is updated, strong or weak depending on overwriting old fields.
        '''
        # test radar
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None, can not perform correction")
            return
        args = {
            'radar': self.Vradar.value,
            'unwrap_unit': str(self.unwrapUnit.currentText()),
            'nyquist_velocity': [i if i >= 0 else None for i in (
                self.nyquistVelocity.value(),)][0],
            'check_nyquist_uniform': self.checkNyquistUniform.isChecked(),
            # 'gatefilter': False,
            'rays_wrap_around': self.raysWrapAround.isChecked(),
            'keep_original': self.keepOriginal.isChecked(),
            'vel_field': [None if a == "" else a for a in (
                str(self.velField.text()),)][0],
            'corr_vel_field': [None if a == "" else a for a in (
                str(self.corrVelField.text()),)][0],
            'skip_checks': self.skipChecks.isChecked(),
        }
        print(args)

        # execute
        print("Correcting ..")
        t0 = time.time()
        try:
            field = pyart.correct.dealias_unwrap_phase(**args)
        except:
            import traceback
            error = traceback.format_exc()
            common.ShowLongText("Py-ART fails with following error\n\n" +
                                error)
        t1 = time.time()
        print(("Correction took %fs" % (t1-t0)))

        # verify field overwriting
        if args['corr_vel_field'] is None:
            name = "dealiased_velocity"
        else:
            name = args['corr_vel_field']

        strong_update = False  # insertion is weak, overwrite strong
        if name in self.Vradar.value.fields.keys():
            resp = common.ShowQuestion(
                "Field %s already exists! Do you want to over write it?" %
                name)
            if resp != QtGui.QMessageBox.Ok:
                return
            else:
                strong_update = True

        # add fields and update
        self.Vradar.value.add_field(name, field, True)
        self.Vradar.value.changed = True
        self.Vradar.update(strong_update)
        print("Correction took %fs" % (t1-t0))

    def _clearLayout(self, layout):
        '''recursively remove items from layout'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clearLayout(item.layout())

_plugins = [DealiasUnwrapPhase]
