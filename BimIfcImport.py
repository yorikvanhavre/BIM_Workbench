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

"""FreeCAD BIM IFC importer"""

import sys
import time
import os
import builtins
import hashlib

import FreeCAD
import Draft
import Arch
import importIFCHelper
from FreeCAD import Base
import ArchIFC

# to resolve later...
import importIFC

# temp constants (to be turned into FreeCAD parameters later)
IFCINCLUDE = "link"  # full, link or none
EXCLUDELIST = ["IfcOpeningElement"]  # temporary
PROPERTYMODE = "new"  # new = IFC properties become FreeCAD properties,
# old is 0.20, hybrid is: Pset* are old-style,
# others are new-style

# global dicts to store ifc object/freecad object relationships
layers = {}  # ifcid : Draft_Layer
materials = {}  # ifcid : Arch_Material
objects = {}  # ifcid : Arch_Component
subs = {}  # host_ifcid: [child_ifcid,...]
adds = {}  # host_ifcid: [child_ifcid,...]
colors = {}  # objname : (r,g,b)


def open(filename):
    "opens an IFC file in a new document"

    return insert(filename)


def insert(filename, docname=None):
    """imports the contents of an IFC file in the given document"""

    import ifcopenshell
    from ifcopenshell import geom

    # reset global values
    global layers
    global materials
    global objects
    global adds
    global subs
    layers = {}
    materials = {}
    objects = {}
    adds = {}
    subs = {}

    # BIM WB header (temporary)
    print("BIM Workbench IFC importer")
    print("==========================\n")

    # statistics
    starttime = time.time()  # in seconds
    filesize = os.path.getsize(filename) * 0.000001  # in megabytes
    print("Opening", filename + ",", round(filesize, 2), "Mb")

    # setup ifcopenshell
    params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Arch")
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_BREP_DATA, True)
    settings.set(settings.SEW_SHELLS, True)
    settings.set(settings.USE_WORLD_COORDS, True)
    # TODO: Treat openings
    # if preferences['SEPARATE_OPENINGS']:
    #    settings.set(settings.DISABLE_OPENING_SUBTRACTIONS,True)
    settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, False)
    # TODO: Treat layers
    # if preferences['SPLIT_LAYERS'] and hasattr(settings,"APPLY_LAYERSETS"):
    settings.set(settings.APPLY_LAYERSETS, True)

    # setup document
    if FreeCAD.ActiveDocument:
        doc = FreeCAD.ActiveDocument
    else:
        if not docname:
            docname = os.path.splitext(os.path.basename(filename))[0]
        doc = FreeCAD.newDocument(docname)
        doc.Label = docname
        FreeCAD.setActiveDocument(doc.Name)

    # store IFC data
    if IFCINCLUDE == "full":
        fobj = doc.addObject("App::TextDocument", "IfcFileData")
        fobj.Label = "IFC file data"
        f = builtins.open(filename)
        ifcdata = f.read()
        f.close()
        fobj.Text = ifcdata
    elif IFCINCLUDE == "link":
        ifcdata = "file://" + filename + ";;hash:"
        hasher = hashlib.md5()
        with builtins.open(filename, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        ifcdata += hasher.hexdigest()
        m = doc.Meta
        m["IfcFileLink"] = ifcdata
        doc.Meta = m

    # open the file
    ifcfile = ifcopenshell.open(filename)
    progressbar = Base.ProgressIndicator()
    productscount = len(ifcfile.by_type("IfcProduct"))
    progressbar.start("Importing " + str(productscount) + " products...", productscount)
    cores = params.GetInt("ifcMulticore", 0)
    iterator = ifcopenshell.geom.iterator(settings, ifcfile, cores)
    iterator.initialize()
    count = 0

    # process objects
    while True:
        item = iterator.get()
        if item:
            ifcproduct = ifcfile.by_id(item.guid)
            if not ifcproduct.is_a() in EXCLUDELIST:
                brep = item.geometry.brep_data
                obj = createProduct(ifcproduct, brep)
                progressbar.next(True)
                writeProgress(count, productscount, starttime)
                count += 1
        if not iterator.next():
            break

    # process 2D annotations
    annotations = ifcfile.by_type("IfcAnnotation")
    if annotations:
        print("Processing", str(len(annotations)), "annotations...")
        gr = doc.addObject("App::DocumentObjectGroup", "Annotations")
        ifcscale = importIFCHelper.getScaling(ifcfile)
        p = {"PREFIX_NUMBERS": False}
        for annotation in annotations:
            anno = importIFCHelper.createAnnotation(annotation, doc, ifcscale, p)
            if anno:
                gr.addObject(anno)

    # post-processing
    processRelationships()
    storeColorDict()

    # finished
    progressbar.stop()
    FreeCAD.ActiveDocument.recompute()
    endtime = round(time.time() - starttime, 1)
    fs = round(filesize, 1)
    ratio = int(endtime / filesize)
    endtime = "%02d:%02d" % (divmod(endtime, 60))
    writeProgress()  # this cleans the line
    print("Finished importing", fs, "Mb in", endtime, "s, or", ratio, "s/Mb")
    return FreeCAD.ActiveDocument


def writeProgress(count=None, total=None, starttime=None):
    """write progress to console"""

    if not FreeCAD.GuiUp:
        if count is None:
            sys.stdout.write("\r")
            return
        r = count / total
        elapsed = round(time.time() - starttime, 1)
        if r:
            rest = elapsed * ((1 - r) / r)
            eta = "%02d:%02d" % (divmod(rest, 60))
        else:
            eta = "--:--"
        hashes = "#" * int(r * 10) + " " * int(10 - r * 10)
        fstring = "\rImporting " + str(total) + " products [{0}] {1}%, ETA: {2}"
        sys.stdout.write(fstring.format(hashes, int(r * 100), eta))


def createProduct(ifcproduct, brep):
    """creates an Arch object from an IFC product"""

    import Part

    shape = Part.Shape()
    shape.importBrepFromString(brep, False)
    shape.scale(1000.0)  # IfcOpenShell outputs in meters
    if ifcproduct.is_a("IfcSpace"):
        obj = Arch.makeSpace()
        # TODO Temp workaround against layer causing appearance change
        if obj.ViewObject:
            obj.ViewObject.DisplayMode = "Wireframe"
    else:
        obj = Arch.makeComponent()
    obj.Shape = shape
    objects[ifcproduct.id()] = obj
    setAttributes(obj, ifcproduct)
    setProperties(obj, ifcproduct)
    createLayer(obj, ifcproduct)
    createMaterial(obj, ifcproduct)
    createModelStructure(obj, ifcproduct)
    setRelationships(obj, ifcproduct)
    setColor(obj, ifcproduct)
    return obj


def setAttributes(obj, ifcproduct):
    """sets the IFC attributes of a component"""

    ifctype = ArchIFC.uncamel(ifcproduct.is_a())
    if ifcproduct.Name:
        obj.Label = ifcproduct.Name
    if ifctype in ArchIFC.IfcTypes:
        obj.IfcType = ifctype
    for attr in dir(ifcproduct):
        if attr in obj.PropertiesList:
            value = getattr(ifcproduct, attr)
            if value:
                try:
                    setattr(obj, attr, value)
                except Exception:
                    pass

    # register IFC data
    obj.addProperty("App::PropertyInteger", "IfcID", "IfcLink")
    obj.addProperty("App::PropertyBool", "Modified", "IfcLink")
    obj.IfcID = ifcproduct.id()
    obj.Modified = False
    obj.setEditorMode("IfcID", 2)
    obj.setEditorMode("Modified", 2)


def setProperties(obj, ifcproduct):
    """sets the IFC properties of a component"""

    props = obj.IfcProperties
    for prel in ifcproduct.IsDefinedBy:
        if prel.is_a("IfcRelDefinesByProperties"):
            pset = prel.RelatingPropertyDefinition
            if pset.is_a("IfcPropertySet"):
                for prop in pset.HasProperties:
                    if hasattr(prop, "NominalValue"):
                        propname = cleanName(prop.Name)
                        propgroup = cleanName(pset.Name)
                        proptype, propvalue, ifctype = getPropertyValue(
                            prop.NominalValue
                        )
                        # if pset.Name.startswith("Ifc"):
                        if (PROPERTYMODE == "new") or (
                            (PROPERTYMODE == "hybrid")
                            and not (propgroup.lower().startswith("pset"))
                        ):
                            # creating FreeCAD property
                            while propname in obj.PropertiesList:
                                propname = propname + "_"
                            obj.addProperty(proptype, propname, propgroup)
                            setattr(obj, propname, propvalue)
                        else:
                            # storing in IfcProperties (0.20 behaviour)
                            propname = propname + ";;" + propgroup
                            propvalue = ifctype + ";;" + propvalue
                            props[propname] = propvalue
    obj.IfcProperties = props


def cleanName(txt):
    """removes anything non alpha and non ascii from a string"""

    txt = "".join([c for c in txt if c.isalnum() and c.isascii()])
    if txt[0].isdigit():
        txt = "_" + txt
    return txt


def getPropertyValue(value):
    """returns a FreeCAD property type and value form an IfcNominalProperty"""

    values = [p.strip("'") for p in str(value).strip(")").split("(")]
    ifctype = values[0]
    propvalue = values[1]
    proptype = "App::PropertyString"  # default
    if ifctype == "IfcInteger":
        proptype = "App::PropertyInteger"
        propvalue = int(propvalue)
    elif ifctype in ["IfcReal", "IfcThermodynamicTemperatureMeasure"]:
        proptype = "App::PropertyFloat"
        propvalue = float(propvalue)
    elif ifctype == "IfcBoolean":
        proptype = "App::PropertyBool"
        if "T" in propvalue:
            propvalue = True
        else:
            propvalue = False
    elif ifctype in "IfcPlaneAngleMeasure":
        proptype = "App::PropertyAngle"
        propvalue = float(propvalue)
    return proptype, propvalue, ifctype


def setColor(obj, ifcproduct):
    """sets the color of an object"""

    global colors

    color = importIFCHelper.getColorFromProduct(ifcproduct)
    colors[obj.Name] = color
    if FreeCAD.GuiUp and color:
        obj.ViewObject.ShapeColor = color[:3]


def createLayer(obj, ifcproduct):
    """sets the layer of a component"""

    global layers

    if ifcproduct.Representation:
        for rep in ifcproduct.Representation.Representations:
            for layer in rep.LayerAssignments:
                if not layer.id() in layers:
                    l = Draft.make_layer(layer.Name)
                    # TODO: read layer properties
                    if l.ViewObject:
                        l.ViewObject.OverrideLineColorChildren = False
                        l.ViewObject.OverrideShapeColorChildren = False
                    layers[layer.id()] = l
                layers[layer.id()].Proxy.addObject(layers[layer.id()], obj)


def createMaterial(obj, ifcproduct):
    """sets the material of a component"""

    global materials

    for association in ifcproduct.HasAssociations:
        if association.is_a("IfcRelAssociatesMaterial"):
            material = association.RelatingMaterial
            if material.is_a("IfcMaterialList"):
                material = material.Materials[0]  # take the first one for now...
            if material.is_a("IfcMaterial"):
                if not material.id() in materials:
                    color = importIFCHelper.getColorFromMaterial(material)
                    materials[material.id()] = Arch.makeMaterial(
                        material.Name, color=color
                    )
                obj.Material = materials[material.id()]


def createModelStructure(obj, ifcobj):
    """sets the parent containers of an IFC object"""

    global objects

    for parent in importIFCHelper.getParents(ifcobj):
        if not parent.id() in objects:
            if parent.is_a("IfcProject"):
                parentobj = Arch.makeProject()
            elif parent.is_a("IfcSite"):
                parentobj = Arch.makeSite()
            else:
                parentobj = Arch.makeBuildingPart()
            setAttributes(parentobj, parent)
            setProperties(parentobj, parent)
            createModelStructure(parentobj, parent)
            objects[parent.id()] = parentobj
        if hasattr(objects[parent.id()].Proxy, "addObject"):
            objects[parent.id()].Proxy.addObject(objects[parent.id()], obj)


def setRelationships(obj, ifcobj):
    """sets additions/subtractions"""

    global adds
    global subs

    if hasattr(ifcobj, "HasOpenings") and ifcobj.HasOpenings:
        for rel in ifcobj.HasOpenings:
            subs.setdefault(ifcobj.id(), []).append(rel.RelatedOpeningElement)

    # TODO: assemblies & booleans


def processRelationships():
    """process all stored relationships"""

    for dom in ((subs, "Subtractions"), (adds, "Additions")):
        for key, vals in dom[0].items():
            if key in objects:
                for val in vals:
                    if val in objects:
                        if hasattr(objects[key], dom[1]):
                            g = getattr(objects[key], dom[1])
                            g.append(val)
                            setattr(objects[key], dom[1], g)


def storeColorDict():
    """stores the color dictionary in the document Meta if non-GUI mode"""

    if colors and not FreeCAD.GuiUp:
        import json

        d = FreeCAD.ActiveDocument.Meta
        d["colordict"] = json.dumps(colors)
        FreeCAD.ActiveDocument.Meta = d
