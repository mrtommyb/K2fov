"""Tests the functionality specific to the K2C9 microlensing campaign."""
from .. import c9


def test_point_inside_polygon():
    """Basic test of c9.isPointInsidePolygon()"""
    vertices_x = [+1, +1, -1, -1]
    vertices_y = [+1, -1, -1, +1]
    # Simple cases
    for x, y in [(0, 0), (0.5, -0.5), (-0.5, 0.5)]:
        assert(c9.isPointInsidePolygon(x, y, vertices_x, vertices_y))
    for x, y in [(2, 2), (1.5, -0.5), (0.5, 1.5)]:
        assert(not c9.isPointInsidePolygon(x, y, vertices_x, vertices_y))
    # Edge cases
    for x, y in [(0.999, 0.999), (0.999, -0.999), (-0.999, 0.999)]:
        assert(c9.isPointInsidePolygon(x, y, vertices_x, vertices_y))
    for x, y in [(1.001, 0), (0, 1.001), (-1.001, 0.999)]:
        assert(not c9.isPointInsidePolygon(x, y, vertices_x, vertices_y))


def test_in_microlens_region():
    """Basic test of c9.inMicrolensRegion()"""
    # The following coordinates are well within the superstamp
    # according to plots circulated by Radek on the K2C9 mailing list
    for ra, dec in [(269.5, -28.5), (271, -28.2), (268.5, -28.5),
                    (269.9, -27.5), (271.2, -27.2), (269.2, -28.8)]:
        assert(c9.inMicrolensRegion(ra, dec))
        # All coordinates 5 degrees away are not in the superstamp
        assert(not c9.inMicrolensRegion(ra - 5, dec))
        assert(not c9.inMicrolensRegion(ra + 5, dec))
        assert(not c9.inMicrolensRegion(ra, dec - 5))
        assert(not c9.inMicrolensRegion(ra, dec + 5))

    # The coordinates below are also definitely not inside the region
    for ra, dec in [(0, 0), (0, +90), (90, -45), (270, +45)]:
        assert(not c9.inMicrolensRegion(ra, dec))
