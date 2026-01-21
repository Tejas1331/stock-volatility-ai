from typing import TypedDict, List

from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os
from src.model_inference import predict_volatility
from src.report_builder import build_final_report
import json



load_dotenv()  # 👈 loads .env into environment



# ----------------------------
# Agent State
# ----------------------------
class ContextState(TypedDict):
    ticker: str
    date: str
    news: List[str]
    summary: str
    risk_score: float
    risk_bucket: str
    risk_type: str
    exogenous_shock: bool
    context_alignment: str
    confidence_modifier: str
    final_signal: str

# ----------------------------
# Tool: Fetch news (stub for now)
# ----------------------------
'''def fetch_news(state: ContextState) -> ContextState:
    """
    Later this will call NewsAPI / Google News.
    For now, mock data.
    """
    state["news"] = [
        "Oil prices surged amid Middle East tensions.",
        "Indian markets saw heavy FII outflows this week.",
        "Energy sector stocks experienced increased volatility."
    ]
    return state
    '''

from src.news_fetcher import fetch_google_news


'''def fetch_news(state: ContextState) -> ContextState:
    """
    Fetch real Google News headlines related to the ticker.
    """
    query = state["ticker"].replace(".NS", "")
    headlines = fetch_google_news(
        query=query,
        days_back=3,
        max_items=8
    )

    state["news"] = headlines
    return state
'''

def fetch_news(state: ContextState) -> ContextState:
    query = state["ticker"].replace(".NS", "")

    headlines = fetch_google_news(
        query=query,
        reference_date=state["date"],
        window_days=3,
        max_items=8
    )

    state["news"] = headlines
    return state



def classify_context(state: ContextState) -> ContextState:
    summary = state["summary"].lower()

    # 🔴 STRICT macro-only triggers (no generic words)
    macro_triggers = [
        "war", "geopolitical", "military conflict",
        "oil price surge", "crude price spike",
        "interest rate hike", "interest rate cut",
        "inflation spike", "recession",
        "currency crisis",
        "sanctions", "trade war"
    ]

    # 🟡 Market-wide reaction language (NEVER macro)
    market_reaction_terms = [
        "sensex", "nifty",
        "top loser", "selling pressure",
        "gap-down", "market drag",
        "dragging the index"
    ]

    # 🔵 Company & earnings language
    company_triggers = [
        "earnings", "profit", "missed",
        "revenue", "results", "q3",
        "guidance", "segment",
        "retail", "jio",
        "oil-to-chemicals",
        "gdr slipped", "ipo"
    ]

    macro_hit = any(k in summary for k in macro_triggers)
    company_hit = any(k in summary for k in company_triggers)
    market_hit = any(k in summary for k in market_reaction_terms)

    # 🚫 HARD BLOCK: earnings context disables macro
    if macro_hit and not company_hit:
        state["risk_type"] = "macro"
        state["exogenous_shock"] = True
        state["context_alignment"] = "supports_model"
        state["confidence_modifier"] = "increase"

    else:
        # Everything else is endogenous
        state["risk_type"] = "company"
        state["exogenous_shock"] = False
        state["context_alignment"] = "neutral"
        state["confidence_modifier"] = "unchanged"

    return state




# ----------------------------
# LLM summarizer (Google Gemini)
# ----------------------------
def summarize_news(state: ContextState) -> ContextState:
    """
    Summarize news if available.
    If no relevant news exists, explicitly state that.
    """

    if not state["news"]:
        state["summary"] = (
            f"No time-aligned news was found around {state['date']} "
            f"to explain volatility in {state['ticker']}. "
            "The volatility signal may be driven by endogenous market dynamics."
        )
        return state

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2
    )

    prompt = f"""
You are given news headlines published around {state['date']}.

IMPORTANT:
- Base your reasoning strictly on the provided headlines.
- If the headlines are insufficient to explain volatility, explicitly state that.
- Do NOT infer context from outdated events.

Summarize possible drivers of stock volatility for {state['ticker']}.
"""

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="\n".join(state["news"]))
    ]

    response = llm.invoke(messages)
    state["summary"] = response.content
    return state

def reconcile_signal(state: ContextState) -> ContextState:
    if state["risk_bucket"] == "high" and state["exogenous_shock"]:
        state["final_signal"] = "high_risk_avoid"

    elif state["risk_bucket"] == "high":
        state["final_signal"] = "high_risk_monitor"

    elif state["risk_bucket"] == "medium":
        state["final_signal"] = "monitor"

    else:
        state["final_signal"] = "stable"

    return state



# ----------------------------
# Build agent graph
# ----------------------------

def build_agent():
    graph = StateGraph(ContextState)

    graph.add_node("fetch_news", fetch_news)
    graph.add_node("summarize", summarize_news)
    graph.add_node("classify", classify_context)
    graph.add_node("reconcile", reconcile_signal)  # ✅ ADD THIS

    graph.set_entry_point("fetch_news")

    graph.add_edge("fetch_news", "summarize")
    graph.add_edge("summarize", "classify")
    graph.add_edge("classify", "reconcile")  # ✅ ADD THIS

    return graph.compile()



def run_pipeline(ticker: str) -> dict:
    """
    Run full ML + agent pipeline for a given ticker.
    Returns final JSON report.
    """
    import pandas as pd
    from datetime import date
    from src.model_inference import predict_volatility
    from src.report_builder import build_final_report

    FEATURES = [
        "log_return",
        "vol_past",
        "Volume",
        "vol_percentile",
        "vol_compression",
        "trend_strength"
    ]

    df = pd.read_parquet("data/processed/reliance_labeled.parquet")

    model_out = predict_volatility(ticker)

    agent = build_agent()
    state = agent.invoke({
        "ticker": ticker.upper(),
        "date": date.today().isoformat(),
        "news": [],
        "summary": "",
        "risk_score": model_out["risk_score"],
        "risk_bucket": model_out["risk_bucket"],
        "risk_type": "",
        "exogenous_shock": False,
        "context_alignment": "",
        "confidence_modifier": "",
        "final_signal": ""
    })

    return build_final_report(state)


# ----------------------------
# Run agent
# ----------------------------
if __name__ == "__main__":

    from datetime import date
    import pandas as pd

    FEATURES = [
        "log_return",
        "vol_past",
        "Volume",
        "vol_percentile",
        "vol_compression",
        "trend_strength"
    ]

    df = pd.read_parquet("data/processed/reliance_labeled.parquet")

    model_out = predict_volatility(df, FEATURES)



    agent = build_agent()


    result = agent.invoke({
    "ticker": "RELIANCE.NS",
    "date": date.today().isoformat(),  # ✅ TODAY, EXPLICIT
    "news": [],
    "summary": "",
    "risk_type": "",
    "exogenous_shock": False,
    "context_alignment": "",
    "confidence_modifier": "",
    "risk_score": model_out["risk_score"],
    "risk_bucket": model_out["risk_bucket"],
    "final_signal": ""
    })





    print("\n===== AGENT OUTPUT =====")
    print("Summary:\n", result["summary"])
    print("\nContext Classification:")
    print("Risk type:", result["risk_type"])
    print("Exogenous shock:", result["exogenous_shock"])
    print("Context alignment:", result["context_alignment"])
    print("Confidence modifier:", result["confidence_modifier"])



    final_report = build_final_report(result)

    print("\n===== FINAL JSON REPORT =====")
    print(json.dumps(final_report, indent=2))

    '''print("\n===== FINAL SYSTEM OUTPUT =====")
    print("Date:", result["date"])
    print("Ticker:", result["ticker"])
    print("Model risk score:", result["risk_score"])
    print("Risk bucket:", result["risk_bucket"])
    print("Final signal:", result["final_signal"])
    print("\nExplanation:\n", result["summary"])
    '''

