def bucket_risk(score: float) -> str:
    if score < 0.20:
        return "low"
    elif score < 0.40:
        return "medium"
    else:
        return "high"
