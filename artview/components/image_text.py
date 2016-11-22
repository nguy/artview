"""
image_text.py
Routines for Display modifications and additions.
"""

# Load the needed packages
from ..core import QtGui, QtCore
from .. import core
from datetime import datetime as dt


class ImageTextBox(QtGui.QMainWindow):
    '''
    Interface for executing :py:class:`ImageTextBox`.
    '''

    def __init__(self, display,
                 name="ImageTextBox", parent=None):
        '''Initialize the class to create the interface.
        Parameters
        ----------
        [Optional]
        name : string
            ImageTextBox instance window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated w/ parent PyQt instance
        '''
        super(ImageTextBox, self).__init__(parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)

        self.display = display

        self.generalLayout = QtGui.QVBoxLayout()
        # Set the Variable layout
        self.generalLayout.addWidget(self.ButtonUI(), 2)
        self.generalLayout.addWidget(self.EntryUI(), 1)
        self.generalLayout.addWidget(self.TextUI(), 0)
        self.generalLayout.layout().setDirection(QtGui.QBoxLayout.BottomToTop)

        self.layout.addLayout(self.generalLayout, 0, 0, 1, 2)

        self.chooseText(0)

        self.show()

    ######################
    #   Layout Methods   #
    ######################

    def TextUI(self):
        '''
        Mount the Text layout.
        User may select another Text instance
        '''
        groupBox = QtGui.QGroupBox(self.display.name + " Image Text Selection")
        gBox_layout = QtGui.QGridLayout()

        self.dispCombo = QtGui.QComboBox()
        gBox_layout.addWidget(QtGui.QLabel("Select Text Instance"), 0, 0)
        gBox_layout.addWidget(self.dispCombo, 0, 1, 1, 1)

        self.dispChoiceList = []

        # Add the Add Text option to top of list
        self.dispCombo.addItem('Add Text')
        self.dispChoiceList.append(self._init_entries())
        self.choice = self.dispChoiceList[0]

        # Fill in the rest of the list with existing text boxes
        for tx_inst in self.display.disp_text.keys():
            self.dispCombo.addItem(tx_inst)
            self.dispChoiceList.append(self.display.disp_text[tx_inst])
        self.dispCombo.setCurrentIndex(0)

        self.dispCombo.activated.connect(self.chooseText)
        groupBox.setLayout(gBox_layout)
        return groupBox

    def ButtonUI(self):
        '''Mount the Action layout.'''
        groupBox = QtGui.QGroupBox("Select Action")
        gBox_layout = QtGui.QGridLayout()

        self.helpButton = QtGui.QPushButton("Help")
        self.helpButton.clicked.connect(self._displayHelp)
        gBox_layout.addWidget(self.helpButton, 0, 0, 1, 1)

        self.updateButton = QtGui.QPushButton("Update Text")
        self.updateButton.clicked.connect(self.updateChoice)
        self.updateButton.setToolTip('Display relevant python script')
        gBox_layout.addWidget(self.updateButton, 0, 1, 1, 1)

        self.delButton = QtGui.QPushButton("Delete Text")
        self.delButton.clicked.connect(self.delDispText)
        self.delButton.setToolTip('Save cfRadial data file')
        gBox_layout.addWidget(self.delButton, 1, 0, 1, 1)

        self.clrButton = QtGui.QPushButton("Clear All Text")
        self.clrButton.clicked.connect(self.clrDispText)
        self.clrButton.setToolTip('Remove applied filters')
        gBox_layout.addWidget(self.clrButton, 1, 1, 1, 1)

        groupBox.setLayout(gBox_layout)

        return groupBox

    def EntryUI(self):
        '''Mount text entry layout.'''
        groupBox = QtGui.QGroupBox("Text Entry and Position")
        # groupBox.setFlat(True)
        gBox_layout = QtGui.QGridLayout()

        # Set up the Labels for entry
        tex = QtGui.QLabel("Label Text")
        xpos = QtGui.QLabel("X-Coord")
        ypos = QtGui.QLabel("Y-Coord")
        texc = QtGui.QLabel("Color")
        texsz = QtGui.QLabel("Font Size")
        texst = QtGui.QLabel("Style")

        # Set up the Entry Line Entries / Add text
        self.ent_tex = QtGui.QLineEdit('')
        self.ent_tex.setToolTip('Label box text')
        self.ent_xpos = QtGui.QLineEdit('')
        self.ent_xpos.setToolTip('X position of text on display')
        self.ent_ypos = QtGui.QLineEdit('')
        self.ent_ypos.setToolTip('Y position of text on display')
        self.ent_texc = QtGui.QLineEdit('')
        self.ent_texc.setToolTip('Label text color')
        self.ent_texsz = QtGui.QLineEdit('')
        self.ent_texsz.setToolTip('Label text font size')
        self.ent_texst = QtGui.QLineEdit('')
        self.ent_texst.setToolTip('Label text font style: normal, '
                                  'italic, or bold')

        # Add the Label and Entry fields to layout
        gBox_layout.addWidget(tex, 0, 0, 1, 1)
        gBox_layout.addWidget(xpos, 2, 0, 1, 1)
        gBox_layout.addWidget(ypos, 2, 1, 1, 1)
        gBox_layout.addWidget(texc, 4, 0, 1, 1)
        gBox_layout.addWidget(texsz, 4, 1, 1, 1)
        gBox_layout.addWidget(texst, 4, 2, 1, 1)

        gBox_layout.addWidget(self.ent_tex, 1, 0, 1, 1)
        gBox_layout.addWidget(self.ent_xpos, 3, 0, 1, 1)
        gBox_layout.addWidget(self.ent_ypos, 3, 1, 1, 1)
        gBox_layout.addWidget(self.ent_texc, 5, 0, 1, 1)
        gBox_layout.addWidget(self.ent_texsz, 5, 1, 1, 1)
        gBox_layout.addWidget(self.ent_texst, 5, 2, 1, 1)

        groupBox.setLayout(gBox_layout)
        return groupBox

    #########################
    #   Selection Methods   #
    #########################

    def chooseText(self, selection):
        '''Get Display Text.'''
        self.choice_key = str(self.dispCombo.currentText())
        self.choice = self.dispChoiceList[selection]
        self.dispCombo.setCurrentIndex(selection)
        self._rebuild_entry()

    def _displayHelp(self):
        '''Display help.'''
        text = (
            "<b>Using the ImageTextBox window</b><br><br>"
            "<i>Choose an existing Text box:</i><br>"
            "  1. Select instance from drop-down list.<br>"
            "  2. Modify exising instance by changing values in "
            "     Text Value and Position. Click Update to save.<br>"
            "  3. Create a new Text box by choosing Add Text from drop-down."
            "     Modify default values provided. Click Update to save."
            "<br>"
            "  4. Delete an instance by selecting and click Delete Text.<br>"
            "  5. Clear all instances by clicking Clear All Text.<br>"
            "<br>"
            )
        core.common.ShowLongText(text.replace("\n", "<br>"), set_html=True)

    def updateChoice(self):
        '''Update the Display text box and/or parameters.'''
        self._check_entries()
        self.choice = self._get_entries()

        # Create the text instance
        # Add to list if new instance or overwrite if present
        if self.choice['text'] not in self.display.disp_text.keys():
            self.choice['instance'] = self.display.ax.text(
                self.choice['xpos'], self.choice['ypos'],
                self.choice['text'], style=self.choice['style'],
                color=self.choice['col'], fontsize=self.choice['size'])
            self.dispCombo.addItem(self.choice['text'])
            self.dispChoiceList.append(self.choice)
            self.dispCombo.setCurrentIndex(self.dispCombo.count() - 1)
            self.chooseText(self.dispCombo.count() - 1)
        else:
            print("Overwriting text")
            select = self.dispCombo.findText(self.choice['text'])
            try:
                self.dispChoiceList[select]['instance'].remove()
            except:
                print("No instance found")
            self.choice['instance'] = self.display.ax.text(
                self.choice['xpos'], self.choice['ypos'],
                self.choice['text'], style=self.choice['style'],
                color=self.choice['col'], fontsize=self.choice['size'])
            self.dispChoiceList[select] = self.choice
            self.dispCombo.setCurrentIndex(select)
            self.chooseText(select)
        # Write the updated text item to the Display Text instance
        self.display.disp_text[self.choice['text']] = self.choice

        # Redraw the canvas to place new text
        self.display.fig.canvas.draw()

    def delDispText(self):
        '''Delete selected Display text boxes.'''
        self.choice_key = str(self.ent_tex.text())
        if self.dispCombo.currentText() in self.display.disp_text.keys():
            del self.display.disp_text[self.choice_key]

        delselect = self.dispCombo.findText(self.choice_key)
        if delselect != -1:
            self.dispChoiceList[delselect]['instance'].remove()
            del self.dispChoiceList[delselect]
            self.dispCombo.removeItem(delselect)
            self.display.fig.canvas.draw()

        self.chooseText(0)

    def clrDispText(self):
        '''Clear all Display text boxes.'''
        self.display.disp_text = {}
        self.choice = self._init_entries()
        # Delete each entry, need to reverse indices
        for i in range(self.dispCombo.count())[::-1]:
            if i > 0:
                self.dispChoiceList[i]['instance'].remove()
                del self.dispChoiceList[i]
                self.dispCombo.removeItem(i)
        self.display.fig.canvas.draw()
        self.chooseText(0)

    #####################
    #   Entry Methods   #
    #####################

    def _rebuild_entry(self):
        '''Reset the entries based upon input.'''
        self.ent_tex.setText(str(self.choice['text']))
        self.ent_xpos.setText(str(self.choice['xpos']))
        self.ent_ypos.setText(str(self.choice['ypos']))
        self.ent_texc.setText(str(self.choice['col']))
        self.ent_texsz.setText(str(self.choice['size']))
        self.ent_texst.setText(str(self.choice['style']))

    def _init_entries(self):
        '''Initialize Add Text Instance.'''
        blank_text = {'text': 'NewText', 'xpos': 0.0, 'ypos': 0.0,
                      'col': 'black', 'size': 24, 'style': 'normal'}
        return blank_text

    def _check_entries(self):
        '''Check that entries are valid.'''
        if not isinstance(str(self.ent_tex.text()), str):
            core.common.ShowWarning('Label Text must be string entry')
        if not isinstance(float(self.ent_xpos.text()), float):
            core.common.ShowWarning('X-Coord must be float value')
        if not isinstance(float(self.ent_ypos.text()), float):
            core.common.ShowWarning('Y-Coord must be float value')
        if not isinstance(str(self.ent_texc.text()), str):
            core.common.ShowWarning('Color must be a valid string ')
        if not isinstance(int(self.ent_texsz.text()), int):
            core.common.ShowWarning('Text size must be integer value')
        if str(self.ent_texst.text()) not in ['normal', 'italic', 'oblique']:
            core.common.ShowWarning(
                'Text Style must be normal, italic, or oblique')

    def _get_entries(self):
        '''Get the entry values and put in dictionary.'''
        tmp_tex = {'text': str(self.ent_tex.text()),
                   'xpos': float(self.ent_xpos.text()),
                   'ypos': float(self.ent_ypos.text()),
                   'col': str(self.ent_texc.text()),
                   'size': int(self.ent_texsz.text()),
                   'style': str(self.ent_texst.text())
                   }
        return tmp_tex
