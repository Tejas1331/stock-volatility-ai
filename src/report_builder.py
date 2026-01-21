from typing import Dict
from datetime import datetime


def build_final_report(state: Dict) -> Dict:
    """
    Convert final agent state into a structured JSON report.
    """

    report = {
        "ticker": state["ticker"],
        "date": state["date"],

        "model": {
            "risk_score": round(state["risk_score"], 6),
            "risk_bucket": state["risk_bucket"]
        },

        "context": {
            "risk_type": state["risk_type"],
            "exogenous_shock": state["exogenous_shock"],
            "alignment": state["context_alignment"],
            "confidence_modifier": state["confidence_modifier"]
        },

        "final_decision": {
            "signal": state["final_signal"],
            "confidence": "high" if state["confidence_modifier"] != "decrease" else "low"
        },

        "explanation": {
            "summary": state["summary"],
            "news_count": len(state["news"]) if state.get("news") else 0
        },

        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "system": "stock_volatility_ai_v1"
        }
    }

    return report
