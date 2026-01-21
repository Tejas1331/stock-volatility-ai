export async function analyzeStock(ticker: string) {
    const res = await fetch(
      `http://127.0.0.1:8000/analyze?ticker=${ticker}`
    );
  
    if (!res.ok) {
      throw new Error("Failed to fetch analysis");
    }
  
    return res.json();
  }
  