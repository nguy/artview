#! /usr/bin/env python
#******************************
#  artview.py - PyArt Radar Viewer
#******************************
'''
ARTview - The ARM Radar Toolkit Viewer

Allow a graphical interface to be employed as a quick browse through 
a radar data file opened using the PyArt software package

Author::
------
Nick Guy - OU CIMMS / University of Miami

Updated::
-------
30 Sep 2014

Usage::
-----
parv.py /some/directory/path/to/look/in

TODO::
----
Improve error handling.

Speed up interactive modification of limits for 
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

#===============================================================
# Initialization defaults for variables

VERSION = '0.1.3'

Z_LIMS = (-10., 65.)
VR_LIMS = (-30., 30.)
ZDR_LIMS = (-5., 5.)
RHO_HV_LIMS = (.8, 1.)
KDP_LIMS = (0., 5.)
PHIDP_LIMS =(0., 1.)
NCP_LIMS = (0., 1.)
SW_LIMS = (-1., 10.)
TP_LIMS = (-200., 100.)

AIR_XRNG = (-150., 150.)
AIR_YRNG = (-10., 20.)
AIR_XSIZE = 8
AIR_YSIZE = 5

PPI_XRNG = (-150., 150.)
PPI_YRNG = (-150., 150.)
PPI_XSIZE = 8
PPI_YSIZE = 8

RHI_XRNG = (0., 150.)
RHI_YRNG = (0., 20.)
RHI_XSIZE = 8
RHI_YSIZE = 5

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
    
        self.airborne = airborne
        self.rhi = rhi
        
        # Set size of plot
        self.XSIZE = PPI_XSIZE
        self.YSIZE = PPI_YSIZE
        self.XRNG = PPI_XRNG
        self.YRNG = PPI_YRNG
        if self.airborne:
            self.XSIZE = AIR_XSIZE
            self.YSIZE = AIR_YSIZE
            self.XRNG = AIR_XRNG
            self.YRNG = AIR_YRNG
        if self.rhi:
            self.XSIZE = RHI_XSIZE
            self.YSIZE = RHI_YSIZE
            self.XRNG = RHI_XRNG
            self.YRNG = RHI_YRNG
            
        # Set the default range rings
        self.RngRingList = ["None", "10 km", "20 km", "30 km", "50 km", "100 km"]
        self.RngRing = False
        
        # Launch the GUI interface
        self.LaunchGUI()
    
        # Create a figure for output
        self._set_fig_ax(nrows=1, ncols=1)
        
        # Initialize limits
        self._initialize_limits()
        
        # Create the Limit Entry
        self.Make_Lims_Entry()
        
        # Show an "Open" dialog box and return the path to the selected file
        self._initial_openfile()
        
        # Allow advancement via left and right arrow keys
        self.root.bind('<Left>', self.leftkey)
        self.root.bind
        self.root.bind('<Right>', self.rightkey)
        self.frame.pack()
        
        self.root.update_idletasks()

        Tk.mainloop()
    
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

        # Create a frame to hold the gui stuff
        self.frame = Tk.Frame(self.root)#, width=600, height=600
        self.frame.pack()
        Tk.Label(self.frame).pack()

        # Create the menus
        self.CreateMenu()
        self.AddHelpMenu()
        self.AddPlotMenu()
        self.AddFileAdvanceMenu()

    ######################
    # Help methods #
    ######################

    def _about(self):
        print "This is a simple radar file browser to look at files using PyArt"

    def _dump_radar_info_to_terminal(self):
        '''Print out the radar info to text box'''

        # Get the radar info form rada object and print it
        radar_text = self.radar.info()
        
        print radar_text
        
        ### THIS PORTION DOES NOT WORK TO DATE  ###
#        self.textFrame = Tk.Frame(self.root)
#        self.text = Tk.text(self.textFrame)
#        self.text.pack()
#        self.text.insert(self.radar_info, Tk.END, '''Radar info goes here''')

    def _print_radar_info_short(self):
        '''Print out some basic info about the radar'''
        print ('Radar Name: %s'% self.radar.metadata['instrument_name'])
        print ('Radar longitude: %f'% self.radar.longitude['data'][0])
        print ('Radar latitude: %f'% self.radar.latitude['data'][0])
        print ('Radar altitude: %f'% self.radar.altitude['data'][0])
        print ('   ')
        print ('Unambiguous range: %f %s' % \
              (self.radar.instrument_parameters['unambiguous_range']['data'][0], \
               self.radar.instrument_parameters['unambiguous_range']['units'][0]))
        print ('Nyquist velocity: %f %s' % \
              (self.radar.instrument_parameters['nyquist_velocity']['data'][0], \
               self.radar.instrument_parameters['nyquist_velocity']['units'][0]))
        print ('   ')
        print ('Radar Beamwidth, horiz: %f %s' % \
              (self.radar.instrument_parameters['radar_beam_width_h']['data'][0], \
               self.radar.instrument_parameters['radar_beam_width_h']['units'][0]))
        print ('Radar Beamwidth, vert: %f %s' % \
              (self.radar.instrument_parameters['radar_beam_width_v']['data'][0], \
               self.radar.instrument_parameters['radar_beam_width_v']['units'][0]))
        print ('Pulsewidth: %f %s' % \
              (self.radar.instrument_parameters['pulse_width']['data'][0], \
               self.radar.instrument_parameters['pulse_width']['units'][0]))
        print ('   ')
        
        print ('Number of gates: ', self.radar.ngates)
        print ('Number of sweeps: ', self.radar.nsweeps)

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
        helpmenu.add_command(label="Print Short Radar Info", command=self._print_radar_info_short)
        helpmenu.add_command(label="Print Long Radar Info", command=self._dump_radar_info_to_terminal)

    def AddPlotMenu(self):
        '''Add Plot item to menu bar'''
        plotmenu = Tk.Menu(self.menu)
        self.menu.add_cascade(label="Plot", menu=plotmenu)

        self.fieldmenu = Tk.Menu(self.menu)
        self.tiltmenu = Tk.Menu(self.menu)
        self.rngringmenu = Tk.Menu(self.menu)
        plotmenu.add_cascade(label="Field", menu=self.fieldmenu)
        if self.airborne or self.rhi:
            pass
        else:
            plotmenu.add_cascade(label="Tilt", menu=self.tiltmenu)
            plotmenu.add_cascade(label="Rng Ring every...", menu=self.rngringmenu)
            
    def AddFileAdvanceMenu(self):
        '''Add an option to advance to next or previous file'''
        self.advancemenu = Tk.Menu(self.menu)
        self.menu.add_cascade(label="Advance", menu=self.advancemenu)

    def AddTiltMenu(self):
        '''Add a menu to change tilt angles of current plot'''
        for ntilt in self.rTilts:
            cmd = (lambda ntilt: lambda: self.TiltSelectCmd(ntilt)) (ntilt)
            self.tiltmenu.add_command(label="Tilt %d"%(ntilt+1), command=cmd)

    def AddFieldMenu(self):
        '''Add a menu to change current plot field'''
        for nombre in self.fieldnames:
            cmd = (lambda nombre: lambda: self.FieldSelectCmd(nombre)) (nombre)
            self.fieldmenu.add_command(label=nombre, command=cmd)
            
    def AddRngRingMenu(self):
        '''Add a menu to set range rings'''
        for RngRing in self.RngRingList:
            cmd = (lambda RngRing: lambda: self.RngRingSelectCmd(RngRing)) (RngRing)
            self.rngringmenu.add_command(label=RngRing, command=cmd)
    
    def AddNextPrevMenu(self):
        '''Add an option to advance to next or previous file'''
        nextcmd = (lambda findex: lambda: self.AdvanceFileSelect(findex)) (self.fileindex + 1)
        self.advancemenu.add_command(label="Next", command=nextcmd)
        prevcmd = (lambda findex: lambda: self.AdvanceFileSelect(findex)) (self.fileindex - 1)
        self.advancemenu.add_command(label="Previous", command=prevcmd)
        
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
    
    def _remove_rngring_menu(self):
        '''Remove the range rings menu items'''
        for rngring in self.RngRingList:
            self.rngringmenu.delete(rngring)
            
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
            command = (lambda ntilt: lambda: self.TiltSelectCmd(ntilt)) (ntilt)
            tiltbutton.append(Tk.Radiobutton(self.frame, value=int(ntilt), \
                                  text="Tilt %d"%(ntilt+1), variable=TiltInt, \
                                  command=command))
            tiltbutton[ntilt].pack(expand=1, side=Tk.TOP, anchor="w")
        
        self.tiltbutton = tiltbutton
        
    #########################
    # Button remove methods #
    #########################
    def _remove_tilt_radiobutton(self):
       '''Remove the tilt selection radio buttons'''
       for ntilt in self.rTilts:
           self.tiltbutton[ntilt].destroy()
    
    #############################
    # Limit entry build methods #
    #############################
           
    def Make_Lims_Entry(self):
        '''Make entry boxes to modify variable and axis limits'''
        self.root.update()
        
        disp_strs = ('Data Min:', 'Data Max:', 'X-axis Min:', 'X-axis Max:', \
                      'Y-axis Min:', 'Y-axis Max:')
        limit_strs = ('vmin', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax')
        self.entryfield = []
        
        self.EntryFrame = Tk.Frame(self.frame)
        
        for index, lstr in enumerate(disp_strs):
        
            LimitLabel = Tk.Label(self.EntryFrame, text=lstr)
            LimitLabel.pack(side=Tk.TOP)
            self.entryfield.append(Tk.Entry(self.EntryFrame, width=6))
            self.entryfield[index].pack(expand=1, side=Tk.TOP)
            self.entryfield[index].insert(0, self.limits[limit_strs[index]])
            
#            LimitLabel.update_idletasks()
#            self.entryfield[index].update_idletasks()
        self.root.update()    
        self.EntryFrame.pack(side=Tk.LEFT)
        self.applybutton = Tk.Button(self.EntryFrame, text='Apply',command=self._update_lims)
        self.applybutton.pack(side=Tk.TOP)
        
        
        self.EntryFrame.bind("<Button-1>", self._update_entrylist)
        
    def _update_lims(self):
        '''Update the limits with newly entered limits'''
        limit_strs = ('vmin', 'vmax', 'xmin', 'xmax', 'ymin', 'ymax')
       
        for index, lstr in enumerate(limit_strs):
            self.limits[lstr] = float(self.entryfield[index].get())
        
#            self.root.update_()
        
        # Update the plot with new values
        self._update_plot()
 
    def _update_entrylist(self):
        self.root.update_idletasks()
        self.EntryFrame.update_idletasks()
    
    ########################
    # Selectionion methods #
    ########################
    
    def TiltSelectCmd(self, ntilt):
        '''Captures a selection and redraws the field with new tilt'''
        self.tilt = ntilt
        self._update_plot()

    def FieldSelectCmd(self, nombre):
        '''Captures a selection and redraws the new field'''
        self.field = nombre
        self._initialize_limits()
        self._update_plot()
        
    def RngRingSelectCmd(self, ringSel):
        '''Captures selection and redraws the field with range rings'''
        
        if ringSel is "None":
            self.RngRing = False
        else:
            self.RngRing = True
            # Find the unambigous range of the radar
            unrng = int(self.radar.instrument_parameters['unambiguous_range']['data'][0]/1000)
            
            # Set the step
            if ringSel == '10 km':
                ringdel = 10
            if ringSel == '20 km':
                ringdel = 20
            if ringSel == '30 km':
                ringdel = 30
            if ringSel == '50 km':
                ringdel = 50
            if ringSel == '100 km':
                ringdel = 100
                
            # Calculate an array of range rings
            self.RNG_RINGS = range(ringdel, unrng, ringdel)
        
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

    ########################
    # Data display methods #
    ########################

    def _initial_openfile(self):
        '''Open a file via a file selection window'''
#        self.root.update()
        self.filename = askopenfilename(initialdir=self.dirIn, title='Choose a file')
        
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
        
        # In case the flags were not used at startup
        # Check to see if this is an aircraft or rhi file
        if self.counter == 0:
            self._check_file_type()
            self._set_figure_canvas()

        # Increment counter to know whether to renew Tilt and field menus
        # If > 1 then remove the pre-existing menus before redrawing
        self.counter += 1
        
        if self.counter > 1:
            self._remove_field_menu()
            self._remove_next_prev_menu()
            #self._remove_lims_entry()
            
            if self.airborne or self.rhi:
                pass
            else:
                self._remove_tilt_menu()
                self._remove_tilt_radiobutton()
                self._remove_rngring_menu()

        # Get the tilt angles
        self.rTilts = self.radar.sweep_number['data'][:]
        # Get field names
        self.fieldnames = self.radar.fields.keys()

        # Set up the tilt and field menus
        if self.airborne or self.rhi:
            pass
        else:
            self.SetTiltRadioButtons()
            self.AddRngRingMenu()
        self.AddTiltMenu()
        self.AddFieldMenu()
        self.AddNextPrevMenu()
        
        self.root.update_idletasks()

        self._update_plot()
#        self.frame.update()
        self.root.update_idletasks()
#        self.canvas.draw()

    ####################
    # Plotting methods #
    ####################

    def _set_fig_ax(self, nrows=1, ncols=1):
        '''Set the figure and axis to plot to'''
        self.fig = matplotlib.figure.Figure(figsize=(self.XSIZE, self.YSIZE))
        xwidth = 0.7
        yheight = 0.7 * float(self.YSIZE)/float(self.XSIZE)
        self.ax = self.fig.add_axes([0.2, 0.2, xwidth, yheight])
        self.cax = self.fig.add_axes([0.2,0.10, xwidth, 0.02])
        
    def _set_fig_ax_rhi(self):
        '''Change figure size and limits if RHI'''
        if self.rhi:
            self.XSIZE = RHI_XSIZE
            self.YSIZE = RHI_YSIZE
            self.limits['ymin'] = RHI_YRNG[0]
            self.limits['ymax'] = RHI_YRNG[1]
        if self.airborne:
            self.XSIZE = AIR_XSIZE
            self.YSIZE = AIR_YSIZE
            self.limits['xmin'] = AIR_XRNG[0]
            self.limits['xmax'] = AIR_XRNG[1]
            self.limits['ymin'] = AIR_YRNG[0]
            self.limits['ymax'] = AIR_YRNG[1]
        self.fig.set_size_inches(self.XSIZE, self.YSIZE)
        self._set_fig_ax()
#        self.canvas.draw()

    def _set_figure_canvas(self):
        '''Set the figure canvas to draw in window area'''
        # a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)#window)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.LEFT, expand=1) 

        self.canvas._tkcanvas.pack(side=Tk.LEFT, expand=1)#fill=Tk.BOTH, 
        self.canvas.draw()

    def _update_plot(self):
        '''Renew the plot'''
        print "Plotting " + self.field +" field, " + "Tilt %d" % (self.tilt+1)
        
        # This is a bit of a hack to ensure that the viewer works with files
        # withouth "standard" output as defined by PyArt
        # Check to see if the field 'reflectivity' exists for the initial open
        self._check_default_field()
    
        # Create the plot with PyArt RadarDisplay 
        # Always intitiates at lowest elevation angle
        self.ax.cla()
        
        if self.airborne:
            self.display = pyart.graph.RadarDisplay_Airborne(self.radar)
            
            self.plot = self.display.plot_sweep_grid(self.field, \
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax)
            self.display.set_limits(xlim=(self.limits['xmin'], self.limits['xmax']),\
                                    ylim=(self.limits['ymin'], self.limits['ymax']),\
                                    ax=self.ax)
            self.display.plot_grid_lines()
        else:
            self.display = pyart.graph.RadarDisplay(self.radar)
            if self.radar.scan_type == 'ppi':
                # Create Plot
                self.plot = self.display.plot_ppi(self.field, self.tilt,\
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax)
                # Set limits
                self.display.set_limits(xlim=(self.limits['xmin'], self.limits['xmax']),\
                                        ylim=(self.limits['ymin'], self.limits['ymax']),\
                                        ax=self.ax)
                # Add range rings
                if self.RngRing:
                    self.display.plot_range_rings(self.RNG_RINGS, ax=self.ax)
                # Add radar location
                self.display.plot_cross_hair(5., ax=self.ax)
            elif (self.radar.scan_type == 'rhi') or (self.rhi is True):
                self.plot = self.display.plot_rhi(self.field, self.tilt,\
                                vmin=self.limits['vmin'], vmax=self.limits['vmax'],\
                                colorbar_flag=False, cmap=self.CMAP,\
                                ax=self.ax)
                self.display.set_limits(xlim=(self.limits['xmin'], self.limits['xmax']),\
                                        ylim=(self.limits['ymin'], self.limits['ymax']),\
                                        ax=self.ax)
                # Add range rings
                if self.RngRing:
                    self.display.plot_range_rings(self.RNG_RINGS, ax=self.ax)
               
        
        norm = matplotlib.colors.Normalize(vmin=self.limits['vmin'],\
                                           vmax=self.limits['vmax'])
        self.cbar=matplotlib.colorbar.ColorbarBase(self.cax, cmap=self.CMAP,\
                                                norm=norm, orientation='horizontal')
        self.cbar.set_label(self.radar.fields[self.field]['units'])
        self.canvas.draw()
        
        self.root.update_idletasks()
    
    #########################
    # Get and check methods #
    #########################
        
    def _get_directory_info(self):
        ''' Record the  directory of file
        This is useful if user went somewhere else on startup
        '''
        self.dirIn = os.path.dirname(self.filename)
        
        # Get a list of files in the working directory
        self.filelist = os.listdir(self.dirIn)
        
        self.fileindex = self.filelist.index(os.path.basename(self.filename))
    
    def _initialize_limits(self):
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
        
    def _check_default_field(self):
        '''Hack to perform a check on reflectivity to make it work with 
        a larger number of files
        This should only occur upon start up with a new file'''
        if self.field == 'reflectivity':
            if self.field in self.fieldnames:
                pass
            elif 'CZ' in self.fieldnames:
                self.field = 'CZ'
            elif 'DZ' in self.fieldnames:
                self.field = 'DZ'
            elif 'dbz' in self.fieldnames:
                self.field = 'dbz'
            elif 'DBZ' in self.fieldnames:
                self.field = 'DBZ'
            elif 'dBZ' in self.fieldnames:
                self.field = 'dBZ'
            elif 'Z' in self.fieldnames:
                self.field = 'Z'
                
    def _check_file_type(self):
        '''Check file to see if the file is airborne or rhi'''
        if self.radar.scan_type == 'rhi':
            try:
                (self.radar.metadata['platform_type'] == 'aircraft_tail') or \
                (self.radar.metadata['platform_type'] == 'aircraft')
                self.airborne = True
            except:
                self.rhi = True
            
            self._set_fig_ax_rhi()
        elif self.radar.scan_type == 'ppi':
            pass
        else:
            print "Check the scan type, ARTview supports PPI and RHI"
            return

    ########################
    # Image save methods #
    ########################

    def _savefile(self, PTYPE=PTYPE):
        '''Save the current display'''
        pName = self.display.generate_filename('refelctivity',self.tilt,ext=PTYPE)
        print "Creating "+ pName

        RADNAME = self.radar.metadata['instrument_name']
        plt.savefig(RADNAME+pName,format=PTYPE)

        # Find out the save file name, first get filename
        #savefilename = tkFileDialog.asksaveasfilename(**self.file_opt)
           
###################################
if __name__ == '__main__':
    # Check for directory
    
    parser = argparse.ArgumentParser(
              description='Start ARTview - the ARM Radar Toolkit Viewer.')
    parser.add_argument('searchstring', type=str, help='directory to open')
 
    igroup = parser.add_argument_group(
             title='Set input platform, optional',
             description=(''
                          'The ingest method for various platfoms can be chosen. '
                          'If not chosen, an assumption of a ground-based '
                          'platform is made. '
                          'The following flags may be used to  display' 
                          'RHI or airborne sweep data.'
                          ' '))
  
    igroup.add_argument('--airborne', action='store_true',
                          help='Airborne radar file')
                          
    igroup.add_argument('--rhi', action='store_true',
                          help='RHI scan')
 
    parser.add_argument('-v', '--version', action='version',
                         version='ARTview version %s' % (VERSION))
    
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
    