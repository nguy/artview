.. _plugin_tutorial:

Tutorial: Writing your own Plugin
=================================

    This Section is intended some points of awardness for any one wanting to create a of custom
    plug-in for ARTview. As plug-ins are just a special form of Component and ARTview is all based in Components this is also important to anyone (user or programer) wanting to understand ARTview. Of course we can not say you how do your plug-in, for that you can use all the tools availible in the python programming language, we however sugest before starting programing let us know your intensions and needs though our `GitHub issues page <https://github.com/nguy/artview/issues>`_, we may provide some valiable information and ideas on how to solve the problem.


The Basics
----------

    To allow the integration of plugins in ARTview we have made some rules that must be follow, in the risk of your plug-in or in the worse case ARTview not working. I will list those here and after I will instruct on how to follow them.

    * Plug-ins must be located in one single file in :artview:`artview/plugins` ending in **.py**.

    * The plug-in file must contain a variable ``_plugins``, this is a list of plug-ins, normaly just one.

    * Plug-ins are always a class, moreover they are always child classes of :py:class:`~artview.core.core.Component`. Like this ``class YourPlugin(core.Component):``

    * If plug-ins must interact with other ARTview components they use :py:class:`~artview.core.core.Variable`, not  direct call.

    * Plug-ins must have a GUIstart class method, like this

      .. code-block:: python

          @classmethod
          def guiStart(self, parent=None):
              ################################
              #    Define Call Parameters    #
              ################################
              return self(...), True/False

The Plug-in File
----------------

    ARTview expect all files present in :artview:`artview/plugins` and ending in **.py** (e.g **your_plugin.py**) to be importable into python and have a (possibily empty) list of plug-ins in the variable ``_plugins`` (e.g ``_plugins = [YourPlugin]``. Only plug-ins present in such list are added to :py:mod:`~artview.plugins`. File starting with underscore are ignored, this allow you to separate your plugin in multiple file or even folders if needed.

    As the file **your_plugin.py** is imported inside ARTview you should not import it in absolut, but rather make a relative imports. That is instead of ``from artview import core, components`` do ``from .. import core, components``.

