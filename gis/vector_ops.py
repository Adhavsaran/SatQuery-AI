"""
Vector Operations - Geospatial Vector Analysis

Comprehensive vector spatial operations using GeoPandas and Shapely.
All operations maintain CRS and geometric validity.
"""

from typing import Optional, Union, List, Dict, Tuple
import numpy as np
import geopandas as gpd
from shapely.geometry import box, Point, LineString, Polygon
from shapely.ops import unary_union
from geopandas import GeoDataFrame


class VectorOperations:
    """Vector spatial analysis and operations."""

    def buffer(self, gdf: GeoDataFrame, distance: float, resolution: int = 16,
               dissolve: bool = False, cap_style: str = "round", 
               join_style: str = "round") -> GeoDataFrame:
        """
        Create buffers around vector features.
        
        Args:
            gdf: GeoDataFrame with geometry
            distance: Buffer distance in units of CRS
            resolution: Number of segments per quarter circle
            dissolve: Whether to dissolve into single geometry
            cap_style: 'round', 'flat', or 'square'
            join_style: 'round', 'mitre', or 'bevel'
        
        Returns:
            GeoDataFrame with buffered geometries
        """
        cap_map = {"round": 1, "flat": 2, "square": 3}
        join_map = {"round": 1, "mitre": 2, "bevel": 3}
        
        buffered = gdf.copy()
        buffered.geometry = gdf.geometry.buffer(
            distance, resolution=resolution,
            cap_style=cap_map.get(cap_style, 1),
            join_style=join_map.get(join_style, 1)
        )
        
        if dissolve:
            dissolved = GeoDataFrame(
                {"geometry": [unary_union(buffered.geometry)]},
                crs=gdf.crs
            )
            return dissolved
        
        return buffered

    def clip(self, target_gdf: GeoDataFrame, clip_gdf: GeoDataFrame) -> GeoDataFrame:
        """Clip target layer by clip layer."""
        return gpd.clip(target_gdf, clip_gdf)

    def intersection(self, gdf1: GeoDataFrame, gdf2: GeoDataFrame) -> GeoDataFrame:
        """Compute intersection of two layers."""
        return gpd.overlay(gdf1, gdf2, how="intersection")

    def union(self, gdf1: GeoDataFrame, gdf2: GeoDataFrame) -> GeoDataFrame:
        """Compute union of two layers."""
        return gpd.overlay(gdf1, gdf2, how="union")

    def difference(self, gdf1: GeoDataFrame, gdf2: GeoDataFrame) -> GeoDataFrame:
        """Compute difference (erase) of two layers."""
        return gpd.overlay(gdf1, gdf2, how="difference")

    def symmetric_difference(self, gdf1: GeoDataFrame, gdf2: GeoDataFrame) -> GeoDataFrame:
        """Compute symmetric difference."""
        return gpd.overlay(gdf1, gdf2, how="symmetric_difference")

    def dissolve(self, gdf: GeoDataFrame, by: Optional[str] = None, 
                 aggfunc: str = "first", **agg_dict) -> GeoDataFrame:
        """Dissolve features by attribute field."""
        if by:
            dissolved = gdf.dissolve(by=by, aggfunc=aggfunc, **agg_dict)
        else:
            dissolved = gdf.dissolve()
        return dissolved.reset_index()

    def spatial_join(self, target_gdf: GeoDataFrame, join_gdf: GeoDataFrame,
                     how: str = "left", predicate: str = "intersects",
                     max_distance: Optional[float] = None) -> GeoDataFrame:
        """
        Perform spatial join between two layers.
        
        Args:
            target_gdf: Target layer
            join_gdf: Join layer
            how: 'left', 'right', 'inner', 'outer'
            predicate: 'intersects', 'contains', 'within', etc.
            max_distance: Maximum distance for nearest join
        
        Returns:
            Spatially joined GeoDataFrame
        """
        if max_distance is not None:
            return gpd.sjoin_nearest(target_gdf, join_gdf, how=how, max_distance=max_distance)
        return gpd.sjoin(target_gdf, join_gdf, how=how, predicate=predicate)

    def select_by_location(self, target_gdf: GeoDataFrame, select_gdf: GeoDataFrame,
                           predicate: str = "intersects") -> GeoDataFrame:
        """Select features by spatial relationship."""
        valid_predicates = {
            "intersects", "contains", "within", "touches", "crosses",
            "overlaps", "covers", "covered_by", "disjoint"
        }
        if predicate not in valid_predicates:
            raise ValueError(f"Invalid predicate. Use: {valid_predicates}")
        
        spatial_index = target_gdf.sindex
        possible_matches = list(spatial_index.query(
            select_gdf.geometry.unary_union, predicate=predicate
        ))
        return target_gdf.iloc[possible_matches]

    def calculate_distances(self, gdf1: GeoDataFrame, gdf2: GeoDataFrame) -> np.ndarray:
        """Calculate minimum distances from each feature in gdf1 to gdf2."""
        distances = []
        for geom1 in gdf1.geometry:
            min_dist = min(geom1.distance(geom2) for geom2 in gdf2.geometry)
            distances.append(min_dist)
        return np.array(distances)

    def nearest_neighbor(self, gdf: GeoDataFrame, k: int = 1) -> List[Dict]:
        """
        Find k nearest neighbors for each feature.
        
        Args:
            gdf: GeoDataFrame
            k: Number of neighbors
        
        Returns:
            List of dicts with neighbor info
        """
        results = []
        for idx, geom in enumerate(gdf.geometry):
            distances = [(i, geom.distance(g)) for i, g in enumerate(gdf.geometry) if i != idx]
            distances.sort(key=lambda x: x[1])
            neighbors = distances[:k]
            results.append({
                "feature_idx": idx,
                "neighbors": neighbors
            })
        return results

    def calculate_area(self, gdf: GeoDataFrame) -> np.ndarray:
        """Calculate area of geometries in CRS units."""
        return gdf.geometry.area.values

    def calculate_perimeter(self, gdf: GeoDataFrame) -> np.ndarray:
        """Calculate perimeter of geometries in CRS units."""
        return gdf.geometry.length.values

    def get_centroids(self, gdf: GeoDataFrame) -> GeoDataFrame:
        """Get centroids of geometries."""
        result = gdf.copy()
        result.geometry = gdf.geometry.centroid
        return result

    def get_bounds(self, gdf: GeoDataFrame) -> np.ndarray:
        """Get bounding box for geometries."""
        return gdf.geometry.bounds.values

    def simplify_geometry(self, gdf: GeoDataFrame, tolerance: float) -> GeoDataFrame:
        """Simplify geometries using tolerance."""
        result = gdf.copy()
        result.geometry = gdf.geometry.simplify(tolerance)
        return result
