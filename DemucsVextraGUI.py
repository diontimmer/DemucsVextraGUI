import PySimpleGUI as sg
import glob
import os
from static.guielements import *
from static.const import *
import threading
import dotenv
from subprocess import Popen, PIPE, STDOUT
from shlex import split
import sys


# ****************************************************************************
# *                                  helpers                                 *
# ****************************************************************************

def startDemucsProcess(cmd, output):
    filelog(f"Process started with command {cmd}")
    window['Process'].update(disabled=True)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding='utf8')
    while True:
        procoutput = process.stdout.readline()
        erroutput = process.stderr.readline()
        if procoutput == '' and process.poll() is not None :
            break
        if procoutput :
            filelog(procoutput.strip())
        if erroutput :
            filelog(erroutput.strip())
    filelog("Process finished!")
    processFilenames(output.replace(" -o ", ""))
    window['Process'].update(disabled=False)


def SetConfigKey(key, value):
    value = str(value)
    envfile = "data/.env"
    dotenv.set_key(envfile, key_to_set=key, value_to_set=value)


def filelog(logmsg):
    log.append(logmsg)
    window.Element('-LOG-').update(log, scroll_to_index=len(log))

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
    shownpaths = removeBadCharsInPaths(paths)
    if showpaths:
        window.Element('-LIST-').update(values=shownpaths)
    else:
        window.Element('-LIST-').update(values=getfilenames(shownpaths))

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

def processFilenames(folder):
    try:
        for f in os.listdir(folder):
            if f in modeltypes:
                for d in os.listdir(folder + "/" + f):
                    for file in (os.listdir(folder + "/" + f + "/" + d)):
                        if d not in file:
                            oldname = (folder + "/" + f + "/" + d + "/" + file)
                            newname = (folder + "/" + f + "/" + d + "/" + d + "_" + file)
                            os.rename(oldname, newname)
    except OSError as e:
        filelog("Error renaming pulled files: " + e)

def removeBadCharsInPaths(paths):
    ls = []
    for p in paths:
        ls.append(p.replace("\\", "/"))
    return ls


def setListEnabled(enabled):
    if enabled == True:
        window.Element('-LIST-').update(disabled=False)
        window.Element('-FILE-').update(text_color='grey')
        window.Element('-FILETXT-').update(text_color='grey')
        window.Element('-CURFILETXT-').update(background_color=bgcolor, text_color='grey')
        window.Element('-CURFILE-').update(text_color='grey')
        window.Element('-FILEBROWSE-').update(disabled=True, button_color=bgcolor)
        window.Element('-FOLDERBROWSE-').update(disabled=False, button_color=scolor)
        window.Element('-FOLDER-').update(text_color='black')
        window.Element('-FOLDERTXT-').update(text_color='white')
        window.Element('-REC-').update(disabled=False, background_color=scolor)
        window.Element('-SHOWPATHS-').update(disabled=False, background_color=scolor)
        window.Element('-REFRESH-').update(disabled=False, button_color=scolor)
    else:
        window.Element('-LIST-').update(disabled=True)
        window.Element('-FILE-').update(text_color='black')
        window.Element('-FILETXT-').update(text_color='white')
        window.Element('-CURFILETXT-').update(background_color=scolor2, text_color='white')
        window.Element('-CURFILE-').update(text_color='white')
        window.Element('-FILEBROWSE-').update(disabled=False, button_color=scolor)
        window.Element('-FOLDERBROWSE-').update(disabled=True, button_color=bgcolor)
        window.Element('-FOLDER-').update(text_color='grey')
        window.Element('-FOLDERTXT-').update(text_color='grey')
        window.Element('-REC-').update(disabled=True, background_color=bgcolor)
        window.Element('-SHOWPATHS-').update(disabled=True, background_color=bgcolor)
        window.Element('-REFRESH-').update(disabled=True, button_color=bgcolor)



def runFolderCmd():
    currfolderfiles = getfiles(folder, values['-REC-'])
    try:
        voconly = " --two-stems=vocals" if values['-VOC-'] == True else ""
        model = " -n " + values["-MODEL-"]
        hw = " -d cpu" if values["-HARDWARE-"] == "cpu" else " -d cuda"
        output = f" -o {values['-OUTPUT-']}" if outputset == True else f" -o {folder}"
        jobs = f" -j {values['-JOBS-']}"
        frmt = f" --mp3" if values['-FORMAT-'] == "mp3" else ""
        f = appendfilenames(currfolderfiles)
        cmd = f'demucs{f}{voconly}{hw}{jobs}{frmt}{output}{model}'.replace("\\", "/")
        startDemucsProcess(cmd, output)
    except NameError as error:
        filelog(error)

def runFileCmd():
    try:
        voconly = " --two-stems=vocals" if values['-VOC-'] == True else ""
        model = " -n " + values["-MODEL-"]
        hw = " -d cpu" if values["-HARDWARE-"] == "cpu" else " -d cuda"
        output = f" -o {values['-OUTPUT-']}" if outputset == True else f"-o {os.path.dirname(file)}"
        jobs = f" -j {values['-JOBS-']}"
        frmt = f" --mp3" if values['-FORMAT-'] == "mp3" else ""
        f = f' "{file}"'
        cmd = f'demucs{f}{voconly}{hw}{jobs}{frmt}{model}{output}'.replace("\\", "/")
        startDemucsProcess(cmd, output)
    except Exception as error:
        filelog(error)

# ****************************************************************************
# *                                  Layout                                  *
# ****************************************************************************


layout = [[
    filelist,
    [fileselector],
    [folderselector],
    [sg.HorizontalSeparator(pad=(0,10))],
    modulecol1,
    [sg.HorizontalSeparator(pad=(0,10))],
    bottomcol
    ]]


window = sg.Window('Demucs Wrapper', layout,resizable=True, finalize=True, background_color=windowcolor, size=(960,800), icon=resource_path("data/dtico.ico"), font=("Calibri", 11))


# ****************************************************************************
# *                                  CONFIG                                  *
# ****************************************************************************

CONFIG = dotenv.dotenv_values("data/.env")
### set values to default.
rec = False
paths = False
currfolderfiles = ''

if CONFIG['REC'] != "":
    rec = CONFIG['REC']
    window.Element('-REC-').update(value=rec)

if CONFIG['PATHS'] != "":
    paths = CONFIG['PATHS']
    window.Element('-SHOWPATHS-').update(value=paths)

if CONFIG['FOLDER'] != "":
    folder = CONFIG['FOLDER']
    currfolderfiles = getfiles(folder, rec)
    folderset = True
    updatefilelist(paths, currfolderfiles)
    window.Element('-FOLDER-').update(value=folder)

if CONFIG['OUTPUT'] != "":
    outputfolder = CONFIG['OUTPUT']
    window.Element('-OUTPUT-').update(value=outputfolder)
    outputset = True

if CONFIG['FILE'] != "":
    file = CONFIG['FILE']
    window.Element('-FILE-').update(value=file)
    window.Element('-CURFILE-').update(value=os.path.basename(file))
    fileset = True

if CONFIG['MODEL'] != "":
    window.Element('-MODEL-').update(value=CONFIG['MODEL'])

if CONFIG['ACA'] != "":
    window.Element('-VOC-').update(value=CONFIG['ACA'])

if CONFIG['HW'] != "":
    window.Element('-HARDWARE-').update(value=CONFIG['HW'])

if CONFIG['JOBS'] != "":
    window.Element('-JOBS-').update(value=CONFIG['JOBS'])

if CONFIG['FORMAT'] != "":
    window.Element('-FORMAT-').update(value=CONFIG['FORMAT'])

if CONFIG['PROCTYPE'] != "":
    if CONFIG['PROCTYPE'] == 'File':
        window.Element('-FILEOPT-').update(value=True)
        setListEnabled(False)
    else:
        window.Element('-FOLDEROPT-').update(value=True)
        setListEnabled(True)
else:
    setListEnabled(False)







# ****************************************************************************
# *                             Event Loop x Init                            *
# ****************************************************************************


filelog("Ready to juice! GUI by Dion Timmer")

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == '-FOLDER-':
        folder = values['-FOLDER-']
        currfolderfiles = getfiles(folder, rec)
        updatefilelist(values["-SHOWPATHS-"], currfolderfiles)
        folderset = True
        SetConfigKey('FOLDER', folder)
        filelog("Folder Set")

    if event == '-FILE-':
        file = values['-FILE-']
        fileset = True
        filelog("File Set")
        window.Element('-CURFILE-').update(value=os.path.basename(file))
        SetConfigKey('FILE', file)
        if values['-FILEOPT-']:
            window.Element('-LIST-').update(disabled=True)

    if event == '-OUTPUT-':
        outputfolder = values['-OUTPUT-']
        outputset = True
        filelog("Output Set")
        SetConfigKey('OUTPUT', outputfolder)


    if event == '-REFRESH-':
        if folderset == True:
            currfolderfiles = getfiles(folder, rec)
            updatefilelist(paths, currfolderfiles)

    if event == '-REC-':
        rec = values['-REC-']
        SetConfigKey('REC', rec)
        if folderset == True:
            currfolderfiles = getfiles(folder, rec)
            updatefilelist(paths, currfolderfiles)

    if event == 'Clear':
        outputfolder = values['-FOLDER-']
        outputset = False
        SetConfigKey('OUTPUT', '')
        window.Element('-OUTPUT-').update(value='')

    if event == '-SHOWPATHS-':
        if folderset == True:
            paths = values["-SHOWPATHS-"]
            currfolderfiles = getfiles(folder, rec)
            SetConfigKey('PATHS', paths)
            updatefilelist(paths, currfolderfiles)

    if event == 'Process':
        if values['-FILEOPT-'] == True:
            if fileset:
                threading.Thread(target=runFileCmd).start()
            else:
                filelog("Please browse to a file to process.")
        else:   
            if folderset:
                threading.Thread(target=runFolderCmd).start()
            else:
                filelog("Please browse to a folder to process.")

    if event == '-MODEL-':
        SetConfigKey('MODEL', values['-MODEL-'])

    if event == '-VOC-':
        SetConfigKey('ACA', values['-VOC-'])

    if event == '-HARDWARE-':
        SetConfigKey('HW', values['-HARDWARE-'])

    if event == '-JOBS-':
        SetConfigKey('JOBS', values['-JOBS-'])

    if event == '-FORMAT-':
        SetConfigKey('FORMAT', values['-FORMAT-'])

    if event == '-FILEOPT-':
        SetConfigKey('PROCTYPE', 'File')
        setListEnabled(False)

    if event == '-FOLDEROPT-':
        setListEnabled(True)
        SetConfigKey('PROCTYPE', 'Folder')
        if folderset:
            currfolderfiles = getfiles(folder, rec)
            updatefilelist(paths, currfolderfiles)



window.close()