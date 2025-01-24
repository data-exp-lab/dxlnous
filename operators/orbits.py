import bpy

import numpy as np
import glob
import os


def generate_trees():
    import nodetree_script as ns
    import nodetree_script.api.dynamic.geometry as gs
    import nodetree_script.api.dynamic.shader as ss

    class IndividualOrbit(ns.InputGroup):
        position: ns.Vector
        mass: ns.Float

    @ns.tree("Positions from CSV")
    def positions_from_csv(geometry: ns.Geometry, animation_scale: ns.Float):
        x = gs.named_attribute(name="x").attribute
        y = gs.named_attribute(name="y").attribute
        z = gs.named_attribute(name="z").attribute
        pos = gs.combine_xyz(x=x, y=y, z=z)
        points = gs.set_position(
            geometry=gs.mesh_to_points(mesh=geometry), position=pos
        )
        points = gs.store_named_attribute(
            geometry=points, name="m", value=gs.named_attribute(name="m").attribute
        )
        curves = gs.points_to_curves(points=points)
        mapped_range = gs.map_range(
            value=gs.scene_time().seconds,
            from_min=0,
            from_max=animation_scale,
            to_min=0,
            to_max=1,
        )
        sampled = gs.sample_curve(
            curves=curves,
            value=gs.named_attribute(name="m").attribute,
            factor=mapped_range,
        )
        return {"positions": sampled.position, "mass": sampled.value}

    @ns.tree("Animated Orbit")
    def animated_orbit(geometry: ns.Geometry, radius: ns.Float):
        positions = positions_from_csv(geometry=geometry, animation_scale=10.0)
        return gs.transform_geometry(
            geometry=gs.uv_sphere().mesh, translation=positions.positions
        )


def orbit_load():
    orbit_path = os.path.expanduser("~/dxl/orbit-experiments")

    fns = glob.glob(f"{orbit_path}/orbit_*.csv")

    for obj in bpy.data.objects:
        if obj.name.startswith("CSV_orbit"):
            bpy.data.objects.remove(obj)

    new_objs = []

    import csv_importer.csv

    for fn in sorted(fns):
        obj = csv_importer.csv.load_csv(fn)
        modifier = obj.modifiers.new("GeometryNodes", "NODES")
        modifier.node_group = bpy.data.node_groups["Animated Orbit"]
        new_objs.append(obj)

    # Now we create the collection "Orbits" if it doesn't exist
    if "Orbits" not in bpy.data.collections:
        orbits = bpy.data.collections.new("Orbits")
        bpy.context.scene.collection.children.link(orbits)
    else:
        orbits = bpy.data.collections["Orbits"]

    for obj in new_objs:
        orbits.objects.link(obj)
        if obj.name in bpy.data.collections["Collection"].objects:
            bpy.data.collections["Collection"].objects.unlink(obj)
