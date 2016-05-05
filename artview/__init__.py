"""
========================
ARTview (:mod:`artview`)
========================

.. _user:

################
Reference Manual
################

:Release: |release|
:Date: |today|

This guide provides details on all public functions, modules and classes
included in ARTview which a typical user will use on a regular basis.

.. toctree::
    :maxdepth: 1

    core
    components
    plugins
    scripts
    view

"""


# Detect if we're being called as part of ARTview setup procedure
try:
    __ARTVIEW_SETUP__
except NameError:
    __ARTVIEW_SETUP__ = False

if __ARTVIEW_SETUP__:
    import sys as _sys
    _sys.stderr.write("Running from ARTview source directory.\n")
    del _sys
else:
    try:
        # versioning
        from .version import git_revision as __git_revision__
        from .version import version as __version__
    except:
        import warnings
        warnings.warn("No ARTview Version!")

    import matplotlib
    matplotlib.use('Qt4Agg')
    matplotlib.rcParams['backend.qt4'] = 'PyQt4'

    # import subpackages
    from . import core
    from . import components
    from . import plugins
    from . import scripts
    from . import parser
    from . import view
    from .modes import modes

    modes += plugins._modes
    # define standard execution
    run = scripts.scripts['standard']
