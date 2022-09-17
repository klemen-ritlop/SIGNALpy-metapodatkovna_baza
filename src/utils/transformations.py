import math
from dataclasses import dataclass


@dataclass
class Ellipsoid:
    a: float
    f: float

    @property
    def b(self):
        return self.a * (1 - self.f)

    @property
    def ee(self):
        return (self.a**2 - self.b**2) / self.a**2


GRS80 = Ellipsoid(a=6378137.0, f=0.003352810681183637418)
WGS84 = Ellipsoid(a=6378137, f=1 / 298.257223563)
BESSEL = Ellipsoid(a=6377397.155, f=1 / 299.15281285)


def deg2dms(deg: float) -> tuple:
    sign = 1 if deg >= 0 else -1
    deg = abs(deg)

    d = int(deg) * sign
    m = int((deg - d) * 60)
    s = (deg - d - m / 60) * 3600

    return d, m, s


def ecef2geodetic(
    x: float, y: float, z: float, unit: str = "deg", ellipsoid: Ellipsoid = GRS80
) -> dict:

    a = ellipsoid.a
    b = ellipsoid.b
    ee = ellipsoid.ee

    r = math.sqrt(x**2 + y**2)
    var_ee = (a**2 - b**2) / (b**2)
    big_ee = a**2 - b**2
    f = 54 * b**2 * z**2
    g = r**2 + (1 - ee) * z**2 - ee * big_ee
    c = ee**2 * f * r**2 / g**3
    s = (1 + c + math.sqrt(c**2 + 2 * c)) ** (1.0 / 3.0)
    p = f / (3 * (s + 1 / s + 1) ** 2 * g**2)
    q = math.sqrt(1 + 2 * ee**2 * p)
    r0 = -(p * ee * r) / (1 + q) + math.sqrt(
        1 / 2 * a**2 * (1 + 1 / q)
        - (p * (1 - ee) * z**2) / (q * (1 + q))
        - 1 / 2 * p * r**2
    )
    u = math.sqrt((r - ee * r0) ** 2 + z**2)
    v = math.sqrt((r - ee * r0) ** 2 + (1 - ee) * z**2)
    z0 = b**2 * z / (a * v)
    fi_rad = math.atan((z + var_ee * z0) / r)
    la_rad = math.atan2(y, x)
    h = u * (1 - b**2 / (a * v))

    if unit == "dms":
        return {
            "lat": deg2dms(math.degrees(fi_rad)),
            "lon": deg2dms(math.degrees(la_rad)),
            "h": h,
        }

    if unit == "rad":
        return {
            "lat": fi_rad,
            "lon": la_rad,
            "h": h,
        }

    return {"lat": math.degrees(fi_rad), "lon": math.degrees(la_rad), "h": h}
