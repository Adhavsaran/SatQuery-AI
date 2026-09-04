"""Controlled, evidence-first query controller."""
from time import perf_counter
from backend.schemas import QueryResponse, ConfidenceEstimate, ConfidenceLevel, Evidence, ValidationReport, TaskType, ToolExecution, ExecutionTrace
from agent.tool_registry import tool_registry, init_phase1_tools
from agent.planner import build_plan
from agent.verifier import verify

class SatQueryAgent:
    def __init__(self): init_phase1_tools(); self.name="SatQuery Agent"; self.version="0.2.0"
    def plan(self, query, images, modalities):
        q=query.lower(); p=["validate_image","extract_metadata"]
        if len(images)>=2 and any(k in q for k in ("change","new","constructed","disappeared","expanded","between")):p.append("change_detect")
        if "sar" in modalities or "sar" in q:p.append("sar_analyze")
        if len(images)>=2 and "sar" in modalities and any(m in modalities for m in ("optical","multispectral")):p.append("optical_sar_fusion")
        if any(k in q for k in ("describe","caption","scene")):p.append("caption")
        elif any(k in q for k in ("where","locate","ground")):p.append("ground")
        elif any(k in q for k in ("detect","building","road","ship","vehicle","aircraft")):p.append("detect_objects")
        else:p.append("vqa")
        return build_plan(query,len(images),modalities)
    async def process_query(self, request):
        start=perf_counter(); paths=[x.filepath for x in request.images]; supplied={str(i):x.model_dump() for i,x in enumerate(request.images)}
        raw=tool_registry.execute("validate_image",image_paths=paths,metadata=supplied); validation_data=raw.get("result",{})
        task=getattr(TaskType, validation_data.get("task_type","single_image_analysis").upper(), TaskType.UNKNOWN)
        report=ValidationReport(is_valid=validation_data.get("valid",False),num_images=len(paths),image_modalities=[i.modality for i in request.images],detected_task_type=task,errors=validation_data.get("errors",[]),warnings=validation_data.get("warnings",[]),metadata_summary={"images":validation_data.get("images",[])})
        executions=[ToolExecution(tool_name="validate_image",status="success" if raw.get("success") else "failed",parameters={"image_paths":paths},result=validation_data,error_message=raw.get("error"),duration_ms=raw.get("duration_ms",0))]
        if not report.is_valid:return self._response(request,report,executions,[],{},"Input validation failed; no analysis was performed.",start)
        modalities=validation_data.get("modalities",[]); plan=self.plan(request.query,paths,modalities); results={}; evidence=[]
        for tool in plan:
            if tool=="validate_image":continue
            if tool=="extract_metadata":
                for p in paths: self._run(tool,{"image_path":p},executions,results,evidence)
            elif tool=="change_detect" and len(paths)>=2:self._run(tool,{"t1_path":paths[0],"t2_path":paths[1]},executions,results,evidence)
            elif tool=="sar_analyze":
                for im in validation_data["images"]:
                    if im["modality"]=="sar":self._run(tool,{"image_path":im["filepath"]},executions,results,evidence)
            elif tool=="optical_sar_fusion":
                o=next((x["filepath"] for x in validation_data["images"] if x["modality"] in ("optical","multispectral")),None); s=next((x["filepath"] for x in validation_data["images"] if x["modality"]=="sar"),None)
                if o and s:self._run(tool,{"optical_path":o,"sar_path":s},executions,results,evidence)
            elif tool in ("vqa","caption","ground","detect_objects","segment"):self._run(tool,{"image_path":paths[0],"question":request.query,"phrase":request.query},executions,results,evidence)
        successful=[e for e in executions if e.status=="success"]; unavailable=any((e.result or {}).get("status")=="IMPLEMENTED_ADAPTER_MODEL_REQUIRED" for e in executions)
        verification=verify(plan,executions)
        findings={"tool_results":results,"verification":verification,"analysis_status":"PARTIAL" if unavailable or not verification["verified"] else "COMPLETED","provenance":{"input_hashes":[x.get("file_sha256") for x in validation_data["images"]],"tools":[e.tool_name for e in executions]}}
        answer="Deterministic analysis completed. " + ("Requested semantic model inference was not performed because its optional model stack/weights are unavailable." if unavailable else "Results are available in structured findings.")
        return self._response(request,report,executions,evidence,findings,answer,start,plan)
    def _run(self,tool,params,executions,results,evidence):
        r=tool_registry.execute(tool,**params); result=r.get("result",{}); executions.append(ToolExecution(tool_name=tool,status="success" if r["success"] else "failed",parameters=params,result=result,error_message=r.get("error"),duration_ms=r.get("duration_ms",0))); results.setdefault(tool,[]).append(result)
        if r["success"]: evidence.append(Evidence(source=params.get("image_path",params.get("t1_path","multiple")),tool_name=tool,model_name=result.get("model"),input_data=params,output_data=result,confidence=float(result.get("confidence") or 0)))
    def _response(self,request,report,executions,evidence,findings,answer,start,plan=None):
        usable=[e.confidence for e in evidence if e.confidence>0]; score=sum(usable)/len(usable) if usable else 0.; level=ConfidenceLevel.HIGH if score>=.75 else ConfidenceLevel.MEDIUM if score>=.45 else ConfidenceLevel.INSUFFICIENT_EVIDENCE if not usable else ConfidenceLevel.LOW
        trace=ExecutionTrace(query=request.query,task_type=report.detected_task_type,validation=report,plan=plan or ["validate_image"],executions=executions,total_duration_ms=(perf_counter()-start)*1000,errors=report.errors+[e.error_message for e in executions if e.error_message]) if request.trace_execution else None
        return QueryResponse(query=request.query,answer=answer,confidence=ConfidenceEstimate(level=level,score=score,justification="Aggregate of returned model/change evidence; unavailable adapters contribute no confidence.",evidence_count=len(evidence)),evidence=evidence,findings=findings,execution_trace=trace)
    def get_status(self): return {"name":self.name,"version":self.version,"status":"ready","tools_registered":len(tool_registry.tools)}
agent=SatQueryAgent()
