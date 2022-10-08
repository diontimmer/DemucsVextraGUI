import PySimpleGUI as sg
from static.const import *


scolor="teal"
scolor2="darkslategrey"
bgcolor="snow4"
windowcolor="grey18"

selector = [[
	sg.Text('Folder', background_color=bgcolor), 
	sg.In(size=(25,1), enable_events=True ,key='-FOLDER-', readonly=True), 
	sg.FolderBrowse(button_color=scolor),
	sg.Checkbox('Iterate down folder tree? (Recursive)', key="-REC-", enable_events=True, background_color=scolor),
	sg.Checkbox('Show paths?', key="-SHOWPATHS-", enable_events=True, background_color=scolor),
	sg.Button("Refresh", button_color=scolor)
	]]

filelist = [sg.Listbox([], size=(0,16), key= '-LIST-', background_color=bgcolor, text_color="white", expand_x=True, expand_y=True, sbar_background_color=scolor)]

loglist = [sg.Listbox([], no_scrollbar=True, size=(0,8), key= '-LOG-', background_color=scolor2, text_color="white", expand_x=True)]
log = []

modulecol1 = [sg.Column([
	[sg.Checkbox('Vocal + Instru only?', key="-VOC-", enable_events=True, background_color=scolor)],
	[sg.Text('Hardware Type', background_color=bgcolor), sg.Combo(["gpu", "cpu"], default_value="gpu", button_background_color=scolor, key='-HARDWARE-', readonly=True)],
	[sg.Text('Seperation Model', background_color=bgcolor), sg.Combo(modeltypes, default_value="mdx_extra_q", button_background_color=scolor, key='-MODEL-', readonly=True)],
	[sg.Text('Output', background_color=bgcolor), 
	sg.In(size=(25,1), enable_events=True ,key='-OUTPUT-', readonly=True), 
	sg.FolderBrowse(button_color=scolor),
	sg.Button("Clear", tooltip="Output folder will be in the selected folder.", button_color=scolor)],
	[sg.Text('Max Jobs', background_color=bgcolor), sg.Combo(jobamts, default_value=1, key='-JOBS-')]
	],
	vertical_alignment="top",
	background_color=bgcolor,
	expand_y=True)]

bottomcol = sg.Column([[sg.Button("Process", button_color=scolor, size=30, border_width=4)], loglist], element_justification="c", justification="c", expand_x=True, background_color=windowcolor)
folderset = False
outputset = False