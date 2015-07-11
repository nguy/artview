"""
tilt.py 

Class instance used for modifying tilt via Display window.
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial

from ..core import Variable, Component

class TiltButtonWindow(Component):
    '''Class to display the Window with Tilt Buttons.'''

    Vradar = None #: see :ref:`shared_variable`
    Vgrid = None #: see :ref:`shared_variable`
    Vtilt = None #: see :ref:`shared_variable`

    def __init__(self, Vtilt, Vradar=None, Vgrid=None, name="TiltButtons", parent=None):
        '''Initialize the class to create the Tilt Selection interface.

        Parameters
        ----------
        Vtilt : :py:class:`~artview.core.core.Variable` instance
            Tilt signal variable.
        Vradar, Vgrid : :py:class:`~artview.core.core.Variable` instance
            Radar/Grid signal variable. None will create empty variable.
            For correct behavior one and just one of those should be provided
        [Optional]
        name : string
            Tilt Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to TiltButtonWindow window.
            If None, then Qt owns, otherwise associated with parent PyQt instance.

        Notes
        -----
        This class records the selected button and passes the
        change value back to variable.
        '''
        super(TiltButtonWindow, self).__init__(name=name, parent=parent)

        # Set up signal, so that DISPLAY can react to external 
        # (or internal) changes in tilt (Core.Variable instances expected)
        # The change is sent through Vtilt
        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar
        if Vgrid is None:
            self.Vgrid = Variable(None)
        else:
            self.Vgrid = Vgrid
        self.Vtilt = Vtilt
        self.sharedVariables = {"Vradar": self.NewRadar,
                                "Vgrid": self.NewGrid,
                                "Vtilt": self.NewTilt}
        self.connectAllVariables()

        self.CreateTiltWidget()
        if Vradar is not None:
            self.SetTiltRadioButtonsRadar()
        if Vgrid is not None:
            self.SetTiltRadioButtonsGrid()
        self.show()
           
    ########################
    # Button methods #
    ########################
        
    def TiltSelectCmd(self, ntilt):
        '''Captures a selection and update tilt variable.'''
        self.Vtilt.change(ntilt)

    def CreateTiltWidget(self):
        '''Create a widget to store radio buttons to control tilt adjust.'''
        self.radioBox = QtGui.QGroupBox("Tilt Selection", parent=self)
        self.rBox_layout = QtGui.QVBoxLayout(self.radioBox)
        self.radioBox.setLayout(self.rBox_layout)
        self.setCentralWidget(self.radioBox)
                
    def SetTiltRadioButtonsRadar(self):
        '''Set a tilt selection using radio buttons.'''
        # Instantiate the buttons into a list for future use
        self.tiltbutton = []
        
        # Pull out the tilt indices and elevations for display
        elevs = self.Vradar.value.fixed_angle['data'][:]
        
        # Loop through and create each tilt button and connect a value when selected
        for ntilt in self.Vradar.value.sweep_number['data'][:]:
            btntxt = "%2.1f deg (Tilt %d)"%(elevs[ntilt], ntilt+1)
            button = QtGui.QRadioButton(btntxt, self.radioBox)
            self.tiltbutton.append(button)
            QtCore.QObject.connect(self.tiltbutton[ntilt], QtCore.SIGNAL("clicked()"), \
                         partial(self.TiltSelectCmd, ntilt))
            
            self.rBox_layout.addWidget(self.tiltbutton[ntilt])
        
        self.NewTilt(self.Vtilt, self.Vtilt.value, True)  # setChecked the current tilt

    def SetTiltRadioButtonsGrid(self):
        '''Set a tilt selection using radio buttons.'''
        # Instantiate the buttons into a list for future use
        self.tiltbutton = []
        
        # Pull out the tilt indices and elevations for display
        elevs = self.Vgrid.value.axes["z_disp"]["data"]
        
        # Loop through and create each tilt button and connect a value when selected
        for ntilt in range(len(elevs)):
            btntxt = "%2.1f m (Tilt %d)"%(elevs[ntilt], ntilt+1)
            button = QtGui.QRadioButton(btntxt, self.radioBox)
            self.tiltbutton.append(button)
            QtCore.QObject.connect(self.tiltbutton[ntilt], QtCore.SIGNAL("clicked()"), \
                         partial(self.TiltSelectCmd, ntilt))
            
            self.rBox_layout.addWidget(self.tiltbutton[ntilt])
        
        self.NewTilt(self.Vtilt, self.Vtilt.value, True)  # setChecked the current tilt

    def NewTilt(self, variable, value, strong):
        '''Slot for 'ValueChanged' signal of :py:class:`Vtilt <artview.core.core.Variable>`.

        This will:

        * Update radio check
        '''
        tilt = self.Vtilt.value
        if tilt >= 0 and tilt < len(self.tiltbutton):
            self.tiltbutton[tilt].setChecked(True)
    
    def NewRadar(self, variable, value, strong):
        '''Slot for 'ValueChanged' signal of :py:class:`Vradar <artview.core.core.Variable>`.

        This will:

        * Recreate radio itens
        '''
        # update tilt list
        self.CreateTiltWidget()
        self.SetTiltRadioButtonsRadar()

    def NewGrid(self, variable, value, strong):
        '''Slot for 'ValueChanged' signal of :py:class:`Vgrid <artview.core.core.Variable>`.

        This will:

        * Recreate radio itens
        '''
        # update tilt list
        self.CreateTiltWidget()
        self.SetTiltRadioButtonsGrid()
