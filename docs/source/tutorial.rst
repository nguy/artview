Tutorial: Writing your own Script
=================================

    This Section is intended as a walkthrough for the creation of custom script in
    artview. It is also usefull to undertand how to use artview package. It covers
    the basics of starting components and how to make they interact with each
    other.

The Basics
----------

    Artview run over PyQt, therefore before before using any component you need to
    start a PyQt aplication. After defining what you want, you need to get it to
    run, otherwise windows will not respond. Your basic script look like this

    .. code-block:: python

        import artview
        from PyQt4 import QtGui

        # start pyqt
        app = QtGui.QApplication()

        ###########################
        #     do something        #
        ###########################

        # start program
        app.exec_() # lock until all windows are closed

    So the whole question is about what do between those line. The most simple
    thing you can do is start a single component (or plugin), for instance
    :py:class:`~artview.components.Menu`:

    .. code-block:: python

        import artview
        from PyQt4 import QtGui

        # start pyqt
        app = QtGui.QApplication()

        # start Menu
        menu = Menu(DirIn="/", name="Menu")

        # start program
        app.exec_() # lock until all windows are closed

    This will open a Menu instance with name "Menu", giving every new instance a
    diferent name is important for identifing them afterwards.

    A slightly more useful component is a :py:class:`~artview.components.Display`,
    but this new a :py:class:`pyart.core.Radar` instance. Luckly Py-ART has some
    exemple we can use:

    .. code-block:: python

        import artview
        from PyQt4 import QtGui

        # start pyqt
        app = QtGui.QApplication()

        # get exemple radar from pyart
        import pyart
        radar = pyart.testing.make_target_radar()

        # start shared variables
        Vradar = artview.core.Variable(radar)
        Vfield = artview.core.Variable('reflectivity')
        Vtilt = artview.core.Variable(0) #  first sweep

        # start display
        display = artview.core.Display(Vradar, Vfield, Vtilt, name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

    So here things start to get more complicated, why we couldn't pass radar to
    :py:class:`~artview.components.Display`, but rather need to put it inside
    :py:class:`~artview.core.core.Variable`? The thing we want display to be
    able to share this radar with other components, in C this could be done
    using points, this is kind of an equivalent for python.

Shared Variables
----------------

    The use of shared variables is a important part of ARTview, all variables
    that expect :py:class:`~artview.core.core.Variable` are marked with a capital
    V. Let see how this work, :py:class:`~artview.components.Menu` has the
    possibility of opennig radar files and put them in :py:class:`Menu.Vradar`, we
    want to use display to plot this files. This is simple instead of creating a
    new :py:class:`~artview.core.core.Variable` we take it from
    :py:class:`~artview.components.Menu` and pass to
    :py:class:`~artview.components.Display`:

    .. code-block:: python

        import artview
        from PyQt4 import QtGui

        # start pyqt
        app = QtGui.QApplication()

        # start Menu
        menu = Menu(DirIn="/", name="Menu")

        # get Vradar from menu
        Vradar = menu.Vradar

        # start the other shared variables
        Vfield = artview.core.Variable('reflectivity')
        Vtilt = artview.core.Variable(0) #  first sweep

        # start display
        display = artview.core.Display(Vradar, Vfield, Vtilt, name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

