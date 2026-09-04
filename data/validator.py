"""Raster input validation and metadata extraction. No modality is guessed as fact."""
from dataclasses import asdict, dataclass, field
from pathlib import Path
import hashlib, re
from typing import Any, Optional
import numpy as np
import rasterio
from PIL import Image

SUPPORTED = {".tif", ".tiff", ".png", ".jpg", ".jpeg"}

@dataclass
class ImageMetadata:
    filepath: str; format: str; modality: str; width: int; height: int; bands: int; band_names: list[str]; crs: Optional[str]; resolution: Optional[tuple[float,float]]; bounds: Optional[tuple[float,float,float,float]]; nodata_value: Optional[float]; dtype: str; acquisition_date: Optional[str]; temporal_coverage: Optional[str] = None; transform: Optional[tuple[float,...]] = None; sensor_name: Optional[str] = None; file_sha256: Optional[str] = None; warnings: list[str] = field(default_factory=list)
    def to_dict(self): return asdict(self)
@dataclass
class ValidationResult:
    valid: bool; image_count: int; images: list[ImageMetadata]; task_type: str; required_modalities: list[str]; errors: list[str]; warnings: list[str]

class DataValidator:
    """Validate supported imagery and report compatibility without silently resampling."""
    def validate(self, image_paths: list[str], metadata: Optional[dict[str,Any]]=None) -> ValidationResult:
        metadata = metadata or {}; images=[]; errors=[]; warnings=[]
        for i, path in enumerate(image_paths):
            try: images.append(self.inspect(path, metadata.get(path, metadata.get(str(i), {}))))
            except Exception as exc: errors.append(f"{path}: {exc}")
        warnings.extend(w for im in images for w in im.warnings); warnings.extend(self.compatibility_warnings(images))
        return ValidationResult(not errors, len(images), images, self.infer_task(images), sorted(set(i.modality for i in images)), errors, warnings)
    def inspect(self, image_path: str, supplied: Optional[dict[str,Any]]=None) -> ImageMetadata:
        p=Path(image_path).expanduser().resolve()
        if not p.is_file(): raise FileNotFoundError("file does not exist")
        if p.suffix.lower() not in SUPPORTED: raise ValueError(f"unsupported format {p.suffix}; expected GeoTIFF/TIFF/PNG/JPEG")
        supplied=supplied or {}; date=supplied.get("acquisition_date") or self._date(str(p)); digest=self._hash(p)
        if p.suffix.lower() in {".tif", ".tiff"}:
            with rasterio.open(p) as ds:
                names=supplied.get("bands") or [d or f"Band_{n}" for n,d in enumerate(ds.descriptions,1)]; tags={**ds.tags(), **(ds.tags(1) if ds.count else {})}; warnings=[]
                if not ds.crs: warnings.append("missing CRS; geographic calculations are unavailable")
                if ds.transform.is_identity: warnings.append("identity geotransform; image is not georeferenced")
                if ds.nodata is None: warnings.append("missing nodata value")
                return ImageMetadata(str(p),p.suffix[1:].lower(),self._modality(supplied.get("modality"),names,ds.count,tags),ds.width,ds.height,ds.count,list(names),str(ds.crs) if ds.crs else None,(abs(ds.transform.a),abs(ds.transform.e)),tuple(ds.bounds),ds.nodata,ds.dtypes[0],date,transform=tuple(ds.transform),sensor_name=supplied.get("sensor_name") or tags.get("SENSOR"),file_sha256=digest,warnings=warnings)
        with Image.open(p) as im:
            bands=len(im.getbands())
            return ImageMetadata(str(p),p.suffix[1:].lower(),supplied.get("modality") or ("optical" if bands in (3,4) else "unknown"),im.width,im.height,bands,supplied.get("bands") or list(im.getbands()),None,None,None,None,str(np.asarray(im).dtype),date,file_sha256=digest,warnings=["non-GeoTIFF image has no CRS/geotransform unless supplied externally"])
    def compatibility_warnings(self, images):
        out=[]
        if len(images)<2:return out
        if len({x.crs for x in images})>1: out.append("images use different CRS; reproject before pixel-level comparison")
        if len({(x.width,x.height) for x in images})>1: out.append("images have different dimensions; resample/register before pixel-level comparison")
        for a,b in zip(images,images[1:]):
            if a.bounds and b.bounds and (a.bounds[2]<=b.bounds[0] or b.bounds[2]<=a.bounds[0] or a.bounds[3]<=b.bounds[1] or b.bounds[3]<=a.bounds[1]): out.append("images do not overlap spatially")
        return out
    def infer_task(self, ims):
        if len(ims)==1:return "single_image_analysis"
        return "optical_sar_analysis" if "sar" in {x.modality for x in ims} and len({x.modality for x in ims})>1 else ("bi_temporal_analysis" if len(ims)==2 else "multi_temporal_analysis")
    @staticmethod
    def _date(s):
        m=re.search(r"(20\d{2})[-_]?([01]\d)[-_]?([0-3]\d)",s); return "-".join(m.groups()) if m else None
    @staticmethod
    def _hash(p):
        h=hashlib.sha256()
        with p.open("rb") as f:
            for c in iter(lambda:f.read(1048576),b""):h.update(c)
        return h.hexdigest()
    @staticmethod
    def _modality(declared,names,count,tags):
        if declared and declared != "unknown": return str(declared)
        text=" ".join(map(str,names))+" "+" ".join(f"{k}={v}" for k,v in tags.items())
        if re.search(r"\b(VV|VH|HH|HV|SAR|SENTINEL-1)\b",text,re.I): return "sar"
        return "optical" if count==3 else ("multispectral" if count>=4 else "unknown")
