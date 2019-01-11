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

import os,FreeCAD,FreeCADGui,Draft,Arch,Part
from PySide import QtCore,QtGui

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator

tests = ["testAll",
         "testIFC4",
         "testHierarchy",
         "testSites",
         "testBuildings",
         "testStoreys",
         "testUndefined",
         "testSolid",
         "testQuantities",
         "testCommonPsets",
         "testPsets",
         "testMaterials",
         "testStandards",
         "testExtrusions",
         "testStandardCases",
         "testTinyLines",
        ]

class BIM_Preflight:


    def GetResources(self):

        return {'Pixmap'  : os.path.join(os.path.dirname(__file__),"icons","BIM_Preflight.svg"),
                'MenuText': QT_TRANSLATE_NOOP("BIM_Preflight", "Preflight checks..."),
                'ToolTip' : QT_TRANSLATE_NOOP("BIM_Preflight", "Checks several characteristics of this model before exporting to IFC")}

    def Activated(self):
        FreeCADGui.Control.showDialog(BIM_Preflight_TaskPanel())



class BIM_Preflight_TaskPanel:


    def __init__(self):

        self.results = {} # to store the result message
        self.culprits = {} # to store objects to highlight
        self.rform = None # to store the results dialog
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogPreflight.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icons","BIM_Preflight.svg")))
        for test in tests:
            getattr(self.form,test).setIcon(QtGui.QIcon(":/icons/button_right.svg"))
            getattr(self.form,test).setToolTip("Press to perform the test")
            if hasattr(self,test):
                getattr(self.form,test).clicked.connect(getattr(self,test))
            self.results[test] = None
            self.culprits[test] = None
        
    def getStandardButtons(self):

        return int(QtGui.QDialogButtonBox.Close)

    def reject(self):

        FreeCADGui.Control.closeDialog()
        FreeCAD.ActiveDocument.recompute()
    
    def passed(self,test):
        
        "sets the button as passed"
        
        getattr(self.form,test).setIcon(QtGui.QIcon(":/icons/button_valid.svg"))
        getattr(self.form,test).setText("Passed")
        getattr(self.form,test).setToolTip("This test has succeeded.")
        
    def failed(self,test):
        
        "sets the button as failed"

        getattr(self.form,test).setIcon(QtGui.QIcon(":/icons/process-stop.svg"))
        getattr(self.form,test).setText("Failed")
        getattr(self.form,test).setToolTip("This test has failed. Press the button to know more")
        
    def reset(self,test):
        
        "reset the button"
        
        getattr(self.form,test).setIcon(QtGui.QIcon(":/icons/button_right.svg"))
        getattr(self.form,test).setText("Test")
        getattr(self.form,test).setToolTip("Press to perform the test")

    def show(self,test):
        
        "shows test results"
        
        if self.results[test]:
            if self.culprits[test]:
                FreeCADGui.Selection.clearSelection()
                for c in self.culprits[test]:
                    FreeCADGui.Selection.addSelection(c)
            if not self.rform:
                self.rform = FreeCADGui.PySideUic.loadUi(os.path.join(os.path.dirname(__file__),"dialogPreflightResults.ui"))
                # center the dialog over FreeCAD window
                mw = FreeCADGui.getMainWindow()
                self.rform.move(mw.frameGeometry().topLeft() + mw.rect().center() - self.rform.rect().center())
                self.rform.buttonReport.clicked.connect(self.toReport)
                self.rform.buttonOK.clicked.connect(self.closeReport)
            self.rform.textBrowser.setText(self.results[test])
            self.rform.label.setText("Results of "+test+":")
            self.rform.test = test
            self.rform.show()
    
    def toReport(self):
        
        "copies the resulting text to the report view"
        
        if self.rform and hasattr(self.rform,"test") and self.rform.test:
            if self.results[self.rform.test]:
                FreeCAD.Console.PrintMessage(self.results[self.rform.test]+"\n")

    def closeReport(self):
        
        if self.rform:
            self.rform.test = None
            self.rform.hide()

    def getObjects(self):
        
        "selects target objects"
        
        objs = []
        if self.form.getAll.isChecked():
            objs = FreeCAD.ActiveDocument.Objects
        elif self.form.getVisible.isChecked():
            objs = [o for o in FreeCAD.ActiveDocument.Objects if o.ViewObject.Visibility == True]
        else:
            objs = FreeCADGui.Selection.getSelection()
        # clean objects list of unwanted types
        objs = Draft.getGroupContents(objs,walls=True,addgroups=True)
        objs = [obj for obj in objs if not obj.isDerivedFrom("Part::Part2DObject")]
        objs = [obj for obj in objs if not obj.isDerivedFrom("App::Annotation")]
        objs = [obj for obj in objs if (hasattr(obj,"Shape") and obj.Shape and not (obj.Shape.Edges and (not obj.Shape.Faces)))]
        objs = Arch.pruneIncluded(objs)
        objs = [obj for obj in objs if not obj.isDerivedFrom("App::DocumentObjectGroup")]
        objs = [obj for obj in objs if Draft.getType(obj) not in ["DraftText","Material","MaterialContainer","WorkingPlaneProxy"]]
        return objs

    def testAll(self):
        
        "runs all tests"
        
        for test in tests:
            if test != "testAll":
                self.reset(test)
                if hasattr(self,test):
                    getattr(self,test)()

    def testIFC4(self):
        
        "tests for IFC4 support"
        
        test = "testIFC4"
        if getattr(self.form,test).text() == "Failed":
            self.show(test)
        else:
            self.reset(test)
            self.results[test] = None
            self.culprits[test] = None
            msg = None
            try:
                import ifcopenshell
            except:
                msg = "ifcopenshell is not installed on your system or not available to FreeCAD. "
                msg += "This library is responsible for IFC support in FreeCAD, and therefore IFC support is currently disabled. "
                msg += "Check https://www.freecadweb.org/wiki/Extra_python_modules#IfcOpenShell to obtain more information. "
                self.failed(test)
            else:
                if ifcopenshell.schema_identifier.startswith("IFC4"):
                    self.passed(test)
                else:
                    msg = "The version of ifcopenshell installed on your system will produce files with this schema version:\n\n"
                    msg += ifcopenshell.schema_identifier + "\n\n"
                    msg += "IFC export in FreeCAD is performed by an open-source third-party library called IfcOpenShell. " 
                    msg += "To be able to export to the newer IFC4 standard, IfcOpenShell must have been compiled with IFC4 "
                    msg += "support enabled. This test checks if IFC4 support is available in your version of IfcOpenShell. "
                    msg += "If not, you will only be able to export IFC files in the older IFC2x3 standard. Note that some "
                    msg += "applications out there still have incomplete or inexistant IFC4 support, so in some cases "
                    msg += "IFC2x3 might still work better."
                    self.failed(test)
            self.results[test] = msg

    def testHierarchy(self):
        
        "tests for project hierarchy support"
        
        test = "testHierarchy"
        if getattr(self.form,test).text() == "Failed":
            self.show(test)
        else:
            self.reset(test)
            self.results[test] = None
            self.culprits[test] = []
            msg = None
            sites = False
            buildings = False
            storeys = False
            for obj in self.getObjects():
                if (Draft.getType(obj) == "Site") or (hasattr(obj,"IfcRole") and (obj.IfcRole == "Site")):
                    sites = True
                elif (Draft.getType(obj) == "Building") or (hasattr(obj,"IfcRole") and (obj.IfcRole == "Building")):
                    buildings = True
                elif (hasattr(obj,"IfcRole") and (obj.IfcRole == "Building Storey")):
                    storeys = True
            if (not sites) or (not buildings)  or (not storeys):
                msg = "The IFC standard requires at least one site, one building and one level or building storey per project. "
                msg += "The following types were not found in the project: "
                if not sites:
                    msg += "Site, "
                if not buildings:
                    msg += "Building, "
                if not storeys:
                    msg += "Building Storeys, "
                msg += "\n\nNote that, as this is a mandatory requirement, FreeCAD will automatically add a default site, "
                msg += "a default building and/or a default building storey if any of these is missing. So even if this "
                msg += "test didn't pass, your exported IFC file will meet the requirements. However, it is always better "
                msg += "to create these objects yourself, as you get more control over naming and properties."
            if msg:
                self.failed(test)
            else:
                self.passed(test)
            self.results[test] = msg

    def testSites(self):
        
        "tests for Sites support"
        
        test = "testSites"
        if getattr(self.form,test).text() == "Failed":
            self.show(test)
        else:
            self.reset(test)
            self.results[test] = None
            self.culprits[test] = []
            msg = None
            for obj in self.getObjects():
                if (Draft.getType(obj) == "Building") or (hasattr(obj,"IfcRole") and (obj.IfcRole == "Building")):
                    ok = False
                    for parent in obj.InList:
                        if (Draft.getType(parent) == "Site") or (hasattr(parent,"IfcRole") and (parent.IfcRole == "Site")):
                            if hasattr(parent,"Group") and parent.Group:
                                if obj in parent.Group:
                                    ok = True
                                    break
                    if not ok:
                        self.culprits[test].append(obj)
                        if not msg:
                            msg = "The following Building objects have been found to not be included in any Site. "
                            msg += "You can resolve the situation by creating a Site object, if none is present "
                            msg += "in your model, and drag and drop the Building objects into it in the tree view:\n\n"
                        msg += obj.Label +"\n"
            if msg:
                self.failed(test)
            else:
                self.passed(test)
            self.results[test] = msg

    def testBuildings(self):
        
        "tests for Buildings support"
        
        test = "testBuildings"
        if getattr(self.form,test).text() == "Failed":
            self.show(test)
        else:
            self.reset(test)
            self.results[test] = None
            self.culprits[test] = []
            msg = None
            for obj in self.getObjects():
                if hasattr(obj,"IfcRole") and (obj.IfcRole == "Building Storey"):
                    ok = False
                    for parent in obj.InList:
                        if hasattr(parent,"IfcRole") and (parent.IfcRole == "Building"):
                            if hasattr(parent,"Group") and parent.Group:
                                if obj in parent.Group:
                                    ok = True
                                    break
                    if not ok:
                        self.culprits[test].append(obj)
                        if not msg:
                            msg = "The following Building Storey (BuildingParts with their IFC role set as \"Building Storey\")" 
                            msg += "objects have been found to not be included in any Building. "
                            msg += "You can resolve the situation by creating a Building object, if none is present "
                            msg += "in your model, and drag and drop the Building Storey objects into it in the tree view:\n\n"
                        msg += obj.Label +"\n"
            if msg:
                self.failed(test)
            else:
                self.passed(test)
            self.results[test] = msg

    def testStoreys(self):
        
        "tests for Building Storey support"
        
        test = "testStoreys"
        if getattr(self.form,test).text() == "Failed":
            self.show(test)
        else:
            self.reset(test)
            self.results[test] = None
            self.culprits[test] = []
            msg = None
            for obj in self.getObjects():
                if hasattr(obj,"IfcRole") and (not obj.IfcRole in ["Building","Building Storey","Site"]):
                    ok = False
                    for parent in obj.InListRecursive:
                        # just check if any of the ancestors is a Building Storey for now. Don't check any further...
                        if hasattr(parent,"IfcRole") and (parent.IfcRole == "Building Storey"):
                            ok = True
                            break
                    if not ok:
                        self.culprits[test].append(obj)
                        if not msg:
                            msg = "The following BIM objects have been found to not be included in any Building Storey "
                            msg += "(BuildingParts with their IFC role set as \"Building Storey\"). "
                            msg += "You can resolve the situation by creating a Building Storey object, if none is present "
                            msg += "in your model, and drag and drop the BIM objects into it in the tree view:\n\n"
                        msg += obj.Label +"\n"
            if msg:
                self.failed(test)
            else:
                self.passed(test)
            self.results[test] = msg


    def testUndefined(self):
        
        "tests for undefined BIM objects"
        
        test = "testUndefined"
        if getattr(self.form,test).text() == "Failed":
            self.show(test)
        else:
            self.reset(test)
            self.results[test] = None
            self.culprits[test] = []
            undefined = []
            notbim = []
            msg = None

            for obj in self.getObjects():
                if hasattr(obj,"IfcRole"):
                    if (obj.IfcRole == "Undefined"):
                        self.culprits[test].append(obj)
                        undefined.append(obj)
                else:
                    self.culprits[test].append(obj)
                    notbim.append(obj)
            if undefined or notbim:
                msg = "Some of the objects have no IFC type defined. They will therefore be exported as the generic "
                msg += "IfcBuildingElementProxy type. This is not a problem, and might even be what you want. In some "
                msg += "cases, this type is even recommended as it might prevent host applications to perform unwanted "
                msg += "transformations on the object. However, since IFC is all about semantics, it is often interesting "
                msg += "to give a defined type to all your objects.\n\n"
                if undefined:
                    msg += "The following BIM objects have the \"Undefined\" type:\n\n"
                    for o in undefined:
                        msg += o.Label + "\n"
                if notbim:
                    msg += "The following objects are not BIM objects:\n\n"
                    for o in notbim:
                        msg += o.Label + "\n"
                        msg += "You can turn these objects into BIM objects by using the Utils -> Make Component tool."
            if msg:
                self.failed(test)
            else:
                self.passed(test)
            self.results[test] = msg


    def testTinyLines(self):
        
        "tests for objects with tiny lines (< 0.8mm)"
        
        test = "testTinyLines"
        if getattr(self.form,test).text() == "Failed":
            self.show(test)
        else:
            self.reset(test)
            self.results[test] = None
            self.culprits[test] = []
            msg = None
            minl = 0.8 # min 0.8 millimeters
            edges = []
            objs = []

            for obj in self.getObjects():
                if obj.isDerivedFrom("Part::Feature"):
                        if obj.Shape:
                        for e in obj.Shape.Edges:
                            if e.Length <= minl:
                                edges.append(e)
                                if not obj in objs:
                                    objs.append(obj)
            if edges:
                result = FreeCAD.ActiveDocument.addObject("Part::Feature","TinyLinesResult")
                result.Shape = Part.makeCompound(edges)
                result.ViewObject.LineWidth = 5
                self.culprits[test] = [result]
                msg = "Some of the objects have lines smaller than 1/32 inch or 0.8mm, which is the smallest "
                msg += "line size that Revit accepts. These objects will be discarded when imported into Revit:\n\n"
                for obj in objs:
                    msg += obj.Label +"\n"
                msg += "\nAn additional object, called \"TinyLinesResult\" has been added to this model, and "
                msg += "selected. It contains all the tiny lines found, so you can inspect them and fix the "
                msg += "needed objects. Be sure to delete the TinyLinesResult object when you are done!\n\n"
                msg += "Tip: The results are best viewed in Wireframe mode (menu Views -> Draw Style -> Wireframe)"
            if msg:
                self.failed(test)
            else:
                self.passed(test)
            self.results[test] = msg


FreeCADGui.addCommand('BIM_Preflight',BIM_Preflight())

