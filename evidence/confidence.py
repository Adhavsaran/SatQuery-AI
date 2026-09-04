"""Evidence-weighted confidence aggregation, never LLM-generated."""
def aggregate(items):
    scores=[float(x.get("confidence")) for x in items if x.get("confidence") is not None]
    if not scores:return {"score":0.0,"level":"INSUFFICIENT_EVIDENCE","signals":{"evidence_count":0}}
    score=sum(scores)/len(scores); level="HIGH" if score>=.75 else "MEDIUM" if score>=.45 else "LOW"
    return {"score":score,"level":level,"signals":{"evidence_count":len(scores),"mean_model_or_measurement_confidence":score}}
