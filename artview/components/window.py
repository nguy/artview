"""
menu.py

Class instance used to create menu for ARTview app.
"""
import numpy as np
import pyart

import os
import sys
import glob

from ..core import Variable, Component, common, QtGui, QtCore, componentsList

class Window(Component):
    '''Class to be Main Window'''

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
        self.currentMindex = ()
        self.layoutTree = {}
        root_spliter = QtGui.QSplitter(self)
        self.setCentralWidget(root_spliter)
        self.layoutTree[()] = root_spliter
        root_spliter.setOrientation(QtCore.Qt.Horizontal)

        self.addView()


    def deleteComponent(self, midx, index):
        '''Delete Tab index from view given by midx.'''
        #widget = self.tabWidget.widget(idx)
        #self.tabWidget.removeTab(idx)
        #widget.close()
        pass


    def popComponent(self, midx, index):
        '''Pop Tab index from view given by midx.'''
        pass

    def addComponent(self, component,  midx=None):
        '''Add Component to view given by midx.'''
        if midx is None:
            midx = self.currentMindex
        self.layoutTree[midx].addTab(component, component.name)

    def splitVertical(self):
        if (self.currentMindex is None or
            self.layoutTree[self.currentMindex[:-1]].orientation() ==
            QtCore.Qt.Horizontal):
            self.addView()
            return
        widget = self.layoutTree[self.currentMindex]
        splitter = QtGui.QSplitter()
        splitter.setOrientation(QtCore.Qt.Horizontal)
        splitter.insertWidget(0, widget)
        self.layoutTree[self.currentMindex] = splitter
        self.layoutTree[self.currentMindex[:-1]].insertWidget(self.currentMindex[-1], splitter)
        self.layoutTree[self.currentMindex+(0,)] = widget
        self.setCurrentMindex(self.currentMindex+(0,))
        self.addView()

    def splitHorizontal(self):
        if (self.currentMindex is None or
            self.layoutTree[self.currentMindex[:-1]].orientation() ==
            QtCore.Qt.Vertical):
            self.addView()
            return
        widget = self.layoutTree[self.currentMindex]
        splitter = QtGui.QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.insertWidget(0, widget)
        self.layoutTree[self.currentMindex] = splitter
        self.layoutTree[self.currentMindex[:-1]].insertWidget(self.currentMindex[-1], splitter)
        self.layoutTree[self.currentMindex+(0,)] = widget
        self.setCurrentMindex(self.currentMindex+(0,))
        self.addView()

    def addView(self):
        widget = View()
        QtCore.QObject.connect(widget, QtCore.SIGNAL("turnCurrent"), self.widgetTurnCurrent)

        if self.currentMindex is None:
            self.currentMindex = ()
        splitter = self.layoutTree[self.currentMindex[:-1]]
        splitter.addWidget(widget)
        midx = self.currentMindex[:-1]+(splitter.count()-1,)
        self.layoutTree[midx] = widget
        self.setCurrentMindex(midx)
        widget.show()
        splitter.show()

    def closeCurrentView(self):
        self.removeMindex(self.currentMindex)

    def removeMindex(self, midx):
        print "close:  ", midx
        if midx == ():
            self.setCurrentMindex(())
            return
        widget = self.layoutTree.pop(midx)
        widget.setParent(None)
        widget.close()
        widget.deleteLater()
        print midx[:-1], "count  ", self.layoutTree[midx[:-1]].count()
        if self.layoutTree[midx[:-1]].count() == 0:
            self.removeMindex(midx[:-1])
        else:
            l = [i for i in self.layoutTree if i[:-1]==midx[:-1] and i!=midx and i!=()]
            print l
            if l:
                self.setCurrentMindex(l[0])
            else:
                self.setCurrentMindex(midx[:-1])

    def closeInactiveView(self):
        widget = self.layoutTree[self.currentMindex]
        splitter = self.layoutTree[()]
        splitter.insertWidget(0, widget)
        for midx in list(self.layoutTree.keys()):
            if midx != () and midx !=self.currentMindex:
                self.layoutTree[midx].deleteLater()
                del self.layoutTree[midx]
        del self.layoutTree[self.currentMindex]
        self.layoutTree[(0,)] = widget
        self.setCurrentMindex((0,))

    def showHideTabBar(self):
        bar = self.layoutTree[self.currentMindex].tabBar()
        if bar.isVisible():
            bar.setVisible(False)
        else:
            bar.setVisible(True)

    def widgetTurnCurrent(self, widget):
        for midx,w in self.layoutTree.iteritems():
            if w == widget:
                self.setCurrentMindex(midx)
                return

    def setCurrentMindex(self, midx):
        if midx == self.currentMindex:
            return
        self.currentMindex = midx
        for key, widget in self.layoutTree.iteritems():
            if key == midx:
                widget.isCurrent = True
                widget.update()
            elif isinstance(widget, View):
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

        layoutmenu.addAction('Split Vertical', self.splitVertical)
        layoutmenu.addAction('Split Horizontal', self.splitHorizontal)
        #layoutmenu.addAction('Add View', self.addView)
        layoutmenu.addAction('Current View: show/hide TabBar', self.showHideTabBar)
        layoutmenu.addAction('Close Current View', self.closeCurrentView)
        layoutmenu.addAction('Close Inactive Views', self.closeInactiveView)


        action = QtGui.QAction('New Window', self)
        action.triggered.connect(self.addWindow)
        layoutmenu.addAction(action)

    def addArtviewMenu(self):
        '''Add the Artview Menu to menubar.'''
        menu = self.menubar.addMenu('ARTView')

        # Create About ARTView action
        aboutApp = QtGui.QAction('ARTView...', self)
        aboutApp.setStatusTip('About ARTview')
        aboutApp.triggered.connect(self._about)
        menu.addAction(aboutApp)

        # Create Plugin Help action
        pluginHelp = QtGui.QAction('Plugin Help', self)
        pluginHelp.setStatusTip('More information about Plugins')
        pluginHelp.triggered.connect(self._get_pluginhelp)
        menu.addAction(pluginHelp)

        # Create Close ARTView action
        exitApp = QtGui.QAction('Close', self)
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
            self.addComponent(comp, self.currentMindex)

    def changeMode(self, new_mode):
        ''' Open and connect new components to satisfy mode.

        Parameters
        ----------
        new_mode: see file artview/modes.py for documentation on modes
        '''
        components = new_mode[0][:]
        links = new_mode[1]
        static_comp_list = componentsList[:]
        # find already running components
        for i, component in enumerate(components):
            flag = False
            for j, comp in enumerate(static_comp_list):
                if isinstance(comp, component):
                    components[i] = static_comp_list.pop(j)
                    flag = True
                    break
            if not flag:
                # if there is no component open
                print("starting component: %s" % component.__name__)
                from ..core.core import suggestName
                name = suggestName(components[i])
                components[i] = components[i](name=name, parent=self)
                self.addComponent(components[i], self.currentMindex)

        for link in links:
            dest = getattr(components[link[0][0]], link[0][1])
            orin = getattr(components[link[1][0]], link[1][1])
            if dest is orin:
                # already linked
                pass
            else:
                # not linked, link
                print("linking %s.%s to %s.%s" %
                      (components[link[1][0]].name, link[1][1],
                       components[link[0][0]].name, link[0][1]))
                # Disconect old Variable
                components[link[1][0]].disconnectSharedVariable(link[1][1])
                # comp1.var = comp0.var
                setattr(components[link[1][0]], link[1][1], dest)
                # Connect new Variable
                components[link[1][0]].connectSharedVariable(link[1][1])
                # Emit change signal
                dest.update()

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


class View(QtGui.QTabWidget):
    isCurrent = False
    fix = False

    def __init__(self):
        super(View,self).__init__()
        tab=TabBar()
        tab.dragStart.connect(self.dragStart)
        tab.currentChanged.connect(self.setCurrent)
        tab.clicked.connect(self.setCurrent)
        self.setTabBar(tab)
        self.setAcceptDrops(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        #self.setMinimumSize(80,40)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Maximum)
        self.show()

    def setCurrent(self):
        self.emit(QtCore.SIGNAL("turnCurrent"), self)
        self.isCurrent = True
        self.update()

    def minimumSizeHint(self):
        if self.currentWidget() is not None:
            hint = self.currentWidget().minimumSizeHint()
            tabHint = self.tabBar().minimumSizeHint()
            hint.setHeight(hint.height() + tabHint.height())
            hint.setWidth(max(hint.width(), tabHint.width()))
        else:
            hint = super(View, self).minimumSizeHint()
            if hint.width() < 80:
                hint.setWidth(80)
            if hint.height() < 40:
                hint.setHeight(40)
        return hint

    def sizeHint(self):
        if self.fix:
            return self.minimumSizeHint()
        else:
            return super(View, self).sizeHint()

    def maximumSize(self):
        if self.fix:
            return self.minimumSizeHint()
        else:
            return super(View, self).maximumSize()

    def maximumSizeHint(self):
        if self.fix:
            return self.minimumSizeHint()
        else:
            return super(View, self).maximumSizeHint()


    def minimumSize(self):
        return self.minimumSizeHint()
    def mousePressEvent(self, event):
        super(View,self).mousePressEvent(event)
        self.setCurrent()

    def keyPressEvent(self,event):
        super(View,self).keyPressEvent(event)

    def dragStart(self, idx):
        mimeData = QtCore.QMimeData()
        mimeData.setData("text/artview",self.widget(idx).__repr__())
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.start(QtCore.Qt.MoveAction)
        if drag.target() == None:
            window = Window()
            window.addComponent(self.widget(idx))

    def dragEnterEvent(self, event):
        source = event.source()
        if source.__class__ == View:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData and event.source() != self:
            text = str(mimeData.data("text/artview"))
            d = dict([(c.__repr__(),c) for c in componentsList])
            if text in d:
                widget = d[text]
                self.addTab(widget,widget.name)
                self.setCurrent()

#    def addTab(self, widget, name):
#        widget.installEventFilter(self)
#        super(View, self).addTab(widget, name)
#
#    def tabRemoved(self, idx):
#        print "remove tab",idx
#        super(View, self).tabRemoved(idx)
#
#    def eventFilter(self, obj, event):
#        if event.type() == QtCore.QEvent.FocusIn:
#            print "focus in: ", obj
#        return False

    def closeTab(self, idx):
        self.widget(idx).close()
        self.widget(idx).deleteLater()

    def paintEvent(self, event):
        super(View, self).paintEvent(event)

        painter = QtGui.QPainter(self)
        #painter.setBackgroundMode(1)
        option = QtGui.QStyleOptionButton()
        #option2 = QtGui.QStyleOptionFocusRect()
        option.initFrom(self)
        #option2.initFrom(self)

        style = self.style()
        if self.isCurrent:
            option.state |= style.State_HasFocus
            option.state |= 0x01000000
            option.state |= style.State_MouseOver
            option.state |= style.State_Raised
            style.drawControl(QtGui.QStyle.CE_PushButton, option, painter, self)
            #option2.backgroundColor = QtGui.QColor(QtCore.Qt.green)
            #style.drawPrimitive(QtGui.QStyle.PE_FrameFocusRect, option2, painter, self)
        else:
            option.state &= not style.State_HasFocus
            option.state &= not 0x01000000
            option.state &= not style.State_MouseOver
            option.state |= style.State_Sunken
            #option.background = PyGui.QPalette.Background
            style.drawControl(QtGui.QStyle.CE_PushButton, option, painter, self)
        if self.count() == 0:
            painter.drawText(option.rect,QtCore.Qt.AlignCenter,"Move Tabs \n in Here")


class TabBar(QtGui.QTabBar):
    dragStart = QtCore.pyqtSignal(int)
    clicked = QtCore.pyqtSignal()

    def __init__(self):
        super(QtGui.QTabBar, self).__init__()
        self.pos = None

    def tabInserted(self, index):
        super(TabBar, self).tabInserted(index)
        #self.setVisible(self.count() > 1)

    def tabRemoved(self, index):
        super(TabBar, self).tabRemoved(index)
        #self.setVisible(self.count() > 1)


    def mousePressEvent(self, mouseEvent):
        self.pos = mouseEvent.pos()
        QtGui.QTabBar.mousePressEvent(self, mouseEvent)
        self.clicked.emit()

    def mouseReleaseEvent(self, mouseEvent):
        self.pos = None
        QtGui.QTabBar.mouseReleaseEvent(self, mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.pos is not None:
            pos = mouseEvent.pos()
            if (self.pos-pos).manhattanLength() > 10:
                self.dragStart.emit(self.tabAt(self.pos))
