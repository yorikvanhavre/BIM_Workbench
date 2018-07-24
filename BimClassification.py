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

import os,FreeCAD,FreeCADGui,Arch_rc
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
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Classification.svg")))

        # set help line
        self.form.labelDownload.setText(self.form.labelDownload.text().replace("%s",os.path.join(FreeCAD.getUserAppDataDir(),"BIM","Classification")))

        # fill materials list
        for obj in FreeCAD.ActiveDocument.Objects:
            if obj.isDerivedFrom("App::MaterialObject"):
                s1 = obj.Label
                s2 = ""
                if "StandardCode" in obj.Material:
                    s2 = obj.Material["StandardCode"]
                it = QtGui.QTreeWidgetItem([s1,s2])
                it.setIcon(0,QtGui.QIcon(":/icons/Arch_Material.svg"))
                it.setToolTip(0,obj.Name)
                self.form.treeMaterials.addTopLevelItem(it)
                if obj in FreeCADGui.Selection.getSelection():
                    self.form.treeMaterials.setCurrentItem(it)

        # fill available classifications
        p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch").GetString("DefaultClassificationSystem","")
        presetdir = os.path.join(FreeCAD.getUserAppDataDir(),"BIM","Classification")
        if os.path.isdir(presetdir):
            for f in os.listdir(presetdir):
                if f.endswith(".xml"):
                    n = os.path.splitext(f)[0]
                    self.form.comboSystem.addItem(n)
                    if n == p:
                        self.form.comboSystem.setCurrentIndex(self.form.comboSystem.count()-1)

        # connect signals
        QtCore.QObject.connect(self.form.comboSystem, QtCore.SIGNAL("currentIndexChanged(int)"), self.update)
        QtCore.QObject.connect(self.form.buttonApply, QtCore.SIGNAL("clicked()"), self.apply)
        QtCore.QObject.connect(self.form.buttonRename, QtCore.SIGNAL("clicked()"), self.rename)
        QtCore.QObject.connect(self.form.search, QtCore.SIGNAL("textEdited(QString)"), self.update)
        QtCore.QObject.connect(self.form.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        self.form.move(mw.frameGeometry().topLeft() + mw.rect().center() - self.form.rect().center())

        self.update()
        self.form.show()

    def update(self,search=""):

        self.form.treeClass.clear()
        
        # save as default
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch").SetString("DefaultClassificationSystem",self.form.comboSystem.currentText())

        if isinstance(search,int):
            search = ""
        if self.form.search.text():
            search = self.form.search.text()
        if search:
            search = search.lower()

        system = self.form.comboSystem.currentText()
        if not system:
            return

        if not system in self.Classes:
            self.Classes[system] = self.build(system)
        if not self.Classes[system]:
            return

        for c in self.Classes[system]:
            it = None
            if not c[1]: c[1] = ""
            if search:
                if (search in c[0].lower()) or (search in c[1].lower()):
                    it = QtGui.QTreeWidgetItem([c[0]+" "+c[1]])
                    it.setToolTip(0,c[1])
                    self.form.treeClass.addTopLevelItem(it)
            else:
                it = QtGui.QTreeWidgetItem([c[0]+" "+c[1]])
                it.setToolTip(0,c[1])
                self.form.treeClass.addTopLevelItem(it)
            if c[2]:
                self.addChildren(c[2],it,search)

    def addChildren(self,children,parent,search=""):

        if children:
            for c in children:
                it = None
                if not c[1]: c[1] = ""
                if search:
                    if (search in c[0].lower()) or (search in c[1].lower()):
                        it = QtGui.QTreeWidgetItem([c[0]+" "+c[1]])
                        it.setToolTip(0,c[1])
                        self.form.treeClass.addTopLevelItem(it)
                else:
                    it = QtGui.QTreeWidgetItem([c[0]+" "+c[1]])
                    it.setToolTip(0,c[1])
                    if parent:
                        parent.addChild(it)
                if c[2]:
                    self.addChildren(c[2],it,search)

    def build(self,system):
        
        # a replacement function to parse xml that doesn't depend on expat

        preset = os.path.join(FreeCAD.getUserAppDataDir(),"BIM","Classification",system+".xml")
        if not os.path.exists(preset):
            return None
        import codecs,re
        d = Item(None)
        with codecs.open(preset,"r","utf-8") as f:
            currentItem = d
            for l in f:
                if "<Item>" in l:
                    currentItem = Item(currentItem)
                    currentItem.parent.children.append(currentItem)
                if "</Item>" in l:
                    currentItem = currentItem.parent
                elif currentItem and re.findall("<ID>(.*?)</ID>",l):
                    currentItem.ID = re.findall("<ID>(.*?)</ID>",l)[0]
                elif currentItem and re.findall("<Name>(.*?)</Name>",l):
                    currentItem.Name = re.findall("<Name>(.*?)</Name>",l)[0]
                elif currentItem and re.findall("<Description>(.*?)</Description>",l) and not currentItem.Name:
                    currentItem.Name = re.findall("<Description>(.*?)</Description>",l)[0]
        return [self.listize(c) for c in d.children]

    def listize(self,item):
        return [item.ID, item.Name, [self.listize(it) for it in item.children]]

    def build_xmddom(self,system):

        # currently not working for me because of the infamous expat/coin bug in debian...

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
        
        if self.form.treeMaterials.selectedItems() and len(self.form.treeClass.selectedItems()) == 1:
            c = self.form.treeClass.selectedItems()[0].text(0)
            for m in self.form.treeMaterials.selectedItems():
                m.setText(1,c)

    def rename(self):
        
        if self.form.treeMaterials.selectedItems() and len(self.form.treeClass.selectedItems()) == 1:
            c = self.form.treeClass.selectedItems()[0].toolTip(0)
            for m in self.form.treeMaterials.selectedItems():
                m.setText(0,c)

    def accept(self):
        
        root = self.form.treeMaterials.invisibleRootItem()
        first = True
        standard = self.form.comboSystem.currentText()
        for i in range(root.childCount()):
            item = root.child(i)
            code = item.text(1)
            l = item.text(0)
            if code:
                obj = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
                if obj:
                    m = obj.Material
                    m["StandardCode"] = standard+" "+code
                    if m != obj.Material:
                        if first:
                            FreeCAD.ActiveDocument.openTransaction("Change material codes")
                            first = False
                        obj.Material = m
                    if l != obj.Label:
                        if first:
                            FreeCAD.ActiveDocument.openTransaction("Change material codes")
                            first = False
                        obj.Label = l
                    if obj.ViewObject.isEditing():
                        if hasattr(obj.ViewObject,"Proxy") and hasattr(obj.ViewObject.Proxy,"taskd"):
                            obj.ViewObject.Proxy.taskd.form.FieldCode.setText(standard+" "+code)
                            obj.ViewObject.Proxy.taskd.form.FieldName.setText(l)
        if not first:
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()
        self.form.hide()
        return True

class Item:

    # only used by the non-expat version

    def __init__(self,parent):
        self.parent = parent
        self.ID = None
        self.Name = None
        self.children = []


FreeCADGui.addCommand('BIM_Classification',BIM_Classification())
