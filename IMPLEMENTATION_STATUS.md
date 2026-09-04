# SatQuery-AI implementation status

| Feature | Status | Notes |
|---|---|---|
| FastAPI controlled backend, `/health`, `/models`, `/tools`, analysis endpoints | FULLY_IMPLEMENTED | Starts without model weights. |
| GeoTIFF/TIFF/PNG/JPEG validation and metadata/provenance hashes | FULLY_IMPLEMENTED | Reports CRS, affine, extent, bands, dtype, nodata, resolution and warnings. |
| Controlled agent planning/execution/trace | FULLY_IMPLEMENTED | Registered tools only; no arbitrary code execution. |
| Pixel-level bi-temporal change | FULLY_IMPLEMENTED | Requires exactly aligned CRS/affine/dimensions; refuses otherwise. |
| SAR statistics/preprocessing inspection | FULLY_IMPLEMENTED | Does not claim semantic SAR verification. |
| Optical/SAR evidence fusion | FULLY_IMPLEMENTED | Co-registration gate; decision/evidence-level output. |
| GIS spectral indices, coordinate/area/distance helpers | FULLY_IMPLEMENTED | Named-band requirements are enforced. |
| VQA, captioning, grounding, detection, segmentation | IMPLEMENTED_ADAPTER_MODEL_REQUIRED | Lazy adapters declare missing torch/transformers/checkpoints and return no fabricated result. |
| Remote-sensing fine-tuning | NOT_IMPLEMENTED | No datasets/checkpoints are available locally. |
| Evaluation benchmark runs | NOT_IMPLEMENTED | Infrastructure/data must be supplied; no scores claimed. |

## Runnable now

`python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`

`curl http://127.0.0.1:8000/health`

Use `POST /analyze` with local image paths in `images`. For real VLM inference install compatible `torch`, `transformers`, and configure a downloaded remote-sensing checkpoint; adapters deliberately remain unavailable until then.

## Verification run in this environment

`python -m compileall -q .` passed. Direct synthetic GeoTIFF checks passed for metadata extraction, named-band NDVI contract, localized aligned raster change, and the asynchronous agent workflow. `python -m pytest -q` could not run because this environment has no `pytest` module installed (the dependency remains listed in `requirements.txt`). Uvicorn imported and initialized the application, but binding test ports was denied/occupied by the execution environment.
