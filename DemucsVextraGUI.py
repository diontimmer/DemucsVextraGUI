import PySimpleGUI as sg
import glob
import os
from static.guielements import *
from static.const import *
import threading
import dotenv
from subprocess import Popen, PIPE, STDOUT
import sys
from pathlib import Path
import re

# ****************************************************************************
# *                                  helpers                                 *
# ****************************************************************************

def startDemucsProcess(cmd, modeltype, tracknames):
    window['Process'].update(disabled=True)
    process = Popen(cmd, encoding='utf8', stderr=STDOUT, stdout=PIPE)
    while process.poll() is None:
        procoutput = process.stdout.readline()
        if procoutput:
            if "Separated" in procoutput or "Separating" in procoutput or "Selected" in procoutput:
                filelog(procoutput)
            if "%" in procoutput:
                m = re.search('(\d+)%', procoutput)
                if m:
                    perc = int(m.group(1))
                    window['-PROGBAR-'].update(current_count=perc, bar_color=(percentage_to_hex(perc), None))


    filelog("Process finished!")
    window['-PROGBAR-'].update(current_count=0)
    window['Process'].update(disabled=False)
    processFilenames(values['-OUTPUT-'], modeltype, tracknames)

def percentage_to_hex(percentage):
    rgb = (0, round(percentage * 2.5), 0)
    rgbval = '%02x%02x%02x' % rgb
    return f'#{rgbval}'

def SetConfigKey(key, value):
    value = str(value)
    envfile = "data/.env"
    dotenv.set_key(envfile, key_to_set=key, value_to_set=value)


def filelog(logmsg):
    log.append(logmsg)
    window.Element('-LOG-').update(log, scroll_to_index=len(log))

def filelogreplace(logmsg):
    window.Element('-LOG-').update([logmsg], scroll_to_index=0)

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
    for f in glob.iglob(directory + '**/**', recursive=recursive):
        if f.endswith(tuple(audioformats)):
            files.append(f)
    if len(files) == 0:
        filelog("No valid wavs found!")
    return files

def appendfilepaths(files):
    filelist = []
    for f in files:
        filename = f' "{f}"'
        filelist.append(filename)
    strlist = "".join(filelist)
    return str(strlist)

def processFilenames(folder, modeltype, tracknames):
    for f in os.listdir(folder):
        if f == modeltype:
            modelfolder = f
            for trackfolder in os.listdir(folder + "/" + modelfolder):
                if trackfolder in tracknames:
                    for audiofile in (os.listdir(folder + "/" + modelfolder + "/" + trackfolder)):
                        if trackfolder not in audiofile:
                            oldname = (folder + "/" + modelfolder + "/" + trackfolder + "/" + audiofile)
                            newname = (folder + "/" + modelfolder + "/" + trackfolder + "/" + trackfolder + "_" + audiofile)
                            if os.path.exists(newname):
                                os.remove(newname)
                            os.rename(oldname, newname)

def removeBadCharsInPaths(paths):
    ls = []
    for p in paths:
        ls.append(p.replace("\\", "/"))
    return ls

def getcleanfilenames(files):
    filelist = []
    for f in files:
        filename = Path(f).stem
        filelist.append(filename)
    return filelist


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
        voconly = ["--two-stems=vocals"] if values['-VOC-'] == True else []
        model = ["-n", values["-MODEL-"]]
        hw = ["-d", "cpu"] if values["-HARDWARE-"] == "cpu" else ["-d","cuda"]
        output = ["-o", values['-OUTPUT-']] if outputset == True else ["-o", folder]
        jobs = ["-j",values['-JOBS-']]
        frmt = ["--mp3"] if values['-FORMAT-'] == "mp3" else []
        cmd = ['demucs'] + currfolderfiles + voconly + hw + jobs + frmt + output + model
        startDemucsProcess(cmd, values["-MODEL-"], getcleanfilenames(currfolderfiles))
    except NameError as error:
        filelog(error)

def runFileCmd():
    try:
        voconly = ["--two-stems=vocals"] if values['-VOC-'] == True else []
        model = ["-n", values["-MODEL-"]]
        hw = ["-d", "cpu"] if values["-HARDWARE-"] == "cpu" else ["-d","cuda"]
        output = ["-o", values['-OUTPUT-']] if outputset == True else ["-o", os.path.dirname(file)]
        jobs = ["-j",values['-JOBS-']]
        frmt = ["--mp3"] if values['-FORMAT-'] == "mp3" else []
        f = [file]
        cmd = ['demucs'] + f + voconly + hw + jobs + frmt + output + model
        startDemucsProcess(cmd, values["-MODEL-"], Path(file).stem)
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


window = sg.Window('Demucs Wrapper', layout, resizable=True, finalize=True, background_color=windowcolor, size=(960,800), icon=resource_path("data/dtico.ico"), font=("Calibri", 11))

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