# pyRevit_Adds


FIX for Set Revision On Sheets (pyRevit extension)
===================================

A fix for the "Set Revision On Sheets" pyRevit script that adds functionality to use selected sheets (if selected) or from list (if none selected).

Prerequisite: pyRevit must be installed from https://github.com/eirannejad/pyRevit
Created by: Ehsan Iran-Nejad
Updated by: Brett Beckemeyer (bbeckemeyer@cannondesign.com)


Files
-----
* readme.md (this file)
* script.py (python script text file)
* icon.png (icon graphic)


Installation
------------
Note: Revit does not need to be exited or restarted for installation. If Revit is open, simply use pyRevit's Reload function to access the tool.
1.	Manually:
	a.	Open the /data folder and copy the contents to clipboard (should be just one subfolder).
	b.	Find the pyRevit installation and the pushbutton subfolder named:
		 "\pyRevit\extensions\pyRevitTools.extension\pyRevit.tab\Drawing Set.panel\Revision.pulldown". 
	c.	Paste the copied items into this folder.

Usage
-----
1.	Alternative Usage:
	a.	Select the sheets in the Project Browswer you wish to set the Revision on.
	b.	Run the tool from the pyRevit tab.
	c.	Select the Revision to apply and hit the "Set Revision" button.

Issues/Troubleshooting
----------------------
*	


Created: 09/07/2018
Last updated: 