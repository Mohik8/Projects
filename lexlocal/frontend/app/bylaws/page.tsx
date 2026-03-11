"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Scale, MapPin, Tag, Search, Loader2 } from "lucide-react";
import { fetchBylaws, fetchMunicipalities, type Bylaw } from "@/lib/api";

const CATEGORY_COLORS: Record<string, string> = {
  Noise: "#f59e0b",
  "Short-Term Rentals": "#6c63ff",
  Cycling: "#00d4aa",
  "Fire & Burning": "#ef4444",
  Animals: "#10b981",
  Business: "#3b82f6",
};

const CATEGORIES = ["All", "Noise", "Short-Term Rentals", "Cycling", "Fire & Burning", "Animals", "Business"];

export default function BylawsPage() {
  const router = useRouter();
  const [bylaws, setBylaws] = useState<Bylaw[]>([]);
  const [municipalities, setMunicipalities] = useState<string[]>([]);
  const [activeMuni, setActiveMuni] = useState("All");
  const [activeCat, setActiveCat] = useState("All");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchBylaws().then(d => setBylaws(d.bylaws)),
      fetchMunicipalities().then(setMunicipalities),
    ]).finally(() => setLoading(false));
  }, []);

  const filtered = bylaws.filter(b => {
    const matchMuni = activeMuni === "All" || b.municipality === activeMuni;
    const matchCat = activeCat === "All" || b.category === activeCat;
    const matchSearch = !search || b.title.toLowerCase().includes(search.toLowerCase()) || b.text.toLowerCase().includes(search.toLowerCase());
    return matchMuni && matchCat && matchSearch;
  });

  return (
    <div style={{ minHeight: "100vh", background: "var(--background)" }}>
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
        <span style={{ fontSize: "0.85rem", color: "var(--muted)" }}>Bylaw Library</span>
      </nav>

      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "2rem" }}>
        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ fontSize: "1.7rem", fontWeight: 800, marginBottom: "0.4rem" }}>
            <span className="gradient-text">Bylaw Library</span>
          </h1>
          <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
            Browse all {bylaws.length} bylaws across {municipalities.length} Vancouver Island municipalities.
          </p>
        </div>

        {/* Filters */}
        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", flexWrap: "wrap" }}>
            <div style={{ position: "relative", flex: 1, minWidth: 200 }}>
              <Search size={14} style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", color: "var(--muted)", pointerEvents: "none" }} />
              <input className="input" placeholder="Search bylaws..." value={search} onChange={e => setSearch(e.target.value)}
                style={{ paddingLeft: "2rem" }} />
            </div>
          </div>

          {/* Municipality tabs */}
          <div style={{ marginBottom: "0.75rem" }}>
            <div style={{ fontSize: "0.72rem", color: "var(--muted)", marginBottom: "0.4rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>Municipality</div>
            <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
              {["All", ...municipalities].map(m => (
                <button key={m} onClick={() => setActiveMuni(m)}
                  style={{
                    padding: "0.3rem 0.75rem", borderRadius: 999, fontSize: "0.78rem", cursor: "pointer",
                    background: activeMuni === m ? "var(--accent)" : "var(--surface-2)",
                    border: activeMuni === m ? "1px solid var(--accent)" : "1px solid var(--border)",
                    color: activeMuni === m ? "#fff" : "var(--muted)",
                    transition: "all 0.15s",
                  }}>
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Category chips */}
          <div>
            <div style={{ fontSize: "0.72rem", color: "var(--muted)", marginBottom: "0.4rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>Category</div>
            <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
              {CATEGORIES.map(c => {
                const color = CATEGORY_COLORS[c];
                return (
                  <button key={c} onClick={() => setActiveCat(c)}
                    style={{
                      padding: "0.3rem 0.75rem", borderRadius: 999, fontSize: "0.78rem", cursor: "pointer",
                      background: activeCat === c ? (color ? `${color}25` : "var(--accent)") : "var(--surface-2)",
                      border: activeCat === c ? `1px solid ${color || "var(--accent)"}` : "1px solid var(--border)",
                      color: activeCat === c ? (color || "#fff") : "var(--muted)",
                      transition: "all 0.15s",
                    }}>
                    {c}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {loading && (
          <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--muted)" }}>
            <Loader2 size={28} style={{ margin: "0 auto 0.75rem", animation: "spin 1s linear infinite" }} />
            <p>Loading bylaws...</p>
          </div>
        )}

        {!loading && (
          <>
            <div style={{ fontSize: "0.8rem", color: "var(--muted)", marginBottom: "1rem" }}>
              Showing {filtered.length} of {bylaws.length} bylaws
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "0.75rem" }}>
              {filtered.map((b, idx) => {
                const color = CATEGORY_COLORS[b.category] || "#6c63ff";
                return (
                  <motion.div
                    key={b.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.02 }}
                    className="card card-hover"
                  >
                    <div style={{ display: "flex", gap: "0.4rem", marginBottom: "0.6rem", flexWrap: "wrap" }}>
                      <span style={{
                        background: `${color}20`, border: `1px solid ${color}40`,
                        color, borderRadius: 999, padding: "0.15rem 0.5rem", fontSize: "0.68rem", fontWeight: 600,
                      }}>{b.category}</span>
                      <span style={{
                        background: "rgba(255,255,255,0.04)", border: "1px solid var(--border)",
                        color: "var(--muted)", borderRadius: 999, padding: "0.15rem 0.5rem", fontSize: "0.68rem",
                        display: "flex", alignItems: "center", gap: "0.25rem",
                      }}><MapPin size={9} />{b.municipality}</span>
                    </div>
                    <h3 style={{ fontWeight: 600, fontSize: "0.88rem", marginBottom: "0.4rem", lineHeight: 1.4 }}>{b.title}</h3>
                    <p style={{ color: "var(--muted)", fontSize: "0.78rem", lineHeight: 1.55, display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                      {b.text}
                    </p>
                    <div style={{ marginTop: "0.6rem", display: "flex", flexWrap: "wrap", gap: "0.25rem" }}>
                      {b.tags.slice(0, 3).map(t => (
                        <span key={t} style={{
                          background: "var(--surface-2)", border: "1px solid var(--border)",
                          borderRadius: 4, padding: "0.1rem 0.4rem", fontSize: "0.62rem", color: "var(--muted)",
                          display: "flex", alignItems: "center", gap: "0.2rem",
                        }}><Tag size={8} />{t}</span>
                      ))}
                    </div>
                  </motion.div>
                );
              })}
            </div>
            {filtered.length === 0 && (
              <div style={{ textAlign: "center", padding: "3rem 0", color: "var(--muted)" }}>
                No bylaws match your filters.
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
