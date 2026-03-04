"""
data.py – FastF1 data loading and processing layer.

All FastF1 calls go through here so the Dash app stays clean.
Results are cached to ~/.f1_cache (FastF1 built-in cache).
"""

import fastf1
import pandas as pd
from functools import lru_cache
from pathlib import Path

# ── Cache setup ──────────────────────────────────────────────────────────────
CACHE_DIR = Path.home() / ".f1_cache"
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

# Tyre compound colours matching real F1 visuals
COMPOUND_COLOURS = {
    "SOFT":    "#E8002D",
    "MEDIUM":  "#FFF200",
    "HARD":    "#EBEBEB",
    "INTER":   "#39B54A",
    "WET":     "#0067FF",
    "UNKNOWN": "#999999",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_season_rounds(year: int) -> list[dict]:
    """Return list of {round, name} for every race in the season."""
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    rounds = []
    for _, row in schedule.iterrows():
        rounds.append({
            "round":     int(row["RoundNumber"]),
            "name":      row["EventName"],
            "country":   row.get("Country", ""),
            "location":  row.get("Location", ""),
        })
    return rounds


@lru_cache(maxsize=8)
def load_session(year: int, round_number: int, session_type: str = "R") -> fastf1.core.Session:
    """
    Load and return a FastF1 session with all telemetry.
    Results are cached in-process so tab switches never re-load from disk.
    session_type: 'R' = Race, 'Q' = Qualifying, 'FP1'/'FP2'/'FP3' = Practice
    """
    session = fastf1.get_session(year, round_number, session_type)
    session.load(telemetry=True, laps=True, weather=True)
    return session


def get_drivers(session: fastf1.core.Session) -> list[dict]:
    """Return list of {code, name, team} for all drivers in the session."""
    drivers = []
    for drv in session.drivers:
        info = session.get_driver(drv)
        drivers.append({
            "code":   info["Abbreviation"],
            "name":   f"{info['FirstName']} {info['LastName']}",
            "team":   info["TeamName"],
            "number": info["DriverNumber"],
        })
    return sorted(drivers, key=lambda d: d["code"])


# ── Lap data ─────────────────────────────────────────────────────────────────

def get_lap_times(session: fastf1.core.Session, driver: str) -> pd.DataFrame:
    """
    Return per-lap data for a driver:
    LapNumber, LapTime (seconds), Compound, TyreLife, IsPersonalBest, Stint
    """
    laps = session.laps.pick_driver(driver).pick_quicklaps()
    df = laps[["LapNumber", "LapTime", "Compound", "TyreLife",
               "IsPersonalBest", "Stint", "PitOutTime", "PitInTime"]].copy()
    df["LapTimeSec"] = df["LapTime"].dt.total_seconds()
    df["Compound"] = df["Compound"].fillna("UNKNOWN").str.upper()
    return df.reset_index(drop=True)


def get_tyre_stints(session: fastf1.core.Session, driver: str) -> list[dict]:
    """
    Return tyre stint summary for a driver:
    [{stint, compound, start_lap, end_lap, num_laps}]
    """
    laps = session.laps.pick_driver(driver)
    stints = []
    for stint_num, group in laps.groupby("Stint"):
        compound = group["Compound"].iloc[0]
        if pd.isna(compound):
            compound = "UNKNOWN"
        stints.append({
            "stint":      int(stint_num),
            "compound":   compound.upper(),
            "start_lap":  int(group["LapNumber"].min()),
            "end_lap":    int(group["LapNumber"].max()),
            "num_laps":   int(len(group)),
            "color":      COMPOUND_COLOURS.get(compound.upper(), "#999"),
        })
    return sorted(stints, key=lambda s: s["stint"])


# ── Speed / telemetry trace ───────────────────────────────────────────────────

def get_fastest_lap_telemetry(session: fastf1.core.Session, driver: str) -> pd.DataFrame:
    """
    Return full telemetry for the driver's personal fastest lap:
    Distance, Speed, Throttle, Brake, Gear, RPM, DRS
    """
    lap = session.laps.pick_driver(driver).pick_fastest()
    tel = lap.get_telemetry().add_distance()
    return tel[["Distance", "Speed", "Throttle", "Brake", "nGear", "RPM", "DRS"]].copy()


def get_lap_delta(
    session: fastf1.core.Session,
    driver1: str,
    driver2: str,
) -> pd.DataFrame:
    """
    Return cumulative lap-time delta between two drivers (driver1 − driver2).
    Positive means driver1 is behind (slower cumulative).
    """
    d1 = get_lap_times(session, driver1)[["LapNumber", "LapTimeSec"]].rename(
        columns={"LapTimeSec": "d1"})
    d2 = get_lap_times(session, driver2)[["LapNumber", "LapTimeSec"]].rename(
        columns={"LapTimeSec": "d2"})
    merged = d1.merge(d2, on="LapNumber", how="inner")
    merged["delta"] = (merged["d1"] - merged["d2"]).cumsum()
    return merged


# ── Race results ─────────────────────────────────────────────────────────────

def get_race_results(session: fastf1.core.Session) -> pd.DataFrame:
    """Return finishing order with position, driver, team, points, status."""
    results = session.results[
        ["Position", "Abbreviation", "FullName", "TeamName",
         "Points", "Status", "GridPosition"]
    ].copy()
    results["Position"] = pd.to_numeric(results["Position"], errors="coerce")
    return results.sort_values("Position").reset_index(drop=True)


# ── Weather ──────────────────────────────────────────────────────────────────

def get_weather(session: fastf1.core.Session) -> pd.DataFrame:
    """Return weather data: Time, AirTemp, TrackTemp, Humidity, Rainfall."""
    w = session.weather_data.copy()
    w["MinutesElapsed"] = w["Time"].dt.total_seconds() / 60
    return w[["MinutesElapsed", "AirTemp", "TrackTemp", "Humidity", "Rainfall"]]
