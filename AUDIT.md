# Honest implementation audit

No endpoint returns a placeholder AI answer as an image inference result. Model-only operations return `IMPLEMENTED_ADAPTER_MODEL_REQUIRED` with null outputs/confidence when their dependencies or weights are unavailable. Pixel change is computed only from compatible registered raster grids. GIS helpers perform metric reprojection for area/distance rather than asking an LLM.

Known limitations: file-path API inputs are intended for trusted local deployment and should be constrained to an application data directory before multi-tenant exposure; upload persistence and training/evaluation dataset pipelines are not yet implemented. VQA/captioning/grounding/detection/segmentation require optional model packages and actual remote-sensing checkpoints.
