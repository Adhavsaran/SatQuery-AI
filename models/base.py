"""Honest lazy model adapter contract used by optional ML integrations."""
from abc import ABC, abstractmethod
from typing import Any
class ModelAdapter(ABC):
    name="unknown"; version="unknown"; task="unknown"; required_packages=()
    def __init__(self): self.loaded=False; self.load_error=None
    def load(self):
        try:
            for pkg in self.required_packages: __import__(pkg)
            self.loaded=True
        except Exception as exc: self.load_error=str(exc); self.loaded=False
        return self.loaded
    def get_metadata(self): return {"model":self.name,"version":self.version,"task":self.task,"loaded":self.loaded,"status":"READY" if self.loaded else "IMPLEMENTED_ADAPTER_MODEL_REQUIRED","load_error":self.load_error}
    @abstractmethod
    def validate_input(self, **kwargs): ...
    @abstractmethod
    def predict(self, **kwargs): ...
    def postprocess(self, result): return result

class UnavailableVisionAdapter(ModelAdapter):
    """Adapter declaration that never turns absence into an analysis result."""
    def __init__(self,name,task,model_id): super().__init__(); self.name=name; self.task=task; self.model_id=model_id; self.version=model_id; self.required_packages=("torch","transformers")
    def validate_input(self, **kwargs): return bool(kwargs.get("image_path"))
    def predict(self, **kwargs):
        if not self.loaded: self.load()
        return {**self.get_metadata(),"outputs":None,"evidence":[],"warnings":["No inference performed: install optional ML dependencies and configure/download model weights."],"confidence":None}
