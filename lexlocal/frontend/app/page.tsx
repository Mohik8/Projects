"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Scale, ArrowRight } from "lucide-react";

const EXAMPLES = [
  "Airbnb in a Saanich condo",
  "Backyard fire pit in Sooke",
  "Construction noise hours in Langford",
  "Cycling fine in Esquimalt",
  "Short-term rentals in Oak Bay",
];

const MUNICIPALITIES = ["Victoria", "Saanich", "Esquimalt", "Oak Bay", "Sooke", "Langford"];

const STEPS = [
  { n: "01", title: "Ask anything", desc: "Describe your situation in plain English. No legal jargon needed." },
  { n: "02", title: "AI finds bylaws", desc: "Gemini matches your query against the relevant municipal bylaw corpus." },
  { n: "03", title: "Optimize if needed", desc: "If violations are found, a genetic algorithm evolves the minimum parameter changes to make your plan compliant." },
];

export default function HomePage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [municipality, setMunicipality] = useState("");

  const handleSearch = (q?: string) => {
    const finalQuery = q || query;
    if (!finalQuery.trim()) return;
    const params = new URLSearchParams({ q: finalQuery });
    if (municipality) params.set("m", municipality);
    router.push(`/query?${params}`);
  };

  const PAD = "0 max(2rem, 6vw)";

  return (
    <div style={{ minHeight: "100vh", background: "var(--background)", color: "var(--foreground)" }}>

      {/* Nav */}
      <nav style={{
        borderBottom: "1px solid var(--border)",
        padding: PAD,
        height: 52,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        background: "var(--background)",
        zIndex: 50,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
          <Scale size={14} strokeWidth={1.5} color="var(--accent)" />
          <span style={{ fontWeight: 600, fontSize: "0.88rem", letterSpacing: "-0.01em" }}>LexLocal</span>
        </div>
        <div style={{ display: "flex", gap: "2.5rem", alignItems: "center" }}>
          <a href="/bylaws" style={{ color: "var(--muted)", fontSize: "0.82rem" }}>Bylaws</a>
          <a href="/optimize" style={{ color: "var(--muted)", fontSize: "0.82rem" }}>Optimizer</a>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ padding: `clamp(4rem, 10vh, 8rem) max(2rem, 6vw) clamp(3rem, 6vh, 5rem)` }}>
        <div style={{
          fontSize: "0.65rem",
          color: "var(--muted)",
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          fontFamily: "monospace",
          marginBottom: "2.5rem",
        }}>
          British Columbia · Vancouver Island
        </div>

        <h1 style={{
          fontSize: "clamp(3rem, 7vw, 5.5rem)",
          fontWeight: 800,
          lineHeight: 1.0,
          letterSpacing: "-0.045em",
          marginBottom: "2rem",
          maxWidth: "16ch",
        }}>
          Local bylaws,<br />
          <span style={{ color: "var(--accent)" }}>plain English.</span>
        </h1>

        <p style={{ color: "var(--muted)", fontSize: "0.95rem", marginBottom: "3rem", lineHeight: 1.7, maxWidth: "46ch" }}>
          Ask anything about Victoria, Saanich, Esquimalt, Oak Bay,{" "}
          Sooke, and Langford municipal bylaws. If your plan violates something,
          the GA optimizer finds the minimum fix.
        </p>

        {/* Search — raised container */}
        <div style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: 8,
          padding: "1rem",
          maxWidth: 640,
        }}>
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem" }}>
            <input
              className="input"
              placeholder="e.g. Can I run an Airbnb in my Saanich condo?"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              style={{ flex: 1, fontSize: "0.88rem" }}
            />
            <select
              className="input"
              value={municipality}
              onChange={e => setMunicipality(e.target.value)}
              style={{ width: 132, flex: "none" }}
            >
              <option value="">All areas</option>
              {MUNICIPALITIES.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
            <button className="btn-primary" onClick={() => handleSearch()} style={{ padding: "0.6rem 1rem" }}>
              <Search size={14} />
            </button>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
            <span style={{ fontSize: "0.68rem", color: "var(--muted)", alignSelf: "center", marginRight: "0.2rem" }}>Try:</span>
            {EXAMPLES.map(ex => (
              <button key={ex} onClick={() => handleSearch(ex)} style={{
                background: "var(--surface-2)",
                border: "1px solid var(--border)",
                borderRadius: 4,
                padding: "0.22rem 0.6rem",
                color: "var(--muted)",
                fontSize: "0.71rem",
                cursor: "pointer",
                transition: "border-color 0.12s, color 0.12s",
              }}
                onMouseEnter={e => { const el = e.currentTarget; el.style.borderColor = "#484848"; el.style.color = "var(--foreground)"; }}
                onMouseLeave={e => { const el = e.currentTarget; el.style.borderColor = "var(--border)"; el.style.color = "var(--muted)"; }}
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Info band — contrasting background */}
      <section style={{ background: "var(--surface)", borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)" }}>
        <div style={{
          padding: `3.5rem max(2rem, 6vw)`,
          display: "grid",
          gridTemplateColumns: "240px 1px 1fr",
          gap: "4rem",
          maxWidth: 920,
        }}>

          {/* Coverage list */}
          <div>
            <div style={{
              fontSize: "0.62rem", color: "var(--muted)", letterSpacing: "0.1em",
              textTransform: "uppercase", fontFamily: "monospace", marginBottom: "1.25rem",
            }}>Coverage</div>
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "0" }}>
              {MUNICIPALITIES.map((m, i) => (
                <li key={m} style={{
                  display: "flex", alignItems: "center", gap: "0.7rem",
                  fontSize: "0.88rem",
                  padding: "0.5rem 0",
                  borderBottom: i < MUNICIPALITIES.length - 1 ? "1px solid var(--border)" : "none",
                }}>
                  {m}
                  <span style={{
                    marginLeft: "auto", fontSize: "0.62rem", fontFamily: "monospace",
                    color: "var(--background)", background: "var(--accent)",
                    padding: "0.1rem 0.35rem", borderRadius: 3,
                  }}>BC</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Vertical divider */}
          <div style={{ background: "var(--border)", width: 1, alignSelf: "stretch" }} />

          {/* How it works */}
          <div>
            <div style={{
              fontSize: "0.62rem", color: "var(--muted)", letterSpacing: "0.1em",
              textTransform: "uppercase", fontFamily: "monospace", marginBottom: "1.25rem",
            }}>How it works</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
              {STEPS.map((s, i) => (
                <div key={s.n} style={{
                  display: "flex", gap: "1.5rem",
                  padding: "1rem 0",
                  borderBottom: i < STEPS.length - 1 ? "1px solid var(--border)" : "none",
                }}>
                  <span style={{
                    fontFamily: "monospace", fontSize: "0.7rem",
                    color: "var(--accent)", flexShrink: 0, minWidth: 22,
                    paddingTop: "0.2rem",
                  }}>{s.n}</span>
                  <div>
                    <div style={{ fontSize: "0.93rem", fontWeight: 700, marginBottom: "0.3rem", letterSpacing: "-0.01em" }}>{s.title}</div>
                    <div style={{ fontSize: "0.8rem", color: "var(--muted)", lineHeight: 1.65 }}>{s.desc}</div>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={() => router.push("/optimize")}
              style={{
                marginTop: "1.5rem",
                background: "var(--surface-2)",
                border: "1px solid var(--border)",
                borderRadius: 5,
                padding: "0.5rem 0.9rem",
                color: "var(--foreground)",
                fontSize: "0.78rem",
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "0.4rem",
                transition: "background 0.12s",
              }}
              onMouseEnter={e => { e.currentTarget.style.background = "#252525"; }}
              onMouseLeave={e => { e.currentTarget.style.background = "var(--surface-2)"; }}
            >
              Open optimizer <ArrowRight size={11} />
            </button>
          </div>
        </div>
      </section>

      <footer style={{
        borderTop: "1px solid var(--border)",
        padding: `1.25rem max(2rem, 6vw)`,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <span style={{ fontSize: "0.73rem", color: "var(--muted)" }}>LexLocal — Vancouver Island Bylaw Intelligence</span>
        <span style={{ fontSize: "0.68rem", color: "var(--muted)", fontFamily: "monospace" }}>Next.js · FastAPI · Gemini · GA</span>
      </footer>
    </div>
  );
}
