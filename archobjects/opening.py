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
"""Provide the object code for Arch Opening object."""
## @package opening
# \ingroup ARCH
# \brief Provide the object code for Arch Opening object.

import FreeCAD as App

import DraftVecUtils

from archobjects.base import ShapeGroup
from ArchIFC import IfcProduct

import archobjects.window_presets as window_presets

class Opening(ShapeGroup, IfcProduct):
    def __init__(self, obj=None):
        super(Opening, self).__init__(obj)
        self.Object = obj
        if obj:
            self.attach(obj)


    def attach(self, obj):
        ShapeGroup.attach(self, obj)
        self.set_properties(obj)
   

    def execute(self, obj):
        import Part

        shapes_collection = []

        # ADDITIONS
        a_shape = self.get_addition_shape(obj)
        if a_shape:
            shapes_collection.append(a_shape)

        # FILLING
        f_shape = self.get_fill_shape(obj)
        if f_shape:
            shapes_collection.append(f_shape)

        # create object positive shape
        if len(shapes_collection) > 0:
            obj.Shape = Part.makeCompound(shapes_collection)
        else:
            obj.Shape = Part.Shape()

        # VOID
        vs = self.get_void_shape(obj)

        # create object negative shape
        if vs:
            obj.VoidShape = vs

    def set_properties(self, obj):
        """ Setup object properties.
        """
    
        # Ifc Properties ----------------------------------------------------
        IfcProduct.setProperties(self, obj)
        obj.IfcType = "Opening Element"

        # COMPONENTS - ADDITIONS (not implemented yet) ----------------------------
        _tip = 'List of available shapes for the opening Additions.\n'\
               'Chose Custom to use the Addition Elements objects shape.'
        obj.addProperty('App::PropertyEnumeration', 'Addition', 
                        'Component - Additions', _tip).Addition = ["None", "Default Sill", "Custom"]

        _tip = 'List of objects to be merged into the opening shape.'
        obj.addProperty('App::PropertyLinkListChild', 'AdditionElements', 
                        'Component - Additions', _tip)
        obj.setPropertyStatus("AdditionElements", 2)

        _tip = 'Chose if the Addition Elements have to be individually displayed or\n'\
               'merged into the Opening object shape.'
        obj.addProperty('App::PropertyEnumeration', 'AdditionMode', 
                        'Component - Additions', _tip).AdditionMode = ["Embed Shape", "Display Children"]

        # COMPONENTS - FILLING Properties (Windows, doors) ----------------------------
        _tip = 'List of available shapes for the Fill element.\n'\
               'Chose Custom to use the Fill Element object shape.'
        obj.addProperty('App::PropertyEnumeration', 'Fill', 
                        'Component - Filling', _tip).Fill = ["None", "Default Door", "Default Window", "By Sketch", "Custom"]

        _tip = 'Alignment of the Fill Element according to the Host Thickness property.'
        obj.addProperty('App::PropertyEnumeration', 'FillAlignment', 
                        'Component - Filling', _tip).FillAlignment = ["Left", "Center", "Right"]
        obj.FillAlignment = "Right"

        _tip = 'Offset of the Fill Element from the chosen Fill Alignment.'
        obj.addProperty('App::PropertyDistance', 'FillDisplacement', 
                        'Component - Filling', _tip).FillDisplacement = 0.0

        _tip = 'Link the door or the window that you want to insert into the opening.'
        obj.addProperty('App::PropertyLinkGlobal', 'FillElement', 
                        'Component - Filling', _tip)

        _tip = 'Chose if the Fill Element have to be individually displayed or\n'\
               'merged into the Opening object shape.'
        obj.addProperty('App::PropertyEnumeration', 'FillMode', 
                        'Component - Filling', _tip).FillMode = ["Embed Shape", "Display Child"]

        # COMPONENTS - VOID Properties (not implemented yet) ----------------------------
        _tip = 'List of available shapes of the Opening void.\n'\
               'Chose Custom to use the Void Element object shape.'
        obj.addProperty('App::PropertyEnumeration', 'Void', 
                        'Component - Void', _tip).Void = ["Rectangular", "Arc", "Custom"]

        _tip = 'Ponter to the object that will be used to cut the wall.\n'\
               'To use it, set Void property to Custom'
        obj.addProperty('App::PropertyLinkGlobal', 'VoidElement', 
                        'Component - Void', _tip)

        _tip = 'Subtract also positive shapes from the wall.'
        obj.addProperty('App::PropertyBool', 'VoidSubtractAll', 
                        'Component - Void', _tip).VoidSubtractAll = False

        _tip = 'This property stores the shape of the Void object to be subtracted from the host.'
        obj.addProperty('Part::PropertyPartShape', 'VoidShape', 
                    'Base', _tip)

        # Geometry Properties (not implemented yet) ----------------------------
        _tip = 'Architectural Width of the opening object'
        obj.addProperty('App::PropertyLength', 'OpeningWidth', 
                        'Geometry', _tip).OpeningWidth = 800
        _tip = 'Architectural Height of the opening object'
        obj.addProperty('App::PropertyLength', 'OpeningHeight', 
                        'Geometry', _tip).OpeningHeight = 1500
        _tip = 'Thickness of the hosted object.\n'\
               'This property is set by the hosting wall on creation'
        obj.addProperty('App::PropertyLength', 'HostThickness', 
                        'Geometry', _tip).HostThickness = 500
        _tip = 'Propagate geometry properties to opening childrens'
        obj.addProperty('App::PropertyBool', 'PropagateGeometry', 
                        'Geometry', _tip).PropagateGeometry = False


    def onDocumentRestored(self, obj):
        self.Object = obj


    def onChanged(self, obj, prop):
        """This method is activated when a property changes.
        """
        super(Opening, self).onChanged(obj, prop)

        if 'Addition' in obj.PropertiesList and prop == 'Addition':
            if obj.Addition != "Custom" and 'AdditionElements' in obj.PropertiesList:
                obj.setPropertyStatus("AdditionElements", 2)
            elif 'AdditionElements' in obj.PropertiesList:
                obj.setPropertyStatus("AdditionElements", -2)

        if 'AdditionElements' in obj.PropertiesList and prop == 'AdditionElements':
            pass

        if 'Fill' in obj.PropertiesList and prop == 'Fill':
            self.remove_filling_properties(obj)
            self.setup_filling_properties(obj)

        if 'Void' in obj.PropertiesList and prop == 'Void':
            pass

        if 'VoidElement' in obj.PropertiesList and prop == 'VoidElement':
            pass


    def remove_filling_properties(self, obj):
        """Remove properties for Filling when not used.
        """
        for property in obj.PropertiesList:
            if obj.getGroupOfProperty(property) != "Component - Filling - Options":
                continue
            obj.removeProperty(property)   

    def setup_filling_properties(self, obj):
        if obj.Fill == "None":
            return
        if obj.Fill == "Default Window":
            self.add_default_window_properties(obj)
        if obj.Fill == "Default Door":
            self.add_default_door_properties(obj)

    def add_default_window_properties(self, obj):
        _tip = 'Alignment of the Fill Element according to the Host Thickness property.'
        obj.addProperty('App::PropertyEnumeration', 'FillType', 
                        'Component - Filling - Options', _tip).FillType = ["Rectangular"]

        _tip = 'Number of openable frames. Set 0 for a fixed window.'
        obj.addProperty('App::PropertyInteger', 'NumberOfPanes', 
                        'Component - Filling - Options', _tip).NumberOfPanes = 1

        _tip = 'DESCRIBE.'
        obj.addProperty('App::PropertyLength', 'FrameWidth', 
                        'Component - Filling - Options', _tip).FrameWidth = 50.0

        _tip = 'DESCRIBE.'
        obj.addProperty('App::PropertyLength', 'FrameThickness', 
                        'Component - Filling - Options', _tip).FrameThickness = 50.0

        _tip = 'DESCRIBE.'
        obj.addProperty('App::PropertyLength', 'GlassThickness', 
                        'Component - Filling - Options', _tip).GlassThickness = 20.0

        _tip = 'DESCRIBE.'
        obj.addProperty('App::PropertyLength', 'IncreaseHeight', 
                        'Component - Filling - Options', _tip).IncreaseHeight = 0.0

        _tip = 'DESCRIBE.'
        obj.addProperty('App::PropertyLength', 'IncreaseWidth', 
                        'Component - Filling - Options', _tip).IncreaseWidth = 0.0

    def add_default_door_properties(self, obj):
        pass

    # ADDITIONS ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def get_addition_shape(self, obj):
        if 'Addition' in obj.PropertiesList and obj.Addition == "None":
            return None

        elif 'Addition' in obj.PropertiesList and obj.Addition == "Default Sill":
            return self.get_default_sill_shape(obj)

        elif 'Addition' in obj.PropertiesList and obj.Addition == "Custom":
            return None

        return None


    def get_default_sill_shape(self, obj):
        
        return window_presets.default_sill(opening_width=obj.OpeningWidth.Value,
                                           host_thickness=obj.HostThickness.Value,
                                           sill_thickness=50.0,
                                           front_protrusion=50.0,
                                           lateral_protrusion=50.0,
                                           inner_covering=30.0)


    # FILLING ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    def get_fill_shape(self, obj):
        """Return a shape representing the fill of the Opening object, 
        being it for example a window, a door, a custom fill or just None.
        """
        f_shape = None
        if 'Fill' in obj.PropertiesList and obj.Fill == "None":
            f_shape = None

        elif 'Fill' in obj.PropertiesList and obj.Fill == "Default Door":
            f_shape = self.get_default_door_shape(obj)

        elif 'Fill' in obj.PropertiesList and obj.Fill == "Default Window":
            f_shape = self.get_default_window_shape(obj)

        elif 'Fill' in obj.PropertiesList and obj.Fill == "By Sketch":
            f_shape = self.get_fill_by_sketch(obj)

        elif 'Fill' in obj.PropertiesList and obj.Fill == "Custom":
            if 'FillElement' in obj.PropertiesList and obj.FillElement:
                if 'Shape' in obj.FillElement.PropertiesList and not obj.FillElement.Shape.isNull():
                    if 'FillMode' in obj.PropertiesList and obj.FillMode == "Embed Shape":
                        # if FillMode is "Embed Shape" look for a shape to return
                        f_shape = obj.FillElement.Shape.copy()
                    elif 'FillMode' in obj.PropertiesList and obj.FillMode == "Display Child":
                        # if FillMode is "Display Child" return None cause the children will be visible by itself
                        # BUG: This option does not work so good.
                        f_shape = None

        if f_shape:
            # set the correct placement of filling shape according to alignement and displacement
            if obj.FillAlignment == "Left":
                f_shape.Placement.Base.y = obj.HostThickness.Value/2
            elif obj.FillAlignment == "Center":
                pass
            elif obj.FillAlignment == "Right":
                f_shape.Placement.Base.y = -obj.HostThickness.Value/2
            f_shape.Placement.Base.y += obj.FillDisplacement.Value
            return f_shape
        else:
            return None


    def get_default_door_shape(self, obj):
        import Part

        if (not 'OpeningWidth' in obj.PropertiesList or
            not 'OpeningHeight' in obj.PropertiesList):
            return None
        f = Part.makeBox(obj.OpeningWidth,60,obj.OpeningHeight)
        m = App.Matrix()
        m.move(-obj.OpeningWidth/2, 0, 0)
        f = f.transformGeometry(m)
        return f


    def get_default_window_shape(self, obj):
        import Part

        if (not 'OpeningWidth' in obj.PropertiesList or
            not 'OpeningHeight' in obj.PropertiesList):
            return None

        return window_presets.window_rectangular(obj.HostThickness.Value,
                                                 obj.OpeningHeight.Value + obj.IncreaseHeight.Value,
                                                 obj.OpeningWidth.Value + obj.IncreaseWidth.Value,
                                                 frame_width=obj.FrameWidth.Value,
                                                 frame_th=obj.FrameThickness.Value,
                                                 glass_th=obj.GlassThickness.Value,
                                                 n_pan=obj.NumberOfPanes)


    def get_fill_by_sketch(self, obj):
        #TODO: To be implemented
        pass


    # VOID ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def get_void_shape(self, obj):
        import Part
        void = None
        if obj.Void == "Rectangular":
            if obj.Addition == "None":
                void = self.get_rectangular_void(obj)
            if obj.Addition == "Default Sill":
                void = self.get_rectangular_void(obj)

        if obj.VoidSubtractAll:
            # subtract also positive shapes from the wall
            ps = []
            for s in obj.Shape.Solids:
                ps.append(s.copy())
            void = void.fuse(ps)

        return void

    def get_rectangular_void(self, obj):
        import Part
        void = Part.makeBox(obj.OpeningWidth.Value, obj.HostThickness.Value + 50, obj.OpeningHeight.Value)
        void.Placement.Base.x -= obj.OpeningWidth.Value/2
        void.Placement.Base.y -= obj.HostThickness.Value/2
        void.Placement = obj.Placement.multiply(void.Placement)
        return void