# -*- coding: utf8 -*-

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

import BimWelcome,BimSetup,BimProject,BimLevels,BimWindows,BimIfcElements,BimViews
import BimClassification,BimBox,BimTutorial,BimLibrary,BimMaterial,BimIfcQuantities
import BimIfcProperties,BimNudge,BimUnclone,BimPreflight,BimReextrude


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
            if not trash or not trash.isDerivedFrom("App::DocumentObjectGroup"):
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



class BIM_EmptyTrash:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Trash.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_TogglePanels", "Clean Trash"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_TogglePanels", "Deletes from the trash bin all objects that are not used by any other")}

    def Activated(self):

        trash = FreeCAD.ActiveDocument.getObject("Trash")
        if trash and trash.isDerivedFrom("App::DocumentObjectGroup"):
            deletelist = []
            for obj in trash.Group:
                if (len(obj.InList) == 1) and (obj.InList[0] == trash):
                    deletelist.append(obj.Name)
                    deletelist.extend(self.getDeletableChildren(obj))
            if deletelist:
                FreeCAD.ActiveDocument.openTransaction("Empty Trash")
                for name in deletelist:
                    FreeCAD.ActiveDocument.removeObject(name)
                FreeCAD.ActiveDocument.commitTransaction()

    def getDeletableChildren(self,obj):
        
        deletelist = []
        for child in obj.OutList:
            if (len(child.InList) == 1) and (child.InList[0] == obj):
                deletelist.append(child.Name)
                deletelist.extend(self.getDeletableChildren(child))
        return deletelist



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
                'MenuText': QT_TRANSLATE_NOOP("BIM_Sketch", "Sketch"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Sketch", "Creates a new sketch in the current working plane"),
                'Accel'   : 'S,K'}

    def IsActive(self):

        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):

        if hasattr(FreeCAD,"DraftWorkingPlane"):
            FreeCAD.DraftWorkingPlane.setup()
        if hasattr(FreeCADGui,"Snapper"):
            FreeCADGui.Snapper.setGrid()
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



class BIM_Arc_3Points:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Arc_3Points.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Arc_3Points", "Arc 3 points"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Arc_3Points", "Creates an arc by giving 3 points through which the arc should pass"),
                'Accel'   : 'A,T'}

    def IsActive(self):

        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):

        import DraftTrackers
        self.points = []
        self.normal = None
        self.tracker = DraftTrackers.arcTracker()
        self.tracker.autoinvert = False
        if hasattr(FreeCAD,"DraftWorkingPlane"):
            FreeCAD.DraftWorkingPlane.setup()
        FreeCADGui.Snapper.getPoint(callback=self.getPoint,movecallback=self.drawArc)

    def getPoint(self,point,info):
        if not point: # cancelled
            self.tracker.off()
            return
        if not(point in self.points): # avoid same point twice
            self.points.append(point)
        if len(self.points) < 3:
            if len(self.points) == 2:
                self.tracker.on()
            FreeCADGui.Snapper.getPoint(last=self.points[-1],callback=self.getPoint,movecallback=self.drawArc)
        else:
            import Part
            e = Part.Arc(self.points[0],self.points[1],self.points[2]).toShape()
            o = FreeCAD.ActiveDocument.addObject("Part::Feature","Arc")
            o.Shape = e
            self.tracker.off()
            FreeCAD.ActiveDocument.recompute()

    def drawArc(self,point,info):
        
        if len(self.points) == 2:
            import Part
            if point.sub(self.points[1]).Length > 0.001:
                e = Part.Arc(self.points[0],self.points[1],point).toShape()
                self.tracker.normal = e.Curve.Axis.negative() # for some reason the axis always points "backwards"
                self.tracker.basevector = self.tracker.getDeviation()
                self.tracker.setCenter(e.Curve.Center)
                self.tracker.setRadius(e.Curve.Radius)
                self.tracker.setStartPoint(self.points[0])
                self.tracker.setEndPoint(point)



class BIM_Convert:


    def GetResources(self):

        import Arch_rc
        return {'Pixmap'  : ":/icons/Arch_Component.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_Convert", "Convert to BIM type..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Convert", "Converts any object to a BIM component")}

    def IsActive(self):

        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        
        sel = FreeCADGui.Selection.getSelection()
        if sel:
            FreeCADGui.Control.showDialog(BIM_Convert_TaskPanel(sel))



class BIM_Convert_TaskPanel:


    def __init__(self,objs):

        from PySide import QtGui
        self.types = ["Wall","Structure","Rebar","Window","Stairs","Roof","Panel","Frame","Space","Equipment","Component"]
        self.objs = objs
        self.form = QtGui.QListWidget()
        import Arch_rc
        for t in self.types:
            ti = t+"_Tree"
            tx = t
            if t == "Component":
                ti = t
                tx = "Generic component"
            i = QtGui.QListWidgetItem(QtGui.QIcon(":/icons/Arch_"+ti+".svg"),tx)
            i.setToolTip(t)
            self.form.addItem(i)
        self.form.itemDoubleClicked.connect(self.accept)

    def accept(self,idx=None):
        
        i = self.form.currentItem()
        if i:
            import Arch
            FreeCAD.ActiveDocument.openTransaction("Convert to BIM")
            for o in self.objs:
                getattr(Arch,"make"+i.toolTip())(o)
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()
        if idx:
            from DraftGui import todo
            todo.delay(FreeCADGui.Control.closeDialog,None)
        return True


class BIM_Ungroup:


    def GetResources(self):

        import Draft_rc
        return {'Pixmap'  : ":/icons/Draft_AddToGroup.svg",
                'MenuText': QT_TRANSLATE_NOOP("BIM_Convert", "Remove from group"),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Convert", "Removes this object from its parent group")}

    def Activated(self):
        
        sel = FreeCADGui.Selection.getSelection()
        first = True
        if sel:
            for obj in sel:
                for parent in obj.InList:
                    if parent.isDerivedFrom("App::DocumentObjectGroup") or parent.hasExtension("App::GroupExtension"):
                        if obj in parent.Group:
                            if first:
                                FreeCAD.ActiveDocument.openTransaction("Ungroup")
                                first = False
                            if hasattr(parent,"removeObject"):
                                parent.removeObject(obj)
                            else:
                                g = parent.Group
                                g.remove(obj)
                                parent.Group = g
        if not first:
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()



FreeCADGui.addCommand('BIM_TogglePanels',BIM_TogglePanels())
FreeCADGui.addCommand('BIM_Trash',BIM_Trash())
FreeCADGui.addCommand('BIM_EmptyTrash',BIM_EmptyTrash())
FreeCADGui.addCommand('BIM_Copy',BIM_Copy())
FreeCADGui.addCommand('BIM_Clone',BIM_Clone())
FreeCADGui.addCommand('BIM_Help',BIM_Help())
FreeCADGui.addCommand('BIM_Glue',BIM_Glue())
FreeCADGui.addCommand('BIM_Sketch',BIM_Sketch())
FreeCADGui.addCommand('BIM_WPView',BIM_WPView())
FreeCADGui.addCommand('BIM_Arc_3Points',BIM_Arc_3Points())
FreeCADGui.addCommand('BIM_Convert',BIM_Convert())
FreeCADGui.addCommand('BIM_Ungroup',BIM_Ungroup())



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
        
        # set the label of the unit button
        utext = action.text().replace("&","")
        unit = [0,4,1,3,7,5][["Millimeters","Centimeters","Meters","Inches","Feet","Architectural"].index(utext)]
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema",unit)
        if hasattr(FreeCAD.Units,"setSchema"):
            FreeCAD.Units.setSchema(unit)
        action.parent().parent().parent().setText(utext)
        
        # change the unit of the nudge button
        nudge = action.parent().parent().parent().parent().nudge
        nudgeactions = nudge.menu().actions()
        if unit in [2,3,5,7]:
            nudgelabels = ["Custom...","1/16\"","1/8\"","1/4\"","1\"","6\"","1\'","Auto"]
        else:
            nudgelabels = ["Custom...","1 mm","5 mm","1 cm","5 cm","10 cm","50 cm","Auto"]
        for i in range(len(nudgelabels)):
            nudgeactions[i].setText(nudgelabels[i])
        if not "auto" in nudge.text().replace("&","").lower():
            nudge.setText(FreeCAD.Units.Quantity(nudge.text().replace("&","")).UserString)

    def setNudge(action):
        
        utext = action.text().replace("&","")
        if utext == "Custom...":
            # load dialog
            form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogNudgeValue.ui"))
            # center the dialog over FreeCAD window
            mw = FreeCADGui.getMainWindow()
            form.move(mw.frameGeometry().topLeft() + mw.rect().center() - form.rect().center())
            result = form.exec_()
            if not result:
                return
            utext = form.inputField.text()
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
                    try:
                        gitrepo.fetch()
                        if "git pull" in gitrepo.status():
                            self.updateAvailable.emit(True)
                            return
                    except:
                        # can fail for any number of reasons, ex. not being online
                        pass
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

    # main code

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
                
                # nudge button
                nudge = QtGui.QPushButton("Auto")
                nudge.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Nudge.svg")))
                nudge.setFlat(True)
                nudge.setToolTip("The value of the nudge movement (rotation is always 45°).\n\nCTRL+arrows to move\nCTRL+, to rotate left\nCTRL+. to rotate right\nCTRL+PgUp to extend extrusion\nCTRL+PgDown to shrink extrusion\nCTRL+/ to switch between auto and manual mode")
                statuswidget.addWidget(nudge)
                statuswidget.nudge = nudge
                menu = QtGui.QMenu(nudge)
                gnudge = QtGui.QActionGroup(menu)
                for u in ["Custom...","1 mm","5 mm","1 cm","5 cm","10 cm","50 cm","Auto"]:
                    a = QtGui.QAction(gnudge)
                    a.setText(u)
                    menu.addAction(a)
                nudge.setMenu(menu)
                gnudge.triggered.connect(setNudge)

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
                unitLabel.setToolTip("The preferred unit you are currently working with. You can still use any other unit anywhere in FreeCAD")
                statuswidget.addWidget(unitLabel)
                statuswidget.unitLabel = unitLabel
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

