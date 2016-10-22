git """
console.py
"""

# Load the needed packages
import code
import numpy as np
import pyart

import sys
import os

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '...')
sys.path.insert(0, path)

import artview

from ..core import Component, Variable, common, QtGui, QtCore, componentsList

class Field():

    def __init__(self, Vradar, field_name):
        self._Vradar = Vradar
        self._field = Vradar.value.fields[field_name]
        self._field_name = field_name
        self.auto_update = True

    def update(self):
        self._Vradar.update()

    def _update(self):
        if self.auto_update:
            self.update()

    def __str__(self):
        # this will be class be the print function
        # not sure what to put here, I could be interesting
        # to display some data
        raise NotImplemented

    #################
    # array methods #
    #################

    def _set_array_methods():
        pass

    def __array__(self, *args):
        return self._field['data'].__array__(*args)

    def __copy__(self, order='C'):
        return self._field['data'].__copy__(order)

    def __deepcopy__(self, order='C'):
        return self._field['data'].__deepcopy__(order)

    ###################
    # slicing methods #
    ###################

    def __len__(self):
        return len(self._field['data'])

    def __iter__(self):
        return iter(self._field['data'])

    def __contains__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return y in self._field['data']

    def __getitem__(self, key):
        return self._field['data'][key]

    def __setitem__(self, key, value):
        if isinstance(value , Field):
            value = value[:]
        self._field['data'][key] = value
        self._update()

    ###############
    # math method #
    ###############

    def __pos__(self):
        return +self._field['data']

    def __neg__(self):
        return -self._field['data']

    def __abs__(self):
        return abs(self._field['data'])

    def __invert__(self):
        return ~self._field['data']

    def __add__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] + y

    def __sub__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] - y

    def __mul__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] * y

    def __floordiv__(self,y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] // y

    def __div__(self,y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] / y

    def __truediv__(self,y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'].__truediv__(y)

    def __divmod__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return divmod(self._field['data'], y)

    def __pow__(self, y, *args):
        if isinstance(y , Field):
            y = y[:]
        return pow(self._field['data'], y, *args)

    def __lshift__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] << y

    def __rshift__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] >> y

    def __and__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] & y

    def __or__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] | y

    def __xor__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return self._field['data'] ^ y

    def __iadd__(self, y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] += y
        self._update()
        return self

    def __isub__(self, y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] -= y
        self._update()
        return self

    def __imul__(self, y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] *= y
        self._update()
        return self

    def __ifloordiv__(self,y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] //= y
        self._update()
        return self

    def __idiv__(self,y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] /= y
        self._update()
        return self

    def __itruediv__(self,y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'].__itruediv__(y)
        self._update()
        return self

    def __idivmod__(self, y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] %= y
        self._update()
        return self

    def __ipow__(self, y, *args):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'][:] = pow(self._field['data'], y, *args)
        self._update()
        return self

    def __ilshift__(self, y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] <<= y
        self._update()
        return self

    def __irshift__(self, y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] >>= y
        self._update()
        return self

    def __iand__(self, y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] &= y
        self._update()
        return self

    def __ior__(self, y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] |= y
        self._update()
        return self

    def __ixor__(self, y):
        if isinstance(y , Field):
            y = y[:]
        self._field['data'] ^= y
        self._update()
        return self

    def __int__(self):
        return int(self._field['data'])

    def __long__(self):
        return long(self._field['data'])

    def __float__(self):
        return float(self._field['data'])

    def __oct__(self):
        return oct(self._field['data'])

    def __hex__(self):
        return hex(self._field['data'])

    def __index__(self):
        return self._field['data'].__index__()

    def __cmp__(self, y):
        if isinstance(y , Field):
            y = y[:]
        return cmp(self._field['data'], y)

    def __nonzero__(self):
        return bool(self._field['data'])



import warnings

class LocalEnvoriment(dict):

    def __init__(self, Vradar):
        dict.__init__({})
        self.Vradar = Vradar
        for field in Vradar.value.fields.keys():
            self.__setitem__(field, Field(Vradar, field))
        self.__setitem__("add_field", self.add_field)

    def __setitem__(self, key, value):
        if key in self:
            old = self[key]
            if isinstance(old, Field):
                if repr(old) != repr(value):
                    warnings.warn(
                        "Trying to reset field, redicting to array.\n"
                        "you may delete the field with del")
                    #### this warning is not being shown
                    self[key][:] = value
            else:
                super(LocalEnvoriment, self).__setitem__(key, value)
        else:
            super(LocalEnvoriment, self).__setitem__(key, value)

    def __delitem__(self, key):
        if key in self.Vradar.fields:
            del self.Vradar.value.fields[key]
            self.Vradar.update()
        super(LocalEnvoriment, self).__delitem__(key)

    def add_field(self, field_name, attr={}):
        radar = self.Vradar.value
        if sys.version_info[0] == 3:
            # python3
            if not isinstance(field_name, str):
                raise TypeError("field_name must be a string")
        else:
            # python2
            if not isinstance(field_name, basestring):
                raise TypeError("field_name must be a string")
        if field_name in self:
            if field_name in self.Vradar.value.fields:
                raise TypeError("Field already in radar")
            else:
                if isinstance(self[field_name], Field):
                    attr['data'] = self[field_name].field['data']
                    self.Vradar.value.add_field(field_name, attr)
                else:
                    attr['data'] = np.ma.empty((radar.nrays, radar.ngates))
                    attr['data'][:] = np.ma.masked
                    attr['data'][:] = self[field_name]
                    self.Vradar.value.add_field(field_name, attr)
                    self[field_name] = Field(self.Vradar, field_name)

        else:
            attr['data'] = np.zeros((radar.nrays, radar.ngates))
            self.Vradar.value.add_field(field_name, attr)
            self[field_name] = Field(self.Vradar, field_name)
        self.Vradar.update()



class RadarTerminal(Component):
    '''
    Open an interactive python console so the direct manipulation
    '''

    @classmethod
    def guiStart(self, parent=None):
        '''Graphical interface for starting this class.'''
        kwargs, independent = \
            common._SimplePluginStart("AccessTerminal").startDisplay()
        kwargs['parent'] = parent
        return self(**kwargs), independent

    def __init__(self, name="AccessTerminal", parent=None):
        '''Initialize the class to create the interface.

        Parameters
        ----------
        [Optional]
        name : string
            Field Radiobutton window name.
        parent : PyQt instance
            Parent instance to associate to this class.
            If None, then Qt owns, otherwise associated with parent PyQt
            instance.
        '''
        super(RadarTerminal, self).__init__(name=name, parent=parent)

        self.Vradar = Variable(None)
        self.sharedVariables = {"Vradar": None}
        # Connect the components
        self.connectAllVariables()

        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)
        self.button = QtGui.QPushButton("Interactive Console")
        self.button.clicked.connect(self.runCode)
        self.layout.addWidget(self.button, 0, 0)
        self.layout.addWidget(
            QtGui.QLabel("WARNING: never run this if you don't\n" +
                         "have acess to the running terminal."), 1, 0)
        self.show()

    def runCode(self):
        '''Use :py:func:`code.interact` to acess python terminal'''
        # separe in thread to allow conflict with running Qt Application
        if self.Vradar.value is None:
            common.ShowWarning("No Radar linked, aborting!")
            return
        import threading
        banner = ("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            "\nHELLO: this is an iteractive python console so you can\n"
            "edit your radar field while running the GUI.\n"
            "It uses some python Magic so you can have fun.\n\n"
            )
        env = LocalEnvoriment(self.Vradar)
        env["np"] = np
        env["pyart"] = pyart
        self.thread = threading.Thread(
            target=code.interact,
            kwargs={'banner': banner,
                    'readfunc': None,
                    'local': env}
            )
        self.thread.start()
        # thread.join()


_plugins = [RadarTerminal]
