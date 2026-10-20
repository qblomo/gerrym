import geopandas as gpd

ANALYSIS_EPSG = 5070
# EPSG:5070 is the Albers equal-area conic projection


def project_to_analysis_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Project a GeoDataFrame to the analysis CRS from ANALYSIS_EPSG.

    Not suitable for Alaska and Hawaii, where this projection distorts areas strongly.

    Args:
        gdf: GeoDataFrame in any defined CRS, with geometries located in the 48 contiguous states.

    Returns:
        A GeoDataFrame with the CRS from ANALYSIS_EPSG without changing the input.

    Raises:
        ValueError: If gdf has no CRS.
    """
    if gdf.crs is None:
        raise ValueError(
            "The GeoDataFrame does not have a coordinate reference system (CRS)."
        )
    return gdf.to_crs(epsg=ANALYSIS_EPSG)
