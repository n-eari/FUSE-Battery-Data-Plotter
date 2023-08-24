import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from tkinter import scrolledtext

# Battery Data Plotter
# Written by Navraj Eari
# 22/08/23
# FUSE 2023 Internship Project
# This application allows you to quickly visualize, compare, and save battery data exported from EC/BT Lab software in a publishable format
# See "About" section for instructions on how to use

class App:

    def __init__(self, master):
        self.master = master # intialises main frame into a master varible, to which we can add elements to.

        self.fileList = [] # contains all files loaded
        self.onShowList = [] # contains all files shown on plot
        self.plotType = tk.StringVar(value = "Vol_Cur_vs_Time") # default plotype shown when file loaded
        self.keepShow = tk.BooleanVar()
        self.keepShow.set(False) # variable which allows plots not to be destroyed; set to off by default
        self.multi = False # allows script to know if multiple files are shown in one plot
        # all these varibles are declared once script runs

        self.f = tk.Frame(self.master, width = 300, height = 300, bg = "pink")
        self.f.grid(row = 0, column = 0, padx = 50, pady=50, sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        # pink frame created onto of the blue main frame, where list box will be placed 

        menubar = tk.Menu(self.master, background='white', foreground='black', activebackground='white', activeforeground='black')
        # menu bar declared, which will contain options "File", "Edit", and "About" 

        file = tk.Menu(menubar, tearoff=0, background='white', foreground='black')  
        file.add_command(label="Open Folder", command = lambda:self.loadFolder()) 
        file.add_separator()  
        file.add_command(label="Save as", command = lambda:self.saveAs(all = False))    
        file.add_command(label="Save all as", command = lambda:self.saveAs(all = True)) 
        menubar.add_cascade(label="File", menu=file)
        # file option in menu bar declared, whith actions such as Open Folder, Save as, and Save all as intialised and commands assigned

        edit = tk.Menu(menubar, tearoff=0, background='white', foreground='black')  
        edit.add_checkbutton(label="Keep Plots", variable=self.keepShow, onvalue=1, offvalue=0)
        edit.add_separator()
        # edit option in menu bar declared, with actions such as Keep plots, and ability to switch to different plot types
        # action for "Keep Plots", which prevents plots being destroyed upon selection of new file   

        edit.add_radiobutton(label="Ewe/I vs. Time", variable=self.plotType, value = "Vol_Cur_vs_Time", command = lambda: self.Plotter(clear = True))
        edit.add_radiobutton(label="Ewe vs. Capacity", variable=self.plotType, value = "Vol_vs_Cap", command = lambda: self.Plotter(clear = True))
        edit.add_radiobutton(label="I vs. Ewe", variable=self.plotType, value = "Cur_vs_Vol", command = lambda: self.Plotter(clear = True))
        edit.add_radiobutton(label="Ewe vs. Time", variable=self.plotType, value = "Vol_vs_Time", command = lambda: self.Plotter(clear = True))
        edit.add_radiobutton(label="Dis Capacity vs. Ewe", variable=self.plotType, value = "DisCap_vs_Cyc", command = lambda: self.Plotter(clear = True))                                 
        menubar.add_cascade(label="Edit", menu=edit)  
        # actions to change plot type, with commands assinged to them

        help = tk.Menu(menubar, tearoff=0, background='white', foreground='black')  
        help.add_command(label="About", command = self.openAboutWindow)  
        menubar.add_cascade(label="Help", menu=help) 
        # help option in menu bar declared, with the only action contained being the About action
        # this contains information about the program and how to export data for use 

        self.master.config(menu=menubar) # configures menu bar with all the new options 

        self.listbox = tk.Listbox(self.f, width=30, height = 10, selectmode="extended")
        self.listbox.grid(row=0, column=0, sticky=tk.NSEW)
        self.listbox.bind('<<ListboxSelect>>', self.onselect) # runs a command when a file is selected
        self.listbox.bind("<B1-Motion>", self.disableDrag) # prevents clicking multiple files by dragging accidentally
        # creates the list box, which is contained within the blue pink frame
        # adjusts its size and binds actions to it

        scrollbar_y = tk.Scrollbar(self.f, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox['yscrollcommand'] = scrollbar_y.set
        scrollbar_y.grid(row=0, column=1, sticky=tk.NS)
        scrollbar_x = tk.Scrollbar(self.f, orient=tk.HORIZONTAL, command=self.listbox.xview)
        self.listbox['xscrollcommand'] = scrollbar_x.set
        scrollbar_x.grid(row=1, column=0, sticky=tk.EW)
        self.f.rowconfigure(0, weight=1)
        self.f.columnconfigure(0, weight=1)
        # creates vertical and horizontal scroll bar, and adjusts size

    def saveAs(self, all): # function which saves the plot when action is selected
        dirSave = filedialog.askdirectory(parent=self.master,initialdir=self.dirname,title='Pick a directory')
        # allows user to choose a save dirc

        if all == True: # if you click the Save all as action, then all files in that folder will have their plots saved
            for self.index, _ in enumerate(self.fileList):
                self.value = self.fileList[self.index]
                self.loadDf()
                self.Plotter(show=False)
                plt.savefig(dirSave + "\\" + self.value.rstrip(".txt") + "_" + self.plotType.get(), bbox_inches='tight', dpi = 300)
                # for every file in the filelist, load its df, create plot, and save fig

        else: # if you click the Save as action, then only the plot selected will be saved
            plt.savefig(dirSave + "\\" + self.value.rstrip(".txt") + "_" + self.plotType.get(), bbox_inches='tight', dpi = 300)

    def loadFolder(self): # function which loads the folder when action is selected
        self.fileList.clear() # clears file list incase new folder is selected
        self.dirname = filedialog.askdirectory(parent=self.master,initialdir="/",title='Pick a directory') # allows user to choose dirc
        for f in os.listdir(self.dirname):
            if f.endswith(".txt"):
                self.fileList.append(f)
        # only show files in the listbox with the .txt extenstion
        var = tk.Variable(value=tuple(self.fileList))
        self.listbox.config(listvariable=var)
        self.listbox.select_set(0)
        self.listbox.focus_set()
        self.onselect(None)
        # block of code which changes the listbox to contain files and sets focus

    def loadDf(self): # function with loads selected files data into a dataframe
        neededCols = ['time/s', 'Ewe/V', 'I/mA', 'cycle number', 'Capacity/mA.h']
        neededCols2 = ['time/s', 'Ecell/V', 'I/mA', 'cycle number', 'Capacity/mA.h']
        neededColsCV = ['time/s', 'Ewe/V', '<I>/mA', 'cycle number']
        neededColsCV2 = ['time/s', 'Ecell/V', '<I>/mA', 'cycle number']
        allColsList = [neededCols, neededCols2]
        allColsListCV = [neededColsCV, neededColsCV2]
        # list which contains only the data we need to extract from the files
        # Cyclic voltammetry contains different data we need to extract
        # sometimes for unknown reasons, when exporting data from the EC/BT lab software, the name of the columns is slightly different
        # hence i have created 2 lists for each, and the code below will try each of them

        for i in allColsList:
            try:
                self.df = pd.read_csv(self.dirname + "/" + self.fileList[self.index], encoding= 'unicode_escape', usecols=i, sep="\t",
                                dtype={'time/s':"float64", 'Ewe/V':"float16", 'I/mA':"float16", '|Z|/Ohm':"float16",
                                        'cycle number':"int16", 'Re(Z)/Ohm':"float16", '-Im(Z)/Ohm':"float16", 'Capacity/mA.h':"float16"})
            except Exception:
                pass
        for j in allColsListCV:
            try:
               self.df = pd.read_csv(self.dirname + "/" + self.fileList[self.index], encoding= 'unicode_escape', usecols=j, sep="\t",
                        dtype={'time/s':"float64", 'Ecell/V':"float16", 'I/mA':"float16", '|Z|/Ohm':"float16",
                                'cycle number':"int16", 'Re(Z)/Ohm':"float16", '-Im(Z)/Ohm':"float16", 'Capacity/mA.h':"float16"})
            except Exception:
                pass
        # block which loads data in dataframe with only selected data, and for optimisation, changes variable type

        self.df['time/s'] = self.df['time/s'] / 3600
        self.df.rename(columns={'time/s': 'time/h'}, inplace=True)
        # converts time in seconds to hours

        if 'Ecell/V' in self.df.columns:
            self.df.rename(columns={'Ecell/V': "Ewe/V"}, inplace=True)
        if '<I>/mA' in self.df.columns:
            self.df.rename(columns={'<I>/mA': "I/mA"}, inplace=True)
        # renames the voltage and current columns

        if "_CV_" in self.fileList[self.index]:
            self.df = self.df[self.df['cycle number'] <= 2]
            specific_rows = self.df[self.df['cycle number'] == 2]
            rows_to_remove = len(specific_rows) // 2
            rows_to_remove2 = specific_rows.tail(rows_to_remove)
            self.df = self.df[~self.df.index.isin(rows_to_remove2.index)] 
        # script identifies a CV file if it has "_CV_" in name.
        # if so, only the first 2.5 cycles are used

    def onselect(self, evt): # function which is binded to the listbox, and allows plots to be created when a file(s) from listbox is selected

        if self.master.focus_get() == self.listbox: # if listbox is the focus window

            self.selected_items = [self.listbox.get(index) for index in self.listbox.curselection()]
            # loads selected file(s) into vairable list

            colorList = ["blue", "orange", "green", "red", "purple", "navy", "pink", "teal", "palegreen", "lime"]
            # intialises list of colours, which are used whhen multiple files are selected

            if len(self.selected_items) <= 1: 
                self.onShowList.clear()
            # if you are only going to display 1 file, clear previous plot.
            # this will not run if i select 2 or more files, therefore plot will remain, and the data of the 2nd file will be on the same plot

            for item in self.selected_items: # for each file selected
                if item in self.onShowList:
                    continue # if file is already show on plot, skip to next file
                else: # if file is selected and not already in plot...
                    self.onShowList.append(item) # append file to onshowlist, which contains files which are on the plot
                    self.value = item
                    self.index = self.fileList.index(self.value)
                    self.color = colorList[self.onShowList.index(item)]
                    self.loadDf()
                    # assigns its index, value, and colour to a variable
                    # loads its dataframe

                    if len(self.selected_items) <= 1:
                        self.multi = False
                    else:
                        self.multi = True
                    self.Plotter()
                    # runs function which plots the data
                    # self.multi is a varible which is true only if more than 1 file is selected
                    # allows script to know if multiple files data are shown in 1 plot for scipt logic

    def disableDrag(self, evt): # function which is assigned to listbox; prevents click and dragging if files
        return "break"
    
    def openAboutWindow(self): # function which runs when About action in menubar is selected
        about_window = tk.Toplevel(self.master)
        about_window.title("About")
        # opens a new window

        text = ["Battery Data Plotter\n",
                "Written by Navraj Eari\n",
                "FUSE 2023 Internship Project\n\n",
                "This application allows you to quickly visualize, compare, and save battery data\n",
                "exported from EC/BT Lab software in a publishable format\n\n",
                "How to export data from EC/BT Lab software:\n",
                "      • From the toolbar, Analysis > Batteries > Process Data\n",
                "      • Load the file(s) you wish to export, ensuring they are a .mpr format\n",
                "      • Under 'Variables' check 'All' to be added\n",
                "      • Click process!\n",
                "      • This will export the file into a .mpp format in the same directory as the .mpr file\n",
                "      • From the toolbar, Experiment > Export as Text...\n",
                "      • Load the .mpr file(s) created in the previous steps\n",
                "      • Ensure the template is set to 'Custom*'\n",
                "      • Click the right facing double arrow to move all the variabels over to be exported\n",
                "      • Click export!\n",
                "      • Now we have a .txt file(s) of our data, which can be opened by this application for viewing\n\n",
                "How to use Battery Data Plotter Application:\n",
                "      • From the toolbar, File < Open folder\n",
                "      • Locate the folder where the .txt file(s) are saved\n",
                "      • A list of each .txt file will be shown the box, and data displayed as a graph\n",
                "      • To change the graph axis, from the toolbar click Edit, and select the desired graph type\n",      
                "      • Click on another file to view its data\n",
                "      • To compare 2 or more files, have a file seleted, then hold the CTRL key, and select another file\n",
                "      • Both files data will be displayed on the same plot\n"
                "           • Note: the legend will be taken from the file name if it contains 3 consecutive numbers\n",
                "      • Everytime you click on a new file, the previous files plots will be destroyed\n",
                "           • To keep the plots you click on, from the toolbar click Edit, and check the 'Keep Plots' option\n",
                "      • To save the plot, from the toolbar click File < Save as, and select the destination\n",
                "      • To save the plot for all files within the folder, click 'Save all as' instead\n\n",
                "Bug list:\n",
                "      • Opening files may take upwards of 15 seconds depending on its size and data plotted\n",
                "      • Selecting multiple files may glicth sometimes"
                ]
        # text which will be shown
        # contains information of program, how to extract data to a .txt format from the EC/BT software and how to use program
        # also contains a bug list, which wont be updated

        about_label = scrolledtext.ScrolledText(about_window, width=60, height=20)
        for t in text:
            about_label.insert(tk.END, t)
        about_label.pack(padx=20, pady=20, expand=True, fill="both",)
        about_label.configure(state="disabled")
        # pastes text into a scrollable text window, adjusts size, and prevents editing
    
    def Plotter(self, show = True, clear = False): # function which plots data of selected file (all files in the onshowlist)
        # if show is true, the data will be displayed. will only be set to false when saving all the files in a foler (Save all as action)
        # if clear is true, then plot will be cleared before plotting new data. this is used when only displaying 1 files data
        # its also true when changing plot type

        if clear == True: # if clear is true, then plot is cleared, and only 1 files data is plotted, hence the multi variable is false
            self.multi = False
        
        if (self.multi == False) or (clear == True): # if only showing 1 files data, or changing to a new plotype then...
            if (show == False) or (self.keepShow.get() == False): # but if we are not displaying the data because we are saving all as, the close the figure
                plt.close()
            self.fig, self.ax1 = plt.subplots(figsize = (5, 4))
            self.ax2 = self.ax1.twinx()
            self.ax1.cla()
            self.ax2.cla()
            # creates a new, clean set of axis/fig
            # notice if self.multi is true, then the previous axis/fig will not be cleared, and the code below will run as normal
            # hence new data pasted onto of the old data/plot

        idCode = re.search(r'\d{3}', self.value)
        if idCode.group():
            label = idCode.group()
        else:
            label = "-"
        # block which identifies 3 consectiuve numbers in the files names, which will be used for the legend
        # if none is found, use "-"

        # code below identifes the selected plottype chosen from the action bar, and using the dataframes and figure plots the data
        # besides CV, all plots are scatter plots

        if self.plotType.get() == "Vol_Cur_vs_Time": # this plot has 2 y-axis'

            self.ax2.tick_params(axis='y', left= False, right=True, labelleft=False, labelright=True)

            l1, = self.ax1.plot(self.df["time/h"], self.df["Ewe/V"], color=self.color, alpha = 1)
            self.ax1.set_xlabel('Time / h')
            self.ax1.set_ylabel('Ewe / V', color=self.color)
            self.ax1.tick_params(axis='y', labelcolor=self.color)

            l2, = self.ax2.plot(self.df["time/h"], self.df["I/mA"], color='tab:gray', alpha = 0.50)
            self.ax2.set_ylabel("I / mA", color='tab:gray')
            self.ax2.tick_params(axis='y', labelcolor="tab:gray")

            plt.legend([l1, l2], ["Voltage", "Current"], loc = "upper right")
            
        elif self.plotType.get() == "Vol_vs_Cap":
                
            self.ax2.set_axis_off() # for all other plots, the 2nd y-axis isnt needed
            if (self.df['cycle number']).max() > 5:
                self.ax1.scatter(self.df["Capacity/mA.h"], self.df["Ewe/V"], c=self.df['cycle number'], cmap = "viridis", marker=".", s = 5, label = label)
            else:
                self.ax1.scatter(self.df["Capacity/mA.h"], self.df["Ewe/V"], color = self.color, s = 5, label = label)
            # if there are more than 5 cycles, the color will be a gradient, where the brighter the color the higher the cycle number
            # if there are less than 5 cycles, the colour will follow the colour list defined before

            self.ax1.set_xlabel('Capacity / mA.h')
            self.ax1.set_ylabel('Ewe / V')

        elif self.plotType.get() == "Cur_vs_Vol":
            self.ax2.set_axis_off()

            self.ax1.plot(self.df["Ewe/V"], self.df["I/mA"], color=self.color, label = label, lw = 1)
            self.ax1.set_xlabel('Ewe / V')
            self.ax1.set_ylabel("I / mA")

        elif self.plotType.get() == "Vol_vs_Time":
            self.ax2.set_axis_off()

            self.ax1.scatter(self.df["time/h"], self.df["Ewe/V"], color=self.color, marker=".", s = 5, label = label)
            self.ax1.set_xlabel("Time / h")
            self.ax1.set_ylabel('Ewe / V')      

        elif self.plotType.get() == "DisCap_vs_Cyc":
            self.ax2.set_axis_off()

            highCap = self.df.loc[self.df.groupby("cycle number")["Capacity/mA.h"].idxmax()]

            self.ax1.plot(highCap["cycle number"], highCap["Capacity/mA.h"], color=self.color, label = label)
            self.ax1.set_xlabel("Cycle Number")
            self.ax1.set_ylabel('Capacity / mA.h')

        self.ax1.yaxis.get_ticklocs(minor=True)
        self.ax1.minorticks_on()
        self.ax2.yaxis.get_ticklocs(minor=True)
        self.ax2.minorticks_on()
        # block which sets tick marks on axis
        
        if self.multi == True: # if multiple plots are shown, then the legend will show the 3 numbers in the file name
            self.ax1.legend(loc = "upper right")

        if show == True: # shows plot if true
            plt.show()
        
def main(): # main function which intilaises the root/main app window
    root = tk.Tk()
    root.config(bg="skyblue")
    root.title("Battery Data Plotter")
    App(root)
    root.mainloop()

if __name__ == '__main__':
    main()