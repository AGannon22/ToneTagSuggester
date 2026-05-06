import { useState, useEffect } from "react";

const API_URL = "http://localhost:8000";

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("Checking API...");
  const [statusColor, setStatusColor] = useState("orange");
  const [loading, setLoading] = useState(false);
  const [bgColor, setBgColor] = useState("#49266e");
  const [cardBgColor, setCardBgColor] = useState("#fde7ff");
  const colors = ["#7f7f7f", "#b37777", "#445666", "#477e5a", "#49266e"];
  const cardColors = ["#fff", "#fff8e6", "#f7f7ff", "#e6ffe6", "#fde7ff"];

const toggleBgColor = () => {
  const currentIndex = colors.indexOf(bgColor);
  const cardIDX = cardColors.indexOf(cardBgColor);
  setBgColor(colors[(currentIndex + 1) % colors.length]);
  setCardBgColor(cardColors[(cardIDX + 1) % cardColors.length]);
};

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
    <div style={{ minHeight: "100vh", width: "100%", backgroundColor: bgColor, padding: "20px", boxSizing: "border-box", transition: "background-color 0.3s" }}>
      <div style={{ maxWidth: 330, margin: "0 auto", fontFamily: "Arial, sans-serif", backgroundColor: cardBgColor, padding: "20px", borderRadius: "12px", boxShadow: "0 10px 30px rgba(0,0,0,0.08)" }}>
        <h2>Tone Classifier</h2>

        <button
          onClick={toggleBgColor}
          style={{
            marginBottom: 15,
            padding: "8px 12px",
            fontSize: 12,
            cursor: "pointer",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "4px",
          }}
        >
          Change Card Color
        </button>

        <textarea
          rows={5}
          style={{ width: "100%", padding: 8, fontSize: 14, boxSizing: "border-box", backgroundColor:"f5f5f5" }}
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
    </div>
  );
}