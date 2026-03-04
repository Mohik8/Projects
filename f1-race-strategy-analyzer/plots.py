"""
plots.py – All Plotly figure generators.

Each function takes preprocessed DataFrames (from data.py) and returns
a plotly.graph_objects.Figure ready for Dash.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from data import COMPOUND_COLOURS

# ── Shared theme ─────────────────────────────────────────────────────────────
BG       = "#15151e"
BG_PAPER = "#1e1e2e"
GRID     = "#2a2a3e"
TEXT     = "#ffffff"
SUBTEXT  = "#8b8b9e"

BASE_LAYOUT = dict(
    paper_bgcolor=BG_PAPER,
    plot_bgcolor=BG,
    font=dict(color=TEXT, family="'Inter', 'Segoe UI', sans-serif"),
    margin=dict(l=50, r=30, t=50, b=50),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    legend=dict(
        bgcolor="#1e1e2e",
        bordercolor=GRID,
        borderwidth=1,
    ),
)


def _apply_base(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**BASE_LAYOUT, title=dict(text=title, font=dict(size=16)))
    return fig


# ── 1. Lap time chart ─────────────────────────────────────────────────────────

def fig_lap_times(
    df1: pd.DataFrame, driver1: str,
    df2: pd.DataFrame, driver2: str,
    team_color1: str = "#e8002d",
    team_color2: str = "#1868db",
) -> go.Figure:
    """Line chart of lap times for two drivers, coloured by tyre compound."""
    fig = go.Figure()

    for df, driver, color in [
        (df1, driver1, team_color1),
        (df2, driver2, team_color2),
    ]:
        for compound, group in df.groupby("Compound"):
            c_color = COMPOUND_COLOURS.get(compound, color)
            fig.add_trace(go.Scatter(
                x=group["LapNumber"],
                y=group["LapTimeSec"],
                mode="lines+markers",
                name=f"{driver} – {compound}",
                line=dict(color=c_color, width=2),
                marker=dict(color=c_color, size=6),
                hovertemplate=(
                    f"<b>{driver}</b><br>"
                    "Lap %{x}<br>"
                    "Time: %{customdata}<br>"
                    f"Compound: {compound}"
                    "<extra></extra>"
                ),
                customdata=[
                    f"{int(t // 60)}:{t % 60:06.3f}" for t in group["LapTimeSec"]
                ],
            ))

    fig.update_layout(
        xaxis_title="Lap",
        yaxis_title="Lap Time (s)",
        yaxis_autorange="reversed",
        hovermode="x unified",
    )
    return _apply_base(fig, "Lap Times")


# ── 2. Lap time delta ─────────────────────────────────────────────────────────

def fig_lap_delta(
    delta_df: pd.DataFrame,
    driver1: str,
    driver2: str,
) -> go.Figure:
    """
    Cumulative gap chart: positive = driver1 is behind,
    negative = driver1 is ahead.
    Fill green when driver1 leads, red when behind.
    """
    fig = go.Figure()

    pos = delta_df.copy()
    pos.loc[pos["delta"] < 0, "delta"] = 0
    neg = delta_df.copy()
    neg.loc[neg["delta"] > 0, "delta"] = 0

    fig.add_trace(go.Scatter(
        x=delta_df["LapNumber"], y=pos["delta"],
        fill="tozeroy", fillcolor="rgba(232,0,45,0.25)",
        line=dict(color="rgba(232,0,45,0)", width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=delta_df["LapNumber"], y=neg["delta"],
        fill="tozeroy", fillcolor="rgba(39,162,96,0.25)",
        line=dict(color="rgba(39,162,96,0)", width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=delta_df["LapNumber"],
        y=delta_df["delta"],
        mode="lines",
        line=dict(color="#ffffff", width=1.5),
        name="Gap",
        hovertemplate="Lap %{x}<br>Gap: %{y:.3f}s<extra></extra>",
    ))
    fig.add_hline(y=0, line=dict(color=SUBTEXT, width=1, dash="dot"))
    fig.add_annotation(
        x=delta_df["LapNumber"].min() + 1, y=delta_df["delta"].max() * 0.8,
        text=f"← {driver1} ahead", showarrow=False,
        font=dict(color="#27a260", size=11),
    )
    fig.add_annotation(
        x=delta_df["LapNumber"].min() + 1, y=delta_df["delta"].min() * 0.8,
        text=f"← {driver2} ahead", showarrow=False,
        font=dict(color="#e8002d", size=11),
    )
    fig.update_layout(
        xaxis_title="Lap",
        yaxis_title="Cumulative Gap (s)",
        showlegend=False,
    )
    return _apply_base(fig, f"Race Gap  {driver1} vs {driver2}")


# ── 3. Tyre strategy timeline ─────────────────────────────────────────────────

def fig_tyre_strategy(
    stints1: list[dict], driver1: str,
    stints2: list[dict], driver2: str,
    total_laps: int,
) -> go.Figure:
    """
    Horizontal bar chart of tyre stints — matches the official F1 strategy graphic.
    """
    fig = go.Figure()

    for driver, stints, y_pos in [
        (driver1, stints1, 1),
        (driver2, stints2, 0),
    ]:
        for s in stints:
            fig.add_trace(go.Bar(
                x=[s["num_laps"]],
                y=[driver],
                base=s["start_lap"] - 1,
                orientation="h",
                marker=dict(
                    color=s["color"],
                    line=dict(color=BG, width=2),
                ),
                name=s["compound"],
                showlegend=False,
                hovertemplate=(
                    f"<b>{driver}</b><br>"
                    f"Stint {s['stint']}: {s['compound']}<br>"
                    f"Laps {s['start_lap']}–{s['end_lap']} ({s['num_laps']} laps)"
                    "<extra></extra>"
                ),
            ))
            # Compound label on bar
            fig.add_annotation(
                x=s["start_lap"] - 1 + s["num_laps"] / 2,
                y=driver,
                text=s["compound"][0],   # S / M / H / I / W
                showarrow=False,
                font=dict(
                    color=BG if s["compound"] in ("MEDIUM", "HARD") else "#ffffff",
                    size=11,
                    family="monospace",
                ),
            )

    # Compound legend
    seen = set()
    for s in stints1 + stints2:
        c = s["compound"]
        if c not in seen:
            seen.add(c)
            fig.add_trace(go.Bar(
                x=[0], y=[""], base=0,
                orientation="h",
                marker_color=s["color"],
                name=c,
                showlegend=True,
            ))

    fig.update_layout(
        barmode="stack",
        xaxis=dict(range=[0, total_laps + 2], title="Lap"),
        yaxis=dict(title=""),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return _apply_base(fig, "Tyre Strategy")


# ── 4. Speed trace ────────────────────────────────────────────────────────────

def fig_speed_trace(
    tel1: pd.DataFrame, driver1: str,
    tel2: pd.DataFrame, driver2: str,
    team_color1: str = "#e8002d",
    team_color2: str = "#1868db",
) -> go.Figure:
    """
    Four-panel plot: Speed / Throttle / Brake / Gear vs track distance
    for each driver's fastest lap.
    """
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        row_heights=[0.45, 0.2, 0.15, 0.2],
        vertical_spacing=0.04,
    )

    panels = [
        ("Speed",    "Speed (km/h)",   "Speed",    1),
        ("Throttle", "Throttle (%)",   "Throttle", 2),
        ("Brake",    "Brake",          "Brake",    3),
        ("Gear",     "Gear",           "nGear",    4),
    ]

    for label, y_title, col, row in panels:
        for tel, driver, color in [
            (tel1, driver1, team_color1),
            (tel2, driver2, team_color2),
        ]:
            show = row == 1  # only show legend once
            fig.add_trace(go.Scatter(
                x=tel["Distance"],
                y=tel[col],
                mode="lines",
                name=driver,
                line=dict(color=color, width=1.8),
                showlegend=show,
                hovertemplate=f"{driver}<br>{label}: %{{y}}<extra></extra>",
            ), row=row, col=1)

        fig.update_yaxes(title_text=y_title, row=row, col=1,
                         gridcolor=GRID, zerolinecolor=GRID)

    fig.update_xaxes(title_text="Distance (m)", row=4, col=1,
                     gridcolor=GRID, zerolinecolor=GRID)
    fig.update_layout(
        paper_bgcolor=BG_PAPER,
        plot_bgcolor=BG,
        font=dict(color=TEXT, family="'Inter', sans-serif"),
        margin=dict(l=60, r=30, t=50, b=50),
        hovermode="x unified",
        legend=dict(bgcolor="#1e1e2e", bordercolor=GRID, borderwidth=1),
        title=dict(text="Fastest Lap Telemetry", font=dict(size=16)),
    )
    return fig


# ── 5. Race results bar ───────────────────────────────────────────────────────

def fig_race_results(results: pd.DataFrame) -> go.Figure:
    """Horizontal bar showing finishing positions with team colours."""
    # Use a set of distinct colours per team (Plotly Qualitative)
    palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24
    teams = results["TeamName"].unique().tolist()
    color_map = {t: palette[i % len(palette)] for i, t in enumerate(teams)}

    results = results.dropna(subset=["Position"]).copy()
    results["Position"] = results["Position"].astype(int)
    results = results.sort_values("Position")

    fig = go.Figure(go.Bar(
        x=results["Points"],
        y=results["Abbreviation"],
        orientation="h",
        marker=dict(
            color=[color_map[t] for t in results["TeamName"]],
            line=dict(color=BG, width=1),
        ),
        customdata=results[["FullName", "TeamName", "Position", "GridPosition", "Status"]].values,
        hovertemplate=(
            "<b>P%{customdata[2]}  %{customdata[0]}</b><br>"
            "Team: %{customdata[1]}<br>"
            "Points: %{x}<br>"
            "Grid: P%{customdata[3]}<br>"
            "Status: %{customdata[4]}"
            "<extra></extra>"
        ),
    ))
    fig.update_layout(
        xaxis_title="Points",
        yaxis=dict(autorange="reversed", gridcolor=GRID, zerolinecolor=GRID),
        **{k: v for k, v in BASE_LAYOUT.items() if k != "yaxis"},
        title=dict(text="Race Results", font=dict(size=16)),
        margin=dict(l=60, r=30, t=50, b=50),
    )
    return fig


# ── 6. Weather chart ──────────────────────────────────────────────────────────

def fig_weather(weather: pd.DataFrame) -> go.Figure:
    """Dual-axis: Air & Track temp vs time, with rainfall overlay."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=weather["MinutesElapsed"], y=weather["TrackTemp"],
        mode="lines", name="Track Temp",
        line=dict(color="#e8002d", width=2),
        hovertemplate="Min %{x:.0f}<br>Track: %{y:.1f}°C<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=weather["MinutesElapsed"], y=weather["AirTemp"],
        mode="lines", name="Air Temp",
        line=dict(color="#58a6ff", width=2, dash="dot"),
        hovertemplate="Min %{x:.0f}<br>Air: %{y:.1f}°C<extra></extra>",
    ), secondary_y=False)

    if weather["Rainfall"].any():
        fig.add_trace(go.Bar(
            x=weather["MinutesElapsed"], y=weather["Rainfall"].astype(int),
            name="Rainfall", marker_color="rgba(88,166,255,0.3)",
            hovertemplate="Min %{x:.0f}<br>Rainfall: %{y}<extra></extra>",
        ), secondary_y=True)

    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False,
                     gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(title_text="Rainfall", secondary_y=True,
                     gridcolor=GRID, showgrid=False)
    fig.update_xaxes(title_text="Race Time (min)", gridcolor=GRID)
    fig.update_layout(
        paper_bgcolor=BG_PAPER,
        plot_bgcolor=BG,
        font=dict(color=TEXT),
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(bgcolor="#1e1e2e", bordercolor=GRID, borderwidth=1),
        title=dict(text="Weather Conditions", font=dict(size=16)),
        hovermode="x unified",
    )
    return fig
