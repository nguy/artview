"""
gatefilter.py
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial
import os
import numpy as np
import pyart
import time

from .. import core
from ..components import RadarDisplay
common = core.common


class GateFilter(core.Component):
    '''
    Interface for executing :py:func:`pyart.correct.GateFilter`.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgatefilter = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("GateFilter").startDisplay()
#        kwargs, independent = _GateFilterStart().startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, Vradar=None, Vgatefilter=None,
                 name="GateFilter", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        Vradar : :py:class:`~artview.core.core.Variable` instance
            Radar signal variable.
            A value of None initializes an empty Variable.
        Vgatefilter : :py:class:`~artview.core.core.Variable` instance
            GateFilter signal variable.
            A value of None initializes an empty Variable.
        name : string
            GateFilter instance window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated w/ parent PyQt instance
        '''
        super(GateFilter, self).__init__(name=name, parent=parent)
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

        self.sharedVariables = {"Vradar": None,
                                "Vgatefilter": None}
        self.connectAllVariables()
        self.field = None

        self.operators = {"=": "exclude_equal",
                          "!=": "exclude_not_equal",
                          "<": "exclude_below",
                          "<=": "exclude_below",
                          ">": "exclude_above",
                          ">=": "exclude_above",
                          "inside": "exclude_inside",
                          "outside": "exclude_outside",
                          }

        self.generalLayout = QtGui.QVBoxLayout()
        # Set the Variable layout
        self.generalLayout.addWidget(self.createVarUI())
        self.generalLayout.addWidget(self.createFilterBox())
        self.generalLayout.addWidget(self.createButtonUI())

        self.layout.addLayout(self.generalLayout, 0, 0, 1, 2)

        self.AddCorrectedFields()

        self.newRadar(None, None, True)
        self.newGateFilter(None, None, True)

        self.show()

    ######################
    ##  Layout Methods  ##
    ######################

    def createVarUI(self):
        '''Mount the Variable layout.'''
        groupBox = QtGui.QGroupBox("Variable Input")
        gBox_layout = QtGui.QGridLayout()

#        self.radarButton = QtGui.QPushButton("Find Variable")
#        self.radarButton.clicked.connect(self.chooseRadar)
#        gBox_layout.addWidget(QtGui.QLabel("Radar"), 0, 0, 1, 1)
#        gBox_layout.addWidget(self.radarButton, 0, 1, 1 ,1)

        self.radarCombo = QtGui.QComboBox()
        gBox_layout.addWidget(QtGui.QLabel("Select Radar Variable"), 0, 0)
        gBox_layout.addWidget(self.radarCombo, 0, 1, 1, 1)

        self.radarvars = []
        self.components = core.componentsList
        for component in self.components:
            for var in component.sharedVariables.keys():
                if var == "Vradar":
                    self.radarCombo.addItem(component.name +' ' + var)
                    self.radarvars.append(component.sharedVariables[var])
        self.radarCombo.setCurrentIndex(0)

        self.chooseRadar()
        groupBox.setLayout(gBox_layout)

        return groupBox

    def createButtonUI(self):
        '''Mount the Action layout.'''
        groupBox = QtGui.QGroupBox("Select Action")
        gBox_layout = QtGui.QGridLayout()

        self.helpButton = QtGui.QPushButton("Help")
        self.helpButton.clicked.connect(self.displayHelp)
        gBox_layout.addWidget(self.helpButton, 0, 0, 1, 1)

        self.scriptButton = QtGui.QPushButton("Show Script")
        self.scriptButton.clicked.connect(self.showScript)
        self.scriptButton.setToolTip('Display relevant python script')
        gBox_layout.addWidget(self.scriptButton, 0, 1, 1, 1)

        self.scriptButton = QtGui.QPushButton("Save File")
        self.scriptButton.clicked.connect(self.saveRadar)
        self.scriptButton.setToolTip('Save cfRadial data file')
        gBox_layout.addWidget(self.scriptButton, 0, 2, 1, 1)

        self.filterButton = QtGui.QPushButton("Filter")
        self.filterButton.clicked.connect(self.apply_filters)
        self.filterButton.setToolTip('Execute pyart.correct.GateFilter')
        gBox_layout.addWidget(self.filterButton, 0, 3, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def createFilterBox(self):
        '''Mount options layout.'''
        # Create lists for each column
        chkactive =[]
        fldlab = []
        operator = []
        loval = []
        hival =[]
        chkapply = []

        groupBox = QtGui.QGroupBox("Filter Design - Exclude via the following statements")
		#groupBox.setFlat(True)
        gBox_layout = QtGui.QGridLayout()

        gBox_layout.addWidget(QtGui.QLabel("Activate\nFilter"), 0, 0, 1, 1)
        gBox_layout.addWidget(QtGui.QLabel("Variable"), 0, 1, 1, 1)
        gBox_layout.addWidget(QtGui.QLabel("Operation"), 0, 2, 1, 1)
        gBox_layout.addWidget(QtGui.QLabel("Value 1"), 0, 3, 1, 1)
        gBox_layout.addWidget(QtGui.QLabel("Value 2"), 0, 4, 1, 1)
        gBox_layout.addWidget(QtGui.QLabel("Filter\nField"), 0, 5, 1, 1)

        self.fieldfilter = {}

        for nn, field in enumerate(self.Vradar.value.fields.keys()):
            chkactive.append(QtGui.QCheckBox())
            chkactive[nn].setChecked(False)
            fldlab.append(QtGui.QLabel(field))
            loval.append(QtGui.QLineEdit(""))
            hival.append(QtGui.QLineEdit(""))
            chkapply.append(QtGui.QCheckBox())
            operator.append(self.set_operator_menu())

            gBox_layout.addWidget(chkactive[nn], nn+1, 0, 1, 1)
            gBox_layout.addWidget(fldlab[nn], nn+1, 1, 1, 1)
            gBox_layout.addWidget(operator[nn], nn+1, 2, 1, 1)
            gBox_layout.addWidget(loval[nn], nn+1, 3, 1, 1)
            gBox_layout.addWidget(hival[nn], nn+1, 4, 1, 1)
            gBox_layout.addWidget(chkapply[nn], nn+1, 5, 1, 1)

        groupBox.setLayout(gBox_layout)

        self.fieldfilter["check_active"] = chkactive
        self.fieldfilter["field"] = fldlab
        self.fieldfilter["operator"] = operator
        self.fieldfilter["low_value"] = loval
        self.fieldfilter["high_value"] = hival
        self.fieldfilter["check_apply"] = chkapply

        return groupBox

    def AddCorrectedFields(self):
        '''Launch a display window to show the filter application.'''
        # Add fields for each variable for filters
        for dupfield in self.Vradar.value.fields.keys():
            data = self.Vradar.value.fields[dupfield]['data'][:]
            self.Vradar.value.add_field_like(dupfield, "corr_" + dupfield,
                                         data, replace_existing=False)

    #########################
    ##  Selection Methods  ##
    #########################

    def chooseRadar(self):
        '''Get Radar with :py:class:`~artview.core.VariableChoose`.'''
        selection = self.radarCombo.currentIndex()
        variable = str(self.radarCombo.currentText()).split()[1]
        component = str(self.radarCombo.currentText()).split()[0]
        Vradar = getattr(self.components[selection], str(variable))
        
        self.Vradar = Vradar
    
    def newRadar(self, variable, value, strong):
        '''respond to change in radar.'''
        if self.Vradar.value is None:
            return

    def newGateFilter(self, variable, value, strong):
        '''respond to change in radar.'''
        if self.Vgatefilter.value is None:
            return

    def displayHelp(self):
        '''Display Py-Art's docstring for help.'''
        text = "**Using this window**\n"
        text += "Choose a filter:\n"
        text += "  1. Select an operation and value(s) to exclude.\n"
        text += "  2. Check the 'Activate Filter' box to apply the filter.\n"
        text += "  3. Check the 'Filter this Field' box to apply filter\n"
        text += "     to this variable."
        text += "  4. Click the 'Filter' button.\n\n"
        text += "Change Radar variables:\n"
        text += "  Click the 'Find Variable', select variable.\n\n"
        text += "Show Python script for batching:\n"
        text += "  Click the 'Show Script' button.\n\n"
        text += "The following information is from the PyArt documentation.\n\n"
        text += "**GateFilter**\n"
        text += pyart.correct.GateFilter.__doc__
        text += "\n\n"
        text += "**GateFilter.exclude_below**\n"
        text += pyart.correct.GateFilter.exclude_below.__doc__
        common.ShowLongText(text)

    def set_operator_menu(self):
        '''Set the field operators choice.'''
        opBox = QtGui.QComboBox()
        opBox.setFocusPolicy(QtCore.Qt.NoFocus)
        opBox.setToolTip("Select filter operator.\n")
        opBox_layout = QtGui.QVBoxLayout()
        for op in self.operators.keys():
            opBox.addItem(op)
        opBox.setLayout(opBox_layout)

        return opBox

    def showScript(self):
        '''Create the output script to reproduce filtering results.'''
        text = "<b>PyArt Script Commands</b><br><br>"
        text += "<i>Warning</i>: This generated script is not complete!<br>"
        text += "The commands below are intended to be integrated for use in "
        text += "batch scripting to achieve the same results seen in the Display.<br><br>"
        text += "Just copy and paste the below commands into your script.<br><br>"
        text += "<i>Commands</i>:<br><br>"
        text += "gatefilter = pyart.correct.GateFilter(radar, exclude_based=True)<br>"

        for cmd in self.filterscript:
            text += cmd + "\n"

        common.ShowLongText(text)

    def saveRadar(self):
        '''Open a dialog box to save radar file.'''

        dirIn, fname = os.path.split(self.Vradar.value.filename)
        filename = QtGui.QFileDialog.getSaveFileName(
                self, 'Save Radar File', dirIn)
        filename = str(filename)
        if filename == '' or self.Vradar.value is None:
            return
        else:
            self.plot.statusbar.showMessage("Saved %s"%(filename))
            pyart.io.write_cfradial(filename, self.Vradar.value)
        
    ######################
    ##  Filter Methods  ##
    ######################

    def apply_filters(self):
        '''Mount Options and execute
        :py:func:`~pyart.correct.GateFilter`.
        The resulting fields are added to Vradar.
        Vradar is updated, strong or weak depending on overwriting old fields.
        '''
        # Test radar
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None, can not perform filtering.")
            return
        print(np.sum(self.Vradar.value.fields['reflectivity']['data'].mask))
        self.Vgatefilter.value = pyart.correct.GateFilter(self.Vradar.value, exclude_based=True)

        # Clear flags from previous filter application or instantiate if first
        args = {}
        self.filterscript = []

        # Create a list of possible filtering actions
        val2Cmds = ["inside", "outside"]
        valinc = [">=", "<="]

        # Initial point for timing
        t0 = time.time()

        # Get a list of field to apply the filters
        filt_flds = []
        for index, chk in enumerate(self.fieldfilter["check_apply"]):
            if chk.isChecked():
                field = "corr_" + str(self.fieldfilter["field"][index].text())
                filt_flds.append(field)

        pyarterr = "Py-ART fails with following error\n\n"
        # Find out which filters to apply
        NoChecks = True
        for index, chk in enumerate(self.fieldfilter["check_active"]):
            if chk.isChecked():
                NoChecks = False
                field = str(self.fieldfilter["field"][index].text())
                operator = str(self.fieldfilter["operator"][index].currentText())
                val1 = self.fieldfilter["low_value"][index].text()
                val2 = self.fieldfilter["high_value"][index].text()

                print("%s checked, %s, v1 = %s, v2 = %s"%(
                field, self.operators[operator], val1, val2))

                # Create the command to be issued for filtering
                # Try that command and return error if fail

                # If the operator takes val1 and val2
                if operator in val2Cmds:
                    filtercmd = "gatefilter.%s(%s, %s, %s)"%(
                      self.operators[operator], field, val1, val2)
                    for filt in filt_flds:
                        if operator == "inside":
                        
                            try:
                                self.Vgatefilter.value.exclude_inside(
                                 filt, float(val1), float(val2))
                            except:
                                import traceback
                                error = traceback.format_exc()
                                common.ShowLongText(pyarterr +
                                        error)
                        else:
                            try:
                                self.Vgatefilter.value.exclude_outside(
                                 filt, float(val1), float(val2))
                            except:
                                import traceback
                                error = traceback.format_exc()
                                common.ShowLongText(pyarterr +
                                        error)
                # If the operators are inclusive of val1
                elif operator in valinc:
                    filtercmd = "gatefilter.%s(%s, %s, inclusive=True)"%(
                      self.operators[operator], field, val1)
                    for filt in filt_flds:
                        if operator == "<":
                            try:
                                self.Vgatefilter.value.exclude_below(
                                  filt, float(val1), inclusive=True)
                            except:
                                import traceback
                                error = traceback.format_exc()
                                common.ShowLongText(pyarterr +
                                        error)
                        elif operator == ">":
                            try:
                                self.Vgatefilter.value.exclude_above(
                                  filt, float(val1), inclusive=True)
                            except:
                                import traceback
                                error = traceback.format_exc()
                                common.ShowLongText(pyarterr +
                                        error)
                # If the operators are exclusive of val1
                else:
                    filtercmd = "gatefilter.%s(%s, %s, inclusive=False)"%(
                      self.operators[operator], field, val1)
                    for filt in filt_flds:
                        if operator == "=":
                            try:
                                self.Vgatefilter.value.exclude_equal(
                                  filt, float(val1))
                            except:
                                import traceback
                                error = traceback.format_exc()
                                common.ShowLongText(pyarterr +
                                        error)
                        elif operator == "!=":
                            try:
                                self.Vgatefilter.value.exclude_not_equal(
                                  filt, float(val1))
                            except:
                                import traceback
                                error = traceback.format_exc()
                                common.ShowLongText(pyarterr +
                                        error)
                        elif operator == "<":
                            try:
                                self.Vgatefilter.value.exclude_below(
                                  filt, float(val1), inclusive=False)
                            except:
                                import traceback
                                error = traceback.format_exc()
                                common.ShowLongText(pyarterr +
                                        error)
                        elif operator == ">":
                            try:
                                self.Vgatefilter.value.exclude_above(
                                  filt, float(val1), inclusive=False)
                            except:
                                import traceback
                                error = traceback.format_exc()
                                common.ShowLongText(pyarterr +
                                        error)

                self.filterscript.append(filtercmd)

        # If no filters were applied issue warning  
        if NoChecks:
            common.ShowWarning("Please Activate Filter(s)")
            return
        # execute
        print("Applying filters ..")

        t1 = time.time()
        print(("Filtering took %fs" % (t1-t0)))

        # verify field overwriting
#         if args['spec_at_field'] is None:
#             spec_at_field_name = "specific_attenuation"
#         else:
#             spec_at_field_name = args['spec_at_field']
# 
#         if args['corr_refl_field'] is None:
#             corr_refl_field_name = "corrected_reflectivity"
#         else:
#             corr_refl_field_name = args['corr_refl_field']

        strong_update = True  # insertion is weak, overwrite strong
#         if spec_at_field_name in self.Vradar.value.fields.keys():
#             resp = common.ShowQuestion(
#                 "Field %s already exists! Do you want to over write it?" %
#                 spec_at_field_name)
#             if resp != QtGui.QMessageBox.Ok:
#                 return
#             else:
#                 strong_update = True
# 
#         if corr_refl_field_name in self.Vradar.value.fields.keys():
#             resp = common.ShowQuestion(
#                 "Field %s already exists! Do you want to over write it?" %
#                 corr_refl_field_name)
#             if resp != QtGui.QMessageBox.Ok:
#                 return
#             else:
#                 strong_update = True
        print(np.sum(self.Vgatefilter.value.gate_excluded))
        # add fields and update
        self.Vgatefilter.change(self.Vgatefilter.value, strong_update)
        self.Vradar.change(self.Vradar.value, strong_update)
        print(np.sum(self.Vradar.value.fields['corr_reflectivity']['data'].mask))
#        self.plot._update_plot()

    def _clearLayout(self, layout):
        '''recursively remove items from layout.'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clearLayout(item.layout())

_plugins = [GateFilter]

# class _GateFilterStart(QtGui.QDialog):
#     '''
#     Dialog Class for graphical start of GateFilter, to be used in guiStart.
#     '''
# 
#     def __init__(self):
#         '''Initialize the class to create the interface.'''
#         super(_GateFilterStart, self).__init__()
#         self.result = {"Vradar": None}
#         self.layout = QtGui.QGridLayout(self)
#         # set window as modal
#         self.setWindowModality(QtCore.Qt.ApplicationModal)
# 
#         self.setupUi()
# 
#     def setupUi(self):
# 
# #        self.varCombo = QtGui.QComboBox()
# #        self.layout.addWidget(QtGui.QLabel("Select Variable"), 0, 0)
# #        self.layout.addWidget(self.varCombo, 0, 1, 1, 3)
# #        self.fillCombo()
# 
#         self.name = QtGui.QLineEdit("GateFilter")
#         self.layout.addWidget(QtGui.QLabel("Plugin Name"), 1, 0)
#         self.layout.addWidget(self.name, 1, 1, 1, 3)
# 
#         self.independent = QtGui.QCheckBox("Independent Window")
#         self.independent.setChecked(True)
#         self.layout.addWidget(self.independent, 2, 1, 1, 1)
# 
#         self.closeButton = QtGui.QPushButton("Launch Plugin")
#         self.closeButton.clicked.connect(self.closeDialog)
#         self.layout.addWidget(self.closeButton, 3, 0, 1, 5)
# 
#     def fillCombo(self):
#         self.vars = []
# 
#         self.components = core.componentsList
#         for component in self.components:
#             if self._isDisplay(component):
#                 for var in component.sharedVariables.keys():
#                     self.varCombo.addItem(component.name +' ' + var)
#                     self.vars.append(component.sharedVariables[var])
#         self.varCombo.setCurrentIndex(0)
# 
#     def _isDisplay(self, comp):
#         ''' Test if a component is a valid display to be used. '''
#         if (hasattr(comp, 'getPlotAxis') and
#             hasattr(comp, 'getStatusBar') and
#             hasattr(comp, 'getField') and
#             hasattr(comp, 'getPathInteriorValues')
#             ):
#             return True
#         else:
#             return False
# 
#     def closeDialog(self):
#         self.done(QtGui.QDialog.Accepted)
# 
#     def startDisplay(self):
#         self.exec_()
# 
#         self.result['name'] = str(self.name.text())
# 
#         selection = self.varCombo.currentIndex()
#         variable = str(self.varCombo.currentText()).split()[1]
#         component = str(self.varCombo.currentText()).split()[0]
#         self.result["Vradar"] = getattr(self.components[selection], str(variable))
# 
#         print((self.result['name']))
# 
#         return self.result, self.independent.isChecked()