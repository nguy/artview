"""
gatefilter.py
"""

# Load the needed packages
from functools import partial
import os
import numpy as np
import pyart
import time

from ..core import Component, Variable, common, QtGui, QtCore, componentsList
from ..components import RadarDisplay


class GateFilter(Component):
    '''
    Interface for executing :py:class:`pyart.filters.GateFilter`.
    '''

    Vradar = None  #: see :ref:`shared_variable`
    Vgatefilter = None  #: see :ref:`shared_variable`

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("GateFilter").startDisplay()
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

        # Set up signal, so that DISPLAY can react to
        # changes in radar or gatefilter shared variables
        if Vradar is None:
            self.Vradar = Variable(None)
        else:
            self.Vradar = Vradar

        if Vgatefilter is None:
            self.Vgatefilter = Variable(None)
        else:
            self.Vgatefilter = Vgatefilter

        self.sharedVariables = {"Vradar": None,
                                "Vgatefilter": None, }
        # Connect the components
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

        self.show()

    ######################
    #   Layout Methods   #
    ######################

    def createVarUI(self):
        '''
        Mount the Variable layout.
        User may select another Display
        '''
        groupBox = QtGui.QGroupBox("Variable Input")
        gBox_layout = QtGui.QGridLayout()

        self.dispCombo = QtGui.QComboBox()
        gBox_layout.addWidget(QtGui.QLabel("Select Display Link"), 0, 0)
        gBox_layout.addWidget(self.dispCombo, 0, 1, 1, 1)

        self.DispChoiceList = []
        self.components = componentsList
        for component in self.components:
            if "Vradar" in component.sharedVariables.keys():
                if "Vgatefilter" in component.sharedVariables.keys():
                    self.dispCombo.addItem(component.name)
                    self.DispChoiceList.append(component)
        self.dispCombo.setCurrentIndex(0)

        self.chooseDisplay()
        groupBox.setLayout(gBox_layout)

        return groupBox

    def createButtonUI(self):
        '''Mount the Action layout.'''
        groupBox = QtGui.QGroupBox("Select Action")
        gBox_layout = QtGui.QGridLayout()

        self.helpButton = QtGui.QPushButton("Help")
        self.helpButton.clicked.connect(self._displayHelp)
        gBox_layout.addWidget(self.helpButton, 0, 0, 1, 1)

        self.scriptButton = QtGui.QPushButton("Show Script")
        self.scriptButton.clicked.connect(self.showScript)
        self.scriptButton.setToolTip('Display relevant python script')
        gBox_layout.addWidget(self.scriptButton, 0, 1, 1, 1)

        self.saveButton = QtGui.QPushButton("Save File")
        self.saveButton.clicked.connect(self.saveRadar)
        self.saveButton.setToolTip('Save cfRadial data file')
        gBox_layout.addWidget(self.saveButton, 0, 2, 1, 1)

        self.restoreButton = QtGui.QPushButton("Restore to Original")
        self.restoreButton.clicked.connect(self.restoreRadar)
        self.restoreButton.setToolTip('Remove applied filters')
        gBox_layout.addWidget(self.restoreButton, 0, 3, 1, 1)

        self.filterButton = QtGui.QPushButton("Filter")
        self.filterButton.clicked.connect(self.apply_filters)
        self.filterButton.setToolTip('Make Filter')
        gBox_layout.addWidget(self.filterButton, 0, 4, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def createFilterBox(self):
        '''Mount options layout.'''
        # Create lists for each column
        chkactive = []
        fldlab = []
        operator = []
        loval = []
        hival = []

        groupBox = QtGui.QGroupBox("Filter Design - Exclude gates "
                                   "via the following statements")
        # groupBox.setFlat(True)
        gBox_layout = QtGui.QGridLayout()

        gBox_layout.addWidget(QtGui.QLabel("Activate\nFilter"), 0, 0, 1, 1)
        gBox_layout.addWidget(QtGui.QLabel("Variable"), 0, 1, 1, 1)
        gBox_layout.addWidget(QtGui.QLabel("Operation"), 0, 2, 1, 1)
        gBox_layout.addWidget(QtGui.QLabel("Value 1"), 0, 3, 1, 1)
        gBox_layout.addWidget(QtGui.QLabel("Value 2\nFor outside/inside"),
                              0, 4, 1, 1)

        groupBox.setLayout(gBox_layout)

        self.fieldfilter = {}

        if self.Vradar.value is not None:
            for nn, field in enumerate(self.Vradar.value.fields.keys()):
                chkactive.append(QtGui.QCheckBox())
                chkactive[nn].setChecked(False)
                fldlab.append(QtGui.QLabel(field))
                loval.append(QtGui.QLineEdit(""))
                hival.append(QtGui.QLineEdit(""))
                operator.append(self.set_operator_menu())

                gBox_layout.addWidget(chkactive[nn], nn+1, 0, 1, 1)
                gBox_layout.addWidget(fldlab[nn], nn+1, 1, 1, 1)
                gBox_layout.addWidget(operator[nn], nn+1, 2, 1, 1)
                gBox_layout.addWidget(loval[nn], nn+1, 3, 1, 1)
                gBox_layout.addWidget(hival[nn], nn+1, 4, 1, 1)

            self.fieldfilter["check_active"] = chkactive
            self.fieldfilter["field"] = fldlab
            self.fieldfilter["operator"] = operator
            self.fieldfilter["low_value"] = loval
            self.fieldfilter["high_value"] = hival

#         for index, chk in enumerate(self.fieldfilter["check_active"]):
#             if chk.isChecked():
#                 if (self.fieldfilter["operator"] == 'outside' or
#                    self.fieldfilter["operator"] == 'inside'):
#                     self.fieldfilter["high_value"].setText(' ')
#                     self.fieldfilter["high_value"].setReadOnly(True)

        return groupBox

    #########################
    #   Selection Methods   #
    #########################

    def chooseDisplay(self):
        '''Get Display.'''
        selection = self.dispCombo.currentIndex()
        Vradar = getattr(self.DispChoiceList[selection], str("Vradar"))
        Vgatefilter = getattr(self.DispChoiceList[selection],
                              str("Vgatefilter"))

        self.dispCombo.setCurrentIndex(selection)

        self.disconnectAllVariables()
        self.Vradar = Vradar
        self.Vgatefilter = Vgatefilter
        self.connectAllVariables()

    def _displayHelp(self):
        '''Display Py-Art's docstring for help.'''
        text = (
#             "**Using the GateFilter window**\n"
#             "Choose a filter:\n"
#             "  1. Select an operation and value(s) to exclude.\n"
#             "       Notes: 'outside' masks values less than 'Value 1' and "
#             "greater than 'Value 2.'\n"
#             "              'inside' masks values greater than 'Value 1' and "
#             "less than 'Value 2.'\n"
#             "              For other operations only 'Value 1 is used.\n"
#             "  2. Check the 'Activate Filter' box to apply the filter.\n"
#             "  3. Click the 'Filter' button.\n"
#             "  4. GateFilter needs to be activated in the Display to see the "
#             "results. It is turned on by default. To check see "
#             "'Display Options' dropdown menu on the Display of interest.\n\n"
#             "Change Radar variables:\n"
#             "  Click the 'Find Variable', select variable.\n\n"
#             "Show Python script for batching:\n"
#             "  Click the 'Show Script' button.\n\n"
#             "The following information is from the PyArt documentation.\n\n"
#             "WARNING: By saving the file, the mask associated with the data "
#             "values may be modfidied. The data itself does not change.\n\n"
#             "**GateFilter**\n" +
#             pyart.filters.GateFilter.__doc__ +
#             "\n\n"
#             "**GateFilter.exclude_below**\n" +
#             pyart.filters.GateFilter.exclude_below.__doc__)
            "<b>Using the GateFilter window</b><br><br>"
            "<i>Choose a filter:</i><br>"
            "  1. Select an operation and value(s) to exclude.<br>"
            "       Notes: 'outside' masks values less than 'Value 1' and "
            "greater than 'Value 2.'<br>"
            "              'inside' masks values greater than 'Value 1' and "
            "less than 'Value 2.'<br>"
            "              For other operations only 'Value 1 is used.<br>"
            "  2. Check the 'Activate Filter' box to apply the filter.<br>"
            "  3. Click the 'Filter' button.<br>"
            "  4. GateFilter needs to be activated in the Display to see the "
            "results. It is turned on by default. To check see "
            "'Display Options' dropdown menu on the Display of interest.<br>"
            "<br>"
            "<i>Change Radar variables:</i><br>"
            "  Click the 'Find Variable', select variable.<br><br>"
            "<i>Show Python script for batching:</i><br>"
            "  Click the 'Show Script' button.<br><br>"
            "The following information is from the Py-ART documentation.<br>"
            "<br>"
            "<b>WARNING</b>: By saving the file, the mask associated with "
            "the data "
            "values may be modfidied. The data itself does not change.<br>"
            "<br>"
            "<b>GateFilter</b><br>" + pyart.filters.GateFilter.__doc__ +
            "<br><br>"
            "<b>GateFilter.exclude_below</b><br>"
            "" + pyart.filters.GateFilter.exclude_below.__doc__ + ""
            )
        print(text)
        common.ShowLongText(text.replace("\n", "<br>"), set_html=True)

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
        text = (
            "<b>PyArt Script Commands</b><br><br>"
            "<i>Warning</i>: This generated script is not complete!<br>"
            "The commands below are intended to be integrated for use in "
            "batch scripting to achieve the same results seen in the Display."
            "<br><br>"
            "Just copy and paste the below commands into your script.<br><br>"
            "<i>Commands</i>:<br><br>"
            "gatefilter = pyart.filters.GateFilter(radar, exclude_based=True)"
            "<br>")

        try:
            for cmd in self.filterscript:
                text += cmd + "<br>"
        except:
            common.ShowWarning("Must apply filter first.")

        text += ("<br><br>"
                 "for field in Vradar.value.fields.keys():<br>"
                 "    Vradar.value.fields[field]['data'].mask = ("
                 "Vgatefilter.value._gate_excluded)<br>")
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
            for field in self.Vradar.value.fields.keys():
                self.Vradar.value.fields[field]['data'] = np.ma.array(
                    self.Vradar.value.fields[field]['data'],
                    mask=self.Vgatefilter.value._gate_excluded)

                # **This section is a potential replacement for merging
                # if problems are found in mask later **
#               # combine the masks  (noting two Falses is a good point)
#               combine = np.ma.mask_or(
#                   self.Vradar.value.fields[field]['data'].mask,
#                   self.Vgatefilter.value._gate_excluded)
#               self.Vradar.value.fields[field]['data'].mask = np.ma.mask_or(
#                    combine,
#                    self.Vradar.value.fields[field]['data'].mask)
#               self.Vradar.value.fields[field].data[:]=np.where(combine,
#                     self.Vradar.value.fields[field]['_FillValue'],
#                     self.Vradar.value.fields[field]['data'].data)

            pyart.io.write_cfradial(filename, self.Vradar.value)
            print("Saved %s" % (filename))

    def restoreRadar(self):
        '''Remove applied filters by restoring original mask'''
        for field in self.Vradar.value.fields.keys():
            self.Vradar.value.fields[field]['data'] = np.ma.array(
                self.Vradar.value.fields[field]['data'],
                mask=self.original_masks[field])
        self.Vgatefilter.value._gate_excluded = self.original_masks[field]
        self.Vgatefilter.update(True)

    ######################
    #   Filter Methods   #
    ######################

    def apply_filters(self):
        '''Mount Options and execute
        :py:func:`~pyart.filters.GateFilter`.
        The resulting fields are added to Vradar.
        Vradar is updated, strong or weak depending on overwriting old fields.
        '''
        # Test radar
        if self.Vradar.value is None:
            common.ShowWarning("Radar is None, cannot perform filtering.")
            return

        # Retain the original masks
        self.original_masks = {}
        for field in self.Vradar.value.fields.keys():
            self.original_masks[field] = np.ma.getmaskarray(
                self.Vradar.value.fields[field]['data'])
            print(field)

        gatefilter = pyart.filters.GateFilter(self.Vradar.value,
                                              exclude_based=True)

        # Clear flags from previous filter application or instantiate if first
        args = {}
        self.filterscript = []

        # Create a list of possible filtering actions
        val2Cmds = ["inside", "outside"]
        valinc = [">=", "<="]

        # Initial point for timing
        t0 = time.time()

        # Get a list of field to apply the filters
        self.filt_flds = []

        pyarterr = "Py-ART fails with following error\n\n"
        # Execute chosen filters
        print("Applying filters ..")
        NoChecks = True
        for index, chk in enumerate(self.fieldfilter["check_active"]):
            if chk.isChecked():
                NoChecks = False
                field = str(self.fieldfilter["field"][index].text())
                operator = str(
                    self.fieldfilter["operator"][index].currentText())
                val1 = self.fieldfilter["low_value"][index].text()
                val2 = self.fieldfilter["high_value"][index].text()

                print("%s checked, %s, v1 = %s, v2 = %s" %
                      (field, self.operators[operator], val1, val2))

                # Create the command to be issued for filtering
                # Try that command and return error if fail

                # If the operator takes val1 and val2
                if operator in val2Cmds:
                    filtercmd = "gatefilter.%s(%s, %s, %s)" % (
                        self.operators[operator], field, val1, val2)
                    if operator == "inside":
                        try:
                            gatefilter.exclude_inside(
                                field, float(val1), float(val2))
                        except:
                            import traceback
                            error = traceback.format_exc()
                            common.ShowLongText(pyarterr + error)
                    else:
                        try:
                            gatefilter.exclude_outside(
                                field, float(val1), float(val2))
                        except:
                            import traceback
                            error = traceback.format_exc()
                            common.ShowLongText(pyarterr + error)
                # If the operators are inclusive of val1
                elif operator in valinc:
                    filtercmd = "gatefilter.%s(%s, %s, inclusive=True)" % (
                        self.operators[operator], field, val1)
                    if operator == "<=":
                        try:
                            gatefilter.exclude_below(
                                field, float(val1), inclusive=True)
                        except:
                            import traceback
                            error = traceback.format_exc()
                            common.ShowLongText(pyarterr + error)
                    elif operator == ">=":
                        try:
                            gatefilter.exclude_above(
                                field, float(val1), inclusive=True)
                        except:
                            import traceback
                            error = traceback.format_exc()
                            common.ShowLongText(pyarterr + error)
                # If the operators are exclusive of val1
                else:
                    filtercmd = "gatefilter.%s(%s, %s, inclusive=False)" % (
                        self.operators[operator], field, val1)
                    if operator == "=":
                        try:
                            gatefilter.exclude_equal(
                                field, float(val1))
                        except:
                            import traceback
                            error = traceback.format_exc()
                            common.ShowLongText(pyarterr + error)
                    elif operator == "!=":
                        try:
                            gatefilter.exclude_not_equal(
                                field, float(val1))
                        except:
                            import traceback
                            error = traceback.format_exc()
                            common.ShowLongText(pyarterr + error)
                    elif operator == "<":
                        try:
                            gatefilter.exclude_below(
                                field, float(val1), inclusive=False)
                        except:
                            import traceback
                            error = traceback.format_exc()
                            common.ShowLongText(pyarterr + error)
                    elif operator == ">":
                        try:
                            gatefilter.exclude_above(
                                field, float(val1), inclusive=False)
                        except:
                            import traceback
                            error = traceback.format_exc()
                            common.ShowLongText(pyarterr + error)

                self.filterscript.append(filtercmd)

        print(("Filtering took %fs" % (time.time()-t0)))
        # If no filters were applied issue warning
        if NoChecks:
            common.ShowWarning("Please Activate Filter(s)")
            return

        # add fields and update
        self.Vgatefilter.change(gatefilter, True)

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


class MyQCheckBox(QtGui.QCheckBox):

    def __init__(self, *args, **kwargs):
        QtGui.QCheckBox.__init__(self, *args, **kwargs)
        self.is_modifiable = True
        self.clicked.connect(self.value_change_slot)

    def value_change_slot(self):
        if self.isChecked():
            self.setChecked(self.is_modifiable)
        else:
            self.setChecked(not self.is_modifiable)

    def setModifiable(self, flag):
        self.is_modifiable = flag

    def isModifiable(self):
        return self.is_modifiable
