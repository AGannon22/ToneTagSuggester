import { useState, useEffect } from "react";

const API_URL = "http://localhost:8000";

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("Checking API...");
  const [statusColor, setStatusColor] = useState("orange");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch(`${API_URL}/health`);
        const data = await res.json();
        if (data.model_loaded) {
          setStatus("API connected — model ready");
          setStatusColor("green");
        } else {
          setStatus("API connected — model not loaded");
          setStatusColor("orange");
        }
      } catch {
        setStatus("Cannot reach API at localhost:8000");
        setStatusColor("red");
      }
    }
    checkHealth();
  }, []);

  async function predictTone() {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();

      if (res.ok) {
        setResult({ tone: data.predicted_tone, number: data.predicted_number });
      } else {
        setResult({ error: data.detail });
      }
    } catch {
      setResult({ error: "Request failed — is api.py running?" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 330, margin: "30px auto", fontFamily: "Arial, sans-serif" }}>
      <h2>Tone Classifier</h2>

      <textarea
        rows={5}
        style={{ width: "120%", padding: 8, fontSize: 14, boxSizing: "border-box" }}
        placeholder="Enter text to classify..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button
        onClick={predictTone}
        disabled={loading || !text.trim()}
        style={{ marginTop: 10, width: "100%", padding: 10, fontSize: 15, cursor: "pointer" }}
      >
        {loading ? "Predicting..." : "Predict Tone"}
      </button>

      {result && (
        <p style={{ marginTop: 16, fontSize: 16, color: result.error ? "red" : "#222" }}>
          {result.error
            ? `Error: ${result.error}`
            : `Predicted Tone: ${result.tone} (${result.number})`}
        </p>
      )}

      <p style={{ marginTop: 12, fontSize: 12, color: statusColor }}>{status}</p>
    </div>
  );
}