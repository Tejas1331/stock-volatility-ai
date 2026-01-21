"use client";

import { useState } from "react";
import { analyzeStock } from "../lib/api";
import RiskBadge from "../components/RiskBadge";
import MetricCard from "../components/MetricCard";
import JsonViewer from "../components/JsonViewer";

const STOCKS = [
  { label: "Reliance Industries", value: "RELIANCE" },
  { label: "Tata Consultancy Services", value: "TCS" },
  { label: "Infosys", value: "INFY" },
  { label: "HDFC Bank", value: "HDFCBANK" },
  { label: "ICICI Bank", value: "ICICIBANK" },
];

export default function Home() {
  const [ticker, setTicker] = useState("RELIANCE");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runAnalysis = async () => {
    setLoading(true);
    setError("");
    setData(null);

    try {
      const result = await analyzeStock(ticker);
      setData(result);
    } catch (e: any) {
      setError(e.message || "Failed to analyze stock");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 p-8">
      <div className="max-w-6xl mx-auto space-y-14">

        {/* ================= HERO ================= */}
        <section className="bg-white/95 backdrop-blur rounded-3xl shadow-2xl p-12 space-y-10">

          {/* Header */}
          <div className="space-y-4">
            <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight">
              Stock Volatility Intelligence
            </h1>
            <p className="text-gray-600 text-lg max-w-3xl">
              Probabilistic volatility risk signals powered by regime-aware
              machine learning and real-time market context.
            </p>
          </div>

          {/* Controls */}
          <div className="flex flex-col md:flex-row gap-8 items-start md:items-end">

            {/* Dropdown */}
            <div className="flex flex-col w-72">
              <label className="text-sm font-medium text-gray-600 mb-2">
                Select NSE Stock
              </label>
              <select
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                className="
                  border border-gray-300 rounded-xl px-4 py-3 text-lg
                  bg-white shadow-sm
                  focus:outline-none focus:ring-2 focus:ring-indigo-500
                "
              >
                {STOCKS.map((stock) => (
                  <option key={stock.value} value={stock.value}>
                    {stock.label}
                  </option>
                ))}
              </select>
            </div>

            {/* CTA */}
            <button
              onClick={runAnalysis}
              disabled={loading}
              className={`
                px-10 py-4 rounded-xl text-lg font-semibold text-white
                shadow-xl transition-all
                ${
                  loading
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-indigo-600 hover:bg-indigo-700 hover:scale-[1.02]"
                }
              `}
            >
              {loading ? "Analyzing…" : "Analyze Volatility"}
            </button>
          </div>

          {/* Disclaimer */}
          <p className="text-sm text-gray-500">
            Signals indicate short-term volatility expansion risk.
            This is not price prediction or investment advice.
          </p>
        </section>

        {/* ================= STATUS ================= */}
        {!data && !loading && !error && (
          <p className="text-center text-gray-400">
            Choose a stock to generate an AI-driven volatility risk report.
          </p>
        )}

        {loading && (
          <p className="text-center text-indigo-300 font-medium">
            Evaluating market regimes and contextual signals…
          </p>
        )}

        {error && (
          <p className="text-center text-red-400 font-medium">
            {error}
          </p>
        )}

        {/* ================= RESULTS ================= */}
        {data && (
          <section className="bg-white rounded-3xl shadow-xl p-10 space-y-10">

            {/* Metrics */}
            <div className="flex flex-wrap gap-8 items-center">
              <MetricCard
                label="Final Signal"
                value={data.final_decision.signal}
              />
              <MetricCard
                label="Confidence"
                value={data.final_decision.confidence}
              />

              <div className="flex flex-col">
                <span className="text-sm text-gray-500 mb-1">
                  Risk Bucket
                </span>
                <RiskBadge risk={data.model.risk_bucket} />
              </div>
            </div>

            {/* Explanation */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Model + Context Explanation
              </h2>
              <p className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                {data.explanation.summary}
              </p>
            </div>

            {/* Raw JSON */}
            <details className="pt-4">
              <summary className="cursor-pointer font-semibold text-gray-700 hover:text-indigo-600">
                View full JSON report
              </summary>
              <div className="mt-4">
                <JsonViewer data={data} />
              </div>
            </details>

          </section>
        )}
      </div>
    </main>
  );
}
