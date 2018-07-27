# pyRevit_Adds


FIX for Print Linked Sheets (pyRevit extension)
===================================

The current version of the "Print Linked Sheets" tool for pyRevit does not function when Windows Desktop is set to a network location.
This FIX for that tool replaces the user's Desktop location as default with C:\Temp.

Prerequisite: pyRevit must be installed from https://github.com/eirannejad/pyRevit
Created by: Ehsan Iran-Nejad
Updated by: Brett Beckemeyer (bbeckemeyer@cannondesign.com)


Files
-----
* readme.md (this file)
* script.py (python script text file)
* scrip-orig.txt (original python script text file)


Installation
------------
Note: Revit does not need to be exited or restarted for installation. If Revit is open, simply use pyRevit's Reload function to access the tool.
1.	Manually:
	a.	Open the /data folder and copy the contents to clipboard (should be just one subfolder).
	b.	Find the pyRevit installation and the pushbutton subfolder named:
		 "pyRevit\extensions\pyRevitTools.extension\pyRevit.tab\Drawing Set.panel\Print.pulldown". 
	c.	Paste the copied items into this folder.

Usage
-----
1.	

Issues/Troubleshooting
----------------------
*	


Created: 09/04/2018
Last updated: 