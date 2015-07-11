"""

"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial

from .. import core
common = core.common

import pyart
import time

class DealiasRegionBased(core.Component):
    '''
    Interfase for executing :py:func:`pyart.correct.dealias_region_based`
    '''

    Vradar = None #: see :ref:`shared_variable`
    Vgatefilter = None #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Grafical Interface for Starting this Class'''
        kwargs, independent = common._SimplePluginStart("DealiasRegionBased").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None, Vgatefilter=None, name="DealiasRegionBased", parent=None):
        '''Initialize the class to create the interface

        Parameters
        ----------
        [Optional]
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable. 
            A value of None initializes an empty Variable.
        Vgatefilter : :py:class:`~artview.core.core.Variable` instance
            Gatefilter signal variable. 
            A value of None initializes an empty Variable.
            [Not Implemented]
        name : string
            Field Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt instance.
        '''
        super(DealiasRegionBased, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        if Vradar is None:
            self.Vradar = core.Variable(None)
        else:
            self.Vradar = Vradar

        if Vgatefilter is None:
            self.Vgatefilter = core.Variable(None)
        else:
            self.Vgatefilter = Vgatefilter

        self.sharedVariables = {"Vradar": self.newRadar,
                                "Vgatefilter": None}
        self.connectAllVariables()
        
        self.generalLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.generalLayout, 0, 0, 1, 2)

        self.button = QtGui.QPushButton("Help")
        self.button.clicked.connect(self.displayHelp)
        self.layout.addWidget(self.button, 1, 0, 1, 1)

        self.button = QtGui.QPushButton("Correct")
        self.button.clicked.connect(self.dealias_region_based)
        self.layout.addWidget(self.button, 1, 1, 1, 1)
        self.addGeneralOptions()

        self.newRadar(None, None, True)

        self.show()

    def addGeneralOptions(self):
        '''Mount Options Layout'''
        self.radarButton = QtGui.QPushButton("Find Variable")
        self.radarButton.clicked.connect(self.chooseRadar)
        self.generalLayout.addWidget(QtGui.QLabel("Radar"), 0, 0)
        self.generalLayout.addWidget(self.radarButton, 0, 1)

        self.intervalSplits = QtGui.QSpinBox()
        self.intervalSplits.setRange(0,1000000)
        self.intervalSplits.setValue(3)
        self.generalLayout.addWidget(QtGui.QLabel("interval_splits"), 1, 0)
        self.generalLayout.addWidget(self.intervalSplits, 1, 1)

        self.generalLayout.addWidget(QtGui.QLabel("interval_limits"), 2, 0)
        self.generalLayout.addWidget(QtGui.QLabel("NotImplemented"), 2, 1)

        self.skipBetweenRays = QtGui.QSpinBox()
        self.skipBetweenRays.setRange(0,1000000)
        self.skipBetweenRays.setValue(100)
        self.generalLayout.addWidget(QtGui.QLabel("skip_between_rays"), 3, 0)
        self.generalLayout.addWidget(self.skipBetweenRays, 3, 1)

        self.skipAlongRay = QtGui.QSpinBox()
        self.skipAlongRay.setRange(0,1000000)
        self.skipAlongRay.setValue(100)
        self.generalLayout.addWidget(QtGui.QLabel("skip_along_ray"), 4, 0)
        self.generalLayout.addWidget(self.skipAlongRay, 4, 1)

        self.centered = QtGui.QCheckBox("centered")
        self.centered.setChecked(True)
        self.generalLayout.addWidget(self.centered, 5, 1)

        self.nyquistVelocity = QtGui.QDoubleSpinBox() #XXX must implement desactvation
        self.nyquistVelocity.setRange(-1,1000)
        self.nyquistVelocity.setValue(-1)
        self.generalLayout.addWidget(QtGui.QLabel("nyquist_velocity"), 6, 0)
        self.generalLayout.addWidget(self.nyquistVelocity, 6, 1)

        self.checkNyquistUniform = QtGui.QCheckBox("check_nyquist_uniform")
        self.checkNyquistUniform.setChecked(False)
        self.generalLayout.addWidget(self.checkNyquistUniform, 7, 1)

        self.generalLayout.addWidget(QtGui.QLabel("gatefilter"), 8, 0) #XXX NotImplemented
        self.generalLayout.addWidget(QtGui.QLabel("NotImplemented"), 8, 1)

        self.raysWrapAround = QtGui.QCheckBox("rays_wrap_around")
        self.raysWrapAround.setChecked(True)
        self.generalLayout.addWidget(self.raysWrapAround, 9, 1)

        self.keepOriginal = QtGui.QCheckBox("keep_original")
        self.keepOriginal.setChecked(False)
        self.generalLayout.addWidget(self.keepOriginal, 10, 1)

        self.velField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("vel_field"), 11, 0)
        self.generalLayout.addWidget(self.velField, 11, 1)

        self.corrVelField = QtGui.QLineEdit("")
        self.generalLayout.addWidget(QtGui.QLabel("corr_vel_field"), 12, 0)
        self.generalLayout.addWidget(self.corrVelField, 12, 1)

    def chooseRadar(self):
        '''Get Radar with :py:class:`~artview.core.VariableChoose`'''
        item = core.VariableChoose().chooseVariable()
        if item is None:
            return
        else:
            self.disconnectSharedVariable('Vradar') # disconect old
            self.Vradar = getattr(item[1],item[2])
            self.connectSharedVariable('Vradar') # conect new

    def newRadar(self, variable, value, strong):
        ''' respond to change in radar '''
        if self.Vradar.value is None:
            return

        if self.Vradar.value.scan_type == 'ppi':
            self.raysWrapAround.setChecked(True)
        else:
            self.raysWrapAround.setChecked(False)

    def displayHelp(self):
        '''Display pyart's docstring for help'''
        common.ShowLongText(pyart.correct.dealias_region_based.__doc__)

    def dealias_region_based(self):
        '''Mount Options and execute :py:func:`~pyart.correct.dealias_region_based`.
        The resulting fields are added to Vradar.
        Vradar is updated, strong or weak depending on overwriting old fields.
        '''
        # test radar
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None, can not perform correction")
            return
        args = {
            'radar': self.Vradar.value,
            'interval_splits': self.intervalSplits.value(),
            'interval_limits': None,
            'skip_between_rays': self.skipBetweenRays.value(),
            'skip_along_ray': self.skipAlongRay.value(),
            'centered': self.centered.isChecked(),
            'nyquist_velocity': [i if i>=0 else None for i in (self.nyquistVelocity.value(),)][0],
            'check_nyquist_uniform': self.checkNyquistUniform.isChecked(),
            'gatefilter': False,
            'rays_wrap_around': self.raysWrapAround.isChecked(),
            'keep_original': self.keepOriginal.isChecked(),
            'vel_field': [None if a=="" else a for a in (str(self.velField.text()),)][0],
            'corr_vel_field': [None if a=="" else a for a in (str(self.corrVelField.text()),)][0],
        }
        print args

        # execute
        print "Correcting .."
        t0 = time.time()
        field = pyart.correct.dealias_region_based(**args)
        t1 = time.time()
        common.ShowWarning("Correction took %fs"%(t1-t0))

        # verify field overwriting
        if args['corr_vel_field'] is None:
            name = "dealiased_velocity"
        else:
            name = args['corr_vel_field']

        strong_update = False #insertion is weak, overwrite strong
        if name in self.Vradar.value.fields.keys():
            resp=common.ShowQuestion("Field %s already exists! Do you want to overwrite it?"%name)
            if resp != QtGui.QMessageBox.Ok:
                return
            else:
                strong_update = True

        # add fields and update
        self.Vradar.value.add_field(name, field, True)
        self.Vradar.change(self.Vradar.value, strong_update)
        print "Correction took %fs"%(t1-t0)

    def _clearLayout(self, layout):
        '''recursively remove items from layout'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clearLayout(item.layout())

_plugins=[DealiasRegionBased]
