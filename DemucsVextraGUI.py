import PySimpleGUI as sg
import glob
import os
from static.guielements import *
from static.const import *
import threading
import dotenv

### helpers
def SetConfigKey(key, value):
	value = str(value)
	envfile = "data/.env"
	dotenv.set_key(envfile, key_to_set=key, value_to_set=value)


def filelog(logmsg):
    log.append(logmsg)
    window.Element('-LOG-').update(log)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def getfilenames(paths):
    fnames = []
    for path in paths:
        fnames.append(os.path.basename(path))
    return fnames

def updatefilelist(showpaths, paths):
    if showpaths:
        window.Element('-LIST-').update(values=paths)
    else:
        window.Element('-LIST-').update(values=getfilenames(paths))

def getfiles(directory, recursive):
    files = []
    for file in glob.iglob(directory + '**/**', recursive=recursive):
        if file.endswith(tuple(audioformats)):
            files.append(file)
    if len(files) == 0:
        filelog("No valid wavs found!")
    return files

def appendfilenames(files):
	filelist = []
	for f in files:
		filename = f' "{f}"'
		filelist.append(filename)
	strlist = "".join(filelist)
	return str(strlist)

def runCmd():
	currentfiles = getfiles(folder, values['-REC-'])
	try:
		voconly = " --two-stems=vocals" if values['-VOC-'] == True else ""
		model = "-n " + values["-MODEL-"]
		hw = " -d cpu" if values["-HARDWARE-"] == "cpu" else ""
		output = f" -o {values['-OUTPUT-']}" if outputset == True else f" -o {folder}"
		f = appendfilenames(currentfiles)
		filelog(f"Processing started..")
		cmd = f"demucs{f}{voconly}{hw}{output} {model}".replace("\\", "/")
		os.system(cmd)
		window['Process'].update(disabled=False)

	except NameError as error:
		filelog(error)

#### Layout

layout = [[
	filelist,
	selector,
	[sg.HorizontalSeparator(pad=(0,10))],
	modulecol1,
	[sg.HorizontalSeparator(pad=(0,10))],
	bottomcol
	]]


window = sg.Window('Demucs Wrapper', layout,resizable=True, finalize=True, background_color=windowcolor, size=(960,800), icon=resource_path("data/dtico.ico"), font=("Calibri", 11))

### GUI Logic

CONFIG = dotenv.dotenv_values("data/.env")

#load config
rec = False
paths = False
currentfiles = ''

if CONFIG['FOLDER'] != "":
		folder = CONFIG['FOLDER']
		currentfiles = getfiles(folder, rec)
		updatefilelist(paths, currentfiles)
		window.Element('-FOLDER-').update(value=folder)
		folderset = True

if CONFIG['OUTPUT'] != "":
		outputfolder = CONFIG['OUTPUT']
		window.Element('-OUTPUT-').update(value=folder)
		outputset = True







filelog("Ready to juice! By Dion Timmer")


## Event Loop

while True:
	event, values = window.read()
	if event in (sg.WIN_CLOSED, 'Exit'):
		break
	if event == '-FOLDER-':
		folder = values['-FOLDER-']
		currentfiles = getfiles(folder, rec)
		updatefilelist(values["-SHOWPATHS-"], currentfiles)
		folderset = True
		SetConfigKey('FOLDER', folder)
		filelog("Folder Set")
	if event == '-OUTPUT-':
		outputfolder = values['-FOLDER-']
		outputset = True
		SetConfigKey('OUTPUT', outputfolder)
		filelog("Output Set")
	if event == 'Refresh':
		if folderset == True:
			currentfiles = getfiles(folder, rec)
			updatefilelist(values["-SHOWPATHS-"], currentfiles)

	if event == '-REC-':
		rec = values['-REC-']
		SetConfigKey('REC', rec)
		if folderset == True:
			currentfiles = getfiles(folder, rec)
			updatefilelist(values["-SHOWPATHS-"], currentfiles)

	if event == '-SHOWPATHS-':
		if folderset == True:
			currentfiles = getfiles(folder, rec)
			updatefilelist(values["-SHOWPATHS-"], currentfiles)

	if event == 'Process':
		threading.Thread(target=runCmd).start()
		window['Process'].update(disabled=True)


window.close()