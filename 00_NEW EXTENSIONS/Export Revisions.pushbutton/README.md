# pyRevit_Adds


Export Revisions (pyRevit extension)
===================================

A pushbutton extension for the pyRevit addin ecosystem that exports Revit Revision Cloud data to a CSV format file.
Tool is set up by default and optimized for use with the Change Tracking Excel workflow developed by Brett Beckemeyer for CannonDesign. However, settings can be modified by using Shift-click on the tool's ribbon icon. 

Prerequisite: pyRevit must be installed from https://github.com/eirannejad/pyRevit
Created by: Brett Beckemeyer (bbeckemeyer@cannondesign.com)
Credits / Contributors: Ehsan Iran-Nejad (pyRevit)
Based On: Ehsan Iran-Nejad's pyRevit Extension "Generate Revision Report"
Utilizes Code From: Ehsan Iran-Nejad's pyRevit Extension "Reload Links"

Files
-----
* readme.md (this file)
* icon.png (icon graphic)
* script.py (python script text file)
* config.py (python script configuration file)
* RevcloudWindow.xaml (xaml dialog box file for use with config.py)

Installation
------------
Note: Revit does not need to be exited or restarted for installation. If Revit is open, simply use pyRevit's Reload function to access the tool.
1.	Manually:
	a.	Copy all files to clipboard.
	b.	Find the pyRevit installation and the pushbutton subfolder at this location:
			pyRevit\extensions\pyRevitTools.extension\pyRevit.tab\Drawing Set.panel\Revision.pulldown
	c.	Paste the copied items into this folder.

Usage
-----
0.	Settings for the tool may be changed by clicking on the tool icon while holding "Shift".
1.	With the project model open (all linked models are also included in data extraction), browse to the pyRevit ribbon tab and under
	the "Revisions" pull-down, select "Revision Export".
2.	(Optional) User will be prompted (via Y/N options) to reload all linked models.
3.	An information box will pop up and display the status of the export. 
4.	Once completed, the exported data can be found in the x_rev_clouds, x_sheets, man_rev_clouds_*, or man_sheets_* CSV files. 
	By default these are located in a subdirectory (Export_dynamo) of the project central model's folder.

Options
-------
General Settings
1.	Process clouds in linked models?
		This option selects whether ALL linked *.rvt models are processed for Revision Clouds or NO linked models are processed.
2.	Subfolder for output
		The plain-text name (no slashes) of the subfolder for the output file. Without a location, this defaults to the central
		model folder.
Sheet Export Settings
3.	Sheets where parameter value contains the specified text
		Selects whether the text used to filter (next two options) is used to INCLUDE matching sheets or EXCLUDE matching sheets
		from the exported Revision Clouds.
4.	Name of sheet parameter to filter by
		Plain text field (case-sensitive) to enter the name of the sheet parameter in Revit that user wishes to use for Volume data
		and filtering (if any).
5.	Text in sheet parameter to filter by
		The string of text (case-sensitive) in the parameter field above to filter sheets by. 

Issues/Troubleshooting
----------------------
*	

Created: 16/07/2018
Last updated: 