# FUSE-Battery-Data-Plotter
###  Written by Navraj Eari and supervised by Joshua Cruddos
### FUSE 2023 Internship Project

- This application allows you to quickly visualize, compare, and save battery data exported from EC/BT Lab software in a publishable format.

## How to export data from EC/BT Lab software:
- From the toolbar, Analysis > Batteries > Process Data
- Load the file(s) you wish to export, ensuring they are a .mpr format
- Under 'Variables' check 'All' to be added
- Click process!
- This will export the file into a .mpp format in the same directory as the .mpr file
- From the toolbar, Experiment > Export as Text...
- Load the .mpr file(s) created in the previous steps
- Ensure the template is set to 'Custom*'
- Click the right facing double arrow to move all the variabels over to be exported
- Click export!
- Now we have a .txt file(s) of our data, which can be opened by this application for viewing

## How to use Battery Data Plotter Application:
- From the toolbar, File < Open folder
- Locate the folder where the .txt file(s) are saved
- A list of each .txt file will be shown the box, and data displayed as a graph
- To change the graph axis, from the toolbar click Edit, and select the desired graph type
- Click on another file to view its data
- To compare 2 or more files, have a file seleted, then hold the CTRL key, and select another file
- Both files data will be displayed on the same plot
  - Note: the legend will be taken from the file name if it contains 3 consecutive numbers
- Everytime you click on a new file, the previous files plots will be destroyed
  - To keep the plots you click on, from the toolbar click Edit, and check the 'Keep Plots' option
- To save the plot, from the toolbar click File < Save as, and select the destination
- To save the plot for all files within the folder, click 'Save all as' instead

## Bug list:
- Opening files may take upwards of 15 seconds depending on its size and data plotted
- Selecting multiple files may glicth sometimes

- ## Libraies Used:
- Tkinter
- Pandas
- RegEx
- MatPlotLib
