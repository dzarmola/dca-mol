import os, glob
from math import sqrt
import ntpath
from copy import copy
import numpy as np

IMPRT_ERR = 0

import platform
import sys
import helper_functions as hf
import getpass
#SPLASHES
#1: generic/open-source
#2: evaluation
#3: edu
from distutils.spawn import find_executable
LATEX_FOUND = find_executable('latex')



# TODO check which paths should actually be used

#print hf.find_module("matplotlib")
#print hf.find_module("matplotlib","backend_bases.py")

############## VARIOUS IMPRTS
potential_paths = [""]
if platform.system()=="Linux":
    potential_paths += ["/opt//local/python2.7/site-packages/"]
elif platform.system()=="Windows":
    potential_paths += ["C:\\Python27\\lib\\site-packages"]
elif platform.system() in ["Darwin","darwin"]:
    potential_paths += ["/usr/lib/pymodules/python2.7/","/usr/lib/python2.7/dist-packages/", \
                             "/opt//local/python2.7/site-packages/", \
                             "/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/", \
                            '/Library/Python/2.7/site-packages', \
                             '/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages']


if os.path.isfile("{}\PATHS.txt".format(os.path.dirname(os.path.realpath(__file__)))):
    with open("{}\PATHS.txt".format(os.path.dirname(os.path.realpath(__file__)))) as paths:
        for line in paths:
            sys.path += line.strip().split(";")

PYMOL_LOCATION = "/path/to/pymol"

#### PYMOL.CMD
done = False
for path in potential_paths:
    try:
        sys.path.append(path)
        from pymol import cmd
        import pymol
        PYMOL_LOCATION = pymol.__file__.split("__init__")[0]
        done =1
    except:
        sys.path.pop()
        continue
if not done:
    print """Pymol modules couldn't be found. Try adding their location to $PYTHONPATH, e.g.\n
          > find /opt/ /usr/ -name "_cmd.so"
          /opt//local/python2.7/site-packages/pymol/_cmd.so.
    Then add the found path (up to the "pymol" directory) to your python path:
          >echo 'export PYTHONPATH="/opt//local/python2.7/site-packages/:$PYTHONPATH"' >> ~/.bashrc
          >source ~/.bashrc
          And re-run the plugin"""
    IMPRT_ERR = 1



VERSION = cmd.get_version()
SPLASH = cmd._cmd.splash(cmd._COb,1)

done = False
for path in potential_paths:
    try:
        sys.path.append(path)

        import matplotlib as mpl
        mpl.use('TkAgg')
        #mpl.use('Qt4Agg')
        mpl.rc('font', family='Arial')
        from matplotlib import patches, colors
        import matplotlib.pyplot as plt
        from pylab import cm

        mpl.rcParams['font.family'] = 'sans-serif'
        mpl.rcParams['font.sans-serif'] = ['Arial']
        """if LATEX_FOUND:
            mpl.rcParams['pdf.fonttype'] = 42
            mpl.rcParams['svg.fonttype'] = 'none'
            mpl.rcParams['ps.useafm'] = True
            mpl.rcParams['pdf.use14corefonts'] = True
            mpl.rcParams['text.usetex'] = True
            mpl.rc('text', usetex=True)
            #mpl.rcParams['text.latex.preamble'] = [
            #    r'\usepackage[default,scale=0.85]{opensans}'
            #]"""


        done =1
    except:
        sys.path.pop()
        continue
if not done:
    if SPLASH==3 or VERSION[1] == 2.0:
        """You are using PyMOL 2.0, which comes with its own python environment. 
        If this is your first time encountering this message please run
        {}/bin/conda install matplotlib
        form within your PyMOL directory.
        """.format(PYMOL_LOCATION)
    elif platform.system()=="Windows":
        print """Matplotlib library couldn't be found. Try adding its location to $PYTHONPATH.\n
        Alternatively you can create a "PATHS.txt" in this plugins directory within the Pymol path, and
        write path that you want added, separated by a semicolon [;].
        """
    else:
        print "Matplotlib library couldn't be found. Please install it and re-run the plugin."

    IMPRT_ERR = 1

done = False
for path in potential_paths:
    try:
        sys.path.append(path)
        import tkMessageBox, tkFileDialog,tkSimpleDialog
        import Tkinter as Tk

        done =1
    except:
        sys.path.pop()
        continue
if not done:
    if platform.system()=="Windows":
        print """Tkinter library couldn't be found. Try adding its location to $PYTHONPATH.\n
        Alternatively you can create a "PATHS.txt" file in this plugins directory within the Pymol path, and
        write path that you want added, separated by a semicolon [;].
        """
    else:
        print "Tkinter library couldn't be found. Please install it and re-run the plugin."
    IMPRT_ERR = 1

done = False
for path in potential_paths:
    try:
        sys.path.append(path)
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
        from matplotlib.backend_bases import key_press_handler


        class CustomToolbar(NavigationToolbar2TkAgg):
            def __init__(self, canvas_, parent_):
                self.toolitems = (
                    ('Home', 'Reset original view', 'home', 'home'),
                    ('Back', 'Back to  previous view', 'back', 'back'),
                    ('Forward', 'Forward to next view', 'forward', 'forward'),
                    (None, None, None, None),
                    ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
                    ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
                    (None, None, None, None),
                    #('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
                    ('Save', 'Save the figure', 'filesave', 'save_figure'),
                    )
                NavigationToolbar2TkAgg.__init__(self, canvas_, parent_)

            def save_figure(self, *args):
#                from six.moves import tkinter_tkfiledialog, tkinter_messagebox
                ftypes = [('Portable Network Graphics', '*.png'), \
                          ('Scalable Vector Graphics', '*.svgz'), \
                          ('Tagged Image File Format', '*.tiff'), ('Joint Photographic Experts Group', '*.jpg'), \
                          ('Raw RGBA bitmap', '*.raw'), ('Joint Photographic Experts Group', '*.jpeg'), \
                          ('Postscript', '*.ps'), ('Scalable Vector Graphics', '*.svg'), \
                          ('Encapsulated Postscript', '*.eps'), ('Raw RGBA bitmap', '*.rgba'), \
                          ('Portable Document Format', '*.pdf'), ('Tagged Image File Format', '*.tif')]
                if LATEX_FOUND:
                    ftypes.append(('PGF code for LaTeX', '*.pgf'))

                defaultextension = ''
                initialdir = os.path.expanduser(mpl.rcParams['savefig.directory'])
                fname = tkFileDialog.asksaveasfilename(
                    master=self.window,
                    title='Save the figure',
                    filetypes=ftypes,
                    defaultextension=defaultextension,
                    initialdir=initialdir,
                )

                if fname in ["", ()]:
                    return
                # Save dir for next time, unless empty str (i.e., use cwd).
                if initialdir != "":
                    mpl.rcParams['savefig.directory'] = (ntpath.dirname(fname))
                try:
                    # This method will handle the delegation to the correct type
                    self.canvas.figure.savefig(fname)
                except Exception as e:
                    tkMessageBox.showerror("Error saving file", str(e))


        done = 1
    except:
        sys.path.pop()
        continue
if not done:
    if platform.system()=="Windows":
        print """Matplotlib backend modules couldn't be found. Try adding their location to $PYTHONPATH.\n
        Alternatively you can create a "PATHS.txt" in this plugins directory within the Pymol path, and
        write path that you want added, separated by a semicolon [;].
        """
    else:
        print """Matplotlib backend modules couldn't be found. Try adding their location to $PYTHONPATH.\n
      Some popular locations include: '/usr/lib/pymodules/','/opt//local/python2.7/site-packages/'
      >echo 'export PYTHONPATH="/opt//local/python2.7/site-packages/:$PYTHONPATH"' >> ~/.bashrc
      >source ~/.bashrc
      And re-run the plugin"""
    IMPRT_ERR = 1
#    exit(1)


import dcaMOL_classes as dm

try:
    from tkEntryComplete import AutocompleteCombobox
except:
    from tkentrycomplete import AutocompleteCombobox



def __init__(self):
    if IMPRT_ERR:
        raise RuntimeError("Some important libraries couldn't be found. Please read above messages and install accordingly.")
    else:
        self.menuBar.addmenuitem('Plugin', 'command',
                            'dcaMOL',
                            label = 'dcaMOL',
                            command = lambda s=self: dcaMOL(s))

##### HELPER functions



class dcaMOL:
    modes = {0:"Normal mode", 1:"Multistate mode"}
    def __init__(self,app,DI='',ALN=''):
        self.app = app
        self.parent = app.root

        self.user = "".join(getpass.getuser().split())


        self.path = "{}/temp/".format(os.path.dirname(os.path.realpath(__file__)))
        self.default_cmap = "gist_ncar"
        self.SHOW_INTER_AS_VALENCE = False
        self.default_tpa_color = "pink"
        self.default_tpe_color = "yellow"
        self.default_fp_color = "blue"
        self.default_dpi = 1200
        self.default_plot_dpi = 100
        self.TP_cmap, self.TP_norm = self._make_new_TP_cmap()

        self._read_in_config_file()

        try:
            with open(self.path+"test_file","w",0) as test:
                test.write("Done")
        except IOError:
            if platform.system() == "Linux":
                self.path = "/tmp/dcaMOL_temp_files/"
            elif platform.system() == "Windows":
                home = os.path.expanduser("~")
                self.path = home+"\\dcaMOL_temp_files\\"
            elif platform.system() in ["Darwin", "darwin"]:
                self.path = "/tmp/dcaMOL_temp_files/"
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            try:
                with open(self.path + "test_file", "w", 0) as test:
                    test.write("Done")
            except IOError:
                self.path = self.path.strip("\\").strip("/") + "_" + self.user+"/"
                if not os.path.exists(self.path):
                    os.makedirs(self.path)
                with open(self.path + "test_file", "w", 0) as test:
                    test.write("Done")


        self.loader_window = Tk.Toplevel(self.parent)
        self.loader_window.wm_title("This will someday be the dcaMOL")

        self.root = Tk.Toplevel(self.parent)
        self.root.withdraw()


        self.wait_window = Tk.Toplevel(self.root)
        self.wait_window.withdraw()
        self.wait_window.title('Please wait')
        self.wait_window_message = Tk.StringVar()
        self.wait_window_progress = Tk.StringVar()
        self.wait_window_message_loc = Tk.Entry(master=self.wait_window, textvariable=self.wait_window_message,
                                                state=Tk.DISABLED, disabledforeground="black", justify=Tk.CENTER, width=50)
        self.wait_window_message_loc.grid(row=0,column=0)
        self.wait_window_progress_loc = Tk.Entry(master=self.wait_window, textvariable=self.wait_window_progress,
                                                 state=Tk.DISABLED, disabledforeground="black", justify=Tk.CENTER, width=50)
        self.wait_window_progress_loc.grid(row=1,column=0)

        self.window_of_selected_bonds = Tk.Toplevel(self.root)
        self.window_of_selected_bonds.withdraw()
        self.window_of_selected_bonds.wm_title("Shown bonds")
        self.window_of_selected_bonds_text = Tk.Text(self.window_of_selected_bonds, relief=Tk.FLAT,width=34)
        self.window_of_selected_bonds_scroll = Tk.Scrollbar(self.window_of_selected_bonds)
        self.window_of_selected_bonds_scroll.config(command=self.window_of_selected_bonds_text.yview)
        self.window_of_selected_bonds_text.config(yscrollcommand=self.window_of_selected_bonds_scroll.set)
        self.window_of_selected_bonds_text.insert('1.0', "PLACEHOLDER")
        #self.window_of_selected_bonds_text.bind('<Control-c>', lambda *args: self.window_of_selected_bonds_text.selection_get())
        self.window_of_selected_bonds.bind('<Control-c>', lambda *args: (self.root.clipboard_clear(),self.root.clipboard_append(self.window_of_selected_bonds_text.selection_get())))
        self.window_of_selected_bonds_text.config(state="disabled")
        self.window_of_selected_bonds_text.grid(row=0,column=0)
        self.window_of_selected_bonds_scroll.grid(row=0, column=1,sticky='ns')
        self.window_of_selected_bonds_rmbmenu = dm.RMB_menu(self.root,self.window_of_selected_bonds,self.window_of_selected_bonds_text)
        self.window_of_selected_bonds_text.bind('<Button-3>', self.window_of_selected_bonds_rmbmenu.popup)

        #self.window_of_selected_bonds_text = Tk.StringVar()#Tk.Text(self.window_of_selected_bonds, width=30, state=Tk.DISABLED)
        #self.window_of_selected_bonds_text.set("PLACEHOLDER")
        #Tk.Label(self.window_of_selected_bonds, textvariable=self.window_of_selected_bonds_text).grid(row=0,column=0)


        self.alignment = Tk.StringVar()
        self.discores = Tk.StringVar()
        #self.discores.set("/tmp/common_pfam_short_inserts.di") ### TODO TEMPORARY
        if ALN: self.alignment.set(ALN)
        if DI: self.discores.set(DI)
        self.overall_mode = 0


        #CONTROL VARIABLES
        self.is_rna = Tk.BooleanVar()

        self.STRUCTURES = []
        self.DATA_BACKUP = None
        self.data = None
        self.data2 = None
        self.UPPER_DATA_BOUND = Tk.DoubleVar()

        self.bground = None #computational thread

        self.FIGURE = None
        self.aplot = None
        self.cmapa = None
        self.norm = None
        self.canvas = None
        self.DRAWN_BONDS = []
        self.SS_plots = []
        self.SELECTED_REGIONS = []
        self.SELECTED_MERS = []
        self.AXLINES = []

        self.LAST_HIT_KEY = Tk.IntVar()
        self.LAST_HIT_KEY.set(0)
        self.HELD_CTRL = Tk.BooleanVar()
        self.HELD_CTRL.set(0)
        self.HELD_LMB = Tk.BooleanVar()
        self.HELD_LMB.set(0)
        self.LAST_CLICKED_POS = []
        self.LAST_TRACKED_POS = None
        self.BUTTONS = {1: "L", 2: "M", 3: "R"}

        self.current_structure_var = None
        self.current_structure_obj_var = None

        #### CREATE MAIN WINDOW

#        self.root = Tk.Tk()
        #self.root.wm_title("Here the magic happens")
        #self.root.withdraw()
        #self.root.wm_iconify()
        #self.root.wm_withdraw()

        ###MENUBAR
        self.menubar = Tk.Menu(self.root)
        self.root.config(menu=self.menubar)


        self.fileMenu = Tk.Menu(self.menubar)
        #self.fileMenu.add_command(label='Save plot image', command=lambda: self._save(), underline=14)
        self.fileMenu.add_command(label='Save plot image', command=lambda: self.customToolbar.save_figure(), underline=14)
        #self.fileMenu.add_command(label='Save plot as .svg', command=lambda: self._save(1), underline=14)
        #self.fileMenu.add_command(label='Save plot as .eps', command=lambda: self._save(2), underline=14)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Write out native contacts', command=self.write_native_contacts, underline=10,state=Tk.DISABLED)
        self.fileMenu.add_command(label='Write out all contacts', command=self.write_all_contacts, underline=10,state=Tk.DISABLED)
        self.fileMenu.add_command(label='Write out currently shown DI scores', command=self.write_shown_di, underline=10,state=Tk.DISABLED)
        self.fileMenu.add_command(label='Write out currently selected DI scores', command=self.write_selected_di, underline=10,state=Tk.DISABLED)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Options", command=self._configure_window, underline=0)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Reset", command=self._reset, underline=0)
        self.fileMenu.add_command(label="Quit", command=self._quit, underline=0)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        #### ---------------
        self.show_bond_selection = Tk.BooleanVar()
        self.show_bond_selection.set(0)
        self.window_of_selected_bonds.protocol("WM_DELETE_WINDOW", lambda self=self: self.show_bond_selection.set(0))
        self.trueness_show_intra = Tk.BooleanVar()
        self.trueness_show_intra.set(1)
        self.trueness_show_inter = Tk.BooleanVar()
        self.trueness_show_inter.set(1)
        self.trueness_show_false = Tk.BooleanVar()
        self.trueness_show_false.set(1)
        self.all_combos_var = Tk.BooleanVar()
        self.all_combos_var.set(0)
        self.recolor_by_trueness_var = Tk.BooleanVar()
        self.recolor_by_trueness_var.set(0)
        self.recolor_by_any_trueness = Tk.BooleanVar()
        self.recolor_by_any_trueness.set(0)
        self.TPrate = Tk.StringVar()
        self.comp_mode = Tk.BooleanVar()
        self.comp_mode.set(0)
        self.restrict_to_structure_var = Tk.BooleanVar()
        self.restrict_to_structure_var.set(0)

        self.show_bond_selection.trace("w", self.show_bonds_window)


        self.SSMenu = Tk.Menu(self.menubar)
        self.SSMenu.add_checkbutton(label="Show list of selected bonds", variable=self.show_bond_selection)
        self.SSMenu.add_separator()
        #self.SSMenu.add_checkbutton(label="Consider interchain contacts only with the main chain",
        #                               variable=self.all_combos_var)
        self.SSMenu.add_checkbutton(label="Native contacts comparison mode",
                                              variable=self.comp_mode,
                                              command=lambda: self.comparison_mode_engaged())
        self.SSMenu.add_checkbutton(label="Align plot to structure",
                                     variable=self.restrict_to_structure_var)
        self.SSMenu.add_checkbutton(label="Recolor by true/false positives",
                                                variable=self.recolor_by_trueness_var,
                                                command = self.recolor_by_trueness)
        self.SSMenu.add_checkbutton(label="Recolor by true/false positives at any point",
                                    variable=self.recolor_by_any_trueness,
                                    command=self.recolor_by_any_trueness_do,state=Tk.DISABLED)
        self.SSMenu.add_separator()
        self.SSMenu.add_checkbutton(label="Toggle True Positives (intrachain) - "+self.default_tpa_color,
                                    variable=self.trueness_show_intra,state=Tk.DISABLED)
        self.SSMenu.add_checkbutton(label="Toggle True Positives (interchain) - "+self.default_tpe_color,
                                    variable=self.trueness_show_inter,state=Tk.DISABLED)
        self.SSMenu.add_checkbutton(label="Toggle False Positives - "+self.default_fp_color,
                                    variable=self.trueness_show_false,state=Tk.DISABLED)

        self.menubar.add_cascade(label="Single structure plot", menu=self.SSMenu)
        self.menubar.entryconfig("Single structure plot",state=Tk.DISABLED)

        #### ---------------------------
        self.MCmenu = Tk.Menu(self.menubar)

        self.mark_on_similar = Tk.BooleanVar()
        self.mark_on_similar_just_within = Tk.BooleanVar()
        self.mark_on_similar.set(0)
        self.mark_on_similar_just_within.set(0)


        ### TODO grid above

        self.MCmenu.add_command(label='Flip intra/interchain selection', command=self.lets_do_the_flip,underline=0)

        self.MCmenu.add_checkbutton(label="Add bonds also to homologous chains",
                                       variable=self.mark_on_similar, command=self.redraw_bonds)
        self.MCmenu.add_checkbutton(label="Connect only when within inter-chain cutoff",
                                                   variable=self.mark_on_similar_just_within, command=self.redraw_bonds)

        self.menubar.add_cascade(label="Multichain options", menu=self.MCmenu)

        ### END MENUBAR

#        def mysza(dol=0,args=[]):
#            print "Mysza dol?",dol,vars(args[0])

        self.root.bind("<KeyPress>", self.keydown_all)
        self.root.bind("<KeyRelease>", self.keyup_all)
#        self.root.bind("<ButtonPress-1>", lambda *args: mysza(0,args))
#        self.root.bind("<ButtonRelease-1>", lambda *args: mysza(1,args))
        self.root.bind("<ButtonPress-1>", lambda *args: self.HELD_LMB.set(1))
        self.root.bind("<ButtonRelease-1>", lambda *args: (self.HELD_LMB.set(0),self.recalcTPrate() if  "Single" in self.map_structure_mode.get() and args[0].widget==self.slider_min else None))

        self.content = Tk.Frame(self.root)
        self.upper_bar = Tk.Frame(self.content,borderwidth=1, relief="sunken")
        self.left_bar = Tk.Frame(self.content, borderwidth=1, relief="sunken")
        self.plot_field = Tk.Frame(self.content)
        self.mode_frame = Tk.Frame(self.content)

        self.content.grid(column=0, row=0,sticky="NEWS")
        self.mode_frame.grid(column=0,row=0)
        self.upper_bar.grid(column=1, row=0,sticky='W')
        self.left_bar.grid(column=0, row=1,sticky="N")
        self.plot_field.grid(column=1,row=1,sticky="NWSE")

        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        #### UPPER_BAR ######
        self.OPCJE = ["Full Plot Mode"]
        self.map_structure_mode = Tk.StringVar()
        self.map_structure_mode.set(self.OPCJE[0])
        self.map_structure_mode.trace("w", self.alert_setting_change)


        self.SSframe = Tk.Frame(self.upper_bar)

        self.stats_frame = Tk.Frame(self.SSframe)
        self.stats_frame.grid(column=0, row=0,padx=10)

        self.cursor_position_frame = Tk.Frame(self.stats_frame)
        self.current_cursor_position_X = Tk.StringVar()
        self.current_cursor_position_Y = Tk.StringVar()
        Tk.Label(self.cursor_position_frame, text="Residue X: ").grid(column=0, row=0)
        Tk.Label(self.cursor_position_frame, text="Residue Y: ").grid(column=0, row=1)
        Tk.Label(self.cursor_position_frame, foreground="red",textvariable=self.current_cursor_position_X).grid(column=1, row=0)
        Tk.Label(self.cursor_position_frame, foreground="red",textvariable=self.current_cursor_position_Y).grid(column=1, row=1)
        self.cursor_position_frame.grid(column=0, row=0,padx=10)

        self.TP_frame = Tk.Frame(self.stats_frame)
        Tk.Label(self.TP_frame, text="True Positive Rate").grid(column=0, row=0)
        #Tk.Label(self.cursor_position_frame, text="True Positive Count").grid(column=0, row=0)
        Tk.Label(self.TP_frame, textvariable=self.TPrate).grid(column=0, row=1)
        self.TP_frame.grid(column=1, row=0,padx=10)

        self.comp_moddist_frame = Tk.Frame(self.SSframe)
        Tk.Label(self.comp_moddist_frame, text="Contact map mode").grid(column=0, row=0)
        self.comp_atom_mode = Tk.StringVar()
        self.comp_atom_mode.set(dm.Structure.available_modes[0])
        self.menu_atom_mode = None
        self.menu_atom_mode_rna = Tk.OptionMenu(self.comp_moddist_frame, self.comp_atom_mode, *dm.Structure.available_modes_rna)
        self.menu_atom_mode_prot = Tk.OptionMenu(self.comp_moddist_frame, self.comp_atom_mode, *dm.Structure.available_modes)
        self.comp_atom_mode.trace("w", self.menu_atom_mode_change)
        self.rna_nonwc_pairs = Tk.BooleanVar()
        self.rna_nonwc_pairs.set(0)
        self.rna_nonwc_pairs_check = Tk.Checkbutton(self.comp_moddist_frame, text="Show also non-canonical pairs",
                                                    variable=self.rna_nonwc_pairs,
                                                    command=lambda: self.makeSSplot())

        self.dist_frame = Tk.Frame(self.comp_moddist_frame,borderwidth=1, relief="sunken")
        Tk.Label(self.dist_frame, text="Intrachain distance").grid(column=0, row=0)
        self.comp_distance = Tk.DoubleVar()  # native cutoff
        self.comp_distance.set(8.)
        self.comp_distance.trace("w", self.spin_comp_distance_change)
        self.spin_comp_distance = Tk.Spinbox(self.dist_frame, textvariable=self.comp_distance, from_=0., to=30.,
                                             increment=0.1, width=6)
        self.spin_comp_distance.bind("<KeyPress>", self.spin_comp_distance_key)
        self.spin_comp_distance.bind("<Button-1>", self.spin_comp_distance_click)
        self.spin_comp_distance.grid(column=1, row=0)


        self.mark_on_similar_just_within_cutoff = Tk.DoubleVar()
        self.mark_on_similar_just_within_cutoff.set(24.0)
        self.mark_on_similar_just_within_spin = Tk.Spinbox(self.dist_frame,
                                                           textvariable=self.mark_on_similar_just_within_cutoff,
                                                           from_=0., to=150.,
                                                           increment=0.1,
                                                           width=6)  # ,command=spin_comp_distance_change)
        self.mark_on_similar_just_within_spin.bind("<KeyPress>", self.mosjws_key)
        self.mark_on_similar_just_within_cutoff.trace("w", self.mosjwc_change)

        self.dist_frame.grid(column=1,row=0,rowspan=3,padx=10)
        self.comp_moddist_frame.grid(column=1, row=0)

        ## -- TRAJECTORY --

        self.states_frame = Tk.Frame(self.SSframe)

        self.current_state_var = Tk.IntVar()
        self.current_state_var.set(1)

        self.last_state_var = Tk.IntVar()
        self.last_state_var.set(1)

        Tk.Label(self.states_frame, text="Change current state").grid(column=0,row=0,columnspan=3)
        self.goto_first_button = Tk.Button(master=self.states_frame, text='First', command=self.goto_first_state)
        self.goto_first_button.grid(column=0, row=1)
        self.current_state_spin = Tk.Spinbox(self.states_frame, textvariable=self.current_state_var, from_=1,
                                             to=self.last_state_var.get(),
                                             increment=1,
                                             command=self.state_change, width=8)
        self.current_state_spin.grid(column=1, row=1)
        self.goto_last_button = Tk.Button(master=self.states_frame, text='Last', command=self.goto_last_state)
        self.goto_last_button.grid(column=2, row=1)


        ############################### END UPPER_BAR

        ##### LEFT BAR
        self.spin_min_var = Tk.DoubleVar()
        self.spin_max_var = Tk.DoubleVar()


        ###TOP CONTACTS
        self.top_values_cnt = Tk.IntVar()
        self.top_values_pc = Tk.IntVar()
        top_frame = Tk.Frame(self.left_bar)
        top_frame.grid(column=0, row=0)
        Tk.Label(top_frame, text="Show top N contacts").grid(column=0,row=0,sticky='W')
        top_values_cnt_entry = Tk.Entry(top_frame, width=6, textvariable=self.top_values_cnt)
        top_values_cnt_entry.grid(column=0,row=1)
        Tk.Button(master=top_frame, text='Show top N', command=self.getTopXValues).grid(column=0,row=2)
        Tk.Label(top_frame, text="Show top N% contacts").grid(column=0,row=3,sticky='W')
        top_values_pc_entry = Tk.Entry(top_frame, width=3, textvariable=self.top_values_pc)
        top_values_pc_entry.grid(column=0,row=4)
        Tk.Button(master=top_frame, text='Show top N%', command=self.getTopPCValues).grid(column=0,row=5)

        #### END OF CONTACTS

        ## CMAP
        ### COLORMAP
        cm_frame = Tk.Frame(self.left_bar)
        cm_frame.grid(column=0,row=1)

        Tk.Label(cm_frame, text="Colormap:").grid(column=0,row=0,columnspan=1,sticky='W')
        self.colormap = Tk.StringVar()
        self.colormap.trace("w", self.colormap_change)
        self.colormap.set(self.default_cmap)
        v = AutocompleteCombobox(cm_frame, textvar=self.colormap, width=8)  # , variable, *OPCJE)
        v.set_shortlist(["gist_ncar", "bwr", "BinaryTP"])
        v.set_completion_list([str(m) for m in cm.datad if not m.endswith("_r")])
        v.bind("<KeyPress>", self.keydown)
        v.bind("<Button-1>", self.onclick)
        v.grid(column=0, row=2)

        gradient_frame = Tk.Frame(cm_frame)
        gradient_frame.grid(column=1,row=0,rowspan=4)
        self.cmap_fig = plt.figure(figsize=(0.25, 1.5), dpi=100)
        self.cmap_fig.subplots_adjust(top=1., bottom=0., left=0., right=1., hspace=0, wspace=0)
        self.cmap_ax = self.cmap_fig.add_subplot(111)
        gradient = np.linspace(0, 1, 256)
        gradient = np.vstack((gradient, np.linspace(0, 1, 256)))
        self.spin_max_var_4cmap = Tk.StringVar()
        self.spin_max_var_4cmap.set(str(self.spin_max_var.get()))
        self.spin_min_var_4cmap = Tk.StringVar()
        self.spin_min_var_4cmap.set(str(self.spin_min_var.get()))
        Tk.Label(cm_frame, width=6, textvariable=self.spin_max_var_4cmap).grid(column=0, row=1,sticky='W')
        Tk.Label(cm_frame, width=6, textvariable=self.spin_min_var_4cmap).grid(column=0, row=3,sticky='W')
        gradient_frame_inner = Tk.Frame(gradient_frame)
        gradient_frame_inner.grid(column=0, row=0)
        #self.cmap_ax.matshow(gradient, aspect=20, cmap=self.cmapa)
        mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                  norm=self.norm,
                                  orientation='vertical')

        self.cmap_ax.set_axis_off()
        self.cmap_canvas = FigureCanvasTkAgg(self.cmap_fig, master=gradient_frame_inner)
        self.cmap_canvas.show()
        self.cmap_canvas.get_tk_widget().pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        self.cmap_canvas._tkcanvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        # self.cmap_fig.tight_layout()


        #plt.figure(self.FIGURE.number)
        #### END OF COLORMAP
        ### SPIN MIN


        sl_min = Tk.Frame(self.left_bar)  # min_slider
        sl_min.grid(column=0, row=4)
        self.slider_min = Tk.Scale(sl_min, to=0, from_=1, resolution=0.001,
                                   command=self.slider_min_change,showvalue=0)
        self.spin_min = Tk.Spinbox(sl_min, textvariable=self.spin_min_var, from_=0.01, to=1,
                                   increment=0.001,
                                   command=self.spin_min_change, width=6)
        self.slider_min.set(0.001)
        Tk.Label(sl_min, text="Lower range border").grid(column=0, row=0, columnspan=2,sticky='W')
        self.slider_min.grid(column=1, row=1)
        self.spin_min_var.set(0.001)
        self.spin_min.grid(column=0, row=1)
        self.spin_min.bind("<KeyPress>", self.spin_min_change_key)
        self.spin_min.bind("<Button-1>", self.onclick())
        self.spin_min_var.trace("w", self.spin_min_change)

        ### END SPIN MIN
        sl_max = Tk.Frame(self.left_bar)  # max slider
        sl_max.grid(column=0, row=2)
        self.slider_max = Tk.Scale(sl_max, to=0.01, from_=1, resolution=0.001,
                                   command=self.slider_max_change,showvalue=0)
        self.spin_max = Tk.Spinbox(sl_max, textvariable=self.spin_max_var, from_=0, to=1,
                                   increment=0.001, width=6,
                                   command=self.spin_max_change)
        Tk.Label(sl_max, text="Upper range border").grid(column=0, row=0, columnspan=2,sticky='W')
        self.slider_max.grid(column=1, row=1)
        self.spin_max.grid(column=0, row=1)
        self.spin_max.bind("<KeyPress>", self.spin_max_change_key)
        self.spin_max_var.trace("w", self.spin_max_change)


        self.sl_mid = Tk.Frame(self.left_bar)  # mid slider
        Tk.Label(self.sl_mid, text="Middle range border").grid(column=0, row=0, columnspan=2,sticky='W')
        self.slider_mid = Tk.Scale(self.sl_mid, to=0, from_=1, resolution=0.001,
                                   command=self.slider_mid_change, width=6)
        self.slider_mid.grid(column=1,row=1)

        ### END SPINS

        ##### PYMOL SELECTION
        self.get_pymol_selection = Tk.Button(master=self.left_bar, text='Mark structure selection on plot', \
                                             command=self.mark_pymol_selection_on_plot)

        #### END PYMOL SELECTION


        ### LEGEND
        self.legend = Tk.Frame(self.left_bar)  # legend for secondary structure


        Tk.Label(self.legend, text="Secondary structure plot:").grid(column=0,row=0,sticky="W",columnspan=2)
        Tk.Label(self.legend, text="Alpha helix").grid(column=0,row=1)
        Tk.Label(self.legend, foreground="red",text=ur'\u221D \ \u056E').grid(column=1,row=1)
        Tk.Label(self.legend, text="Beta sheet").grid(column=0,row=2)
        Tk.Label(self.legend, foreground="blue",text=ur'\u21D1 \ \u21D2').grid(column=1,row=2)
        Tk.Label(self.legend, text="Missing residue").grid(column=0,row=3)
        Tk.Label(self.legend, foreground="gray",text="X").grid(column=1,row=3)


        ################################ END LEFT BAR

        ######## PLOT FIELD
        # DO THE PLOT
        self.FIGURE = plt.figure(figsize=(2, 2), dpi=self.default_plot_dpi)
        plt.subplots_adjust(left=0.05, bottom=0.03, right=1, top=1, wspace=0, hspace=0)
        self.aplot = self.FIGURE.add_subplot(111)
        self.aplot.set_aspect('equal')
        self.cmapa = cm.get_cmap(self.default_cmap)
        self.cmapa.set_bad(color="0.75")
        self.cmapa.set_over(color="black")
        self.cmapa.set_under(color="white")

        self.canvas = FigureCanvasTkAgg(self.FIGURE, master=self.plot_field)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.tool_frame = Tk.Frame(self.plot_field)
        self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.customToolbar = CustomToolbar(self.canvas, self.tool_frame)
        self.customToolbar.update()
        self.tool_frame.pack(side=Tk.LEFT)

        #### END PLOT FIELD


        """self.upper_controls = Tk.Frame(self.root)
        self.upper_controls.pack()
        self.below = Tk.Frame(self.root)
        self.below.pack(fill=Tk.BOTH, expand=1)
        self.left_controls = Tk.Frame(self.below)
        self.left_controls.pack(side=Tk.LEFT)

        lframe = Tk.Frame(self.cursor_position_frame)
        lframe.pack(side=Tk.LEFT)
        rframe = Tk.Frame(self.cursor_position_frame)
        rframe.pack(side=Tk.LEFT)


        self.lower_controls = Tk.Frame(self.root)
        self.lower_controls.pack(side=Tk.BOTTOM)"""

        #self.quit_button = Tk.Button(master=self.lower_controls, text='Quit', command=self._quit)
        #self.reset_button = Tk.Button(master=self.lower_controls, text='Reset', command=self._reset)
        #self.save_png_button = Tk.Button(master=self.lower_controls, text='Save plot as .png', command= lambda: self._save(0))
        #self.save_svg_button = Tk.Button(master=self.lower_controls, text='Save plot as .svg', command=lambda: self._save(1))

        #self.write_native_contacts_button = Tk.Button(master=self.lower_controls, text='Placeholder native contacts', command=self.write_native_contacts)
        #self.write_all_contacts_button = Tk.Button(master=self.lower_controls, text='Placeholder all contacts',
        #                                              command=self.write_all_contacts)


        #### VARIABLES


        #self.mark_on_similar_just_within_spin = None

        #self.restrict_check = None
        #self.comp_mode_check = None
        #self.recolor_by_trueness_check = None



        self.root.protocol("WM_DELETE_WINDOW", lambda: self._on_closing(parent=False))
        #self.parent.protocol("WM_DELETE_WINDOW", lambda: self._on_closing(parent=True))

        self.dcaMOL_main()

###### TRAJECTROY MODE
    def writeout_popup(self,container):
        popup = Tk.Toplevel(self.root)

        upper = Tk.Frame(master=popup)
        upper.grid(row=0,column=0,columnspan=2)
#        labels = Tk.Frame(master=upper)
#        labels.grid(row=0,column=0)
#        entries = Tk.Frame(master=upper)
#        entries.pack(side=Tk.LEFT)

        Tk.Label(master=popup, text="From frame").grid(row=1,column=0)
        Tk.Label(master=popup, text="To frame").grid(row=2,column=0)
        Tk.Label(master=popup, text="Step").grid(row=3,column=0)
        Tk.Label(master=popup, text="Output file").grid(row=4,column=0)

        _from_var = Tk.IntVar()
        _from_var.set(1)
        _from = Tk.Entry(master=popup, width=10, textvariable=_from_var)
        _from.grid(row=1,column=1)
        _to_var = Tk.IntVar()
        _to_var.set(self.last_state_var.get())
        _to = Tk.Entry(master=popup, width=10, textvariable=_to_var)
        _to.grid(row=2,column=1)
        _step_var = Tk.IntVar()
        _step_var.set(1 if self.last_state_var.get() <= 100 else 10)
        _step = Tk.Entry(master=popup, width=10, textvariable=_step_var)
        _step.grid(row=3,column=1)
        files = []
        _go = Tk.Button(master=popup,text='Save as', command=lambda: self.ask_for_save(files))
        _go.pack.grid(row=4,column=1)

        def finish_this(container):
            if not files or files[0] is None:
                tkMessageBox.showinfo("Error",
                                      "You must first specify an output file!")
                return
            container += [_from_var.get()-1, _to_var.get(), _step_var.get()]+files
            popup.quit()
            popup.destroy()

        run = Tk.Button(master=popup,text="Go!",command=lambda: finish_this(container))
        run.grid(row=5,column=0,columnspan=2)
        popup.mainloop()


    def write_native_contacts(self):
        container = []
        self.writeout_popup(container)
        if not container or len(container)<4:
            return
        _f,_t,_s,_file = container
        _t-=_f

        self.wait("Writing out contacts below {}A map for {}".format(self.comp_distance.get(),self.current_structure_var))
        with open(_file,"w",1) as outfile:
            with open(self.path+"/_temp_" + self.current_structure_var + "_" + dm.Structure.flat_modes[dm.Structure.mode] + ".map") as map_file:
                for state,line in enumerate(map_file):
                    self._wait_in_progress("State: {}/{}".format(state+1,self.current_structure_obj_var.num_states))
                    #state-=_f+1
                    if 0<=state<=_t and not state%_s:
                        outfile.write("#frame\t{}\n".format(state+_f+1))
                        gen = self.read_in_map_oneliner_gen(line)
                        for (x,y,d) in gen:
                            outfile.write("{}\t{}\t{}\n".format(x,y,d))
                            outfile.flush()
                    if state>_t:
                        break
        self.wait_window.withdraw()
        return

    def write_all_contacts(self):
        ftypes=[('Text file', '*.txt'), ('All files', '*')]
        outfile = tkFileDialog.asksaveasfilename(defaultextension=".txt",filetypes=ftypes)
        self.wait("Writing out all contacts map for {}".format(self.current_structure_var))
        with open(outfile, "w", 1) as outfile:
            with open(self.path+"/_temp_" + self.current_structure_var + "_" + dm.Structure.flat_modes[dm.Structure.mode] + ".map") as map_file:
                for state,line in enumerate(map_file):
                    self._wait_in_progress(
                        "State: {}/{}".format(state+1, self.current_structure_obj_var.num_states))
                    outfile.write("#frame\t{}\n".format(state+1))
                    gen = self.read_in_map_oneliner_gen(line,all=True)
                    for (x, y, d) in gen:
                        outfile.write("{}\t{}\t{}\n".format(x, y, d))
                        outfile.flush()
        self.wait_window.withdraw()
        return

    def write_shown_di(self):
        ftypes=[('Text file', '*.txt'), ('All files', '*')]
        outfile = tkFileDialog.asksaveasfilename(defaultextension=".txt",filetypes=ftypes)
        self.wait("Writing out currently shown DI scores for {}".format(self.current_structure_var))
        single = "Single" in self.map_structure_mode.get()
        assert single is True
        structure = self.current_structure_obj_var
        with open(outfile, "w", 1) as outfile:
            size = self.data.shape[0]
            for x in xrange(size):
                for y in xrange(x+1,size):
                    if self.data[x][y]>self.slider_min.get():

                        if self.restrict_to_structure_var.get():
                            sx = structure.translations.struct2pdb(x)
                            sy = structure.translations.struct2pdb(y)
                        else:
                            sx = structure.translations.struct2pdb(structure.translations.singleplot_bonds(x))
                            sy = structure.translations.struct2pdb(structure.translations.singleplot_bonds(y))
                        if not sx or not sy: continue
                        outfile.write("{}\t{}\t{}\n".format(sx, sy, self.data[x][y]))
                        outfile.flush()
        self.wait_window.withdraw()
        return
    def write_selected_di(self):
        ftypes=[('Text file', '*.txt'), ('All files', '*')]
        outfile = tkFileDialog.asksaveasfilename(defaultextension=".txt",filetypes=ftypes)
        self.wait("Writing out currently selected DI scores for {}".format(self.current_structure_var))
        single = "Single" in self.map_structure_mode.get()
        assert single is True
        structure = self.current_structure_obj_var
        with open(outfile, "w", 1) as outfile:
            size = self.data.shape[0]
            for X, Y, fp2 in self.SELECTED_REGIONS:
                for x in xrange(int(X[0]),int(X[1])+1):
                    for y in xrange(int(Y[0]),int(Y[1])+1):
                        if self.data[x][y]>self.slider_min.get():
                            if self.restrict_to_structure_var.get():
                                sx = structure.translations.struct2pdb(x)
                                sy = structure.translations.struct2pdb(y)
                            else:
                                sx = structure.translations.struct2pdb(structure.translations.singleplot_bonds(x))
                                sy = structure.translations.struct2pdb(structure.translations.singleplot_bonds(y))
                            if not sx or not sy: continue
                            outfile.write("{}\t{}\t{}\n".format(sx, sy, self.data[x][y]))
                            outfile.flush()
        self.wait_window.withdraw()
        return

    def goto_last_state(self):
        #cmd.set("state", self.last_state_var.get())
        self.current_state_var.set(self.last_state_var.get())
        self.state_change()

    def goto_first_state(self):
        #cmd.set("state", 1)
        self.current_state_var.set(1)
        self.state_change()

    def state_change(self):
        #self.current_state_var.set(self.current_state_spin.get())
        cmd.set("state", self.current_state_var.get())
        if self.map_structure_mode.get() != self.OPCJE[0]:
            self.makeSSplot()




    def ask_for_save(self,cont): ## returns opened file?
        ftypes=[('Text file', '*.txt'), ('All files', '*')]
        cont.append(tkFileDialog.asksaveasfilename(defaultextension=".txt",filetypes=ftypes))

    def ask_for_path(self,cont,path): ## returns opened file?
        cont.append(tkFileDialog.askdirectory(initialdir=path))
        #return fopen



    def read_in_map_oneliner_gen(self, line,all=False):
        ## line = "num_line dist(last_idx,last_idx-1) . . . dist(1,0)"
        structrans = self.current_structure_obj_var.translations
        size = len(structrans.structseq2pdb)
        mapa = np.zeros((size, size))
        mapa.fill(-1.)
        line = line.split()[1:]
        for x in xrange(size):
            for y in xrange(x):
                d = float(line.pop())
                if "anonical" in dm.Structure.mode:
                    if d<5.:
                        yield (structrans.struct2pdb(x), structrans.struct2pdb(y), "WC" if d<2. else "nonWC")
                else:
                    if all or d<self.comp_distance.get():
                        yield (structrans.struct2pdb(x),structrans.struct2pdb(y),d)



    def _delete_temp_files(self):
        tmps = glob.glob("{}/_temp_*_C*.map".format(self.path)) + glob.glob("{}/_temp_*_O5.map".format(self.path)) +glob.glob("{}/_temp_*_heavy.map".format(self.path))
        for tmp in tmps:
            #print "removing", tmp
            os.remove(tmp)
        print "Cleaned up temporary files."

    def _read_in_config_file(self):
        #conf_file = os.path.dirname(os.path.realpath(__file__))+"/.dcaMOLrc"
        conf_file = os.path.expanduser("~") + "/.dcaMOLrc"
        print "Reading in configuration file..."
        if os.path.isfile(conf_file):
            options = {}
            with open(conf_file) as conf:
                options = {x.split()[0] : x.split()[1] for x in  conf.readlines()}

            print "Options are", options
            if "DEFAULT_CMAP" in options:
                try:
                    cm.get_cmap(options["DEFAULT_CMAP"])
                    self.default_cmap = options["DEFAULT_CMAP"]
                except:
                    pass
            if "TEMP_PATH" in options:
                self.path = options["TEMP_PATH"]
            if "INTERCHAIN_AS_VALENCE" in options:
                self.SHOW_INTER_AS_VALENCE = bool(options['INTERCHAIN_AS_VALENCE'])
            if "DPI" in options:
                self.default_dpi = int(options['DPI'])
            if "TPA_COLOR" in options:
                self.default_tpa_color = options["TPA_COLOR"]
            if "TPE_COLOR" in options:
                self.default_tpe_color = options["TPE_COLOR"]
            if "FP_COLOR" in options:
                self.default_fp_color = options["FP_COLOR"]
            self.TP_cmap, self.TP_norm = self._make_new_TP_cmap()
            #self.SSMenu.entryconfig(8, label="Toggle True Positives(intrachain) - "+self.default_tpa_color)
            #self.SSMenu.entryconfig(9, label="Toggle True Positives(interchain) - "+self.default_tpe_color)
            #self.SSMenu.entryconfig(10, label="Toggle False Positives - "+self.default_fp_color)


    def _configure_window(self):
        conf_file = os.path.expanduser("~") + "/.dcaMOLrc"
        self.configure_window = Tk.Toplevel(self.root)
        self.configure_window.title("Options")
        opts = {"TEMP_PATH":self.path, "INTERCHAIN_AS_VALENCE":self.SHOW_INTER_AS_VALENCE,"DEFAULT_CMAP":self.default_cmap,\
                "TPA_COLOR":self.default_tpa_color,"TPE_COLOR":self.default_tpe_color,"FP_COLOR":self.default_fp_color}



        options_frame = Tk.Frame(self.configure_window)
        Tk.Label(options_frame, text="Default colormap").grid(column=0,row=0)
        cmap = Tk.StringVar()
        cmap.set(self.default_cmap)
        vv = AutocompleteCombobox(options_frame, textvar=cmap, width=8)  # , variable, *OPCJE)
        vv.set_shortlist(["gist_ncar", "bwr", "BinaryTP"])
        vv.set_completion_list([str(m) for m in cm.datad if not m.endswith("_r")])
        vv.grid(column=1,row=0)

        Tk.Label(options_frame, text="Show interchain contacts\nas valence instead of dotted line").grid(column=0, row=1)
        valence = Tk.BooleanVar()
        valence.set(self.SHOW_INTER_AS_VALENCE)
        Tk.Checkbutton(options_frame, text="", variable=valence).grid(column=1, row=1)

        Tk.Label(options_frame, text="Select path for temporary files").grid(column=0,row=2)
        files = []
        Tk.Button(master=options_frame, text='Open', command=lambda: self.ask_for_path(files.self.path)).grid(column=1,row=2)
        Tk.Label(options_frame, text="Select DPI for images when saving").grid(column=0,row=3)
        dpi = Tk.IntVar()  # native cutoff
        dpi.set(self.default_dpi)
        Tk.Spinbox(options_frame, textvariable=dpi, from_=100, to=2400,increment=100, width=5).grid(column=1,row=3)
        options_frame.grid(column=0,row=0)

        TPcolor_frame=Tk.LabelFrame(self.configure_window,text="Coloring contacts by nativeness")

        colors=map(str,mpl.colors.cnames.keys())

        Tk.Label(TPcolor_frame, text="Intrachain True Positives").grid(column=0, row=0)
        tpa = Tk.StringVar()
        tpa.set(self.default_tpa_color)
        #Tk.Entry(TPcolor_frame, width=8, textvariable=tpa).grid(column=1, row=0)
        combo1 = AutocompleteCombobox(TPcolor_frame, textvar=tpa, width=8)
        combo1.set_shortlist(['blue', 'green', 'red', 'cyan', 'magenta', 'yellow'])
        combo1.set_completion_list(colors)
        combo1.grid(column=1, row=0)
        Tk.Label(TPcolor_frame, text="Interchain True Positives").grid(column=0, row=1)
        tpe = Tk.StringVar()
        tpe.set(self.default_tpe_color)
        #Tk.Entry(TPcolor_frame, width=8, textvariable=tpe).grid(column=1, row=1)
        combo2 = AutocompleteCombobox(TPcolor_frame, textvar=tpe, width=8)
        combo2.set_shortlist(['blue', 'green', 'red', 'cyan', 'magenta', 'yellow'])
        combo2.set_completion_list(colors)
        combo2.grid(column=1, row=1)
        Tk.Label(TPcolor_frame, text="False Positives").grid(column=0, row=2)
        fp = Tk.StringVar()
        fp.set(self.default_fp_color)
        #Tk.Entry(TPcolor_frame, width=8, textvariable=fp).grid(column=1, row=2)
        combo3 = AutocompleteCombobox(TPcolor_frame, textvar=fp, width=8)
        combo3.set_shortlist(['blue', 'green', 'red', 'cyan', 'magenta', 'yellow'])
        combo3.set_completion_list(colors)
        combo3.grid(column=1, row=2)
        TPcolor_frame.grid(column=0,row=1)


        def _save_and_quit():
            with open(conf_file,"w",0) as out:
                out.write("{}\t{}\n".format("TEMP_PATH", (files[0] if files and files[0] is not None else self.path).encode('string-escape')))
                out.write("{}\t{}\n".format("INTERCHAIN_AS_VALENCE", valence.get()))
                out.write("{}\t{}\n".format("DPI", dpi.get()))
                self.SHOW_INTER_AS_VALENCE = valence.get()
                try:
                    cm.get_cmap(cmap.get())
                    out.write("{}\t{}\n".format("DEFAULT_CMAP",cmap.get()))
                except:
                    out.write("{}\t{}\n".format("DEFAULT_CMAP", self.default_cmap))
                new_colors = [fp.get() if fp.get() in colors else self.default_fp_color, \
                              tpa.get() if tpa.get() in colors else self.default_tpa_color, \
                              tpe.get() if tpe.get() in colors else self.default_tpe_color]
                out.write("{}\t{}\n".format("TPA_COLOR",  new_colors[0]))
                out.write("{}\t{}\n".format("TPE_COLOR", new_colors[1]))
                out.write("{}\t{}\n".format("FP_COLOR",  new_colors[2]))
                self.SSMenu.entryconfig(8, label="Toggle True Positives(intrachain) - " + self.default_tpa_color)
                self.SSMenu.entryconfig(9, label="Toggle True Positives(interchain) - " + self.default_tpe_color)
                self.SSMenu.entryconfig(10, label="Toggle False Positives - " + self.default_fp_color)
                ###MAKE NEW TP CMAP
                self.TP_cmap,self.TP_norm = self._make_new_TP_cmap(new_colors)
                #### END
                self.configure_window.quit()
                self.configure_window.destroy()

        Tk.Button(master=self.configure_window, text='Save', command=_save_and_quit).grid(column=0, row=2)
        self.configure_window.mainloop()

    def _make_new_TP_cmap(self,new_colors=[]):
        if not new_colors:
            new_colors = [self.default_fp_color,self.default_tpa_color,self.default_tpe_color]
        cmap = plt.cm.jet.from_list("moja", new_colors, 3)
        norm = mpl.colors.BoundaryNorm([0, 1, 2,3], 3)
        return cmap,norm

    def _quit(self,asked=False,parent=False):
        if parent:
            self.parent.destroy()
            self.parent.quit()
            return
        if asked or tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            pass
        else:
            return
        self._delete_temp_files()
        self.clear_pymol_bonds()
        self.root.quit()  # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    def _reset(self):
        self._quit(asked=True)
        dcaMOL(self.app,self.discores.get(),self.alignment.get())

    def _reset_old(self):
        print "Resetting DCA-MOL..."
        self.show_bond_selection.trace_vdelete(*self.show_bond_selection.trace_vinfo()[0])
        self.map_structure_mode.trace_vdelete(*self.map_structure_mode.trace_vinfo()[0])
        self.comp_atom_mode.trace_vdelete(*self.comp_atom_mode.trace_vinfo()[0])
        self.comp_distance.trace_vdelete(*self.comp_distance.trace_vinfo()[0])
        self.mark_on_similar_just_within_cutoff.trace_vdelete(*self.mark_on_similar_just_within_cutoff.trace_vinfo()[0])
        self.colormap.trace_vdelete(*self.colormap.trace_vinfo()[0])
        self.spin_min_var.trace_vdelete(*self.spin_min_var.trace_vinfo()[0])
        self.spin_max_var.trace_vdelete(*self.spin_max_var.trace_vinfo()[0])
        self.restrict_to_structure_var.trace_vdelete(*self.restrict_to_structure_var.trace_vinfo()[0])
        self.trueness_show_intra.trace_vdelete(*self.trueness_show_intra.trace_vinfo()[0])
        self.trueness_show_inter.trace_vdelete(*self.trueness_show_inter.trace_vinfo()[0])
        self.trueness_show_false.trace_vdelete(*self.trueness_show_false.trace_vinfo()[0])


        self.show_bond_selection.set(0)
        self.trueness_show_intra.set(1)
        self.trueness_show_inter.set(1)
        self.trueness_show_false.set(1)
        self.all_combos_var.set(0)
        self.recolor_by_trueness_var.set(0)
        self.recolor_by_any_trueness.set(0)
        self.comp_mode.set(0)
        self.restrict_to_structure_var.set(0)
        self.mark_on_similar.set(0)
        self.mark_on_similar_just_within.set(0)
        self.map_structure_mode.set(self.OPCJE[0])
        self.comp_atom_mode.set(dm.Structure.available_modes[0])
        self.menu_atom_mode = None
        self.rna_nonwc_pairs.set(0)
        self.comp_distance.set(8.)
        self.mark_on_similar_just_within_cutoff.set(24.0)
        self.current_state_var.set(1)
        self.last_state_var.set(1)
        self.colormap.set(self.default_cmap)
        self.cmapa = cm.get_cmap(self.colormap.get())
        mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                  norm=self.norm,
                                  orientation='vertical')
        self.cmap_canvas.draw()
        self.slider_min.set(0.001)
        self.slider_max.set(1)
        self.cmapa.set_bad(color="0.75")
        self.cmapa.set_over(color="black")
        self.cmapa.set_under(color="white")
        self.window_of_selected_bonds.withdraw()
        self.wait_window.withdraw()
        try:
            #self.configure_window.quit()
            self.configure_window.destroy()
        except AttributeError:
            pass

        self.current_structure_var = None
        self.current_structure_obj_var = None

        self.root.withdraw()
        self._delete_temp_files()
        for structure in self.STRUCTURES:
            cmd.delete(structure.objId)
            self.STRUCTURES = []
        self.clear_pymol_bonds()
        self.SELECTED_REGIONS = []

        #self.loader_window.deiconify()
        self.loader_window.destroy()

        #print vars(self.app)
        #print help(self.parent)

        self.__init__(self.app)

    def _on_closing(self,parent=False):
        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            self._quit(True,parent)

    def _save(self):
        #exts = {0:".png",1:".svg",2:".eps"}
        ftypes = [('Portable Network Graphics', '*.png'),\
                  ('Scalable Vector Graphics', '*.svgz'), \
                  ('Tagged Image File Format', '*.tiff'), ('Joint Photographic Experts Group', '*.jpg'), \
                  ('Raw RGBA bitmap', '*.raw'), ('Joint Photographic Experts Group', '*.jpeg'), \
                   ('Postscript', '*.ps'), ('Scalable Vector Graphics', '*.svg'), \
                  ('Encapsulated Postscript', '*.eps'), ('Raw RGBA bitmap', '*.rgba'), \
                  ('Portable Document Format', '*.pdf'), ('Tagged Image File Format', '*.tif')]
        if LATEX_FOUND:
            ftypes.append(('PGF code for LaTeX', '*.pgf'))
        plik = tkFileDialog.asksaveasfilename(filetypes=ftypes)
        print "Saving {} ... ".format(plik),
        """if vector>0:
            if "Single" in self.map_structure_mode.get():
                self.makeSSplot(mesh=True)
            else:
                heatmap = self.aplot.pcolormesh(self.data, cmap=self.cmapa,vmin=self.slider_min.get(),vmax=self.slider_max.get())
                self.canvas.draw()"""

        self.FIGURE.savefig(plik,format=plik.split(".")[-1],dpi=self.default_dpi)
        """if "Single" in self.map_structure_mode.get():
            self.makeSSplot()
        else:
            heatmap = self.aplot.pcolorfast(self.data, cmap=self.cmapa,vmin=self.slider_min.get(),vmax=self.slider_max.get())
            self.canvas.draw()"""
        print "Done"


    def wait(self, message):
        self.wait_window_message.set(message)
        self.wait_window.deiconify()
        self.wait_window.update_idletasks()
        self.wait_window.update()
        #win = Tk.Toplevel(self.root)
        #self.wait_window.transient()

    def _wait_in_progress(self, progress):
        self.wait_window_progress.set(progress)
        self.wait_window.update_idletasks()
        self.wait_window.update()



    def keydown_all(self,event):
        if event.keysym=="Control_L" or event.keysym=="Control_R":
            self.HELD_CTRL.set(True)

    def keyup_all(self,event):
        if event.keysym=="Control_L" or event.keysym=="Control_R":
            self.HELD_CTRL.set(False)

    def dcaMOL_main(self):
        root = self.loader_window
        root.title("Starting dcaMOL")

        but_la_label = Tk.StringVar()
        but_la_label.set("Load alignment")
        but_ld_label = Tk.StringVar()
        but_ld_label.set("Load DI scores")

        def shorten(tk_var):
            fname = ntpath.basename(tk_var.get())
            if len(fname) > 15:
                fname = fname[:10] + "(...)"
            return fname

        def load_alignment(*args):
            file = tkFileDialog.askopenfilename(parent=root, filetypes=[('MSA files', '*.fa *.fasta *.msa *txt'),
                                                                               ('All files', '.*')],
                                                       title="Select your alignment file")
            if not file:
                return
            self.alignment.set(file)
            print "Alignment scores will be read from:", self.alignment.get()
            but_la_label.set("Load alignment from {}".format(shorten(self.alignment)))
            if self.discores.get() and self.alignment.get():
                starter0.config(state="normal")
                starter1.config(state="normal")

        def load_discores(*args):
            file = tkFileDialog.askopenfilename(parent=root, filetypes=[('DI files', ('*.dca *.di *.DI')), ('All files', '.*')],
                                             title="Select your DI file")
            if not file:
                return
            self.discores.set(file)
            but_ld_label.set("Load DI scores from {}".format(shorten(self.discores)))
            print "DI scores will be read from:",self.discores.get()
            if self.discores.get() and self.alignment.get():
                starter0.config(state="normal")
                starter1.config(state="normal")

        but_la_label = Tk.StringVar()
        but_la_label.set("Load alignment")
        but_ld_label = Tk.StringVar()
        but_ld_label.set("Load DI scores")

        but_la = Tk.Button(root, textvariable=but_la_label, command=load_alignment)
        but_la.grid(row=0,column=0,columnspan=2)

        but_ld = Tk.Button(root, textvariable= but_ld_label, command=load_discores)
        but_ld.grid(row=1,column=0,columnspan=2)

        #starter0 = Tk.Button(root, text="Start analyzing!", command=self.start_plot)
        starter0 = Tk.Button(root, text="Start analysis\n(single state)", command=lambda: self.start_plot(0))
        starter0.config(state="disabled")
        starter0.grid(row=2,column=0)

        starter1 = Tk.Button(root, text="Start analysis\n(multi state)", command=lambda: self.start_plot(1))
        starter1.config(state="disabled")
        starter1.grid(row=2,column=1)

        if self.alignment.get() and self.discores.get():
            but_la_label.set("Load alignment from {}".format(shorten(self.alignment)))
            but_ld_label.set("Load DI scores from {}".format(shorten(self.discores)))
            starter0.config(state="normal")
            starter1.config(state="normal")

    def ask_for_structures(self,headers, selected):
        self.sequence_selection_window = Tk.Toplevel(self.root)
        self.sequence_selection_window.title("Select")
        Tk.Label(master=self.sequence_selection_window,text="For which sequence(s) from the alignment do you want to assign a structure?").grid(row=0,column=0,columnspan=2)
        sequence_selection = Tk.Listbox(self.sequence_selection_window, selectmode='multiple', exportselection=0,width=max(len(x) for x in headers))
        sequence_selection.grid(row=1,column=0,columnspan=2)
        for header in headers:
            sequence_selection.insert(Tk.END, header)

        def get_selected(is_rna,*args):
            if is_rna:
                self.is_rna.set(1)
            items = map(int, sequence_selection.curselection())
            for i in items:
                selected.append(sequence_selection.get(i))
            self.sequence_selection_window.quit()
            self.sequence_selection_window.destroy()

        sequence_selection_scroll = Tk.Scrollbar(self.sequence_selection_window)
        sequence_selection_scroll.config(command=sequence_selection.yview)
        sequence_selection_scroll.grid(row=1, column=2, sticky='ns')
        sequence_selection.config(yscrollcommand=sequence_selection_scroll.set)

        sel_button_protein = Tk.Button(master=self.sequence_selection_window, text='Proceed\n(protein)', command=lambda : get_selected(0))
        sel_button_rna = Tk.Button(master=self.sequence_selection_window, text='Proceed\n(RNA/DNA)', command=lambda : get_selected(1))
        sel_button_protein.grid(row=2,column=0)
        sel_button_rna.grid(row=2, column=1)
        self.sequence_selection_window.mainloop()

    def read_pdb(self,variable, label):
        file = tkFileDialog.askopenfilename(filetypes=[('PDB files', '.pdb'), ('All files', '.*')],
                                                  title="Select your PDB file")
        if not file:
            return
        variable.set(file)
        label.set(ntpath.basename(variable.get()))  #TODO  unix filenames with backslashes - may fail

    def on_entry_click(self,event):
        entry = event.widget
        """function that gets called whenever entry is clicked"""
        #print entry
        #print vars(entry)
        if entry.get() == 'PDB ID':
           entry.delete(0, "end") # delete all the text in the entry
           entry.insert(0, '') #Insert blank for user input
           entry.config(fg = 'black')
    def on_focusout(self, event):
        entry = event.widget
        if entry.get() == '':
            entry.insert(0, 'PDB ID')
            entry.config(fg = 'grey')

    def ask_for_correct_ids(self, selected, mapping):
        self.sequence_selection_window = Tk.Toplevel(self.root)
        self.sequence_selection_window.wm_title("Specify PDB ids of those sequences/select a file")
        ## header # [pdb] Chain [] [load file] [select loaded] [] Keep similar [] DNA/RNA [Add more]

        currently_present = cmd.get_object_list('(all)')

        frames = []
        entries_vars = {}
        chains_vars = {}
        loaded_vars = {}
        filenames_vars = {}
        similar_vars = []
        cnt_vars = []
        del_butts = [None for x in selected]

        def del_row(vars):
            frame, index = vars
            row=cnt_vars[index]

            entries_vars[index].pop()
            chains_vars[index].pop()
            filenames_vars[index].pop()
            if loaded_vars[index]:
                loaded_vars[index].pop()
            #similar_vars[index].pop()
            cnt_vars[index] -= 1
            if row > 1:
#                print "Moving button from",row,"to",row-1
                del_butts[index].grid(row=row - 1, column=7,sticky="E")
            else:
#                print "reMoving button from", row
                del_butts[index].grid_forget()
                del_butts[index].destroy()
                del_butts[index] = None

            rf = frames[index].pop()
#            print rf
            for item in rf:
#                print item
                item.grid_forget()
                item.destroy()



        def add_row(frame, seqid, index):
            row = cnt_vars[index]+1
            cnt_vars[index]+=1
            rf = []#Tk.Frame(frame)
#            print "Adding row",frame,seqid,index,row
            f = frame
            if row == 0:
                header = Tk.Entry(f, relief=Tk.FLAT)
                header.insert(0, seqid)
                header.config(state="readonly")
                header.grid(row=row, column=0)
                rf.append(header)

            entries_vars[index] = entries_vars.get(index, [])
            chains_vars[index] = chains_vars.get(index, [])
            filenames_vars[index] = filenames_vars.get(index, [])
            loaded_vars[index] = loaded_vars.get(index, [])
            #similar_vars[index] = similar_vars.get(index, [])

            entries_vars[index] += [Tk.StringVar()]
            e = Tk.Entry(f, width=6, textvariable=entries_vars[index][row])
            e.insert(0, 'PDB ID')
            e.bind('<FocusIn>', self.on_entry_click)
            e.bind('<FocusOut>', self.on_focusout)
            e.config(fg='grey')
            e.grid(row=row, column=1)
            rf.append(e)
            Tk.Label(f, text="Chain:").grid(row=0, column=2)
            chains_vars[index] += [Tk.StringVar()]
            c = Tk.Entry(f, width=2, textvariable=chains_vars[index][row])
            c.grid(row=row, column=3)
            rf.append(c)
            filenames_vars[index] += [(Tk.StringVar(),Tk.StringVar())]
            filenames_vars[index][row][1].set("Load local file")
            fn = Tk.Button(f, textvariable=filenames_vars[index][row][1])
            fn['command'] = lambda index=index: self.read_pdb(*filenames_vars[index][row])
            fn.grid(row=row, column=4)
            rf.append(fn)
            if currently_present:
                loaded_vars[index] += [Tk.StringVar()]
                om = Tk.OptionMenu(f, loaded_vars[index][row], "Select already loaded", *currently_present)
                loaded_vars[index][-1].set("Select already loaded")
                om.grid(row=row, column=5)
                rf.append(om)
            if row == 0:
                similar_vars.append(Tk.BooleanVar())
                similar_vars[-1].set(0)
                if self.overall_mode != 1:
                    ks = Tk.Checkbutton(f, text="Keep chains with >90% identity", variable=similar_vars[-1])
                    ks.grid(row=row, column=6)
                    rf.append(ks)
            else:
                similar_vars[index].set(0)
            # if self.overall_mode == 1:
            #    keep_gay_utopia[-1]['state'] = Tk.DISABLED
            if row == 0:
                a = Tk.Button(f, text="Add more structures to this seq",
                              command=lambda vars=(f, seqid, index): add_row(*vars))
                a.grid(row=row, column=7)
            elif row == 1:
                a = Tk.Button(f, text="Delete this row",
                              command=lambda vars=(f, index): del_row(vars))
                a.grid(row=row, column=7,sticky="E")
                del_butts[index] = a
            else:
                del_butts[index].grid(row=row, column=7,sticky="E")
            #row_frame.grid(row=row,column=0)
            frames[index].append(rf)

        def read_one_row(i, row_num):
            taken_ids = cmd.get_object_list('(all)')
            keep_others = similar_vars[i].get()
            appendix = ""
            chain = chains_vars[i][row_num].get()
            if loaded_vars[i] and loaded_vars[i][row_num].get() != "Select already loaded":
                lv = loaded_vars[i][row_num].get()
                name = "DM_" + lv + appendix
                while name in taken_ids:
                    appendix = "_1" if not appendix else ("_%d" % (int(appendix.strip("_")) + 1))
                    name = "DM_" + lv + appendix
                cmd.copy(name, lv)
                mapping_id = [name, chain, keep_others, False]
            elif filenames_vars[i][row_num][0].get() not in ["Load local file", ""]:
                print "Loading from file", id
                nid = ntpath.splitext(ntpath.basename(filenames_vars[i][row_num][0].get()))[0]
                while nid + appendix in taken_ids:
                    appendix = "_1" if not appendix else ("_%d" % (int(appendix.strip("_")) + 1))
                cmd.load(filenames_vars[i][row_num][0].get(), nid + appendix)  # TODO: obj name as seq
                mapping_id = [nid + appendix, chain, keep_others, False]
                # mapping[id]=[".".join(filenames_vars[i].get().split("/")[-1].split(".")[:-1]),chains_vars[i].get()]
                # added = cmd.get_object_list('(all)')[-1]
                # cmd.split_chains(added)
            elif entries_vars[i][row_num].get():
                while entries_vars[i][row_num].get() + appendix in taken_ids:
                    appendix = "_1" if not appendix else ("_%d" % (int(appendix.strip("_")) + 1))
                print "Fetching for", i
                cmd.fetch(entries_vars[i][row_num].get(), entries_vars[i][row_num].get() + appendix)
                mapping_id = [entries_vars[i][row_num].get() + appendix, chain, keep_others, False]
            else:
                print "No selection for ", i, row_num
                mapping_id = None
            return mapping_id

        def get_selected(*args):
            for i, id in enumerate(selected):
                if similar_vars[i].get() and cnt_vars[i] != 0:
                    tkMessageBox.showinfo("Choose wisely",
                                          "You can't have both multiple structure per sequence and 'Keep similar chains' enabled at the same time!")
                    return

                mapping_id = []
                for x in xrange(cnt_vars[i] + 1):
                    row = read_one_row(i, x)
                    if row is not None:
                        mapping_id.append(row)
                if len(mapping_id) == 1:
                    mapping_id = mapping_id[0]
                    if similar_vars[i].get():
                        mapping_id[2] = 1
                elif len(mapping_id) > 1:
                    mapping_id[0][3] = mapping_id[1:]
                    mapping_id = mapping_id[0]
                else:
                    if tkMessageBox.askokcancel("No selection",
                                                "There is no valid structure specified for {}.\n Do you wish to continue regardless?".format(
                                                        id)):
                        selected[i] = None
                    else:
                        return
                mapping[id] = mapping_id
#            print mapping
            self.sequence_selection_window.quit()
            self.sequence_selection_window.destroy()

        for index, id in enumerate(selected):
            f = Tk.Frame(master=self.sequence_selection_window)
            frames.append([])
            cnt_vars.append(-1)
            # jako pierwszy prosta pozioma kreska?
#            print index,id
            add_row(f, id, index)
            f.grid(row=index,column=0)

        # entries[0].focus()
        sel_button = Tk.Button(master=self.sequence_selection_window, text='Done', command=get_selected)
        sel_button.grid(column=0, row=len(selected))
        self.sequence_selection_window.mainloop()

    def get_sequence_splits_for_structures(self,id, seq, mapid, results):
        text = "Indicate correct sequence breaks between {}\n on the sequence below by adding newlines.".format(
            ",".join([mapid[0]] + [x[0] for x in mapid[-1]]))
        self.sequence_splits_window = Tk.Toplevel(self.root)
        self.sequence_splits_window.wm_title("Specify sequence breaks")
        l = Tk.Label(self.sequence_splits_window, text=text)
        l.grid(row=0,column=0)
        e = Tk.Text(self.sequence_splits_window, width=80)
        e.insert(Tk.END, seq)
        e.grid(row=1,column=0)

        def done():
            results.append(str(e.get("1.0", Tk.END)).split())
            if len(results[-1]) - 1 == len(mapid[-1]):
                self.sequence_splits_window.quit()
                self.sequence_splits_window.destroy()
            else:
                tkMessageBox.showerror('Try again!', 'You have entered too {} breaks ({} instead of {}).'.format("few"
                    if len(results[-1]) - 1 < len(mapid[-1]) else "many", len(results[-1]) - 1, len(mapid[-1])))
                e.delete("1.0", Tk.END)
                e.insert(Tk.END, seq)

        def lucky():
            results.append(False)
            self.sequence_splits_window.quit()
            self.sequence_splits_window.destroy()

        b = Tk.Button(self.sequence_splits_window, text="OK", command=done)
        b.grid(row=2,column=0)
        b2 = Tk.Button(self.sequence_splits_window, text="Alternatively: Try your luck - we'll try to guess", command=lucky)
        b2.grid(row=3,column=0)
        self.sequence_splits_window.mainloop()

    def read_in_alignment(self):
        filename = self.alignment.get()
        allSeqs = []
        with open(filename) as infile1:
            gen = hf.read_in_headers(infile1)
            while True:
                try:
                    h = gen.next()
                    allSeqs.append(h.strip())
                except StopIteration:
                    break
        selected = []
        allSeqs = sorted(allSeqs)
        self.ask_for_structures(allSeqs, selected)
        with open(filename) as infile1:
            allSeqs = hf.get_seq_by_head(infile1, selected)
        mapping = {}
        if allSeqs:
            self.ask_for_correct_ids(selected, mapping)  # TODO autofill entry if id[:4] in PDB?
        for id in mapping.keys():
            if mapping[id] is None:
                del mapping[id]
                continue
            if mapping[id][-1]:
                res = []
                self.get_sequence_splits_for_structures(id, allSeqs[id], mapping[id], res)
                mapping[id].append(res[-1])
            else:
                mapping[id].append(None)
        importantSeqs = {h: [allSeqs[h]] + mapping[h] for h in selected if h and h in mapping.keys()}

        return importantSeqs  # TODO - somehow check if homopolymer

    def ask_for_start(self,minimal, actual):
        def send_result(entry):
            try:
                out = int(entry.get())
            except ValueError:
                tkMessageBox.showinfo("Alert", "Invalid value: not an integer!")
                return
            actual.set(out)
            self.asker.quit()
            self.asker.destroy()

        self.asker = Tk.Toplevel(self.root)
        self.asker.title("Action needed")
        Tk.Label(self.asker,
                 text="Your residue indices start at {},\nwhat index corresponds to the first column\nof the alignmnent?".format(
                     minimal)).grid(row=0, column=0)
        val = Tk.IntVar()
        val.set(minimal)
        vale = Tk.Entry(self.asker, width=3, textvariable=val)
        vale.grid(row=1,column=0)
        vale.focus()
        Tk.Button(master=self.asker, text='Done', command=lambda: send_result(val)).grid(row=2,column=0)
        self.asker.mainloop()

    def slider_min_change(self,*args):  # TODO - wywalic bondy ponizej wartosci
        if self.slider_min.get() > self.slider_max.get():
            self.slider_max.set(self.slider_min.get())
        if self.map_structure_mode.get() != self.OPCJE[0] and \
                (self.recolor_by_trueness_var.get() or self.recolor_by_any_trueness.get()):
            self.makeSSplot()
        else:
            if self.colormap.get() == "BinaryTP":
                cmapa, norm = self.binaryColormap()
                heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, norm=norm, vmin=self.slider_min.get(), vmax=self.slider_max.get())
            else:
                norm = None
                cmapa = cm.get_cmap(self.colormap.get())
                heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, vmin=self.slider_min.get(), vmax=self.slider_max.get())
            self.cmapa = cmapa
            self.norm = norm
            #self.recolor_by_trueness_var.set(False)
            #print "Slider recalc", self.HELD_LMB.get()
            if not self.HELD_LMB.get():
            #    print "Recalcing"
                self.recalcTPrate()
            self.canvas.draw()
        mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                  norm=self.norm,
                                  orientation='vertical')
        #self.
        self.LAST_HIT_KEY.set(0)
        self.spin_min_var.set(self.slider_min.get())

        self.cmap_canvas.draw()
        self.redraw_bonds()

    def spin_min_change(self,*args):
        if not self.LAST_HIT_KEY.get():
            return
        self.slider_min.set(self.spin_min.get())
        if not self.recolor_by_trueness_var.get() and not self.recolor_by_any_trueness.get():
            self.spin_min_var_4cmap.set(str(self.spin_min.get()))

    def spin_max_change(self,*args):
        if not self.LAST_HIT_KEY.get():
            return
        self.slider_max.set(self.spin_max.get())
        if not self.recolor_by_trueness_var.get() and not self.recolor_by_any_trueness.get():
            self.spin_max_var_4cmap.set(str(self.spin_max.get()))

    def slider_max_change(self,*args):  ## TODO (?) - wywalic bondy powyzej
        self.LAST_HIT_KEY.set(0)
        self.spin_max_var.set(self.slider_max.get())
        if self.slider_min.get() > self.slider_max.get():
            self.slider_min.set(self.slider_max.get())
        if self.map_structure_mode.get() != self.OPCJE[0] and (self.recolor_by_trueness_var.get() or self.recolor_by_any_trueness.get()):
            self.makeSSplot()
        else:
            if self.colormap.get() == "BinaryTP":
                cmapa, norm = self.binaryColormap()
                heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, norm=norm, vmin=self.slider_min.get(), vmax=self.slider_max.get())
            else:
                norm = None
                cmapa = cm.get_cmap(self.colormap.get())
                heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, vmin=self.slider_min.get(), vmax=self.slider_max.get())
            self.cmapa = cmapa
            self.norm = norm
            #self.recolor_by_trueness_var.set(False)
            self.canvas.draw()
        mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                  norm=self.norm,
                                  orientation='vertical')
        self.cmap_canvas.draw()
        self.redraw_bonds()

    def slider_mid_change(self,*args):
        self.LAST_HIT_KEY.set(0)
        if self.slider_mid.get() > self.slider_max.get():
            self.slider_mid.set(self.slider_max.get())
        if self.slider_mid.get() < self.slider_min.get():
            self.slider_mid.set(self.slider_min.get())
        if self.map_structure_mode.get() != self.OPCJE[0]  and (self.recolor_by_trueness_var.get() or self.recolor_by_any_trueness.get()):
            self.makeSSplot()
        else:
            if self.colormap.get() == "BinaryTP":
                cmapa, norm = self.binaryColormap()
                heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, norm=norm, vmin=self.slider_min.get(), vmax=self.slider_max.get())
            else:
                norm = None
                cmapa = cm.get_cmap(self.colormap.get())
                heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, vmin=self.slider_min.get(), vmax=self.slider_max.get())
            self.cmapa = cmapa
            self.norm = norm
            #self.recolor_by_trueness_var.set(False)
            self.canvas.draw()
        mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                  norm=self.norm,
                                  orientation='vertical')
        self.cmap_canvas.draw()
        self.redraw_bonds()


    def keydown(self,event):
        self.LAST_HIT_KEY.set(event.keysym=="Return")
        self.colormap_change()
    def onclick(self,*args):
        self.LAST_HIT_KEY.set(1)

    def colormap_change(self,*args):
        if not self.LAST_HIT_KEY.get():
            return
        if self.colormap.get() == "BinaryTP":
            cmapa, norm = self.binaryColormap()
            cmapa.set_bad(color="0.75")
            cmapa.set_over(color="black")
            cmapa.set_under(color="white")
            heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, norm=norm, vmin=self.slider_min.get(), vmax=self.slider_max.get())
            self.sl_mid.grid(column=0, row=3)
#            self.slider_mid.pack(side=Tk.LEFT)
            self.slider_mid.set((self.slider_max.get() - self.slider_min.get()) / 2)
        else:
            #            if slider_mid: slider_mid[0].destroy()
            norm = None
#            self.slider_mid.pack_forget()
            self.sl_mid.grid_forget()
            cmapa = cm.get_cmap(self.colormap.get())
            cmapa.set_bad(color="0.75")
            cmapa.set_over(color="black")
            cmapa.set_under(color="white")
            heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, vmin=self.slider_min.get(), vmax=self.slider_max.get())
        self.cmapa = cmapa
        self.norm = norm
        self.recolor_by_trueness_var.set(False)
        self.recolor_by_any_trueness.set(False)
        self.recolor_by_trueness()
        for patch in self.SELECTED_REGIONS: ## TODO only draws on top
            self.draw_selected_patch(patch)
        self.canvas.draw()
        mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                  norm=self.norm,
                                  orientation='vertical')
        self.cmap_canvas.draw()
        self.redraw_bonds()

    def getTopXValues(self):
        try:
            X = int(self.top_values_cnt.get())
        except:
            tkMessageBox.showerror(message="There is something wrong with the entered value \n Error code: (PEBKAC)")
            return
        if X==-1:
            X=0
        if type(self.data) == np.ma.MaskedArray:
            cutoff = np.ma.sort(np.triu(self.data), axis=None, fill_value=0.)[-X]
        else:
            cutoff = np.sort(np.triu(self.data), axis=None)[-X]
        percent = X * 100. / ((self.data.shape[0] * self.data.shape[1] - self.data.shape[1]) / 2)
        self.top_values_pc.set(int(percent + 1))
        self.slider_min.set(cutoff)

    def getTopPCValues(self):
        try:
            PC = int(self.top_values_pc.get())
        except:
            tkMessageBox.showerror(message="There is something wrong with the entered value \n Error code: (PEBKAC)")
            return
        if PC==-1:
            X=0
        else:
            X = int(((self.data.shape[0] * self.data.shape[1] - self.data.shape[1]) / 2) * (PC / 100.))
        self.top_values_cnt.set(int(X))
        if type(self.data) == np.ma.MaskedArray:
            cutoff = np.ma.sort(np.triu(self.data), axis=None, fill_value=0.)[-X]
        else:
            cutoff = np.sort(np.triu(self.data), axis=None)[-X]
        self.slider_min.set(cutoff)

    def spin_comp_distance_change(self,*args):
        if not self.LAST_HIT_KEY.get():
            return
        self.makeSSplot()
    def spin_comp_distance_click(self,*args):
        self.makeSSplot()


    def spin_comp_distance_key(self,event):
        self.LAST_HIT_KEY.set(event.keysym in ["Return", "KP_Enter", "Extended-Return"])
        if not self.LAST_HIT_KEY.get():
            return
        self.makeSSplot()

    def spin_min_change_key(self,event):
        self.LAST_HIT_KEY.set(event.keysym in ["Return", "KP_Enter", "Extended-Return"])
        if not self.LAST_HIT_KEY.get():
            return
        self.spin_min_change()

    def spin_max_change_key(self,event):
        self.LAST_HIT_KEY.set(event.keysym in ["Return", "KP_Enter", "Extended-Return"])
        if not self.LAST_HIT_KEY.get():
            return
        self.spin_max_change()

    def mosjws_key(self,event):
        self.LAST_HIT_KEY.set(event.keysym in ["Return", "KP_Enter", "Extended-Return"])
        if not self.LAST_HIT_KEY.get():
            return
        if self.mark_on_similar_just_within.get() and any(
                [len(x) == 1 or x[0].split()[3] != x[1].split()[3] for x in self.DRAWN_BONDS]):
            self.redraw_bonds()
        self.makeSSplot()

    def mosjwc_change(self,*args):

        if not self.LAST_HIT_KEY.get():
            return
        if self.mark_on_similar_just_within.get() and any(
                [len(x) == 1 or x[0].split()[3] != x[1].split()[3] for x in self.DRAWN_BONDS]):
            self.redraw_bonds()
        self.makeSSplot()
    def menu_atom_mode_change(self,*args):
        dm.Structure.mode = self.comp_atom_mode.get()
        self.clear_pymol_bonds()
        for structure in self.STRUCTURES:
            structure.makeContactMap(self.current_state_var.get(), mchain=False)
            if structure.chains_to_keep:
                structure.makeContactMap(self.current_state_var.get(), mchain=True)

        if dm.Structure.isRNA:
            if "anonical" in self.comp_atom_mode.get():
                self.rna_nonwc_pairs_check.grid(column=0, row=2)
                self.dist_frame.grid_forget()
            else:
                self.rna_nonwc_pairs_check.grid_forget()
                self.dist_frame.grid(column=1, row=0)
        self.makeSSplot()

    def show_bonds_window(self, *args):
        if self.show_bond_selection.get():
            self.window_of_selected_bonds.deiconify()
        else:
            self.window_of_selected_bonds.withdraw()
    def update_list_of_bonds(self):
        #self.window_of_selected_bonds_text.set("")
        self.window_of_selected_bonds_text.config(state=Tk.NORMAL)
        self.window_of_selected_bonds_text.delete('1.0',Tk.END)
        print "Updating"
        def get_res(s):
            try:
                i = s.split("i. ")[1].split()[0]
                c = s.split("c. ")[1].split()[0]
                return (i+c.strip())
            except:
                raise IndexError(s)
        #self.window_of_selected_bonds_text.delete(1.0, Tk.END)
        text = "Currently selected residue pairs:\n"
        #print self.DRAWN_BONDS
        for x in self.DRAWN_BONDS:
            if x[0][:5] == "dist_":
                text+="{}\t{}\n".format(x[1],x[2])
            else:
                text+="\t".join(map(get_res, x[:2]))+"\n"
        #text += "\n".join( "\t".join(map(get_res, x[:2])) for x in self.DRAWN_BONDS)
        #print text
        #self.window_of_selected_bonds_text.set(text[:-1])#.insert(Tk.END,text)
        self.window_of_selected_bonds_text.insert('1.0', text)
        self.window_of_selected_bonds_text.config(state="disabled")


    def draw_selected_from_pymol(self):
        structure = self.current_structure_obj_var
        for mer in self.SELECTED_MERS:
            if self.restrict_to_structure_var.get():
                idx  = structure.translations.pdb2structseq
            else:
                idx = structure.translations.resid2unal_fasta(mer)
        #l = lines.Line2D




    def binaryColormap(self):
        cmapa = colors.ListedColormap(['grey','red','blue'])
        bounds = [0.,self.slider_min.get(),self.slider_mid.get(),self.slider_max.get()]
        norm = colors.BoundaryNorm(bounds, cmapa.N)
        return cmapa,norm

    def binaryColormapColor(self,value):
        return (.5,.5,.5,1.) if value<self.slider_min.get() else (1.,0.,0.,1.) if value<=self.slider_mid.get() else (0.,0.,1.,1.)

    def comparison_mode_engaged(self,*args):
        self.clear_pymol_bonds()
        self.SELECTED_REGIONS=[]
        #self.window_of_selected_bonds_text.set("")
        self.window_of_selected_bonds_text.config(state=Tk.NORMAL)
        self.window_of_selected_bonds_text.delete('1.0',Tk.END)
        self.window_of_selected_bonds_text.config(state="disabled")
        #if self.comp_mode.get():
        #    self.spin_comp_distance.pack(side=Tk.TOP)
        #    self.menu_atom_mode.pack(side=Tk.TOP)
        #else:
        #    self.spin_comp_distance.pack_forget()
        #    self.menu_atom_mode.pack_forget()
        self.makeSSplot()

    def recolor_by_any_trueness_do(self, *args):
        self.recolor_by_trueness(any=True)

    def recolor_by_trueness(self,any=False,*args):
        #self.recolor_by_trueness_var.set( not self.recolor_by_trueness_var.get()) #TODO WTF
        if any and self.recolor_by_any_trueness.get():
            self.recolor_by_trueness_var.set(0)
        if not any and self.recolor_by_trueness_var.get():
            self.recolor_by_any_trueness.set(0)

        if (self.recolor_by_trueness_var.get() or self.recolor_by_any_trueness.get()):
            #self.toggleTP = Tk.Checkbutton(self.left_controls,text="Toggle True Positives (intrachain)",variable=self.trueness_show_intra) #,command=lambda: makeSSplot)
            """self.toggleTP.pack()
            #self.toggleTPm = Tk.Checkbutton(self.left_controls,text="Toggle True Positives (interchain)",variable=self.trueness_show_inter) #,command=lambda: makeSSplot)
            self.toggleTPm.pack()
            #self.all_combos_check = Tk.Checkbutton(self.left_controls,text="Consider interchain contacts only with the main chain",variable=self.all_combos_var) #,command=lambda: makeSSplot)

            #self.all_combos_check.pack()

            #self.toggleFP = Tk.Checkbutton(self.left_controls,text="Toggle False Positives",variable=trueness_show_false) #,command=lambda: makeSSplot)
            self.toggleFP.pack()"""

            self.SSMenu.entryconfig(8, state=Tk.NORMAL)
            self.SSMenu.entryconfig(9, state=Tk.NORMAL)
            self.SSMenu.entryconfig(10, state=Tk.NORMAL)

            self.spin_min_var_4cmap.set("FP")
            self.spin_max_var_4cmap.set("TP (intra)")


        else:
            """self.toggleTP.pack_forget()
            self.toggleTPm.pack_forget()
            #self.all_combos_check.pack_forget()
            self.toggleFP.pack_forget()"""
            self.SSMenu.entryconfig(8, state=Tk.DISABLED)
            self.SSMenu.entryconfig(9, state=Tk.DISABLED)
            self.SSMenu.entryconfig(10, state=Tk.DISABLED)
            #print "spin min var",self.spin_min_var.get()
            self.spin_min_var_4cmap.set(str(self.spin_min_var.get()))
            self.spin_max_var_4cmap.set(str(self.spin_max_var.get()))
        if self.map_structure_mode.get() != self.OPCJE[0]:
            self.makeSSplot()
            #self.redraw_bonds()
        #self.clear_pymol_bonds()
        for patch in self.SELECTED_REGIONS: ## TODO only draws on top
            self.draw_selected_patch(patch)
        mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                  norm=self.norm,
                                  orientation='vertical')
        self.cmap_canvas.draw()
        self.canvas.draw()
        self.redraw_bonds()

    def alert_setting_change(self,*args):
        # tkMessageBox.showinfo("Tytul alertu", "Zmieniona wartosc na "+map_structure_mode.get())
        #self.comp_mode_check.pack_forget()
        #self.restrict_check.pack_forget()
        #self.recolor_by_trueness_check.pack_forget()

        ##TODO
        #self.spin_comp_distance.pack_forget()
        #self.menu_atom_mode.pack_forget()
        #self.cursor_position_frame.pack_forget()
        ##
        #self.toggle_show_bond_selection.pack_forget()
        #self.toggleTP.pack_forget()
        #self.toggleTPm.pack_forget()
        #self.toggleFP.pack_forget()
        self.SELECTED_MERS = []

        self.FIGURE.clf()
        self.clear_pymol_bonds()
        #        aplot = f.add_subplot(111)
        if "Single" in self.map_structure_mode.get():
            self.current_structure_var = self.map_structure_mode.get().split("ture: ")[1]
            self.current_structure_obj_var = [x for x in self.STRUCTURES if x.objId in self.current_structure_var][0]
            self.fileMenu.entryconfig(5,state=Tk.NORMAL)
            self.fileMenu.entryconfig(6,state=Tk.NORMAL)
            self.fileMenu.entryconfig(3, state=Tk.NORMAL)
            self.fileMenu.entryconfig(4, state=Tk.NORMAL)
            #    self.write_native_contacts_button.pack(side=Tk.LEFT)
            #    self.write_all_contacts_button.pack(side=Tk.LEFT)
            self.comp_mode.set(False)
            """self.comp_mode_check.pack()
            self.restrict_check.pack()
            self.recolor_by_trueness_check.pack()
            if self.overall_mode == 1:
                self.recolor_by_any_trueness_check.pack()"""

            self.menubar.entryconfig("Single structure plot", state=Tk.NORMAL)
            self.SSframe.grid(column=0,row=0)
            self.get_pymol_selection.grid(column=0, row=5, sticky="S")
            self.legend.grid(column=0, row=6, sticky="S")
            #self.spin_comp_distance.pack(side=Tk.TOP)
            #self.menu_atom_mode.pack(side=Tk.TOP)
            #self.cursor_position_frame.pack(side=Tk.TOP)
            #self.toggle_show_bond_selection.pack(side=Tk.TOP)
            self.makeSSplot()
        else:
            self.menubar.entryconfig("Single structure plot", state=Tk.DISABLED)
            self.SSframe.grid_remove()
            self.legend.grid_remove()
            self.get_pymol_selection.grid_remove()
            plt.subplots_adjust(left=0.03, bottom=0.03, right=1, top=1, wspace=0, hspace=0)
            self.current_structure_var = None
            self.current_structure_obj_var = None
            self.fileMenu.entryconfig(5,state=Tk.DISABLED)
            self.fileMenu.entryconfig(6,state=Tk.DISABLED)
            self.fileMenu.entryconfig(3,state=Tk.DISABLED)
            self.fileMenu.entryconfig(4,state=Tk.DISABLED)
            #    self.write_native_contacts_button.pack_forget()
            #    self.write_all_contacts_button.pack_forget()
            #self.spin_comp_distance.pack_forget()
            #self.menu_atom_mode.pack_forget()
            self.aplot = self.FIGURE.add_subplot(111)
            self.data = np.array(self.DATA_BACKUP)
            if self.colormap.get() == "BinaryTP":
                cmapa, norm = self.binaryColormap()
                heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, norm=norm, vmin=self.slider_min.get(),
                                           vmax=self.slider_max.get())
            else:
                norm = None
                cmapa = cm.get_cmap(self.colormap.get())
                heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, vmin=self.slider_min.get(), vmax=self.slider_max.get())
            self.cmapa = cmapa
            self.norm = norm
            self.recolor_by_trueness_var.set(False)
            self.recolor_by_any_trueness.set(False)
            self.canvas.draw()
        mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                  norm=self.norm,
                                  orientation='vertical')
        self.cmap_canvas.draw()


    def recalcTPrate(self):
        #print "recalcing TP rate"
        if (self.recolor_by_trueness_var.get() or self.recolor_by_any_trueness.get()):
            TPrate = (len(self.data2[np.triu(self.data2) == 1.]),
                      len(self.data2[np.triu(self.data2) == 0.1]))  # TP,FP  ## TODO co zrobic z interchain?
#            print "TPRATE", TPrate, sum(TPrate)
            self.TPrate.set("%5.2f%%" % (TPrate[0] * 100. / sum(TPrate)))
            self.TP_frame.grid(column=1, row=0, padx=10)
        else:
            if self.comp_mode.get():
                TPrate=0
                all=0
                for x in xrange(self.data.shape[0]):
                    for y in xrange(x+1,self.data.shape[0]):
                        #print x,y,self.data[x][y]
                        TPrate+=(type(self.data[x][y]) != np.ma.core.MaskedConstant and self.data[x][y]>self.slider_min.get() and type(self.data[y][x]) != np.ma.core.MaskedConstant and self.data[y][x]>0)
                        all+= (type(self.data[x][y]) != np.ma.core.MaskedConstant and self.data[x][y]>self.slider_min.get() and type(self.data[y][x]) != np.ma.core.MaskedConstant)
#                print "TPRATE",TPrate,all
                self.TPrate.set("%5.2f%%" % (TPrate*100./all))
                                #(TPrate*100./len(self.data[np.triu(self.data)>self.slider_min.get()])))
                self.TP_frame.grid(column=1, row=0, padx=10)

    def makeSSplot(self,*args,**kwargs):
        mesh =False
        if 'mesh' in kwargs and kwargs['mesh']:
            mesh = True
        if self.map_structure_mode.get() == self.OPCJE[0]:
            return
        self.clear_pymol_bonds()
        self.SELECTED_REGIONS = []
        self.TP_frame.grid_forget()
        self.FIGURE.clf()
        self.SS_plots = []
        restricted = self.restrict_to_structure_var.get()
        self.aplot = plt.subplot2grid((60, 60), (0, 6), colspan=55,
                                 rowspan=55)  # ,fig=FIGURE)#,fig=0)#FIGURE)#    add_subplot(211)
        my_struct = self.current_structure_obj_var
            #[x for x in self.STRUCTURES if x.objId in self.map_structure_mode.get().split(": ")[-1]][0]


        if (self.recolor_by_trueness_var.get() or self.recolor_by_any_trueness.get()):  # TODO recalc only on change
            self.data = my_struct.makeSSarray(self.DATA_BACKUP, comparison=self.comp_mode.get(), distance=self.comp_distance.get(),
                                         restricted=restricted, state=self.current_state_var.get(), nonwc=self.rna_nonwc_pairs.get())
            #if not restricted: self.data = self.DATA_BACKUP
            #else: self.data.mask = np.ma.nomask
            data2 = np.array(self.data)
            data2[data2 < self.slider_min.get()] = -0.1
            data2 = my_struct.recolorSSarray(data2, self.slider_min.get(), distance_intra=self.comp_distance.get(),
                                             distance_inter=self.mark_on_similar_just_within_cutoff.get(),
                                             restricted=restricted, comparison=self.comp_mode.get(),
                                             all_combos=(1 + self.all_combos_var.get()) % 2, state=self.current_state_var.get(),
                                             any=self.recolor_by_any_trueness.get(),nonwc = self.rna_nonwc_pairs.get())
            data2[data2 == 3.] = 1.  # TODO for now inter/intra are exclusive
            cmapa = self.TP_cmap#copy(cm.get_cmap("spring"))
            cmapa.set_bad(color="white")
            cmapa.set_over(color="black")  # "red")
            cmapa.set_under(color="white")
            norm = self.TP_norm#None
            #vmin = 0.5
            #vmax = 2.5
            bad = []
            if not self.trueness_show_intra.get():
                data2[data2 == 1.] = -1.
            if not self.trueness_show_inter.get():
                data2[data2 == 2.] = -1.
            if not self.trueness_show_false.get():
                data2[data2 == 0.1] = -1.  ## TODO some combos?
            data2 = np.ma.masked_where(data2 < -0.75, data2)
            self.data2 = data2
            if mesh:
                heatmap = self.aplot.pcolormesh(data2, cmap=cmapa,norm=norm, vmin=0.)#, vmax=vmax)
            else:
                heatmap = self.aplot.pcolorfast(data2, cmap=cmapa,norm=norm, vmin=0.)#, vmax=vmax)
            #self.wait_window.quit()
            if not self.HELD_LMB.get():
                self.recalcTPrate()
        else:
            self.data = my_struct.makeSSarray(self.DATA_BACKUP, comparison=self.comp_mode.get(), distance=self.comp_distance.get(),
                                         restricted=restricted, state=self.current_state_var.get(), nonwc=self.rna_nonwc_pairs.get())
            if self.colormap.get() == "BinaryTP":
                cmapa, norm = self.binaryColormap()
                cmapa.set_bad(color="0.75")
                cmapa.set_over(color="black")
                cmapa.set_under(color="white")
                if mesh:
                    heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, norm=norm, vmin=self.slider_min.get(),
                                               vmax=self.slider_max.get())
                else:
                    heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, norm=norm, vmin=self.slider_min.get(),
                                           vmax=self.slider_max.get())
            else:
                norm = None
                cmapa = cm.get_cmap(self.colormap.get())
                cmapa.set_bad(color="0.75")
                cmapa.set_over(color="black")
                cmapa.set_under(color="white")
                if mesh:
                    heatmap = self.aplot.pcolormesh(self.data, cmap=cmapa, vmin=self.slider_min.get(), vmax=self.slider_max.get())
                else:
                    heatmap = self.aplot.pcolorfast(self.data, cmap=cmapa, vmin=self.slider_min.get(), vmax=self.slider_max.get())
            mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                      norm=self.norm,
                                      orientation='vertical')
            self.cmap_canvas.draw()
            if not self.HELD_LMB.get():
                self.recalcTPrate()
            self.data2 = None
        self.cmapa = cmapa
        self.norm = norm
        self.SS_plots += my_struct.plotSS(self.FIGURE, self.aplot, restricted=restricted)
        #self.aplot.set_aspect('equal', 'datalim')
        self.canvas.draw()

    def lets_do_the_flip(self):
        def flip(x):
            if x=="L": return "R"
            else: return "L"

#        print "selected",self.SELECTED_REGIONS
        for i,reg in enumerate(self.SELECTED_REGIONS):
            self.SELECTED_REGIONS[i] = list(reg[:-1])+[flip(reg[-1])]
#        print "new selected", self.SELECTED_REGIONS
        for patch in self.SELECTED_REGIONS: ## TODO only draws on top
            self.draw_selected_patch(patch)
        self.canvas.draw()
        self.redraw_bonds()

    def add_pymol_bond_to_object_intra(self,res1,res2,color,obj=""):
        bonded_atom = "name CA and elem C"
        if dm.Structure.isRNA:
            bonded_atom = "name P and elem P"

        tmp_color_name = "tmp_color_%d" % len(self.DRAWN_BONDS)
        cmd.set_color(tmp_color_name,"[ %.3f, %.3f, %.3f ]" % color[:3])
        others = self.mark_on_similar.get()
        obj,clist,cmap,idx_ref = obj if obj else (False,False,False)

        for c in clist:
            for tmpi,chain in enumerate([c]+(cmap.get(c,[]) if others else [])):
                r1,r2 = res1,res2
                if others and tmpi:
                    r1 += idx_ref[(c,chain)]
                    r2 += idx_ref[(c,chain)]
                cmd.bond("%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj,chain) if obj else "", r1),
                            "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj,chain) if obj else "", r2))
                cmd.select("tmp_select","%s i. %d+%d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj,chain) if obj else "", r1,r2))
                cmd.show("sticks","tmp_select")
                cmd.set_bond("stick_color",tmp_color_name, #str(color[:3]),
                             "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj,chain) if obj else "", r1),
                            "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj,chain) if obj else "", r2))
                cmd.deselect()
                self.DRAWN_BONDS.append(("%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj,chain) if obj else "", r1),
                            "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj,chain) if obj else "", r2), r1,r2,obj))

    def add_pymol_bond_to_object_inter(self,res1, res2, color, obj=""):

        bonded_atom = "name CA and elem C"
        if dm.Structure.isRNA:
            bonded_atom = "name P and elem P"

        tmp_color_name = "tmp_color_%d" % len(self.DRAWN_BONDS)
        cmd.set_color(tmp_color_name, "[ %.3f, %.3f, %.3f ]" % color[:3])
        others = self.mark_on_similar.get()
        just_within = self.mark_on_similar_just_within.get()
        if just_within:
            just_within_cutoff = self.mark_on_similar_just_within_cutoff.get()
        obj, clist, cmap, idx_ref = obj if obj else (False, False, False)
        """try:
            assert len(obj.chain) == 1
        except:
            raise AssertionError("How did you manage to get both multichain and 'similar chains' options on? I refuse to work with a cheater")
        """
        my_list = clist #+ cmap[clist[0]]
        pairs_to_bond = []
        cmd.set('valence', 1)
        for tmpi, c in enumerate(my_list):
            for chain in my_list[tmpi + 1:]:
                r1, r2 = res1, res2
                r3, r4 = res1, res2
                r2 += idx_ref[(clist[0], chain)]
                r3 += idx_ref[(clist[0], chain)]
                if c not in clist:
                    if not others:
                        continue
                    r1 += idx_ref[(clist[0], c)]
                    r4 += idx_ref[(clist[0], c)]
                if not just_within:
                    pairs_to_bond.append((c, chain, r1, r2))
                    pairs_to_bond.append((chain, c, r3, r4))
                else:
                    a1 = "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj, c) if obj else "", r1)
                    a2 = "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj, chain) if obj else "", r2)
                    a3 = "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj, chain) if obj else "", r3)
                    a4 = "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj, c) if obj else "", r4)
                    din = cmd.distance("tmp", a1, a2)  # ,state=0)
                    dax = cmd.distance("tmp", a3, a4)  # ,state=0)
                    cmd.delete("tmp")
                    if din <= just_within_cutoff:
                        pairs_to_bond.append([c, chain, r1, r2])
                    if dax <= just_within_cutoff:
                        pairs_to_bond.append([chain, c, r3, r4])

        for c, chain, r1, r2 in pairs_to_bond:

            if self.SHOW_INTER_AS_VALENCE:
                cmd.bond(
                    "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj, c) if obj else "", r1),
                    "%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj, chain) if obj else "", r2),
                    2)
                cmd.select("tmp_select",
                           "(%s i. %d and {}) or (%s i. %d and {})".format(bonded_atom,bonded_atom) % (
                           "{} and c. {} and ".format(obj, c)
                           if obj else "", r1, "{} and c. {} and ".format(obj, chain) if obj else "", r2))
                cmd.show("sticks", "tmp_select")
                cmd.set_bond("stick_color", tmp_color_name,  # str(color[:3]),
                             "%s i. %d and {}".format(bonded_atom) % (
                             "{} and c. {} and ".format(obj, c) if obj else "", r1),
                             "%s i. %d and {}".format(bonded_atom) % (
                             "{} and c. {} and ".format(obj, chain) if obj else "", r2))
                #                    cmd.set_bond("valence",1, #str(color[:3]),
                #                                 "%s i. %d and name CA and elem C" % ("{} and c. {} and ".format(obj,c) if obj else "", r1),
                #                                "%s i. %d and name CA and elem C" % ("{} and c. {} and ".format(obj,chain) if obj else "", r2))
                cmd.deselect()
                self.DRAWN_BONDS.append(
                    ("%s i. %d and {}".format(bonded_atom) % ("{} and c. {} and ".format(obj, c) if obj else "", r1),
                     "%s i. %d and {}".format(bonded_atom) % (
                     "{} and c. {} and ".format(obj, chain) if obj else "", r2), r1, r2, obj))
            else:
                obj_name = "dist_{}".format(len(self.DRAWN_BONDS))
                cmd.distance(obj_name, "%s i. %d and {}".format(bonded_atom) % (
                "{} and c. {} and ".format(obj, c) if obj else "", r1),
                             "%s i. %d and {}".format(bonded_atom) % (
                             "{} and c. {} and ".format(obj, chain) if obj else "", r2))
                cmd.color(tmp_color_name, obj_name)
                cmd.hide("labels", obj_name)
                self.DRAWN_BONDS.append([obj_name,"{}{}".format(r1,c),"{}{}".format(r2,chain)])

    def clear_pymol_bonds(self):
        for bond in self.DRAWN_BONDS:
            if bond[0][:5]=="dist_":
                cmd.delete(bond[0])
            else:
#            if len(bond) > 1:
                cmd.unbond(*bond[:2])
#            else:
#                cmd.delete(bond[0])
            del bond
        self.DRAWN_BONDS = []

    def get_added_bonds(self):
        pass

    def add_pymol_bond(self,res1, res2, color, obj='', mode=0):
#        print "Adding?",mode, obj
        if mode == 0:
            self.add_pymol_bond_to_object_intra(res1, res2, color, obj)
        elif len(obj[1])>1:
#            print "Will add inter"
            self.add_pymol_bond_to_object_inter(res1, res2, color, obj)

    def bonds_in_patches(self, X, Y, structures=None, mode=0):
        if structures is None:
            structures = self.STRUCTURES
        single = "Single" in self.map_structure_mode.get()
        if single:
            structures = [self.current_structure_obj_var]
            #[x for x in self.STRUCTURES if x.objId in self.map_structure_mode.get().split(": ")[-1]]
        for structure in structures:  # active_structures:
            if not structure.active: continue
            for x in xrange(int(X[0]), int(X[1]) + 1):
                for y in xrange(int(Y[0]), int(Y[1]) + 1):
                    if not self.recolor_by_trueness_var.get() and not self.recolor_by_any_trueness.get():
                        value = self.data[min(x, y)][max(x, y)]
                        if value <= self.slider_min.get() or type(value) == np.ma.core.MaskedConstant:
                            continue
                    else:
                        value = self.data2[min(x, y)][max(x, y)]
                        if type(value) == np.ma.core.MaskedConstant:
                            continue
                    if single:
                        if self.restrict_to_structure_var.get():
                            #sx = structure.residues[x].pdbid
                            #sy = structure.residues[y].pdbid
                            #sx = structure.translations.struct2pdb(structure.translations.singleplot_restrict(x))
                            #sy = structure.translations.struct2pdb(structure.translations.singleplot_restrict(y))
                            sx = structure.translations.struct2pdb(x)
                            sy = structure.translations.struct2pdb(y)
                        else:
                            #sx = structure.SS_data_mapping[x][1][0] if structure.SS_data_mapping[x][1] else False
                            #sy = structure.SS_data_mapping[y][1][0] if structure.SS_data_mapping[y][1] else False
                            sx = structure.translations.struct2pdb(structure.translations.singleplot_bonds(x))
                            sy = structure.translations.struct2pdb(structure.translations.singleplot_bonds(y))
                    else:
                        sx = structure.translations.struct2pdb(structure.translations.fullplot2struct(x))
                        sy = structure.translations.struct2pdb(structure.translations.fullplot2struct(y))
#                        sx = structure.FS_data_to_struct(x)
#                        sy = structure.FS_data_to_struct(y)
                    if not sx or not sy: continue
                    color = self.get_bond_color(value)
#                    color = cmap(value / scale) if cmap else self.binaryColormapColor(value)
#                    print "Should add",sx,sy,color
                    self.add_pymol_bond(sx, sy, color, (structure.objId, structure.chain_list, structure.chain_map, structure.chain_idx_ref), mode=mode)
        if single:
            self.update_list_of_bonds()

    def get_bond_color(self,value):
        #cmap = self.colormap.get()
        #if cmap == "BinaryTP":
        #    return self.binaryColormapColor(value)
        #cmap = cm.get_cmap(cmap)
        #cmap = self.cmapa
        if (self.recolor_by_trueness_var.get() or self.recolor_by_any_trueness.get()):
            if value>2.5: value=2.5
            scale = 2.0
            #value -= 0.5
        else:
            if value>self.slider_max.get(): value=self.slider_max.get()
            scale = self.slider_max.get() - self.slider_min.get()
            #value -= self.slider_min.get()
        return self.cmapa((value-self.slider_min.get())/scale) #TODO a jak w binary colormap?



    def redraw_bonds(self,*args):
        self.clear_pymol_bonds()
        for X, Y, fp2 in self.SELECTED_REGIONS:
            self.bonds_in_patches(X, Y, mode=(fp2 == "R"))
        self.update_list_of_bonds()

    def draw_selected_patch(self, patch):
        X, Y, typ = patch
#        print "drawing selected patch"
#        print X
#        print Y
        X = map(int,X)
        Y = map(int,Y)

        if typ == "L":
            p = patches.Rectangle((X[0], Y[0]), (X[1] - X[0] + 1), (Y[1] - Y[0] + 1), ls='dashed',color="r", fill=0)
            self.aplot.add_patch(p)
            self.AXLINES.append(p)
            if self.comp_mode.get():
                r = patches.Rectangle((Y[0], X[0]), (Y[1] - Y[0] + 1), (X[1] - X[0] + 1), ls='dashed',color="r", fill=0)
                self.aplot.add_patch(r)
                self.AXLINES.append(r)

        elif typ == "R":
            p = patches.Rectangle((X[0], Y[0]), (X[1] - X[0] + 1), (Y[1] - Y[0] + 1), ls='dashed',color="g", fill=0)
            self.aplot.add_patch(p)
            self.AXLINES.append(p)
            if self.comp_mode.get():
                r = patches.Rectangle((Y[0], X[0]), (Y[1] - Y[0] + 1), (X[1] - X[0] + 1), ls='dashed',color="g", fill=0)
                self.aplot.add_patch(r)
                self.AXLINES.append(r)
        else:
            pass

    def mark_pymol_selection_on_plot(self):
        space = {'residues': []}
        cmd.iterate_state(1, "( %s ) and polymer and (sele)" % (self.current_structure_obj_var.objId),
                          "residues.append((resv,chain))",
                          space=space)
        selections,chains = hf.find_regions(space['residues'])
        if len(selections)!=2:
            tkMessageBox.showerror(message="You must select -exactly- two, non-consecutive (in terms or residue indices) regions!")
            return

        structure = self.current_structure_obj_var
        if len(chains)>1:
            selections = map(lambda x: x[0] if x[1]==structure.chain_simple else map(lambda y: y-structure.chain_idx_ref[(structure.chain_simple,x[1])],x[0]),selections)
        else:
            selections = map(lambda x: x[0],selections)

#        print "selections",selections
        X = selections[0]
        Y = selections[1]
#        print "pre", X,Y
        if self.restrict_to_structure_var.get():
            X = map(lambda x: structure.translations.pdb2structseq[x],X)
            Y = map(lambda x: structure.translations.pdb2structseq[x],Y)
        else:
            X = map(structure.translations.resid2unal_fasta,X)
            Y = map(structure.translations.resid2unal_fasta,Y)
        mode = "R" if len(chains)>1 else "L"
        X= filter(lambda x: x is not None,X)
        Y= filter(lambda x: x is not None,Y)
        if len(X)<2 or len(Y)<2:
            tkMessageBox.showerror(
                message="At least one of your selected regions does not appear in the DI scores file")
            return
        X=[X[0],X[-1]]
        Y=[Y[0],Y[-1]]
#        print "post", X, Y
#        print self.SELECTED_REGIONS
        self.SELECTED_REGIONS = [(X, Y, mode)]
#        print self.SELECTED_REGIONS
        if not self.HELD_CTRL.get():
            self.clear_pymol_bonds()
            for line in self.AXLINES:
                try:
                    line.remove()
                    del line
                except ValueError:
                    pass
                    self.AXLINES = []
        #if mode=="L" or len(chains)>1:
        self.draw_selected_patch((X, Y, mode))
        self.canvas.draw()
        self.bonds_in_patches(X, Y, structure, mode=(mode == "R"))


    def select_on_plot(self,final_pos):

        size = self.aplot.get_xlim()[1]#len(self.data) + 1
        #print "held ctrl=",self.HELD_CTRL.get()
        if not self.HELD_CTRL.get():
            self.clear_pymol_bonds()
            for line in self.AXLINES:
                try:
                    line.remove()
                    del line
                except ValueError:
                    pass
                    self.AXLINES = []

            if self.SELECTED_REGIONS and self.LAST_CLICKED_POS[0]==final_pos[0] and self.LAST_CLICKED_POS[1]==final_pos[1]:
                self.SELECTED_REGIONS = []
                self.canvas.draw()
                return

        X = [max(0, min([self.LAST_CLICKED_POS[0], final_pos[0]])), min(max([self.LAST_CLICKED_POS[0], final_pos[0]]), size)]
        Y = [max(0, min([self.LAST_CLICKED_POS[1], final_pos[1]])), min(max([self.LAST_CLICKED_POS[1], final_pos[1]]), size)]
        self.SELECTED_REGIONS.append((X, Y, final_pos[2]))
        s = []
        if final_pos[2]=="L" or any(len(x.chain_list)>1 for x in s):
            self.draw_selected_patch((X, Y, final_pos[2]))

        self.canvas.draw()
        if "Single" in self.map_structure_mode.get():
            #            pass
            s = [self.current_structure_obj_var]
            self.bonds_in_patches(X, Y, s, mode=(final_pos[2] == "R"))
            #[x for x in self.STRUCTURES if x.objId in self.map_structure_mode.get().split(": ")[-1] and
                              #x.active][:1]
        else:
            s=self.STRUCTURES
            self.bonds_in_patches(X, Y,  s, mode=(final_pos[2] == "R"))



        return

    def onclick_plot(self,event):
        if event.xdata is not None and event.ydata is not None:
            self.LAST_CLICKED_POS = [event.xdata, event.ydata, event.x, event.y]
        else:
            self.LAST_CLICKED_POS = None

    def onclick2_plot(self,event):

        self.size = len(self.data) + 1
        if self.LAST_CLICKED_POS is None:
            return
        xdat = event.xdata
        ydat = event.ydata
        if event.xdata is None:
            if event.x < self.LAST_CLICKED_POS[2]:
                xdat = 0
            else:
                xdat = self.aplot.get_xlim()[1]-1# size
        if event.ydata is None:
            if event.y < self.LAST_CLICKED_POS[3]:
                ydat = 0
            else:
                ydat = self.aplot.get_ylim()[1]-1# .size
        self.select_on_plot([xdat, ydat, self.BUTTONS[event.button]])
        self.LAST_CLICKED_POS = [xdat, ydat, event.x, event.y]

    def track_cursor(self, event):
        if self.map_structure_mode.get() == self.OPCJE[0]:
            return
        self.size = len(self.data) + 1
        #if self.LAST_TRACKED_POS is None:
        #    self.LAST_TRACKED_POS = [event.x,event.y]
        #    return
        xdat = event.xdata
        ydat = event.ydata
        if xdat is None or ydat is None:
            actualX = None
            actualY = None
        else:
            xdat,ydat = map(lambda x:int(x)-1,(xdat,ydat))
            actualX = self.current_structure_obj_var.translations.struct2pdb(xdat) if self.restrict_to_structure_var.get() else self.current_structure_obj_var.translations.singleplot_cursor(xdat)
            actualY = self.current_structure_obj_var.translations.struct2pdb(ydat) if self.restrict_to_structure_var.get() else self.current_structure_obj_var.translations.singleplot_cursor(ydat)
            if None in [actualX,actualY]:
                actualX,actualY = None,None
        #print "Pointing at",actualX, actualY
        self.current_cursor_position_X.set("% 5d" % actualX if actualX is not None else "  NaN")
        self.current_cursor_position_Y.set("% 5d" % actualY if actualY is not None else "  NaN")

    """def guess_if_protein(self,data):
        allowed = "actugACTUGnN.-"
        return any(set(allowed)!=set(x[0]+allowed) for x in data)"""

    """def confirm_if_rna(self):
        rna_win = Tk.Toplevel(self.root)
        Tk.Label(rna_win,text="Our guess is that you are working on RNA/DNA - is that correct?").pack()
        Tk.Button(rna_win,text="Yes",command=lambda: [self.is_rna.set(1), rna_win.quit(), rna_win.destroy()]).pack()
        Tk.Button(rna_win, text="No", command=lambda: [self.is_rna.set(0), rna_win.quit(),rna_win.destroy()]).pack()
        rna_win.mainloop()"""


    def start_plot(self, self_mode, *args):
        self.loader_window.withdraw()
        #self.loader_window.destroy()

        print "Setting mode to", self_mode
        self.overall_mode = self_mode

        # READ IN ALIGNMENT
        if self.alignment.get():
            importantSeqs = self.read_in_alignment()

            #self.is_rna.set(not self.guess_if_protein(importantSeqs.values()))

            #if self.is_rna.get():
            #    self.confirm_if_rna()
            if self.is_rna.get():
                dm.Structure.isRNA = True
                dm.Structure.mode = dm.Structure.available_modes_rna[0]
            else:
                dm.Structure.isRNA = False
                dm.Structure.mode = dm.Structure.available_modes[0]
            for seq, dane in importantSeqs.items():
                self.STRUCTURES.append(dm.Structure(dane[1], dane[2], seq, dane[0], dane[3], dane[4], splits=dane[-1]))


        _num = 1
        for structure in self.STRUCTURES:
            self.OPCJE.append("Single structure: " + structure.objId)
            structure.temp_path = self.path
            self.wait("Calculating native contacts map for {}".format(structure.objId))
            structure.makeMultiStateContactFile(progress=self._wait_in_progress)
            #print [vars(i) for i in structure.residues]
            structure.makeContactMap(1)
            #print [vars(i) for i in structure.residues]
            if self.overall_mode == 1:
                structure.makeAnyContactMaps()
            #print structure.objId, structure.chain_list, structure.chains_to_keep
            if structure.chains_to_keep:
                self.wait("Calculating interchain contacts map for {}".format(structure.objId))
                structure.makeMultiChainContactFile(progress=self._wait_in_progress)
                structure.makeContactMap(1,mchain=True)
            _num = max(_num, structure.num_states)
        self.wait_window.withdraw()
        self.last_state_var.set(_num)
        self.option_menu = Tk.OptionMenu(self.mode_frame, self.map_structure_mode, *self.OPCJE)
        self.option_menu.grid(column=0, row=0,sticky="NW")
        #self.quit_button.pack(side=Tk.RIGHT)
        #self.reset_button.pack(side=Tk.RIGHT)
        #self.save_png_button.pack(side=Tk.RIGHT)
        #self.save_svg_button.pack(side=Tk.RIGHT)

        if self.overall_mode == 1:
            self.SSMenu.entryconfig(6, state=Tk.NORMAL)
            self.states_frame.grid(column=2, row=0,padx=10)
        else:
            self.goto_first_button.forget()#grid(column=6, row=0, rowspan=2)
            self.current_state_spin.forget()#grid(column=7, row=0, rowspan=2)
            self.goto_last_button.forget()

        print "Will now read DI scores"
        size = 0
        with open(self.discores.get()) as input:
            #size = int(sqrt(len(input.readlines()) * 2))
            minimal_idx = None
            max_idx = None
            for line in input.readlines():
                line = line.split()
                if not line: continue
                if minimal_idx is not None:
                    minimal_idx = min(minimal_idx, int(line[1]), int(line[0]))
                else:
                    minimal_idx = min(int(line[1]), int(line[0]))
                if max_idx is not None:
                    max_idx = max(max_idx, int(line[1]), int(line[0]))
                else:
                    max_idx = max(int(line[1]), int(line[0]))

        self.data = [[0 for x in xrange(max_idx + 2)] for y in xrange(max_idx + 2)]
        skip = 0
        if minimal_idx != 0:
            actual_start = Tk.IntVar()
            self.ask_for_start(minimal_idx, actual_start)
            X, Y = len(self.data), len(self.data)
            skip = actual_start.get()
            #for x in xrange(X):
            #    for y in xrange(Y):
            #        if x + skip < X and y + skip < Y:
            #            self.data[x][y] = self.data[x + skip][y + skip]
            #        else:
            #            self.data[x][y] = 0

        with open(self.discores.get()) as input:
            check = True
            di_loc = Tk.IntVar()
            di_loc.set(2)
            for line in input.readlines():
                if check:
                    check = False
                    if len(line.split())>3:
                        #try:
                        #    _ = float(line[3])
                        #    di_loc.set(3)
                        #except:
                            loc = tkSimpleDialog.askinteger("Input","In which column ({}-{}) are the DI scores?\nExample line from your file:\n\n{}".format(1,len(line.split()),line), \
                                                             parent=self.root,minvalue=1,maxvalue=len(line.split()))
                            if loc is not None:
                                di_loc.set(loc-1)
                            else:
                                di_loc.set(len(line.split())-1)
                line = line.split()
                self.data[int(line[0])-skip][int(line[1])-skip] = float(line[di_loc.get()])  # /scale
                self.data[int(line[1])-skip][int(line[0])-skip] = float(line[di_loc.get()])





        self.UPPER_DATA_BOUND.set(max([max(i) for i in self.data]))
        self.DATA_BACKUP = np.array(self.data)
        self.data = np.array(self.DATA_BACKUP)
        # END READ IN DI
        self.slider_min.config(from_=self.UPPER_DATA_BOUND.get())
        self.spin_min.config(to=self.UPPER_DATA_BOUND.get())
        self.spin_max.config(to=self.UPPER_DATA_BOUND.get())
        self.slider_max.config(from_=self.UPPER_DATA_BOUND.get())
        self.slider_mid.config(from_=self.UPPER_DATA_BOUND.get())
        self.slider_max.set(self.UPPER_DATA_BOUND.get())

        heatmap = self.aplot.pcolorfast(self.data, cmap=self.cmapa)
        mpl.colorbar.ColorbarBase(self.cmap_ax, cmap=self.cmapa,
                                  norm=self.norm,
                                  orientation='vertical')
        self.cmap_canvas.draw()
        self.canvas.draw()



        ### MARK ON SIMILAR

        if not any([s.chains_to_keep for s in self.STRUCTURES]):
            self.menubar.delete(3,3)
        else:
            Tk.Label(self.dist_frame, text="Interchain distance").grid(column=0, row=1)
            self.mark_on_similar_just_within_spin.grid(column=1,row=1)

        #### END OF UPPER CONTROLS
        ### LEFT CONTROLS
        if dm.Structure.isRNA:
            self.comp_atom_mode.set(dm.Structure.available_modes_rna[0])
            self.menu_atom_mode_rna.grid(column=0, row=1)
        else:
            self.comp_atom_mode.set(dm.Structure.available_modes[0])
            self.menu_atom_mode_prot.grid(column=0, row=1, rowspan=2)


            #self.recolor_by_any_trueness.trace("w",self.recolor_by_any_trueness_do)
            #Tk.Button(self.left_controls, text="Recolor by nativeness", command=self.recolor_by_trueness)  # ,command=lambda: makeSSplot)



        self.restrict_to_structure_var.trace("w", self.makeSSplot)
        self.trueness_show_intra.trace("w", self.makeSSplot)
        self.trueness_show_inter.trace("w", self.makeSSplot)
        self.trueness_show_false.trace("w", self.makeSSplot)
        #self.all_combos_var.trace("w", self.makeSSplot)



        self.cid = self.canvas.mpl_connect('button_press_event', self.onclick_plot)
        self.cid2 = self.canvas.mpl_connect('button_release_event', self.onclick2_plot)
        self.cid3 = self.canvas.mpl_connect('motion_notify_event', self.track_cursor)
        if len(self.OPCJE)>1:
            self.map_structure_mode.set(self.OPCJE[1])

        self.root.deiconify()
        sw = self.mode_frame.winfo_width()
        sh = self.mode_frame.winfo_height()
        #print "Setting w",sw,"h",sh
        hei = self.root.winfo_height()
        wid = self.root.winfo_width()
        #print hei,wid

        self.root.minsize(775,700)
        self.root.aspect(620, 530, 620, 530)

#        self.root.bind('<Configure>', self.resize)

        self.root.mainloop()
    def resize(self, event):
        #print "Resizing",event.width, event.height
        hei = self.root.winfo_height()
        wid = self.root.winfo_width()
        #print hei,wid
#        sw = self.mode_frame.winfo_width()
#        sh = self.mode_frame.winfo_height()
#        h = min(wid - sw, hei - sh)#*1./self.default_plot_dpi
#        w=h
#        print "Setting w",w,"h",h
#        self.plot_field.config(width=w, height=h)
#        self.canvas.draw()
        #self.FIGURE.set_figwidth(w,forward=True)
        #self.FIGURE.set_figheight(h,forward=True)
        #self.root.wm_deiconify()
