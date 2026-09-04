"""Evidence-level optical/SAR fusion with explicit compatibility gates."""
def fuse(optical_meta, sar_meta, optical_result, sar_result):
    compatible=all([optical_meta.get("crs"),sar_meta.get("crs"), optical_meta.get("crs")==sar_meta.get("crs"), optical_meta.get("width")==sar_meta.get("width"), optical_meta.get("height")==sar_meta.get("height")])
    if not compatible:return {"status":"INPUTS_NOT_COREGISTERED","fused":False,"confidence":None,"warnings":["Fusion withheld: CRS/dimensions do not establish co-registration."],"evidence":[optical_result,sar_result]}
    return {"status":"EVIDENCE_FUSED","fused":True,"method":"decision/evidence-level conjunction","optical_evidence":optical_result,"sar_evidence":sar_result,"confidence":None,"warnings":["Semantic verification requires a configured SAR model or independently compatible detections."]}
