"""Small closed solids from corresponding convex XY contours at increasing Z."""
from bisect import bisect_right
from dataclasses import dataclass
from math import dist, isfinite, ulp


def _points(loop):
    points = tuple(tuple(float(v) for v in point) for point in loop)
    if len(points) < 3 or any(len(p) != 2 or not all(map(isfinite, p)) for p in points):
        raise ValueError("expected at least three finite XY points")
    return points


def _check_convex_ccw(points):
    # Every other corner must lie to the left of each directed edge. A local
    # turning test alone would admit star polygons with crossing edges.
    span = max(max(axis) - min(axis) for axis in zip(*points))
    if not isfinite(span) or span == 0:
        raise ValueError("contour needs finite extent")
    pts = [((x - points[0][0]) / span, (y - points[0][1]) / span) for x, y in points]
    for i, (ax, ay) in enumerate(pts):
        j = (i + 1) % len(pts)
        bx, by = pts[j]
        for k, (cx, cy) in enumerate(pts):
            if k not in (i, j) and (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) <= 1e-12:
                raise ValueError("expected a strictly convex counterclockwise contour")


@dataclass(frozen=True)
class SectionLoft:
    """Each (z, contour) shares corner zero, winding and semantic corner order."""
    stations: tuple

    def __post_init__(self):
        stations = tuple((float(z), _points(loop)) for z, loop in self.stations)
        if len(stations) < 2:
            raise ValueError("expected at least two stations")
        for i, (z, loop) in enumerate(stations):
            if not isfinite(z) or (i and z <= stations[i - 1][0]):
                raise ValueError("station heights must be finite and strictly increasing")
            if len(loop) != len(stations[0][1]):
                raise ValueError("inconsistent corner counts")
            _check_convex_ccw(loop)
        object.__setattr__(self, "stations", stations)

    def mesh(self):
        """Return vertices and outward faces suitable for Mesh.from_pydata."""
        n = len(self.stations[0][1])
        vertices = [(x, y, z) for z, loop in self.stations for x, y in loop]
        faces = [tuple(reversed(range(n)))]
        for ring in range(len(self.stations) - 1):
            for i in range(n):
                a = ring * n + i
                b = ring * n + (i + 1) % n
                # A taper can make a side nonplanar. Fix its diagonal once.
                faces.extend([(a, b, b + n), (a, b + n, a + n)])
        faces.append(tuple(range(len(vertices) - n, len(vertices))))
        return vertices, faces

    def svg(self):
        """Return an XY section overlay with station heights in polygon titles."""
        xs, ys = zip(*(p for _, loop in self.stations for p in loop))
        width, height = max(xs) - min(xs), max(ys) - min(ys)
        span = max(width, height)
        padding = span * 0.05
        lines = [
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{min(xs)-padding} {-max(ys)-padding} {width+2*padding} {height+2*padding}">',
            '<title>Section contours viewed along the station axis</title>',
        ]
        for i, (z, loop) in enumerate(self.stations):
            points = ' '.join(f'{x},{-y}' for x, y in loop)
            hue = round(240 * i / (len(self.stations) - 1))
            lines.append(f'<polygon points="{points}" fill="none" stroke="hsl({hue},65%,38%)" '
                         f'stroke-width="{span * .005}"><title>z = {z}</title></polygon>')
        return '\n'.join([*lines, '</svg>'])


def perimeter_samples(loop, count, phase=0.0):
    """Return (point, unit tangent) at equal arc intervals on a closed 2D polyline.

    Phase is a fraction of the entire perimeter. Exact corners use the outgoing
    edge. A self-crossing path retains its input traversal order.
    """
    points = _points(loop)
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("count must be a positive integer")
    if not isfinite(phase) or not 0 <= phase < 1:
        raise ValueError("phase must be in [0, 1)")
    ends = []
    tangents = []
    total = 0.0
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        length = dist(a, b)
        if not isfinite(total + length) or total + length <= total:
            raise ValueError("edge length must be finite and measurable")
        total += length
        ends.append(total)
        tangents.append(((b[0] - a[0]) / length, (b[1] - a[1]) / length))
    samples = []
    for i in range(count):
        arc = (((phase + i / count) % 1.0) * total) % total
        edge = bisect_right(ends, arc)
        start = ends[edge - 1] if edge else 0.0
        stop = ends[edge]
        # A rational sample such as 12/94 may round just short of a corner.
        # Bound the snap by the current edge as well as the circuit precision.
        tolerance = min(4 * ulp(total), (stop - start) / 8)
        offset = arc - start
        if offset <= tolerance:
            offset = 0.0
        elif stop - arc <= tolerance:
            edge = (edge + 1) % len(points)
            offset = 0.0
        a = points[edge]
        dx, dy = tangents[edge]
        samples.append(((a[0] + dx * offset, a[1] + dy * offset), (dx, dy)))
    return samples
