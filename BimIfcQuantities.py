# -*- coding: utf-8 -*-

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

"""This module contains FreeCAD commands for the BIM workbench"""

import os,FreeCAD,FreeCADGui,Arch_rc,Draft
from PySide import QtCore,QtGui


def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator

qprops = ["Length","Width","Height","Area","HorizontalArea","VerticalArea","Volume"] # quantities columns


class BIM_IfcQuantities:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_IfcQuantities.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_IfcQuantities", "Manage IFC quantities..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_IfcQuantities", "Manage how the quantities of different elements of of your BIM project will be exported to IFC")}

    def IsActive(self):

        if FreeCAD.ActiveDocument:
            # disable for pre-v0.18
            if float(FreeCAD.Version()[0]+"."+FreeCAD.Version()[1]) < 0.18:
                return False
            return True
        else:
            return False

    def Activated(self):

        # build objects list
        self.objectslist = {}
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj,"IfcType"):
                self.objectslist[obj.Name] = obj.IfcType
            elif hasattr(obj,"IfcRole"):
                self.objectslist[obj.Name] = obj.IfcRole
        try:
            import ArchIFC
            self.ifcroles = ArchIFC.IfcTypes
        except:
            import ArchComponent
            self.ifcroles = ArchComponent.IfcRoles

        # load the form and set the tree model up
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogIfcQuantities.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_IfcQuantities.svg")))

        # quantities tab
        self.qmodel = QtGui.QStandardItemModel()
        self.form.quantities.setModel(self.qmodel)
        self.form.quantities.setUniformRowHeights(True)
        self.form.quantities.setItemDelegate(QtGui.QStyledItemDelegate())
        self.quantitiesDrawn = False
        QtCore.QObject.connect(self.qmodel, QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.setChecked)
        QtCore.QObject.connect(self.form.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.form.quantities, QtCore.SIGNAL("clicked(QModelIndex)"), self.onClickTree)
        QtCore.QObject.connect(self.form.onlyVisible, QtCore.SIGNAL("stateChanged(int)"), self.update)

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        self.form.move(mw.frameGeometry().topLeft() + mw.rect().center() - self.form.rect().center())

        self.update()
        self.form.show()

    def decamelize(self,s):

        return ''.join([' '+c if c.isupper() else c for c in s]).strip(' ')

    def update(self,index=None):
        
        "updates the tree widgets in all tabs"

        import Draft

        # quantities tab - only fill once

        if not self.quantitiesDrawn:

            self.qmodel.setHorizontalHeaderLabels(["Label"] + [self.decamelize(s) for s in qprops])
            quantheaders = self.form.quantities.header() #QHeaderView instance
            if hasattr(quantheaders,"setClickable"): # qt4
                quantheaders.setClickable(True)
            else: # qt5
                quantheaders.setSectionsClickable(True)
            quantheaders.sectionClicked.connect(self.quantHeaderClicked)

            # sort by type

            groups = {}
            for name,role in self.objectslist.items():
                groups.setdefault(role,[]).append(name)
            for names in groups.values():
                for name in names:
                    obj = FreeCAD.ActiveDocument.getObject(name)
                    if obj:
                        if (not self.form.onlyVisible.isChecked()) or obj.ViewObject.isVisible():
                            if obj.isDerivedFrom("Part::Feature") and not (Draft.getType(obj) == "Site"):
                                it1 = QtGui.QStandardItem(obj.Label)
                                it1.setToolTip(name)
                                it1.setEditable(False)
                                if QtCore.QFileInfo(":/icons/Arch_"+obj.Proxy.Type+"_Tree.svg").exists():
                                    icon = QtGui.QIcon(":/icons/Arch_"+obj.Proxy.Type+"_Tree.svg")
                                else:
                                    icon = QtGui.QIcon(":/icons/Arch_Component.svg")
                                it1.setIcon(icon)
                                props = []
                                for prop in qprops:
                                    it = QtGui.QStandardItem()
                                    val = None
                                    if prop == "Volume":
                                        if obj.Shape and hasattr(obj.Shape,"Volume"):
                                            val = FreeCAD.Units.Quantity(obj.Shape.Volume,FreeCAD.Units.Volume)
                                            it.setText(val.getUserPreferred()[0].replace(u"^3",u"³"))
                                            it.setCheckable(True)
                                    else:
                                        if hasattr(obj,prop) and (not "Hidden" in obj.getEditorMode(prop)):
                                            val = getattr(obj,prop)
                                            it.setText(val.getUserPreferred()[0].replace(u"^2",u"²"))
                                            it.setCheckable(True)
                                    if val != None:
                                        if hasattr(obj,"IfcAttributes") and ("Export"+prop in obj.IfcAttributes) and (obj.IfcAttributes["Export"+prop] == "True"):
                                            it.setCheckState(QtCore.Qt.Checked)
                                        if val == 0:
                                            it.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","warning.svg")))
                                    if prop in ["Area","HorizontalArea","VerticalArea","Volume"]:
                                        it.setEditable(False)
                                    props.append(it)
                                self.qmodel.appendRow([it1]+props)
            self.quantitiesDrawn = True

    def accept(self):

        self.form.hide()
        changed = False
        for row in range(self.qmodel.rowCount()):
            name = self.qmodel.item(row,0).toolTip()
            obj = FreeCAD.ActiveDocument.getObject(name)
            if obj:
                for i in range(len(qprops)):
                    item = self.qmodel.item(row,i+1)
                    val = item.text()
                    sav = bool(item.checkState())
                    if i < 3: # Length, Width, Height, value can be changed
                        if hasattr(obj,qprops[i]):
                            if getattr(obj,qprops[i]).getUserPreferred()[0] != val:
                                setattr(obj,qprops[i],val)
                                if not changed:
                                    FreeCAD.ActiveDocument.openTransaction("Change quantities")
                                changed = True
                    if hasattr(obj,"IfcAttributes"):
                        d = obj.IfcAttributes
                        if sav:
                            if (not "Export"+qprops[i] in d) or (d["Export"+qprops[i]] == "False"):
                                d["Export"+qprops[i]] = "True"
                                obj.IfcAttributes = d
                                if not changed:
                                    FreeCAD.ActiveDocument.openTransaction("Change quantities")
                                changed = True
                        else:
                            if ("Export"+qprops[i] in d):
                                if d["Export"+qprops[i]] == "True":
                                    d["Export"+qprops[i]] = "False"
                                    obj.IfcAttributes = d
                                    if not changed:
                                        FreeCAD.ActiveDocument.openTransaction("Change quantities")
                                    changed = True

        if changed:
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()

    def setChecked(self,id1,id2):

        sel = self.form.quantities.selectedIndexes()
        state = self.qmodel.itemFromIndex(id1).checkState()
        if len(sel) > 7:
            for idx in sel:
                if idx.column() == id1.column():
                    item = self.qmodel.itemFromIndex(idx)
                    if item.checkState() != state:
                        item.setCheckState(state)

    def quantHeaderClicked(self,col):

        sel = self.form.quantities.selectedIndexes()
        state = None
        if len(sel) > 7:
            for idx in sel:
                if idx.column() == col:
                    item = self.qmodel.itemFromIndex(idx)
                    if state == None:
                        # take the state to apply from the first selected item
                        state = QtCore.Qt.Checked
                        if item.checkState():
                            state = QtCore.Qt.Unchecked
                    item.setCheckState(state)

    def onClickTree(self,index=None):

        FreeCADGui.Selection.clearSelection()
        sel = self.form.quantities.selectedIndexes()
        mode = None
        mat = None
        for index in sel:
            if index.column() == 0:
                obj = FreeCAD.ActiveDocument.getObject(self.qmodel.itemFromIndex(index).toolTip())
                if obj:
                    FreeCADGui.Selection.addSelection(obj)


FreeCADGui.addCommand('BIM_IfcQuantities',BIM_IfcQuantities())
