.. _script_tutorial:

Tutorial: Writing your own Script
=================================

    This tutorial is intended as a walk-through for the creation of a custom
    script in ARTview. It is also useful to understand how to use the ARTview
    package. It covers the basics of starting components and how to make them
    interact with each other.

The Basics
----------

    Artview runs with PyQt4, therefore before using any component you need to
    start a Qt application, but do that with artview, not directly in PyQt4. After defining what you want, you need to get it
    to run, otherwise windows will not respond. Your basic script will look like
    this:

    .. code-block:: python

        import artview

        # start pyqt
        app = artview.core.QtGui.QApplication([])

        ###########################
        #     do something        #
        ###########################

        # start program
        app.exec_() # lock until all windows are closed

    So what to do between those line?
    The simplest thing you can do is start a single instance
    :py:class:`~artview.core.core.Component` (or plugin), for instance
    :py:class:`~artview.components.Menu`:

    .. code-block:: python

        import artview

        # start pyqt
        app = artview.core.QtGui.QApplication([])

        # start Menu
        menu = artview.components.Menu(DirIn="/", name="Menu")

        # start program
        app.exec_() # lock until all windows are closed

    The above will open a Menu instance with name "Menu". Note: giving every new
    instance a different name is important for identifying them afterward.

    A slightly more useful component is a
    :py:class:`~artview.components.RadarDisplay`, but this needs a
    :py:class:`pyart.core.Radar` instance. Luckily Py-ART has examples we
    can use:

    .. code-block:: python

        import artview

        # start pyqt
        app = artview.core.QtGui.QApplication([])

        # get example radar from pyart
        import pyart
        radar = pyart.testing.make_target_radar()

        # start shared variables
        Vradar = artview.core.Variable(radar)
        Vfield = artview.core.Variable('reflectivity')
        Vtilt = artview.core.Variable(0) #  first sweep

        # start display
        display = artview.components.RadarDisplay(Vradar, Vfield, Vtilt,
                                       name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

    Now things start to get more complicated.
    The question is: Why we can't pass the radar instance directly to
    :py:class:`~artview.components.RadarDisplay`, but
    rather need to put it inside a
    :py:class:`~artview.core.core.Variable` instance?

    We want our display(s) to be able to share this radar instance with
    other components. In C programming this could be done using pointers, and
    here we employ a kind of equivalent for Python. More about that in the
    next section.

Shared Variables
----------------

    The use of shared variables is an important part of ARTview, all attributes
    that expect a :py:class:`~artview.core.core.Variable` instance are indicated
    by a capital V. Let's see how this works.

    Using :py:class:`~artview.components.Menu` we can open radar
    files and put them in :py:attr:`Menu.Vradar`. Since this is a visualization
    package we want to plot this files.

    This is simple. Instead of creating a new
    :py:class:`~artview.core.core.Variable` we take it from
    :py:class:`~artview.components.Menu` and pass it to
    :py:class:`~artview.components.RadarDisplay`:

    .. code-block:: python

        import artview

        # start pyqt
        app = artview.core.QtGui.QApplication([])

        # start Menu
        menu = artview.components.Menu(DirIn="/", name="Menu")

        # get Vradar from menu
        Vradar = menu.Vradar

        # start the other shared variables
        Vfield = artview.core.Variable('reflectivity')
        Vtilt = artview.core.Variable(0) #  first sweep

        # start display
        display = artview.components.RadarDisplay(Vradar, Vfield, Vtilt,
                                       name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

    So now we have the most simple script one would want.

    :py:class:`~artview.components.Menu` opens a file and
    :py:class:`~artview.components.RadarDisplay` plots it.

    But ARTview is much more powerful.
    Suppose you want to compare two fields of the same radar
    side-by-side. Simply add another display:

    .. code-block:: python

        import artview

        # start pyqt
        app = artview.core.QtGui.QApplication([])

        # start Menu
        menu = artview.components.Menu(DirIn="/", name="Menu")

        # DISPLAY 1

        # get Vradar from menu
        Vradar1 = menu.Vradar

        # start the other shared variables
        Vfield1 = artview.core.Variable('reflectivity')
        Vtilt1 = artview.core.Variable(0) #  first sweep

        # start display
        display1 = artview.components.RadarDisplay(Vradar1, Vfield1, Vtilt1,
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
        display = artview.components.RadarDisplay(Vradar2, Vfield2, Vtilt2,
                                       name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

    This script will open 1 :py:class:`~artview.components.Menu` and 2
    :py:class:`~artview.components.RadarDisplay` instance. Both show the same
    file, but different fields. 

    However, we have actually made a mistake. Because the Displays use
    different sweeps (Vtilt) - that is, they start with the same
    tilt but the user changes the sweep of the first - this will not change
    the second. We'd like them to change together.

    To get that behavior, we just need to change one line. Instead of
    creating a new Vtilt :py:class:`~artview.core.core.Variable`,
    use the old one:

    .. code-block:: python
        :emphasize-lines: 32-34

        import artview

        # start pyqt
        app = artview.core.QtGui.QApplication([])

        # start Menu
        menu = artview.components.Menu(DirIn="/", name="Menu")

        # DISPLAY 1

        # get Vradar from menu
        Vradar1 = menu.Vradar

        # start the other shared variables
        Vfield1 = artview.core.Variable('reflectivity')
        Vtilt1 = artview.core.Variable(0) #  first sweep

        # start display
        display1 = artview.components.RadarDisplay(Vradar1, Vfield1, Vtilt1,
                                        name="DisplayRadar")

        # DISPLAY 2

        # get Vradar from menu
        Vradar2 = menu.Vradar
        # or equivalently
        Vradar2 = Vradar1

        # start the other shared variables
        Vfield2 = artview.core.Variable('radial_velocity')
        # wrong: Vtilt2 = artview.core.Variable(0)
        # correct:
        Vtilt2 = Vtilt1

        # start display
        display2 = artview.components.RadarDisplay(Vradar2, Vfield2, Vtilt2,
                                        name="DisplayRadar")

        # start program
        app.exec_() # lock until all windows are closed

Graphical Tools
---------------

    In the previous section we made a script with two displays sharing Vradar and
    Vtilt but not sharing Vfield, we will leave this as an exercise to explore
    other potential sharing configurations.

    There is the possibility that you don't know the kind of sharing that you want.
    AND you don't want to keep changing your script every time. There is a tool
    that allows the user to modify the sharing behavior of Components,
    that is to link/unlink variables between components (e.g. Displays).
    This is :py:class:`~artview.components.LinkSharedVariables`. To get it running
    just add the following line to your script:

    .. code-block:: python

        control = artview.components.LinkSharedVariables()

    Now we got 4 independent windows floating around our Desktop.
    To avoid this :py:class:`~artview.components.Menu` has the
    method :py:func:`~artview.components.Menu.addLayoutWidget`,
    which offers the ability to put additional Components inside the Menu window.

    For instance like this:

    .. code-block:: python

        # start Menu
        menu = artview.components.Menu(DirIn="/", name="Menu")

        # start Control
        control = artview.components.LinkSharedVariables()

        # put control inside Menu
        menu.addLayoutWidget(control)

    Ok, maybe you don't want to put components inside menu. Your problem is
    that you would like to close all windows at once and not each individually.
    For this we leverage the fact that PyQt closes all children instances (windows)
    of an existing (parent) window. A good policy is to pass menu as the parent
    for all other components (components always accept a parent key)

    For instance:

    .. code-block:: python

        # start Menu
        menu = artview.components.Menu(DirIn="/", name="Menu")

        # start Control
        control = artview.components.LinkSharedVariables(parent=menu)

    Yay, we know how to close windows! What about opening new ones?

    This is a bit more complicated. Some components can just be started as
    a priori in the script. But some components like
    :py:class:`~artview.components.RadarDisplay` and
    :py:class:`~artview.components.LinkSharedVariables` have the `GUIstart`
    method and can be started by the user at execution time. To do this, use the
    Menu method :py:func:`~artview.components.Menu.addComponent`. For
    instance

    .. code-block:: python

        # start Menu
        menu = artview.components.Menu(DirIn="/", name="Menu")

        # start Control
        menu.addComponent(artview.components.RadarDisplay)

    Now you find Display in the components sub-menu and can start a new one
    there.

Plug-ins
--------

    Plug-ins are defined as user specific components that don't interfere in
    the over all working of ARTview. They are found in the :artview:`artview/plugins`
    folder and accessed in :py:mod:`artview.plugins`. For specific
    information on what each plug-in does please see the reference-manual.
    By default we ask that all plug-ins have the
    `GUIstart` method. Therefore to access them at execution time add the
    following at your script:

    .. code-block:: python

        # start Menu
        menu = artview.components.Menu(DirIn="/", name="Menu")

        # add plugins
        for plugin in artview.plugins._plugins:
            menu.addComponent(plugin)

    For more on Plug-ins see :ref:`plugin_tutorial`

Official Scripts
----------------

    ARTview has a :artview:`artview/scripts` folder where some "official" scripts are
    found, including the standard startup that is executed with the
    ``artview`` command. It's not particularly recommended to put your
    script there as some details on how that folder works may change with time.
    If you'd like to see your script included in the future, please submit an
    `Issue <https://github.com/nguy/artview/issues>`_
    at the code repository or introduce a
    `pull request <https://help.github.com/articles/using-pull-requests/>`_
    of your modified code.

    However, if you want to put your script there you should do two things:

    * Put your script inside a run function
      ``def run(DirIn='./', filename=None, field=None):``

    * Don't import artview, but its parts relatively, that is:
      ``from .. import core, components, plugins``

    Doing this you may find your script according to its file name in
    :py:mod:`artview.scripts`
