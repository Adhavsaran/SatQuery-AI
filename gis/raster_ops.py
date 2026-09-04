"""
Raster Operations - Geospatial Raster Analysis

Comprehensive raster data operations using Rasterio and GDAL.
All operations maintain CRS and spatial reference.
"""

from typing import Optional, Union, List, Tuple, Dict
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.merge import merge as rio_merge
from rasterio.transform import from_bounds
from rasterio.crs import CRS
from pathlib import Path


class RasterOperations:
    """Raster spatial analysis and operations."""

    @staticmethod
    def read_raster(path: Union[str, Path]) -> Tuple[np.ndarray, dict, rasterio.DatasetReader]:
        """
        Read raster file.
        
        Args:
            path: Path to raster file
        
        Returns:
            Tuple of (data array, metadata dict, dataset)
        """
        path = str(path)
        with rasterio.open(path) as src:
            data = src.read()
            metadata = {
                'crs': src.crs,
                'transform': src.transform,
                'bounds': src.bounds,
                'height': src.height,
                'width': src.width,
                'count': src.count,
                'dtype': src.dtypes[0] if src.count > 0 else None,
                'nodata': src.nodata,
            }
            return data, metadata, src

    @staticmethod
    def write_raster(path: Union[str, Path], data: np.ndarray, metadata: dict) -> None:
        """
        Write raster file.
        
        Args:
            path: Output path
            data: Numpy array (bands, height, width)
            metadata: Dict with crs, transform, etc.
        """
        path = str(path)
        if data.ndim == 2:
            data = data[np.newaxis, :, :]
        
        with rasterio.open(
            path, 'w',
            driver='GTiff',
            height=data.shape[1],
            width=data.shape[2],
            count=data.shape[0],
            dtype=data.dtype,
            crs=metadata.get('crs'),
            transform=metadata.get('transform'),
            nodata=metadata.get('nodata'),
        ) as dst:
            dst.write(data)

    @staticmethod
    def get_statistics(data: np.ndarray, band: int = 0) -> Dict[str, float]:
        """
        Get raster statistics.
        
        Args:
            data: Numpy array
            band: Which band (0-indexed)
        
        Returns:
            Dict with min, max, mean, std
        """
        if data.ndim == 3:
            band_data = data[band]
        else:
            band_data = data
        
        valid_data = band_data[~np.isnan(band_data) & ~np.isinf(band_data)]
        
        return {
            'min': float(np.min(valid_data)) if len(valid_data) > 0 else None,
            'max': float(np.max(valid_data)) if len(valid_data) > 0 else None,
            'mean': float(np.mean(valid_data)) if len(valid_data) > 0 else None,
            'std': float(np.std(valid_data)) if len(valid_data) > 0 else None,
            'count': len(valid_data),
        }

    @staticmethod
    def clip_raster(data: np.ndarray, metadata: dict, geometry) -> Tuple[np.ndarray, dict]:
        """
        Clip raster to geometry.
        
        Args:
            data: Raster data
            metadata: Metadata dict
            geometry: Shapely geometry
        
        Returns:
            Clipped data and updated metadata
        """
        # This requires a temporary file for rasterio
        from tempfile import NamedTemporaryFile
        
        with NamedTemporaryFile(suffix='.tif', delete=False) as tmp:
            tmp_path = tmp.name
        
        RasterOperations.write_raster(tmp_path, data, metadata)
        
        with rasterio.open(tmp_path) as src:
            clipped_data, clipped_transform = rio_mask(src, [geometry], crop=True)
            clipped_metadata = src.meta.copy()
            clipped_metadata.update({
                'height': clipped_data.shape[1],
                'width': clipped_data.shape[2],
                'transform': clipped_transform,
            })
        
        Path(tmp_path).unlink()
        return clipped_data, clipped_metadata

    @staticmethod
    def resample_raster(data: np.ndarray, metadata: dict, 
                        scale: float) -> Tuple[np.ndarray, dict]:
        """
        Resample raster to new scale factor.
        
        Args:
            data: Raster data
            metadata: Metadata
            scale: Scale factor (0.5 = 50% resolution)
        
        Returns:
            Resampled data and metadata
        """
        from scipy import ndimage
        
        new_shape = (data.shape[0],
                     int(data.shape[1] * scale),
                     int(data.shape[2] * scale))
        
        resampled = np.zeros(new_shape, dtype=data.dtype)
        for i in range(data.shape[0]):
            resampled[i] = ndimage.zoom(data[i], scale, order=1)
        
        new_metadata = metadata.copy()
        new_transform = rasterio.transform.from_bounds(
            metadata['bounds'].left,
            metadata['bounds'].bottom,
            metadata['bounds'].right,
            metadata['bounds'].top,
            new_shape[2],
            new_shape[1]
        )
        new_metadata.update({
            'height': new_shape[1],
            'width': new_shape[2],
            'transform': new_transform,
        })
        
        return resampled, new_metadata

    @staticmethod
    def calculate_slope(dem: np.ndarray) -> np.ndarray:
        """Calculate slope from DEM in degrees."""
        from scipy import ndimage
        
        gy, gx = np.gradient(dem)
        slope = np.arctan(np.sqrt(gx**2 + gy**2))
        return np.degrees(slope)

    @staticmethod
    def calculate_aspect(dem: np.ndarray) -> np.ndarray:
        """Calculate aspect from DEM in degrees."""
        from scipy import ndimage
        
        gy, gx = np.gradient(dem)
        aspect = np.arctan2(-gx, gy)
        aspect = np.degrees(aspect)
        aspect = np.where(aspect < 0, aspect + 360, aspect)
        return aspect

    @staticmethod
    def zonal_statistics(data: np.ndarray, zones: np.ndarray) -> Dict[int, Dict]:
        """
        Calculate statistics for zones.
        
        Args:
            data: Raster data
            zones: Zone ID raster
        
        Returns:
            Dict mapping zone ID to statistics
        """
        results = {}
        unique_zones = np.unique(zones[~np.isnan(zones)])
        
        for zone_id in unique_zones:
            zone_mask = zones == zone_id
            zone_values = data[zone_mask]
            zone_values = zone_values[~np.isnan(zone_values) & ~np.isinf(zone_values)]
            
            results[int(zone_id)] = {
                'min': float(np.min(zone_values)) if len(zone_values) > 0 else None,
                'max': float(np.max(zone_values)) if len(zone_values) > 0 else None,
                'mean': float(np.mean(zone_values)) if len(zone_values) > 0 else None,
                'std': float(np.std(zone_values)) if len(zone_values) > 0 else None,
                'count': len(zone_values),
            }
        
        return results

    @staticmethod
    def merge_rasters(paths: List[Union[str, Path]]) -> Tuple[np.ndarray, dict]:
        """
        Merge multiple rasters.
        
        Args:
            paths: List of raster paths
        
        Returns:
            Merged raster data and metadata
        """
        datasets = [rasterio.open(str(p)) for p in paths]
        try:
            merged, merged_transform = rio_merge(datasets)
            metadata = datasets[0].meta.copy()
            metadata.update({
                'height': merged.shape[1],
                'width': merged.shape[2],
                'transform': merged_transform,
            })
            return merged, metadata
        finally:
            for ds in datasets:
                ds.close()

    @staticmethod
    def normalize_raster(data: np.ndarray, method: str = "minmax") -> np.ndarray:
        """
        Normalize raster values.
        
        Args:
            data: Input data
            method: 'minmax' (0-1) or 'zscore'
        
        Returns:
            Normalized data
        """
        valid_mask = ~np.isnan(data) & ~np.isinf(data)
        result = data.copy().astype(float)
        
        if method == "minmax":
            valid_data = data[valid_mask]
            min_val, max_val = np.min(valid_data), np.max(valid_data)
            if max_val - min_val > 0:
                result[valid_mask] = (result[valid_mask] - min_val) / (max_val - min_val)
        
        elif method == "zscore":
            valid_data = data[valid_mask]
            mean, std = np.mean(valid_data), np.std(valid_data)
            if std > 0:
                result[valid_mask] = (result[valid_mask] - mean) / std
        
        return result
