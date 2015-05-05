"""
limits.py - Classes for modifying plot limits via Display window
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore

class DisplayLimits(QtGui.QMainWindow):
    '''Class to initialize and change plot limits'''
    
    def __init__(self, Vfield, name="DisplayLimits", parent=None):
        '''Initialize the class to create the Tilt Selection interface'''
        super(DisplayLimits, self).__init__(parent)
        self.parent = parent
        self.name = name
        self.setWindowTitle(name)
        self.field = Vfield.value
        
        # Set up signal, so that DISPLAY can react to external 
        # (or internal) changes in field (Core.Variable instances expected)
        self.Vfield = Vfield
#        QtCore.QObject.connect(Vfield,QtCore.SIGNAL("ValueChanged"),self.NewField)

    def _initialize_limits(self, airborne=False, rhi=False):
        '''Initialized limits to default program values'''
        self.airborne = airborne
        self.rhi = rhi
        
        # Limits for variables
        Z_LIMS = (-10., 65.)
        VR_LIMS = (-30., 30.)
        ZDR_LIMS = (-5., 5.)
        RHO_HV_LIMS = (.8, 1.)
        KDP_LIMS = (0., 5.)
        PHIDP_LIMS =(0., 1.)
        NCP_LIMS = (0., 1.)
        SW_LIMS = (-1., 10.)
        TP_LIMS = (-200., 100.)
        
        # X, Y range and size for airborne file typesAIR_XRNG = (-150., 150.)
        AIR_YRNG = (-10., 20.)
        AIR_XSIZE = 8
        AIR_YSIZE = 5
        
        # X, Y range and size for PPI file types
        PPI_XRNG = (-150., 150.)
        PPI_YRNG = (-150., 150.)
        PPI_XSIZE = 8
        PPI_YSIZE = 8
        
        # X, Y range and size for RHI file types
        RHI_XRNG = (0., 150.)
        RHI_YRNG = (0., 20.)
        RHI_XSIZE = 8
        RHI_YSIZE = 5
        
        # Set size of plot
        self.XSIZE = PPI_XSIZE
        self.YSIZE = PPI_YSIZE
        self.XRNG = PPI_XRNG
        self.YRNG = PPI_YRNG
        if self.airborne:
            self.XSIZE = AIR_XSIZE
            self.YSIZE = AIR_YSIZE
            self.XRNG = AIR_XRNG
            self.YRNG = AIR_YRNG
        if self.rhi:
            self.XSIZE = RHI_XSIZE
            self.YSIZE = RHI_YSIZE
            self.XRNG = RHI_XRNG
            self.YRNG = RHI_YRNG

        # Check the field and apply the proper limits
        if self.field == 'reflectivity':
            self.vminmax = (Z_LIMS[0], Z_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif self.field == 'DBZ':
            self.vminmax = (Z_LIMS[0], Z_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif self.field == 'velocity':
            self.vminmax = (VR_LIMS[0], VR_LIMS[1])
            self.CMAP = 'RdBu_r'
        elif self.field == 'VEL':
            self.vminmax = (VR_LIMS[0], VR_LIMS[1])
            self.CMAP = 'RdBu_r'
        elif self.field == 'differential_reflectivity':
            self.vminmax = (ZDR_LIMS[0], ZDR_LIMS[1])
            self.CMAP = 'RdYlBu_r'
        elif self.field == 'cross_correlation_ratio':
            self.vminmax = (RHO_HV_LIMS[0], RHO_HV_LIMS[1])
            self.CMAP = 'cool'
        elif self.field == 'differential_phase':
            self.vminmax = (KDP_LIMS[0], KDP_LIMS[1])
            self.CMAP = 'YlOrBr'
        elif self.field == 'normalized_coherent_power':
            self.vminmax = (NCP_LIMS[0], NCP_LIMS[1])
            self.CMAP = 'jet'
        elif self.field == 'spectrum_width':
            self.vminmax = (SW_LIMS[0], SW_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif self.field == 'specific_differential_phase':
            self.vminmax = (PHIDP_LIMS[0], PHIDP_LIMS[1]) 
            self.CMAP = 'RdBu_r'
        elif self.field == 'total_power':
            self.vminmax = (TP_LIMS[0], TP_LIMS[1])
            self.CMAP = 'jet'
           
        limit_strs = ('vmin', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax')
        self.limits = {}
        
        # Now pull the default values
        self.limits['vmin'] = self.vminmax[0]
        self.limits['vmax'] = self.vminmax[1]
        self.limits['xmin'] = self.XRNG[0]
        self.limits['xmax'] = self.XRNG[1]
        self.limits['ymin'] = self.YRNG[0]
        self.limits['ymax'] = self.YRNG[1]
        self.limits['xsize'] = self.XSIZE
        self.limits['ysize'] = self.YSIZE
        
        return self.limits, self.CMAP

###############################
# Limits Dialog Class Methods #
###############################
class Ui_LimsDialog(QtGui.QMainWindow):
    '''
    Limits Dialog Class
    Popup window to set various limits
    '''
    def __init__(self, Vradar, Vlims, limits, name="LimsDialog", parent=None):
        super(Ui_LimsDialog, self).__init__(parent)
        self.parent = parent
        self.name = name
        self.setWindowTitle(name)
        self.LimsDialog = QtGui.QDialog(parent=self)
        self.mainLimits = limits
        self.Vradar = Vradar
        
        # Set up an entry variable to pass
        self.limits = {}
        self.limits['vmin'] = self.mainLimits['vmin']
        self.limits['vmax'] = self.mainLimits['vmax']
        self.limits['xmin'] = self.mainLimits['xmin']
        self.limits['xmax'] = self.mainLimits['xmax']
        self.limits['ymin'] = self.mainLimits['ymin']
        self.limits['ymax'] = self.mainLimits['ymax']
        
        # Set up signal, so that DISPLAY can react to external 
        # (or internal) changes in limits (Core.Variable instances expected)
        self.Vlims = Vlims
        QtCore.QObject.connect(Vlims, QtCore.SIGNAL("ValueChanged"), self.NewLimits)
        QtCore.QObject.connect(Vradar, QtCore.SIGNAL("ValueChanged"), self.NewRadar)
        
        self.setupUi()
        self.LimsDialog.show()
#        self.show()
           
    def setupUi(self):
        # Set aspects of Dialog Window
        self.LimsDialog.setObjectName("Limits Dialog")
        self.LimsDialog.setWindowModality(QtCore.Qt.WindowModal)
        self.LimsDialog.setWindowTitle(self.name+" Limits Entry")
        
        # Setup window layout
        self.gridLayout_2 = QtGui.QGridLayout(self.LimsDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
	
        # Set up the Labels for entry
        self.lab_dmin = QtGui.QLabel("Data Min")
        self.lab_dmax = QtGui.QLabel("Data Max")
        self.lab_xmin = QtGui.QLabel("X Min")
        self.lab_xmax = QtGui.QLabel("X Max")
        self.lab_ymin = QtGui.QLabel("Y Min")
        self.lab_ymax = QtGui.QLabel("Y Max")
	
        # Set up the Entry limits
        self.ent_dmin = QtGui.QLineEdit(self.LimsDialog)
        self.ent_dmax = QtGui.QLineEdit(self.LimsDialog)
        self.ent_xmin = QtGui.QLineEdit(self.LimsDialog)
        self.ent_xmax = QtGui.QLineEdit(self.LimsDialog)
        self.ent_ymin = QtGui.QLineEdit(self.LimsDialog)
        self.ent_ymax = QtGui.QLineEdit(self.LimsDialog)
        
        # Input the current values
        self.ent_dmin.setText(str(self.mainLimits['vmin']))
        self.ent_dmax.setText(str(self.mainLimits['vmax']))
        self.ent_xmin.setText(str(self.mainLimits['xmin']))
        self.ent_xmax.setText(str(self.mainLimits['xmax']))
        self.ent_ymin.setText(str(self.mainLimits['ymin']))
        self.ent_ymax.setText(str(self.mainLimits['ymax']))
	
        # Add to the layout
        self.gridLayout.addWidget(self.lab_dmin, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_dmin, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_dmax, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_dmax, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_xmin, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_xmin, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_xmax, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_xmax, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_ymin, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_ymin, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.lab_ymax, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.ent_ymax, 5, 1, 1, 1)
	
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.LimsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)
        
        self.LimsDialog.setLayout(self.gridLayout_2)
        self.setCentralWidget(self.LimsDialog)

        # Connect the signals from OK and Cancel buttons
        self.buttonBox.accepted.connect(self._pass_lims)
        self.buttonBox.rejected.connect(self.LimsDialog.reject)
	
    def _pass_lims(self):
        self.limits['vmin'] = float(self.ent_dmin.text())
        self.limits['vmax'] = float(self.ent_dmax.text())
        self.limits['xmin'] = float(self.ent_xmin.text())
        self.limits['xmax'] = float(self.ent_xmax.text())
        self.limits['ymin'] = float(self.ent_ymin.text())
        self.limits['ymax'] = float(self.ent_ymax.text())
        
        self.LimsDialog.accept()
        self.Vlims.change(self.limits)
             
    def NewLimits(self, variable, value):
        '''Retrieve new limits input'''
        self.buttonBox.accepted.connect(self._pass_lims)
    
    def NewRadar(self, variable, value):
        # update Limits
        self.setupUi()
        self.LimsDialog.show()