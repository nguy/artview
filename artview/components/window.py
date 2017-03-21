"""
menu.py

Class instance used to create menu for ARTview app.
"""
from __future__ import print_function

import numpy as np
import pyart

import os
import sys
import glob

from ..core import (Variable, Component, common, QtGui, QtCore, componentsList,
                    QtWidgets, log)

class Window(Component):
    '''Class to be Main Window'''
    rootMultindex = ()

    def __init__(self, name="Window", parent=None):
        '''
        Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        name : string
            Window name.
        parent : PyQt instance
            Parent instance to associate to menu.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        Notes
        -----
        This class creates the main application interface and creates
        a menubar for the program.
        '''
        super(Window, self).__init__(name=name, parent=parent)

        # Launch the GUI interface
        self.LaunchApp()
        self.raise_()

        self.show()

    ####################
    # GUI methods #
    ####################

    def LaunchApp(self):
        '''Launches a GUI interface.'''
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Create the menus
        self.CreateMenu()

        self.widgets = {}
        self.currentMultindex = self.rootMultindex
        self.layoutTree = {}
        root_spliter = QtWidgets.QSplitter(self)
        root_spliter.setOpaqueResize(False)
        self.setCentralWidget(root_spliter)
        self.layoutTree[self.rootMultindex] = root_spliter
        root_spliter.setOrientation(QtCore.Qt.Horizontal)

        self.addPane()

    def deleteComponent(self, midx, index):
        '''Delete Tab index from pane given by midx.'''
        #widget = self.tabWidget.widget(idx)
        #self.tabWidget.removeTab(idx)
        #widget.close()
        pass


    def popComponent(self, midx, index):
        '''Pop Tab index from pane given by midx.'''
        pass

    def addComponent(self, component,  midx=None):
        '''Add Component to pane given by midx.'''
        if midx is None:
            midx = self.currentMultindex
        self.layoutTree[midx].addTab(component, component.name)
        self.layoutTree[midx].tabBar().setVisible(True)

    def setDesign(self, nrows, ncols):
        components = []
        rootMultindex = self.rootMultindex
        depth = len(rootMultindex)

        for multindex in list(self.layoutTree.keys()):
            if (multindex not in self.layoutTree or len(multindex)<=depth or
                multindex[0:depth] != rootMultindex):
                continue
            widget = self.layoutTree[multindex]
            if isinstance(widget, Pane) and widget.isClosable:
                while widget.count() > 0:
                    components.append(widget.widget(0))
                    widget.removeTab(0)
                self.removeMultindex(multindex)

        root = self.layoutTree[rootMultindex]
        self.setCurrentMultindex(rootMultindex+(0,))
        if root.orientation() == QtCore.Qt.Vertical:
            for j in range(ncols-1):
                self.splitVertical()
            for row in range(nrows-1):
                self.setCurrentMultindex(rootMultindex+(0,))
                self.addPane()
                for j in range(ncols-1):
                    self.splitVertical()
        else:
            for row in range(nrows-1):
                self.splitHorizontal()
            for col in range(ncols-1):
                self.setCurrentMultindex(rootMultindex+(0,))
                self.addPane()
                for row in range(nrows-1):
                    self.splitHorizontal()

        root = self.layoutTree[self.currentMultindex]
        for component in components:
            root.addTab(component, component.name)

    def replaceWithSplitter(self, multindex, orientation, setCurrent=True):
        '''Replace widget in multindex with splitter and move tree down'''
        widget = self.layoutTree[multindex]
        splitter = QtWidgets.QSplitter()
        splitter.setOpaqueResize(False)
        splitter.setOrientation(orientation)
        splitter.insertWidget(0, widget)
        self.layoutTree[multindex[:-1]].insertWidget(multindex[-1], splitter)

        depth = len(multindex)
        widgets = []
        for index in list(self.layoutTree.keys()):
            if (len(index)<depth or
                index[0:depth] != multindex):
                continue
            widgets.append((index,self.layoutTree.pop(index)))
        for index, widget in widgets:
            self.layoutTree[index[0:depth]+(0,)+index[depth:]] = widget
        self.layoutTree[multindex] = splitter
        self.layoutTree[multindex+(0,)].midx = multindex+(0,)
        if setCurrent and len(self.currentMultindex)>=depth:
            index = self.currentMultindex
            self.setCurrentMultindex(index[0:depth]+(0,)+index[depth:])

    def splitVertical(self):
        if (self.currentMultindex is None or
            self.layoutTree[self.currentMultindex[:-1]].orientation() ==
            QtCore.Qt.Horizontal):
            self.addPane()
            return
        self.replaceWithSplitter(self.currentMultindex, QtCore.Qt.Horizontal,
                                 False)
        self.setCurrentMultindex(self.currentMultindex+(0,))
        self.addPane()

    def splitHorizontal(self):
        if (self.currentMultindex is None or
            self.layoutTree[self.currentMultindex[:-1]].orientation() ==
            QtCore.Qt.Vertical):
            self.addPane()
            return
        self.replaceWithSplitter(self.currentMultindex, QtCore.Qt.Vertical,
                                 False)
        self.setCurrentMultindex(self.currentMultindex+(0,))
        self.addPane()

    def addPane(self):
        widget = Pane()
        widget.turnCurrent.connect(self.widgetTurnCurrent)

        if self.currentMultindex is None:
            self.currentMultindex = self.rootMultindex
        splitter = self.layoutTree[self.currentMultindex[:-1]]
        splitter.addWidget(widget)
        midx = self.currentMultindex[:-1]+(splitter.count()-1,)
        self.layoutTree[midx] = widget
        widget.midx = midx
        self.setCurrentMultindex(midx)
        widget.show()
        splitter.show()

    def closeCurrentPane(self):
        print("Close current Pane: ", self.currentMultindex,
              self.layoutTree[self.currentMultindex],
              file=log.debug)
        if self.layoutTree[self.currentMultindex].isClosable:
            self.removeMultindex(self.currentMultindex, True)
        else:
            common.ShowWarning("Current Pane is not closable!")

    def removeMultindex(self, midx, resetCurrent=False):
        print("Close multindex: ", midx, self.layoutTree[midx],
              file=log.debug)
        resetCurrent = (resetCurrent or midx == self.currentMultindex)
        if midx == self.rootMultindex:
            if isinstance(self.layoutTree[midx], QtWidgets.QSplitter):
                widget = Pane()
                widget.turnCurrent.connect(self.widgetTurnCurrent)
                self.layoutTree[midx].insertWidget(0, widget)
                self.layoutTree[midx+(0,)] = widget
                widget.midx = midx+(0,)
                if resetCurrent:
                    self.setCurrentMultindex(midx+(0,))
            elif resetCurrent:
                self.setCurrentMultindex(self.rootMultindex)
            return
        widget = self.layoutTree.pop(midx)
        widget.setParent(None)
        widget.close()
        widget.deleteLater()
        if self.layoutTree[midx[:-1]].count() == 0:
            self.removeMultindex(midx[:-1], resetCurrent)
        elif resetCurrent:
            l = [i for i in self.layoutTree if i[:-1]==midx[:-1] and i!=midx and i!=()]
            if l:
                self.setCurrentMultindex(l[0])
            else:
                self.setCurrentMultindex(midx[:-1])

#    def closeInactivePanes(self):
#        widget = self.layoutTree[self.currentMultindex]
#        splitter = self.layoutTree[()]
#        splitter.insertWidget(0, widget)
#        for midx in list(self.layoutTree.keys()):
#            if midx != () and midx !=self.currentMultindex:
#                self.layoutTree[midx].deleteLater()
#                del self.layoutTree[midx]
#        del self.layoutTree[self.currentMultindex]
#        self.layoutTree[(0,)] = widget
#        self.setCurrentMultindex((0,))

    def closeEmptyPanes(self):
        for midx in list(self.layoutTree.keys()):
            if midx not in self.layoutTree:
                continue
            widget = self.layoutTree[midx]
            if isinstance(widget, Pane):
                if widget.count() == 0 and widget.isClosable:
                    self.removeMultindex(midx)

    def showHideTabBar(self):
        bar = self.layoutTree[self.currentMultindex].tabBar()
        if bar.isVisible():
            bar.setVisible(False)
        else:
            bar.setVisible(True)

    def popNewWindow(self):
        widget = self.layoutTree[self.currentMultindex]
        if not isinstance(widget, Pane):
            common.ShowWarning("ERROR: current widget is not a Pane.\n"
                               "this should not happen, please report at github")
        components = []
        while widget.count() > 0:
            components.append(widget.widget(0))
            widget.removeTab(0)

        newWindow = Window()
        pane = newWindow.layoutTree[newWindow.currentMultindex]
        for component in components:
            pane.addTab(component,component.name)

        self.removeMultindex(self.currentMultindex)

    def widgetTurnCurrent(self, widget):
        for midx in self.layoutTree.keys():
            if self.layoutTree[midx] == widget:
                self.setCurrentMultindex(midx)
                return

    def setCurrentMultindex(self, midx):
        if midx == self.currentMultindex:
            return
        self.currentMultindex = midx
        for key in self.layoutTree.keys():
            widget = self.layoutTree[key]
            if key == midx:
                widget.isCurrent = True
                widget.update()
            elif isinstance(widget, Pane):
                if widget.isCurrent:
                    widget.isCurrent = False
                    widget.update()

    def addWindow(self):
        Window()

    ######################
    # Menu build methods #
    ######################

    def menus(self):
        return (self.menubar, self.subMenus(self.menubar))

    def subMenus(self, menu):
        ''' get submenu list of menu as dictionary. '''
        if menu is None:
            return None
        menus = {}
        for act in menu.actions():
            menus[str(act.text())] = (act.menu(), self.subMenus(act.menu()))
        return menus

    def addMenuAction(self, position, *args):
        menu, menus = self.menus()
        for key in position:
            if key in menus:
                menu, menus = menus[key]
            else:
                menu = menu.addMenu(key)
                menus = {}
        return menu.addAction(*args)

    def addMenuSeparator(self, position, *args):
        menu, menus = self.menus()
        for key in position:
            if key in menus:
                menu, menus = menus[key]
            else:
                menu = menu.addMenu(key)
                menus = {}
        return menu.addSeparator(*args)

    def CreateMenu(self):
        '''Create the main menubar.'''

        self.menubar = self.menuBar()

        self.addArtviewMenu()
        layoutmenu = self.menubar.addMenu('&Layout')

        designsMenu = layoutmenu.addMenu("Designs")
        designsMenu.addAction("1 x 1", lambda: self.setDesign(1, 1))
        designsMenu.addAction("2 x 2", lambda: self.setDesign(2, 2))
        designsMenu.addAction("4 x 1", lambda: self.setDesign(4, 1))

        layoutmenu.addAction('Split Pane Verticaly', self.splitVertical)
        layoutmenu.addAction('Split Pane Horizontaly', self.splitHorizontal)
        #layoutmenu.addAction('Add Pane', self.addPane)
        layoutmenu.addAction('Current Pane: show/hide TabBar', self.showHideTabBar)
        layoutmenu.addAction('Current Pane: Pop into new Window', self.popNewWindow)
        layoutmenu.addAction('Close Current Pane', self.closeCurrentPane)
        layoutmenu.addAction('Close Empty Panes', self.closeEmptyPanes)

        action = QtWidgets.QAction('New Window', self)
        action.triggered.connect(self.addWindow)
        layoutmenu.addAction(action)

    def addArtviewMenu(self):
        '''Add the Artview Menu to menubar.'''
        menu = self.menubar.addMenu('ARTView')

        # Create About ARTView action
        aboutApp = QtWidgets.QAction('ARTView...', self)
        aboutApp.setStatusTip('About ARTview')
        aboutApp.triggered.connect(self._about)
        menu.addAction(aboutApp)

        # Create Plugin Help action
        pluginHelp = QtWidgets.QAction('Plugin Help', self)
        pluginHelp.setStatusTip('More information about Plugins')
        pluginHelp.triggered.connect(self._get_pluginhelp)
        menu.addAction(pluginHelp)

        # Create Close ARTView action
        exitApp = QtWidgets.QAction('Close', self)
        exitApp.setShortcut('Ctrl+Q')
        exitApp.setStatusTip('Exit ARTview')
        exitApp.triggered.connect(self.close)
        menu.addAction(exitApp)
        menu.addSeparator()

    def startComponent(self, Comp):
        '''Execute the GUI start of Component and
        add to layout if not independent.'''
        comp, independent = Comp.guiStart(self)
        if not independent:
            self.addComponent(comp, self.currentMultindex)

    ######################
    # Help methods #
    ######################

    def _about(self):
        # Add a more extensive about eventually
        text = (
            "<b>About ARTView</b><br><br>"
            "ARTview is a visualization package that leverages the <br>"
            "DoE Py-ART python software to view individual weather <br>"
            "radar data files or to browse a directory of data.<br><br>"
            "<i>Note</i>:<br>"
            "Tooltip information is available if you hover over buttons <br> "
            "and menus with the mouse.<br><br>"
            "<i>Documentation</i>:<br>"
            "<br><br>"
            "For a demonstration, a "
            "<a href='https://rawgit.com/nguy/artview/master/docs/build/"
            "html/index.html'>Software Package Documentation</a><br>"
            )
        common.ShowLongTextHyperlinked(text)

    def _get_pluginhelp(self):
        '''Print out a short help text box regarding plugins.'''

        text = (
            "<b>Existing Plugins</b><br><br>"
            "Current plugins can be found under the <i>File->Plugins</i> "
            "menu.<br>"
            "Most plugins have a help button for useage information.<br>"
            "<br><br>"
            "<b>Creating a Custom Plugin</b><br><br>"
            "ARTview allows the creation of custom user plugins.<br><br>"
            "Instructions and examples can be found at:<br>"
            "https://rawgit.com/nguy/artview/master/docs/build/html/"
            "plugin_tutorial.html<br><br>"
            "Please consider submitting your plugin for inclusion in "
            "ARTview<br>"
            "  Submit a pull request if you forked the repo on Github or"
            "  Post the code in an Issue:<br>"
            "https://github.com/nguy/artview/issues<br><br>")

        common.ShowLongText(text)


class Pane(QtWidgets.QTabWidget):
    turnCurrent = QtCore.pyqtSignal(QtWidgets.QTabWidget, name="turnCurrent")
    isCurrent = False
    isClosable = True
    fix = False

    def __init__(self):
        super(Pane,self).__init__()
        tab=TabBar()
        tab.dragStart.connect(self.dragStart)
        tab.currentChanged.connect(self.setCurrent)
        tab.clicked.connect(self.setCurrent)
        self.setTabBar(tab)
        self.setAcceptDrops(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        #self.setMinimumSize(80,40)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                           QtWidgets.QSizePolicy.Maximum)
        self.show()

    def setCurrent(self):
        self.turnCurrent.emit(self)
        self.isCurrent = True
        self.update()

    def minimumSizeHint(self):
        if self.currentWidget() is not None:
            hint = self.currentWidget().minimumSizeHint()
            if self.tabBar().isVisible():
                tabHint = self.tabBar().minimumSize()
            else:
                tabHint = QtCore.QSize(0, 0)
            hint.setHeight(hint.height() + tabHint.height())
            hint.setWidth(max(hint.width(), tabHint.width()))
        else:
            hint = super(Pane, self).minimumSizeHint()
            if hint.width() < 80:
                hint.setWidth(80)
            if hint.height() < 40:
                hint.setHeight(40)
        return hint

    def sizeHint(self):
        if self.fix:
            return self.minimumSizeHint()
        else:
            return super(Pane, self).sizeHint()

    def maximumSize(self):
        if self.fix:
            return self.minimumSizeHint()
        else:
            return super(Pane, self).maximumSize()

    def maximumSizeHint(self):
        if self.fix:
            return self.minimumSizeHint()
        else:
            return super(Pane, self).maximumSizeHint()

    def minimumSize(self):
        return self.minimumSizeHint()

    def mousePressEvent(self, event):
        super(Pane,self).mousePressEvent(event)
        self.setCurrent()

    def keyPressEvent(self,event):
        super(Pane,self).keyPressEvent(event)

    def dragStart(self, idx):
        mimeData = QtCore.QMimeData()
        mimeData.setData("text/artview",self.widget(idx).__repr__())
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec_(QtCore.Qt.MoveAction)
        if drag.target() == None:
            window = Window()
            window.addComponent(self.widget(idx))

    def dragEnterEvent(self, event):
        source = event.source()
        if source.__class__ == Pane and self.tabBar().isVisible():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData and event.source() != self:
            text = mimeData.data("text/artview")
            try:
                text = str(text, "utf-8") # python3
            except:
                text = str(text)
            d = dict([(c.__repr__(),c) for c in componentsList])
            if text in d.keys():
                widget = d[text]
                self.addTab(widget,widget.name)
                self.setCurrent()

#    def addTab(self, widget, name):
#        widget.installEventFilter(self)
#        super(Pane, self).addTab(widget, name)
#
#    def tabRemoved(self, idx):
#        print "remove tab",idx
#        super(Pane, self).tabRemoved(idx)
#
#    def eventFilter(self, obj, event):
#        if event.type() == QtCore.QEvent.FocusIn:
#            print "focus in: ", obj
#        return False

    def closeTab(self, idx):
        self.widget(idx).close()
        self.widget(idx).deleteLater()

    def paintEvent(self, event):
        super(Pane, self).paintEvent(event)

        painter = QtGui.QPainter(self)
        #painter.setBackgroundMode(1)
        option = QtWidgets.QStyleOptionButton()
        #option2 = QtWidgets.QStyleOptionFocusRect()
        option.initFrom(self)
        #option2.initFrom(self)

        style = self.style()
        if self.isCurrent:
            option.state |= style.State_HasFocus
            option.state |= 0x01000000
            option.state |= style.State_MouseOver
            option.state |= style.State_Raised
            style.drawControl(QtWidgets.QStyle.CE_PushButton, option, painter, self)
            #option2.backgroundColor = QtGui.QColor(QtCore.Qt.green)
            #style.drawPrimitive(QtWidgets.QStyle.PE_FrameFocusRect, option2, painter, self)
        else:
            option.state &= not style.State_HasFocus
            option.state &= not 0x01000000
            option.state &= not style.State_MouseOver
            option.state |= style.State_Sunken
            #option.background = PyGui.QPalette.Background
            style.drawControl(QtWidgets.QStyle.CE_PushButton, option, painter, self)
        if self.count() == 0:
            painter.drawText(option.rect,QtCore.Qt.AlignCenter,"Move Tabs \n in Here \n")

    def close(self):
        for i in range(self.count()):
            self.closeTab(i)
        super(Pane, self).close()

class TabBar(QtWidgets.QTabBar):
    dragStart = QtCore.pyqtSignal(int)
    clicked = QtCore.pyqtSignal()

    def __init__(self):
        super(QtWidgets.QTabBar, self).__init__()
        self.pos = None

#    def tabInserted(self, index):
#        super(TabBar, self).tabInserted(index)
#        self.setVisible(self.count() > 1)

#    def tabRemoved(self, index):
#        super(TabBar, self).tabRemoved(index)
#        self.setVisible(self.count() > 1)


    def mousePressEvent(self, mouseEvent):
        self.pos = mouseEvent.pos()
        QtWidgets.QTabBar.mousePressEvent(self, mouseEvent)
        self.clicked.emit()

    def mouseReleaseEvent(self, mouseEvent):
        self.pos = None
        QtWidgets.QTabBar.mouseReleaseEvent(self, mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.pos is not None:
            pos = mouseEvent.pos()
            if (self.pos-pos).manhattanLength() > 10:
                self.dragStart.emit(self.tabAt(self.pos))

class LayoutComponent(Component):
    '''Class to staticly hold other components inside a layout.
    Once they are added do not try remove or delete then.'''

    def __init__(self, name="Layout", parent=None):
        '''
        Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        name : string
            Window name.
        parent : PyQt instance
            Parent instance to associate to menu.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.

        '''
        super(LayoutComponent, self).__init__(name=name, parent=parent)
        widget = QtWidgets.QWidget()
        self.widgets = []
        self.layout = QtWidgets.QGridLayout()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.layout.setContentsMargins(0,0,0,0)

    def addWidget(self, widget, *args, **kwargs):
        """ Add widget to the layout and to a list that keeps track of it
        there is no way to revert this, once added the widget shall not be
        removed, and when this component is closed all added widgets are closed
        as well."""
        self.layout.addWidget(widget, *args, **kwargs)
        self.widgets.append(widget)

    def close(self):
        for widget in self.widgets:
            widget.close()
            widget.deleteLater()
        super(LayoutComponent, self).close()
