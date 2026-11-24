"""Build the removable calibration controls on the active factory collection.

World coordinates are X across, Z up, and negative Y toward the operator.
The perimeter is 1.56 by 1.99, centered at X=0, Z=1.37.
"""

import math

import bpy


def material(name, color, roughness, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if emission:
        shader.inputs["Emission Color"].default_value = (*color, 1.0)
        shader.inputs["Emission Strength"].default_value = emission
    return mat


def rectangle(width, height, radius, y, z, x=0.0, rotation=0.0):
    """A rounded profile with consistent corner correspondence across sections."""
    points = []
    half_w, half_h = width / 2 - radius, height / 2 - radius
    corners = [(half_w, half_h), (-half_w, half_h),
               (-half_w, -half_h), (half_w, -half_h)]
    c, s = math.cos(rotation), math.sin(rotation)
    for corner, (cx, cz) in enumerate(corners):
        for step in range(9):
            angle = (corner + step / 8) * math.pi / 2
            u = cx + radius * math.cos(angle)
            v = cz + radius * math.sin(angle)
            points.append((x + c * u + s * v, y, z - s * u + c * v))
    return points


def circle(radius, y, x, z, fluting=0.0):
    points = []
    for i in range(192):
        angle = math.tau * i / 192
        r = radius - fluting * (0.5 + 0.5 * math.cos(32 * angle)) ** 2
        points.append((x + r * math.cos(angle), y, z + r * math.sin(angle)))
    return points


def profile_mesh(name, loops, finishes, *, ring=False, origin=(0.0, 0.0, 0.0)):
    """Loft closed profiles from rear to front, then inward for open rings."""
    size = len(loops[0])
    vertices = [(x - origin[0], y - origin[1], z - origin[2])
                for loop in loops for x, y, z in loop]
    bands = len(loops) if ring else len(loops) - 1
    faces = []
    for band in range(bands):
        a = band * size
        b = ((band + 1) % len(loops)) * size
        for i in range(size):
            j = (i + 1) % size
            faces.append((a + i, a + j, b + j, b + i))
    if not ring:
        faces.extend([tuple(reversed(range(size))),
                      tuple(range(len(vertices) - size, len(vertices)))])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = origin
    for mat in dict.fromkeys(finishes):
        mesh.materials.append(mat)
    for face in mesh.polygons:
        finish = finishes[min(face.index // size, bands - 1)]
        face.material_index = mesh.materials.find(finish.name)
    return obj


def build_insert():
    frame = material("Controls | satin nickel perimeter", (0.56, 0.61, 0.62), 0.32, 0.54)
    graphite = material("Controls | graphite face", (0.052, 0.071, 0.080), 0.40, 0.20)
    edge = material("Controls | anodized chamfer", (0.085, 0.108, 0.113), 0.33, 0.48)
    seal = material("Controls | black seating gasket", (0.012, 0.019, 0.019), 0.55)
    lens = material("Controls | smoked display", (0.012, 0.034, 0.032), 0.25, 0.17)
    alloy = material("Controls | bright machined alloy", (0.67, 0.72, 0.72), 0.30, 0.55)
    grip = material("Controls | molded grip", (0.021, 0.029, 0.028), 0.54)
    cap = material("Controls | selector cap", (0.048, 0.059, 0.056), 0.42)
    amber = material("Controls | amber display segments", (0.94, 0.31, 0.040), 0.31, emission=0.55)
    index = material("Controls | amber index", (0.95, 0.32, 0.042), 0.33)

    center = 1.37
    display_z = 1.854
    selector_z = 0.988

    profile_mesh("Insert perimeter", [
        rectangle(1.526, 1.956, 0.129, -0.286, center),
        rectangle(1.560, 1.990, 0.146, -0.316, center),
        rectangle(1.560, 1.990, 0.146, -0.358, center),
        rectangle(1.540, 1.970, 0.136, -0.380, center),
        rectangle(1.502, 1.932, 0.117, -0.380, center),
        rectangle(1.484, 1.914, 0.108, -0.365, center),
        rectangle(1.484, 1.914, 0.108, -0.286, center),
    ], [seal, frame, frame, frame, alloy, seal, seal], ring=True)

    # The faceplate wraps around a real through-opening for the display.
    profile_mesh("Chamfered graphite faceplate", [
        rectangle(1.496, 1.926, 0.115, -0.330, center),
        rectangle(1.496, 1.926, 0.115, -0.379, center),
        rectangle(1.457, 1.887, 0.096, -0.408, center),
        rectangle(1.265, 0.628, 0.099, -0.408, display_z),
        rectangle(1.238, 0.601, 0.086, -0.385, display_z),
        rectangle(1.238, 0.601, 0.086, -0.330, display_z),
    ], [graphite, edge, graphite, seal, seal, graphite], ring=True)

    profile_mesh("Display bezel", [
        rectangle(1.233, 0.595, 0.083, -0.349, display_z),
        rectangle(1.244, 0.606, 0.088, -0.409, display_z),
        rectangle(1.218, 0.580, 0.075, -0.438, display_z),
        rectangle(1.158, 0.520, 0.057, -0.438, display_z),
        rectangle(1.129, 0.491, 0.045, -0.407, display_z),
        rectangle(1.129, 0.491, 0.045, -0.349, display_z),
    ], [seal, alloy, frame, edge, seal, seal], ring=True)

    profile_mesh("Recessed smoked display bed", [
        rectangle(1.144, 0.506, 0.052, -0.325, display_z),
        rectangle(1.144, 0.506, 0.052, -0.384, display_z),
        rectangle(1.126, 0.488, 0.043, -0.397, display_z),
    ], [seal, lens])

    baseline = display_z - 0.157
    for number, (x, height) in enumerate(zip((-0.270, 0.0, 0.270),
                                             (0.136, 0.242, 0.360)), 1):
        z = baseline + height / 2
        profile_mesh(f"Amber display column {number}", [
            rectangle(0.169, height, 0.021, -0.395, z, x),
            rectangle(0.169, height, 0.021, -0.406, z, x),
            rectangle(0.157, height - 0.012, 0.015, -0.412, z, x),
        ], [amber, amber])

    profile_mesh("Selector seating gasket", [
        circle(0.435, -0.401, 0, selector_z),
        circle(0.442, -0.417, 0, selector_z),
        circle(0.428, -0.446, 0, selector_z),
    ], [seal, seal])

    profile_mesh("Machined selector collar", [
        circle(0.413, -0.432, 0, selector_z),
        circle(0.426, -0.454, 0, selector_z),
        circle(0.412, -0.484, 0, selector_z),
        circle(0.355, -0.487, 0, selector_z),
        circle(0.340, -0.471, 0, selector_z),
        circle(0.340, -0.432, 0, selector_z),
    ], [frame, alloy, alloy, alloy, edge, frame], ring=True)

    knob = profile_mesh("Fluted selector knob", [
        circle(0.333, -0.437, 0, selector_z),
        circle(0.349, -0.477, 0, selector_z, 0.006),
        circle(0.350, -0.527, 0, selector_z, 0.010),
        circle(0.347, -0.578, 0, selector_z, 0.010),
        circle(0.333, -0.602, 0, selector_z, 0.004),
        circle(0.308, -0.618, 0, selector_z),
        circle(0.296, -0.622, 0, selector_z),
    ], [grip, grip, grip, grip, grip, cap], origin=(0, -0.437, selector_z))
    for face in knob.data.polygons:
        face.use_smooth = face.loop_total == 4

    angle = math.radians(39)
    x = 0.181 * math.sin(angle)
    z = selector_z + 0.181 * math.cos(angle)
    pointer = profile_mesh("Selector amber pointer", [
        rectangle(0.048, 0.214, 0.005, -0.620, z, x, angle),
        rectangle(0.048, 0.214, 0.005, -0.628, z, x, angle),
        rectangle(0.041, 0.207, 0.003, -0.632, z, x, angle),
    ], [index, index], origin=tuple(knob.location))
    pointer.parent = knob
    pointer.location = (0, 0, 0)

    for x, side in [(-0.677, "left"), (0.677, "right")]:
        for z, level in [(0.479, "lower"), (2.261, "upper")]:
            profile_mesh(f"Faceplate screw | {level} {side}", [
                circle(0.030, -0.404, x, z),
                circle(0.030, -0.419, x, z),
                circle(0.024, -0.426, x, z),
            ], [edge, alloy])
            profile_mesh(f"Screw drive | {level} {side}", [
                rectangle(0.033, 0.007, 0.002, -0.425, z, x, 0.4),
                rectangle(0.033, 0.007, 0.002, -0.427, z, x, 0.4),
            ], [seal])


build_insert()
