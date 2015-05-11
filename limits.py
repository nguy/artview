"""
limits.py

Routines used for modifying limits via Display window.
"""
        
# Load the needed packages
from PyQt4 import QtGui, QtCore

def initialize_limits(field, airborne=False, rhi=False):
    '''Initialized limits to default program values'''
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
    XSIZE = PPI_XSIZE
    YSIZE = PPI_YSIZE
    XRNG = PPI_XRNG
    YRNG = PPI_YRNG
    if airborne:
        XSIZE = AIR_XSIZE
        YSIZE = AIR_YSIZE
        XRNG = AIR_XRNG
        YRNG = AIR_YRNG
    if rhi:
        XSIZE = RHI_XSIZE
        YSIZE = RHI_YSIZE
        XRNG = RHI_XRNG
        YRNG = RHI_YRNG

    # Check the field and apply the proper limits
    if field == 'reflectivity':
        vminmax = (Z_LIMS[0], Z_LIMS[1])
        CMAP = 'gist_ncar'
    elif field == 'DBZ':
        vminmax = (Z_LIMS[0], Z_LIMS[1])
        CMAP = 'gist_ncar'
    elif field == 'velocity':
        vminmax = (VR_LIMS[0], VR_LIMS[1])
        CMAP = 'RdBu_r'
    elif field == 'VEL':
        vminmax = (VR_LIMS[0], VR_LIMS[1])
        CMAP = 'RdBu_r'
    elif field == 'differential_reflectivity':
        vminmax = (ZDR_LIMS[0], ZDR_LIMS[1])
        CMAP = 'RdYlBu_r'
    elif field == 'cross_correlation_ratio':
        vminmax = (RHO_HV_LIMS[0], RHO_HV_LIMS[1])
        CMAP = 'cool'
    elif field == 'differential_phase':
        vminmax = (KDP_LIMS[0], KDP_LIMS[1])
        CMAP = 'YlOrBr'
    elif field == 'normalized_coherent_power':
        vminmax = (NCP_LIMS[0], NCP_LIMS[1])
        CMAP = 'jet'
    elif field == 'spectrum_width':
        vminmax = (SW_LIMS[0], SW_LIMS[1])
        CMAP = 'gist_ncar'
    elif field == 'specific_differential_phase':
        vminmax = (PHIDP_LIMS[0], PHIDP_LIMS[1]) 
        CMAP = 'RdBu_r'
    elif field == 'total_power':
        vminmax = (TP_LIMS[0], TP_LIMS[1])
        CMAP = 'jet'
    else:
        vminmax = (Z_LIMS[0], Z_LIMS[1])
        CMAP = 'gist_ncar'
    
       
    limit_strs = ('vmin', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax')
    limits = {}
        
    # Now pull the default values
    limits['vmin'] = vminmax[0]
    limits['vmax'] = vminmax[1]
    limits['xmin'] = XRNG[0]
    limits['xmax'] = XRNG[1]
    limits['ymin'] = YRNG[0]
    limits['ymax'] = YRNG[1]
    limits['xsize'] = XSIZE
    limits['ysize'] = YSIZE
        
    return limits, CMAP

###############################
# Limits Dialog Class Methods #
###############################

def limits_dialog(limits, name):
    '''function'''
    LimsDialog = QtGui.QDialog()
    LimsDialog.setObjectName("Limits Dialog")
    LimsDialog.setWindowModality(QtCore.Qt.WindowModal)
    LimsDialog.setWindowTitle(name+" Limits Entry")
        
    # Setup window layout
    gridLayout_2 = QtGui.QGridLayout(LimsDialog)
    gridLayout_2.setObjectName("gridLayout_2")
    gridLayout = QtGui.QGridLayout()
    gridLayout.setObjectName("gridLayout")
	
    # Set up the Labels for entry
    lab_dmin = QtGui.QLabel("Data Min")
    lab_dmax = QtGui.QLabel("Data Max")
    lab_xmin = QtGui.QLabel("X Min")
    lab_xmax = QtGui.QLabel("X Max")
    lab_ymin = QtGui.QLabel("Y Min")
    lab_ymax = QtGui.QLabel("Y Max")
	
    # Set up the Entry limits
    ent_dmin = QtGui.QLineEdit(LimsDialog)
    ent_dmax = QtGui.QLineEdit(LimsDialog)
    ent_xmin = QtGui.QLineEdit(LimsDialog)
    ent_xmax = QtGui.QLineEdit(LimsDialog)
    ent_ymin = QtGui.QLineEdit(LimsDialog)
    ent_ymax = QtGui.QLineEdit(LimsDialog)
        
    # Input the current values
    ent_dmin.setText(str(limits['vmin']))
    ent_dmax.setText(str(limits['vmax']))
    ent_xmin.setText(str(limits['xmin']))
    ent_xmax.setText(str(limits['xmax']))
    ent_ymin.setText(str(limits['ymin']))
    ent_ymax.setText(str(limits['ymax']))
	
    # Add to the layout
    gridLayout.addWidget(lab_dmin, 0, 0, 1, 1)
    gridLayout.addWidget(ent_dmin, 0, 1, 1, 1)
    gridLayout.addWidget(lab_dmax, 1, 0, 1, 1)
    gridLayout.addWidget(ent_dmax, 1, 1, 1, 1)
    gridLayout.addWidget(lab_xmin, 2, 0, 1, 1)
    gridLayout.addWidget(ent_xmin, 2, 1, 1, 1)
    gridLayout.addWidget(lab_xmax, 3, 0, 1, 1)
    gridLayout.addWidget(ent_xmax, 3, 1, 1, 1)
    gridLayout.addWidget(lab_ymin, 4, 0, 1, 1)
    gridLayout.addWidget(ent_ymin, 4, 1, 1, 1)
    gridLayout.addWidget(lab_ymax, 5, 0, 1, 1)
    gridLayout.addWidget(ent_ymax, 5, 1, 1, 1)
	
    gridLayout_2.addLayout(gridLayout, 0, 0, 1, 1)
    buttonBox = QtGui.QDialogButtonBox(LimsDialog)
    buttonBox.setOrientation(QtCore.Qt.Horizontal)
    buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
    buttonBox.setObjectName("buttonBox")
    gridLayout_2.addWidget(buttonBox, 1, 0, 1, 1)
        
    LimsDialog.setLayout(gridLayout_2)
#    LimsDialog.setCentralWidget(LimsDialog)

    # Connect the signals from OK and Cancel buttons
    buttonBox.accepted.connect(LimsDialog.accept)
    buttonBox.rejected.connect(LimsDialog.reject)
    retval = LimsDialog.exec_()
    
    if retval == 1:
        limits['vmin'] = float(ent_dmin.text())
        limits['vmax'] = float(ent_dmax.text())
        limits['xmin'] = float(ent_xmin.text())
        limits['xmax'] = float(ent_xmax.text())
        limits['ymin'] = float(ent_ymin.text())
        limits['ymax'] = float(ent_ymax.text())

    return limits
    
######################################
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
             
    def NewLimits(self, variable, value, strong):
        '''Retrieve new limits input'''
        self.buttonBox.accepted.connect(self._pass_lims)
    
    def NewRadar(self, variable, value, strong):
        # update Limits
        self.setupUi()
        self.LimsDialog.show()
