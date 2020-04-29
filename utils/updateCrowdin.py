#!/usr/bin/python

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2015 Yorik van Havre <yorik@uncreated.net>              *
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

from __future__ import print_function

import sys,os,xml.sax,pycurl,StringIO

"Interacts with Crowdin. Options: status, build, download, update"

# handler for the command responses
class ResponseHandler( xml.sax.ContentHandler ):

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
        if self.current in ["language","success","error"]:
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
            pc = int((float(self.translated)/self.total)*100)
            self.data += " : " + str(pc) + "%\n"
        elif self.current == "message":
            self.data += content

if __name__ == "__main__":

    # only one argument allowed
    arg = sys.argv[1:]
    if len(arg) != 1:
        print(__doc__)
        sys.exit()
    arg = arg[0]

    # getting API key stored in ~/.crowdin-freecad
    configfile = os.path.expanduser("~")+os.sep+".crowdin-freecadaddons"
    if not os.path.exists(configfile):
        print("Config file not found!")
        sys.exit()
    f = open(configfile)
    url = "https://api.crowdin.com/api/project/freecad-addons/"
    key = "?key="+f.read().strip()
    f.close()

    if arg == "build":
        print("Building (warning, this can be invoked only once per 30 minutes)...")
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url+"export"+key)
        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()
        c.close()
        handler = ResponseHandler()
        xml.sax.parseString(b.getvalue(),handler)
        print(handler.data)

    elif arg == "download":
        print("Downloading all.zip in current directory...")
        cmd = "wget -O freecad-addons.zip "+url+"download/all.zip"+key
        os.system(cmd)

    elif arg == "update":
        basepath = os.path.dirname(os.path.abspath("."))
        print("Sending BIM.ts...")
        c = pycurl.Curl()
        fields = [('files[BIM.ts]', (c.FORM_FILE, basepath+"/translations/BIM.ts"))]
        c.setopt(pycurl.URL, url+"update-file"+key)
        c.setopt(pycurl.HTTPPOST, fields)
        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()
        c.close()
        handler = ResponseHandler()
        xml.sax.parseString(b.getvalue(),handler)
        print(handler.data)

    else:
        print(__doc__)
