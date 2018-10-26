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

html = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }</style></head><body>inserthere</body></html>"""

pixYes = QtGui.QPixmap(":/icons/button_valid.svg").scaled(16,16)
pixNo = QtGui.QPixmap(":/icons/button_right.svg").scaled(16,16)
pixEmpty = QtGui.QPixmap()


def tutorialWidget():

    url = "https://www.freecadweb.org/wiki/BIM_ingame_tutorial"

    form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogTutorial.ui"))
    form.setObjectName("BIMTutorial")

    # load tutorial from wiki
    u = urllib2.urlopen(url)
    p = u.read().replace("\n"," ")

    # setup title and progress bar
    steps = len(re.findall("infotext",p))-1
    step = 1
    form.progressBar.setValue(0)

    # setup description texts and goals
    descriptions = [""]+re.findall("<p><br /> </p><p><br /> </p> (.*?)<p><b>Tutorial step",p)
    goal1 = re.findall("goal1\">(.*?)</div",p)
    goal2 = re.findall("goal1\">(.*?)</div",p)

    form.textEdit.setHtml(html.replace("inserthere",descriptions[step]))
    form.labelGoal1.setText(goal1[step])
    form.labelGoal2.setText(goal2[step])

    dw = QtGui.QDockWidget()
    dw.setWindowTitle("BIM Tutorial - step "+str(step)+" / "+str(steps))
    dw.setWidget(form)
    return dw


def launch():

    m = FreeCADGui.getMainWindow()
    w = m.findChild(QtGui.QDockWidget,"BIMTutorial")
    if not w:
        m.addDockWidget(QtCore.Qt.RightDockWidgetArea,tutorialWidget())


def update():
    return
