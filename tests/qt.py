"""
Test if Matplotlib is using PyQt4 as backend
"""


def test_matplotlib_qt_backend():
    print ("testing matplotlib qt backend ...")
    try:
        # Matplot changed its file structure several times in history, so we
        # must test all
        try:
            from matplotlib.backends.qt_compat import QtCore
        except:
            try:
                from matplotlib.backends.qt4_compat import QtCore
            except:
                from matplotlib.backends.qt import QtCore
        from PyQt4 import QtCore as QtCore4

        if QtCore is QtCore4:
            print ("... test passed")
            return True
        else:
            using = QtCore.__name__.split('.')[0]
            expect = QtCore4.__name__.split('.')[0]
            print ("... Qt test FAILURE\n" +
                   "    Matplotlib is using %s\n" % using +
                   "    It must use %s\n" % expect +
                   "    Possible reasons for that are that " +
                   "%s is not installed " % expect +
                   "or the envoriment variable QT_API is overwriting it.")
            return False
    except:
        import traceback
        print(traceback.format_exc())
        print ("... If you experience this test failure, it may be an "
               "expected! We would like to know why, "
               "please report in 'https://github.com/nguy/artview/issues'")
        return None


if __name__ == '__main__':
    test_matplotlib_qt_backend()
