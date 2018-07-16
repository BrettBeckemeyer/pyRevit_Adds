"""Set selected revisions on selected sheets."""
"""Updated version by Brett Beckemeyer on 07/09/2018 which allows preselecting sheets in Project Browser."""

from pyrevit import revit, DB
from pyrevit import forms


__doc__ = 'Select a revision from the list of revisions and '\
          'this script set that revision on all sheets in the '\
          'model as an additional revision.'


revisions = forms.select_revisions(button_name='Select Revision',
                                   multiselect=False)

if revisions:
	sheets = revit.get_selection()
	if not sheets:
		sheets = forms.select_sheets(button_name='Set Revision')
	if sheets:
		with revit.Transaction('Set Revision on Sheets'):
			updated_sheets = revit.update.update_sheet_revisions(revisions,
																sheets)
		if updated_sheets:
			print('SELECTED REVISION ADDED TO THESE SHEETS:')
			print('-' * 100)
			for s in updated_sheets:
				snum = s.Parameter[DB.BuiltInParameter.SHEET_NUMBER]\
						.AsString().rjust(10)
				sname = s.Parameter[DB.BuiltInParameter.SHEET_NAME]\
						.AsString().ljust(50)
				print('NUMBER: {0}   NAME:{1}'.format(snum, sname))
