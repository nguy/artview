.. _plugin_tutorial:

Tutorial: Writing your own Plugin
=================================

    This tutorial presents information for any one wanting to create a
    custom plug-in for ARTview. Plug-ins are just a special form of a Component.
    ARTview is all based on Components, so this information is important
    to anyone (user or developer) wanting to understand ARTview.

    Plug-ins can be added by anyone and are encouraged in this open source
    environment. There are a few rules the developers have established in the
    course of setting up the ARTview infastructure (see below). There are no
    limits on how to program your plug-in, for that you can use any of the
    tools available in the Python programming language.

    That said, we do suggest that you start a `Github Issue
    <https://github.com/nguy/artview/issues>`_ as the intended tool may be
    in development or we could provide some hard-learned advice or
    ideas on how to solve the problem.


The Basics
----------

    To allow the integration of plug-ins in ARTview the developers have had
    to make some rules to follow. Otherwise you risk the operability of your
    plug-in or in worse ARTview. Here are the requirements:

    * Plug-ins must be located in one single file in
      :artview:`artview/plugins` ending in **.py**.

    * The plug-in file must contain a variable ``_plugins``, this is a list of
      plug-ins, normally just one.

    * Plug-ins are always a class, moreover they are always child classes
      of :py:class:`~artview.core.core.Component`. Like this:
      ``class MyPlugin(core.Component):``

    * Plug-ins have no mandatory argument and can be started like this:
      ``myplugin = MyPlugin()``

    * If plug-ins must interact with other ARTview components they use
      :py:class:`~artview.core.core.Variable`, not direct call.

    * Plug-ins must have a GUIstart class method, like this:

      .. code-block:: python

          @classmethod
          def guiStart(self, parent=None):
              ################################
              #    Define Call Parameters    #
              ################################
              return self(...), True/False

    * Last in order to avoid future problems get :py:mod:`~PyQt4.QtCore` and :py:mod:`~PyQt4.QtGui` modules
      from :py:mod:`artview.core` and not directly for :py:mod:`PyQt4`, even if this is still
      only an alias.

    Next we'll discuss how these are used in creating a plug-in.

The Plug-in File
----------------

    ARTview expects all plug-in files to be present in :artview:`artview/plugins`
    and with a **.py** extension (e.g **my_plugin.py**) and to be importable into
    Python. There must also exist a (possibly empty) list of plug-ins in the
    attribute ``_plugins`` (e.g ``_plugins = [MyPlugin]``. Only plug-ins present
    in such list are added to :py:mod:`artview.plugins`. Files starting with an
    underscore(_) are ignored. This allows the separation of a plug-in into
    multiple file or even folders if needed.

    As the file **my_plugin.py** is imported inside ARTview you should not
    import it in an absolute sense, but rather make this a relative import. An
    example is instead of ``from artview import core, components`` do
    ``from .. import core, components``.

The Component Class
-------------------

    Plug-ins are a special case of Components, therefore it must work
    just like one. The first requirement being that it is a class derived
    from :py:class:`~artview.core.core.Component`. This class in turn
    inherits :py:class:`PyQt4.QtGui.QMainWindow`, so you can use any PyQt
    method of a QMainWindow while building your component. Accordingly,
    there is just one difference from
    :py:class:`~PyQt4.QtGui.QMainWindow` and
    :py:class:`~artview.core.core.Component`:

    :py:class:`~artview.core.core.Component` passes keyPressEvents to its
    parent, while :py:class:`~PyQt4.QtGui.QMainWindow` mostly ignores them.

    Another aspect of :py:class:`~artview.core.core.Component` is that
    it always has a string name. This has two functions: First, it will
    define the window title; and Second, ARTview may use it to identify
    different instances of the same component. Therefore it is important
    for the user to have the potential to define the name at initialization.
    But there is a helpful standard to follow, the common practice of
    capitilization relatively common in Python programming, along with no
    underscores. For instance ``def __init__(..., name="MyPlugin", ...):``.

    Further important points are:

    * As of now ARTview keeps a list of initialized components in
      :py:attr:`artview.core.core.componentsList`.
    * :py:class:`~artview.core.core.Component` has the methods
      :py:func:`~artview.core.core.Component.connectSharedVariable` and
      :py:func:`~artview.core.core.Component.disconnectSharedVariable`, which
      will be explained in the next section.

    Finally it is our policy that all components are able to stand on their own.
    One must be able to execute it as the only ARTview component, even if it
    depends of other ones to work properly. Parallel to that, starting a
    component from another component is not prohibited, but it's strongly
    discouraged. Component iteration shall be performed mainly using shared
    variables.

Shared Variables
----------------

    Before using shared variables it is useful to know how they work on
    the user side. For that :ref:`script_tutorial` may help.

    In defining a shared variable you should have three things clear in
    your mind:

    1. the name (starting with capital V)
    2. the function it will perform
    3. the type of value it will hold

    Examples of shared variable are present in the :ref:`shared_variable`.
    If your variable is already present in that list, use the same name.

    For every shared variable a component uses, you must define the response
    if the value is changed. An important point to understand here
    is that you do NOT have absolute control a variable, any other part of
    ARTview may change the value of this shared variable. Hence, the "shared"
    part.

    By causing a change to the variable in your class, the variable will
    receive the "ValueChange" signal and executes some function in response.
    This is called the variable slot and it looks like this:

    .. code-block:: python

        def NewMyVar(self, var, strong):

    To define the slot of every shared variable define a dictionary named
    sharedVariables in ``__init__``. The key is the name of a variable
    (e.g. ``"VmyVar"``) and the value its slot (e.g. ``self.ŃewMyVar``). You
    may also assign the value ``None`` to signal that the plug-in does not
    need to respond to "ValueChanged".

    You must also set an attribute with the instance of
    :py:class:`~artview.core.core.Variable` (e.g
    ``self.VourVar = core.Variable()``).

    After those two steps call
    :py:func:`~artview.core.core.Component.connectAllVariables` to connect
    your variables to the slots. You also have access to the methods
    :py:func:`~artview.core.core.Component.connectSharedVariable` to connect a
    single variable,
    :py:func:`~artview.core.core.Component.disconnectSharedVariable` to
    disconnect a single variable and
    :py:func:`~artview.core.core.Component.disconnectAllVariables` to
    disconnect all variables.

    To access the value of a variable use the
    :py:attr:`~artview.core.core.Variable.value` attribute. To change the value
    use the :py:func:`~artview.core.core.Variable.change` method. Once ``change``
    is called, the value is updated and after that the slot of a shared variable
    is called receiving thre arguments: the variable, the new value and the
    strong flag. Remember that when the slot is executed the value is already
    changed. Never do ``var.change(value)``, otherwise you run the risk of an
    infinite loop. The final argument is a boolean value indicating if a
    strong or weak change is requested. True is the default value. If the flag
    ``strong`` is False this avoids any expensive computations in your slot,
    like for instance replotting some data.

    Finally a brief orientation on shared variables:

    * There are two way of getting a shared variable: ``__init__`` receives it
      or ``__init__`` initializes it. A variable that is received is considered
      to already have a valid value, an initialized variable must leave
      ``__init__`` with a valid value.
    * If for some reason one needs to change the value of a initialized
      variable inside ``__init__`` do that with a weak change (```strong``` set
      to False), unless there is a really good reason for not doing this.
    * If for some reason you need to trigger the slot of a shared variable
      inside ``__init__`` do that by direct call. Do not use the variable to
      emit a signal unless there is a really good reason for doing so.

Graphical Start
---------------

    A graphical start is mandatory for plug-ins. A class method called
    ``GUIstart`` that receives an optional parent argument
    and returns two values: an initialized instance of the the plug-in and a
    boolean value. The boolean value will be used by
    :py:class:`~artview.components.Menu`. If False, the menu instance will
    execute :py:func:`~artview.components.Menu.addLayoutWidget`, otherwise the
    plug-in will be an independent window. The main difficulty in writing a
    method is defining the arguments needed for initializing your plug-in.

    Here are some tools in ARTview to hopefully help:

    * :py:class:`artview.core.common._SimplePluginStart` will ask the user for
      a name and if the plug-in should be an independent window. Use like
      this:

    .. code-block:: python

        def guiStart(self, parent=None):
            kwargs, independent = core.common._SimplePluginStart(
                                        "CalculateAttenuation").startDisplay()
            kwargs['parent'] = parent
            return self(**kwargs), independent

    * :py:class:`artview.core.choose_variable.VariableChoose` will present the
      user a tree view of the current components and its shared variables,
      allowing the selection of one instance.

      This is a more historical request, but as for now it is still useful and
      therefore still mandatory.


Example
-------

    Combining the above tutorial, here is a skeleton outline for your Plug-in:

    .. code-block:: python

        # Load the needed packages
        from .. import core, components

        class MyPlugin(core.Component):

            @classmethod
            def guiStart(self, parent=None):
                kwargs, independent = core.common._SimplePluginStart(
                                                    "MyPlugin").startDisplay()
                kwargs['parent'] = parent
                return self(**kwargs), independent

            def __init__(self, VmyVar=None, name="MyPlugin", parent=None):

                if VmyVar is None:
                    valid_value = "something"
                    self.VmyVar = core.Variable(valid_value)
                else:
                    self.VmyVar = VmyVar

                self.sharedVariables = {"VmyVar": self.NewMyVar}
                self.connectAllVariables()

                ################################
                #          Build Plug-in       #
                ################################

                #  don`t do: self.VmyVar.change(value, True)
                #  but rather: self.VmyVar.change(value, False)

                #  don`t do: self.VmyVar.emit(...)
                #  but rather: self.NewMyVar(...)

                # show plugin
                self.show()

            ################################
            #         Other Methods        #
            ################################

            def NewMyVar(self, variable, strong):
                print self.VmyVar.value  #  => "something else"

        _plugins=[MyPlugin]





