#! /usr/bin/env python
#******************************
#  parv.py - PyArt Radar Viewer
#******************************
'''
PARV - The PyArt Radar Viewer

Allow a graphical interface to be employed as a quick browse through 
a radar data file opened using the PyArt software package

Author::
------
Nick Guy - OU CIMMS / University of Miami

Updated::
26 Sep 2014

Usage::
-----
parv.py /some/directory/path/to/look/in

TODO::
----
Improve the Next and Previous Advancement features and error handling.

Allow interactive modification of limits for 
  contouring, xrange, and yrange.

KNOWN BUGS::
----------
Some crashes after some number of left and right keystrokes.
'''
#-------------------------------------------------------------------
# Load the needed packages
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pyart

from glob import glob
import sys
import os
import argparse

import Tkinter as Tk
#from Tkinter import Tk, Button
from tkFileDialog import askopenfilename

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
#from matplotlib.backend_bases import key_press_handler

#===============================================================
# Initialize some variables

VERSION = '0.1.1'

RNG_RINGS = [50.,100.,150.]

Z_LIMS = (-10., 65.)
VR_LIMS = (-30., 30.)
ZDR_LIMS = (-5., 5.)
RHO_HV_LIMS = (.8, 1.)
KDP_LIMS = (0., 5.)
PHIDP_LIMS =(0., 1.)
NCP_LIMS = (0., 1.)
SW_LIMS = (-1., 10.)
TP_LIMS = (-200., 100.)

PTYPE = 'png'
#========================================================================
#######################
# BEGIN PARV CODE #
#######################

class Browse(object):
    '''
    Class to hold the GUI browse method
    '''

    def __init__(self, pathDir=None, airborne=False, rhi=False):
        '''
        Initialize the class to create the interface
        '''
        # Set some parameters
        self.dirIn = pathDir
        
        # Default field and tilt angle to plot
        self.field = 'reflectivity'
        self.tilt = 0
#        if airborne:
#            self.field = 'DBZ'
    
        # Set size of plot
        self.XSIZE = 8
        self.YSIZE = 8
        self.XRNG = (0., 0.) # Just placeholders, let PyArt do the work
        self.YRNG = (0., 0.) # Just placeholders, let PyArt do the work
        if airborne:
            self.XSIZE = 8
            self.YSIZE = 5
            self.XRNG = (-150., 150.)
            self.YRNG = (-5., 20.)
        if rhi:
            self.XSIZE = 8
            self.YSIZE = 5
            self.YRNG = (0., 20.)
            
        # Launch the GUI interface
        self.LaunchGUI()
    
        # Create a figure for output
        self.Set_fig_ax(nrows=1, ncols=1, xsize=self.XSIZE, ysize=self.YSIZE)
        #matplotlib.rcParams['toolbar'] = 'None'
        self._set_figure_canvas()
    
        # Show an "Open" dialog box and return the path to the selected file
        self._initial_openfile()
        
        # Allow advancement via left and right arrow keys
        self.root.bind('<Left>', self.leftkey)
        self.root.bind
        self.root.bind('<Right>', self.rightkey)
        self.frame.pack()

        Tk.mainloop()
        #root.destroy()
    
    ####################
    # GUI methods #
    ####################

    def LaunchGUI(self):
        '''Launches a GUI interface.
        Creates and returns gui and frame to pack
        '''
    
        # Initiate a counter, used so that Tilt and Field menus are 
        # not increased every time there is a selection
        # Might be a more elegant way
        self.counter = 0
    
        self.root = Tk.Tk()
        self.root.title("ARTView - ARM Radar Toolkit Viewer")
        #self.root.withdraw() # If we don't want a full GUI, this removes

        # Create a frame to hold the gui stuff
        self.frame = Tk.Frame(self.root, width=600, height=600)
        self.frame.pack()
        Tk.Label(self.frame).pack()
#        Tk.Label(self.frame, text="Radar File Browser").pack()

        # Create the menus
        self.CreateMenu()
        self.AddHelpMenu()
        self.AddPlotMenu()
        self.AddFileAdvanceMenu()

    def _print_radar_info(self):  ####NEEDS WORK### info() does not return to variable
        '''Print out the radar info to text box'''
        self.textFrame = Tk.Frame(self.root)
        self.text = Tk.text(self.textFrame)
        self.text.pack()

        # Get the radar info form rada object and print it
        radar_text = self.radar.info()
        self.text.insert(self.radar_info, Tk.END, '''Radar info goes here''')

    ######################
    # Menu build methods #
    ######################

    def CreateMenu(self):
        '''Create a selection menu'''
        self.menu = Tk.Menu(self.frame)
        self.root.config(menu=self.menu)

        filemenu = Tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open...", command=self._initial_openfile)
        filemenu.add_separator()
        filemenu.add_command(label="Save Image", command=self._savefile)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._quit)

    def AddHelpMenu(self):
        '''Add Help item to menu bar'''
        helpmenu = Tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self._about)
        helpmenu.add_command(label="Print Radar Info", command=self._print_radar_info)

    def AddPlotMenu(self):
        '''Add Plot item to menu bar'''
        plotmenu = Tk.Menu(self.menu)
        self.menu.add_cascade(label="Plot", menu=plotmenu)

        self.fieldmenu = Tk.Menu(self.menu)
        self.tiltmenu = Tk.Menu(self.menu)
        plotmenu.add_cascade(label="Field", menu=self.fieldmenu)
        if airborne:
            pass
        else:
            plotmenu.add_cascade(label="Tilt", menu=self.tiltmenu)
            
    def AddFileAdvanceMenu(self):
        '''Add an option to advance to next or previous file'''
        self.advancemenu = Tk.Menu(self.menu)
        self.menu.add_cascade(label="Advance", menu=self.advancemenu)

    def AddTiltMenu(self):
        '''Add a menu to change tilt angles of current plot'''
        for ntilt in self.rTilts:
            command = (lambda ntilt: lambda: self.TiltSelectCommand(ntilt)) (ntilt)
            self.tiltmenu.add_command(label="Tilt %d"%(ntilt+1), command=command)

    def AddFieldMenu(self):
        '''Add a menu to change current plot field'''
        for nombre in self.fieldnames:
            command = (lambda nombre: lambda: self.FieldSelectCommand(nombre)) (nombre)
            self.fieldmenu.add_command(label=nombre, command=command)
    
    def AddNextPrevMenu(self):
        '''Add an option to advance to next or previous file'''
        nextcmd = (lambda findex: lambda: self.AdvanceFileSelect(findex)) (self.fileindex + 1)
        self.advancemenu.add_command(label="Next", command=nextcmd)
        prevcmd = (lambda findex: lambda: self.AdvanceFileSelect(findex)) (self.fileindex - 1)
        self.advancemenu.add_command(label="Previous", command=prevcmd)

    def _about(self):
        print "This is a simple radar file browser to look at files using PyArt"

    def _quit(self):
        self.root.quit()
        self.root.destroy()

    #######################
    # Menu remove methods #
    #######################

    def _remove_tilt_menu(self):
        '''Remove the tilt menu items'''
        for ntilt in self.rTilts:
            self.tiltmenu.delete("Tilt %d"%(ntilt+1))
        
    def _remove_field_menu(self):
        '''Remove the field menu items'''
        for nombre in self.fieldnames:
            self.fieldmenu.delete(nombre)
            
    def _remove_next_prev_menu(self):
        '''Remove the next and previous'''
        self.advancemenu.delete("Next")
        self.advancemenu.delete("Previous")
    
    ########################
    # Button build methods #
    ########################

    def SetTiltRadioButtons(self):
        '''Set a tilt selection using radio buttons'''
        # Create a dialog box to choose Tilt angle
        TiltInt = Tk.IntVar()
        # Create array to hold button instances
        tiltbutton = []

        for ntilt in self.rTilts:
            command = (lambda ntilt: lambda: self.TiltSelectCommand(ntilt)) (ntilt)
            tiltbutton.append(Tk.Radiobutton(self.frame, value=int(ntilt), \
                                  text="Tilt %d"%(ntilt+1), variable=TiltInt, \
                                  command=command))
            tiltbutton[ntilt].pack(expand=1, side=Tk.TOP, anchor="w")
        
        self.tiltbutton = tiltbutton
        
    ########################
    # Button remove methods #
    ########################
    def _remove_tilt_radiobutton(self):
       '''Remove the tilt selection radio buttons'''
       for ntilt in self.rTilts:
           self.tiltbutton[ntilt].destroy()
    
    ########################
    # Selectionion methods #
    ########################
    
    def TiltSelectCommand(self, ntilt):
        '''Captures a selection and redraws the field with new tilt'''
        self.tilt = ntilt
        self._update_plot()

    def FieldSelectCommand(self, nombre):
        '''Captures a selection and redraws the new field'''
        self.field = nombre
        #self.PlotnewField()
        self._update_plot()
        
    def AdvanceFileSelect(self, findex):
        '''Captures a selection and redraws figure with new file'''
        if findex > len(self.filelist):
            print "END OF DIRECTORY, CANNOT ADVANCE"
            return
        if findex < 0:
            print "BEGINNING OF DIRECTORY CANNOT ADVANCE"
            return
        self.fileindex = findex
        self.filename = self.dirIn + "/" + self.filelist[findex]
        self._openfile()
        
    def leftkey(self, event):
        '''Left arrow key event triggers advancement'''
        self.AdvanceFileSelect(self.fileindex - 1)
        
    def rightkey(self, event):
        '''Right arrow key event triggers advancement'''
        self.AdvanceFileSelect(self.fileindex + 1)

    ####################
    # Data methods #
    ####################

    def _initial_openfile(self):
        '''Open a file via a file selection window'''
        self.filename = askopenfilename(initialdir=self.dirIn, title='Choose a file')
        print "Opening file " + self.filename 
        
        # Reset the directory path if needed, build list for advancing
        self._get_directory_info()
        
        self._openfile()

    def _openfile(self):
        '''Open a file via a file selection window'''
        print "Opening file " + self.filename
    
        # Read the data from file
        try:
            self.radar = pyart.io.read(self.filename)
        except:
            "This is not a recognized radar file"
            return
        
        # Increment counter to know whether to renew Tilt and field menus
        # If > 1 then remove the pre-existing menus before redrawing
        self.counter += 1
        if self.counter > 1:
            self._remove_tilt_menu()
            self._remove_field_menu()
            self._remove_tilt_radiobutton()
            self._remove_next_prev_menu()

        # Get the tilt angles
        self.rTilts = self.radar.sweep_number['data'][:]
        # Get field names
        self.fieldnames = self.radar.fields.keys()

        # Set up the tilt and field menus
        if airborne:
            pass
        else:
            self.SetTiltRadioButtons()
        self.AddTiltMenu()
        self.AddFieldMenu()
        self.AddNextPrevMenu()

        self._update_plot()
        
#        self.Make_Lims_Entry()

    def _savefile(self, PTYPE=PTYPE):
        '''Save the current display'''
        pName = self.display.generate_filename('refelctivity',self.tilt,ext=PTYPE)
        print "Creating "+ pName

        RADNAME = self.radar.metadata['instrument_name']
        plt.savefig(RADNAME+pName,format=PTYPE)

        # Find out the save file name, first get filename
        #savefilename = tkFileDialog.asksaveasfilename(**self.file_opt)

#    def on_key_event(self, event):
#        print('you pressed %s'%event.key)
#        key_press_handler(event, self.canvas, toolbar=None)#self.toolbar)

    ####################
    # Plotting methods #
    ####################

    def Set_fig_ax(self, nrows=1, ncols=1, xsize=10, ysize=10):
        '''Set the figure and axis to plot to'''
        self.fig = matplotlib.figure.Figure(figsize=(xsize, ysize))#, dpi=100)
        #self.ax = self.fig.add_subplot(111)
        self.ax = self.fig.add_axes([0.2, 0.2, 0.7,0.7])
        self.cax = self.fig.add_axes([0.2,0.10,0.7,0.02])

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area'''
        # a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)#window)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.LEFT, expand=1) 

#        self.toolbar = NavigationToolbar2TkAgg( self.canvas, self.root)
#        self.toolbar.update()
        #self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.canvas._tkcanvas.pack(side=Tk.LEFT, expand=1)#fill=Tk.BOTH, 
    
#        self.canvas.mpl_connect('key_press_event', self.on_key_event)

    def _update_plot(self):
        '''Renew the plot'''
        print "Plotting " + self.field +" field, " + "Tilt %d" % (self.tilt+1)
    
        # Get the min and max to use for plotting
        self._initialize_plot()
        print self.limits['ymax']
        # Create the plot with PyArt RadarDisplay 
        # Always intitiates at lowest elevation angle
        self.ax.cla()
        
        if airborne:
            self.display = pyart.graph.RadarDisplay_Airborne(self.radar)
            
            self.plot = self.display.plot_sweep_grid(self.field, \
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax)
            self.display.set_limits(xlim=(self.XRNG[0], self.XRNG[1]), \
                                    ylim=(self.YRNG[0], self.YRNG[1]))
            self.display.plot_grid_lines()
        else:
            self.display = pyart.graph.RadarDisplay(self.radar)
            if self.radar.scan_type == 'ppi':
                self.plot = self.display.plot_ppi(self.field, self.tilt,\
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax)

                self.display.plot_range_rings(RNG_RINGS)
                self.display.plot_cross_hair(5.)
            elif self.radar.scan_type == 'rhi':
                self.plot = self.display.plot_rhi(self.field, self.tilt,\
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax)
                self.display.set_limits(ylim=(self.limits['ymin'],self.limits['ymax']),\
                                        ax=self.ax)
               
    
        norm = matplotlib.colors.Normalize(vmin=self.vminmax[0], vmax=self.vminmax[1])
        self.cbar=matplotlib.colorbar.ColorbarBase(self.cax, cmap=self.CMAP,\
                                                norm=norm, orientation='horizontal')
        self.cbar.set_label(self.radar.fields[self.field]['units'])
        self.canvas.draw()
    
    ###############
    # Get methods #
    ###############
    
    def _initialize_plot(self):
        if self.field == 'reflectivity':
            self.vminmax = (Z_LIMS[0], Z_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif self.field == 'DBZ':
            self.vminmax = (Z_LIMS[0], Z_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif self.field == 'velocity':
            self.vminmax = (VR_LIMS[0], VR_LIMS[1])
            self.CMAP = 'RdBu_r'
        elif self.field == 'VEL':
            self.vminmax = (VR_LIMS[0], VR_LIMS[1])
            self.CMAP = 'RdBu_r'
        elif self.field == 'differential_reflectivity':
            self.vminmax = (ZDR_LIMS[0], ZDR_LIMS[1])
            self.CMAP = 'RdYlBu_r'
        elif self.field == 'cross_correlation_ratio':
            self.vminmax = (RHO_HV_LIMS[0], RHO_HV_LIMS[1])
            self.CMAP = 'cool'
        elif self.field == 'differential_phase':
            self.vminmax = (KDP_LIMS[0], KDP_LIMS[1])
            self.CMAP = 'YlOrBr'
        elif self.field == 'normalized_coherent_power':
            self.vminmax = (NCP_LIMS[0], NCP_LIMS[1])
            self.CMAP = 'jet'
        elif self.field == 'spectrum_width':
            self.vminmax = (SW_LIMS[0], SW_LIMS[1])
            self.CMAP = 'gist_ncar'
        elif self.field == 'specific_differential_phase':
            self.vminmax = (PHIDP_LIMS[0], PHIDP_LIMS[1]) 
            self.CMAP = 'RdBu_r'
        elif self.field == 'total_power':
            self.vminmax = (TP_LIMS[0], TP_LIMS[1])
            self.CMAP = 'jet'
           
        limit_strs = ('vmin', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax')
        self.limits = {}
        
        # Now pull the default values
        self.limits['vmin'] = self.vminmax[0]
        self.limits['vmax'] = self.vminmax[1]
        self.limits['xmin'] = self.XRNG[0]
        self.limits['xmax'] = self.XRNG[1]
        self.limits['ymin'] = self.YRNG[0]
        self.limits['ymax'] = self.YRNG[1]
        
        if self.radar.scan_type == 'rhi':
            print "IN HERE"
            self.fig.set_size_inches(8,5)
            self.limits['ymin'] = 0.
            self.limits['ymax'] = 20.
            
            self.canvas.draw()
        
    def _get_directory_info(self):
        # Record the new directory if user went somewhere else
        self.dirIn = os.path.dirname(self.filename)
        
        # Get a list of files in the working directory
        self.filelist = os.listdir(self.dirIn)
        
        self.fileindex = self.filelist.index(os.path.basename(self.filename))
           
###################################
if __name__ == '__main__':
    # Check for directory
    
    parser = argparse.ArgumentParser(
              description='Start PARV - the PyArt Radar Viewer.')
    parser.add_argument('searchstring', type=str, help='directory to open')
 
    igroup = parser.add_argument_group(
             title='set input platform, optional',
             description=('The ingest method for various platfoms can be chosen. '
                          'If not chosen, an assumption of a gound '
                          'platform is made. '
                          'Specify airborne as follows:'))
  
    igroup.add_argument('--airborne', action='store_true',
                          help='Airborne radar file')
                          
    igroup.add_argument('--rhi', action='store_true',
                          help='RHI scan')
 
    parser.add_argument('-v', '--version', action='version',
                         version='PARV version %s' % (VERSION))
    
    # Parse the args                     
    args = parser.parse_args()
    
    # Check if there is an input directory
    if args.searchstring:
        fDirIn = args.searchstring
    else: 
        fDirIn = "./"
        
    # Set airborne flag off and change if airborne called
    airborne, rhi = False, False
    if args.airborne:
        airborne = True
    if args.rhi:
        rhi = True
        
    Browse(pathDir=fDirIn, airborne=airborne, rhi=rhi)
    