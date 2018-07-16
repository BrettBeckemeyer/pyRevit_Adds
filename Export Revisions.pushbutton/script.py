# -*- coding: utf-8 -*-
"""Exports Revision Cloud information to external CSV file"""
__author__ = 'Brett Beckemeyer (bbeckemeyer@cannondesign.com)'

from pyrevit import coreutils
from pyrevit import revit, DB
from pyrevit.revit import query
from pyrevit import script
from pyrevit import forms
import os, shutil, csv, re
from timeit import default_timer as timer
from sys import exit


start = timer()
#logger = script.get_logger()
# ...

sht_placeholder = "ZZ"
rev_count = 0
sheets_count = 0

#-----------GET CONFIG DATA--------------------

my_config = script.get_config()
process_links = my_config.get_option('process_links', default_value=True)
sheetfilter_exclude = my_config.get_option('filter_exclude', default_value=False)
sheetfilter_include = my_config.get_option('filter_include', default_value=True)
sheetfilter_param = my_config.get_option('sheetfilter_param', default_value='Volume Number')
sheetfilter = my_config.get_option('sheetfilter', default_value='')

# check if sheetfilter is empty, then set to ZZ placeholder value
if not (sheetfilter and sheetfilter.strip()):
	sheetfilter = sht_placeholder
"""
if sheetfilter is None:
	sheetfilter = sht_placeholder
else:
	if sheetfilter = "":
		sheetfilter = sht_placeholder
"""
export_folder = my_config.get_option('exportfolder', default_value='Export_dynamo')
if sheetfilter_include:
	sheetfilter_type = 1
else:
	sheetfilter_type = 0

# Sets variables for export filenames
#export_folder = "Export_dynamo"
backup_extension = "bak"
filename_extension = "csv"
filename_revclouds = "x_revclouds"
filename_sheets = "x_sheets"
filename_manual = "man"

# Begin console window
console = script.get_output()
console.set_height(400)
console.lock_size()

report_title = 'Revision Export'
report_date = coreutils.current_date()
report_project = revit.get_project_info().name

# setup element styling
console.add_style(
    'table { border-collapse: collapse; width:100% }'
    'table, th, td { border-bottom: 1px solid #aaa; padding: 5px;}'
    'th { background-color: #545454; color: white; }'
    'tr:nth-child(odd) {background-color: #f2f2f2}'
    )
#-----RETURN DOCUMENT FOLDER AND FILENAME-------------
# Get full path of current document
try:
	docpath = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(revit.doc.GetWorksharingCentralModelPath())
except:
	docpath = revit.doc.PathName
	
# Split file path
(docfolder, docfile) = os.path.split(docpath)
#------------------------------------------------------

#------BEGIN DICTIONARY OF LINK NAME, DOC--------------
#---structure to be: Linkname:Linkdoc for each file
lnk_data = {}
lnk_data[docfile] = revit.doc
#---next step is to append each linked model to list
#------------------------------------------------------

#------DEFINE BLANK AND EMPTY--------------------------	
class BlankObj:
	def __repr__(self):
		return ""

blank = BlankObj()
empty = "$"
#------------------------------------------------------

#------RELOAD LINKS FUNCTION---------------------------
def reload_links(linktype=DB.ExternalFileReferenceType.RevitLink):
    try:
        extrefs = query.get_links(linktype)
        #for ref in extrefs:
            #logger.debug(ref)

        if extrefs:
            refcount = len(extrefs)
            if refcount > 1:
                selected_extrefs = \
                    forms.SelectFromCheckBoxes.show(
                        extrefs,
                        title='Select Links to Reload',
                        width=500,
                        button_name='Reload',
                        checked_only=True
                        )
                if not selected_extrefs:
                    script.exit()
            elif refcount == 1:
                selected_extrefs = extrefs

            for extref in selected_extrefs:
				extref.reload()
    except Exception as load_err:
        #logger.debug('Load error: %s' % load_err)
        forms.alert('Model is not saved yet or link no loaded.')
#--------------------------------------------------------

if process_links:
	#------GET REVIT LINKS AS INSTANCES----------------------
	lnks = DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance)

	#------DIALOG BOX TO RELOAD LINKS------------------------
	if lnks:
		res = forms.alert('Reload Revit links?',
						  yes=True, no=True)

	if res:
		reload_links()
	#--------------------------------------------------------

	#------GET LINK DOCS, CHECK IF LOADED--------------------
	lnkinst = []
	lnkdocs = []
	for index, i in enumerate(lnks,1):
		#linkType = ''
		#linkType = revit.doc.GetElement(i.GetTypeId())
		#workset = revit.doc.GetElement(linkType.WorksetId)
		ddoc = i.GetLinkDocument()
		if not ddoc:
			rel = forms.alert('A link is unloaded, load it and run again.', yes=True)
			if rel:
				exit(0)
		else:
			lnkinst.append(i)
			lnkdocs.append(ddoc)

#-------EXTRACT ELEMENTS FROM ACTIVE MODEL---------------
print "Collecting elements from active model..."

# Variables list
all_sheets = []
sheetsnotsorted = []
sheets_filename = []
revs_filename = []

# Extract sheets from DOCUMENT
docsheets = DB.FilteredElementCollector(revit.doc)\
                    .OfCategory(DB.BuiltInCategory.OST_Sheets)\
                    .WhereElementIsNotElementType()\
                    .ToElements()
for i in range(len(docsheets)):
	sheets_filename.append(docfile)

all_sheets.extend(docsheets)

sheets_count = sheets_count + len(docsheets)
print str(sheets_count) + " sheets extracted"
sheets_count = 0


# collect clouds from DOCUMENT
all_clouds = []
docclouds = DB.FilteredElementCollector(revit.doc)\
               .OfCategory(DB.BuiltInCategory.OST_RevisionClouds)\
               .WhereElementIsNotElementType()

all_clouds.extend(docclouds)

for i in range(len(all_clouds)):
	revs_filename.append(docfile)
 
# collect revisions from DOCUMENT
all_revisions = []

docrevs = DB.FilteredElementCollector(revit.doc)\
                  .OfCategory(DB.BuiltInCategory.OST_Revisions)\
                  .WhereElementIsNotElementType()
all_revisions.extend(docrevs)

print "...done."
console.insert_divider()
#--------------------------------------------------------

if process_links:
	#-------COLLECT ELEMENTS FROM LINKED MODELS--------------
	print "\nCollecting elements from linked models..."

	# ITERATE THROUGH LINKS AND GATHER ELEMENTS
	for index, doclnk in enumerate(lnkdocs,1):
		doclnkpath = ""
		lnkfolder = ""
		lnkfile = ""

		# Get full path of current document
		try:
			doclnkpath = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(doclnk.GetWorksharingCentralModelPath())
		except:
			doclnkpath = doclnk.PathName
		# Split file path
		(lnkfolder, lnkfile) = os.path.split(doclnkpath)
		
		# Add to the link data array
		lnk_data[lnkfile] = doclnk
			
		isheets = DB.FilteredElementCollector(doclnk).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
		for s in range(len(isheets)):
			sheets_filename.append(lnkfile)
		iclouds = DB.FilteredElementCollector(doclnk).OfCategory(DB.BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements()
		for r in range(len(iclouds)):
			revs_filename.append(lnkfile)
		irevisions = DB.FilteredElementCollector(doclnk).OfCategory(DB.BuiltInCategory.OST_Revisions).WhereElementIsNotElementType().ToElements()
	#	sheetsnotsorted.extend(isheets)
		all_sheets.extend(isheets)
		all_clouds.extend(iclouds)
		all_revisions.extend(irevisions)
		print lnkfile + " processed."
	print str(index) + " links processed."
	console.insert_divider()
	#-------------------------------------------------------

#SORT FOR SHEETS - REMOVED BECAUSE BREAKS FILENAME RETRIEVAL
# all_sheets = sorted(sheetsnotsorted, key=lambda x: x.SheetNumber)

class RevisedSheet:
    def __init__(self, rvt_sheet):
        self._rvt_sheet = rvt_sheet
        self._find_all_clouds()
        self._find_all_revisions()

    def _find_all_clouds(self):
        ownerview_ids = [self._rvt_sheet.Id]
        ownerview_ids.extend(self._rvt_sheet.GetAllViewports())
        self._clouds = []
        for rev_cloud in all_clouds:
            if rev_cloud.OwnerViewId in ownerview_ids:
                self._clouds.append(rev_cloud)

    def _find_all_revisions(self):
        self._revisions = set([cloud.RevisionId for cloud in self._clouds])
        #self._addl_rev_ids = []
        self._addl_rev_ids = self._rvt_sheet.GetAdditionalRevisionIds()
        #print str(len(self._addl_rev_ids))

    @property
    def sheet_number(self):
        return self._rvt_sheet.SheetNumber

    @property
    def sheet_name(self):
        return self._rvt_sheet.Name

    @property
    def cloud_count(self):
        return len(self._clouds)

    @property
    def rev_count(self):
        return len(self._revisions)

    def get_clouds(self):
        return self._clouds

    def get_comments(self):
        all_comments = set()
        for cloud in self._clouds:
            comment = cloud.LookupParameter('Comments').AsString()
            if not coreutils.is_blank(comment):
                all_comments.add(comment)
        return all_comments
		
    def get_marks(self):
        all_marks = set()
        for cloud in self._clouds:
            mark = cloud.LookupParameter('Mark').AsString()
            if not coreutils.is_blank(mark):
                all_marks.add(mark)
        return all_marks

    def get_param(el, par):
        val = el.LookupParameter(par).AsString()
        return val

    def get_addl_revs(self):
        return self._addl_rev_ids

 # REMOVED THIS DEFINITION BECAUSE BREAKS IF NUMBERING IS BY SHEET
 #   def get_revision_numbers(self):
 #       return self._rev_numbers
 
#-------CREATE EXPORT TABLE FOR SHEETS-----------
print "\nAssembling Sheets table for export..."
sheet_table = []
sheet_table.append(["Sheet Number","Sheet Name","Volume","Prefix","Sequence"])
revised_sheets = []
rev_sheets_file = []
numchars = 2
replacement = ""

for index, sheet in enumerate(all_sheets):
	if sheet.CanBePrinted:
		volx = ""
		
		try:
			# get the value of the parameter used for volume definition
			sheetfilter_value = sheet.LookupParameter(sheetfilter_param).AsString()
			# if this parameter is not empty, set volume number to this value
			if sheetfilter_value <> None:
				volx = sheetfilter_value
			# otherwise, if the parameter is empty, set sheetfilter_value to match placeholder and keep volx blank
			else:
				sheetfilter_value = sht_placeholder
		# if parameter itself does not exist, allow user to ignore filtering or exit
		except:
			no_filter_param = forms.alert('Sheet parameter asked to filter by does not exist. Do you wish to ignore filter?', yes=True, no=False)
			if no_filter_param:
				sheetfilter = sht_placeholder
			else:
				exit(0)
		
		# if sheetfilter value is set to placeholder (meaning blank), then set sheetfilter_value to placeholder as well (no filtering)
		if sheetfilter in sht_placeholder:
			sheetfilter_value = sht_placeholder
		
		if sheetfilter in sheetfilter_value:
			item = sheet.SheetNumber
			try:
				restN = re.sub('[^0-9]', replacement, item[:numchars]) + item[numchars:]
				prefix = re.sub('[^A-Z]', replacement, item[:numchars])
			except:
				prefix = ""
			
			sheet_table.append([sheet.SheetNumber,sheet.Name,volx,prefix,restN])
			revised_sheets.append(RevisedSheet(sheet))
			rev_sheets_file.append(sheets_filename[index])

#		revised_sheets.append(RevisedSheet(sheet))
# print sheet_table
print "...done."
#-------------------------------------------------

console.insert_divider()

#------ASSEMBLE TABLE OF REVISIONS FOR EXPORT-----
print "\nAssembling Revision Clouds table for export..."

table_revclouds = []
table_revclouds.append(["Sheet Number","Sheet Qty","Filename","Element ID","View Name","Reason Code","ID","View Number","Comment","Revision Description","Revision Date"])
blank = "00"
rev_cloud_sheets = []
qty = 0
addlrevs = []

#	Iterate through all sheets and get revision cloud elements
for index, rev_sheet in enumerate(revised_sheets):
	#shtelem = rev_sheet.get_sheet()
	shtnum = rev_sheet.sheet_number
	shtfile = rev_sheets_file[index]
	
	#for shtfile, d in lnk_data.items():
		#thisdoc = d
	thisdoc = lnk_data.get(shtfile, "")
	
	# Get manually placed Revisions and iterate through
	try:
		addlrevs = rev_sheet.get_addl_revs()
		for x in addlrevs:
			#print "additional revision found"
			r = thisdoc.GetElement(x)
			rev = x.ToString()
			revdes = r.Description
			revdate = r.RevisionDate
			reason = "00"
			rID = "00"
			viewno = ''
			comment = ''
			viewname = shtnum + " - " + rev_sheet.sheet_name
			table_revclouds.append([shtnum, qty, shtfile, rev, viewname, reason, rID, viewno, comment, revdes, revdate])
	except:
		print "no additional revision"
		
	try:
		thisclouds = rev_sheet.get_clouds()

		#	Iterate through all revision clouds and retrieve parameters
		for i in thisclouds:
			reason = ''
			rID = ''
			rev = i.Id.ToString()
			rev_cloud_sheets.append(i.Id)
			
			view = thisdoc.GetElement(i.OwnerViewId)
			try: 
				viewname = view.ViewName 
			except: 
				viewname = shtnum + " - " + rev_sheet.sheet_name
			
			try:
				mark = i.LookupParameter('Mark').AsString()
			except:
				mark = ""
			
			#	Mark extraction to reason & ID
			if mark:
				if '.' in mark or ':' in mark:
					temp = mark.replace(":", ".").split(".")
					reason = temp[0].rjust(2,'0')
					rID = reason + "." + (temp[1].rjust(2,'0'))
				else:
					reason = mark
					rID = reason + "." + blank
			#	End Mark extraction
			
			comments = i.LookupParameter('Comments').AsString()
			
			#	Comments extraction to viewno, comment		
			#	if comment exists (not empty)
			if comments:
			#	if comments has colon or vertical separator
				if '|' in comments[:9] or ':' in comments[:9]:
					temp1 = comments[:9].replace(":", "|")
					temp2 = comments[9:]
			#	if comments has period
				else:
					if '.' in comments[:9]:
						temp1 = comments[:9].replace(".", "|")
						temp2 = comments[9:]
			#	if comments is blank (empty)
					else:
						temp1 = blank + "|"
						temp2 = comments
				temp = (temp1 + temp2).split("|")
				viewno = temp[0]
				comment = temp[1].strip()
			else:
				viewno = blank
				comment = blank
			#	End Comments extraction
			
			revdes = i.LookupParameter('Revision Description').AsString()
			revdate = i.LookupParameter('Revision Date').AsString()
			
			#	Create table of revision cloud parameters for export
			table_revclouds.append([shtnum, qty, shtfile, rev, viewname, reason, rID, viewno, comment, revdes, revdate])
		
	except:
		a = "a"
#			print(shtnum, rev, mark, comments, revdes, revdate)
#--------------------------------------------------------------

print "...done."
console.insert_divider()

for index, rc in enumerate(all_clouds):
	rev = rc.Id
	shtnum = ''
	viewname = ''
	shtfile = revs_filename[index]
	
	#for shtfile, d in lnk_data.items():
		#thisdoc = d
	thisdoc = lnk_data.get(shtfile, "")
		
	thisclouds = rev_sheet.get_clouds()
	
	if rev not in rev_cloud_sheets:
		reason = ''
		rID = ''
		qty = 0
		view = thisdoc.GetElement(rc.OwnerViewId)
		if view:
			viewz = []
			viewname = view.ViewName
			viewz.extend(rc.GetSheetIds())
			qty = len(viewz)
			if qty == 1:
				sheetview = thisdoc.GetElement(viewz[0])
				shtnum = sheetview.SheetNumber
#			for index2, v in enumerate(viewz):
#				if index2 == 0:
#					#print v
#					sheetview = thisdoc.GetElement(v)
#					shtnum = sheetview.SheetNumber
#					#console.insert_divider()
#				else:
#					next
			viewz = []
		else:
			viewname = ''
			shtnum = ''

		mark = rc.LookupParameter('Mark').AsString()
		
		#	Mark extraction to reason & ID
		if mark:
			if '.' in mark or ':' in mark:
				temp = mark.replace(":", ".").split(".")
				reason = temp[0].rjust(2,'0')
				rID = reason + "." + (temp[1].rjust(2,'0'))
			else:
				reason = mark
				rID = reason + "." + blank
		#	End Mark extraction

		comments = rc.LookupParameter('Comments').AsString()

		#	Comments extraction to viewno, comment		
		#	if comment exists (not empty)
		if comments:
		#	if comments has colon or vertical separator
			if '|' in comments[:9] or ':' in comments[:9]:
				temp1 = comments[:9].replace(":", "|")
				temp2 = comments[9:]
		#	if comments has period
			else:
				if '.' in comments[:9]:
					temp1 = comments[:9].replace(".", "|")
					temp2 = comments[9:]
		#	if comments is blank (empty)
				else:
					temp1 = blank + "|"
					temp2 = comments
			temp = (temp1 + temp2).split("|")
			viewno = temp[0]
			comment = temp[1].strip()
		else:
			viewno = ''
			comment = ''
		#	End Comments extraction

		revdes = rc.LookupParameter('Revision Description').AsString()
		revdate = rc.LookupParameter('Revision Date').AsString()
		
		table_revclouds.append([shtnum, qty, shtfile, rev, viewname, reason, rID, viewno, comment, revdes, revdate])
		


#-------FILE WRITING---------------------------------
# Create export paths
if not process_links:
	filename_revclouds = filename_revclouds.replace('x',filename_manual) + "_" + docfile
	filename_sheets = filename_sheets.replace('x',filename_manual) + "_" + docfile
export_revclouds = os.path.join(docfolder, export_folder, (filename_revclouds + "." + filename_extension))
export_sheets = os.path.join(docfolder, export_folder, (filename_sheets + "." + filename_extension))

# Check if export folder exists and make it if not
directory = os.path.join(docfolder,export_folder)
if not os.path.exists(directory):
    os.makedirs(directory)

# Check if file exists and make copy
if os.path.isfile(export_revclouds):
	print "\nRevision Cloud export file found..."
	shutil.copy(export_revclouds, os.path.join(docfolder, export_folder, (filename_revclouds + "." + backup_extension)))
	print "...backed up file."
else:
	print "Revision Cloud export file not found, new file will be created."

# Write CSV output for Revision Clouds
#with open(export_revclouds, 'w', newline='') as f:
try:
	with open(export_revclouds, 'w') as f:
		print "\nWriting Revision Cloud export..."
		writer = csv.writer(f, lineterminator='\n')
		writer.writerows(table_revclouds)
		print "...done."
except:
	print "\nError accessing Revision Cloud export file, close the file if it is open in another program."
console.insert_divider()

# Check if file exists and make copy
if os.path.isfile(export_sheets):
	print "\nSheets export file found..."
	shutil.copy(export_sheets, os.path.join(docfolder, export_folder, (filename_sheets + "." + backup_extension)))
	print "...backed up file."
else:
	print "Sheets export file not found, new file will be created."

# Write CSV output for Sheets
#with open(export_revclouds, 'w', newline='') as f:
try:
	with open(export_sheets, 'w') as f:
		print "\nWriting Sheets export..."
		writer = csv.writer(f, lineterminator='\n')
		writer.writerows(sheet_table)
		print "...done."
except:
	print "\nError accessing Sheets export file, close the file if it is open in another program."
#------------------------------------------------
console.insert_divider()

print str(len(revised_sheets)) + " sheets exported"
print str(len(all_clouds)) + " revclouds exported"
print " "

end = (timer() - start)
m, s = divmod(end, 60)
h, m = divmod(m, 60)

print "Elapsed time: %d:%02d:%02d" % (h, m, s)

print "\nExport complete, this window may be closed."
