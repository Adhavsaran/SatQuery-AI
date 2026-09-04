"""SatQuery Entry Point

Run the backend server.
"""

import sys
import logging
from backend.main import app
from backend.config import settings

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run the SatQuery backend."""
    logger.info("=" * 80)
    logger.info("SatQuery AI - Remote Sensing Vision-Language Assistant")
    logger.info(f"Version: 0.1.0 (Phase 1)")
    logger.info("=" * 80)

    import uvicorn

    uvicorn.run(
        app,
        host=settings.backend_host,
        port=settings.backend_port,
        log_level=settings.log_level.lower(),
        reload=settings.environment == "development",
    )


if __name__ == "__main__":
    main()
