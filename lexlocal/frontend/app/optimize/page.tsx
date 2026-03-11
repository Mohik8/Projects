"use client";

import { useState, useRef, useCallback, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Scale, Play, Zap, TrendingUp, CheckCircle, Loader2, AlertTriangle, Code2 } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { createGASocket, fetchBylaws, type GAGeneration } from "@/lib/api";

interface Dimension {
  name: string;
  label: string;
  unit: string;
  min: number;
  max: number;
  value: number;
  step: number;
}

const DEFAULT_DIMS: Dimension[] = [
  { name: "noise_level_db", label: "Noise Level", unit: "dB", min: 40, max: 90, value: 75, step: 1 },
  { name: "start_hour", label: "Start Time", unit: "hr (24h)", min: 0, max: 23, value: 7, step: 0.5 },
  { name: "end_hour", label: "End Time", unit: "hr (24h)", min: 0, max: 23, value: 23, step: 0.5 },
  { name: "distance_m", label: "Distance from Boundary", unit: "m", min: 0, max: 100, value: 1, step: 1 },
  { name: "guests", label: "Max Guests / Night", unit: "persons", min: 1, max: 20, value: 8, step: 1 },
];

const MUNICIPALITIES = ["Victoria", "Saanich", "Esquimalt", "Oak Bay", "Sooke", "Langford"];

function formatHour(h: number) {
  const hh = Math.floor(h);
  const mm = h % 1 === 0.5 ? "30" : "00";
  const ap = hh < 12 ? "AM" : "PM";
  return `${((hh - 1) % 12) + 1}:${mm} ${ap}`;
}

function ChromosomeBar({ values, dims }: { values: number[]; dims: Dimension[] }) {
  return (
    <div style={{ display: "grid", gap: "0.4rem" }}>
      {dims.map((d, i) => {
        const pct = ((values[i] ?? d.value) - d.min) / (d.max - d.min);
        return (
          <div key={d.name} style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <div style={{ width: 130, fontSize: "0.72rem", color: "var(--muted)", textAlign: "right", flexShrink: 0 }}>{d.label}</div>
            <div style={{ flex: 1, height: 8, background: "var(--border)", borderRadius: 99, overflow: "hidden" }}>
              <motion.div
                animate={{ width: `${Math.min(100, Math.max(0, pct * 100))}%` }}
                transition={{ duration: 0.25 }}
                style={{ height: "100%", background: "linear-gradient(90deg, var(--accent), var(--accent-2))", borderRadius: 99 }}
              />
            </div>
            <div style={{ width: 70, fontSize: "0.72rem", color: "var(--foreground)", flexShrink: 0 }}>
              {d.name.includes("hour") ? formatHour(values[i] ?? d.value) : `${(values[i] ?? d.value).toFixed(1)} ${d.unit}`}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function OptimizeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [dims, setDims] = useState<Dimension[]>(DEFAULT_DIMS);
  const [municipality, setMunicipality] = useState(searchParams.get("m") || "Victoria");
  const [category, setCategory] = useState(searchParams.get("cat") || "Noise");
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);
  const [chartData, setChartData] = useState<{ gen: number; best: number; avg: number }[]>([]);
  const [currentGen, setCurrentGen] = useState<GAGeneration | null>(null);
  const [finalSuggestion, setFinalSuggestion] = useState<GAGeneration | null>(null);
  const [error, setError] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  const handleDimChange = (i: number, val: number) => {
    setDims(prev => { const d = [...prev]; d[i] = { ...d[i], value: val }; return d; });
  };

  const startGA = useCallback(async () => {
    setRunning(true);
    setDone(false);
    setChartData([]);
    setCurrentGen(null);
    setFinalSuggestion(null);
    setError("");

    // Load bylaws for selected municipality/category to pass as context
    let bylawIds: string[] = [];
    try {
      const data = await fetchBylaws(municipality, category);
      bylawIds = data.bylaws.map((b) => b.id);
    } catch { /* fallback fine */ }

    const sessionId = crypto.randomUUID();
    const payload = {
      dimensions: dims.map(d => ({ name: d.name, original: d.value, min_val: d.min, max_val: d.max, unit: d.unit, weight: 1.0 })),
      municipality,
      category,
      bylaw_ids: bylawIds,
    };

    wsRef.current = createGASocket(
      sessionId,
      payload,
      (gen: GAGeneration) => {
        setCurrentGen(gen);
        setChartData(prev => [...prev, { gen: gen.generation, best: gen.best_fitness, avg: gen.avg_fitness }]);
      },
      (final: GAGeneration) => {
        setFinalSuggestion(final);
        setRunning(false);
        setDone(true);
      },
      (e: string) => {
        setError(e);
        setRunning(false);
      }
    );
  }, [dims, municipality, category]);

  const stopGA = () => {
    wsRef.current?.close();
    setRunning(false);
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
          color: "var(--muted)", background: "none", border: "none", cursor: "pointer",
        }}>
          <Scale size={18} color="var(--accent)" />
          <span className="gradient-text" style={{ fontWeight: 700 }}>LexLocal</span>
        </button>
        <span style={{ fontSize: "0.85rem", color: "var(--muted)" }}>GA Penalty Optimizer</span>
      </nav>

      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem" }}>
        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ fontSize: "1.7rem", fontWeight: 800, marginBottom: "0.4rem" }}>
            <span className="gradient-text">GA Penalty Optimizer</span>
          </h1>
          <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
            Set your activity parameters below. The genetic algorithm will evolve the minimum adjustments needed to comply with local bylaws.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: "1.5rem", alignItems: "start" }}>
          {/* Left: Config */}
          <div>
            <div className="card" style={{ marginBottom: "1rem" }}>
              <h2 style={{ fontWeight: 700, fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", marginBottom: "1rem" }}>
                Context
              </h2>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <div>
                  <label style={{ fontSize: "0.78rem", color: "var(--muted)", display: "block", marginBottom: "0.35rem" }}>Municipality</label>
                  <select className="input" value={municipality} onChange={e => setMunicipality(e.target.value)} disabled={running}>
                    {MUNICIPALITIES.map(m => <option key={m} value={m}>{m}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: "0.78rem", color: "var(--muted)", display: "block", marginBottom: "0.35rem" }}>Category</label>
                  <select className="input" value={category} onChange={e => setCategory(e.target.value)} disabled={running}>
                    {["Noise", "Short-Term Rentals", "Cycling", "Fire & Burning", "Animals", "Business"].map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="card" style={{ marginBottom: "1rem" }}>
              <h2 style={{ fontWeight: 700, fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--muted)", marginBottom: "1rem" }}>
                Activity Parameters
              </h2>
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {dims.map((d, i) => (
                  <div key={d.name}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                      <label style={{ fontSize: "0.8rem", color: "var(--foreground)" }}>{d.label}</label>
                      <span style={{ fontSize: "0.78rem", color: "var(--accent-2)", fontWeight: 600 }}>
                        {d.name.includes("hour") ? formatHour(d.value) : `${d.value} ${d.unit}`}
                      </span>
                    </div>
                    <input type="range" min={d.min} max={d.max} step={d.step} value={d.value}
                      onChange={e => handleDimChange(i, parseFloat(e.target.value))}
                      disabled={running}
                      style={{ width: "100%", accentColor: "var(--accent)", cursor: running ? "not-allowed" : "pointer" }} />
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.65rem", color: "var(--muted)", marginTop: "0.1rem" }}>
                      <span>{d.min}</span><span>{d.max}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button className="btn-primary"
              onClick={running ? stopGA : startGA}
              style={{ width: "100%", justifyContent: "center", gap: "0.5rem",
                background: running ? "rgba(239,68,68,0.2)" : "linear-gradient(135deg, var(--accent), var(--accent-2))",
                border: running ? "1px solid rgba(239,68,68,0.4)" : "none", fontSize: "0.95rem", padding: "0.75rem",
              }}>
              {running ? <><Loader2 size={16} style={{ animation: "spin 1s linear infinite" }} /> Stop</> : <><Play size={16} /> Run GA Optimizer</>}
            </button>
          </div>

          {/* Right: Visualization */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {error && (
              <div style={{
                background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
                borderRadius: 10, padding: "1rem",
                display: "flex", gap: "0.6rem", alignItems: "flex-start", color: "#fca5a5",
              }}>
                <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                <span style={{ fontSize: "0.85rem" }}>{error}. Is the backend running? <code>cd backend &amp;&amp; uvicorn main:app --reload --port 8000</code></span>
              </div>
            )}

            {/* Status bar */}
            <div className="card" style={{ display: "flex", gap: "2rem", padding: "1rem 1.25rem" }}>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: "1.6rem", fontWeight: 800, fontVariantNumeric: "tabular-nums", color: "var(--accent)" }}>
                  {currentGen?.generation ?? 0}<span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>/60</span>
                </div>
                <div style={{ fontSize: "0.72rem", color: "var(--muted)" }}>Generation</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: "1.6rem", fontWeight: 800, fontVariantNumeric: "tabular-nums", color: "var(--accent-2)" }}>
                  {currentGen ? Math.abs(currentGen.best_fitness).toFixed(1) : "—"}
                </div>
                <div style={{ fontSize: "0.72rem", color: "var(--muted)" }}>Penalty Score</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: "1.6rem", fontWeight: 800, fontVariantNumeric: "tabular-nums", color: currentGen?.violations === 0 ? "#10b981" : "#f59e0b" }}>
                  {currentGen?.violations ?? "—"}
                </div>
                <div style={{ fontSize: "0.72rem", color: "var(--muted)" }}>Violations</div>
              </div>
              <div style={{ flex: 1, textAlign: "right" }}>
                {running && <span style={{ fontSize: "0.75rem", color: "var(--accent)", animation: "pulse 1.5s infinite" }}>● Evolving...</span>}
                {done && <span style={{ fontSize: "0.75rem", color: "#10b981" }}>✓ Converged</span>}
              </div>
            </div>

            {/* Fitness chart */}
            <div className="card">
              <h3 style={{ fontWeight: 600, fontSize: "0.85rem", color: "var(--muted)", marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <TrendingUp size={14} /> Fitness Convergence
              </h3>
              {chartData.length === 0 ? (
                <div style={{ height: 220, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--muted)", fontSize: "0.85rem" }}>
                  Run the optimizer to see evolution data
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="gen" tick={{ fill: "var(--muted)", fontSize: 11 }} />
                    <YAxis tick={{ fill: "var(--muted)", fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8 }}
                      labelStyle={{ color: "var(--muted)" }}
                      itemStyle={{ color: "var(--foreground)" }}
                    />
                    <Legend wrapperStyle={{ fontSize: "0.75rem", color: "var(--muted)" }} />
                    <Line type="monotone" dataKey="best" stroke="#6c63ff" strokeWidth={2} dot={false} name="Best Fitness" />
                    <Line type="monotone" dataKey="avg" stroke="#00d4aa" strokeWidth={1.5} dot={false} strokeDasharray="4 2" name="Avg Fitness" />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Live best chromosome */}
            {currentGen?.best_chromosome && (
              <div className="card">
                <h3 style={{ fontWeight: 600, fontSize: "0.85rem", color: "var(--muted)", marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <Zap size={14} /> Best Chromosome
                </h3>
                <ChromosomeBar values={currentGen.best_chromosome} dims={dims} />
              </div>
            )}

            {/* Final suggestion */}
            <AnimatePresence>
              {done && finalSuggestion && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  className="card glow-teal"
                >
                  <h3 style={{ fontWeight: 700, fontSize: "0.95rem", marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <CheckCircle size={16} color="#00d4aa" /> Optimal Compliant Configuration
                  </h3>
                  {finalSuggestion.suggestion && (
                    <p style={{ fontSize: "0.88rem", color: "var(--accent-2)", marginBottom: "1rem", lineHeight: 1.6 }}>
                      {finalSuggestion.suggestion}
                    </p>
                  )}
                  <ChromosomeBar values={finalSuggestion.best_chromosome} dims={dims} />
                  <div style={{ marginTop: "1rem", padding: "0.75rem", background: "var(--surface-2)", borderRadius: 8 }}>
                    <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginBottom: "0.4rem", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                      <Code2 size={12} /> Raw Chromosome
                    </div>
                    <code style={{ fontSize: "0.7rem", color: "var(--accent)", wordBreak: "break-all" }}>
                      [{finalSuggestion.best_chromosome.map(v => v.toFixed(2)).join(", ")}]
                    </code>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function OptimizePage() {
  return (
    <Suspense>
      <OptimizeContent />
    </Suspense>
  );
}
