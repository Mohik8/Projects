"""
Neuroevolution Snake AI - Streamlit Dashboard
=============================================
A genetic algorithm evolves neural-network weights (no backprop) to
play Snake. Watch fitness curves and the best agent improve in real time.
"""

import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from network  import NeuralNetwork
from genetic  import (
    DEFAULT_LAYERS, init_population, evaluate_agent,
    evolve_generation, replay_agent,
)

# ──────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "Neuroevolution Snake AI",
    page_icon   = "🐍",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# Custom CSS - white base with per-section color accents
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #ffffff; }
  .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }

  /* ── Sidebar: deep indigo ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important;
    border-right: none;
  }
  [data-testid="stSidebar"] * { color: #e0e7ff !important; }
  [data-testid="stSidebar"] .stSlider > div > div > div { background: #6366f1 !important; }
  [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }

  /* ── Stats strip ── */
  .stats-strip {
    display: flex; align-items: center; gap: 0;
    background: #fafafa;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 8px; margin-bottom: 12px;
  }
  .stat-item { flex: 1; text-align: center; padding: 0 12px; }
  .stat-item + .stat-item { border-left: 1px solid #e2e8f0; }
  .stat-num { font-size: 1.65rem; font-weight: 700; letter-spacing: -0.5px; line-height: 1.1; }
  .stat-lbl { font-size: 0.68rem; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 3px; }

  /* ── Section wrappers ── */
  .section-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 6px; padding-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
  }
  .section-dot {
    width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
  }
  .section-title {
    font-size: 0.82rem; font-weight: 600; letter-spacing: 0.5px;
    color: #475569; text-transform: uppercase; margin: 0;
  }
  .section-wrap {
    background: #fafafa; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 14px 14px 8px 14px; margin-bottom: 6px;
  }
  h1 { color: #1e293b !important; }
  .stButton > button {
    border-radius: 10px !important; font-weight: 600 !important;
    letter-spacing: 0.5px !important; transition: all 0.2s !important;
  }
  .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(99,102,241,0.25) !important; }
  [data-testid="stMetric"] {
    background: #ffffff; border: 1.5px solid #e8ecf2;
    border-radius: 12px; padding: 12px 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────
# Sidebar - hyperparameters
# ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🐍 NeuroSnake")
    st.caption("Genetic Algorithm · Neuroevolution")
    st.divider()

    st.subheader("Population")
    pop_size     = st.slider("Population size",  20, 500, 150, 10)
    elite_n      = st.slider("Elite agents kept", 1, 20,    3,  1)
    tournament_k = st.slider("Tournament size",   2, 20,    5,  1)

    st.subheader("Mutation")
    mutation_rate = st.slider("Mutation rate",  0.01, 0.50, 0.10, 0.01)
    mutation_std  = st.slider("Mutation σ",     0.01, 1.00, 0.20, 0.01)

    st.subheader("Training")
    max_gens         = st.slider("Max generations",     10, 500, 100, 10)
    n_trials         = st.slider("Trials per agent",     1,   5,   2,   1,
                                  help="Avg over this many episodes to reduce luck")
    max_steps_no_food = st.slider("Max steps without food", 50, 500, 150, 10)
    grid_size        = st.selectbox("Grid size", [10, 15, 20], index=2)

    st.subheader("Network")
    h1 = st.slider("Hidden layer 1", 4, 64, 16, 2)
    h2 = st.slider("Hidden layer 2", 4, 64, 16, 2)
    layer_sizes = [24, h1, h2, 4]
    st.caption(f"Architecture: 24 → {h1} → {h2} → 4")
    n_params = NeuralNetwork(layer_sizes).num_params
    st.caption(f"Trainable params: **{n_params:,}**")

    st.divider()
    start_btn = st.button("▶  Start Training", use_container_width=True,
                          type="primary")
    stop_btn  = st.button("⏹  Stop",           use_container_width=True)

# ──────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────
for key, default in [
    ("running",    False),
    ("history",    []),
    ("best_nn",    None),
    ("best_score", 0.0),
    ("gen",        0),
    ("population", None),
    ("stop_flag",  False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if stop_btn:
    st.session_state.stop_flag = True
    st.session_state.running   = False

if start_btn:
    # Reset everything
    st.session_state.history   = []
    st.session_state.best_nn   = None
    st.session_state.best_score = 0.0
    st.session_state.gen       = 0
    st.session_state.stop_flag = False
    st.session_state.running   = True
    st.session_state.population = init_population(pop_size, layer_sizes)

# ──────────────────────────────────────────────────────────────────────
# Helper: build plotly snake board
# ──────────────────────────────────────────────────────────────────────
_COLORSCALE = [
    [0.00, "#e8ecf2"],   # empty (light grid)
    [0.25, "#e8ecf2"],
    [0.26, "#ef4444"],   # food (value=1)
    [0.50, "#ef4444"],
    [0.51, "#22c55e"],   # body (value=2)
    [0.75, "#22c55e"],
    [0.76, "#16a34a"],   # head (value=3)
    [1.00, "#16a34a"],
]

def make_board_fig(grid: np.ndarray, title: str = "") -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z          = grid,
        colorscale = _COLORSCALE,
        zmin=0, zmax=3,
        showscale  = False,
        xgap=1, ygap=1,
    ))
    fig.update_layout(
        title          = dict(text=title, font=dict(color="#64748b", size=12)),
        paper_bgcolor  = "#fafafa",
        plot_bgcolor   = "#ffffff",
        margin         = dict(l=5, r=5, t=30, b=5),
        height         = 350,
        xaxis          = dict(visible=False),
        yaxis          = dict(visible=False, autorange="reversed"),
    )
    return fig


def make_animated_fig(frames: list[np.ndarray], score: int) -> go.Figure:
    """Build a Plotly animated figure from a list of grid frames."""
    plotly_frames = []
    for i, grid in enumerate(frames):
        plotly_frames.append(go.Frame(
            data=[go.Heatmap(
                z=grid, colorscale=_COLORSCALE, zmin=0, zmax=3,
                showscale=False, xgap=1, ygap=1,
            )],
            name=str(i),
        ))

    fig = go.Figure(
        data   = [go.Heatmap(
            z=frames[0], colorscale=_COLORSCALE, zmin=0, zmax=3,
            showscale=False, xgap=1, ygap=1,
        )],
        frames = plotly_frames,
        layout = go.Layout(
            title         = dict(
                text=f"Best Agent Replay  |  Score: {score}",
                font=dict(color="#1e293b", size=15)
            ),
            paper_bgcolor = "#fffbeb",
            plot_bgcolor  = "#fef3c7",
            height        = 420,
            margin        = dict(l=5, r=5, t=40, b=5),
            xaxis         = dict(visible=False),
            yaxis         = dict(visible=False, autorange="reversed"),
            updatemenus   = [dict(
                type="buttons", showactive=False,
                y=0, x=0.5, xanchor="center", yanchor="top",
                buttons=[
                    dict(label="▶  Play",
                         method="animate",
                         args=[None, dict(frame=dict(duration=80, redraw=True),
                                          fromcurrent=True, mode="immediate")]),
                    dict(label="⏸  Pause",
                         method="animate",
                         args=[[None], dict(frame=dict(duration=0, redraw=False),
                                            mode="immediate")]),
                ],
            )],
            sliders=[dict(
                steps=[dict(method="animate", args=[[str(i)],
                            dict(mode="immediate", frame=dict(duration=80, redraw=True))],
                            label="") for i in range(len(frames))],
                currentvalue=dict(visible=False),
                len=0.9, x=0.05, y=-0.02,
            )],
        )
    )
    return fig


# ──────────────────────────────────────────────────────────────────────
# Main layout
# ──────────────────────────────────────────────────────────────────────
st.title("🐍 Neuroevolution Snake AI")
st.caption(
    "A genetic algorithm evolves neural-network weights with no backprop, "
    "no gradients. Fitness = score\u00b2 x 1000 + steps_survived."
)

# Stats strip (single placeholder, one HTML row)
ph_stats = st.empty()

def refresh_stats(gen, best_score, best_fit, avg_fit, pop):
    ph_stats.markdown(
        f"""
        <div class="stats-strip">
          <div class="stat-item">
            <div class="stat-num" style="color:#1e293b">{gen}</div>
            <div class="stat-lbl">Generation</div>
          </div>
          <div class="stat-item">
            <div class="stat-num" style="color:#16a34a">{best_score:.1f}</div>
            <div class="stat-lbl">Best Score</div>
          </div>
          <div class="stat-item">
            <div class="stat-num" style="color:#2563eb">{best_fit:,.0f}</div>
            <div class="stat-lbl">Best Fitness</div>
          </div>
          <div class="stat-item">
            <div class="stat-num" style="color:#f97316">{avg_fit:,.0f}</div>
            <div class="stat-lbl">Avg Fitness</div>
          </div>
          <div class="stat-item">
            <div class="stat-num" style="color:#7c3aed">{pop}</div>
            <div class="stat-lbl">Population</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

refresh_stats(
    st.session_state.gen,
    st.session_state.best_score,
    max((r["best_fitness"]   for r in st.session_state.history), default=0),
    np.mean([r["avg_fitness"] for r in st.session_state.history]) if st.session_state.history else 0,
    pop_size,
)

st.divider()

# Two-column layout: chart | snake board
left_col, right_col = st.columns([3, 2])

with left_col:
    st.markdown(
        '<div class="section-wrap">'
        '<div class="section-header">'
        '<div class="section-dot" style="background:#3b82f6"></div>'
        '<span class="section-title">Fitness over Generations</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    chart_ph = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown(
        '<div class="section-wrap">'
        '<div class="section-header">'
        '<div class="section-dot" style="background:#22c55e"></div>'
        '<span class="section-title">Best Agent</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    board_ph = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

# Progress + log
progress_ph = st.empty()
log_ph      = st.empty()

# ──────────────────────────────────────────────────────────────────────
# Draw existing history (if re-running after pause)
# ──────────────────────────────────────────────────────────────────────
def draw_chart(history):
    if not history:
        chart_ph.caption("Training will start when you press ▶  Start Training.")
        return
    df = pd.DataFrame(history)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["gen"], y=df["best_fitness"], name="Best",
        line=dict(color="#2563eb", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df["gen"], y=df["avg_fitness"], name="Average",
        line=dict(color="#f97316", width=1.5, dash="dot"),
    ))
    fig.update_layout(
        paper_bgcolor="#fafafa", plot_bgcolor="#ffffff",
        font=dict(color="#475569"),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#e2e8f0", borderwidth=1),
        xaxis=dict(title="Generation", gridcolor="#f1f5f9", linecolor="#e2e8f0"),
        yaxis=dict(title="Fitness",    gridcolor="#f1f5f9", linecolor="#e2e8f0"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
    )
    chart_ph.plotly_chart(fig, use_container_width=True)

draw_chart(st.session_state.history)

# ──────────────────────────────────────────────────────────────────────
# Training loop
# ──────────────────────────────────────────────────────────────────────
if st.session_state.running and st.session_state.population is not None:
    population = st.session_state.population
    start_gen  = st.session_state.gen

    for gen in range(start_gen, max_gens):
        if st.session_state.stop_flag:
            st.session_state.running = False
            log_ph.warning("⏹ Training stopped by user.")
            break

        t0 = time.perf_counter()

        # ── Evaluate ──────────────────────────────────────────────────
        results = [
            evaluate_agent(nn, grid_size, max_steps_no_food, n_trials)
            for nn in population
        ]
        fitnesses   = np.array([r[0] for r in results])
        scores      = np.array([r[1] for r in results])

        best_idx     = int(np.argmax(fitnesses))
        best_fitness = float(fitnesses[best_idx])
        avg_fitness  = float(np.mean(fitnesses))
        best_score   = float(scores[best_idx])
        best_nn      = population[best_idx]

        t_eval = time.perf_counter() - t0

        # ── Record ────────────────────────────────────────────────────
        st.session_state.history.append({
            "gen": gen + 1,
            "best_fitness": best_fitness,
            "avg_fitness":  avg_fitness,
            "best_score":   best_score,
        })
        if best_score > st.session_state.best_score:
            st.session_state.best_score = best_score
            st.session_state.best_nn    = best_nn.copy()

        # ── Update UI ─────────────────────────────────────────────────
        refresh_stats(gen + 1, best_score, best_fitness, avg_fitness, pop_size)
        draw_chart(st.session_state.history)

        # Show best agent's final frame
        replay = replay_agent(best_nn, grid_size, max_steps_no_food)
        board_ph.plotly_chart(
            make_board_fig(replay[-1], f"Gen {gen+1} · Score {int(best_score)}"),
            use_container_width=True,
        )

        # Progress bar
        progress_ph.progress(
            (gen + 1) / max_gens,
            text=f"Generation {gen+1}/{max_gens}  |  "
                 f"Best score: {best_score:.0f}  |  "
                 f"Eval time: {t_eval:.2f}s",
        )

        # ── Evolve ────────────────────────────────────────────────────
        population = evolve_generation(
            population, fitnesses,
            mutation_rate=mutation_rate,
            mutation_std=mutation_std,
            elite_n=elite_n,
            tournament_k=tournament_k,
        )
        st.session_state.population = population
        st.session_state.gen        = gen + 1

    else:
        # Completed all generations
        st.session_state.running = False
        progress_ph.success(
            f"✅  Training complete! Best score ever: **{st.session_state.best_score:.0f}**"
        )

# ──────────────────────────────────────────────────────────────────────
# Replay section (always visible after training)
# ──────────────────────────────────────────────────────────────────────
if st.session_state.best_nn is not None and not st.session_state.running:
    st.divider()
    st.subheader("🎮 Replay Best Agent")
    replay_col, info_col = st.columns([2, 1])

    with info_col:
        st.metric("All-time best score",  f"{st.session_state.best_score:.0f}")
        st.metric("Generations trained",  st.session_state.gen)
        st.metric("Network params",       f"{st.session_state.best_nn.num_params:,}")
        arch = " → ".join(str(x) for x in st.session_state.best_nn.layer_sizes)
        st.caption(f"Architecture: `{arch}`")

        if st.button("🔄 Replay again"):
            pass  # triggers re-render below

    with replay_col:
        frames = replay_agent(
            st.session_state.best_nn, grid_size, max_steps_no_food
        )
        final_score = int(
            sum(1 for i in range(1, len(frames))
                if (frames[i] == 1).any() != (frames[i-1] == 1).any())
        )
        st.plotly_chart(
            make_animated_fig(frames, int(st.session_state.best_score)),
            use_container_width=True,
        )
        st.caption(
            f"▶ Press Play to watch the snake.  "
            f"Frame count: {len(frames)}"
        )
