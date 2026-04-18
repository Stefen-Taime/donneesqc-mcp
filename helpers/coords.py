"""Conversion de coordonnees EPSG:32198 (Lambert MTQ) <-> EPSG:4326 (WGS84)."""

import logging

from pyproj import Transformer

logger = logging.getLogger(__name__)

# Transformers (thread-safe, reutilisables)
_to_wgs84 = Transformer.from_crs("EPSG:32198", "EPSG:4326", always_xy=True)
_to_lambert = Transformer.from_crs("EPSG:4326", "EPSG:32198", always_xy=True)


def lambert_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """Convertit des coordonnees Lambert MTQ (EPSG:32198) en WGS84 (lon, lat)."""
    lon, lat = _to_wgs84.transform(x, y)
    return round(lon, 7), round(lat, 7)


def wgs84_to_lambert(lon: float, lat: float) -> tuple[float, float]:
    """Convertit des coordonnees WGS84 (lon, lat) en Lambert MTQ (x, y)."""
    x, y = _to_lambert.transform(lon, lat)
    return round(x, 2), round(y, 2)
