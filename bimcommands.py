#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2017 Yorik van Havre <yorik@uncreated.net>              *
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

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator



class BIM_Welcome:


    def GetResources(self):

        return {'Pixmap'  : ":icons/preferences-system.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_Welcome", "Welcome screen"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Welcome", "Show the welcome screen")}

    def Activated(self):

        # load dialog
        form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogWelcome.ui"))

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        form.move(mw.frameGeometry().topLeft() + mw.rect().center() - form.rect().center())

        # show dialog and run setup dialog afterwards if OK was pressed
        result = form.exec_()
        if result:
            FreeCADGui.runCommand("BIM_Setup")



class BIM_Setup:


    def GetResources(self):

        return {'Pixmap'  : ":icons/preferences-system.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_Setup", "BIM Setup"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Setup", "Set some common FreeCAD preferences for BIM workflow")}

    def Activated(self):

        TECHDRAWDIMFACTOR = 0.16 # How many times TechDraw dim arrows are smaller than Draft

        # load dialog
        from PySide import QtGui
        form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogSetup.ui"))

        # center the dialog over FreeCAD window
        mw = FreeCADGui.getMainWindow()
        form.move(mw.frameGeometry().topLeft() + mw.rect().center() - form.rect().center())

        # fill values from current settings
        unit = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").GetInt("UserSchema",0)
        unit = [0,2,3,3,1,4,0][unit] # less choices in our simplified dialog
        form.settingUnits.setCurrentIndex(unit)
        decimals = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").GetInt("Decimals",2)
        form.settingDecimals.setValue(decimals)
        grid = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetFloat("gridSpacing",10)
        grid = FreeCAD.Units.Quantity(grid,FreeCAD.Units.Length).UserString
        form.settingGrid.setText(grid)
        wp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("defaultWP",0)
        form.settingWP.setCurrentIndex(wp)
        tsize = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetFloat("textheight",10)
        tsize = FreeCAD.Units.Quantity(tsize,FreeCAD.Units.Length).UserString
        form.settingText.setText(tsize)
        font = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetString("textfont","Sans")
        form.settingFont.setCurrentFont(QtGui.QFont(font))
        linewidth = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").GetInt("DefautShapeLineWidth",2)
        form.settingLinewidth.setValue(linewidth)
        dimstyle = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetInt("dimsymbol",0)
        dimstyle = [0,0,1,2][dimstyle] # less choices in our simplified dialog
        form.settingDimstyle.setCurrentIndex(dimstyle)
        asize = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").GetFloat("arrowsize",5)
        asize = FreeCAD.Units.Quantity(asize,FreeCAD.Units.Length).UserString
        form.settingArrowsize.setText(asize)
        author = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetString("prefAuthor","")
        form.settingAuthor.setText(author)
        lic = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetInt("prefLicenseType",0)
        lic = [0,1,2,1,3,4,1,0,0,0][lic] # less choices in our simplified dialog
        form.settingLicense.setCurrentIndex(lic)
        bimdefault = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").GetString("AutoloadModule","")
        form.settingWorkbench.setChecked(bimdefault == "BIMWorkbench")
        newdoc = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetBool("CreateNewDoc",False)
        form.settingNewdocument.setChecked(newdoc)
        bkp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").GetInt("CountBackupFiles",2)
        form.settingBackupfiles.setValue(bkp)
        # TODO - antialiasing?

        # show dialog and exit if cancelled
        result = form.exec_()
        if not result:
            return

        # set preference values
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").SetBool("FirstTime",False)
        unit = form.settingUnits.currentIndex()
        unit = [0,4,1,3,5][unit] # less choices in our simplified dialog
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema",unit)
        decimals = form.settingDecimals.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("Decimals",decimals)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetBool("UseGlobalDecimals",True)
        grid = form.settingGrid.text()
        grid = FreeCAD.Units.Quantity(grid).Value
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetFloat("gridSpacing",grid)
        wp = form.settingWP.currentIndex()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("defaultWP",wp)
        tsize = form.settingText.text()
        tsize = FreeCAD.Units.Quantity(tsize).Value
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetFloat("textheight",tsize)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetFloat("FontSize",tsize) # TODO - check if this needs a mult factor?
        font = form.settingFont.currentFont().family()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetString("textfont",font)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Labels").SetString("LabelFont",font)
        linewidth = form.settingLinewidth.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View").SetInt("DefautShapeLineWidth",linewidth)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("linewidth",linewidth)
        # TODO - TechDraw default line styles
        dimstyle = form.settingDimstyle.currentIndex()
        ddimstyle = [0,2,3][dimstyle] # less choices in our simplified dialog
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetInt("dimsymbol",ddimstyle)
        tdimstyle = [3,0,2][dimstyle] # TechDraw has different order than Draft
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetInt("dimsymbol",tdimstyle)
        asize = form.settingArrowsize.text()
        asize = FreeCAD.Units.Quantity(asize).Value
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft").SetFloat("arrowsize",asize)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/TechDraw/Dimensions").SetFloat("ArrowSize",asize*TECHDRAWDIMFACTOR)
        author = form.settingAuthor.text()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetString("prefAuthor",author)
        lic = form.settingLicense.currentIndex()
        lic = [0,1,2,4,5][lic] # less choices in our simplified dialog
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetInt("prefLicenseType",lic)
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetString("prefLicenseUrl","") # TODO - set correct license URL
        bimdefault = form.settingWorkbench.isChecked()
        if bimdefault:
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General").SetString("AutoloadModule","BIMWorkbench")
        newdoc = form.settingNewdocument.isChecked()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetBool("CreateNewDoc",newdoc)
        bkp = form.settingBackupfiles.value()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Document").SetInt("CountBackupFiles",bkp)

        # set the working plane
        if hasattr(FreeCAD,"DraftWorkingPlane") and hasattr(FreeCADGui,"draftToolBar"):
            if wp == 1:
                FreeCAD.DraftWorkingPlane.alignToPointAndAxis(Vector(0,0,0), Vector(0,0,1), 0)
                FreeCADGui.draftToolBar.wplabel.setText("Top(XY)")
            elif wp == 2:
                FreeCAD.DraftWorkingPlane.alignToPointAndAxis(Vector(0,0,0), Vector(0,1,0), 0)
                FreeCADGui.draftToolBar.wplabel.setText("Front(XZ)")
            elif wp == 3:
                FreeCAD.DraftWorkingPlane.alignToPointAndAxis(Vector(0,0,0), Vector(1,0,0), 0)
                FreeCADGui.draftToolBar.wplabel.setText("Side(YZ)")
            else:
                FreeCADGui.draftToolBar.wplabel.setText("Auto")

        # set Draft toolbar
        if hasattr(FreeCADGui,"draftToolBar"):
            FreeCADGui.draftToolBar.widthButton.setValue(linewidth)
            FreeCADGui.draftToolBar.fontsizeButton.setValue(tsize)



class BIM_Levels:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Levels.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Levels", "Manage levels..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Levels", "Set/modify the different levels of your BIM project")}

    def Activated(self):
        FreeCADGui.Control.showDialog(BIM_Levels_TaskPanel())



class BIM_Levels_TaskPanel:


    def __init__(self):

        from PySide import QtCore,QtGui
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogLevels.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Levels.svg")))
        self.form.levels.setColumnWidth(0,190)
        self.form.levels.setColumnWidth(1,70)
        QtCore.QObject.connect(self.form.levels, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *, int)"), self.editLevel)
        QtCore.QObject.connect(self.form.levels, QtCore.SIGNAL("itemDoubleClicked(QTreeWidgetItem *, int)"), self.showLevel)
        QtCore.QObject.connect(self.form.buttonStore, QtCore.SIGNAL("clicked()"), self.storeView)
        QtCore.QObject.connect(self.form.buttonAdd, QtCore.SIGNAL("clicked()"), self.addLevel)
        QtCore.QObject.connect(self.form.levelName, QtCore.SIGNAL("returnPressed()"), self.updateLevels)
        QtCore.QObject.connect(self.form.levelCoord, QtCore.SIGNAL("returnPressed()"), self.updateLevels)
        QtCore.QObject.connect(self.form.levelHeight, QtCore.SIGNAL("returnPressed()"), self.updateLevels)
        QtCore.QObject.connect(self.form.restoreView, QtCore.SIGNAL("stateChanged(int)"), self.updateLevels)
        QtCore.QObject.connect(self.form.restoreState, QtCore.SIGNAL("stateChanged(int)"), self.updateLevels)
        QtCore.QObject.connect(self.form.buttonDelete, QtCore.SIGNAL("clicked()"), self.deleteLevels)
        self.update()

    def getStandardButtons(self):

        from PySide import QtGui
        return int(QtGui.QDialogButtonBox.Close)

    def accept(self):

        FreeCADGui.Control.closeDialog()

    def reject(self):

        FreeCADGui.Control.closeDialog()

    def update(self,keepSelection=False):

        sel = [it.toolTip(0) for it in self.form.levels.selectedItems()]
        import Draft,Arch_rc
        from PySide import QtGui
        self.form.levels.clear()
        levels = [o for o in FreeCAD.ActiveDocument.Objects if (Draft.getType(o) == "Floor")]
        for level in levels:
            s1 = level.Label
            s2 = FreeCAD.Units.Quantity(level.Placement.Base.z,FreeCAD.Units.Length).UserString
            it = QtGui.QTreeWidgetItem([s1,s2])
            it.setIcon(0,QtGui.QIcon(":/icons/Arch_Floor_Tree.svg"))
            it.setToolTip(0,level.Name)
            self.form.levels.addTopLevelItem(it)
        if keepSelection and sel:
            for i in range(self.form.levels.topLevelItemCount()):
                it = self.form.levels.topLevelItem(i)
                if it.toolTip(0) in sel:
                    self.form.levels.setCurrentItem(it)

    def showLevel(self,item,column):

        level = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
        if level:
            if hasattr(level.Proxy,"show"):
                level.Proxy.show()

    def editLevel(self,item,column):

        if len(self.form.levels.selectedItems()) == 1:
            # dont change the contents if we have more than one floor selected
            level = FreeCAD.ActiveDocument.getObject(item.toolTip(0))
            if level:
                self.form.levelName.setText(level.Label)
                self.form.levelCoord.setText(FreeCAD.Units.Quantity(level.Placement.Base.z,FreeCAD.Units.Length).UserString)
                if hasattr(level,"Height"):
                    self.form.levelHeight.setText(FreeCAD.Units.Quantity(level.Height,FreeCAD.Units.Length).UserString)
                if hasattr(level,"RestoreView"):
                    self.form.restoreView.setChecked(level.RestoreView)
                if hasattr(level,"RestoreState"):
                    self.form.restoreState.setChecked(level.RestoreState)

    def storeView(self):

        for it in self.form.levels.selectedItems():
            level = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
            if level:
                if hasattr(level.Proxy,"writeCamera"):
                    level.Proxy.writeCamera()

    def addLevel(self):
        
        import Arch
        level = Arch.makeFloor()
        self.setLevel(level)
        self.update()
        
    def setLevel(self,level):

        if self.form.levelName.text():
            level.Label = self.form.levelName.text()
        if self.form.levelCoord.text():
            p = FreeCAD.Placement()
            p.Base = FreeCAD.Vector(0,0,FreeCAD.Units.Quantity(self.form.levelCoord.text()).Value)
            level.Placement = p
        if self.form.levelHeight.text():
            level.Height = FreeCAD.Units.Quantity(self.form.levelHeight.text()).Value
        if hasattr(level,"RestoreView"):
            level.RestoreView = self.form.restoreView.isChecked()
        if hasattr(level,"RestoreState"):
            level.RestoreState = self.form.restoreState.isChecked()

    def updateLevels(self,arg=None):
        
        for it in self.form.levels.selectedItems():
            level = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
            if level:
                self.setLevel(level)
        self.update(keepSelection=True)

    def deleteLevels(self):

        dels = []
        for it in self.form.levels.selectedItems():
            level = FreeCAD.ActiveDocument.getObject(it.toolTip(0))
            if level:
                dels.append(level.Name)
        for d in dels:
            FreeCAD.ActiveDocument.removeObject(d)
        self.update()

class BIM_Windows:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Windows.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Windows", "Manage doors and windows..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Levels", "Manage the different doors and windows of your BIM project")}

    def Activated(self):
        FreeCADGui.Control.showDialog(BIM_Windows_TaskPanel())



class BIM_Windows_TaskPanel:


    def __init__(self):

        from PySide import QtGui
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogWindows.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Windows.svg")))
        #QtCore.QObject.connect(self.form.buttonRefresh, QtCore.SIGNAL("clicked()"), self.getFiles)

    def getStandardButtons(self):

        from PySide import QtGui
        return int(QtGui.QDialogButtonBox.Close)

    def accept(self):

        FreeCADGui.Control.closeDialog()

    def reject(self):

        FreeCADGui.Control.closeDialog()



class BIM_TogglePanels:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_TogglePanels.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_TogglePanels", "Toggle panels"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Toggle report panels on/off"),
                'Accel': 'Ctrl+0'}

    def Activated(self):

        from  PySide import QtGui
        mw = FreeCADGui.getMainWindow()
        windows = [mw.findChild(QtGui.QWidget,"Python console"),mw.findChild(QtGui.QWidget,"Selection view"),mw.findChild(QtGui.QWidget,"Report view")]
        if windows[0].isVisible():
            for w in windows:
                w.hide()
        else:
            for w in windows:
                w.show()



FreeCADGui.addCommand('BIM_Welcome',BIM_Welcome())
FreeCADGui.addCommand('BIM_Setup',BIM_Setup())
FreeCADGui.addCommand('BIM_Levels',BIM_Levels())
FreeCADGui.addCommand('BIM_Windows',BIM_Windows())
FreeCADGui.addCommand('BIM_TogglePanels',BIM_TogglePanels())



def setStatusIcons(show=True):

    "shows or hides the BIM icons in the status bar"

    def toggle(): FreeCADGui.runCommand("BIM_TogglePanels")

    mw = FreeCADGui.getMainWindow()
    if mw:
        st = mw.statusBar()
        from PySide import QtCore,QtGui
        statuswidget = st.findChild(QtGui.QPushButton,"BIMStatusWidget")
        if show:
            if statuswidget:
                statuswidget.show()
            else:
                statuswidget = QtGui.QPushButton()
                statuswidget.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_TogglePanels.svg")))
                statuswidget.setText("")
                statuswidget.setToolTip("Toggle report panels on/off")
                statuswidget.setObjectName("BIMStatusWidget")
                QtCore.QObject.connect(statuswidget,QtCore.SIGNAL("pressed()"),toggle)
                st.addPermanentWidget(statuswidget)
        else:
            if statuswidget:
                statuswidget.hide()
