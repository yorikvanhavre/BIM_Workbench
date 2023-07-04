#!/usr/bin/python3

# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2021 Yorik van Havre <yorik@uncreated.net>              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Library General Public License (LGPL)   *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

"""
This script allows you to manage the translations
of your workbench with crowdin.

USAGE:

updateTranslations [command]

Possible commands are:

* updatets: Updates the ts files found in your WB
* upload: Sends the ts file to crowdin
* build: Creates a ready-for-download zip file on crowdin
* download: Download the zip file created in previous step
* install: Unzips the above file and creates corresponding qm files

Prior to using this script, you must have been made an manager on crowdin
freecad-addons project (ask Yorik), and you must have added your secret key
in a simple text file named ~/.crowdin-freecadaddons
You must also adapt the config values below. There is nothing else to do if
your workbench includes only .py and .ui files. They will all be gathered
automatically under one single ts file by this script.

"""

from __future__ import print_function

import sys
import os
import xml.sax
import pycurl
import io
import tempfile
import shutil
import zipfile

### CONFIGURATION

# adapt the following values to your workbench

# the name of your workench, and also the .ts file. Ex: "BIM" means the ts file is BIM.ts
MODULENAME = "BIM"

# the account name on crowdin
USERNAME = "yorik"

# The base path of your module, relative to this file
BASEPATH = ".."

# the path to the translations files location, inside your module folder
TRANSLATIONSPATH = "translations"

# the list of languages to install
# LANGUAGES = None to use all found in the zip file
LANGUAGES = "af ar ca cs de el es-ES eu fi fil fr gl hr hu id it ja kab ko lt nl no pl pt-BR pt-PT ro ru sk sl sr sv-SE tr uk val-ES vi zh-CN zh-TW"

# pylupdate util to use (pylupdae5, pyside2-lupdate,...)
PYLUPDATE = "pyside2-lupdate"

### END CONFIGURATION


class ResponseHandler(xml.sax.ContentHandler):
    "handler for the command responses"

    def __init__(self):
        self.current = ""
        self.data = ""
        self.translated = 1
        self.total = 1

    def startElement(self, tag, attributes):
        self.current = tag
        if tag == "file":
            self.data += attributes["status"]
        elif tag == "error":
            self.data == "Error: "

    def endElement(self, tag):
        if self.current in ["language", "success", "error"]:
            self.data = ""
            self.translated = 1
            self.total = 1
        self.current = ""

    def characters(self, content):
        if self.current == "name":
            self.data += content
        elif self.current == "phrases":
            self.total = int(content)
        elif self.current == "translated":
            self.translated = int(content)
            pc = int((float(self.translated) / self.total) * 100)
            self.data += " : " + str(pc) + "%\n"
        elif self.current == "message":
            self.data += content


def doLanguage(tempfolder, translationsfolder, lncode):
    "copies and compiles a single ts file"

    if lncode == "en":
        # never treat "english" translation... For now :)
        return

    tsfilepath = os.path.join(tempfolder, lncode, MODULENAME + ".ts")
    newtspath = os.path.join(translationsfolder, MODULENAME + "_" + lncode + ".ts")
    newqmpath = os.path.join(translationsfolder, MODULENAME + "_" + lncode + ".qm")
    # print(tsfilepath)
    # print(newtspath)
    shutil.copyfile(tsfilepath, newtspath)
    os.system("lrelease " + newtspath)
    if not os.path.exists(newqmpath):
        print("ERROR: unable to create", newqmpath, ", aborting")
        sys.exit()


if __name__ == "__main__":
    "main thread"

    # only one argument allowed
    arg = sys.argv[1:]
    if len(arg) != 1:
        print(__doc__)
        sys.exit()
    arg = arg[0]

    # getting API key stored in ~/.crowdin-freecad
    configfile = os.path.expanduser("~") + os.sep + ".crowdin-freecadaddons"
    if arg != "install":
        if not os.path.exists(configfile):
            print("Config file not found!")
            sys.exit()
        f = open(configfile)
        url = "https://api.crowdin.com/api/project/freecad-addons/"
        key = "?login=" + USERNAME + "&account-key=" + f.read().strip()
        f.close()

    basepath = os.path.abspath(BASEPATH)
    transpath = os.path.join(basepath, TRANSLATIONSPATH)

    if arg == "updatets":
        os.chdir(basepath)
        # os.system("lupdate *.ui -ts "+os.path.join(transpath,"uifiles.ts"))
        # os.system(PYLUPDATE+" *.py -ts "+os.path.join(transpath,"pyfiles.ts"))
        # os.system("lconvert -i "+os.path.join(transpath,"uifiles.ts")+" "+os.path.join(transpath,"pyfiles.ts")+" -o "+os.path.join(transpath,MODULENAME+".ts"))
        # os.system("rm "+os.path.join(transpath,"uifiles.ts"))
        # os.system("rm "+os.path.join(transpath,"pyfiles.ts"))
        cmd = (
            PYLUPDATE
            + ' `find ./ -name "*.py"` `find ./ -name "*.ui"` -ts '
            + os.path.join(transpath, MODULENAME + ".ts")
        )
        os.system(cmd)
        print("Updated", os.path.join(transpath, MODULENAME + ".ts"))

    elif arg == "build":
        print(
            "Building (warning, this can be invoked only once per 30 minutes)... ",
            end="",
        )
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url + "export" + key)
        b = io.BytesIO()
        c.setopt(pycurl.WRITEDATA, b)
        c.perform()
        c.close()
        handler = ResponseHandler()
        xml.sax.parseString(b.getvalue(), handler)
        print(handler.data)

    elif arg == "download":
        print("Downloading all.zip in current directory...")
        cmd = "wget -O freecad-addons.zip " + url + "download/all.zip" + key
        os.system(cmd)

    elif arg == "upload":
        print("Sending " + MODULENAME + ".ts... ", end="")
        c = pycurl.Curl()
        fields = [
            (
                "files[" + MODULENAME + ".ts]",
                (c.FORM_FILE, os.path.join(transpath, MODULENAME + ".ts")),
            )
        ]
        c.setopt(pycurl.URL, url + "update-file" + key)
        c.setopt(pycurl.HTTPPOST, fields)
        b = io.BytesIO()
        c.setopt(pycurl.WRITEDATA, b)
        c.perform()
        c.close()
        handler = ResponseHandler()
        xml.sax.parseString(b.getvalue(), handler)
        print(handler.data)

    elif arg == "install":
        zippath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "freecad-addons.zip"
        )
        tempfolder = tempfile.mkdtemp()
        print("creating temp folder " + tempfolder)
        os.chdir(tempfolder)
        if not os.path.exists(zippath):
            print("ERROR: " + zippath + " not found")
            sys.exit()
        shutil.copy(zippath, tempfolder)
        zfile = zipfile.ZipFile(os.path.join(tempfolder, os.path.basename(zippath)))
        print("extracting zip...")
        zfile.extractall()
        os.chdir(transpath)
        if not LANGUAGES:
            LANGUAGES = " ".join([n[:-1] for n in zfile.namelist() if n.endswith("/")])
        for ln in LANGUAGES.split(" "):
            path = os.path.join(tempfolder, ln)
            if not os.path.exists(path):
                print("ERROR: language path", path, "not found!")
            else:
                doLanguage(tempfolder, transpath, ln)

    else:
        print(__doc__)
