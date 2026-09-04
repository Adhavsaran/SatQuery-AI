"""Deterministic pixel-change analysis for compatible, aligned rasters."""
from pathlib import Path
import numpy as np, rasterio
from rasterio.features import shapes
from shapely.geometry import shape

def detect_change(t1_path:str,t2_path:str, threshold:float|None=None):
    with rasterio.open(t1_path) as a, rasterio.open(t2_path) as b:
        if (a.crs != b.crs or a.transform != b.transform or a.width != b.width or a.height != b.height):
            return {"status":"INPUTS_NOT_REGISTERED","change_mask":None,"changed_regions":[],"warnings":["Pixel-level change requires equal CRS, affine transform, width and height. Reproject/register externally or use a registration adapter."],"confidence":None}
        x=a.read(masked=True).astype("float32"); y=b.read(masked=True).astype("float32")
        if x.shape != y.shape: raise ValueError("band count differs")
        difference=np.abs(y.filled(np.nan)-x.filled(np.nan))
        counts=np.isfinite(difference).sum(axis=0)
        delta=np.divide(np.nansum(difference,axis=0),counts,out=np.full(counts.shape,np.nan,dtype=float),where=counts>0)
        valid=np.isfinite(delta)
        if not valid.any(): return {"status":"NO_VALID_PIXELS","change_mask":None,"changed_regions":[],"confidence":None,"warnings":["all pixels are nodata"]}
        used=float(threshold) if threshold is not None else float(np.nanmedian(delta[valid])+2*np.nanstd(delta[valid]))
        mask=(delta>used)&valid; regions=[]
        for geom,val in shapes(mask.astype("uint8"),mask=mask,transform=a.transform):
            g=shape(geom); regions.append({"geometry":geom,"area_crs_units":float(g.area)})
        score=float(mask.sum()/valid.sum())
        return {"status":"SUCCESS","threshold":used,"changed_pixel_fraction":score,"changed_regions":regions,"change_mask":{"shape":list(mask.shape),"changed_pixels":int(mask.sum())},"confidence":min(1.,max(0.,score*4)) if mask.any() else 0.,"evidence":{"operation":"mean_absolute_band_difference","transform":tuple(a.transform),"crs":str(a.crs)}}
