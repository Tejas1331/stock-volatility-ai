from pydantic import BaseModel
from typing import Dict, Any


class FinalReport(BaseModel):
    ticker: str
    date: str
    model: Dict[str, Any]
    context: Dict[str, Any]
    final_decision: Dict[str, Any]
    explanation: Dict[str, Any]
    metadata: Dict[str, Any]
