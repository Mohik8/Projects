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

# Custom dark CSS
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080812 0%, #0d0d1e 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
  }
  .stat-card {
    background: linear-gradient(135deg, rgba(0,255,136,0.06) 0%, rgba(79,195,247,0.04) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px 14px;
    text-align: center;
    margin-bottom: 8px;
    backdrop-filter: blur(12px);
    transition: border-color 0.2s;
  }
  .stat-card:hover { border-color: rgba(0,255,136,0.3); }
  .stat-value {
    font-size: 1.9rem; font-weight: 700; letter-spacing: -0.5px;
    background: linear-gradient(135deg, #00ff88, #4fc3f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .stat-label { font-size: 0.7rem; color: rgba(255,255,255,0.4); letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
  h1 { background: linear-gradient(135deg, #00ff88 0%, #4fc3f7 100%);
       -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(0,255,136,0.25) !important; }
  [data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 12px 16px;
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
    [0.00, "#0d0d1a"],   # empty
    [0.25, "#0d0d1a"],
    [0.26, "#ff4444"],   # food (value=1)
    [0.50, "#ff4444"],
    [0.51, "#00cc66"],   # body (value=2)
    [0.75, "#00cc66"],
    [0.76, "#00ff88"],   # head (value=3)
    [1.00, "#00ff88"],
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
        title          = dict(text=title, font=dict(color="#aaa", size=13)),
        paper_bgcolor  = "#0d0d1a",
        plot_bgcolor   = "#0d0d1a",
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
                font=dict(color="#00ff88", size=15)
            ),
            paper_bgcolor = "#0d0d1a",
            plot_bgcolor  = "#0d0d1a",
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

# Stat cards row
col_gen, col_best_score, col_best_fit, col_avg_fit, col_pop = st.columns(5)
ph_gen        = col_gen.empty()
ph_best_score = col_best_score.empty()
ph_best_fit   = col_best_fit.empty()
ph_avg_fit    = col_avg_fit.empty()
ph_pop        = col_pop.empty()

def render_stat(placeholder, value, label, color="#00ff88"):
    placeholder.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-value" style="color:{color}">{value}</div>'
        f'<div class="stat-label">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def refresh_stats(gen, best_score, best_fit, avg_fit, pop):
    render_stat(ph_gen,        gen,                    "Generation")
    render_stat(ph_best_score, f"{best_score:.1f}",    "Best Score",   "#00ff88")
    render_stat(ph_best_fit,   f"{best_fit:,.0f}",     "Best Fitness", "#4fc3f7")
    render_stat(ph_avg_fit,    f"{avg_fit:,.0f}",      "Avg Fitness",  "#ffb74d")
    render_stat(ph_pop,        pop,                    "Population",   "#ce93d8")

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
    st.subheader("Fitness over Generations")
    chart_ph = st.empty()

with right_col:
    st.subheader("Best Agent (last generation)")
    board_ph = st.empty()

# Progress + log
progress_ph = st.empty()
log_ph      = st.empty()

# ──────────────────────────────────────────────────────────────────────
# Draw existing history (if re-running after pause)
# ──────────────────────────────────────────────────────────────────────
def draw_chart(history):
    if not history:
        chart_ph.info("Training will start when you press ▶  Start Training.")
        return
    df = pd.DataFrame(history)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["gen"], y=df["best_fitness"], name="Best",
        line=dict(color="#00ff88", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df["gen"], y=df["avg_fitness"], name="Average",
        line=dict(color="#ffb74d", width=1.5, dash="dot"),
    ))
    fig.update_layout(
        paper_bgcolor="#0d0d1a", plot_bgcolor="#111128",
        font=dict(color="#ccc"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Generation", gridcolor="#222"),
        yaxis=dict(title="Fitness",    gridcolor="#222"),
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
