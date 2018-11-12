#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2018 Yorik van Havre <yorik@uncreated.net>              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
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

"""This is the tutorial of the BIM workbench"""

import os,FreeCAD,FreeCADGui,re,sys
if sys.version_info.major < 3:
    import urllib2
else:
    import urllib.request as urllib2
from PySide import QtCore,QtGui

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator

html = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }</style></head><body>inserthere</body></html>"""

pixYes = QtGui.QPixmap(":/icons/button_valid.svg").scaled(16,16)
pixNo = QtGui.QPixmap(":/icons/button_right.svg").scaled(16,16)
pixEmpty = QtGui.QPixmap()
url = "https://www.freecadweb.org/wiki/BIM_ingame_tutorial"


class BIM_Tutorial:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Tutorial.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Tutorial", "BIM Tutorial"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Tutorial", "Starts or continues the BIM in-game tutorial")}

    def Activated(self):

        # find existing tutorial
        m = FreeCADGui.getMainWindow()
        self.dock = m.findChild(QtGui.QDockWidget,"BIMTutorial")

        if not self.dock:

            # set the tutorial dialog up
            self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogTutorial.ui"))
            self.form.setObjectName("BIMTutorial")
            self.form.progressBar.setValue(0)
            self.form.labelGoal1.setText("")
            self.form.labelGoal2.setText("")
            self.form.labelIcon1.setText("")
            self.form.labelIcon2.setText("")
            self.form.buttonPrevious.setEnabled(False)
            self.form.buttonNext.setEnabled(False)
            self.form.buttonPrevious.clicked.connect(self.previous)
            self.form.buttonNext.clicked.connect(self.next)
            self.form.labelTasks.hide()

            self.dock = QtGui.QDockWidget()
            self.dock.setWidget(self.form)

            m.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.dock)

            # fire the loading after displaying the widget
            from DraftGui import todo
            todo.delay(self.load,None)

    def load(self,arg=None):

        # initial loading

        if not hasattr(self,"form") or not self.form or not hasattr(self,"dock"):
            return

        # load tutorial from wiki
        u = urllib2.urlopen(url)
        p = u.read()
        if sys.version_info.major >= 3:
            p = p.decode("utf8")
        p = p.replace("\n"," ")
        p = p.replace("\"/wiki/","\"https://www.freecadweb.org/wiki/")

        # setup title and progress bar
        self.steps = len(re.findall("infotext",p))-1

        # setup description texts and goals
        self.descriptions = [""]+re.findall("<p><br /> </p><p><br /> </p> (.*?)<p><b>Tutorial step",p)
        self.goal1 = re.findall("goal1\">(.*?)</div",p)
        self.goal2 = re.findall("goal2\">(.*?)</div",p)
        
        # check where we are
        self.step = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").GetInt("CurrentTutorialStep",0)
        if self.step:
            self.update()
        else:
            self.next()

    def next(self):

        self.step += 1
        self.update()

    def previous(self):

        self.step -= 1
        self.update()


    def update(self):

        if not hasattr(self,"form") or not self.form or not hasattr(self,"dock"):
            return

        # stay within bounds!
        if self.step > self.steps:
            self.step = self.steps
        elif self.step < 1:
            self.step = 1

        t = self.descriptions[self.step]
        
        # downlaod images (QTextEdit cannot load online images)
        imagepaths = re.findall("<img.*?src=\"(.*?)\"",t)
        if imagepaths:
            storedimages = []
            self.form.textEdit.setHtml(html.replace("downloading images...",t))
            store = os.path.join(FreeCAD.getUserAppDataDir(),"BIM")
            for path in imagepaths:
                name = re.findall("[\\w.-]+\\.(?i)(?:jpg|png|gif|bmp)",path)[-1]
                storename = os.path.join(store,name)
                if not os.path.exists(storename):
                    u = urllib2.urlopen(path)
                    p = u.read()
                    f = open(storename,"wb")
                    f.write(p)
                    f.close()
                t = t.replace(path,"file://"+storename.replace("\\","/"))

        #print(t)
        
        # set contents
        self.form.textEdit.setHtml(html.replace("inserthere",t))
        self.form.labelGoal1.setText(self.goal1[self.step])
        if self.goal1[self.step]:
            self.form.labelIcon1.setPixmap(pixNo)
        else:
            self.form.labelIcon1.setPixmap(pixEmpty)
        self.form.labelGoal2.setText(self.goal2[self.step])
        if self.goal2[self.step]:
            self.form.labelIcon2.setPixmap(pixNo)
        else:
            self.form.labelIcon2.setPixmap(pixEmpty)
        if self.goal1[self.step] or self.goal2[self.step]:
            self.form.labelTasks.show()
        else:
            self.form.labelTasks.hide()
        self.dock.setWindowTitle("BIM Tutorial - step "+str(self.step)+" / "+str(self.steps))
        self.form.progressBar.setValue(int((float(self.step)/self.steps)*100))
        
        # save the current step
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").SetInt("CurrentTutorialStep",self.step)

        if self.steps > self.step:
            self.form.buttonNext.setEnabled(True)
        else:
            self.form.buttonNext.setEnabled(False)
        if self.step == 1:
            self.form.buttonPrevious.setEnabled(False)
        else:
            self.form.buttonPrevious.setEnabled(True)



FreeCADGui.addCommand('BIM_Tutorial',BIM_Tutorial())
