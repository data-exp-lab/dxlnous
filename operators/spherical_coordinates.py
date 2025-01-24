import bpy


class SphericalCoordintesOperator(bpy.types.Operator):
    bl_idname = "object.spherical_coordinates"
    bl_label = "spherical_coordinates"

    def execute(self, context: bpy.types.Context):
        import nodetree_script as ns
        import nodetree_script.api.dynamic.geometry as gs

        @ns.tree("Spherical Coordinates")
        def spherical_coordinates(positions: ns.Vector):
            r = gs.length(positions)
            pos = gs.position()
            theta = gs.math(operation=gs.Math.Operation.ARCCOSINE, value=pos.z / r)
            phi = gs.math(operation=gs.Math.Operation.ARCTAN2, value=(pos.y, pos.x))
            return gs.combine_xyz(x=r, y=theta, z=phi)

        return {"FINISHED"}
