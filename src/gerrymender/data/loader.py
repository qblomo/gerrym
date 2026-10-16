from pathlib import Path
import geopandas as gpd

EXPECTED_EPSG = 4269


def load_districts(file_path: Path) -> gpd.GeoDataFrame:
    """
    Load district boundaries from a file.

    Args:
        file_path: Path to the file containing district boundaries.

    Returns:
        A GeoDataFrame containing the district boundaries in the CRS defined by EXPECTED_EPSG.

    Raises:
        ValueError: If the file has no CRS.
        ValueError: If the CRS is not the EXPECTED_EPSG.
    """
    gdf = gpd.read_file(file_path)
    if gdf.crs is None:
        raise ValueError(
            "The GeoDataFrame does not have a coordinate reference system (CRS)."
        )
    if gdf.crs.to_epsg() != EXPECTED_EPSG:
        raise ValueError(f"Expected CRS EPSG:{EXPECTED_EPSG}, but got {gdf.crs.name}.")
    return gdf
