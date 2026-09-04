"""Schema-described allow-list of SatQuery tools; no shell/Python execution."""
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable
from data.validator import DataValidator
from models.change_detection.core import detect_change
from models.sar.core import analyze_sar
from models.fusion.core import fuse
from models.base import UnavailableVisionAdapter

@dataclass
class Tool:
    name:str; description:str; requirements:dict; schema:dict; fn:Callable
    def info(self): return {"name":self.name,"description":self.description,"modality_requirements":self.requirements,"input_schema":self.schema}
class ToolRegistry:
    def __init__(self): self.tools={}
    def register(self,t): self.tools[t.name]=t
    def list_tools(self,category=None): return {n:t.info() for n,t in self.tools.items()}
    def execute(self,name,**params):
        if name not in self.tools: return {"success":False,"error":"unregistered tool"}
        start=perf_counter()
        try:return {"success":True,"result":self.tools[name].fn(**params),"duration_ms":round((perf_counter()-start)*1000,3)}
        except Exception as e:return {"success":False,"error":str(e),"duration_ms":round((perf_counter()-start)*1000,3)}
tool_registry=ToolRegistry()
validator=DataValidator()
adapters={"vqa":UnavailableVisionAdapter("remote-sensing-vqa","vqa","RSVQA-compatible HuggingFace model"),"caption":UnavailableVisionAdapter("remote-sensing-captioner","captioning","VRSBench-compatible HuggingFace model"),"ground":UnavailableVisionAdapter("grounding-dino","grounding","IDEA-Research/grounding-dino-base"),"detect":UnavailableVisionAdapter("remote-sensing-detector","detection","fine-tuned detector checkpoint"),"segment":UnavailableVisionAdapter("remote-sensing-segmenter","segmentation","fine-tuned segmentation checkpoint")}
def _metadata(image_path): return validator.inspect(image_path).to_dict()
def _validate(image_paths, metadata=None):
    r=validator.validate(image_paths,metadata); return {"valid":r.valid,"image_count":r.image_count,"images":[x.to_dict() for x in r.images],"task_type":r.task_type,"modalities":r.required_modalities,"errors":r.errors,"warnings":r.warnings}
def _fusion(optical_path,sar_path,optical_result=None): return fuse(_metadata(optical_path),_metadata(sar_path),optical_result or {},analyze_sar(sar_path))
def init_phase1_tools():
    if tool_registry.tools:return
    entries=[("validate_image","Validate formats, raster dimensions and geospatial metadata",{}, {"image_paths":"list[str]"},_validate),("extract_metadata","Extract raster metadata and provenance hash",{}, {"image_path":"str"},_metadata),("change_detect","Pixel-level bi-temporal change for registered rasters",{"images":2},{"t1_path":"str","t2_path":"str","threshold":"number?"},detect_change),("sar_analyze","Compute actual SAR raster statistics and preprocessing needs",{"modality":"sar"},{"image_path":"str"},analyze_sar),("optical_sar_fusion","Fuse compatible optical and SAR evidence",{"modalities":["optical","sar"]},{"optical_path":"str","sar_path":"str"},_fusion)]
    for key,label in [("vqa","vqa"),("caption","caption"),("ground","ground"),("detect","detect_objects"),("segment","segment")]: entries.append((label,f"Lazy real-model adapter: {key}",{}, {"image_path":"str"},adapters[key].predict))
    for n,d,r,s,f in entries: tool_registry.register(Tool(n,d,r,s,f))
