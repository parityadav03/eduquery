import { useState, useEffect, useRef } from "react"
import axios from "axios"

const API = "http://localhost:8000"

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const bottomRef = useRef(null)

  useEffect(() => {
    axios.get(`${API}/session`).then(r => setSessionId(r.data.session_id))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const ask = async () => {
    if (!input.trim() || loading) return
    const question = input.trim()
    setInput("")
    setMessages(m => [...m, { role: "user", text: question }])
    setLoading(true)

    try {
      const res = await axios.post(`${API}/query`, {
        session_id: sessionId,
        question
      })
      setMessages(m => [...m, {
        role: "bot",
        text: res.data.answer,
        sources: res.data.sources,
        latency: res.data.latency_ms
      }])
      setHistory(h => [{ question, answer: res.data.answer }, ...h])
    } catch {
      setMessages(m => [...m, { role: "bot", text: "Something went wrong. Please try again." }])
    }
    setLoading(false)
  }

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "sans-serif", background: "#0f172a", color: "#e2e8f0" }}>

      {/* Sidebar */}
      <div style={{ width: 260, background: "#1e293b", padding: "1rem", overflowY: "auto", borderRight: "1px solid #334155" }}>
        <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 16, color: "#7c3aed" }}>EduQuery</div>
        <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>Recent questions</div>
        {history.length === 0 && <div style={{ fontSize: 12, color: "#475569" }}>No history yet</div>}
        {history.map((h, i) => (
          <div key={i} style={{ fontSize: 12, padding: "8px 10px", background: "#0f172a", borderRadius: 8, marginBottom: 6, color: "#cbd5e1", cursor: "pointer" }}
            onClick={() => setInput(h.question)}>
            {h.question.slice(0, 50)}...
          </div>
        ))}
      </div>

      {/* Main chat */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>

        {/* Header */}
        <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid #1e293b", background: "#1e293b", display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", background: "#7c3aed", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14 }}>E</div>
          <div>
            <div style={{ fontWeight: 600 }}>EduQuery</div>
            <div style={{ fontSize: 11, color: "#22c55e" }}>● RAG-powered academic tutor</div>
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "1.5rem", display: "flex", flexDirection: "column", gap: 16 }}>
          {messages.length === 0 && (
            <div style={{ textAlign: "center", color: "#475569", marginTop: "4rem" }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>📚</div>
              <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>Ask anything from your documents</div>
              <div style={{ fontSize: 13 }}>Powered by LLaMA 3 + RAG</div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
              <div style={{
                maxWidth: "70%", padding: "12px 16px", borderRadius: 12,
                background: m.role === "user" ? "#7c3aed" : "#1e293b",
                fontSize: 14, lineHeight: 1.6
              }}>
                <div>{m.text}</div>
                {m.sources && (
                  <div style={{ marginTop: 10, paddingTop: 8, borderTop: "1px solid #334155" }}>
                    <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 4 }}>Sources</div>
                    {m.sources.map((s, j) => (
                      <div key={j} style={{ fontSize: 11, color: "#7c3aed", background: "#0f172a", padding: "2px 8px", borderRadius: 4, display: "inline-block", marginRight: 4, marginBottom: 2 }}>{s}</div>
                    ))}
                    <div style={{ fontSize: 10, color: "#475569", marginTop: 4 }}>{m.latency}ms</div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: "flex" }}>
              <div style={{ background: "#1e293b", padding: "12px 16px", borderRadius: 12, fontSize: 14, color: "#94a3b8" }}>
                Thinking...
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={{ padding: "1rem 1.5rem", borderTop: "1px solid #1e293b", display: "flex", gap: 10 }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && ask()}
            placeholder="Ask a question from your documents..."
            style={{ flex: 1, padding: "12px 16px", borderRadius: 10, border: "1px solid #334155", background: "#1e293b", color: "#e2e8f0", fontSize: 14, outline: "none" }}
          />
          <button onClick={ask} disabled={loading}
            style={{ padding: "12px 20px", borderRadius: 10, background: "#7c3aed", color: "#fff", border: "none", cursor: "pointer", fontWeight: 600, fontSize: 14 }}>
            Ask
          </button>
        </div>
      </div>
    </div>
  )
}