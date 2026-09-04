# SatQuery AI

**An Autonomous Vision-Language Assistant for Multimodal Remote Sensing Image Analysis**

## Overview

SatQuery AI is a backend system that transforms natural language queries into evidence-grounded investigations of satellite imagery. It integrates vision-language models, geospatial GIS engines, and an autonomous planning agent.

**Status**: backend, validation, deterministic change/SAR/GIS and controlled agent execution are implemented. Optional VLM adapters are honest adapters, not downloaded models; see `IMPLEMENTATION_STATUS.md`.

## Architecture

```
User Query
    ↓
FastAPI Backend (/api/query)
    ↓
SatQuery Agent
    ├─→ UNDERSTAND (query parsing, task detection)
    ├─→ VALIDATE (input validation, metadata extraction)
    ├─→ PLAN (dynamic tool selection)
    ├─→ EXECUTE (tool invocation)
    ├─→ VERIFY (result verification)
    ├─→ FUSE (evidence combination)
    └─→ EXPLAIN (natural language generation)
    ↓
Structured Answer + Evidence + Execution Trace
```

## Project Structure

```
SatQuery-AI/
├── backend/                    # FastAPI application
│   ├── main.py                # API endpoints
│   ├── config.py              # Configuration & settings
│   └── schemas.py             # Pydantic models
├── agent/                      # Autonomous agent system
│   ├── agent.py               # Main orchestrator
│   ├── state.py               # Execution state machine
│   ├── tool_registry.py       # Tool management
│   └── base.py                # Abstract base classes
├── data/                       # Data handling (Phase 1)
│   ├── validator.py           # Input validation (Phase 1)
│   ├── metadata.py            # Metadata extraction
│   └── loader.py              # Data I/O (from GeoPilot)
├── gis/                        # GIS operations (from GeoPilot)
│   ├── indices.py             # Spectral indices
│   ├── vector.py              # Vector operations
│   ├── raster.py              # Raster operations
│   └── spatial.py             # Spatial utilities
├── providers/                  # LLM & VLM integrations
│   ├── base.py                # Provider framework
│   ├── llm.py                 # Language models
│   └── vlm.py                 # Vision-language models (Phase 2)
├── models/                     # AI model implementations
│   ├── vqa/                   # Visual Question Answering (Phase 2)
│   ├── captioning/            # Scene description (Phase 2)
│   ├── grounding/             # Visual grounding (Phase 2)
│   ├── detection/             # Object detection
│   ├── segmentation/          # Semantic segmentation
│   ├── change_detection/      # Bi-temporal analysis
│   ├── sar/                   # SAR analysis
│   └── fusion/                # Optical + SAR fusion
├── evidence/                   # Evidence tracking
│   ├── evidence.py            # Evidence objects
│   ├── provenance.py          # Evidence tracing
│   └── confidence.py          # Confidence estimation
├── tests/                      # Unit tests
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Configuration template
└── README.md                   # This file
```

## Quick Start

### 1. Install Dependencies

```bash
cd /home/adhavsaran/Documents/SatQuery-AI
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

## Current API and honest model behavior

`GET /health`, `GET /models`, and `GET /tools` expose service status, model-adapter state, and the controlled tool allow-list. `POST /analyze` (also `/agent/query`) accepts the existing `QueryRequest` shape. Task aliases are available at `/vqa`, `/caption`, `/ground`, `/detect`, `/segment`, `/change`, `/sar`, and `/fusion`.

For an end-to-end local deterministic example, supply two co-registered GeoTIFFs:

```bash
curl -X POST http://127.0.0.1:8000/analyze -H 'content-type: application/json' -d '{"query":"What changed between 2024 and 2026?", "images":[{"filepath":"/absolute/t1_2024.tif","modality":"optical"},{"filepath":"/absolute/t2_2026.tif","modality":"optical"}]}'
```

It will execute validation, metadata extraction, alignment-gated pixel change, evidence aggregation, and an auditable trace. VQA/captioning/grounding/detection/segmentation adapters do **not** emit results until their optional model runtime and actual weights are configured.

**Dependencies include**:
- FastAPI + Uvicorn (web framework)
- Pydantic (data validation)
- Geospatial: geopandas, rasterio, shapely, gdal, pyproj
- ML: scikit-learn, torch, transformers
- Visualization: matplotlib, pillow

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```ini
# LLM Provider (choose one)
LLM_PROVIDER=ollama  # or: openai, deepseek, claude, google
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

**For Ollama (recommended for local development)**:
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Start server
ollama serve &

# Pull a model
ollama pull mistral
```

### 3. Run Backend

```bash
python main.py
```

**Output**:
```
INFO: SatQuery AI - Remote Sensing Vision-Language Assistant
INFO: Version: 0.1.0 (Phase 1)
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 4. Access API

- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Main Endpoint**: POST http://localhost:8000/api/query

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Query Processing
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find newly constructed buildings in 2024",
    "images": [
      {
        "filepath": "/data/image_2024.tif",
        "modality": "multispectral",
        "acquisition_date": "2024-06-15"
      }
    ],
    "trace_execution": true
  }'
```

## Phase 1 Features

✅ **Implemented**:
- FastAPI backend with async support
- Pydantic request/response schemas
- Agent state management
- Tool registry (controlled execution)
- Configuration management
- Logging infrastructure
- Health check endpoints

⏳ **Phase 1 Placeholders** (Ready for Phase 2):
- Query understanding (LLM integration)
- Input validation (will implement in next PR)
- Dynamic planning (will implement in Phase 2)
- Tool execution (framework in place)
- Evidence fusion (framework in place)
- Confidence estimation (framework in place)

❌ **Not Yet Implemented** (Planned for Phase 2+):
- Vision-language models (VQA, captioning)
- Object detection & segmentation
- Change detection
- SAR analysis
- Optical + SAR fusion
- Real execution trace collection

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format
black .

# Lint
flake8 . --max-line-length=100

# Type check
mypy . --ignore-missing-imports

# Sort imports
isort .
```

### Project Phases

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 1** | Backend + Agent Skeleton | ✅ Complete |
| **Phase 2** | Vision-Language Models + VQA | ⏳ Planned |
| **Phase 3** | Captioning + Grounding | ⏳ Planned |
| **Phase 4** | Change Detection | ⏳ Planned |
| **Phase 5** | GIS Reasoning | ⏳ Planned |
| **Phase 6** | SAR Analysis | ⏳ Planned |
| **Phase 7** | Optical + SAR Fusion | ⏳ Planned |
| **Phase 8** | Evidence + Confidence + Tracing | ⏳ Planned |
| **Phase 9** | Evaluation | ⏳ Planned |

## Migration from GeoPilot

GeoPilot components successfully integrated:

| Component | Status | Location |
|-----------|--------|----------|
| Spectral Indices (30+) | ✅ Ready for extraction | `gis/indices.py` |
| Vector Analysis | ✅ Ready for extraction | `gis/vector.py` |
| Raster Analysis | ✅ Ready for extraction | `gis/raster.py` |
| Data Manager | ✅ Ready for adaptation | `data/loader.py` |
| Provider Framework | ✅ Generalized for VLM | `providers/base.py` |

Removed:
- QGIS plugin infrastructure
- PyQt5 GUI code
- Paper generation tools
- Journal recommendation system

## Key Design Principles

1. **No QGIS Dependency**: All code runs standalone
2. **Type Hints**: Full typing for IDE support
3. **Modular**: Each component independently testable
4. **Deterministic GIS**: Measurements via GIS, not LLM guessing
5. **Evidence-Based Confidence**: Confidence tied to actual evidence
6. **Execution Tracing**: Full audit trail for every query
7. **Tool Registry**: Only registered tools can execute
8. **Stateful Agent**: Complete state tracking through execution

## Configuration

All configuration via `.env` file or environment variables:

```ini
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ENVIRONMENT=development

# LLM Provider
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Data
DATA_DIR=./data/input
OUTPUT_DIR=./data/output
TEMP_DIR=./data/temp

# Features
ENABLE_CACHE=true
ENABLE_EXECUTION_TRACE=true
```

## Logging

Logs are written to console and optionally to file:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
logger.error("Error message")
```

Configure log level via `.env`:
```ini
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=./logs/satquery.log
```

## Next Steps

### Phase 2: Vision-Language Models
1. Implement `providers/vlm.py` with Hugging Face integration
2. Create `models/vqa/` module for visual question answering
3. Add VLM model initialization and inference
4. Create example VQA tool

### Phase 3: Scene Understanding
1. Implement `models/captioning/` for scene description
2. Implement `models/grounding/` for location identification
3. Add grounding tool to tool registry

### Phase 4+: Advanced Capabilities
1. Change detection (bi-temporal analysis)
2. SAR processing
3. Optical + SAR fusion
4. Evidence collection and confidence estimation

## Support

- **Documentation**: See README.md and code docstrings
- **Issues**: Check agent logs in console
- **Development**: Each module has type hints and docstrings

## License

See LICENSE file (MIT)

## Authors

SatQuery AI Development Team
