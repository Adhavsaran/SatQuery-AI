"""Deterministic fallback planner; an LLM provider may propose only registered tools."""
def build_plan(query, image_count, modalities):
    q=query.lower(); plan=["validate_image","extract_metadata"]
    if image_count>=2 and any(x in q for x in ("change","new","between","expanded","disappeared")): plan.append("change_detect")
    if "sar" in modalities or "sar" in q: plan.append("sar_analyze")
    if "sar" in modalities and any(x in modalities for x in ("optical","multispectral")): plan.append("optical_sar_fusion")
    if any(x in q for x in ("caption","describe","scene")): plan.append("caption")
    elif any(x in q for x in ("where","locate","ground")): plan.append("ground")
    elif any(x in q for x in ("building","road","ship","vehicle","aircraft","detect")): plan.append("detect_objects")
    else: plan.append("vqa")
    return list(dict.fromkeys(plan))
