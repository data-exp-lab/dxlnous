import bpy
import cmyt
import matplotlib.pyplot as plt
import numpy as np
from . import orbits


class Load_colormapsOperator(bpy.types.Operator):
    bl_idname = "object.load_colormaps"
    bl_label = "load_colormaps"

    def execute(self, context):
        # orbits.orbit_load()
        orbits.generate_trees()
        vals = np.mgrid[0.0:1.0:256j]

        for cmap_name in cmyt._utils.cmyt_cmaps:
            arr = np.zeros((256, 64, 4), dtype="f4")
            if f"cmyt_{cmap_name}" not in bpy.data.images:
                img = bpy.data.images.new(
                    f"cmyt_{cmap_name}", 64, 256, alpha=False, float_buffer=True
                )
            else:
                img = bpy.data.images[f"cmyt_{cmap_name}"]
            cmap = plt.cm.ScalarMappable(cmap=plt.get_cmap(f"cmyt.{cmap_name}"))
            cmap.set_clim(0.0, 1.0)
            arr[:] = cmap.to_rgba(vals).astype("f4")[:, None, :]
            img.pixels.foreach_set(arr.ravel(order="C"))

        import nodetree_script as ns
        import nodetree_script.api.dynamic.geometry as gs
        import nodetree_script.api.dynamic.shader as ss

        @ns.materialtree("Apply Colormap")
        def apply_colormap():
            mi = ss.attribute(
                attribute_type=ss.Attribute.AttributeType.INSTANCER,
                attribute_name="cm_min",
            ).fac
            ma = ss.attribute(
                attribute_type=ss.Attribute.AttributeType.INSTANCER,
                attribute_name="cm_max",
            ).fac
            value = ss.attribute(
                attribute_type=ss.Attribute.AttributeType.GEOMETRY,
                attribute_name="cm_value",
            ).fac
            normalized = ss.map_range(
                data_type=ss.MapRange.DataType.FLOAT,
                value=value,
                from_min=mi,
                from_max=ma,
                to_min=0.0,
                to_max=1.0,
            )
            vec = ss.combine_xyz(x=0.5, y=normalized, z=1.0)
            image_texture = ss.image_texture(vector=vec)
            return ss.principled_bsdf(base_color=image_texture.color)

        @ns.tree("Colormapped Mesh")
        def colormapped_mesh(geometry: ns.Geometry, property_name: ns.String):
            stored = gs.store_named_attribute(
                data_type=gs.StoreNamedAttribute.DataType.FLOAT,
                name="cm_value",
                domain=gs.StoreNamedAttribute.Domain.POINT,
                value=gs.named_attribute(name=property_name).attribute,
                geometry=geometry,
            )
            stats = gs.attribute_statistic(
                geometry=stored, attribute=gs.named_attribute(name="cm_value").attribute
            )
            instances = gs.geometry_to_instance(geometry=[stored])
            stored = gs.store_named_attribute(
                data_type=gs.StoreNamedAttribute.DataType.FLOAT,
                name="cm_min",
                domain=gs.StoreNamedAttribute.Domain.INSTANCE,
                value=stats.min,
                geometry=instances,
            )
            stored = gs.store_named_attribute(
                data_type=gs.StoreNamedAttribute.DataType.FLOAT,
                name="cm_max",
                domain=gs.StoreNamedAttribute.Domain.INSTANCE,
                value=stats.max,
                geometry=stored,
            )
            return gs.set_material(geometry=stored, material=apply_colormap)

        return {"FINISHED"}


class DXLNousPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_dxlnous"
    bl_label = "DXL Nous"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"

    def draw(self, context):
        self.layout.label(text="DXL Nous")
        self.layout.row().operator("object.load_colormaps")
        self.layout.row().operator("object.spherical_coordinates")
