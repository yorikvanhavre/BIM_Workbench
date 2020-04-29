#!/usr/bin/python3

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2009 Yorik van Havre <yorik@uncreated.net>              *  
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Library General Public License (LGPL)   *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************


'''
This script updates the translations obtained from crowdin
'''

import sys 
import os
import shutil
import tempfile
import zipfile


modulename = "BIM" # the name of your module
translations = "translations" # the path to the translations files location, inside your module folder
languages = "af ar ca cs de el es-ES eu fi fil fr gl hr hu id it ja kab ko lt nl no pl pt-BR pt-PT ro ru sk sl sr sv-SE tr uk val-ES vi zh-CN zh-TW"



def doLanguage(tempfolder,translationsfolder,lncode):

    " treats a single language"

    if lncode == "en":
        # never treat "english" translation... For now :)
        return

    tsfilepath = os.path.join(tempfolder,lncode,modulename+".ts")
    newtspath = os.path.join(translationsfolder,modulename+"_"+lncode+".ts")
    newqmpath = os.path.join(translationsfolder,modulename+"_"+lncode+".qm")
    print(tsfilepath)
    print(newtspath)
    shutil.copyfile(tsfilepath, newtspath)
    os.system("lrelease " + newtspath)
    if not os.path.exists(newqmpath):
        print("ERROR: unable to create", newqmpath, ", aborting")
        sys.exit()


if __name__ == "__main__":
    
    zippath = os.path.join(os.path.abspath(os.path.dirname(__file__)),"freecad-addons.zip")
    translationsfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)),"..",translations)
    tempfolder = tempfile.mkdtemp()
    print ("creating temp folder " + tempfolder)
    os.chdir(tempfolder)
    if not os.path.exists(zippath):
        print ("ERROR: " + zippath + " not found")
        sys.exit()
    shutil.copy(zippath,tempfolder)
    zfile=zipfile.ZipFile(os.path.join(tempfolder,os.path.basename(zippath)))
    print ("extracting zip...")
    zfile.extractall()
    os.chdir(translationsfolder)
    for ln in languages.split(" "):
        path = os.path.join(tempfolder,ln)
        if not os.path.exists(path):
            print ("ERROR: language path",path,"not found!")
        else:
            doLanguage(tempfolder,translationsfolder,ln)
