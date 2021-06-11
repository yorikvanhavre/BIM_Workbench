#***************************************************************************
#*   Copyright (c) 2020 Carlo Pavan                                        *
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
"""Provide the object code for Arch Wall."""
## @package wall
# \ingroup ARCH
# \brief Provide the object code for Arch Wall.

import math

import FreeCAD as App

import Draft
import DraftVecUtils
import DraftGeomUtils
import draftutils.utils as utils

from archobjects.base import ShapeGroup
from ArchIFC import IfcProduct

if App.GuiUp:
    import FreeCADGui as Gui
    from PySide import QtCore, QtGui


class Wall(ShapeGroup, IfcProduct):
    """
    A prototype for a new wall object for the Arch Workbench
    """
    def __init__(self, obj=None):
        super(Wall, self).__init__(obj)
        # print("running wall object init method\n")
        if obj:
            # print("running obj init method")

            obj.Proxy = self
            self.Object = obj
            self.attach(obj)
            self.execute(obj)

        self.Type = 'Arch_Wall'

        self.obj_gui_tools = None
        if App.GuiUp:
            self.obj_gui_tools = WallGuiTools()


    def attach(self, obj):
        ShapeGroup.attach(self, obj)
        self.set_properties(obj)


    def set_properties(self, obj):
        """ Setup object properties.
        """
        # Ifc Properties ----------------------------------------------------
        IfcProduct.setProperties(self, obj)
        obj.IfcType = "Wall"
        obj.PredefinedType = "STANDARD"

        # BASE Properties ---------------------------------------------------
        _tip = 'Link to the material object.'
        obj.addProperty('App::PropertyLink', 'Material',
                        'Base', _tip)

        # COMPONENTS Properties (partially implemented at the moment) ---------
        _tip = 'Optional objects to use as base geometry for the wall shape'
        obj.addProperty('App::PropertyLinkListChild', 'BaseGeometry',
                        'Components', _tip) # TODO: better PropertyLinkListGlobal or PropertyLinkListChild?
        
        _tip = 'List of objects to include in a compound with the base wall shape'
        obj.addProperty('App::PropertyLinkListChild', 'Additions',
                        'Components', _tip) # TODO: better PropertyLinkListGlobal or PropertyLinkListChild?
        
        _tip = 'List of objects to subtract from the wall shape'
        obj.addProperty('App::PropertyLinkListGlobal', 'Subtractions',
                        'Components', _tip)

        _tip = 'List of Openings inserted into the wall.\n'\
               'Openings have to be grouped into the wall object.'
        obj.addProperty('App::PropertyLinkListGlobal', 'Openings',
                        'Components', _tip)

        # GEOMETRY Properties -----------------------------------------------
        _tip = 'Define the X coordinate of the start point of the core axis.\n'
        obj.addProperty('App::PropertyDistance', 'AxisFirstPointX', #change to BaselineStart
                        'Geometry', _tip).AxisFirstPointX = 0.0

        _tip = 'Define the X coordinate of the end point of the core axis.\n'
        obj.addProperty('App::PropertyDistance', 'AxisLastPointX', #change to BaselineEnd
                        'Geometry', _tip).AxisLastPointX = 4000.0

        _tip = 'Link to an edge subobject to bind the wall axis\n'\
               'Not implemented yet' # TODO: implement external axis binding
        obj.addProperty('App::PropertyLinkSubGlobal', 'AxisLink',
                        'Geometry', _tip)

        obj.addProperty('App::PropertyLength', 'Length',
                        'Geometry', 'Wall length',1).Length = '4 m'

        obj.addProperty('App::PropertyLength', 'Width',
                        'Geometry', 'Wall width').Width = '35 cm'

        obj.addProperty('App::PropertyLength', 'Height',
                        'Geometry', 'Wall height').Height = '2.7 m'

        # LEVEL Properties (not implemented yet) ----------------------------
        _tip = 'Constrain the wall base to the parent level (Not implemented yet).'
        obj.addProperty('App::PropertyBool', 'BaseConstrain', 
                        'Level properties', 
                        _tip).BaseConstrain = True

        _tip = 'If the wall base is constrained to the parent level,\
                set Z offset (Not implemented yet).'
        obj.addProperty('App::PropertyLength', 'BaseOffset', 
                        'Level properties', 
                        _tip).BaseOffset = '0'

        _tip = 'Constrain the wall top to the upper level (Not implemented yet).'
        obj.addProperty('App::PropertyBool', 'TopConstrain', 
                        'Level properties', 
                        _tip).TopConstrain = True

        _tip = 'If the wall top is constrained to the parent level,\
                set Z offset (Not implemented yet).'
        obj.addProperty('App::PropertyLength', 'TopOffset', 
                        'Level properties', 
                        _tip).TopOffset = '0'

        # WALL CONNECTIONS Properties ---------------------------------------
        _tip = "Allow automatic compute of first end"
        obj.addProperty('App::PropertyBool', 'JoinFirstEnd',# TODO: Transform to AutoJoinFirstEnd
                        'Wall connections', _tip).JoinFirstEnd = True

        _tip = "Allow automatic compute of last end"
        obj.addProperty('App::PropertyBool', 'JoinLastEnd',# TODO: Transform to AutoJoinLastEnd
                        'Wall connections', _tip).JoinLastEnd = True

        _tip = "Names of the objects that target current wall"
        obj.addProperty('App::PropertyStringList', 'IncomingTJoins',
                        'Wall connections', _tip).IncomingTJoins = []

        _tip = "Name of the object to join wall's first end"
        obj.addProperty('App::PropertyString', 'JoinFirstEndTo',
                        'Wall connections', _tip).JoinFirstEndTo = ''

        _tip = "Name of the object to join wall's last end"
        obj.addProperty('App::PropertyString', 'JoinLastEndTo',
                        'Wall connections', _tip).JoinLastEndTo = ''

        # WALL ENDS Properties ---------------------------------------------- 
        # All the angle properties are meant to be hidden and showed just on user demand
        _tip = 'Angular cut of first wall end core inner half'
        obj.addProperty('App::PropertyAngle', 'FirstCoreInnerAngle', 
                        'Wall Ends', _tip, 4).FirstCoreInnerAngle = '90 deg'
        
        _tip = 'Angular cut of first wall end core outer half'
        obj.addProperty('App::PropertyAngle', 'FirstCoreOuterAngle', 
                        'Wall Ends', _tip, 4).FirstCoreOuterAngle = '90 deg'

        _tip = 'First core axis endline offset'
        obj.addProperty('App::PropertyDistance', 'FirstCoreOffset', 
                        'Wall Ends', _tip, 4).FirstCoreOffset = 0.0

        _tip = 'Angular cut of first wall end inner layer (to be implemented)'
        obj.addProperty('App::PropertyAngle', 'LastCoreInnerAngle',
                        'Wall Ends', _tip, 4).LastCoreInnerAngle = '90 deg'

        _tip = 'Angular cut of first wall end outer layer (to be implemented)'
        obj.addProperty('App::PropertyAngle', 'LastCoreOuterAngle', 
                        'Wall Ends', _tip, 4).LastCoreOuterAngle = '90 deg'
        
        _tip = 'Last core axis endline offset'
        obj.addProperty('App::PropertyDistance', 'LastCoreOffset', 
                        'Wall Ends', _tip, 4).LastCoreOffset = 0.0
        

    def onBeforeChange(self, obj, prop):
        """this method is activated before a property changes"""
        
        # WALL ENDS properties: remove the old join references before computing the new
        if (hasattr(obj, "JoinFirstEndTo") and hasattr(obj, "JoinLastEndTo") and
            hasattr(obj, "JoinFirstEnd")and hasattr(obj, "JoinLastEnd")):

            if prop == "JoinFirstEndTo" and obj.JoinFirstEnd:
                target = App.ActiveDocument.getObject(obj.JoinFirstEndTo)
                if hasattr(target, "IncomingTJoins"):
                    lst = target.IncomingTJoins
                    if obj.Name in lst:
                        lst.remove(obj.Name)
                        target.IncomingTJoins = lst

            elif prop == "JoinLastEndTo" and obj.JoinLastEnd:
                target = App.ActiveDocument.getObject(obj.JoinFirstEndTo)
                if hasattr(target, "IncomingTJoins"):
                    lst = target.IncomingTJoins
                    if obj.Name in lst:
                        lst.remove(obj.Name)
                        target.IncomingTJoins = lst

        if prop == "Group":
            # store the previous configuration of wall Group property
            # so the onChanged method can compare with the new configuration
            # and understand if objects were added or removed
            self.oldGroup = obj.Group
    

    def onChanged(self, obj, prop):
        """This method is activated when a property changes.
        """
        super(Wall, self).onChanged(obj, prop)

        if prop == "Material" and hasattr(obj, "Material"):
            if obj.Material and utils.get_type(obj.Material) == 'MultiMaterial':
                obj.Width = App.Units.Quantity(str(sum(obj.Material.Thicknesses))+"mm")

        if prop == "Placement" and hasattr(obj, "Placement"):
            # TODO: recompute only if end is set
            # Recompute wall joinings
            self.recompute_ends(obj)
            for t_name in obj.IncomingTJoins:
                t = App.ActiveDocument.getObject(t_name)
                t.Proxy.recompute_ends(t)

        if prop == "Width" and hasattr(obj, "Width") and hasattr(obj, "IncomingTJoins") and hasattr(obj, "Openings"):
            obj.Proxy.recompute_ends(obj)
            for t_name in obj.IncomingTJoins:
                t = App.ActiveDocument.getObject(t_name)
                t.Proxy.recompute_ends(t)
            for opening in obj.Openings:
                if not hasattr(opening, "HostThickness"):
                    continue
                opening.HostThickness = obj.Width

        # WALL JOIN ENDS properties
        if (hasattr(obj, "JoinFirstEndTo") and hasattr(obj, "JoinLastEndTo") and
            hasattr(obj, "JoinFirstEnd") and hasattr(obj, "JoinLastEnd")):

            if prop == "JoinFirstEndTo" and obj.JoinFirstEnd:
                self.recompute_end(obj, 0)

            elif prop == "JoinLastEndTo" and obj.JoinLastEnd:
                self.recompute_end(obj, 1)

        if (prop == "AxisFirstPointX" or prop == "AxisLastPointX") and (
                hasattr(obj, "AxisFirstPointX") and hasattr(obj, "AxisLastPointX")):
            #if obj.AxisFirstPointX.x > obj.AxisLastPointX.x:   circular
            #    obj.AxisFirstPointX, obj.AxisLastPointX = obj.AxisLastPointX, obj.AxisFirstPointX
            if hasattr(obj, "Length"):
                obj.Length = abs(obj.AxisLastPointX - obj.AxisFirstPointX)

        # CHILDREN properties: remember to first assign basegeometry and then add the object to the group
        if prop == "BaseGeometry" and hasattr(obj, "BaseGeometry"):
            pass

        # AXIS properties: align wall to an external edge
        if prop == "AxisLink" and hasattr(obj, "AxisLink"):
            self.align_axis_to_edge(obj, obj.AxisLink)

        # Group property: an object is added or removed from the wall
        if prop == "Group" and hasattr(obj, "Group") and hasattr(obj, 
                "BaseGeometry") and hasattr(obj, "Subtractions"):
            self.group_changed(obj)


    def mustExecute(self, obj):
        """Return True if the object must be executed.
        """
        if hasattr(obj, 'AxisLink') and obj.AxisLink is not None:
            linkedObj = obj.AxisLink[0]
            if linkedObj.State == ['Touched']:
                self.align_axis_to_edge(obj, obj.AxisLink)
                return True


    def execute(self, obj):
        """ Compute the wall shape as boolean operations among the component objects """


        # print("running " + obj.Name + " execute() method\n")
        import Part

        # gather base wall_shape (from obj.BaseGeometry or from default shape)
        wall_shape = None
        if hasattr(obj, "BaseGeometry") and obj.BaseGeometry:
            wall_shape = self.get_shape_from_base_geometry(obj)
        else:
            wall_shape = self.get_default_shape(obj)
        
        if wall_shape is None:
            return

        """
        Perform boolean operations between the base shape and 
        Additions, Subtractions, and Openings.

        Openings have to provide a proper shape to cut the wall through
        opening.Proxy.get_void_shape(opening) method that returns a Part Shape
        already in the right relative position.
        If the user wants to use a random shape to cut the wall he will use 
        the Subtractions list.
        """
        if hasattr(obj, "Additions") and obj.Additions:
            # get wall base shape from BaseGeometry objects
            shape_collection = []
            for o in obj.Additions:
                if hasattr(o, "Shape") and not o.Shape.isNull():
                    shape_collection.append(o.Shape)
            if shape_collection:
                shape_collection.append(wall_shape)
                # TODO: Is it better to fuse the additions instead of grouping them with a compound?
                wall_shape = Part.makeCompound(shape_collection)

        # subtract Subtractions
        if hasattr(obj, "Subtractions") and obj.Subtractions:
            for o in obj.Subtractions:
                cut_shape = None
                if o in obj.Group and hasattr(o, "Shape"):
                    # subtraction object is inside the wall
                    relative_placement = o.Placement
                    if hasattr(o, "InList") and o.InList[0] != obj:
                        # don't remember why this is necessary...
                        relative_placement = o.InList[0].Placement.multiply(o.Placement)
                    cut_shape = o.Shape.copy()
                    cut_shape.Placement = relative_placement
                elif hasattr(o, "Shape"):
                    # subtraction object is not inside the wall, compute it's correct relative placement
                    global_placement = o.getGlobalPlacement()
                    relative_placement = obj.getGlobalPlacement().inverse().multiply(global_placement)
                    cut_shape = o.Shape.copy()
                    cut_shape.Placement = relative_placement

                if cut_shape is not None:
                    wall_shape = wall_shape.cut(cut_shape)

        if hasattr(obj, "Openings") and obj.Openings:
            # objects marked as Openings must be appropriate Opening objects to cut the wall
            # TODO: Add a flag to also subtract window positive shapes from wall
            for o in obj.Openings:
                # cut opening void
                void = None
                if o in obj.Group and hasattr(o, "VoidShape"):
                    void = o.VoidShape.copy()
                elif hasattr(o, "VoidShape"):
                    # opening object is not inside the wall, compute it's correct relative placement
                    global_placement = o.getGlobalPlacement()
                    relative_placement = obj.getGlobalPlacement().inverse().multiply(global_placement)
                    void = o.VoidShape.copy()
                    # void placement can be different from opening placement:
                    void.Placement = relative_placement.multiply(o.Placement.inverse().multiply(void.Placement))

                if void is not None:
                    wall_shape = wall_shape.cut(void)

        obj.Shape = wall_shape


    # Wall default shape methods +++++++++++++++++++++++++++++++++++++++++++++++

    def get_default_shape(self, obj):
        """
        The wall default base shape is defined as 2 Part Wedge solids, fused together;
        splays are controlled by obj.FirstCoreOuterAngle, obj.LastCoreOuterAngle
                                 obj.FirstCoreInnerAngle, obj.LastCoreInnerAngle

        TODO: Adding support for default multi-layer walls.

                 <--> first_splay                <--> last_splay
                 ---------------------------------  outer surface
                  \         Part Wedge 1          \ 
                   \           core axis           \ 
        first_point o-------------------------------o  last_point
                     \                               \ 
                      \       Part Wedge 2            \ 
                       ---------------------------------  inner surface
                    <--> first_splay                <--> last_splay
        """
        import Part

        if not hasattr(obj,"AxisFirstPointX") or not hasattr(obj,"AxisLastPointX") \
            or not hasattr(obj,"Width") or not hasattr(obj,"Height"):
            return

        length = obj.Length

        if obj.AxisFirstPointX == obj.AxisLastPointX or length < Draft.tolerance():
            return

        if hasattr(obj, "Material") and obj.Material and utils.get_type(obj.Material) == 'MultiMaterial':
            # if MultiMaterial assigned, ignore Width property.
            thickness = App.Units.Quantity(str(sum(obj.Material.Thicknesses))+"mm") # TODO: Multimaterial should have a readonly Thickness Property
            # self.onChanged(obj, "Material") # to update the Width property
        else:
            thickness = obj.Width

        # swap first point and last point to have them in the right order
        # TODO: Swap the points phisically and change end constraints!
        if obj.AxisFirstPointX < obj.AxisLastPointX:
            first_point = obj.AxisFirstPointX
        elif obj.AxisFirstPointX > obj.AxisLastPointX:
            first_point = obj.AxisLastPointX
        
        first_splay = thickness/2 * math.tan(math.pi/2-math.radians(obj.FirstCoreInnerAngle))
        last_splay = thickness/2 * math.tan(math.pi/2-math.radians(obj.LastCoreInnerAngle))
        
        Xmin = -obj.FirstCoreOffset
        Ymin = 0
        Zmin = 0
        Z2min = 0
        X2min = first_splay - obj.FirstCoreOffset
        Xmax = length + obj.LastCoreOffset
        Ymax = thickness/2
        Zmax = obj.Height
        Z2max = obj.Height
        X2max = length - last_splay + obj.LastCoreOffset

        # checking conditions that will break Part.makeWedge()
        if first_splay >= length:
            print("Wall is too short compared to the first splay: removing angles of outer core layer\n")
            X2min = 0
        if last_splay >= length:
            print("Wall is too short compared to the last splay: removing angles of outer core layer\n")
            X2max = length
        if ( first_splay + last_splay ) >= length:
            print("Wall is too short compared to the splays: removing angles of inner core layer\n")
            X2min = 0
            X2max = length

        inner_half = Part.makeWedge( Xmin, Ymin, Zmin, Z2min, X2min,
                                        Xmax, Ymax, Zmax, Z2max, X2max)#, obj.AxisFirstPointX, obj.AxisLastPointX )
        inner_half.Placement.Base.x = first_point

        first_splay = thickness/2 * math.tan(math.pi/2-math.radians(obj.FirstCoreOuterAngle))
        last_splay = thickness/2 * math.tan(math.pi/2-math.radians(obj.LastCoreOuterAngle))          
        
        Xmin = first_splay - obj.FirstCoreOffset
        Ymin = 0
        Zmin = 0
        Z2min = 0
        X2min = -obj.FirstCoreOffset
        Xmax = length - last_splay + obj.LastCoreOffset
        Ymax = thickness/2
        Zmax = obj.Height
        Z2max = obj.Height
        X2max = length + obj.LastCoreOffset

        # checking conditions that will break Part.makeWedge()
        if first_splay >= length:
            print("Wall is too short compared to the first splay: removing angles of outer core layer\n")
            Xmin = 0
        if last_splay >= length:
            print("Wall is too short compared to the last splay: removing angles of outer core layer\n")
            Xmax = length
        if ( first_splay + last_splay ) >= length:
            print("Wall is too short compared to the splays: removing angles of outer core layer\n")
            Xmin = 0
            Xmax = length

        outer_half = Part.makeWedge( Xmin, Ymin, Zmin, Z2min, X2min,
                                        Xmax, Ymax, Zmax, Z2max, X2max)#, obj.Start, obj.End)
                
        outer_half.Placement.Base = App.Vector(first_point, - thickness/2)
        
        mono_layer = inner_half.fuse(outer_half)

        mono_layer = mono_layer.removeSplitter()
        
        # split according to material layers

        if hasattr(obj, "Material") and obj.Material and utils.get_type(obj.Material) == 'MultiMaterial':
            pass
        else:
            return mono_layer

        layer_thicknesses = obj.Material.Thicknesses

        slicing_plane = Part.makePlane(500000.0, 500000.0, App.Vector(-250000.0, -250000.0, 0.0))
        slicing_plane.rotate(App.Vector(0 ,0 , 0), App.Vector(1, 0, 0), 90.0)

        slicing_planes = []
        offset = 0.0
        for lt in layer_thicknesses[:-1]:
            offset += lt
            plane = slicing_plane.copy()
            plane.translate(App.Vector(0, offset-thickness.Value/2, 0))
            slicing_planes.append(plane)

        compound = mono_layer.generalFuse(slicing_planes)[0] # generalFuse output also a list of list of shape (map)

        for shape in compound.SubShapes:
            if shape.ShapeType == "Compound":
                return shape


    # Wall default shape joining methods ++++++++++++++++++++++++++++++++++++++++

    def recompute_ends(self, obj):
        self.recompute_end(obj, 0)
        self.recompute_end(obj, 1)


    def recompute_end(self, obj, end_idx):
        """
        This method auto recompute the first or the last wall end joint
        If the obj and the target objects are both joinable it recompute the
        joints, if not it resets the corresponding wall end to 90 deg.

        Parameters
        -----
        obj         wall object
        end_idx     None or 0 or 1
                    the wall end index:
                    0 for first end
                    1 for last end
                    2 for both ends
        """
        if obj == None:
            print("Cannot recompute ends of a None object")
            return
        if obj.JoinFirstEndTo == obj.JoinLastEndTo and obj.JoinFirstEndTo != "":
            print("The wall cannot target the same wall on both JoinFirst and JoinLast properties")
            return
        if end_idx == 0:
            target = App.ActiveDocument.getObject(obj.JoinFirstEndTo)
            if target == obj or target == None:
                return
            if self.is_wall_joinable(obj):
                if self.is_wall_joinable(target):
                    self.join_end(obj, target, 0)
                else:
                    self.reset_end(obj, 0)

        if end_idx == 1:
            target = App.ActiveDocument.getObject(obj.JoinLastEndTo)
            if target == obj or target == None:
                return
            if self.is_wall_joinable(obj):
                if self.is_wall_joinable(target):
                    self.join_end(obj, target, 1)
                else:
                    self.reset_end(obj, 1)


    def is_wall_joinable(self, obj):
        """
        Returns True if the given object type is 'Arch_Wall' and if its
        BaseGeometry is an 'Arch_WallSegment' object.
        in every other case returns False.
        """

        if Draft.get_type(obj) != "Arch_Wall":
            print("Wall " + obj.Name + "is not a valid Arch_Wall objects")
            return False
        if obj.BaseGeometry != []:
            print("Wall Joining only works if base geometry is not set")
            return False
        return True


    def reset_end(self, obj, idx):
        """
        Reset given wall object end joints.

        Parameters
        -----
        obj         wall object
        end_idx     the wall end index to reset
                    0 for first end
                    1 for last end
        """
        print("running reset_end() "+obj.Name+"_"+str(idx)+"\n")
        if idx == 0:
            obj.FirstCoreInnerAngle = '90 deg'
            obj.FirstCoreOuterAngle = '90 deg'
        elif idx == 1:
            obj.LastCoreInnerAngle = '90 deg'
            obj.LastCoreOuterAngle = '90 deg'


    def remove_linked_walls_references(self, obj):
        """ 
        Removes the reference to given wall to all the other 
        walls that target it to join
        """
        print("REMOVE ALL REFERENCES on DELETING")
        references = obj.IncomingTJoins
        references.append(obj.JoinFirstEndTo)
        references.append(obj.JoinLastEndTo)
    
        for link in references:
            o = App.ActiveDocument.getObject(link)

            if o:
                if hasattr(o, "JoinFirstEndTo"):
                    if o.JoinFirstEndTo == obj.Name:
                        o.JoinFirstEndTo = ""
                if hasattr(o, "JoinLastEndTo"):
                    if o.JoinLastEndTo == obj.Name:
                        o.JoinLastEndTo = ""
                if hasattr(o, "IncomingTJoins"):
                    if obj.Name in o.IncomingTJoins:
                        target_list = o.IncomingTJoins
                        target_list.remove(obj.Name)
                        o.IncomingTJoins = target_list


    def join_end(self, obj, target, end_idx):
        """ Join the wall to the target wall """
        # calculate which type of joining
        join_type, target_idx = self.guess_join_type(obj, target)

        if join_type == "T":
            w_ext = self.extend(obj, target, end_idx)
            if w_ext:
                self.T_join(obj, target, end_idx)
            else:
                return False

        elif join_type == "L":
            w_ext = self.extend(obj, target, end_idx)
            t_ext = self.extend(target, obj, target_idx)
            if w_ext and t_ext:
                self.L_join(obj, target, end_idx, target_idx)
                self.L_join(target, obj, target_idx, end_idx)
            else:
                return False
   
        return True 
    

    def guess_join_type(self, obj, target):
        """ Guess which kind of joint to apply to the given wall """
        # print("running guess_join_type()\n")
        if target.JoinFirstEndTo == obj.Name and target.JoinFirstEnd:
            return "L", 0
        elif target.JoinLastEndTo == obj.Name and target.JoinLastEnd:
            return "L", 1
        else:
            return "T", None


    def extend(self, wall, target, idx):
        """ Extend the given wall to the target wall """
        print("--------\n"+"Extend "+wall.Name + " to " +target.Name+ "\n")

        wall_core_axis = wall.Proxy.get_core_axis(wall)#.toShape()
        target_core_axis = target.Proxy.get_core_axis(target)#.toShape()
        if wall_core_axis is None or target_core_axis is None:
            print("Failed to get wall core axis")
            return False

        int_pts = wall_core_axis.intersect(target_core_axis)
        if len(int_pts) == 1:
            int_p = int_pts[0]        
            intersection = App.Vector(int_p.X,int_p.Y,int_p.Z)
        else:
            print("No intersection point found, or too many intersection points found")
            return False

        if idx == 0:
            wall.Proxy.set_first_point(wall, intersection)
            return True
        elif idx == 1:
            wall.Proxy.set_last_point(wall, intersection)
            return True


    def T_join(self, wall, target, idx): 
        """ Compute wall angles according to given parameters """
        print("--------\n"+"T_Join "+wall.Name + " with " +target.Name+ "\n")

        if idx == 0:
            w1 = wall.Proxy.get_first_point(wall)
            w2 = wall.Proxy.get_last_point(wall)
        elif idx == 1:
            w1 = wall.Proxy.get_last_point(wall)
            w2 = wall.Proxy.get_first_point(wall)

        t1 = target.Proxy.get_first_point(target)
        t2 = target.Proxy.get_last_point(target)

        angle = math.degrees(DraftVecUtils.angle(w2-w1,t2-t1))
        # print(angle)

        # identify if the function have to join the first or the end of the wall
        if idx == 0:
            wall.FirstCoreInnerAngle = angle
            wall.FirstCoreOuterAngle = -angle
            wall.FirstCoreOffset = - abs(target.Width / 2 / math.cos(math.pi / 2 - math.radians(angle)))
        elif idx == 1:
            wall.LastCoreInnerAngle = -angle
            wall.LastCoreOuterAngle = angle
            wall.LastCoreOffset = - abs(target.Width / 2 / math.cos(math.pi / 2 - math.radians(angle)))

        if not wall.Name in target.IncomingTJoins:
            target_list = target.IncomingTJoins
            target_list.append(wall.Name)
            target.IncomingTJoins = target_list


    def L_join(self, wall, target, idx , target_idx):
        """ Compute given wall angles to corner join target wall,
            mind that when calling this method, the 2 walls already
            have a coincident end point (achieved by the extend method).

                      /    wall
                     /     /     / .
                    /     /     /   angle   
                   /     /_wi__/______.__________________________         
                  /     /    ./       .
                 /  ti /  c. /        .
                /     /  .  /ti       . target.Width        
               /     / .   /          .
              /____ /_____/_____ _____._____ _____ _____ _____ __
             /    ./  wi /                    target
            /   . /     /
           /  .  /     /
          / .w_angle  /
         /.____/_____/___________________________________________          

        """
        # TODO: correct the bug of two different size walls with big angle in between
        print("--------\n"+"L_Join "+wall.Name+"_"+str(idx) + " with " +target.Name+"_"+str(target_idx) + "\n")
        
        if idx == 0:
            w1 = wall.Proxy.get_first_point(wall)
            w2 = wall.Proxy.get_last_point(wall)
        elif idx == 1:
            w1 = wall.Proxy.get_last_point(wall)
            w2 = wall.Proxy.get_first_point(wall)

        if target_idx == 0:
            t1 = target.Proxy.get_first_point(target)
            t2 = target.Proxy.get_last_point(target)
        elif target_idx == 1:
            t1 = target.Proxy.get_last_point(target)
            t2 = target.Proxy.get_first_point(target)

        angle = DraftVecUtils.angle(w2-w1,t2-t1)

        # print("angle between walls: " + str(math.degrees(angle)) + "\n")

        if angle > 0:
            w_i = wall.Width * math.cos(math.pi/2-angle)
            t_i = target.Width * math.cos(math.pi/2-angle)
        if angle < 0:
            w_i = wall.Width * math.cos(-math.pi/2-angle)
            t_i = target.Width * math.cos(-math.pi/2-angle)

        c = math.sqrt( w_i**2 + t_i**2 - 2 * abs(w_i) * t_i * math.cos(math.pi-angle) )
        w_angle = math.asin( w_i / c * math.sin(math.pi-angle))
        
        # print("Parameters:\n")
        # print("w_i: " + str(w_i) + "\n")
        # print("c: " + str(c) + "\n")
        # print("flipping parameter: " + str(c) + "\n")    
        # print("cut angle: " + str(math.degrees(w_angle)) + "\n")

        # assign the angles to the correct wall end
        w_angle = math.degrees( w_angle )
        if idx == 0:
            wall.FirstCoreInnerAngle = w_angle
            wall.FirstCoreOuterAngle = -w_angle
            wall.FirstCoreOffset = 0.0
        elif idx == 1:
            wall.LastCoreInnerAngle = -w_angle
            wall.LastCoreOuterAngle = +w_angle
            wall.LastCoreOffset = 0.0


    # Compute shape from base geometry +++++++++++++++++++++++++++++++++++++

    def get_shape_from_base_geometry(self, obj):
        if not self.is_basegeometry_usable(obj.BaseGeometry):
            return

        if len(obj.BaseGeometry) == 1:
            tp = utils.get_type(obj.BaseGeometry)
            if tp == 'Sketcher::SketchObject':
                return self.compute_shape_from_sketch(obj)
            elif tp == 'Wire':
                return self.compute_shape_from_sketch(obj)
            elif obj.BaseGeometry[0].Shape.Solids:
                return self.get_shape_from_object(obj.BaseGeometry[0])
            # TODO: Cover usecase when the basegeometry is a mesh feature
        else:
            return self.get_shape_from_objects(obj.BaseGeometry)
        return None


    def is_basegeometry_usable(self, basegeometry):
        for o in basegeometry:
            if not hasattr(o, "Shape") or not o.Shape.isValid() or o.Shape.isNull():
                return False
        return True


    def compute_shape_from_sketch(self, obj):
        sketch_object = obj.BaseGeometry[0]
        return None


    def compute_shape_from_wire(self, obj):
        wire_object = obj.BaseGeometry[0]
        return None


    def compute_shape_from_face(self, obj):
        face_object = obj.BaseGeometry[0]
        return None


    def get_shape_from_object(self, obj):
        """Returns the shape of the given object after applying the object 
        placement straight to the geometry."""
        shape = obj.Shape.copy()
        shape = shape.transformGeometry(obj.Placement.toMatrix())
        return shape


    def get_shape_from_objects(self, objects):
        import Part
        shape_collection = []
        for o in objects:
            if hasattr(o, "Shape") and not o.Shape.isNull():
                # TODO: Check if the object shape is a solid, 
                # TODO: check if the placement is correctly taken into account
                shape_collection.append(o.Shape.copy())
        return Part.makeCompound(shape_collection)


    # Axis alignment handling methods +++++++++++++++++++++++++++++++++++++++

    def align_axis_to_edge(self, wall, sub_link):
        """Align the wall Placement in LCS xy plane to a given edge.
        If the linked subobject changes, the wall is not notified, so 
        I was thinking to modify the Axis system object to do that.
        TODO: Take into account global placement.
        """

        if sub_link is None:
            return
        linked_object = sub_link[0]
        linked_subobject_names = sub_link[1]
        for name in linked_subobject_names:
            subobject = linked_object.getSubObject(name)
            if hasattr(subobject, "ShapeType") and subobject.ShapeType == 'Edge':
                break
        
        import DraftVecUtils
        v1 = subobject.Vertexes[0].Point
        v2 = subobject.Vertexes[1].Point
        self.align_axis_to_points(wall, v1, v2)

    def align_axis_to_points(self, wall, v1, v2, exact=False):
        p = wall.Placement.Base.sub(v1)
        point_on_edge = DraftVecUtils.project(p, v2.sub(v1)) + v1

        angle = DraftVecUtils.angle(App.Vector(1,0,0), v2.sub(v1))
        print(angle)

        wall.Placement.Base.x = point_on_edge.x
        wall.Placement.Base.y = point_on_edge.y

        wall.Placement.Rotation.Angle = angle


    # Group objects handling methods ++++++++++++++++++++++++++++++++++++++++

    def group_changed(self, obj):
        """This method is called by onChanged when property Group changes.
        Understand if object was added or removed from wall, and performs 
        consequent operations.
        """
        if hasattr(self, "oldGroup"):
            # understand if the object was added or removed
            added_objs = [x for x in obj.Group if x not in self.oldGroup]
            removed_objs = [x for x in self.oldGroup if x not in obj.Group]
            del self.oldGroup
        for o in removed_objs:
            # if it was removed, remove it from wall children linking
            print("Removing " + o.Label + " from " + obj.Label)
            if o in obj.BaseGeometry:
                BaseGeometry = obj.BaseGeometry
                BaseGeometry.remove(o)
                obj.BaseGeometry = BaseGeometry

            elif o in obj.Subtractions:
                Subtractions = obj.Subtractions
                Subtractions.remove(o)
                obj.Subtractions = Subtractions

            elif o in obj.Openings:
                Openings = obj.Openings
                Openings.remove(o)
                obj.Openings = Openings

        for o in added_objs:
            # if it was added, check if it is an opening or ask if it has to be treated as a 
            print("Adding " + o.Name + " to " + obj.Label)
            if o == obj.BaseGeometry:
                continue # check if this is necessary

            if hasattr(o, "IfcType"):
                if o.IfcType == 'Opening Element':
                    self.add_opening(obj, o)
                    continue

            if not o in obj.Subtractions: # subtracting objects can be wherever in the document
                print("added a new object to the wall")
                self.add_as_base_shape(obj, o)


    def add_opening(self, obj, child):
        """
        This method is called when a new object is added to the wall and
        it has a IfcType property that is set to 'Opening Element'.
        
        TODO: check if the opening is a proper FreeCAD Opening object, else
              add it to subtractions
        """
        openings = obj.Openings
        openings.append(child)
        obj.Openings = openings


    def add_as_base_shape(self, obj, child):
        """
        This method is called when a new object is added to the wall.
        It ask the user if the object has to be treated as an opening.
        If so, it add the object to the Subtractions PropertyLinkListChild.
        """
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Object " + obj.Label + " has been added to the wall.")
        msgBox.setInformativeText("Do you want to add it to the wall Base Geometry?\n")
        msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msgBox.setDefaultButton(QtGui.QMessageBox.Yes)
        ret = msgBox.exec_()

        if ret == QtGui.QMessageBox.Yes:
            BaseGeometry = obj.BaseGeometry
            BaseGeometry.append(child)
            obj.BaseGeometry = BaseGeometry
            child.Visibility = False
        elif ret == QtGui.QMessageBox.No:
            return


    # General getter methods ++++++++++++++++++++++++++++++++++++++++++++++++


    def get_core_axis(self, obj):
        """returns a part line representing the core axis of the wall"""
        import Part
        p1 = self.get_first_point(obj)
        p2 = self.get_last_point(obj)
        if p1 == p2:
            print("Points are equal, cannot get the axis")
            return None
        else:
            core_axis= Part.Line(p1, p2)
            return core_axis


    def get_first_point(self, obj, local=False):
        """return a part line representing the core axis of the wall"""
        p1 = App.Vector(obj.AxisFirstPointX, 0, 0)
        if not local:
            p1 = obj.getGlobalPlacement().multVec(p1)
        return p1


    def get_last_point(self, obj, local=False):
        """return a part line representing the core axis of the wall"""
        p2 = App.Vector(obj.AxisLastPointX, 0, 0)
        if not local:
            p2 = obj.getGlobalPlacement().multVec(p2)
        return p2


    def get_point_on_axis(self, obj, point):
        """get_point_on_axis(self, obj, point)

        Return the projection of a point on the wall axis referred to the wall local coordinates."""
        gpl = obj.getGlobalPlacement()
        proj = point.projectToLine(gpl.multVec(self.get_first_point(obj)),
                                   gpl.multVec(self.get_last_point(obj)))
        return gpl.inverse().multVec(proj)


    # General setter methods ++++++++++++++++++++++++++++++++++++++++++++++++

    def set_first_point(self, obj, first_point, local=False):
        """returns a part line representing the core axis of the wall"""
        if first_point.x != obj.AxisLastPointX:
            self.set_point(obj, first_point, 0, local)
            return True
        else:
            print("You are trying to set the first point equal to the last point, this is not allowed.\n")
            return False


    def set_last_point(self, obj, last_point, local=False):
        """returns a part line representing the core axis of the wall"""
        if last_point.x != obj.AxisFirstPointX:
            self.set_point(obj, last_point, 1, local)
            return True
        else:
            print("You are trying to set the last point equal to the first point, this is not allowed.\n")
            return False


    def set_point(self, obj, point, point_idx, local=False):
        """returns a part line representing the core axis of the wall"""
        if local:
            np = point
        else:
            np = obj.getGlobalPlacement().inverse().multVec(point)

        # assign the np to the first or end point of the wall
        if point_idx == 0:
            obj.AxisFirstPointX = np.x
        elif point_idx == 1:
            obj.AxisLastPointX = np.x


    # Other methods +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def flip_wall(self, obj):
        """
        describe
        """
        #TODO: To be implemented yet
        pass


    def onDocumentRestored(self, obj):
        self.Object = obj
        # obj.Proxy.Type needs to be re-setted every time the document is opened.
        obj.Proxy.Type = "Arch_Wall"
        
        self.obj_gui_tools = None
        if App.GuiUp:
            self.obj_gui_tools = WallGuiTools()



try:
    from draftguitools.gui_edit_base_object import GuiTools
except:
    GuiTools = object

class WallGuiTools(GuiTools):
    """ This object contains the tools to provide editpoints, 
    update the object according their movement,
    custom context menu for every editpoint,
    function to evaluate the context menu action, 
    the code for the preview of the modification (TODO).
    This tools are currently used by Draft Edit command.
    """

    def __init__(self):
        pass

    def get_edit_points(self, obj):
        """Return to Draft_Edit a list of edipoints for the given object.
        Remember to use object local coordinates system.

        Parameters:
        obj: the object
        """
        editpoints = []
        editpoints.append(obj.Proxy.get_first_point(obj, local=True))
        editpoints.append(obj.Proxy.get_last_point(obj, local=True))
        return editpoints


    def update_object_from_edit_points(self, obj, node_idx, v, alt_edit_mode=0):
        """Update the object from modified Draft_Edit point.
        No need to recompute at the end.

        Parameters:
        obj: the object
        node_idx: number of the edited node
        v: target vector of the node in object local coordinates system
        alt_edit_mode: alternative edit mode to perform different operations
                       (usually can be selected from the Draft_Edit context menu)
                       default = 0
        """
        if alt_edit_mode == 0:
            # trim/extend endpoint
            if node_idx == 0:
                obj.Proxy.set_first_point(obj, v, local=True)
            elif node_idx == 1:
                obj.Proxy.set_last_point(obj, v, local=True)

        elif alt_edit_mode == 1:
            # rotate wall on the opposite endpoint (context menu "align")
            import Draft
            global_v = obj.getGlobalPlacement().multVec(v)
            p1 = obj.Proxy.get_first_point(obj)
            p2 = obj.Proxy.get_last_point(obj)
            if node_idx == 0:
                current_angle = DraftVecUtils.angle(App.Vector(1,0,0), p1.sub(p2))
                new_angle = DraftVecUtils.angle(App.Vector(1,0,0), global_v.sub(p2))
                Draft.rotate(obj, math.degrees(new_angle - current_angle), p2)
                # obj.Proxy.set_first_point(obj, global_v) # this causes frequent hard crashes, probably to delay
            elif node_idx == 1:
                current_angle = DraftVecUtils.angle(App.Vector(1,0,0), p2.sub(p1))
                new_angle = DraftVecUtils.angle(App.Vector(1,0,0), global_v.sub(p1))
                Draft.rotate(obj, math.degrees(new_angle - current_angle), p1)
                #obj.Proxy.set_last_point(obj, global_v) # this causes frequent hard crashes, probably to delay

    def get_edit_point_context_menu(self, edit_command, obj, node_idx):
        return [
            ("reset end", lambda: self.handle_reset_end(edit_command, obj, node_idx)),
            ("align", lambda: self.handle_align(edit_command, obj, node_idx)),
        ]

    def handle_reset_end(self, edit_command, obj, node_idx):
        obj.Proxy.reset_end(obj, node_idx)
        obj.recompute()

    def handle_align(self, edit_command, obj, node_idx):
        edit_command.alt_edit_mode = 1
        edit_command.startEditing(obj, node_idx)

    def get_edit_obj_context_menu(self, edit_command, obj, position):
        # not supported yet
        return [
        ]
