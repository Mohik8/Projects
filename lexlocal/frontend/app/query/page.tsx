"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Scale, Search, ArrowLeft, ArrowRight, MapPin, Tag, AlertCircle, CheckCircle, Loader2, GitBranch } from "lucide-react";
import { queryBylaws, type QueryResponse, type Bylaw } from "@/lib/api";

const CATEGORY_COLORS: Record<string, string> = {
  Noise: "#f59e0b",
  "Short-Term Rentals": "#6c63ff",
  Cycling: "#00d4aa",
  "Fire & Burning": "#ef4444",
  Animals: "#10b981",
  Business: "#3b82f6",
};

function BylawCard({ bylaw }: { bylaw: Bylaw }) {
  const color = CATEGORY_COLORS[bylaw.category] || "#6c63ff";
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="card card-hover"
      style={{ marginBottom: "0.75rem" }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "1rem" }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem", flexWrap: "wrap" }}>
            <span style={{
              background: `${color}20`, border: `1px solid ${color}40`,
              color, borderRadius: 999, padding: "0.2rem 0.6rem", fontSize: "0.72rem", fontWeight: 600,
            }}>
              {bylaw.category}
            </span>
            <span style={{
              background: "rgba(255,255,255,0.05)", border: "1px solid var(--border)",
              color: "var(--muted)", borderRadius: 999, padding: "0.2rem 0.6rem", fontSize: "0.72rem",
              display: "flex", alignItems: "center", gap: "0.3rem",
            }}>
              <MapPin size={10} /> {bylaw.municipality}
            </span>
          </div>
          <h3 style={{ fontWeight: 600, fontSize: "0.95rem", marginBottom: "0.4rem" }}>{bylaw.title}</h3>
          <p style={{ color: "var(--muted)", fontSize: "0.85rem", lineHeight: 1.6 }}>{bylaw.text}</p>
        </div>
      </div>
      <div style={{ marginTop: "0.75rem", display: "flex", gap: "0.35rem", flexWrap: "wrap" }}>
        {bylaw.tags.slice(0, 5).map(tag => (
          <span key={tag} style={{
            background: "var(--surface-2)", border: "1px solid var(--border)",
            borderRadius: 4, padding: "0.15rem 0.5rem", fontSize: "0.7rem", color: "var(--muted)",
            display: "flex", alignItems: "center", gap: "0.25rem",
          }}>
            <Tag size={9} />{tag}
          </span>
        ))}
      </div>
    </motion.div>
  );
}

function QueryContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const q = searchParams.get("q") || "";
  const m = searchParams.get("m") || "";

  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [input, setInput] = useState(q);

  useEffect(() => {
    if (q) runQuery(q, m);
  }, [q, m]);

  async function runQuery(query: string, muni: string) {
    setLoading(true);
    setError("");
    try {
      const data = await queryBylaws(query, muni || undefined);
      setResult(data);
    } catch (e) {
      setError("Could not reach the backend. Make sure the FastAPI server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  const handleSearch = () => {
    if (!input.trim()) return;
    const params = new URLSearchParams({ q: input });
    if (m) params.set("m", m);
    router.push(`/query?${params}`);
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--background)" }}>
      {/* Nav */}
      <nav style={{
        borderBottom: "1px solid var(--border)", padding: "1rem 2rem",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "rgba(5,7,15,0.9)", backdropFilter: "blur(12px)", position: "sticky", top: 0, zIndex: 50,
      }}>
        <button onClick={() => router.push("/")} style={{
          display: "flex", alignItems: "center", gap: "0.5rem",
          color: "var(--muted)", background: "none", border: "none", cursor: "pointer", fontSize: "0.9rem",
        }}>
          <Scale size={18} color="var(--accent)" />
          <span className="gradient-text" style={{ fontWeight: 700 }}>LexLocal</span>
        </button>
      </nav>

      <div style={{ maxWidth: 860, margin: "0 auto", padding: "2rem" }}>
        {/* Search bar */}
        <div style={{ marginBottom: "2rem" }}>
          <div style={{
            display: "flex", gap: "0.75rem",
            background: "var(--surface)", border: "1px solid var(--border)",
            borderRadius: 12, padding: "0.75rem",
          }}>
            <input className="input" value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              placeholder="Ask about any local bylaw..."
              style={{ flex: 1, background: "transparent", border: "none", boxShadow: "none" }} />
            <button className="btn-primary" onClick={handleSearch} disabled={loading}>
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
        </div>

        {error && (
          <div style={{
            background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
            borderRadius: 10, padding: "1rem", marginBottom: "1.5rem",
            display: "flex", gap: "0.75rem", color: "#fca5a5",
          }}>
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
            <span style={{ fontSize: "0.9rem" }}>{error}</span>
          </div>
        )}

        {loading && (
          <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--muted)" }}>
            <Loader2 size={32} style={{ margin: "0 auto 1rem", animation: "spin 1s linear infinite" }} />
            <p>Searching bylaws...</p>
          </div>
        )}

        {result && !loading && (
          <AnimatePresence mode="wait">
            <motion.div key={q} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {/* AI Answer */}
              <div style={{
                background: "linear-gradient(135deg, rgba(108,99,255,0.08), rgba(0,212,170,0.05))",
                border: "1px solid rgba(108,99,255,0.25)",
                borderRadius: 12, padding: "1.5rem", marginBottom: "2rem",
              }}>
                <div style={{ display: "flex", gap: "0.6rem", alignItems: "flex-start" }}>
                  <CheckCircle size={20} color="#00d4aa" style={{ flexShrink: 0, marginTop: 2 }} />
                  <div>
                    <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginBottom: "0.5rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                      AI Answer {result.municipality_detected && `· ${result.municipality_detected}`}
                    </div>
                    <p style={{ lineHeight: 1.7, fontSize: "0.95rem" }}>{result.answer}</p>
                  </div>
                </div>
              </div>

              {/* GA optimizer nudge if violations might exist */}
              {result.matched_bylaws.length > 0 && (
                <div style={{
                  background: "rgba(0,212,170,0.07)", border: "1px solid rgba(0,212,170,0.2)",
                  borderRadius: 10, padding: "1rem 1.25rem", marginBottom: "2rem",
                  display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem",
                }}>
                  <div style={{ display: "flex", gap: "0.6rem", alignItems: "center" }}>
                    <GitBranch size={18} color="#00d4aa" />
                    <span style={{ fontSize: "0.88rem", color: "var(--foreground)" }}>
                      Your plan may violate some constraints — the GA Optimizer can evolve the minimum adjustments to make it legal.
                    </span>
                  </div>
                  <button className="btn-primary" onClick={() => router.push("/optimize")}
                    style={{ background: "linear-gradient(135deg, #00d4aa, #0099cc)", whiteSpace: "nowrap", fontSize: "0.82rem", padding: "0.5rem 1rem" }}>
                    Optimize <ArrowRight size={14} />
                  </button>
                </div>
              )}

              {/* Matched bylaws */}
              {result.matched_bylaws.length > 0 && (
                <div>
                  <h2 style={{ fontWeight: 700, marginBottom: "1rem", fontSize: "1rem", color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    Matched bylaws ({result.matched_bylaws.length})
                  </h2>
                  {result.matched_bylaws.map(b => <BylawCard key={b.id} bylaw={b} />)}
                </div>
              )}

              {result.matched_bylaws.length === 0 && (
                <div style={{ textAlign: "center", padding: "3rem 0", color: "var(--muted)" }}>
                  <p>No specific bylaws matched. Try being more specific about the activity or location.</p>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

export default function QueryPage() {
  return (
    <Suspense>
      <QueryContent />
    </Suspense>
  );
}
