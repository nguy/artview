"""
limits.py

Routines used for modifying limits via Display window.
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
import pyart

def _default_limits(field, scan_type):
    '''
    Initialize limits to default program values.

    Parameters::
    ----------
    field - string
        Field name to use for initialization (e.g. 'reflectivity').

    [Optional]
    scan_type - "ppi", "rhi", "airborne" or None
        Scan_type of the plot

    Notes::
    -----
    Returns a dictionary of display limits and colormap instance
    '''
    # Limits for variables
    Z_LIMS = (-10., 65.)
    VR_LIMS = (-30., 30.)
    ZDR_LIMS = (-5., 5.)
    RHO_HV_LIMS = (.8, 1.)
    KDP_LIMS = (-2., 5.)
    PHIDP_LIMS = (-180, 180)
    NCP_LIMS = (0., 1.)
    SW_LIMS = (-1., 10.)
    TP_LIMS = (-200., 100.)
    SNR_LIMS = (0., 65.)
    RR_LIMS = (0., 150.)#Rrait12

    # X, Y range and size for airborne file typesAIR_XRNG = (-150., 150.)
    AIR_XRNG = (-50., 50.)
    AIR_YRNG = (-10., 20.)
    AIR_XSIZE = 8
    AIR_YSIZE = 5

    # X, Y range and size for PPI file types
    PPI_XRNG = (-150., 150.)
    PPI_YRNG = (-150., 150.)

    # X, Y range and size for RHI file types
    RHI_XRNG = (0., 150.)
    RHI_YRNG = (0., 20.)

    # Set size of plot
    XRNG = PPI_XRNG
    YRNG = PPI_YRNG
    if scan_type == "airborne":
        XRNG = AIR_XRNG
        YRNG = AIR_YRNG
    if scan_type == "rhi":
        XRNG = RHI_XRNG
        YRNG = RHI_YRNG

    name = pyart.config.get_field_name

    # Check the field and apply the proper limits
    if field == name('reflectivity'):
        vminmax = (Z_LIMS[0], Z_LIMS[1])
#        CMAP = 'gist_ncar'
        CMAP = 'pyart_NWSRef'
    elif field == name('velocity'):
        vminmax = (VR_LIMS[0], VR_LIMS[1])
#        CMAP = 'RdBu_r'
        CMAP = 'pyart_NWSVel'
    elif field == name('differential_reflectivity'):
        vminmax = (ZDR_LIMS[0], ZDR_LIMS[1])
#        CMAP = 'RdYlBu_r'
        CMAP = 'pyart_BuDRd12'
    elif field == name('cross_correlation_ratio'):
        vminmax = (RHO_HV_LIMS[0], RHO_HV_LIMS[1])
#        CMAP = 'cool'
        CMAP = 'pyart_BrBu12'
    elif field == name('specific_differential_phase'):
        vminmax = (KDP_LIMS[0], KDP_LIMS[1])
#        CMAP = 'YlOrBr'
        CMAP = 'pyart_BrBu12'
    elif field == name('normalized_coherent_power'):
        vminmax = (NCP_LIMS[0], NCP_LIMS[1])
#        CMAP = 'jet'
        CMAP = 'pyart_Carbone17'
    elif field == name('spectrum_width'):
        vminmax = (SW_LIMS[0], SW_LIMS[1])
#        CMAP = 'gist_ncar'
        CMAP = 'pyart_Carbone17'
    elif field == name('differential_phase'):
        vminmax = (PHIDP_LIMS[0], PHIDP_LIMS[1])
#        CMAP = 'RdBu_r'
        CMAP = 'pyart_BlueBrown11'
    elif field == name('total_power'):
        vminmax = (TP_LIMS[0], TP_LIMS[1])
#        CMAP = 'jet'
        CMAP = 'pyart_StepSeq25'
    elif field == name('radar_echo_classification'):
        vminmax = (0, 12)
        CMAP = 'pyart_EWilson17'
    else:
        vminmax = (Z_LIMS[0], Z_LIMS[1])
#        CMAP = 'gist_ncar'
        CMAP = 'pyart_Carbone17'

    limit_strs = ('vmin', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax')
    limits = {}
    cmap = {}

    # Now pull the default values
    limits['xmin'] = XRNG[0]
    limits['xmax'] = XRNG[1]
    limits['ymin'] = YRNG[0]
    limits['ymax'] = YRNG[1]
    cmap['vmin'] = vminmax[0]
    cmap['vmax'] = vminmax[1]
    cmap['cmap'] = CMAP

    return limits, cmap

###############################
# Limits Dialog Class Methods #
###############################


def limits_dialog(limits, cmap, name):
    '''Function to instantiate a Display Limits Window.

    Parameters::
    ----------
    limits - dict
        Dictionary containing display limits.
    name - string
        Window name to add as prefix in window title .

    Notes::
    -----
    Returns a dictionary of display limits.
    '''
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
    ent_dmin.setText(str(cmap['vmin']))
    ent_dmax.setText(str(cmap['vmax']))
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
    buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel |
                                 QtGui.QDialogButtonBox.Ok)
    buttonBox.setObjectName("buttonBox")
    gridLayout_2.addWidget(buttonBox, 1, 0, 1, 1)

    LimsDialog.setLayout(gridLayout_2)
#    LimsDialog.setCentralWidget(LimsDialog)

    # Connect the signals from OK and Cancel buttons
    buttonBox.accepted.connect(LimsDialog.accept)
    buttonBox.rejected.connect(LimsDialog.reject)
    retval = LimsDialog.exec_()
    print retval
    if retval == 1:
        cmap['vmin'] = float(ent_dmin.text())
        cmap['vmax'] = float(ent_dmax.text())
        limits['xmin'] = float(ent_xmin.text())
        limits['xmax'] = float(ent_xmax.text())
        limits['ymin'] = float(ent_ymin.text())
        limits['ymax'] = float(ent_ymax.text())

    return limits, cmap, retval
