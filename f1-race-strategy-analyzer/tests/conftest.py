"""
conftest.py — shared pytest fixtures for F1 Race Strategy Analyzer tests.

All fixtures use synthetic DataFrames so no network/FastF1 calls are made.
"""
import pandas as pd
import numpy as np
import pytest


# ── Lap time DataFrames ──────────────────────────────────────────────────────

@pytest.fixture
def lap_df_nor():
    """Synthetic lap data for NOR — 50 laps, two stints."""
    rng = np.random.default_rng(42)
    laps = []
    for lap in range(1, 51):
        stint = 1 if lap <= 28 else 2
        compound = "SOFT" if lap <= 28 else "MEDIUM"
        laps.append({
            "LapNumber":      lap,
            "LapTimeSec":     88.0 + rng.normal(0, 0.4),
            "Compound":       compound,
            "TyreLife":       lap if stint == 1 else lap - 28,
            "IsPersonalBest": lap == 23,
            "Stint":          stint,
        })
    return pd.DataFrame(laps)


@pytest.fixture
def lap_df_ver():
    """Synthetic lap data for VER — 50 laps, three stints."""
    rng = np.random.default_rng(7)
    laps = []
    for lap in range(1, 51):
        if lap <= 20:
            stint, compound = 1, "SOFT"
        elif lap <= 38:
            stint, compound = 2, "MEDIUM"
        else:
            stint, compound = 3, "HARD"
        laps.append({
            "LapNumber":      lap,
            "LapTimeSec":     88.3 + rng.normal(0, 0.4),
            "Compound":       compound,
            "TyreLife":       lap if stint == 1 else (lap - 20 if stint == 2 else lap - 38),
            "IsPersonalBest": lap == 18,
            "Stint":          stint,
        })
    return pd.DataFrame(laps)


@pytest.fixture
def delta_df(lap_df_nor, lap_df_ver):
    """Cumulative lap delta between NOR and VER."""
    d1 = lap_df_nor[["LapNumber", "LapTimeSec"]].rename(columns={"LapTimeSec": "d1"})
    d2 = lap_df_ver[["LapNumber", "LapTimeSec"]].rename(columns={"LapTimeSec": "d2"})
    merged = d1.merge(d2, on="LapNumber", how="inner")
    merged["delta"] = (merged["d1"] - merged["d2"]).cumsum()
    return merged


@pytest.fixture
def stints_nor():
    return [
        {"stint": 1, "compound": "SOFT",   "start_lap": 1,  "end_lap": 28, "num_laps": 28, "color": "#E8002D"},
        {"stint": 2, "compound": "MEDIUM", "start_lap": 29, "end_lap": 50, "num_laps": 22, "color": "#FFF200"},
    ]


@pytest.fixture
def stints_ver():
    return [
        {"stint": 1, "compound": "SOFT",   "start_lap": 1,  "end_lap": 20, "num_laps": 20, "color": "#E8002D"},
        {"stint": 2, "compound": "MEDIUM", "start_lap": 21, "end_lap": 38, "num_laps": 18, "color": "#FFF200"},
        {"stint": 3, "compound": "HARD",   "start_lap": 39, "end_lap": 50, "num_laps": 12, "color": "#EBEBEB"},
    ]


@pytest.fixture
def telemetry_df():
    """Synthetic telemetry trace (~1500 samples)."""
    rng = np.random.default_rng(0)
    n = 1500
    distance = np.linspace(0, 5300, n)
    speed = 200 + 100 * np.sin(distance / 500) + rng.normal(0, 5, n)
    return pd.DataFrame({
        "Distance": distance,
        "Speed":    np.clip(speed, 0, 340),
        "Throttle": np.clip(80 + rng.normal(0, 20, n), 0, 100),
        "Brake":    np.where(rng.random(n) > 0.85, 1, 0).astype(float),
        "nGear":    rng.integers(1, 9, n),
        "RPM":      rng.integers(8000, 12000, n),
        "DRS":      np.where(rng.random(n) > 0.7, 1, 0).astype(float),
    })


@pytest.fixture
def race_results_df():
    """Synthetic race results DataFrame."""
    return pd.DataFrame({
        "Position":    [1, 2, 3, 4, 5],
        "Abbreviation":["NOR", "VER", "LEC", "SAI", "HAM"],
        "FullName":    ["Lando Norris", "Max Verstappen", "Charles Leclerc",
                        "Carlos Sainz", "Lewis Hamilton"],
        "TeamName":    ["McLaren", "Red Bull Racing", "Ferrari",
                        "Ferrari", "Mercedes"],
        "Points":      [25, 18, 15, 12, 10],
        "Status":      ["Finished"] * 5,
        "GridPosition":[2, 1, 4, 3, 5],
    })


@pytest.fixture
def weather_df():
    """Synthetic weather data over 55 minutes."""
    minutes = np.linspace(0, 55, 110)
    rng = np.random.default_rng(1)
    return pd.DataFrame({
        "MinutesElapsed": minutes,
        "AirTemp":        22 + rng.normal(0, 0.3, 110),
        "TrackTemp":      37 + rng.normal(0, 0.5, 110),
        "Humidity":       45 + rng.normal(0, 1.0, 110),
        "Rainfall":       np.zeros(110),
    })
