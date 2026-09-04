"""
Spectral Indices - Remote Sensing Analysis Toolkit

30+ spectral indices for vegetation, water, built-up, burn, moisture, snow, and soil analysis.
All indices are implemented as pure numpy computations with no external dependencies except numpy.
"""

from typing import Dict, List, Optional, Union, Tuple
import numpy as np


class SpectralIndices:
    """Compute spectral indices from satellite imagery bands."""

    # Spectral index formulas (band input as dict with standard band names)
    # Standard band naming: B=Blue, G=Green, R=Red, N=NIR, S1=SWIR1, S2=SWIR2, RE1=RedEdge
    INDICES = {
        # VEGETATION INDICES
        "NDVI": lambda B: (B["N"] - B["R"]) / (B["N"] + B["R"] + 1e-10),
        "EVI": lambda B: 2.5 * (B["N"] - B["R"]) / (B["N"] + 6 * B["R"] - 7.5 * B.get("B", 0) + 1 + 1e-10),
        "EVI2": lambda B: 2.5 * (B["N"] - B["R"]) / (B["N"] + 2.4 * B["R"] + 1 + 1e-10),
        "SAVI": lambda B: (B["N"] - B["R"]) * 1.5 / (B["N"] + B["R"] + 0.5 + 1e-10),
        "OSAVI": lambda B: (B["N"] - B["R"]) / (B["N"] + B["R"] + 0.16 + 1e-10),
        "MSAVI2": lambda B: (2 * B["N"] + 1 - np.sqrt(np.maximum((2 * B["N"] + 1) ** 2 - 8 * (B["N"] - B["R"]), 0))) / 2,
        "ARVI": lambda B: (B["N"] - (2 * B["R"] - B.get("B", 0))) / (B["N"] + (2 * B["R"] - B.get("B", 0)) + 1e-10),
        "GCVI": lambda B: (B["N"] / np.maximum(B.get("G", 1), 1e-10)) - 1,
        "NDRE": lambda B: (B["N"] - B.get("RE1", 0)) / (B["N"] + B.get("RE1", 0) + 1e-10),
        "CVI": lambda B: B["N"] * B["R"] / (np.maximum(B.get("G", 1), 1e-10) ** 2 + 1e-10),
        "RVI": lambda B: B["N"] / (B["R"] + 1e-10),
        "DVI": lambda B: B["N"] - B["R"],
        "GNDVI": lambda B: (B["N"] - B.get("G", 0)) / (B["N"] + B.get("G", 0) + 1e-10),
        
        # WATER INDICES
        "NDWI": lambda B: (B.get("G", 0) - B["N"]) / (B.get("G", 0) + B["N"] + 1e-10),
        "MNDWI": lambda B: (B.get("G", 0) - B.get("S1", 0)) / (B.get("G", 0) + B.get("S1", 0) + 1e-10),
        "AWEI_sh": lambda B: B.get("B", 0) + 2.5 * B.get("G", 0) - 1.5 * (B["N"] + B.get("S1", 0)) - 0.25 * B.get("S2", 0),
        "AWEI_nsh": lambda B: 4 * (B.get("G", 0) - B.get("S1", 0)) - (0.25 * B["N"] + 2.75 * B.get("S2", 0)),
        "WRI": lambda B: (B.get("G", 0) + B["R"]) / (B["N"] + B.get("S1", 0) + 1e-10),
        
        # BUILT-UP INDICES
        "NDBI": lambda B: (B.get("S1", 0) - B["N"]) / (B.get("S1", 0) + B["N"] + 1e-10),
        "BUI": lambda B: ((B.get("S1", 0) - B["N"]) / (B.get("S1", 0) + B["N"] + 1e-10)) - ((B["N"] - B["R"]) / (B["N"] + B["R"] + 1e-10)),
        "IBI": lambda B: _compute_ibi(B),
        
        # BURN INDICES
        "NBR": lambda B: (B["N"] - B.get("S2", 0)) / (B["N"] + B.get("S2", 0) + 1e-10),
        "BAI": lambda B: 1 / ((0.1 - B["R"]) ** 2 + (0.06 - B["N"]) ** 2 + 1e-10),
        
        # MOISTURE INDICES
        "NDMI": lambda B: (B["N"] - B.get("S1", 0)) / (B["N"] + B.get("S1", 0) + 1e-10),
        "MSI": lambda B: B.get("S1", 0) / (B["N"] + 1e-10),
        
        # SNOW INDEX
        "NDSI": lambda B: (B.get("G", 0) - B.get("S1", 0)) / (B.get("G", 0) + B.get("S1", 0) + 1e-10),
        
        # SOIL INDICES
        "BI": lambda B: np.sqrt((B["R"] ** 2 + B.get("G", 0) ** 2 + B["N"] ** 2) / 3),
        "CI": lambda B: (B["R"] - B.get("G", 0)) / (B["R"] + B.get("G", 0) + 1e-10),
    }

    def __init__(self):
        """Initialize spectral indices toolkit."""
        self._cache = {}

    def list_indices(self) -> List[str]:
        """Return list of available indices."""
        return list(self.INDICES.keys())

    def compute_index(self, bands: Dict[str, np.ndarray], index_name: str) -> np.ndarray:
        """
        Compute a single spectral index.
        
        Args:
            bands: Dict mapping band names to numpy arrays
                   Standard names: B, G, R, N, S1, S2, RE1, etc.
            index_name: Name of the index to compute
        
        Returns:
            Numpy array with index values
        
        Raises:
            ValueError: If index name not recognized
        """
        if index_name not in self.INDICES:
            raise ValueError(f"Unknown index: {index_name}. Available: {list(self.INDICES.keys())}")
        
        try:
            return self.INDICES[index_name](bands)
        except Exception as e:
            raise ValueError(f"Error computing {index_name}: {str(e)}")

    def compute_multiple_indices(self, bands: Dict[str, np.ndarray], 
                                 index_names: Optional[List[str]] = None) -> Dict[str, np.ndarray]:
        """
        Compute multiple indices at once.
        
        Args:
            bands: Band dictionary
            index_names: List of indices to compute (None = all)
        
        Returns:
            Dict mapping index names to arrays
        """
        if index_names is None:
            index_names = list(self.INDICES.keys())
        
        results = {}
        for name in index_names:
            try:
                results[name] = self.compute_index(bands, name)
            except Exception as e:
                results[name] = None  # Mark failed indices
        
        return results

    def get_index_info(self, index_name: str) -> Dict[str, any]:
        """Get metadata about an index."""
        category_map = {
            "NDVI": "vegetation", "EVI": "vegetation", "EVI2": "vegetation",
            "SAVI": "vegetation", "OSAVI": "vegetation", "MSAVI2": "vegetation",
            "ARVI": "vegetation", "GCVI": "vegetation", "NDRE": "vegetation",
            "CVI": "vegetation", "RVI": "vegetation", "DVI": "vegetation",
            "GNDVI": "vegetation",
            "NDWI": "water", "MNDWI": "water", "AWEI_sh": "water",
            "AWEI_nsh": "water", "WRI": "water",
            "NDBI": "built-up", "BUI": "built-up", "IBI": "built-up",
            "NBR": "burn", "BAI": "burn",
            "NDMI": "moisture", "MSI": "moisture",
            "NDSI": "snow",
            "BI": "soil", "CI": "soil",
        }
        
        return {
            "name": index_name,
            "category": category_map.get(index_name, "unknown"),
            "description": f"Index: {index_name}",
            "range": "[-1, 1] typically",
            "available": index_name in self.INDICES,
        }


def _compute_ibi(B: Dict[str, np.ndarray]) -> np.ndarray:
    """Index-Based Built-up Index (complex computation)."""
    ndbi = (B.get("S1", 0) - B["N"]) / (B.get("S1", 0) + B["N"] + 1e-10)
    ndvi = (B["N"] - B["R"]) / (B["N"] + B["R"] + 1e-10)
    ndwi = (B.get("G", 0) - B.get("S1", 0)) / (B.get("G", 0) + B.get("S1", 0) + 1e-10)
    
    numerator = 2 * ndbi / (ndbi + ndvi + ndwi + 1e-10) - (ndvi / (ndvi + ndbi + 1e-10) + ndwi / (ndwi + ndbi + 1e-10))
    denominator = 2 * ndbi / (ndbi + ndvi + ndwi + 1e-10) + (ndvi / (ndvi + ndbi + 1e-10) + ndwi / (ndwi + ndbi + 1e-10))
    
    return numerator / (denominator + 1e-10)
