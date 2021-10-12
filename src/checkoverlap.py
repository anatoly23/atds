from math import tan
from geographiclib.geodesic import Geodesic


def if_overlap(point_lat: float, point_long: float, point_height: float, lat: float, long: float, radkon: float,
               angelcon: float, heightkon: float) -> bool:
    geod = Geodesic.WGS84
    distance = geod.Inverse(point_lat, point_long, lat, long)
    if distance['s12'] > radkon:
        return False
    katet_b = distance['s12'] * tan(angelcon)
    if katet_b + heightkon >= point_height:
        return False
    return True
