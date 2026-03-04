"""
app.py – F1 Race Strategy Analyzer
Plotly Dash app — modern layout with F1-style typography.

All 6 charts are pre-built on "Compare" click and stored client-side.
Tab switches are instant. Session is cached in-process via lru_cache.

Run:
    python app.py  →  http://localhost:8050
"""

import datetime
import plotly.io as pio
import pandas as pd

from dash import Dash, html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc

import data as f1data
import plots

# ── App ───────────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="F1 Strategy Analyzer",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

CURRENT_YEAR = datetime.datetime.now().year

# ── Team colours ──────────────────────────────────────────────────────────────
TEAM_COLORS: dict[str, str] = {
    "Red Bull Racing": "#3671C6",
    "Ferrari":         "#E8002D",
    "Mercedes":        "#27F4D2",
    "McLaren":         "#FF8000",
    "Aston Martin":    "#229971",
    "Alpine":          "#FF87BC",
    "Williams":        "#64C4FF",
    "RB":              "#6692FF",
    "Kick Sauber":     "#52E252",
    "Haas F1 Team":    "#B6BABD",
}

def team_color(team: str) -> str:
    for k, v in TEAM_COLORS.items():
        if k.lower() in team.lower():
            return v
    return "#e8002d"

# ── Next race helper ──────────────────────────────────────────────────────────
def get_next_race() -> dict | None:
    try:
        import fastf1
        now  = datetime.datetime.now(datetime.timezone.utc)
        full = fastf1.get_event_schedule(now.year, include_testing=False)
        for _, row in full.sort_values("RoundNumber").iterrows():
            d = pd.to_datetime(row.get("Session5DateUtc") or row.get("EventDate"))
            if d.tzinfo is None:
                d = d.replace(tzinfo=datetime.timezone.utc)
            if d > now:
                return {"name": row["EventName"], "round": int(row["RoundNumber"]),
                        "country": row.get("Country", ""), "date": d.isoformat()}
    except Exception:
        pass
    return None

# ── Layout helpers ────────────────────────────────────────────────────────────
def labeled_dd(label: str, dd_id: str, **kw):
    return html.Div([
        html.Div(label, className="ctrl-label"),
        dcc.Dropdown(id=dd_id, **kw),
    ], className="mb-3")

def stat_tile(label: str, value: str, accent: str):
    return html.Div([
        html.Div(value, className="stat-value", style={"color": accent}),
        html.Div(label, className="stat-label"),
    ], className="stat-tile", style={"--accent": accent})

def next_race_banner():
    race = get_next_race()
    if not race:
        return html.Div()
    return html.Div([
        html.Div([
            html.Span("NEXT RACE", className="next-label"),
            html.Span(f" R{race['round']}", className="round-pill"),
        ], className="next-race-meta"),
        html.Div(race["name"], className="next-race-name"),
        html.Div([
            html.Div([html.Div("--", id="cd-days",  className="cd-num"), html.Div("DAYS", className="cd-unit")], className="cd-block"),
            html.Div(":", className="cd-sep"),
            html.Div([html.Div("--", id="cd-hours", className="cd-num"), html.Div("HRS",  className="cd-unit")], className="cd-block"),
            html.Div(":", className="cd-sep"),
            html.Div([html.Div("--", id="cd-mins",  className="cd-num"), html.Div("MIN",  className="cd-unit")], className="cd-block"),
            html.Div(":", className="cd-sep"),
            html.Div([html.Div("--", id="cd-secs",  className="cd-num"), html.Div("SEC",  className="cd-unit")], className="cd-block"),
        ], className="countdown-row"),
        dcc.Store(id="store-race-date", data=race["date"]),
        dcc.Interval(id="interval-countdown", interval=1000, n_intervals=0),
    ], className="next-race-banner")

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div([

    html.Header([
        html.Div([
            html.Span("F1",       className="brand-f1"),
            html.Span("STRATEGY", className="brand-strategy"),
            html.Span("ANALYZER", className="brand-analyzer"),
        ], className="brand-block"),
        html.Div(next_race_banner(), className="header-right"),
    ], className="app-header"),

    html.Div([

        html.Aside([
            html.Div([
                html.Div("SESSION", className="sidebar-section-title"),
                labeled_dd("YEAR", "dd-year",
                    options=[{"label": str(y), "value": y} for y in range(2018, CURRENT_YEAR + 1)],
                    value=CURRENT_YEAR, clearable=False),
                labeled_dd("RACE",         "dd-race",         clearable=False),
                labeled_dd("SESSION TYPE", "dd-session-type",
                    options=[
                        {"label": "Race",       "value": "R"},
                        {"label": "Qualifying", "value": "Q"},
                        {"label": "Practice 1", "value": "FP1"},
                        {"label": "Practice 2", "value": "FP2"},
                        {"label": "Practice 3", "value": "FP3"},
                    ], value="R", clearable=False),
                html.Button("LOAD SESSION", id="btn-load", className="btn-primary-f1 w-100"),
                dcc.Loading(html.Div(id="load-spinner"), type="circle", color="#e8002d"),
            ], className="sidebar-block"),

            html.Div(className="sidebar-divider"),

            html.Div([
                html.Div("COMPARISON", className="sidebar-section-title"),
                labeled_dd("DRIVER 1", "dd-driver1", clearable=False),
                labeled_dd("DRIVER 2", "dd-driver2", clearable=False),
                html.Button("COMPARE", id="btn-compare",
                            className="btn-primary-f1 w-100", disabled=True),
            ], className="sidebar-block"),

            html.Div(className="sidebar-divider"),
            html.Div(id="status-box", className="sidebar-block"),

        ], className="sidebar"),

        html.Main([
            html.Div(id="stat-row", className="stat-row"),
            html.Div([
                html.Div([
                    html.Button("LAP TIMES", id="tab-btn-0", className="tab-btn active"),
                    html.Button("RACE GAP",  id="tab-btn-1", className="tab-btn"),
                    html.Button("STRATEGY",  id="tab-btn-2", className="tab-btn"),
                    html.Button("TELEMETRY", id="tab-btn-3", className="tab-btn"),
                    html.Button("RESULTS",   id="tab-btn-4", className="tab-btn"),
                    html.Button("WEATHER",   id="tab-btn-5", className="tab-btn"),
                ], className="tab-bar"),
                dcc.Store(id="store-active-tab", data=0),
            ]),
            dcc.Loading(
                html.Div(id="chart-area", className="chart-area"),
                type="circle", color="#e8002d",
            ),
        ], className="main-content"),

    ], className="app-body"),

    dcc.Store(id="store-session-meta"),
    dcc.Store(id="store-fig-0"),
    dcc.Store(id="store-fig-1"),
    dcc.Store(id="store-fig-2"),
    dcc.Store(id="store-fig-3"),
    dcc.Store(id="store-fig-4"),
    dcc.Store(id="store-fig-5"),

], className="app-root")


# ── Callbacks ─────────────────────────────────────────────────────────────────

# Countdown — clientside (zero latency)
app.clientside_callback(
    """
    function(n, target) {
        if (!target) return ['--','--','--','--'];
        var diff = Math.max(0, Math.floor((new Date(target) - new Date()) / 1000));
        var pad  = v => String(v).padStart(2,'0');
        return [pad(Math.floor(diff/86400)),
                pad(Math.floor((diff%86400)/3600)),
                pad(Math.floor((diff%3600)/60)),
                pad(diff%60)];
    }
    """,
    Output("cd-days","children"), Output("cd-hours","children"),
    Output("cd-mins","children"), Output("cd-secs","children"),
    Input("interval-countdown","n_intervals"),
    State("store-race-date","data"),
)

# Active tab — clientside
app.clientside_callback(
    """
    function(c0,c1,c2,c3,c4,c5, cur) {
        var trig = window.dash_clientside.callback_context.triggered;
        if (!trig || !trig.length) return window.dash_clientside.no_update;
        var map = {'tab-btn-0':0,'tab-btn-1':1,'tab-btn-2':2,
                   'tab-btn-3':3,'tab-btn-4':4,'tab-btn-5':5};
        var v = map[trig[0].prop_id.split('.')[0]];
        return v !== undefined ? v : cur;
    }
    """,
    Output("store-active-tab","data"),
    Input("tab-btn-0","n_clicks"), Input("tab-btn-1","n_clicks"),
    Input("tab-btn-2","n_clicks"), Input("tab-btn-3","n_clicks"),
    Input("tab-btn-4","n_clicks"), Input("tab-btn-5","n_clicks"),
    State("store-active-tab","data"),
)

for _i in range(6):
    app.clientside_callback(
        f"function(a){{ return a==={_i}?'tab-btn active':'tab-btn'; }}",
        Output(f"tab-btn-{_i}","className"),
        Input("store-active-tab","data"),
    )


@callback(
    Output("dd-race","options"), Output("dd-race","value"),
    Input("dd-year","value"),
)
def populate_races(year):
    rounds  = f1data.get_season_rounds(year)
    options = [{"label": f"R{r['round']}  {r['name']}", "value": r["round"]} for r in rounds]
    return options, (options[-1]["value"] if options else None)


@callback(
    Output("dd-driver1","options"), Output("dd-driver2","options"),
    Output("dd-driver1","value"),   Output("dd-driver2","value"),
    Output("btn-compare","disabled"),
    Output("status-box","children"),
    Output("store-session-meta","data"),
    Output("stat-row","children"),
    Output("load-spinner","children"),
    Input("btn-load","n_clicks"),
    State("dd-year","value"), State("dd-race","value"), State("dd-session-type","value"),
    prevent_initial_call=True,
)
def load_session(_, year, round_num, stype):
    try:
        session = f1data.load_session(year, round_num, stype)
        drivers = f1data.get_drivers(session)
        opts = [{"label": f"{d['code']}  ·  {d['team']}", "value": d["code"]} for d in drivers]
        d1   = drivers[0]["code"] if drivers        else None
        d2   = drivers[1]["code"] if len(drivers)>1 else None
        meta = {"year": year, "round": round_num, "stype": stype,
                "event": session.event["EventName"]}

        tiles = []
        if stype == "R":
            try:
                res  = f1data.get_race_results(session)
                win  = res.iloc[0]
                laps = int(session.laps["LapNumber"].max())
                tiles = [
                    stat_tile("WINNER",     win["Abbreviation"], "#e8002d"),
                    stat_tile("TEAM",       win["TeamName"],      "#ffffff"),
                    stat_tile("TOTAL LAPS", str(laps),           "#58a6ff"),
                    stat_tile("DRIVERS",    str(len(drivers)),   "#27a260"),
                ]
            except Exception:
                pass

        status = html.Div([
            html.Span("● ", style={"color":"#27a260"}),
            html.Span(f"{session.event['EventName']} {year} — {stype}",
                      style={"color":"#c0c0d0","fontSize":"0.78rem"}),
        ])
        return opts, opts, d1, d2, False, status, meta, tiles, ""

    except Exception as exc:
        err = html.Div([
            html.Span("✕ ", style={"color":"#e8002d"}),
            html.Span(str(exc), style={"color":"#888898","fontSize":"0.75rem"}),
        ])
        return (no_update,)*4 + (True, err, no_update, no_update, "")


@callback(
    Output("store-fig-0","data"), Output("store-fig-1","data"),
    Output("store-fig-2","data"), Output("store-fig-3","data"),
    Output("store-fig-4","data"), Output("store-fig-5","data"),
    Input("btn-compare","n_clicks"),
    State("dd-driver1","value"), State("dd-driver2","value"),
    State("store-session-meta","data"),
    prevent_initial_call=True,
)
def build_all_charts(_, d1, d2, meta):
    if not meta or not d1 or not d2:
        return (no_update,) * 6

    def _j(fig):
        return pio.to_json(fig)

    def _err(msg):
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(text=f"⚠ {msg}", x=0.5, y=0.5,
                           xref="paper", yref="paper", showarrow=False,
                           font=dict(color="#e8002d", size=13))
        fig.update_layout(paper_bgcolor="#0f0f18", plot_bgcolor="#0f0f18",
                          margin=dict(l=0,r=0,t=0,b=0))
        return _j(fig)

    try:
        session = f1data.load_session(meta["year"], meta["round"], meta["stype"])
        drvs = f1data.get_drivers(session)
        c1   = team_color(next((d["team"] for d in drvs if d["code"]==d1), ""))
        c2   = team_color(next((d["team"] for d in drvs if d["code"]==d2), ""))

        df1   = f1data.get_lap_times(session, d1)
        df2   = f1data.get_lap_times(session, d2)
        delta = f1data.get_lap_delta(session, d1, d2)
        s1    = f1data.get_tyre_stints(session, d1)
        s2    = f1data.get_tyre_stints(session, d2)
        tel1  = f1data.get_fastest_lap_telemetry(session, d1)
        tel2  = f1data.get_fastest_lap_telemetry(session, d2)
        total = int(session.laps["LapNumber"].max())

        r0 = _j(plots.fig_lap_times(df1, d1, df2, d2, c1, c2))
        r1 = _j(plots.fig_lap_delta(delta, d1, d2))
        r2 = _j(plots.fig_tyre_strategy(s1, d1, s2, d2, total))
        r3 = _j(plots.fig_speed_trace(tel1, d1, tel2, d2, c1, c2))

        try: r4 = _j(plots.fig_race_results(f1data.get_race_results(session)))
        except Exception as e: r4 = _err(str(e))
        try: r5 = _j(plots.fig_weather(f1data.get_weather(session)))
        except Exception as e: r5 = _err(str(e))

        return r0, r1, r2, r3, r4, r5

    except Exception as exc:
        e = _err(str(exc))
        return (e,) * 6


HEIGHTS = ["520px", "420px", "310px", "700px", "620px", "420px"]

@callback(
    Output("chart-area","children"),
    Input("store-active-tab","data"),
    Input("store-fig-0","data"), Input("store-fig-1","data"),
    Input("store-fig-2","data"), Input("store-fig-3","data"),
    Input("store-fig-4","data"), Input("store-fig-5","data"),
)
def render_chart(tab, f0, f1, f2, f3, f4, f5):
    figs     = [f0, f1, f2, f3, f4, f5]
    fig_json = figs[tab] if (tab is not None and figs[tab]) else None
    if not fig_json:
        return html.Div([
            html.Div("↑", style={"fontSize":"2.5rem","color":"#252530","marginBottom":"12px"}),
            html.Div("Load a session, pick two drivers, then click COMPARE",
                     style={"color":"#44445a","fontSize":"0.85rem"}),
        ], style={"display":"flex","flexDirection":"column","alignItems":"center",
                  "justifyContent":"center","height":"400px"})
    fig = pio.from_json(fig_json)
    return dcc.Graph(
        figure=fig,
        style={"height": HEIGHTS[tab]},
        config={"displayModeBar": True, "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d","select2d"]},
        className="graph-fadein",
    )


if __name__ == "__main__":
    print("\n  F1 Race Strategy Analyzer  ->  http://localhost:8050\n")
    app.run(debug=False, host="0.0.0.0", port=8050)
