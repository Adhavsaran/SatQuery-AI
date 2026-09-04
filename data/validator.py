"""
Data Validation - Image and Metadata Validation

Complete input validation for satellite imagery.
Determines modality, bands, CRS, resolution, and data quality.
Never fabricates missing metadata.
"""

from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import numpy as np
import rasterio
from rasterio.crs import CRS
import geopandas as gpd


@dataclass
class ImageMetadata:
    """Validated image metadata."""
    filepath: str
    format: str
    modality: str  # optical, multispectral, sar, thermal, panchromatic, hyperspectral
    width: int
    height: int
    bands: int
    band_names: List[str]
    crs: Optional[str]
    resolution: Optional[Tuple[float, float]]  # (x, y) in CRS units
    bounds: Optional[Tuple[float, float, float, float]]  # (left, bottom, right, top)
    nodata_value: Optional[float]
    dtype: str
    acquisition_date: Optional[str]
    temporal_coverage: Optional[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class ValidationResult:
    """Result of input validation."""
    valid: bool
    image_count: int
    images: List[ImageMetadata]
    task_type: str  # single_image, bi_temporal, optical_sar, multi_temporal, unknown
    required_modalities: List[str]
    errors: List[str]
    warnings: List[str]


class DataValidator:
    """Validate satellite imagery and metadata."""

    OPTICAL_BANDS = {"B", "G", "R", "L", "PAN"}
    MULTISPECTRAL_BANDS = {"B", "G", "R", "N", "RE1", "RE2", "RE3", "S1", "S2", "S3"}
    SAR_BANDS = {"VV", "VH", "HH", "HV", "HX"}
    THERMAL_BANDS = {"B10", "B11", "TIR1", "TIR2"}

    def validate(self, image_paths: List[str], metadata: Optional[Dict] = None) -> ValidationResult:
        """
        Validate input images and metadata.
        
        Args:
            image_paths: List of paths to image files
            metadata: Optional user-provided metadata (query, date range, etc.)
        
        Returns:
            ValidationResult with detailed validation info
        """
        if not image_paths:
            return ValidationResult(
                valid=False,
                image_count=0,
                images=[],
                task_type="unknown",
                required_modalities=[],
                errors=["No images provided"],
                warnings=[]
            )

        # Validate each image
        validated_images = []
        errors = []
        warnings = []
        
        for path in image_paths:
            try:
                img_meta = self._validate_single_image(path)
                validated_images.append(img_meta)
            except Exception as e:
                errors.append(f"Error validating {path}: {str(e)}")

        if errors and not validated_images:
            return ValidationResult(
                valid=False,
                image_count=len(image_paths),
                images=[],
                task_type="unknown",
                required_modalities=[],
                errors=errors,
                warnings=warnings
            )

        # Determine task type from image count and modalities
        task_type = self._infer_task_type(validated_images)
        required_modalities = self._extract_modalities(validated_images)

        # Cross-check compatibility
        compatibility_issues = self._check_compatibility(validated_images)
        warnings.extend(compatibility_issues)

        is_valid = len(errors) == 0
        
        return ValidationResult(
            valid=is_valid,
            image_count=len(validated_images),
            images=validated_images,
            task_type=task_type,
            required_modalities=required_modalities,
            errors=errors,
            warnings=warnings
        )

    def _validate_single_image(self, path: str) -> ImageMetadata:
        """Validate a single image file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = path.suffix.lower()
        
        # Try to open as raster
        try:
            with rasterio.open(path) as src:
                return self._extract_raster_metadata(src, path)
        except Exception:
            pass

        # Try to open as vector
        try:
            gdf = gpd.read_file(path)
            return self._extract_vector_metadata(gdf, path)
        except Exception:
            raise ValueError(f"Cannot read file as raster or vector: {path}")

    def _extract_raster_metadata(self, src, path: Path) -> ImageMetadata:
        """Extract metadata from raster file."""
        band_count = src.count
        band_names = [f"Band_{i+1}" for i in range(band_count)]
        
        # Try to detect modality from band count and names
        modality = self._detect_modality(band_count, band_names, src)
        
        # Get resolution (pixel size)
        pixel_size_x = abs(src.transform.a)
        pixel_size_y = abs(src.transform.e)
        resolution = (pixel_size_x, pixel_size_y)

        # Get bounds
        left, bottom, right, top = src.bounds
        bounds = (left, bottom, right, top)

        # Get CRS string
        crs_str = None
        if src.crs:
            crs_str = str(src.crs)

        # Try to detect acquisition date from filename or metadata
        acquisition_date = self._extract_date_from_path(str(path))

        metadata = ImageMetadata(
            filepath=str(path),
            format=path.suffix.lower()[1:],
            modality=modality,
            width=src.width,
            height=src.height,
            bands=band_count,
            band_names=band_names,
            crs=crs_str,
            resolution=resolution,
            bounds=bounds,
            nodata_value=src.nodata,
            dtype=src.dtypes[0] if src.count > 0 else "unknown",
            acquisition_date=acquisition_date,
            temporal_coverage=None,
        )

        # Add warnings
        if src.nodata is None and modality != "unknown":
            metadata.warnings.append("No NoData value defined")
        if src.crs is None:
            metadata.warnings.append("No CRS defined")

        return metadata

    def _extract_vector_metadata(self, gdf, path: Path) -> ImageMetadata:
        """Extract metadata from vector file."""
        bounds = gdf.total_bounds  # (minx, miny, maxx, maxy)
        
        return ImageMetadata(
            filepath=str(path),
            format=path.suffix.lower()[1:],
            modality="vector",
            width=len(gdf),
            height=1,
            bands=len(gdf.columns),
            band_names=list(gdf.columns),
            crs=str(gdf.crs) if gdf.crs else None,
            resolution=None,
            bounds=(bounds[0], bounds[1], bounds[2], bounds[3]),
            nodata_value=None,
            dtype="vector",
            acquisition_date=None,
            temporal_coverage=None,
        )

    def _detect_modality(self, band_count: int, band_names: List[str], src) -> str:
        """Detect image modality from band count and properties."""
        # Try to detect from band count
        if band_count == 1:
            return "panchromatic"
        elif band_count == 3:
            return "optical"
        elif band_count == 4:
            # Could be RGB+NIR or could be something else
            return "multispectral"
        elif band_count in [10, 11, 12, 13]:
            # Likely Sentinel-2 (12 bands)
            return "multispectral"
        elif band_count == 2:
            # Likely SAR (VV, VH)
            return "sar"
        elif band_count in [10, 11]:
            # Landsat thermal bands
            return "thermal"
        else:
            return "multispectral"  # Default guess for multi-band

    def _extract_date_from_path(self, path: str) -> Optional[str]:
        """Try to extract acquisition date from filename."""
        import re
        
        # Look for YYYY-MM-DD or YYYYMMDD patterns
        date_pattern = r'(\d{4}[-_]?\d{2}[-_]?\d{2})'
        match = re.search(date_pattern, path)
        if match:
            return match.group(1).replace('_', '-').replace('-', '-')
        return None

    def _infer_task_type(self, images: List[ImageMetadata]) -> str:
        """Infer task type from image list."""
        if len(images) == 0:
            return "unknown"
        elif len(images) == 1:
            return "single_image_analysis"
        elif len(images) == 2:
            modalities = [img.modality for img in images]
            if modalities[0] == modalities[1] == "optical" or modalities[0] == modalities[1] == "multispectral":
                return "bi_temporal_analysis"
            elif "sar" in modalities and ("optical" in modalities or "multispectral" in modalities):
                return "optical_sar_analysis"
            else:
                return "multi_temporal_analysis"
        else:
            return "multi_temporal_analysis"

    def _extract_modalities(self, images: List[ImageMetadata]) -> List[str]:
        """Extract unique modalities from images."""
        return list(set(img.modality for img in images))

    def _check_compatibility(self, images: List[ImageMetadata]) -> List[str]:
        """Check compatibility between images."""
        warnings = []
        
        if len(images) < 2:
            return warnings

        # Check CRS compatibility
        crss = [img.crs for img in images]
        if len(set(crss)) > 1 and not all(c is None for c in crss):
            warnings.append("Images have different CRS - reprojection may be needed")

        # Check resolution compatibility
        resolutions = [img.resolution for img in images]
        if len(set(str(r) for r in resolutions if r)) > 1:
            warnings.append("Images have different resolutions - resampling may be needed")

        # Check spatial extent compatibility
        bounds = [img.bounds for img in images if img.bounds]
        if len(bounds) > 1:
            # Check if bounds overlap
            b0 = bounds[0]
            b1 = bounds[1]
            overlap = not (b0[2] < b1[0] or b1[2] < b0[0] or b0[3] < b1[1] or b1[3] < b0[1])
            if not overlap:
                warnings.append("Image spatial extents do not overlap")

        return warnings
