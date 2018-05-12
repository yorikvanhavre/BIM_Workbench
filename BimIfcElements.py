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

import os,FreeCAD,FreeCADGui
from PySide import QtCore,QtGui


def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator



class BIM_IfcElements:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_IfcElements.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_IfcElements", "Manage IFC elements..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_IfcElements", "Manage how the different elements of of your BIM project will be exported to IFC")}
                
    def IsActive(self):

        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):

        # build objects list
        self.objectslist = {}
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj,"IfcRole"):
                self.objectslist[obj.Name] = obj.IfcRole
        import ArchComponent
        self.ifcroles = ArchComponent.IfcRoles

        # load the form and set the tree model up
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogIfcElements.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_IfcElements.svg")))
        self.model = QtGui.QStandardItemModel()
        self.form.tree.setModel(self.model)
        self.form.tree.setUniformRowHeights(True)
        self.form.tree.setItemDelegate(IfcElementsDelegate(dialog=self))
        self.form.globalMode.addItems([" "]+self.ifcroles)
        QtCore.QObject.connect(self.form.groupMode, QtCore.SIGNAL("currentIndexChanged(int)"), self.update)
        QtCore.QObject.connect(self.form.tree, QtCore.SIGNAL("clicked(QModelIndex)"), self.setGlobalMode)
        QtCore.QObject.connect(self.form.onlyVisible, QtCore.SIGNAL("stateChanged(int)"), self.update)
        QtCore.QObject.connect(self.form.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.form.globalMode, QtCore.SIGNAL("currentIndexChanged(int)"), self.getGlobalMode)


        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        self.form.move(mw.frameGeometry().topLeft() + mw.rect().center() - self.form.rect().center())

        self.update()
        self.form.show()

    def update(self,index=None):
        
        import Draft,Arch_rc
        
        # store current state of tree into self.objectslist before redrawing
        for row in range(self.model.rowCount()):
            name = self.model.item(row,0).toolTip()
            if name:
                self.objectslist[name] = self.model.item(row,1).text()
            if self.model.item(row,0).hasChildren():
                for childrow in range(self.model.item(row,0).rowCount()):
                    name = self.model.item(row,0).child(childrow,0).toolTip()
                    if name:
                        self.objectslist[name] = self.model.item(row,0).child(childrow,1).text()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Name","IFC type"])
        
        if self.form.groupMode.currentIndex() == 1: # group by type
    
            groups = {}
            for name,role in self.objectslist.items():
                obj = FreeCAD.ActiveDocument.getObject(name)
                if obj:
                    if (not self.form.onlyVisible.isChecked()) or obj.ViewObject.isVisible():
                        groups.setdefault(role,[]).append(name)

            for group in groups.keys():
                s1 = group + " ("+str(len(groups[group]))+")"
                top = QtGui.QStandardItem(s1)
                self.model.appendRow([top,QtGui.QStandardItem()])
                for name in groups[group]:
                    obj = FreeCAD.ActiveDocument.getObject(name)
                    if obj:
                        it1 = QtGui.QStandardItem(obj.Label)
                        if QtCore.QFileInfo(":/icons/Arch_"+obj.Proxy.Type+"_Tree.svg").exists():
                            icon = QtGui.QIcon(":/icons/Arch_"+obj.Proxy.Type+"_Tree.svg")
                        else:
                            icon = QtGui.QIcon(":/icons/Arch_Component.svg")
                        it1.setIcon(icon)
                        it1.setToolTip(obj.Name)
                        it2 = QtGui.QStandardItem(group)
                        if group != obj.IfcRole:
                            it2.setIcon(QtGui.QIcon(":/icons/edit-edit.svg"))
                        top.appendRow([it1,it2])
                top.sortChildren(0)
            self.form.tree.expandAll()

        else: # alphabetic order

            for name,role in self.objectslist.items():
                obj = FreeCAD.ActiveDocument.getObject(name)
                if obj:
                    if (not self.form.onlyVisible.isChecked()) or obj.ViewObject.isVisible():
                        it1 = QtGui.QStandardItem(obj.Label)
                        if QtCore.QFileInfo(":/icons/Arch_"+obj.Proxy.Type+"_Tree.svg").exists():
                            icon = QtGui.QIcon(":/icons/Arch_"+obj.Proxy.Type+"_Tree.svg")
                        else:
                            icon = QtGui.QIcon(":/icons/Arch_Component.svg")
                        it1.setIcon(icon)
                        it1.setToolTip(obj.Name)
                        it2 = QtGui.QStandardItem(role)
                        if role != obj.IfcRole:
                            it2.setIcon(QtGui.QIcon(":/icons/edit-edit.svg"))
                        self.model.appendRow([it1,it2])
        
        self.model.sort(0)

    def setGlobalMode(self,index=None):

        FreeCADGui.Selection.clearSelection()
        sel = self.form.tree.selectedIndexes()
        mode = None
        for index in sel:
            if index.column() == 0:
                obj = FreeCAD.ActiveDocument.getObject(self.model.itemFromIndex(index).toolTip())
                if obj:
                    FreeCADGui.Selection.addSelection(obj)
        for index in sel:
            if index.column() == 1:
                if index.data() in self.ifcroles:
                    if mode:
                        if index.data() != mode:
                            mode = None
                            break
                    else:
                        mode = index.data()
        if mode:
            self.form.globalMode.setCurrentIndex(self.ifcroles.index(mode)+1)
        else:
            self.form.globalMode.setCurrentIndex(0)

    def getGlobalMode(self,index=-1):

        changed = False
        if index >= 1:
            role = self.ifcroles[index-1]
            sel = self.form.tree.selectedIndexes()
            for index in sel:
                if index.column() == 1:
                    if role:
                        if index.data() != role:
                            self.model.setData(index, role)
                            changed = True
        if changed:
            self.update()

    def accept(self):

        # get current state of tree
        self.form.hide()
        for row in range(self.model.rowCount()):
            name = self.model.item(row,0).toolTip()
            if name:
                self.objectslist[name] = self.model.item(row,1).text()
            if self.model.item(row,0).hasChildren():
                for childrow in range(self.model.item(row,0).rowCount()):
                    name = self.model.item(row,0).child(childrow,0).toolTip()
                    if name:
                        self.objectslist[name] = self.model.item(row,0).child(childrow,1).text()
        changed = False
        for name,role in self.objectslist.items():
            obj = FreeCAD.ActiveDocument.getObject(name)
            if obj:
                if obj.IfcRole != role:
                    if not changed:
                        FreeCAD.ActiveDocument.openTransaction("Change IFC role")
                        changed = True
                    obj.IfcRole = role
        if changed:
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()


class IfcElementsDelegate(QtGui.QStyledItemDelegate):


    def __init__(self, parent=None, dialog=None, *args):

        import ArchComponent
        self.roles = ArchComponent.IfcRoles
        self.dialog = dialog
        QtGui.QStyledItemDelegate.__init__(self, parent, *args)

    def createEditor(self,parent,option,index):

        if index.column() == 1:
            editor = QtGui.QComboBox(parent)
        else:
            editor = QtGui.QLineEdit(parent)
        return editor

    def setEditorData(self, editor, index):

        if index.column() == 1:
            idx = -1
            editor.addItems(self.roles)
            if index.data() in self.roles:
                idx = self.roles.index(index.data())
            editor.setCurrentIndex(idx)
        else:
            editor.setText(index.data())

    def setModelData(self, editor, model, index):

        if index.column() == 1:
            if editor.currentIndex() == -1:
                model.setData(index, "")
            else:
                model.setData(index,self.roles[editor.currentIndex()])
        else:
            model.setData(index,editor.text())
            item = model.itemFromIndex(index)
            obj = FreeCAD.ActiveDocument.getObject(item.toolTip())
            if obj:
                obj.Label = editor.text()
        self.dialog.update()


FreeCADGui.addCommand('BIM_IfcElements',BIM_IfcElements())
