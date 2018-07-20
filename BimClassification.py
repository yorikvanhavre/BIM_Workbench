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

"""This module contains FreeCAD commands for the BIM workbench"""

import os,FreeCAD,FreeCADGui,Arch_rc,xml.sax
from PySide import QtCore,QtGui


def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator



class BIM_Classification:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Classification.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Classification", "Manage Material classification..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Classification", "Manage how the different materials of this documents use classification systems")}
                
    def IsActive(self):

        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):

        # init checks
        if not hasattr(self,"Classes"):
            self.Classes = {}

        # load the form and set the tree model up
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogClassification.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_IfcElements.svg")))
        
        # set help line
        self.form.labelDownload.setText(self.form.labelDownload.text()+" "+os.path.join(FreeCAD.getUserAppDataDir(),"BIM","Classification"))

        # fill materials list
        for obj in FreeCAD.ActiveDocument.Objects:
            if obj.isDerivedFrom("App::MaterialObject"):
                s1 = obj.Label
                s2 = ""
                if "StandardCode" in obj.Material:
                    s2 = obj.Material.StandardCode
                it = QtGui.QTreeWidgetItem([s1,s2])
                it.setIcon(0,QtGui.QIcon(":/icons/Arch_Material.svg"))
                it.setToolTip(0,obj.Name)
                self.form.treeMaterials.addTopLevelItem(it)
                if obj in Gui.Selection.getSelection():
                    self.form.treeMaterials.setCurrentItem(it)
        
        # fill available classifications
        presetdir = os.path.join(FreeCAD.getUserAppDataDir(),"BIM","Classification")
        if os.path.isdir(presetdir):
            for f in os.listdir(presetdir):
                if f.endswith(".xml"):
                    self.form.comboSystem.addItem(os.path.splitext(f)[0])

        # connect signals
        QtCore.QObject.connect(self.form.comboSystem, QtCore.SIGNAL("currentIndexChanged(int)"), self.update)
        QtCore.QObject.connect(self.form.buttonApply, QtCore.SIGNAL("clicked()"), self.apply)
        QtCore.QObject.connect(self.form.buttonApply, QtCore.SIGNAL("textEdited(QString)"), self.update)

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        self.form.move(mw.frameGeometry().topLeft() + mw.rect().center() - self.form.rect().center())

        self.update()
        self.form.show()

    def update(self,search=""):
        
        self.form.treeClass.clear()

        system = self.form.comboSystem.currentText()
        if not system:
            return
        
        if not system in self.Classes:
            self.Classes[system] = self.build(system)
        if not self.Classes[system]:
            return

        for cl in self.Classes[system]:
            top = self.form.treeClass.addTopLevelItem(c[0]+" "+cl[1])
            if cl[2]:
                self.addChildren(cl[2],top)
        
    def addChildren(self,children,parent):
        
        if children:
            for c in children:
                top = parent.addChild(c[0]+" "+c[1])
                if c[2]:
                    addChildren(c[2],top)

    def build(self,system):

        print("Building tables for",system,"...")
        preset = os.path.join(FreeCAD.getUserAppDataDir(),"BIM","Classification",system+".xml")
        if not os.path.exists(preset):
            return None
        handler = ClassHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(preset)
        return handler.classes

    def buildOld(self,system):

        print("Building tables for",system,"...")
        preset = os.path.join(FreeCAD.getUserAppDataDir(),"BIM","Classification",system+".xml")
        if not os.path.exists(preset):
            return None
        import xml.dom.minidom
        d = xml.dom.minidom.parse(preset)
        return self.getChildren(d.getElementsByTagName("Items")[0])
            
    def getChildren(self,node):
        
        children = []
        for child in node.childNodes:
            if child.hasChildNodes():
                ID = None
                Name = None
                children = []
                for tag in child.childNodes:
                    if tag.hasChildNodes():
                        if tag.tagName == "ID":
                            ID = tag.childNodes[0].wholeText
                        elif tag.tagName == "Name":
                            Name = tag.childNodes[0].wholeText
                        elif tag.tagName == "Children":
                            children = self.getChildren(tag.childNodes)
                if ID and Name:
                    children.append([ID,name,children])

    def apply(self):
        pass

    def accept(self):
        pass


class ClassHandler(xml.sax.ContentHandler):

    "A XML handler to process class definitions"

    def __init__(self):

        self.classes = []
        self.currentparent = None
        self.currentID = None
        self.currentName = None
        self.currentlist = []
        self.charbuffer = []
        self.writing = False
        
    # Call when raw text is read
    
    def characters(self, data):
        
        if self.writing:
            self.charbuffer.append(data)

    # Call when an element starts

    def startElement(self, tag, attributes):

        if tag == "ID":
            self.writing = True
        if tag == "Name":
            self.writing = True

    # Call when an elements ends

    def endElement(self, tag):

        if tag == "ID":
            self.writing = False
            self.currentID = "".join(self.charbuffer)
        elif tag == "Name":
            self.writing = False
            self.currentName = "".join(self.charbuffer)


FreeCADGui.addCommand('BIM_Classification',BIM_Classification())
