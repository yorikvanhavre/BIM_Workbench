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

"""The BIM library tool"""

import os,FreeCAD,FreeCADGui,sys

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator

FILTERS = ["*.fcstd","*.FCStd","*.FCSTD","*.stp","*.STP","*.step","*.STEP", "*.brp", "*.BRP", "*.brep", "*.BREP", "*.ifc", "*.IFC", "*.sat", "*.SAT"]


class BIM_Library:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Library.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Library", "Library..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Library", "Opens the objects library")}

    def Activated(self):

        libok = False
        self.librarypath = FreeCAD.ParamGet('User parameter:Plugins/parts_library').GetString('destination','')
        if self.librarypath:
            if os.path.exists(self.librarypath):
                libok = True
        else:
            # check if the library is at the standard addon location
            addondir = os.path.join(FreeCAD.getUserAppDataDir(),"Mod","parts_library")
            if os.path.exists(addondir):
                FreeCAD.ParamGet('User parameter:Plugins/parts_library').SetString('destination',addondir)
                libok = True
        if libok:
            FreeCADGui.Control.showDialog(BIM_Library_TaskPanel())


class BIM_Library_TaskPanel:


    def __init__(self):

        from PySide import QtCore,QtGui
        self.librarypath = FreeCAD.ParamGet('User parameter:Plugins/parts_library').GetString('destination','')
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogLibrary.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Library.svg")))
        # setting up a flat (no directories) file model for search
        self.filemodel = QtGui.QStandardItemModel()
        self.filemodel.setColumnCount(1)
        # setting up a directory model that shows only fcstd, step and brep
        self.dirmodel = LibraryModel()
        self.dirmodel.setRootPath(self.librarypath)
        self.dirmodel.setNameFilters(FILTERS)
        self.dirmodel.setNameFilterDisables(False)
        self.form.tree.setModel(self.dirmodel)
        self.form.tree.doubleClicked[QtCore.QModelIndex].connect(self.insert)
        self.form.buttonInsert.clicked.connect(self.insert)
        self.modelmode = 1 # 0 = File search, 1 = Dir mode
        # Don't show columns for size, file type, and last modified
        self.form.tree.setHeaderHidden(True)
        self.form.tree.hideColumn(1)
        self.form.tree.hideColumn(2)
        self.form.tree.hideColumn(3)
        self.form.tree.setRootIndex(self.dirmodel.index(self.librarypath))
        self.form.searchBox.textChanged.connect(self.onSearch)
        self.form.buttonBimObject.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","bimobject.png")))
        self.form.buttonBimObject.clicked.connect(self.onBimObject)
        self.form.buttonNBSLibrary.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","nbslibrary.png")))
        self.form.buttonNBSLibrary.clicked.connect(self.onNBSLibrary)
        self.form.buttonBimTool.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","bimtool.png")))
        self.form.buttonBimTool.clicked.connect(self.onBimTool)

    def onSearch(self,text):

        from PySide import QtGui
        import PartGui
        if text:
            self.form.tree.setModel(self.filemodel)
            self.filemodel.clear()
            for dp, dn,fn in os.walk(self.librarypath):
                for f in fn:
                    if text.lower() in f.lower():
                        if not os.path.isdir(os.path.join(dp,f)):
                            it = QtGui.QStandardItem(f)
                            it.setToolTip(os.path.join(dp,f))
                            self.filemodel.appendRow(it)
                            if f.endswith('.fcstd'):
                                it.setIcon(QtGui.QIcon(':icons/freecad-doc.png'))
                            elif f.endswith('.ifc'):
                                it.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","IFC.svg")))
                            else:
                                it.setIcon(QtGui.QIcon(':icons/Tree_Part.svg'))
            self.modelmode = 0
            
        else:
            #self.form.tree.clear()
            self.form.tree.setModel(self.dirmodel)
            self.dirmodel.setRootPath(self.librarypath)
            self.dirmodel.setNameFilters(FILTERS)
            self.dirmodel.setNameFilterDisables(False)
            self.form.tree.setRootIndex(self.dirmodel.index(self.librarypath))
            self.modelmode = 1
            self.form.tree.setHeaderHidden(True)
            self.form.tree.hideColumn(1)
            self.form.tree.hideColumn(2)
            self.form.tree.hideColumn(3)

    def urlencode(self,text):

        from PySide import QtGui
        print(text,type(text))
        if sys.version_info.major < 3:
            import urllib
            return urllib.quote_plus(text)
        else:
            import urllib.parse
            return urllib.parse.quote_plus(text)

    def onBimObject(self):
        
        term = self.form.searchBox.text()
        if term:
            QtGui.QDesktopServices.openUrl("https://www.bimobject.com/en/product?filetype=8&freetext="+self.urlencode(term))

    def onNBSLibrary(self):
        
        term = self.form.searchBox.text()
        if term:
            QtGui.QDesktopServices.openUrl("https://www.nationalbimlibrary.com/en/search/?facet=Xo-P0w&searchTerm="+self.urlencode(term))

    def onBimTool(self):
        
        term = self.form.searchBox.text()
        if term:
            QtGui.QDesktopServices.openUrl("https://www.bimtool.com/Catalog.aspx?criterio="+self.urlencode(term))

    def needsFullSpace(self):

        return True

    def getStandardButtons(self):

        from PySide import QtGui
        return int(QtGui.QDialogButtonBox.Close)

    def reject(self):

        FreeCADGui.Control.closeDialog()
        FreeCAD.ActiveDocument.recompute()

    def insert(self, index=None):
        
        if not index:
            index = self.form.tree.selectedIndexes()
            if not index:
                return
            index = index[0]
        if self.modelmode == 1:
            path = self.dirmodel.filePath(index)
        else:
            path = self.filemodel.itemFromIndex(index).toolTip()
        before = FreeCAD.ActiveDocument.Objects
        self.name = os.path.splitext(os.path.basename(path))[0]
        if path.lower().endswith(".stp") or path.lower().endswith(".step") or path.lower().endswith(".brp") or path.lower().endswith(".brep"):
            self.place(path)
        elif path.lower().endswith(".fcstd"):
            FreeCADGui.ActiveDocument.mergeProject(path)
            from DraftGui import todo
            todo.delay(self.reject,None)
        elif path.lower().endswith(".ifc"):
            import importIFC
            importIFC.insert(path,FreeCAD.ActiveDocument.Name)
            from DraftGui import todo
            todo.delay(self.reject,None)
        elif path.lower().endswith(".sat"):
            try:
                import CadExchangerIO
            except:
                FreeCAD.Console.PrintError("Error: Unable to import SAT files - CadExchanger addon must be installed")
            else:
                path = CadExchangerIO.insert(path,FreeCAD.ActiveDocument.Name,returnpath = True)
                self.place(path)
        FreeCADGui.Selection.clearSelection()
        for o in FreeCAD.ActiveDocument.Objects:
            if not o in before:
                FreeCADGui.Selection.addSelection(o)
        FreeCADGui.SendMsgToActiveView("ViewSelection")

    def place(self,path):

        import Part
        self.shape = Part.read(path)
        if hasattr(FreeCADGui,"Snapper"):
            import DraftTrackers
            self.box = DraftTrackers.ghostTracker(self.shape,dotted=True,scolor=(0.0,0.0,1.0),swidth=1.0)
            self.delta = self.shape.BoundBox.Center
            self.box.move(self.delta)
            self.box.on()
            if hasattr(FreeCAD,"DraftWorkingPlane"):
                FreeCAD.DraftWorkingPlane.setup()
            self.origin = self.makeOriginWidget()
            FreeCADGui.Snapper.getPoint(movecallback=self.mouseMove,callback=self.mouseClick,extradlg=self.origin)
        else:
            Part.show(self.shape)

    def makeOriginWidget(self):
        
        from PySide import QtGui
        w = QtGui.QWidget()
        w.setWindowTitle("Insertion point")
        w.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Library.svg")))
        l = QtGui.QVBoxLayout()
        w.setLayout(l)
        c = QtGui.QComboBox()
        c.ObjectName = "comboOrigin"
        w.comboOrigin = c
        c.addItems(["Origin","Top left","Top center","Top right","Middle left","Middle center","Middle right","Bottom left","Bottom center","Bottom right"])
        l.addWidget(c)
        return w

    def mouseMove(self,point,info):
        
        self.box.move(point.add(self.getDelta()))

    def mouseClick(self,point,info):
        
        if point:
            import Arch,Part
            self.box.off()
            self.shape.translate(point.add(self.getDelta()))
            obj = Arch.makeEquipment()
            obj.Shape = self.shape
            obj.Label = self.name
        self.reject()

    def getDelta(self):
        
        d = FreeCAD.Vector(-self.shape.BoundBox.Center.x,-self.shape.BoundBox.Center.y,0)
        idx = self.origin.comboOrigin.currentIndex()
        if idx <= 0:
            return FreeCAD.Vector()
        elif idx == 1:
            return d.add(FreeCAD.Vector(self.shape.BoundBox.XLength/2,-self.shape.BoundBox.YLength/2,0))
        elif idx == 2:
            return d.add(FreeCAD.Vector(0,-self.shape.BoundBox.YLength/2,0))
        elif idx == 3:
            return d.add(FreeCAD.Vector(-self.shape.BoundBox.XLength/2,-self.shape.BoundBox.YLength/2,0))
        elif idx == 4:
            return d.add(FreeCAD.Vector(self.shape.BoundBox.XLength/2,0,0))
        elif idx == 5:
            return d
        elif idx == 6:
            return d.add(FreeCAD.Vector(-self.shape.BoundBox.XLength/2,0,0))
        elif idx == 7:
            return d.add(FreeCAD.Vector(self.shape.BoundBox.XLength/2,self.shape.BoundBox.YLength/2,0))
        elif idx == 8:
            return d.add(FreeCAD.Vector(0,self.shape.BoundBox.YLength/2,0))
        elif idx == 9:
            return d.add(FreeCAD.Vector(-self.shape.BoundBox.XLength/2,self.shape.BoundBox.YLength/2,0))
            

if FreeCAD.GuiUp:

    from PySide import QtCore,QtGui

    class LibraryModel(QtGui.QFileSystemModel):

        "a custom QFileSystemModel that displays freecad file icons"

        def __init__(self):

            QtGui.QFileSystemModel.__init__(self)

        def data(self, index, role):

            if index.column() == 0 and role == QtCore.Qt.DecorationRole:
                if index.data().lower().endswith('.fcstd'):
                    return QtGui.QIcon(':icons/freecad-doc.png')
                elif index.data().lower().endswith('.ifc'):
                    return QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","IFC.svg"))
                elif index.data().lower() == "private":
                    return QtGui.QIcon.fromTheme("folder-lock")
            return super(LibraryModel, self).data(index, role)


FreeCADGui.addCommand('BIM_Library',BIM_Library())
