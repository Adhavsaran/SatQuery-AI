# 📦 GEOPILOT REUSABLE COMPONENTS GUIDE

**Purpose**: Detailed reference for which GeoPilot code can be reused in SatQuery-AI  
**Date**: September 4, 2026

---

## 🏆 TIER 1: COPY-PASTE READY (Minimal Changes)

### 1. Spectral Indices Library
**Source**: `GeoPilot-main/scripts/geoai_remote_sensing.py` (lines ~50-120)

**What to Copy**:
```python
class RemoteSensing:
    INDICES = {
        # 30+ index definitions as lambdas
        "NDVI": lambda B: (B["N"] - B["R"]) / (B["N"] + B["R"] + 1e-10),
        "EVI": lambda B: 2.5 * (B["N"] - B["R"]) / ...,
        # ... (30 more)
    }
    
    def compute_index(self, bands, index_name):
        """Compute single index"""
    
    def compute_multiple_indices(self, bands, index_names):
        """Batch compute"""
    
    def compute_all_indices(self, bands):
        """All indices"""
```

**Where to Put in SatQuery**: `SatQuery-AI/models/spectral_analysis.py`

**Changes Needed**: None (copy as-is)

**How to Use**:
```python
from models.spectral_analysis import RemoteSensing

rs = RemoteSensing()
bands = {"B": blue_array, "G": green_array, "R": red_array, "N": nir_array, ...}

# Single index
ndvi = rs.compute_index(bands, "NDVI")

# Multiple
indices = rs.compute_multiple_indices(bands, ["NDVI", "EVI", "NDBI"])

# All available
all_idx = rs.compute_all_indices(bands)
```

**Integration**: Create Tool wrapper:
```python
class SpectralIndexTool(BaseTool):
    def execute(self, image_bands, index_names, **kwargs):
        rs = RemoteSensing()
        return rs.compute_multiple_indices(image_bands, index_names)
```

---

### 2. Vector Analysis Toolkit
**Source**: `GeoPilot-main/scripts/geoai_vector_analysis.py` (lines ~30-300)

**What to Copy**: Entire `VectorAnalysis` class with 20+ methods:
```python
class VectorAnalysis:
    def buffer(gdf, distance, ...)
    def clip(target_gdf, clip_gdf)
    def intersection(gdf1, gdf2)
    def union(gdf1, gdf2)
    def spatial_join(target_gdf, join_gdf, ...)
    def hotspot_analysis_getis_ord(gdf, value_field)
    def morans_i(gdf, value_field)
    def lisa(gdf, value_field)
    def kernel_density(gdf)
    def voronoi_diagram(gdf)
    # ... 10+ more operations
```

**Where to Put in SatQuery**: `SatQuery-AI/gis/vector_ops.py`

**Changes Needed**: None (copy as-is)

**How to Use**:
```python
from gis.vector_ops import VectorAnalysis

va = VectorAnalysis()

# Buffer features
buffered = va.buffer(gdf, distance=100)

# Spatial analysis
hotspots = va.hotspot_analysis_getis_ord(gdf, value_field="population")

# Statistics
morans = va.morans_i(gdf, value_field="ndvi")
```

**Integration**: Create Tool wrappers for each method:
```python
class VectorBufferTool(BaseTool):
    def execute(self, gdf, distance, **kwargs):
        va = VectorAnalysis()
        return va.buffer(gdf, distance)

class HotspotAnalysisTool(BaseTool):
    def execute(self, gdf, value_field, **kwargs):
        va = VectorAnalysis()
        return va.hotspot_analysis_getis_ord(gdf, value_field)
```

---

### 3. Raster Analysis Toolkit
**Source**: `GeoPilot-main/scripts/geoai_raster_analysis.py` (lines ~30-300)

**What to Copy**: Entire `RasterAnalysis` class with 20+ methods:
```python
class RasterAnalysis:
    def read(path)
    def clip(data, meta, xmin, ymin, xmax, ymax)
    def resample(data, meta, target_res, method)
    def mosaic(raster_list)
    def calc(raster_path, expression)  # Raster calculator
    def slope(dem)
    def aspect(dem)
    def hillshade(dem)
    def flow_direction(dem)
    def flow_accumulation(dem)
    def zonal_stats(raster, zones)
    def focal_stats(raster, kernel)
    # ... 10+ more operations
```

**Where to Put in SatQuery**: `SatQuery-AI/gis/raster_ops.py`

**Changes Needed**: None (copy as-is)

**How to Use**:
```python
from gis.raster_ops import RasterAnalysis

ra = RasterAnalysis()

# Read and clip
data, meta = ra.read("image.tif")
clipped = ra.clip(data, meta, xmin, ymin, xmax, ymax)

# Terrain analysis
slope = ra.slope(dem)
hillshade = ra.hillshade(dem)

# Zonal statistics
zones = ra.zonal_stats(ndvi_raster, aoi_zones)
```

**Integration**: Create Tool wrappers:
```python
class RasterClipTool(BaseTool):
    def execute(self, raster_path, bounds, **kwargs):
        ra = RasterAnalysis()
        data, meta = ra.read(raster_path)
        return ra.clip(data, meta, *bounds)

class TerrainSlopeTool(BaseTool):
    def execute(self, dem_path, **kwargs):
        ra = RasterAnalysis()
        return ra.slope(dem_path)
```

---

### 4. Data Manager (Format Abstraction)
**Source**: `GeoPilot-main/scripts/geoai_data_manager.py` (lines ~30-240)

**What to Copy**: Entire `DataManager` class:
```python
class DataManager:
    def __init__(self, workspace)
    def scan_directory(path, recursive)
    def read_vector(path, layer, **kwargs)
    def read_raster(path, **kwargs)
    def write_vector(gdf, path, driver)
    def write_raster(data, meta, path)
    def reproject(gdf/raster, target_crs)
    def merge_vectors(gdf_list)
    def merge_rasters(raster_list)
    def sample_points(gdf, n_points)
    def grid(bounds, cell_size, crs)
```

**Supports** (22+ formats):
- Vectors: Shapefile, GeoJSON, GeoPackage, KML, KMZ, GML, MapInfo, DWG, DXF, WFS
- Rasters: GeoTIFF, NetCDF, HDF5, ERDAS IMG, JPEG2000, MRF, COG, GeoPackage
- Tabular: CSV, Excel
- Point Cloud: LAS, LAZ

**Where to Put in SatQuery**: `SatQuery-AI/data/geospatial_io.py`

**Changes Needed**: Adapt paths for async operations (optional)

**How to Use**:
```python
from data.geospatial_io import DataManager

dm = DataManager(workspace="./data")

# Auto-detect and load
gdf = dm.read_vector("data/input.shp")
raster_data, meta = dm.read_raster("data/sentinel2.tif")

# Multi-format support
geojson = dm.read_vector("data.geojson")
kml = dm.read_vector("data.kml")  # Auto-handles unpacking
netcdf = dm.read_raster("data.nc")

# Export to different format
dm.write_vector(gdf, "output.geojson", driver="GeoJSON")
dm.write_raster(raster_data, meta, "output.tif")

# Reproject
gdf_reprojected = dm.reproject(gdf, "EPSG:3857")

# Merge
merged_gdf = dm.merge_vectors([gdf1, gdf2, gdf3])
```

**Integration**: Wrap in data validation tools:
```python
class DataLoaderTool(BaseTool):
    def execute(self, file_path, **kwargs):
        dm = DataManager("./data")
        if file_path.endswith(('.shp', '.geojson', '.gkpg')):
            return dm.read_vector(file_path)
        elif file_path.endswith(('.tif', '.nc', '.hdf5')):
            return dm.read_raster(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_path}")
```

---

---

## 🔧 TIER 2: NEEDS ADAPTATION (Low-Medium Effort)

### 5. Google Earth Engine Bridge
**Source**: `GeoPilot-main/scripts/geoai_gee_bridge.py` (entire file)

**What to Copy**:
```python
def init_ee(project)
def get_s2_collection(roi, start_date, end_date, cloud_pct)
def get_l8_collection(roi, start_date, end_date, cloud_pct)
def gee_to_geopandas(ee_feature_collection)
def export_to_drive(image, description, folder, region, scale)
```

**Where to Put in SatQuery**: `SatQuery-AI/data/earth_engine.py`

**Changes Needed**:
- Make async (use asyncio.to_thread for blocking calls)
- Add error handling for auth failures
- Cache authentication token

**How to Use**:
```python
from data.earth_engine import init_ee, get_s2_collection, export_to_drive

# Initialize (requires Earth Engine API key)
init_ee(project="your-gcp-project")

# Query Sentinel-2
s2_collection = get_s2_collection(
    roi=aoi_geojson,
    start_date="2024-01-01",
    end_date="2024-12-31",
    cloud_pct=20
)

# Convert to GeoDataFrame
gdf = gee_to_geopandas(s2_collection)

# Export results
export_to_drive(
    image=processed_image,
    description="export_2024",
    folder="SatQuery-Exports",
    region=aoi_bounds
)
```

**Integration**: Create tool:
```python
class SentinelDataTool(BaseTool):
    def execute(self, aoi_geometry, start_date, end_date, **kwargs):
        init_ee("your-project")
        collection = get_s2_collection(aoi_geometry, start_date, end_date)
        return gee_to_geopandas(collection)
```

---

### 6. SCI Figure Generator
**Source**: `GeoPilot-main/scripts/geoai_sci_figure.py` (lines ~30-225)

**What to Copy**: `SCIFigures` class with 8 methods:
```python
class SCIFigures:
    JOURNAL_CONFIGS = {...}  # 7 journal templates
    
    def figure1_study_area(satellite_img, boundary_gdf, inset_map)
    def figure2_land_cover(lc_maps, time_labels, class_names)
    def figure3_accuracy(confusion_matrix, class_names)
    def figure4_change_detection(before, after, change_map)
    def figure5_spatial_pattern(values_gdf, field, method)
    def figure6_driver_analysis(drivers_list, correlation_values)
    def figure7_uncertainty(error_map, stats)
    def figure8_framework(flowchart_data)
```

**Supported Journals**:
- Nature, Science, Remote Sensing, ISPRS JPRS, Ecological Indicators, MDPI, IEEE

**Where to Put in SatQuery**: `SatQuery-AI/evaluation/figure_generator.py`

**Changes Needed**:
- Make async (matplotlib is blocking)
- Add web-friendly output (PNG, SVG, etc.)
- Add Jupyter notebook export option

**How to Use**:
```python
from evaluation.figure_generator import SCIFigures

sci_fig = SCIFigures(journal="Nature")

# Generate study area figure
fig = sci_fig.figure1_study_area(
    satellite_img=rgb_image,
    boundary_gdf=study_area_gdf,
    inset_map=True
)
fig.savefig("figure1.png", dpi=300)

# Generate change detection figure
fig = sci_fig.figure4_change_detection(
    before=2020_image,
    after=2024_image,
    change_map=changes_array
)

# Generate accuracy assessment
fig = sci_fig.figure3_accuracy(
    confusion_matrix=cm,
    class_names=["Urban", "Forest", "Water", "Agriculture"]
)
```

**Integration**: Create tool:
```python
class ResultsFigureTool(BaseTool):
    def execute(self, analysis_results, journal="Nature", **kwargs):
        sci_fig = SCIFigures(journal=journal)
        figures = {}
        # Generate appropriate figures based on analysis type
        return figures
```

---

### 7. Provider Framework Architecture
**Source**: `GeoPilot-main/providers/base.py` + `providers/*_provider.py`

**What to Adapt** (not copy):
```python
# Current: LLM-specific factory
class BaseProvider:
    def chat(messages, system_prompt, temperature, max_tokens)

# Needed: Generalized API client factory
class BaseAPIClient:
    def call(request_type, **kwargs)  # Generic interface
```

**Current Providers** (18):
- OpenAI-compatible (16 variants)
- Anthropic Claude
- Google Gemini
- Ollama (local)
- Baidu ERNIE
- iFlytek Spark

**Adapt For SatQuery**:
1. Generalize to support any API type (LLM, VLM, data service)
2. Add VLM providers (BLIP-2, LLaVA, etc.)
3. Add data service clients (USGS, Copernicus, etc.)
4. Make provider loading more flexible

**Where to Put in SatQuery**: `SatQuery-AI/backend/api_clients.py`

**Example Adaptation**:
```python
# Generalized from GeoPilot's LLM-specific pattern
class APIClientRegistry:
    """Support any API, not just LLMs"""
    
    def register_client(name, client_class):
        pass
    
    def get_client(name, config):
        pass

# Support LLM
class LLMClient(BaseAPIClient):
    def call(self, messages, **kwargs):
        pass

# Support VLM
class VLMClient(BaseAPIClient):
    def call(self, image, text_prompt, **kwargs):
        pass

# Support data service
class DataServiceClient(BaseAPIClient):
    def call(self, query, **kwargs):
        pass
```

---

### 8. Pipeline Orchestrator Templates
**Source**: `GeoPilot-main/scripts/geoai_pipeline.py` (lines ~30-186)

**What to Copy** (as reference, not direct reuse):
```python
class GeoAIPipeline:
    # 6 workflow templates
    
    def urban_expansion_workflow(city, years):
        # Load → NDBI/NDVI → RF classification → Change detection → Figures
    
    def forest_disturbance_workflow(region, years):
        # Load → NBR time series → Disturbance detection
    
    def carbon_stock_workflow(region, year, method):
        # Load → Calculate carbon → Report
    
    def water_monitoring_workflow(region, years):
        # Load → MNDWI/AWEI time series → Water extraction
    
    def ecosystem_health_workflow(region, year):
        # Load → Vegetation health → Fragmentation
    
    def lulc_mapping_workflow(region, year):
        # Full LULC pipeline
```

**Where to Put in SatQuery**: Reference in `SatQuery-AI/agent/workflow_examples.py`

**Changes Needed**: Adapt workflow logic into agent phase handlers

**How to Use as Reference**:
```python
# These workflows become planning templates for agent
# When user asks: "Analyze urban expansion 2020-2024"
# Agent uses urban_expansion_workflow as planning template
# Phases: Understand → PLAN (choose workflow) → EXECUTE → EXPLAIN

WORKFLOW_TEMPLATES = {
    "urban_expansion": {
        "required_tools": ["NDBI", "NDVI", "Classification", "ChangeDetection"],
        "data_required": ["multispectral_2020", "multispectral_2024"],
        "outputs": ["change_map", "statistics", "figures"]
    },
    "forest_disturbance": {
        "required_tools": ["NBR", "TimeSeriesAnalysis", "Segmentation"],
        "data_required": ["multispectral_timeseries"],
        "outputs": ["disturbance_map", "timeline", "drivers"]
    }
}
```

---

---

## 📋 TIER 3: REFERENCE ONLY (Don't Copy)

### 9. Paper Submission Agent
**Source**: `GeoPilot-main/scripts/geoai_paper_agent.py`

**Why Reference Only**: Domain-specific to research paper submission  
**Use For**: Evaluation framework, not core SatQuery functionality

**Data to Use**:
```python
JOURNALS_DB = {
    "Nature": {"if": 64.8, "acceptance_rate": 0.05, ...},
    "Science": {"if": 56.9, "acceptance_rate": 0.06, ...},
    # 12 more
}

# Useful for: Recommending where to publish SatQuery findings
```

**Keep For Later**: `evaluation/paper_recommendations.py`

---

### 10. UI Dialog
**Source**: `GeoPilot-main/geopilot_dialog.py` (916 LOC)

**Why NOT Reusable**: QGIS/PyQt5-specific

**What NOT to Copy**:
- PyQt5 widgets (not suitable for web)
- QGIS integration (not applicable)
- Settings storage (use FastAPI configuration instead)

**What to Learn From**:
- UI/UX patterns (adapt for web)
- Settings management approach (adapt for FastAPI)
- API worker thread pattern (adapt for async/await)

---

### 11. Plugin Bootstrap & QGIS Integration
**Source**: `GeoPilot-main/geopilot.py`, `__init__.py`, `geoai_qgis_bootstrap.py`

**Why NOT Reusable**: QGIS plugin system

**What NOT to Use**: 
- Plugin entry points
- QGIS toolbar integration
- QgsApplication initialization
- Windows-specific paths

---

---

## 📝 QUICK REFERENCE: FILE LOCATIONS & COMMANDS

### Copy These Files Directly

```bash
# Spectral Analysis
cp GeoPilot-main/scripts/geoai_remote_sensing.py \
   SatQuery-AI/models/spectral_analysis.py

# Vector Operations
cp GeoPilot-main/scripts/geoai_vector_analysis.py \
   SatQuery-AI/gis/vector_ops.py

# Raster Operations
cp GeoPilot-main/scripts/geoai_raster_analysis.py \
   SatQuery-AI/gis/raster_ops.py

# Data Manager
cp GeoPilot-main/scripts/geoai_data_manager.py \
   SatQuery-AI/data/geospatial_io.py

# Earth Engine Bridge
cp GeoPilot-main/scripts/geoai_gee_bridge.py \
   SatQuery-AI/data/earth_engine.py

# SCI Figures
cp GeoPilot-main/scripts/geoai_sci_figure.py \
   SatQuery-AI/evaluation/figure_generator.py

# Paper Agent (optional)
cp GeoPilot-main/scripts/geoai_paper_agent.py \
   SatQuery-AI/evaluation/paper_recommender.py
```

### Adapt These (Don't Copy Directly)

```bash
# Provider Framework - Generalize
# Reference: GeoPilot-main/providers/base.py
# Destination: SatQuery-AI/backend/api_clients.py
# Task: Generalize from LLM-specific to any API type

# Pipeline Templates - Use as Reference
# Reference: GeoPilot-main/scripts/geoai_pipeline.py
# Destination: SatQuery-AI/agent/workflow_examples.py
# Task: Adapt workflow logic into agent phase handlers
```

### Don't Copy These

```bash
# ❌ geopilot_dialog.py - QGIS/PyQt5 specific
# ❌ geopilot.py - QGIS plugin protocol
# ❌ geoai_qgis_bootstrap.py - QGIS initialization
# ❌ geoai_env_setup.py - Windows-centric paths
```

---

---

## 🚀 IMPLEMENTATION CHECKLIST

### Phase 2: Core Tools (Weeks 1-2)

- [ ] Import Spectral Indices
  - [ ] Copy `geoai_remote_sensing.py`
  - [ ] Create `SpectralIndexTool` wrapper
  - [ ] Add to tool registry
  - [ ] Test with example indices

- [ ] Import Vector Operations
  - [ ] Copy `geoai_vector_analysis.py`
  - [ ] Create tool wrappers for 10+ operations
  - [ ] Add to tool registry
  - [ ] Test with sample geometries

- [ ] Import Raster Operations
  - [ ] Copy `geoai_raster_analysis.py`
  - [ ] Create tool wrappers for 10+ operations
  - [ ] Add to tool registry
  - [ ] Test with sample rasters

- [ ] Import Data Manager
  - [ ] Copy `geoai_data_manager.py`
  - [ ] Adapt for async operations
  - [ ] Test format detection
  - [ ] Test CRS reprojection

### Phase 2: Agent Implementation (Weeks 2-3)

- [ ] Implement agent.py phases
  - [ ] `_phase_understand()` - LLM integration
  - [ ] `_phase_validate()` - Real validation
  - [ ] `_phase_plan()` - Dynamic planning
  - [ ] `_phase_execute()` - Tool execution
  - [ ] `_phase_verify()` - Result verification
  - [ ] `_phase_fuse()` - Evidence fusion
  - [ ] `_phase_explain()` - LLM-based explanation

- [ ] Implement real tools
  - [ ] ImageValidatorTool (real GDAL check)
  - [ ] MetadataExtractorTool (real metadata extraction)
  - [ ] 10+ GIS operation tools

- [ ] Add LLM integration
  - [ ] Query understanding
  - [ ] Explanation generation
  - [ ] Prompt templates

### Phase 3: Optional Features (Weeks 4+)

- [ ] Import GEE Bridge
- [ ] Import SCI Figure Generator
- [ ] Add VLM integration
- [ ] Adapt pipeline templates
- [ ] Add paper recommender

---

**Created**: September 4, 2026  
**For Project**: SatQuery-AI Phase 2+  
**Reference**: GeoPilot-main v1.3.7
