"""Checks that critical claims have corresponding successful evidence."""
def verify(plan, executions):
    names={x.tool_name:x for x in executions}; failures=[]
    for required in ("validate_image",):
        if required not in names or names[required].status!="success": failures.append(f"critical tool failed: {required}")
    if "change_detect" in plan and names.get("change_detect") and names["change_detect"].result.get("status")!="SUCCESS": failures.append("change result is not valid for the supplied raster alignment")
    return {"verified":not failures,"failures":failures}
