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

import os,FreeCAD,FreeCADGui,DraftTools

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator


# import commands that are defined in their separate files

import BimWelcome,BimSetup,BimProject,BimLevels,BimWindows,BimIfcElements,BimViews,BimClassification,BimBox,BimTutorial,BimLibrary,BimMaterial


# additional, smaller commands that are defined directly in this file

class BIM_TogglePanels:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_TogglePanels.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_TogglePanels", "Toggle panels"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Toggle report panels on/off"),
                'Accel': 'Ctrl+0'}

    def Activated(self):

        from  PySide import QtGui
        mw = FreeCADGui.getMainWindow()
        togglebutton = None
        st = mw.statusBar()
        statuswidget = st.findChild(QtGui.QToolBar,"BIMStatusWidget")
        if statuswidget:
            if hasattr(statuswidget,"togglebutton"):
                togglebutton = statuswidget.togglebutton
        windows = [mw.findChild(QtGui.QWidget,"Python console"),mw.findChild(QtGui.QWidget,"Report view"),mw.findChild(QtGui.QWidget,"Selection view")]
        if windows[0].isVisible():
            for w in windows:
                w.hide()
            if togglebutton:
                    togglebutton.setChecked(False)
        else:
            for w in windows:
                w.show()
            if togglebutton:
                togglebutton.setChecked(True)


class BIM_Trash:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Trash.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_TogglePanels", "Move to Trash"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Moves the selected objects to the Trash folder"),
                'Accel': 'Shift+Del'}

    def Activated(self):

        if FreeCADGui.Selection.getSelection():
            trash = FreeCAD.ActiveDocument.getObject("Trash")
            if trash:
                if not trash.isDerivedFrom("App::DocumentObjectGroup"):
                    trash = None
            if not trash:
                trash = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Trash")
            for obj in FreeCADGui.Selection.getSelection():
                trash.addObject(obj)
                # check for parents still there
                for par in obj.InList:
                    if (par != trash) and hasattr(par,"Group"):
                        if obj in par.Group:
                            if hasattr(par,"removeObject"):
                                par.removeObject(obj)
                            else:
                                g = par.Group
                                g.remove(obj)
                                par.Group = g
                obj.ViewObject.hide()

    def IsActive(self):

        if FreeCADGui.Selection.getSelection():
            return True
        else:
            return False



class BIM_Copy(DraftTools.Move):


    def __init__(self):
        DraftTools.Move.__init__(self)
        self.copymode = True

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Copy.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Copy", "Copy"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Copies selected objects to another location"),
                'Accel': 'C,P'}



class BIM_Clone(DraftTools.Draft_Clone):


    def __init__(self):
        DraftTools.Draft_Clone.__init__(self)
        self.moveAfterCloning = True


class BIM_Help:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Help.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Help", "BIM Help"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Help", "Opens the BIM help page on the FreeCAD documentation website")}

    def Activated(self):

        from PySide import QtCore,QtGui
        QtGui.QDesktopServices.openUrl("https://www.freecadweb.org/wiki/BIM_Workbench")



class BIM_Glue:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Glue.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Glue", "Glue"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Glue", "Joins selected shapes into one non-parametric shape")}

    def IsActive(self):

        if FreeCADGui.Selection.getSelection():
            return True
        else:
            return False

    def Activated(self):

        sel = FreeCADGui.Selection.getSelection()
        if sel:
            rem = []
            shapes = []
            for obj in sel:
                if obj.isDerivedFrom("Part::Feature"):
                    if obj.Shape:
                        shapes.append(obj.Shape)
                        rem.append(obj.Name)
            import Part
            if shapes:
                comp = Part.makeCompound(shapes)
                FreeCAD.ActiveDocument.openTransaction("Glue")
                Part.show(comp)
                for name in rem:
                    FreeCAD.ActiveDocument.removeObject(name)
                FreeCAD.ActiveDocument.commitTransaction()



class BIM_Sketch:


    def GetResources(self):

        return {'Pixmap'  : ":/icons/Sketcher_NewSketch.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_Sketch", "New Sketch"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Sketch", "Creates a new sketch in the current working plane and enters edit mode")}

    def IsActive(self):

        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):

        sk = FreeCAD.ActiveDocument.addObject('Sketcher::SketchObject','Sketch')
        sk.MapMode = "Deactivated"
        p = FreeCAD.DraftWorkingPlane.getPlacement()
        p.Base = FreeCAD.DraftWorkingPlane.position
        sk.Placement = p
        FreeCADGui.ActiveDocument.setEdit(sk.Name)
        FreeCADGui.activateWorkbench('SketcherWorkbench')


class BIM_WPView:

    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_WPView.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_WPView", "Working Plane View"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_WPView", "Aligns the view on the current item in BIM Views window or on the current working plane"),
                'Accel'   : '9'}

    def IsActive(self):

        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):

        done = False
        try:
            import BimViews
        except:
            pass
        else:
            v = BimViews.findWidget()
            if v:
                i = v.currentItem()
                if i:
                    # Aligning on current widget item
                    BimViews.show(i)
                    done = True
                elif hasattr(v,"lastSelected"):
                    BimViews.show(v.lastSelected)
                    # Aligning on stored widget item
                    done = True
        if not done:
            # Aligning on working plane
            c = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()
            r = FreeCAD.DraftWorkingPlane.getRotation().Rotation.Q
            c.orientation.setValue(r)


FreeCADGui.addCommand('BIM_TogglePanels',BIM_TogglePanels())
FreeCADGui.addCommand('BIM_Trash',BIM_Trash())
FreeCADGui.addCommand('BIM_Copy',BIM_Copy())
FreeCADGui.addCommand('BIM_Clone',BIM_Clone())
FreeCADGui.addCommand('BIM_Help',BIM_Help())
FreeCADGui.addCommand('BIM_Glue',BIM_Glue())
FreeCADGui.addCommand('BIM_Sketch',BIM_Sketch())
FreeCADGui.addCommand('BIM_WPView',BIM_WPView())


# Status bar buttons


def setStatusIcons(show=True):

    "shows or hides the BIM icons in the status bar"
    
    from PySide import QtCore,QtGui

    def toggle(state):
        FreeCADGui.runCommand("BIM_TogglePanels")

    def toggleBimViews(state):
        FreeCADGui.runCommand("BIM_Views")

    def addonMgr():
        mw = FreeCADGui.getMainWindow()
        if mw:
            st = mw.statusBar()
            statuswidget = st.findChild(QtGui.QToolBar,"BIMStatusWidget")
            if statuswidget:
                updatebutton = statuswidget.findChild(QtGui.QPushButton,"UpdateButton")
                if updatebutton:
                    statuswidget.actions()[-1].setVisible(False)
        FreeCADGui.runCommand("Std_AddonMgr")

    def setUnit(action):
        utext = action.text().replace("&","")
        unit = [0,4,1,3,7,5][["Millimeters","Centimeters","Meters","Inches","Feet","Architectural"].index(utext)]
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema",unit)
        if hasattr(FreeCAD.Units,"setSchema"):
            FreeCAD.Units.setSchema(unit)
        action.parent().parent().parent().setText(utext)
        
    class CheckWorker(QtCore.QThread):
        updateAvailable = QtCore.Signal(bool)
    
        def __init__(self):
            QtCore.QThread.__init__(self)
    
        def run(self):
            try:
                import git
            except:
                return
            FreeCAD.Console.PrintLog("Checking for available updates of the BIM workbench\n")
            bimdir = os.path.join(FreeCAD.getUserAppDataDir(),"Mod","BIM")
            if os.path.exists(bimdir):
                if os.path.exists(bimdir + os.sep + '.git'):
                    gitrepo = git.Git(bimdir)
                    gitrepo.fetch()
                    if "git pull" in gitrepo.status():
                        self.updateAvailable.emit(True)
                        return
            self.updateAvailable.emit(False)

    def checkUpdates():
        FreeCAD.bim_update_checker = CheckWorker()
        FreeCAD.bim_update_checker.updateAvailable.connect(showUpdateButton)
        FreeCAD.bim_update_checker.start()
        
    def showUpdateButton(avail):
        if avail:
            mw = FreeCADGui.getMainWindow()
            if mw:
                st = mw.statusBar()
                statuswidget = st.findChild(QtGui.QToolBar,"BIMStatusWidget")
                if statuswidget:
                    updatebutton = statuswidget.findChild(QtGui.QPushButton,"UpdateButton")
                    if updatebutton:
                        #updatebutton.show() # doesn't work for some reason
                        statuswidget.actions()[-1].setVisible(True)
        if hasattr(FreeCAD,"bim_update_checker"):
            del FreeCAD.bim_update_checker

    mw = FreeCADGui.getMainWindow()
    if mw:
        st = mw.statusBar()
        statuswidget = st.findChild(QtGui.QToolBar,"BIMStatusWidget")
        if show:
            if statuswidget:
                statuswidget.show()
            else:
                statuswidget = QtGui.QToolBar()
                statuswidget.setObjectName("BIMStatusWidget")
                
                # units chooser
                unitLabel = QtGui.QPushButton("Unit")
                unitLabel.setObjectName("UnitLabel")
                unitLabel.setFlat(True)
                unit = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").GetInt("UserSchema",0)
                menu = QtGui.QMenu(unitLabel)
                gUnits = QtGui.QActionGroup(menu)
                for u in ["Millimeters","Centimeters","Meters","Inches","Feet","Architectural"]:
                    a = QtGui.QAction(gUnits)
                    a.setText(u)
                    menu.addAction(a)
                unitLabel.setMenu(menu)
                gUnits.triggered.connect(setUnit)
                unitLabel.setText(["Millimeters","Meters","Inches","Inches","Centimeters","Architectural","Millimeters","Feet"][unit])
                statuswidget.addWidget(unitLabel)
                st.addPermanentWidget(statuswidget)
                
                # report panels toggle button
                togglebutton = QtGui.QPushButton()
                bwidth = togglebutton.fontMetrics().boundingRect("AAAA").width()
                togglebutton.setMaximumWidth(bwidth)
                togglebutton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_TogglePanels.svg")))
                togglebutton.setText("")
                togglebutton.setToolTip("Toggle report panels on/off")
                togglebutton.setFlat(True)
                togglebutton.setCheckable(True)
                rv = mw.findChild(QtGui.QWidget,"Python console")
                if rv and rv.isVisible():
                    togglebutton.setChecked(True)
                statuswidget.togglebutton = togglebutton
                QtCore.QObject.connect(togglebutton,QtCore.SIGNAL("clicked(bool)"),toggle)
                statuswidget.addWidget(togglebutton)

                # bim views widget toggle button
                bimviewsbutton = QtGui.QPushButton()
                bwidth = bimviewsbutton.fontMetrics().boundingRect("AAAA").width()
                bimviewsbutton.setMaximumWidth(bwidth)
                bimviewsbutton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Views.svg")))
                bimviewsbutton.setText("")
                bimviewsbutton.setToolTip("Toggle BIM views panel on/off")
                bimviewsbutton.setFlat(True)
                bimviewsbutton.setCheckable(True)
                if BimViews.findWidget():
                    bimviewsbutton.setChecked(True)
                statuswidget.bimviewsbutton = bimviewsbutton
                QtCore.QObject.connect(bimviewsbutton,QtCore.SIGNAL("clicked(bool)"),toggleBimViews)
                statuswidget.addWidget(bimviewsbutton)

                # update notifier button (starts hidden)
                updatebutton = QtGui.QPushButton()
                updatebutton.setObjectName("UpdateButton")
                updatebutton.setMaximumWidth(bwidth)
                updatebutton.setIcon(QtGui.QIcon(":/icons/view-refresh.svg"))
                updatebutton.setText("")
                updatebutton.setToolTip("An update to the BIM workbench is available. Click here to open the addons manager.")
                updatebutton.setFlat(True)
                QtCore.QObject.connect(updatebutton,QtCore.SIGNAL("pressed()"),addonMgr)
                updatebutton.hide()
                statuswidget.addWidget(updatebutton)
                QtCore.QTimer.singleShot(2500, checkUpdates) # delay a bit the check for BIM WB update...
        else:
            if statuswidget:
                statuswidget.hide()
            else:
                # when switching workbenches, the toolbar sometimes "jumps"
                # out of the status bar to any other dock area...
                statuswidget = mw.findChild(QtGui.QToolBar,"BIMStatusWidget")
                if statuswidget:
                    statuswidget.hide()

