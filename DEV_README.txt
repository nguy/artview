this is initially just a list of topic developer of Artview should be aware of, this shall be re-worked in a more complete manual in the future


* All components of ARTview that are suppose to exist on it own (even if don't make practical reason) must be child class of core.Components and will be refereed in this manual as Component. Defining components for new functionalities is highly recommended. 

* In the __init__ function of every component, it must define a variable called sharedVariables, which is a dictionary. The variable name of every shared variable used (those are instances of core.Variable) must be a key in this dictionary, its value must be the function that will receive the "ValueChanged" signal emitted by the variable, the value may be None so no slot is connected. After defining this dictionary and assigning all shared variables call the Component method connectAllVariables, this just connect the variables signal to the slot.

Example: 
    self.Vradar = Vradar
    self.Vfield = Vfield
    self.Vtilt = Vtilt
    if Vlims is None:
        self.Vlims = Variable(None)
    else:
        self.Vlims = Vlims

    self.sharedVariables = {"Vradar": self.NewRadar,
                            "Vfield": self.NewField,
                            "Vtilt": self.NewTilt,
                            "Vlims": self.NewLims}
    self.connectAllVariables()

* This is not mandatory, but is recommend that components have a form of starting it self (even if just partially) in graphical interface. For that define the class method guiStart, which return a instance of your component. To use this function use the functionality menu.addComponent(comp).

Example: 
in component_control.py:


class ComponentsControl(core.Component):

    @classmethod
    def guiStart(self):
        val, entry = common.string_dialog("", "Component Name", "Name:")
        return self(name=val)

    def __init__(self, components=None, name="ComponentsControl", parent=None):
    ...

in execute_two.py:

menu.addComponent(component_control.ComponentsControl)

* Parallel to that, starting a component from another component is not prohibited, but it's strongly unrecommended. Use graphical initialization as above or direct code initialization in a execute file.

* Uses may add their custom components, those are called plug-ins. For that add the file to the plugins folder, in that file there must be a variable called _plugins, which is a list of components. Those components must have the guiStart method and will be automatically added to the menu in the standard execution, if the user uses a non-standard execution it must add it self.

Example:

in plugins/exemple1.py

class Exemple1(core.Component):
    @classmethod
    def guiStart(self):
        val, entry = common.string_dialog("Exemple1", "Exemple1", "Name:")
        return self(name=val)

    def __init__(self, name="Exemple1", parent=None):
    ...

_plugins=[Exemple1]


* Shared Variable are instances of core.Variable, they exist to hold a value that may be shared between components and emits the "ValueChanged" signal. There are two way of getting a shared variable: __init__ receives it or __init__ initialize it. A variable that is received is consider to already have a valid value, an initialized variable must leave __int__ with a valid value. If for some reason one need to change the value of a initialized variable inside __init__ do that with a weak changes, unless you have a really good reason for not doing so
.

Example:

in plot.py

    if Vlims is None:
        self.Vlims = Variable(None)
    else:
        self.Vlims = Vlims
...
    if Vlims.value is None:
        self.Vlims.change(self.limits, False)

*If for some reason you need to trigger the slot of a shared variable inside __init__ do that by direct call, do not use the variable to emit a signal unless you have a really good reason for doing so.

Example

in plot.py

    self.newRadar(None, None, True)

*In theory components are allowed to name shared variable as they want, however for a better interaction with control components its advised to name them according to other components and use the sharedVariables dictionary. It follows a list of variable use with their names, functions and valid value

Name       |Function                                |valid values
Vradar     |Hold a radar function open with pyart   |a instance of pyart.core.Radar
Vfield     |Name of a Field in radar file           |string in of radar.fields.keys()
Vtitl      |Tilt (sweep) of a radar file            |int between 0 and the (number of sweeps)-1
Vlims      |limits of display                       |dict containing keys:'vmin', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax' and holding float values


obs: we want to make None a valid value for Vradar, but this need some changes in plot.py
obs: Vlims is deprecated in favor of a not shared variable
