Tutorial: Writing your own Script
=================================

    This Section is intended as a walk-through for the creation of custom
    script in ARTview. It is also useful to understand how to use the ARTview
    package. It covers the basics of starting components and how to make they
    interact with each other.

The Basics
----------

    Artview run over PyQt, therefore before using any component you need to
    start a PyQt application. After defining what you want, you need to get it
    to run, otherwise windows will not respond. Your basic script look like
    this:

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

    So the whole question is about what to do between those line. The most
    simple thing you can do is start a single
    :py:class:`~artview.core.Component` (or plugin), for instance
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

    This will open a Menu instance with name "Menu", giving every new
    instance a different name is important for identifying them afterward.

    A slightly more useful component is a
    :py:class:`~artview.components.Display`, but this need a
    :py:class:`pyart.core.Radar` instance. Luckily Py-ART has some example we
    can use:

    .. code-block:: python

        import artview
        from PyQt4 import QtGui

        # start pyqt
        app = QtGui.QApplication()

        # get example radar from pyart
        import pyart
        radar = pyart.testing.make_target_radar()

        # start shared variables
        Vradar = artview.core.Variable(radar)
        Vfield = artview.core.Variable('reflectivity')
        Vtilt = artview.core.Variable(0) #  first sweep

        # start display
        display = artview.core.Display(Vradar, Vfield, Vtilt,
                                       name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

    So here things start to get more complicated, the question is: why we
    can't pass radar to :py:class:`~artview.components.Display`, but
    rather need to put it inside :py:class:`~artview.core.core.Variable`?
    The point is that we want display to be able to share this radar with
    other components, in C this could be done using pointers, this is kind of
    an equivalent for python, more about that in the next section.

Shared Variables
----------------

    The use of shared variables is an important part of ARTview, all attributes
    that expect a :py:class:`~artview.core.core.Variable` instance are marked
    with a capital V. Let see how this work, lets try the following:
    :py:class:`~artview.components.Menu` has the possibility of opening radar
    files and put them in :py:attr:`Menu.Vradar`, we want to use display to
    plot this files. This is simple: instead of creating a new
    :py:class:`~artview.core.core.Variable` we take it from
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
        display = artview.core.Display(Vradar, Vfield, Vtilt,
                                       name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

    So now we have the most simple script one would want.
    :py:class:`~artview.components.Menu` opens a file and
    :py:class:`~artview.components.Display` plots it. But ARTview is much more
    powerful, suppose you want the following: Compare side to side two fields
    of the same radar. One can just add an other display

    .. code-block:: python

        import artview
        from PyQt4 import QtGui

        # start pyqt
        app = QtGui.QApplication()

        # start Menu
        menu = Menu(DirIn="/", name="Menu")

        # DISPLAY 1

        # get Vradar from menu
        Vradar1 = menu.Vradar

        # start the other shared variables
        Vfield1 = artview.core.Variable('reflectivity')
        Vtilt1 = artview.core.Variable(0) #  first sweep

        # start display
        display1 = artview.core.Display(Vradar1, Vfield1, Vtilt1,
                                        name="DisplayRadar")

        # DISPLAY 2

        # get Vradar from menu
        Vradar2 = menu.Vradar
        # or equivalently
        Vradar2 = Vradar1

        # start the other shared variables
        Vfield2 = artview.core.Variable('radial_velocity')
        Vtilt2 = artview.core.Variable(0) #  first sweep

        # start display
        display = artview.core.Display(Vradar2, Vfield2, Vtilt2,
                                       name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

    This script will open 1 :py:class:`~artview.components.Menu` and 2
    :py:class:`~artview.components.Display`, both show the same file but
    different fields. But we have actually made a mistake, because the two
    Displays are also with different sweeps, that is, they start with the same
    one but if the user changes the sweep of the first this will not change
    the second, and we would want it to change together. To get that behavior
    we just need to change 1 line: don't create a new Vtilt
    :py:class:`~artview.core.core.Variable`, use the old one

    .. code-block:: python
        :emphasize-lines: 32-34

        import artview
        from PyQt4 import QtGui

        # start pyqt
        app = QtGui.QApplication()

        # start Menu
        menu = Menu(DirIn="/", name="Menu")

        # DISPLAY 1

        # get Vradar from menu
        Vradar1 = menu.Vradar

        # start the other shared variables
        Vfield1 = artview.core.Variable('reflectivity')
        Vtilt1 = artview.core.Variable(0) #  first sweep

        # start display
        display1 = artview.core.Display(Vradar1, Vfield1, Vtilt1,
                                        name="DisplayRadar")

        # DISPLAY 2

        # get Vradar from menu
        Vradar2 = menu.Vradar
        # or equivalently
        Vradar2 = Vradar1

        # start the other shared variables
        Vfield2 = artview.core.Variable('radial_velocity')
        # wrong: Vtilt2 = artview.core.Variable(0) #  first sweep
        # correct:
        Vtilt2 = Vtilt1

        # start display
        display2 = artview.core.Display(Vradar2, Vfield2, Vtilt2,
                                        name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

Graphical Tools
---------------

    In the last section we made a script with two displays sharing Vradar and
    Vtilt but not sharing Vfield, we will let to you to explore the other
    possible sharing configurations. But there is also the possibility that
    you don't know the kind of sharing that you want and you don't want to
    keep changing your script every time. For that there is a tool that allow
    the user to change the sharing behavior of
    Components, that is connect/disconnect variables
    between components. This is the
    :py:class:`~artview.components.ComponentsControl` and to get it running
    just add the following line to your script

    .. code-block:: python

        control = artview.components.ComponentsControl()

    The Problem here is that now we got 4 independent windows floating around
    our Desktop, to avoid that :py:class:`~artview.components.Menu` has the
    method :py:class:`~artview.components.Menu.addLayoutWidget`, this allow
    putting other Components inside Menu, for instance like this:

    .. code-block:: python

        # start Menu
        menu = Menu(DirIn="/", name="Menu")

        # start Control
        control = artview.components.ComponentsControl()

        # put control inside Menu
        menu.addLayoutWidget(control)

    The only problem here is that you lose the close button for `control`, to
    over come that menu has the layout sub-menu that allow the user to close
    components inside the main menu.

    Ok, may be you don't want to put components inside menu, your problem is
    you want to close all windows at once, and not having to close each one.
    To get that we use that PyQt closes all children windows of a window when
    this is closed, so a good police is to pass menu as parent for all other
    components (components always accept a parent key), for instance

    .. code-block:: python

        # start Menu
        menu = Menu(DirIn="/", name="Menu")

        # start Control
        control = artview.components.ComponentsControl(parent=menu)

    So we know how to close windows, what about opening new ones. This is more
    complicated, as for now some components can just be started a priory in
    the script, but some other like :py:class:`~artview.components.Display`
    and :py:class:`~artview.components.ComponentsControl` have the `GUIstart`
    method and can be started by the user at execution time, for that use the
    Menu method :py:class:`~artview.components.Menu.addComponentMenuItem`, for
    instance

    .. code-block:: python

        # start Menu
        menu = Menu(DirIn="/", name="Menu")

        # start Control
        menu.addComponentMenuItem(artview.components.Display)

    Now you may found Display at the components sub-menu and start a new one
    there.

Plug-ins
--------

    Plug-ins are define as user specific components that don't interfere in
    the over all working of ARTview, they are all found in the :file:`artview/plugins`
    folder and accessed in :py:class:`artview.plugins`. For specific
    information on what each plug-in does please see the reference-manual, I
    just want to say that by default we ask that all plug-ins have the
    `GUIstart` method, therefore to access them at execution time add the
    following at your script

    .. code-block:: python

        # start Menu
        menu = Menu(DirIn="/", name="Menu")

        # add plugins
        for plugin in artview.plugins._plugins:
            menu.addComponent(plugin)

Official Scripts
----------------

    ARTview has a :file:`artview/scripts` folder where some "official" scripts are
    found, including the standard one that is executed with the
    ``python -m artview`` command. We don't particularly recommend putting your
    script there as some details on how that folder work may change with time.
    However as for now if you want to put it there you should do two things:

    * Put your script inside a run function
      ``def run(DirIn='./', filename=None, field=None):``

    * Don't import artview, but its parts relatively, that is:
      ``from .. import core, components, plugins``

    Doing this you may found your script according to its file name in
    :py:class:`artview.scripts`
