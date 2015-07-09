.. _plugin_tutorial:

Tutorial: Writing your own Plugin
=================================

    This Section is intended to present some points of awareness for any one
    wanting to create a custom plug-in for ARTview. As plug-ins are just a
    special form of Component and as ARTview is all based in Components this
    is also important to anyone (user or programmer) wanting to understand
    ARTview. Of course we can not say you how to program your plug-in, for
    that you can use all the tools available in the python programming
    language, we however suggest before starting programing let us know your
    intension and needs though our
    `GitHub issues page <https://github.com/nguy/artview/issues>`_, we may
    provide some valuable information and ideas on how to solve the problem.


The Basics
----------

    To allow the integration of plug-ins in ARTview we have made some rules
    that must be follow, in the risk of your plug-in or in the worse case
    ARTview not working. I will list those here and after that I will instruct
    on how to follow them.

    * Plug-ins must be located in one single file in
      :artview:`artview/plugins` ending in **.py**.

    * The plug-in file must contain a variable ``_plugins``, this is a list of
      plug-ins, normally just one.

    * Plug-ins are always a class, moreover they are always child classes
      of :py:class:`~artview.core.core.Component`. Like this: 
      ``class MyPlugin(core.Component):``

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

The Plug-in File
----------------

    ARTview expect all files present in :artview:`artview/plugins` and ending
    in **.py** (e.g **my_plugin.py**) to be importable into python and have a
    (possibly empty) list of plug-ins in the attribute ``_plugins`` (e.g
    ``_plugins = [MyPlugin]``. Only plug-ins present in such list are added
    to :py:mod:`artview.plugins`. File starting with underscore are ignored,
    this allow you to separate your plug-in in multiple file or even folders
    if needed.

    As the file **my_plugin.py** is imported inside ARTview you should not
    import it in absolute, but rather make a relative imports. That is instead
    of ``from artview import core, components`` do ``from .. import core,
    components``.

The Component Class
-------------------

    Plug-ins are just a especial case of components, therefore it must work
    just like one. For that first thing is that its is a class derived
    from :py:class:`~artview.core.core.Component`. This class for its turn
    inherit :py:class:`PyQt4.QtGui.QMainWindow`, so you can use any PyQt
    method of a QMainWindow while building your component, in this point of
    view there is just one difference from
    :py:class:`~PyQt4.QtGui.QMainWindow` and
    :py:class:`~artview.core.core.Component`:
    :py:class:`~artview.core.core.Component` passes keyPressEvents to its
    parent, while :py:class:`~PyQt4.QtGui.QMainWindow` mostly ignore it.

    An other particularity of :py:class:`~artview.core.core.Component` is that
    it always has a name, this is a string and have two function first it will
    define the window title and second ARTview may use it to identify
    different instances of the same component. It is important that the user
    has the possibility of defining the name at initialization, but there
    shall also be a standard, for instance
    ``def __init__(..., name="MyPlugin", ...):``. Further important points
    are:

    * As now ARTview keep a list of initialized components in
      :py:attr:`artview.core.core.componentsList`.
    * :py:class:`~artview.core.core.Component` has the methods
      :py:func:`~artview.core.core.Component.connectSharedVariable` and
      :py:func:`~artview.core.core.Component.disconnectSharedVariable`, those
      will be explained in the next section.

    Finally its our policy that all components are able to stand on its own,
    one must be able to execute it as the only ARTview component, even if it
    depends of other ones to work properly. Parallel to that, starting a
    component from another component is not prohibited, but it's strongly
    unrecommended. Component iteration shall be performed mainly using shared
    variables.

Shared Variables
----------------

    First of all before programing with shared variables you should know how
    they work in the user side, for that :ref:`script_tutorial` may help.

    In defining your shared variable you should have three things clear in
    your mind: it name (starting with capital V), it function, and what kind
    of value it holds. Examples of some shared variable are present in
    the :ref:`shared_variable`. If your variable is already present in that
    list, use the same name.

    For every shared variable a component uses you must define how you want it
    to respond if the value is change, one important point to understand here
    is that you do not control a variable, any other part of ARTview shall
    change the value of your variable. What happens them it that your class
    will receive the "ValueChange" signal and will be able to execute a
    function to respond to that, that is the variable slot and it looks like
    this:

    .. code-block:: python

        def newMyVar(self, var, value, strong):

    To define what is the slot of every shared variable define in ``__init__``
    a dictionary named sharedVariables: the key is the name of a variable
    (e.g. ``"VmyVar"``) and the value its slot (e.g. ``self.newMyVar``), you
    may also give the value ``None`` to signalize that our plug-in does not
    need to respond to "ValueChanged". You must also set to the attribute an
    instance of :py:class:`~artview.core.core.Variable` (e.g
    ``self.VourVar = core.Variable()``). After those two steps call
    :py:func:`~artview.core.core.Component.connectAllVariables` to connect
    your variables to the slots. You also have access to the methods
    :py:func:`~artview.core.core.Component.connectSharedVariable` to connect a
    single variable,
    :py:func:`~artview.core.core.Component.disconnectSharedVariable` to
    disconnect a single variable and
    :py:func:`~artview.core.core.Component.disconnectAllVariables` to
    disconnect all variables.

    To access the value of a variable use the
    :py:attr:`~artview.core.core.Variable.value` attribute and to change it the
    :py:func:`~artview.core.core.Variable.change` method. Once change is
    called the value is updated and after that the slot of a shared variable
    is called receiving 3 arguments: the variable, the new value and the
    strong flag. Remember that when the slot is executed the value is already
    changed, never do ``var.change(value)`` in the risk of an infinite loop.
    The final argument is a boolean value defining if this is a strong or weak
    change. True is the standard value, otherwise if the flag ``strong`` is
    False avoid making any expensive computation in your slot, like for
    instance reploting some data.

    Finally here are some orientation on shared variables:

    * There are two way of getting a shared variable: ``__init__`` receives it
      or ``__init__`` initialize it. A variable that is received is consider
      to already have a valid value, an initialized variable must leave
      ``__init__`` with a valid value.
    * If for some reason one need to change the value of a initialized
      variable inside ``__init__`` do that with a weak changes, unless you
      have a really good reason for not doing so.
    * If for some reason you need to trigger the slot of a shared variable
      inside ``__init__`` do that by direct call, do not use the variable to
      emit a signal unless you have a really good reason for doing so.

Graphical Start
---------------

    For plug-ins is mandatory that they have a graphical start, this is a
    class method called ``GUIstart`` that receive an optional parent argument
    and returns two value: an initialized instance of the the plug-in and a
    boolean value. This boolean value will be used by
    :py:class:`~artview.components.Menu`, if False menu will
    execute :py:func:`~artview.components.Menu.addLayoutWidget`, otherwise the
    plug-in will be an independent window. The main difficulty in writing this
    method is defining the arguments need for initializing your plug-in, we
    will not say how you should do this, but there are some tools to help:

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
      allowing it to select one.


Example
-------

    Uniting all instructions of this tutorial here is an base skeleton for your Plug-in

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

                self.sharedVariables = {"VmyVar": self.newMyVar}
                self.connectAllVariables()

                ################################
                #          Build Plug-in       #
                ################################

                #  don`t do: self.VmyVar.change(value, True)
                #  but rather: self.VmyVar.change(value, False)

                #  don`t do: self.VmyVar.emit(...)
                #  but rather: self.newMyVar(...)

                # show plugin
                self.show()

            ################################
            #         Other Methods        #
            ################################

            def newMyVar(self, variable, value, strong):
                print self.VmyVar.value  #  => "something else"
                print value #  => "something else"

        _plugins=[MyPlugin]





