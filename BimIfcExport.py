# ***************************************************************************
# *   Copyright (c) 2022 Yorik van Havre <yorik@uncreated.net>              *
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

"""FreeCAD BIM IFC exporter"""


import os
import time
import tempfile
import math

import FreeCAD
import exportIFCHelper
import Draft
import Arch


IFCTEMPLATE = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
FILE_NAME('$filename','$timestamp',('$owner','$email'),('$company'),'$soft','$soft','');
FILE_SCHEMA(('$ifcschema'));
ENDSEC;
DATA;
#1=IFCPERSON($,$,'$owner',$,$,$,$,$);
#2=IFCORGANIZATION($,'$company',$,$,$);
#3=IFCPERSONANDORGANIZATION(#1,#2,$);
#4=IFCAPPLICATION(#2,'$version','FreeCAD','118df2cf_ed21_438e_a41');
#5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$now,#3,#4,$now);
#6=IFCDIRECTION((1.,0.,0.));
#7=IFCDIRECTION((0.,0.,1.));
#8=IFCCARTESIANPOINT((0.,0.,0.));
#9=IFCAXIS2PLACEMENT3D(#8,#7,#6);
#10=IFCDIRECTION((0.,1.,0.));
#12=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
#13=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
#14=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
#15=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
#16=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
#17=IFCMEASUREWITHUNIT(IFCPLANEANGLEMEASURE(0.017453292519943295),#16);
#18=IFCCONVERSIONBASEDUNIT(#12,.PLANEANGLEUNIT.,'DEGREE',#17);
ENDSEC;
END-ISO-10303-21;
"""


# temp constants (to be turned into FreeCAD parameters later)
SCHEMA = "IFC4"
FULL_PARAMETRIC = False


def export(exportList, filename):
    """Exports the given list of objects to the given filename"""

    import ifcopenshell

    ifcfile = buildTemplate(FreeCAD.ActiveDocument, filename)
    objectslist, annotations = buildExportLists(exportList)
    history, context, objectslist = setupProject(ifcfile, objectslist)

    # run the recycler on the existing file
    ifcbin = exportIFCHelper.recycler(ifcfile)  # TODO replace with own

    for obj in objectslist:
        writeObject(obj, ifcbin)
        writeProperties(obj, ifcbin)
    ifcfile.write(filename)


def buildTemplate(doc, filename):
    """builds a template IFC file for the given document"""

    if doc.getObject("IfcFileData"):
        ifcfile = getIfcDocument(doc.getObject("IfcFileData").Text)
    elif "IfcFileLink" in doc.Meta:
        filedata = doc.Meta["IfcFileLink"].split(";;")
        filename = filedata[0].replace("file://", "")
        filehash = filedata[1].replace("hash:", "")
        if os.path.exists(filename):
            ifcfile = ifcopenshell.open(filename)
        else:
            raise Exception("IFC file does not exist")
    else:
        version = FreeCAD.Version()
        version = version[0] + "." + version[1] + " build " + version[2]
        owner = FreeCAD.ActiveDocument.CreatedBy
        email = ""
        if ("@" in owner) and ("<" in owner):
            s = owner.split("<")
            owner = s[0].strip()
            email = s[1].strip(">")
        soft = "IfcOpenShell"

        if hasattr(ifcopenshell, "version"):
            soft = soft + ifcopenshell.version
        timestamp = str(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))
        tpl = IFCTEMPLATE.replace("$version", version)
        tpl = tpl.replace("$ifcschema", SCHEMA)
        tpl = tpl.replace("$owner", owner)
        tpl = tpl.replace("$company", FreeCAD.ActiveDocument.Company)
        tpl = tpl.replace("$email", email)
        tpl = tpl.replace("$now", str(int(time.time())))
        tpl = tpl.replace("$filename", os.path.basename(filename))
        tpl = tpl.replace("$timestamp", timestamp)
        tpl = tpl.replace("$soft", soft)
        ifcfile = getIfcDocument(tpl)
    setUnits(ifcfile)
    return ifcfile


def getIfcDocument(text):
    """returns an IFC file object from IFC text"""

    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, "w") as f:
        f.write(text)
    ifcfile = ifcopenshell.open(tmp.name)
    return ifcfile


def setDeclinations(objectslist, cc):
    """sets the north declination in the IFC file"""

    sites = Draft.getObjectsOfType(objectslist, "Site")
    if sites:
        decl = sites[0].Declination.getValueAs(FreeCAD.Units.Radian)
        ratios = (math.cos(decl + math.pi / 2), math.sin(decl + math.pi / 2))
        cc.model_context.TrueNorth.DirectionRatios = ratios


def setupProject(objectslist, ifcfile):
    """sets up project"""

    history = ifcfile.by_type("IfcOwnerHistory")[0]
    cc = exportIFCHelper.ContextCreator(ifcfile, objectslist)
    context = contextCreator.model_view_subcontext
    project = contextCreator.project
    objectslist = [obj for obj in objectslist if obj != cc.project_object]
    setDeclination(objectslist, cc)
    return history, context, objectslist
    # include project?


def getIfcDocument(text):
    """returns an IFC file object from IFC text"""

    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, "w") as f:
        f.write(text)
    ifcfile = ifcopenshell.open(tmp.name)
    return ifcfile


def setUnits(ifcfile):
    """sets the units of the IFC file (meters or feet)"""

    p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch")
    u = p.GetInt("ifcUnit", 0)
    if u == 1:
        unit = "foot"
    else:
        unit = "metre"
    exportIFCHelper.writeUnits(ifcfile, unit)  # TODO replace with own


def buildExportLists(exportList):
    """builds a complete list of objects to export"""

    texttypes = [
        "DraftText",
        "Text",
        "Dimension",
        "LinearDimension",
        "AngularDimension",
    ]
    exlist = [
        "Dimension",
        "Material",
        "MaterialContainer",
        "WorkingPlaneProxy",
        "Project",
    ]
    objectslist = Draft.get_group_contents(exportList, walls=True, addgroups=True)
    annotations = []
    for obj in objectslist:
        if obj.isDerivedFrom("Part::Part2DObject"):
            annotations.append(obj)
        elif obj.isDerivedFrom("App::Annotation"):
            annotations.append(obj)
        elif Draft.getType(obj) in texttypes:
            annotations.append(obj)
        elif obj.isDerivedFrom("Part::Feature"):
            if obj.Shape and (not obj.Shape.Solids) and obj.Shape.Edges:
                if not obj.Shape.Faces:
                    annotations.append(obj)
                elif obj.Shape.BoundBox.XLength < 0.0001:
                    annotations.append(obj)
                elif obj.Shape.BoundBox.YLength < 0.0001:
                    annotations.append(obj)
                elif obj.Shape.BoundBox.ZLength < 0.0001:
                    annotations.append(obj)
    objectslist = [obj for obj in objectslist if obj not in annotations]
    objectslist = Arch.pruneIncluded(objectslist, strict=True)
    objectslist = [obj for obj in objectslist if Draft.getType(obj) not in exlist]
    if FULL_PARAMETRIC:
        objectslist = Arch.getAllChildren(objectslist)
    return objectslist, annotations


def writeObject(obj, ifcbin):
    """writes a FreeCAD object to the given IFC file"""

    # to integrate
    if preferences["EXPORT_MODEL"] in ["struct", "hybrid"]:
        structobj = exportIFCStructuralTools.createStructuralMember(
            ifcfile, ifcbin, obj
        )
        if preferences["EXPORT_MODEL"] == "struct":
            return

    # if unmodified, do nothing

    # if modified, locate the old one

    # if no old one, write from scratch

    # generic data
    name = obj.Label
    description = getattr(obj, "Description", "")
    uid = getUID(obj, ifcbin)
    ifctype = getIfcType(obj)


def writeProperties(obj, ifcfile):
    """writes the properties of a FreeCAD object to the given IFC file"""

    return


def getUID(obj, ifcbin):
    """gets or creates an UUID for an object"""

    uid = None
    if hasattr(obj, " IfcData"):
        if "IfcUID" in obj.IfcData.keys():
            uid = str(obj.IfcData["IfcUID"])
            if uid in ifcbin.uids:  # get UIDs
                uid = None
    if not uid:
        uid = ifcopenshell.guid.new()
        if hasattr(obj, "IfcData"):
            d = obj.IfcData
            d["IfcUID"] = uid
            obj.IfcData = d
        if hasattr(obj, "GlobalId"):
            obj.GlobalId = uid
    return uid


def getIfcType(obj):
    """Returns an IFC type for an object"""

    dtype = Draft.getType(obj)
    if (dtype == "BuildingPart") and getattr(
        obj, "IfcType", "Undefined"
    ) != "Undefined":
        ifctype = "IfcBuildingStorey"
    elif hasattr(obj, "IfcType"):
        ifctype = obj.IfcType.replace(" ", "")
    elif dtype in ["App::Part", "Part::Compound"]:
        ifctype = "IfcElementAssembly"
    elif dtype in ["App::DocumentObjectGroup"]:
        ifctype = "IfcGroup"
    else:
        ifctype = "IfcBuildingElementProxy"
    return ifctype
