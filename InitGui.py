# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 Yorik van Havre <yorik@uncreated.net>              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

# main workbench class


class BIMWorkbench(Workbench):
    def __init__(self):
        self.__class__.MenuText = "BIM"
        self.__class__.ToolTip = "BIM workbench"
        self.__class__.Icon = """
/* XPM */
static char * IFC_xpm[] = {
"16 16 9 1",
" 	c None",
".	c #D80742",
"+	c #C20B5E",
"@	c #B11A71",
"#	c #0E4A94",
"$	c #A12288",
"%	c #61398E",
"&	c #983563",
"*	c #1E8BA6",
"                ",
"     #   ..     ",
"    ### ....    ",
"   ## ##+  ..   ",
"  ##  .##   ..  ",
" ##  +. ##   .. ",
" ## $$$+##**..  ",
"  #%$$$%#**&.   ",
"  $$% ##*+..&*  ",
" $$$###*@..  ** ",
" $$  #**$@@  ** ",
"  $$  **%$  **  ",
"   $$  **  **   ",
"    $$$$****    ",
"     $$  **     ",
"                "};
"""

    def Initialize(self):
        # QT macro

        def QT_TRANSLATE_NOOP(scope, text):
            return text

        if hasattr(FreeCAD, "Qt"):
            translate = FreeCAD.Qt.translate
        else:

            def translate(scope, text):
                return text

        if not hasattr(Gui, "listCommands"):
            Gui.listCommands = Gui.Command.listAll

        import DraftTools
        import Arch

        import BimCommands
        import BimWelcome
        import BimSetup
        import BimWindows
        import BimIfcElements
        import BimViews
        import BimClassification
        import BimBox
        import BimTutorial
        import BimLibrary
        import BimMaterial
        import BimIfcQuantities
        import BimIfcProperties
        import BimNudge
        import BimPreflight
        import BimReextrude
        import BimDiff
        import BimIfcExplorer
        import BimLayers
        import BimTogglePanels
        import BimTrash
        import BimClone
        import BimStructure
        import BimStatusBar
        import BimWorkingPlaneTools
        import BimWrappedTools
        import BimReorder
        import BimProjectManager

        # add translations path
        FreeCADGui.addLanguagePath(BimStatusBar.getLanguagePath())

        # create BIM commands
        # maybe this should go back in each module...

        # these should be move out of BimCommands
        FreeCADGui.addCommand("BIM_Help", BimCommands.BIM_Help())
        FreeCADGui.addCommand("BIM_Examples", BimCommands.BIM_Examples())
        FreeCADGui.addCommand("BIM_Glue", BimCommands.BIM_Glue())
        FreeCADGui.addCommand("BIM_Sketch", BimCommands.BIM_Sketch())
        FreeCADGui.addCommand("BIM_WPView", BimCommands.BIM_WPView())
        FreeCADGui.addCommand("BIM_Convert", BimCommands.BIM_Convert())
        FreeCADGui.addCommand("BIM_Ungroup", BimCommands.BIM_Ungroup())
        FreeCADGui.addCommand("BIM_Rewire", BimCommands.BIM_Rewire())
        FreeCADGui.addCommand("BIM_Door", BimCommands.BIM_Door())
        FreeCADGui.addCommand("BIM_Leader", BimCommands.BIM_Leader())
        FreeCADGui.addCommand("BIM_Background", BimCommands.BIM_Background())
        FreeCADGui.addCommand("BIM_MoveView", BimCommands.BIM_MoveView())
        FreeCADGui.addCommand(
            "BIM_ProjectManager", BimProjectManager.BIM_ProjectManager()
        )
        FreeCADGui.addCommand("BIM_SetWPTop", BimWorkingPlaneTools.BIM_SetWPTop())
        FreeCADGui.addCommand("BIM_SetWPFront", BimWorkingPlaneTools.BIM_SetWPFront())
        FreeCADGui.addCommand("BIM_SetWPSide", BimWorkingPlaneTools.BIM_SetWPSide())
        FreeCADGui.addCommand("BIM_TogglePanels", BimTogglePanels.BIM_TogglePanels())
        FreeCADGui.addCommand("BIM_Trash", BimTrash.BIM_Trash())
        FreeCADGui.addCommand("BIM_EmptyTrash", BimTrash.BIM_EmptyTrash())
        FreeCADGui.addCommand("BIM_Copy", BimClone.BIM_Copy())
        FreeCADGui.addCommand("BIM_Clone", BimClone.BIM_Clone())
        FreeCADGui.addCommand("BIM_Column", BimStructure.BIM_Column())
        FreeCADGui.addCommand("BIM_Beam", BimStructure.BIM_Beam())
        FreeCADGui.addCommand("BIM_Slab", BimStructure.BIM_Slab())
        FreeCADGui.addCommand("BIM_ResetCloneColors", BimClone.BIM_ResetCloneColors())
        FreeCADGui.addCommand("BIM_Welcome", BimWelcome.BIM_Welcome())
        FreeCADGui.addCommand("BIM_Setup", BimSetup.BIM_Setup())
        FreeCADGui.addCommand("BIM_Windows", BimWindows.BIM_Windows())
        FreeCADGui.addCommand("BIM_IfcElements", BimIfcElements.BIM_IfcElements())
        FreeCADGui.addCommand("BIM_Views", BimViews.BIM_Views())
        FreeCADGui.addCommand(
            "BIM_Classification", BimClassification.BIM_Classification()
        )
        FreeCADGui.addCommand("BIM_Box", BimBox.BIM_Box())
        FreeCADGui.addCommand("BIM_Tutorial", BimTutorial.BIM_Tutorial())
        FreeCADGui.addCommand("BIM_Library", BimLibrary.BIM_Library())
        FreeCADGui.addCommand("BIM_Material", BimMaterial.BIM_Material())
        FreeCADGui.addCommand("BIM_IfcQuantities", BimIfcQuantities.BIM_IfcQuantities())
        FreeCADGui.addCommand("BIM_IfcProperties", BimIfcProperties.BIM_IfcProperties())
        FreeCADGui.addCommand("BIM_Nudge_Switch", BimNudge.BIM_Nudge_Switch())
        FreeCADGui.addCommand("BIM_Nudge_Up", BimNudge.BIM_Nudge_Up())
        FreeCADGui.addCommand("BIM_Nudge_Down", BimNudge.BIM_Nudge_Down())
        FreeCADGui.addCommand("BIM_Nudge_Left", BimNudge.BIM_Nudge_Left())
        FreeCADGui.addCommand("BIM_Nudge_Right", BimNudge.BIM_Nudge_Right())
        FreeCADGui.addCommand("BIM_Nudge_Extend", BimNudge.BIM_Nudge_Extend())
        FreeCADGui.addCommand("BIM_Nudge_Shrink", BimNudge.BIM_Nudge_Shrink())
        FreeCADGui.addCommand("BIM_Nudge_RotateLeft", BimNudge.BIM_Nudge_RotateLeft())
        FreeCADGui.addCommand("BIM_Nudge_RotateRight", BimNudge.BIM_Nudge_RotateRight())
        FreeCADGui.addCommand("BIM_Unclone", BimClone.BIM_Unclone())
        FreeCADGui.addCommand("BIM_Preflight", BimPreflight.BIM_Preflight())
        FreeCADGui.addCommand("BIM_Diff", BimDiff.BIM_Diff())
        FreeCADGui.addCommand("BIM_IfcExplorer", BimIfcExplorer.BIM_IfcExplorer())
        FreeCADGui.addCommand("BIM_Layers", BimLayers.BIM_Layers())
        FreeCADGui.addCommand("BIM_Reextrude", BimReextrude.BIM_Reextrude())
        FreeCADGui.addCommand("BIM_Reorder", BimReorder.BIM_Reorder())

        # wrapped tools from other workbenches
        FreeCADGui.addCommand("BIM_Builder", BimWrappedTools.BIM_Builder())
        FreeCADGui.addCommand("BIM_Offset2D", BimWrappedTools.BIM_Offset2D())
        FreeCADGui.addCommand("BIM_Extrude", BimWrappedTools.BIM_Extrude())
        FreeCADGui.addCommand("BIM_Cut", BimWrappedTools.BIM_Cut())
        FreeCADGui.addCommand("BIM_Fuse", BimWrappedTools.BIM_Fuse())
        FreeCADGui.addCommand("BIM_Common", BimWrappedTools.BIM_Common())
        FreeCADGui.addCommand("BIM_Compound", BimWrappedTools.BIM_Compound())
        FreeCADGui.addCommand("BIM_SimpleCopy", BimWrappedTools.BIM_SimpleCopy())
        FreeCADGui.addCommand("BIM_TDPage", BimWrappedTools.BIM_TDPage())
        FreeCADGui.addCommand("BIM_TDArchView", BimWrappedTools.BIM_TDArchView())
        FreeCADGui.addCommand("BIM_ImagePlane", BimWrappedTools.BIM_ImagePlane())
        FreeCADGui.addCommand(
            "BIM_DimensionAligned", BimWrappedTools.BIM_DimensionAligned()
        )
        FreeCADGui.addCommand(
            "BIM_DimensionHorizontal", BimWrappedTools.BIM_DimensionHorizontal()
        )
        FreeCADGui.addCommand(
            "BIM_DimensionVertical", BimWrappedTools.BIM_DimensionVertical()
        )
        FreeCADGui.addCommand("BIM_Text", BimWrappedTools.BIM_Text())
        FreeCADGui.addCommand("BIM_Shape2DView", BimWrappedTools.BIM_Shape2DView())
        FreeCADGui.addCommand("BIM_Project", BimWrappedTools.BIM_Project())

        self.draftingtools = [
            "BIM_Sketch",
            "Draft_Line",
            "Draft_Wire",
            "Draft_Circle",
            "Draft_Arc",
            "Draft_Arc_3Points",
            "Draft_Ellipse",
            "Draft_Polygon",
            "Draft_Rectangle",
            "Draft_BSpline",
            "Draft_BezCurve",
            "Draft_Point",
        ]

        self.annotationtools = [
            "BIM_ImagePlane",
            "BIM_Text",
            "Draft_ShapeString",
            "BIM_DimensionAligned",
            "BIM_DimensionHorizontal",
            "BIM_DimensionVertical",
            "BIM_Leader",
            "Draft_Label",
            "Arch_Axis",
            "Arch_AxisSystem",
            "Arch_Grid",
            "Arch_SectionPlane",
            "BIM_TDPage",
            "BIM_TDArchView",
            "BIM_Shape2DView",
        ]

        self.bimtools = [
            "BIM_Project",
            "Arch_Site",
            "Arch_Building",
            "Arch_Floor",
            "Arch_Space",
            "Separator",
            "Arch_Wall",
            "BIM_Column",
            "BIM_Beam",
            "BIM_Slab",
            "Arch_Rebar",
            "BIM_Door",
            "Arch_Window",
            "Arch_Pipe",
            "Arch_PipeConnector",
            "Arch_Stairs",
            "Arch_Roof",
            "Arch_Panel",
            "Arch_Frame",
            "Separator",
            "BIM_Box",
            "BIM_Builder",
            "Draft_Facebinder",
            "BIM_Library",
            "Arch_Component",
        ]

        self.modify = [
            "Draft_Move",
            "BIM_Copy",
            "Draft_Rotate",
            "BIM_Clone",
            "BIM_Unclone",
            "Draft_Offset",
            "BIM_Offset2D",
            "Draft_Trimex",
            "Draft_Join",
            "Draft_Split",
            "Draft_Scale",
            "Draft_Stretch",
            "Draft_Edit",
            "BIM_Rewire",
            "BIM_Glue",
            "Draft_Upgrade",
            "Draft_Downgrade",
            "Draft_Draft2Sketch",
            "Arch_CutPlane",
            "Arch_Add",
            "Arch_Remove",
            "BIM_Reextrude",
            "Draft_OrthoArray",
            "Draft_PathArray",
            "Draft_PointArray",
            "Draft_Mirror",
            "BIM_Extrude",
            "BIM_Cut",
            "BIM_Fuse",
            "BIM_Common",
            "BIM_Compound",
            "BIM_SimpleCopy",
        ]

        self.snap = [
            "Draft_ToggleGrid",
            "Draft_Snap_Lock",
            "Draft_Snap_Midpoint",
            "Draft_Snap_Perpendicular",
            "Draft_Snap_Grid",
            "Draft_Snap_Intersection",
            "Draft_Snap_Parallel",
            "Draft_Snap_Endpoint",
            "Draft_Snap_Angle",
            "Draft_Snap_Center",
            "Draft_Snap_Extension",
            "Draft_Snap_Near",
            "Draft_Snap_Ortho",
            "Draft_Snap_Special",
            "Draft_Snap_Dimensions",
            "Draft_Snap_WorkingPlane",
            "BIM_SetWPTop",
            "BIM_SetWPFront",
            "BIM_SetWPSide",
        ]

        self.manage = [
            "BIM_Setup",
            "BIM_Views",
            "BIM_ProjectManager",
            "BIM_Windows",
            "BIM_IfcElements",
            "BIM_IfcQuantities",
            "BIM_IfcProperties",
            "BIM_Classification",
            "BIM_Layers",
            "BIM_Material",
            "Arch_Schedule",
            "BIM_Preflight",
        ]

        # experimental arch tools (for 0.19 only)
        try:
            from ArchIFC import IfcProduct
        except:
            # this is 0.18
            self.experimentaltools = None
        else:
            from archguitools import gui_wall
            from archguitools import gui_openings
            from archguitools import gui_joinwalls
            from archguitools import gui_archview

            self.experimentaltools = [
                "Arch_Wall2",
                "Arch_JoinWalls",
                "Arch_ExtendWall",
                "Separator",
                "Arch_Opening",
                "Arch_Door2",
                "Arch_Window2",
                "Separator",
                "Arch_View",
            ]

        # fixed command names
        if "Draft_WorkingPlaneProxy" in Gui.listCommands():
            _tool = "Draft_WorkingPlaneProxy"
        else:
            _tool = "Draft_SetWorkingPlaneProxy"

        self.utils = [
            "BIM_TogglePanels",
            "BIM_Trash",
            "BIM_WPView",
            "Draft_SelectGroup",
            "Draft_Slope",
            _tool,
            "Draft_AddConstruction",
            "Arch_SplitMesh",
            "Arch_MeshToShape",
            "Arch_SelectNonSolidMeshes",
            "Arch_RemoveShape",
            "Arch_CloseHoles",
            "Arch_MergeWalls",
            "Arch_Check",
            "Arch_ToggleIfcBrepFlag",
            "Arch_ToggleSubs",
            "Arch_Survey",
            "BIM_Diff",
            "BIM_IfcExplorer",
        ]

        nudge = [
            "BIM_Nudge_Switch",
            "BIM_Nudge_Up",
            "BIM_Nudge_Down",
            "BIM_Nudge_Left",
            "BIM_Nudge_Right",
            "BIM_Nudge_RotateLeft",
            "BIM_Nudge_RotateRight",
            "BIM_Nudge_Extend",
            "BIM_Nudge_Shrink",
        ]

        # post-0.18 tools

        if "Arch_Reference" in Gui.listCommands():
            self.bimtools.insert(-5, "Arch_Reference")
        if "Arch_Fence" in Gui.listCommands():
            self.bimtools.insert(-7, "Arch_Fence")
        if "Draft_Arc_3Points" in Gui.listCommands():
            self.draftingtools.insert(5, "Draft_Arc_3Points")
        if "Draft_CubicBezCurve" in Gui.listCommands():
            self.draftingtools.insert(
                len(self.draftingtools) - 2, "Draft_CubicBezCurve"
            )
        if "Draft_AnnotationStyleEditor" in Gui.listCommands():
            self.manage.insert(4, "Draft_AnnotationStyleEditor")
        if "Arch_Truss" in Gui.listCommands():
            self.bimtools.insert(self.bimtools.index("Arch_Frame") + 1, "Arch_Truss")
        if "Arch_CurtainWall" in Gui.listCommands():
            self.bimtools.insert(
                self.bimtools.index("Arch_Wall") + 1, "Arch_CurtainWall"
            )
        if "Arch_Profile" in Gui.listCommands():
            self.bimtools.insert(self.bimtools.index("BIM_Box"), "Arch_Profile")
        if "Draft_Hatch" in Gui.listCommands():
            self.draftingtools.append("Draft_Hatch")

        # load rebar tools (Reinforcement addon)

        try:
            import RebarTools
        except ImportError:
            self.rebar = None
        else:
            # create popup group for Rebar tools
            class RebarGroupCommand:
                def GetCommands(self):
                    return tuple(["Arch_Rebar"] + RebarTools.RebarCommands)

                def GetResources(self):
                    return {
                        "MenuText": QT_TRANSLATE_NOOP(
                            "Arch_RebarTools", "Reinforcement tools"
                        ),
                        "ToolTip": QT_TRANSLATE_NOOP(
                            "Arch_RebarTools", "Reinforcement tools"
                        ),
                    }

                def IsActive(self):
                    return not FreeCAD.ActiveDocument is None

            FreeCADGui.addCommand("Arch_RebarTools", RebarGroupCommand())
            self.bimtools[self.bimtools.index("Arch_Rebar")] = "Arch_RebarTools"
            Log("Load Reinforcement Module...done\n")
            if hasattr(RebarTools, "updateLocale"):
                RebarTools.updateLocale()
            # self.appendMenu(QT_TRANSLATE_NOOP("Arch_RebarTools","Reinforcement tools"),RebarTools.RebarCommands + ["Arch_Rebar"])
            self.rebar = RebarTools.RebarCommands + ["Arch_Rebar"]

        # try to load bimbots

        try:
            import bimbots
        except ImportError:
            pass
        else:

            class BIMBots:
                def GetResources(self):
                    return bimbots.get_plugin_info()

                def Activated(self):
                    bimbots.launch_ui()

            FreeCADGui.addCommand("BIMBots", BIMBots())
            self.utils.append("BIMBots")

        # load Reporting

        try:
            import report
        except ImportError:
            pass
        else:
            if "Report_Create" in Gui.listCommands():
                self.manage[self.manage.index("Arch_Schedule")] = "Report_Create"

        # load webtools

        try:
            import BIMServer, Git, Sketchfab
        except ImportError:
            pass
        else:
            self.utils.extend(
                ["WebTools_Git", "WebTools_BimServer", "WebTools_Sketchfab"]
            )

        # load flamingo

        try:
            import CommandsPolar, CommandsFrame, CommandsPipe
        except ImportError:
            flamingo = None
        else:
            flamingo = [
                "frameIt",
                "fillFrame",
                "insertPath",
                "insertSection",
                "FrameLineManager",
                "spinSect",
                "reverseBeam",
                "shiftBeam",
                "pivotBeam",
                "levelBeam",
                "alignEdge",
                "rotJoin",
                "alignFlange",
                "stretchBeam",
                "extend",
                "adjustFrameAngle",
                "insertPipe",
                "insertElbow",
                "insertReduct",
                "insertCap",
                "insertFlange",
                "insertUbolt",
                "insertPypeLine",
                "breakPipe",
                "mateEdges",
                "extend2intersection",
                "extend1intersection",
                "laydown",
                "raiseup",
            ]

        # load fasteners

        try:
            import FastenerBase, FastenersCmd
        except ImportError:
            fasteners = None
        else:
            fasteners = [
                c
                for c in FastenerBase.FSGetCommands("screws")
                if not isinstance(c, tuple)
            ]

        # load Native IFC tools

        try:
            import ifc_commands
        except ImportError:
            ifctools = None
        else:
            ifctools = ifc_commands.get_commands()


        # create toolbars

        self.appendToolbar(
            QT_TRANSLATE_NOOP("Workbench", "Drafting tools"), self.draftingtools
        )
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "3D/BIM tools"), self.bimtools)
        self.appendToolbar(
            QT_TRANSLATE_NOOP("Workbench", "Annotation tools"), self.annotationtools
        )
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Modification tools"), self.modify)
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Manage tools"), self.manage)
        if self.experimentaltools:
            self.appendToolbar(
                QT_TRANSLATE_NOOP("Workbench", "Experimental tools"), self.experimentaltools
            )
        # if flamingo:
        #    self.appendToolbar("Flamingo tools",flamingo)

        # create menus

        # ugly!
        # build a new list of bimtools only for menu
        # and put rebar menu with sub menus into it
        self.bimtools_menu = list(self.bimtools)
        if "Arch_RebarTools" in self.bimtools_menu:
            self.bimtools_menu.remove("Arch_RebarTools")

        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&2D Drafting"), self.draftingtools)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&3D/BIM"), self.bimtools_menu)
        if self.rebar:
            self.appendMenu(
                [
                    QT_TRANSLATE_NOOP("Workbench", "&3D/BIM"),
                    QT_TRANSLATE_NOOP("Workbench", "Reinforcement tools"),
                ],
                self.rebar,
            )
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&Annotation"), self.annotationtools)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&Snapping"), self.snap)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&Modify"), self.modify)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&Manage"), self.manage)
        if ifctools:
            self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&IFC"), ifctools)
        if flamingo:
            self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&Flamingo"), flamingo)
        if fasteners:
            self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&Fasteners"), fasteners)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "&Utils"), self.utils)
        self.appendMenu(
            [QT_TRANSLATE_NOOP("Workbench", "&Utils"), QT_TRANSLATE_NOOP("Workbench", "Nudge")], nudge
        )
        self.appendMenu("&Help", ["BIM_Welcome", "BIM_Help", "BIM_Tutorial", "BIM_Examples"])

        # load Arch & Draft preference pages

        if hasattr(FreeCADGui, "draftToolBar"):
            if not hasattr(FreeCADGui.draftToolBar, "loadedArchPreferences"):
                import Arch_rc

                FreeCADGui.addPreferencePage(":/ui/preferences-arch.ui", "Arch")
                FreeCADGui.addPreferencePage(":/ui/preferences-archdefaults.ui", "Arch")
                FreeCADGui.draftToolBar.loadedArchPreferences = True
            if not hasattr(FreeCADGui.draftToolBar, "loadedPreferences"):
                import Draft_rc

                try:
                    from draftutils import params
                except ImportError:
                    pass
                else:
                    params._param_observer_start()

                FreeCADGui.addPreferencePage(":/ui/preferences-draft.ui", "Draft")
                FreeCADGui.addPreferencePage(":/ui/preferences-draftsnap.ui", "Draft")
                FreeCADGui.addPreferencePage(":/ui/preferences-draftvisual.ui", "Draft")
                FreeCADGui.addPreferencePage(":/ui/preferences-drafttexts.ui", "Draft")
                FreeCADGui.draftToolBar.loadedPreferences = True

        Log("Loading BIM module... done\n")
        FreeCADGui.updateLocale()

    def setupMultipleObjectSelection(self):
        import BimSelect

        if hasattr(FreeCADGui, "addDocumentObserver") and not hasattr(
            self, "BimSelectObserver"
        ):
            self.BimSelectObserver = BimSelect.Setup()
            FreeCADGui.addDocumentObserver(self.BimSelectObserver)

    def Activated(self):
        if hasattr(FreeCADGui, "draftToolBar"):
            FreeCADGui.draftToolBar.Activated()
        if hasattr(FreeCADGui, "Snapper"):
            FreeCADGui.Snapper.show()
        import WorkingPlane
        if hasattr(WorkingPlane, "_view_observer_start"):
            WorkingPlane._view_observer_start()

        from DraftGui import todo
        import BimStatusBar

        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").GetBool(
            "FirstTime", True
        ) and (not hasattr(FreeCAD, "TestEnvironment")):
            todo.delay(FreeCADGui.runCommand, "BIM_Welcome")
        todo.delay(BimStatusBar.setStatusIcons, True)

        FreeCADGui.Control.clearTaskWatcher()

        class BimWatcher:
            def __init__(self, cmds, name, invert=False):
                self.commands = cmds
                self.title = name
                self.invert = invert

            def shouldShow(self):
                if self.invert:
                    return (FreeCAD.ActiveDocument != None) and (
                        FreeCADGui.Selection.getSelection() != []
                    )
                else:
                    return (FreeCAD.ActiveDocument != None) and (
                        not FreeCADGui.Selection.getSelection()
                    )

        FreeCADGui.Control.addTaskWatcher(
            [
                BimWatcher(self.draftingtools + self.annotationtools, "2D geometry"),
                BimWatcher(self.bimtools, "3D/BIM geometry"),
                BimWatcher(self.modify, "Modify", invert=True),
            ]
        )

        # restore views widget if needed

        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").GetBool(
            "RestoreBimViews", True
        ):
            import BimViews

            w = BimViews.findWidget()
            if not w:
                FreeCADGui.runCommand("BIM_Views")
            else:
                w.show()
                w.toggleViewAction().setVisible(True)

        self.setupMultipleObjectSelection()

        Log("BIM workbench activated\n")

    def Deactivated(self):
        if hasattr(self, "BimSelectObserver"):
            FreeCADGui.removeDocumentObserver(self.BimSelectObserver)
            del self.BimSelectObserver

        if hasattr(FreeCADGui, "draftToolBar"):
            FreeCADGui.draftToolBar.Deactivated()
        if hasattr(FreeCADGui, "Snapper"):
            FreeCADGui.Snapper.hide()
        import WorkingPlane
        if hasattr(WorkingPlane, "_view_observer_stop"):
            WorkingPlane._view_observer_stop()

        from DraftGui import todo
        import BimStatusBar
        import BimViews

        # print("Deactivating status icon")

        todo.delay(BimStatusBar.setStatusIcons, False)

        FreeCADGui.Control.clearTaskWatcher()

        # store views widget state and vertical size

        w = BimViews.findWidget()
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").SetBool(
            "RestoreBimViews", bool(w)
        )
        if w:
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/BIM").SetInt(
                "BimViewsSize", w.height()
            )
            w.hide()
            w.toggleViewAction().setVisible(False)

        Log("BIM workbench deactivated\n")

    def ContextMenu(self, recipient):
        translate = FreeCAD.Qt.translate

        import DraftTools

        if recipient == "Tree":
            groups = False
            ungroupable = False
            for o in FreeCADGui.Selection.getSelection():
                if o.isDerivedFrom("App::DocumentObjectGroup") or o.hasExtension(
                    "App::GroupExtension"
                ):
                    groups = True
                else:
                    groups = False
                    break
            for o in FreeCADGui.Selection.getSelection():
                for parent in o.InList:
                    if parent.isDerivedFrom(
                        "App::DocumentObjectGroup"
                    ) or parent.hasExtension("App::GroupExtension"):
                        if o in parent.Group:
                            ungroupable = True
                        else:
                            ungroupable = False
                            break
            if groups:
                self.appendContextMenu("", ["Draft_SelectGroup"])
            if ungroupable:
                self.appendContextMenu("", ["BIM_Ungroup"])
            if (len(FreeCADGui.Selection.getSelection()) == 1) and (
                FreeCADGui.Selection.getSelection()[0].Name == "Trash"
            ):
                self.appendContextMenu("", ["BIM_EmptyTrash"])
        elif recipient == "View":
            self.appendContextMenu(translate("BIM", "Snapping"), self.snap)
        if FreeCADGui.Selection.getSelection():
            if FreeCADGui.Selection.getSelection()[0].Name != "Trash":
                self.appendContextMenu("", ["BIM_Trash"])
            self.appendContextMenu("", ["Draft_AddConstruction", "Draft_AddToGroup"])
            allclones = False
            for obj in FreeCADGui.Selection.getSelection():
                if hasattr(obj, "CloneOf") and obj.CloneOf:
                    allclones = True
                else:
                    allclones = False
                    break
            if allclones:
                self.appendContextMenu("", ["BIM_ResetCloneColors"])
            if len(FreeCADGui.Selection.getSelection()) == 1:
                obj = FreeCADGui.Selection.getSelection()[0]
                if hasattr(obj, "Group"):
                    if obj.getTypeIdOfProperty("Group") == "App::PropertyLinkList":
                        self.appendContextMenu("", ["BIM_Reorder"])
                if obj.isDerivedFrom("TechDraw::DrawView"):
                    self.appendContextMenu("", ["BIM_MoveView"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(BIMWorkbench)
