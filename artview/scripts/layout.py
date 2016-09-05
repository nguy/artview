"""
standard.py

Driver function that creates two ARTView displays.
This is the default start for ARTView
"""
import os
import sys

from ..core import Variable, QtGui, QtCore, componentsList
from ..components import RadarDisplay, Menu, LevelButtonWindow, \
    LinkSharedVariables, SelectRegion, Window, FileNavigator
from ._parse_field import _parse_field
from ._common import startMainMenu
from .. import view

list_widget={}

class View(QtGui.QTabWidget):
    isCurrent = False

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
        self.show()

    def setCurrent(self):
        self.emit(QtCore.SIGNAL("turnCurrent"), self)
        self.isCurrent = True
        self.update()

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
        #print drag.target()

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
            comp_dict = dict([(c.__repr__(),c) for c in componentsList])
            if text in comp_dict:
                widget = comp_dict[text]
                self.addTab(widget,widget.name)
                self.setCurrent()

    def closeTab(self, idx):
        self.widget(idx).close()
        self.widget(idx).deleteLater()

    def minimumSizeHint(self):
        hint = super(View, self).minimumSizeHint()
        if hint.width() < 80:
            hint.setWidth(80)
        if hint.height() < 40:
            hint.setHeight(40)
        return hint


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

class Window2(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.widgets = {}
        self.currentMindex = ()
        self.layoutTree = {}
        self.layoutTree[()] = QtGui.QSplitter(self)
        self.layoutTree[()].setOrientation(QtCore.Qt.Horizontal)
        self.setCentralWidget(self.layoutTree[()])

        self.menubar = self.menuBar()
        layoutmenu = self.menubar.addMenu('&Layout')

        layoutmenu.addAction('Split Vertical', self.splitVertical)
        layoutmenu.addAction('Split Horizontal', self.splitHorizontal)
        layoutmenu.addAction('Add View', self.addView)
        layoutmenu.addAction('Close Current View', self.closeCurrentView)
        layoutmenu.addAction('Close Inactive Views', self.closeInactiveView)

        addmenu = self.menubar.addMenu('&Add')
        action = QtGui.QAction('New Window', self)
        action.triggered.connect(self.addWindow)
        addmenu.addAction(action)

        self.addView()

        self.show()
        list_widget[self.__repr__()] = self

    def splitVertical(self):
        if self.currentMindex is None:
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
        if self.currentMindex is None:
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

    def mousePressEvent(self, event):
        if ((not False) and
            event.button() == QtCore.Qt.RightButton):
            menu = QtGui.QMenu(self)
            for action in self.menubar.actions():
                menu.addAction(action)
            menu.exec_(self.mapToGlobal(event.pos()))
        super(Window, self).mousePressEvent(event)

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
        print "new windows"
        Window()



def run(DirIn=None, filename=None, field=None):
    """
    standard artview execution

    It has :py:class:`~artview.components.Menu`
    with :py:class:`~artview.components.LinkSharedVariables`,

    2 :py:class:`~artview.components.RadarDisplay`,

    graphical start for:
        * All :py:class:`~artview.plugins`
        * :py:class:`~artview.components.RadarDisplay`
        * :py:class:`~artview.components.LinkSharedVariables`
        * :py:class:`~artview.components.SelectRegion`
    """

    view.startWindow()

    if DirIn is None:  # avoid reference to path while building documentation
        DirIn = os.getcwd()

    menu = FileNavigator()

    Vradar = menu.Vradar

    # handle input
    if field is None:
        import pyart
        field = pyart.config.get_field_name('reflectivity')
        field = _parse_field(Vradar.value, field)

    # start Displays
    Vtilt = Variable(0)
    plot1 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display1",
                         parent=view.MainWindow)
    plot2 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display2",
                         parent=view.MainWindow)

    # start ComponentsControl
    control = LinkSharedVariables()
    control.setComponent0(plot1.name)
    control.setComponent1(plot2.name)

    # add control to Menu
    #view.MainMenu.addLayoutWidget(control)
    window = view.MainWindow
    window.splitHorizontal()
    window.splitVertical()

    window.layoutTree[(0,1,0)].addTab(control,control.name)
    window.layoutTree[(0,0)].addTab(menu,menu.name)
    window.layoutTree[(0,1,1)].addTab(plot1,plot1.name)
    window.layoutTree[(0,1,1)].addTab(plot2,plot2.name)

    window.layoutTree[(0,1,0)].fix=True
    window.layoutTree[(0,1,0)].setSizePolicy(0,0)
    window.layoutTree[(0,1,0)].sizePolicy().setHorizontalStretch(1)
    window.layoutTree[(0,1,0)].sizePolicy().setVerticalStretch(1)
    window.layoutTree[(0,1,1)].sizePolicy().setHorizontalStretch(3)
    window.layoutTree[(0,1,1)].sizePolicy().setVerticalStretch(3)

    window.showMaximized()
    geom =  QtGui.QDesktopWidget().screenGeometry()
    window.layoutTree[(0,)].setSizes([window.layoutTree[(0,0)].minimumSize().height(),geom.height()-window.layoutTree[(0,0)].minimumSize().height()])
    window.layoutTree[(0,1)].setSizes([window.layoutTree[(0,1,0)].minimumSize().width(),geom.width()-window.layoutTree[(0,1,0)].minimumSize().width()])

    # start program
    view.execute()
    print("You used ARTView. What you think and what you need of ARTView? "
          "Send your comment to artview-users@googlegroups.com")
