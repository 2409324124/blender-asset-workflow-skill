"""Add a removable calibration-meter insert in global X/Y/Z coordinates."""

from math import cos, pi, sin

import bpy


def finish(name, color, roughness, metallic=0.0, glow=0.0, grain=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Emission Color"].default_value = (*color, 1.0)
    shader.inputs["Emission Strength"].default_value = glow
    if grain:
        coordinates = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 240.0
        noise.inputs["Detail"].default_value = 2.0
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = grain
        bump.inputs["Distance"].default_value = 0.004
        links.new(coordinates.outputs["Object"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    return material


def rounded_rectangle(width, height, radius):
    points = []
    for quadrant, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        for step in range(13):
            angle = (quadrant + step / 12) * pi / 2
            points.append((
                sx * (width / 2 - radius) + radius * cos(angle),
                sz * (height / 2 - radius) + radius * sin(angle),
            ))
    return points


def circle(radius, flute=0.0):
    return [
        (r * cos(angle), r * sin(angle))
        for i in range(192)
        for angle in (2 * pi * i / 192,)
        for r in (radius - flute * (0.5 - 0.5 * cos(32 * angle)) ** 2,)
    ]


def profile(name, center, sections, materials, *, ring=False, smooth=False):
    """Loft CCW XZ contours from the rear, then close the solid or rim."""
    x, y, z = center
    count = len(sections[0][1])
    vertices = [(u, depth - y, v) for depth, outline, _ in sections for u, v in outline]
    faces = []
    bands = []
    for layer in range(len(sections) - (0 if ring else 1)):
        first = layer * count
        following = ((layer + 1) % len(sections)) * count
        for i in range(count):
            j = (i + 1) % count
            faces.append((first + i, first + j, following + j, following + i))
            bands.append(sections[layer][2])
    if not ring:
        faces.append(tuple(reversed(range(count))))
        faces.append(tuple(range(len(vertices) - count, len(vertices))))
        bands.extend((sections[0][2], sections[-1][2]))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    part = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(part)
    part.location = (x, y, z)
    for material in materials:
        mesh.materials.append(material)
    side_count = len(faces) if ring else len(faces) - 2
    for face, band in zip(mesh.polygons, bands):
        face.material_index = band
        face.use_smooth = smooth and face.index < side_count
    return part


def rectangle(name, center, sections, materials, *, ring=False):
    return profile(
        name, center,
        [(y, rounded_rectangle(w, h, radius), band)
         for y, w, h, radius, band in sections],
        materials, ring=ring,
    )


def round_part(name, center, sections, materials, *, ring=False):
    return profile(
        name, center,
        [(y, circle(radius, flute), band) for y, radius, flute, band in sections],
        materials, ring=ring, smooth=True,
    )


def build():
    seal = finish("Insert | Graphite gasket", (0.018, 0.024, 0.025), 0.67)
    panel = finish("Insert | Charcoal powder coat", (0.050, 0.066, 0.073), 0.43, grain=0.24)
    metal = finish("Insert | Satin nickel", (0.50, 0.54, 0.55), 0.27, 0.76)
    collar_metal = finish("Selector | Bright satin nickel", (0.65, 0.68, 0.69), 0.34, 0.58)
    channel = finish("Insert | Dark bezel liner", (0.028, 0.043, 0.043), 0.38, 0.20)
    window = finish("Insert | Smoked display", (0.009, 0.021, 0.019), 0.24)
    knob_grip = finish("Insert | Molded selector grip", (0.028, 0.034, 0.034), 0.49, grain=0.31)
    knob_face = finish("Insert | Selector face", (0.051, 0.061, 0.060), 0.46, grain=0.18)
    amber = finish("Insert | Amber indicators", (1.0, 0.37, 0.048), 0.33, glow=0.45)
    pointer = finish("Insert | Amber pointer paint", (0.98, 0.31, 0.032), 0.39, glow=0.10)

    insert = (0, -0.30, 1.37)
    rectangle("Insert | Perimeter gasket", insert, [
        (-0.289, 1.536, 1.966, 0.132, 0),
        (-0.310, 1.560, 1.990, 0.144, 0),
        (-0.328, 1.556, 1.986, 0.142, 0),
    ], [seal])
    rectangle("Insert | Nickel perimeter", insert, [
        (-0.320, 1.534, 1.964, 0.133, 0),
        (-0.337, 1.538, 1.968, 0.135, 0),
        (-0.354, 1.500, 1.930, 0.116, 0),
        (-0.353, 1.459, 1.889, 0.095, 0),
        (-0.322, 1.459, 1.889, 0.095, 0),
    ], [metal], ring=True)
    rectangle("Insert | Chamfered faceplate", insert, [
        (-0.313, 1.493, 1.923, 0.110, 0),
        (-0.347, 1.484, 1.914, 0.106, 0),
        (-0.365, 1.445, 1.875, 0.087, 0),
    ], [panel])

    display = (0, -0.365, 1.845)
    rectangle("Display | Recessed window", display, [
        (-0.362, 1.153, 0.594, 0.068, 0),
        (-0.378, 1.153, 0.594, 0.068, 0),
    ], [window])
    rectangle("Display | Raised nickel bezel and recessed liner", display, [
        (-0.363, 1.229, 0.638, 0.090, 1),
        (-0.395, 1.245, 0.649, 0.097, 0),
        (-0.422, 1.215, 0.624, 0.083, 0),
        (-0.422, 1.143, 0.552, 0.059, 1),
        (-0.407, 1.116, 0.525, 0.046, 1),
        (-0.372, 1.105, 0.514, 0.041, 1),
        (-0.363, 1.105, 0.514, 0.041, 1),
    ], [metal, channel], ring=True)
    baseline = 1.680
    for index, (x, height) in enumerate(zip((-0.272, 0, 0.272), (0.144, 0.253, 0.375)), 1):
        rectangle(f"Display | Amber column {index}", (x, -0.378, baseline + height / 2), [
            (-0.376, 0.164, height - 0.004, 0.016, 0),
            (-0.383, 0.168, height, 0.018, 0),
            (-0.391, 0.160, height - 0.008, 0.014, 0),
        ], [amber])

    dial = (0, -0.365, 0.977)
    round_part("Selector | Seating gasket", dial, [
        (-0.362, 0.425, 0, 0), (-0.374, 0.438, 0, 0),
        (-0.391, 0.425, 0, 0),
    ], [seal])
    round_part("Selector | Turned nickel collar", dial, [
        (-0.379, 0.398, 0, 0), (-0.402, 0.413, 0, 0),
        (-0.423, 0.410, 0, 0), (-0.438, 0.396, 0, 0),
        (-0.440, 0.355, 0, 0), (-0.428, 0.344, 0, 0),
        (-0.379, 0.344, 0, 0),
    ], [collar_metal], ring=True)
    knob = (0, -0.430, dial[2])
    round_part("Selector | Fluted knob", knob, [
        (-0.386, 0.325, 0, 0), (-0.451, 0.337, 0, 0),
        (-0.474, 0.344, 0.006, 0), (-0.557, 0.344, 0.008, 0),
        (-0.582, 0.330, 0.004, 0), (-0.597, 0.310, 0, 0),
        (-0.603, 0.294, 0, 1),
    ], [knob_grip, knob_face])

    # The pointer is inset from the edge and aligned 38 degrees clockwise from Z.
    angle = 38 * pi / 180
    outline = [
        (u * cos(angle) + (v + 0.180) * sin(angle),
         -u * sin(angle) + (v + 0.180) * cos(angle))
        for u, v in rounded_rectangle(0.042, 0.201, 0.006)
    ]
    profile("Selector | Amber pointer", (0, -0.603, dial[2]), [
        (-0.602, outline, 0), (-0.608, outline, 0),
    ], [pointer])

    for x, side in ((-0.666, "left"), (0.666, "right")):
        for z, end in ((0.480, "lower"), (2.260, "upper")):
            center = (x, -0.365, z)
            round_part(f"Insert | {end} {side} captive fastener", center, [
                (-0.363, 0.024, 0, 0), (-0.370, 0.024, 0, 0),
                (-0.376, 0.019, 0, 0),
            ], [metal])
            rectangle(f"Insert | {end} {side} fastener slot", center, [
                (-0.375, 0.026, 0.006, 0.002, 0),
                (-0.377, 0.026, 0.006, 0.002, 0),
            ], [seal])


build()
