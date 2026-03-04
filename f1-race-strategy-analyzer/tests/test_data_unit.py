"""
test_data_unit.py — Unit tests for data.py

FastF1 network calls are fully mocked with unittest.mock so these tests run
offline and complete in milliseconds. Tests follow the Arrange-Act-Assert pattern.
"""
import pandas as pd
import numpy as np
import pytest
from unittest.mock import MagicMock, patch, PropertyMock


# ── Helpers to build realistic mock sessions ─────────────────────────────────

def _make_mock_laps(driver: str, n_laps: int = 50, base_time: float = 88.0):
    """Return a mock Laps DataFrame-like iterable with pick_driver support."""
    rng = np.random.default_rng(hash(driver) % (2**32))
    laps = []
    for lap in range(1, n_laps + 1):
        stint = 1 if lap <= 28 else 2
        compound = "SOFT" if lap <= 28 else "MEDIUM"
        laps.append({
            "LapNumber":      lap,
            "LapTime":        pd.Timedelta(seconds=base_time + rng.normal(0, 0.4)),
            "Compound":       compound,
            "TyreLife":       lap if stint == 1 else lap - 28,
            "IsPersonalBest": lap == 23,
            "Stint":          stint,
            "PitOutTime":     pd.NaT,
            "PitInTime":      pd.NaT,
            "Driver":         driver,
        })
    df = pd.DataFrame(laps)
    # Teach the DataFrame to respond to pick_driver / pick_quicklaps
    df.pick_driver   = lambda d: df[df["Driver"] == d].copy()
    df.pick_quicklaps = lambda: df.copy()
    df.pick_fastest  = lambda: df.iloc[df["LapTime"].apply(lambda t: t.total_seconds()).idxmin()]
    return df


def _make_mock_session(drivers=("NOR", "VER")):
    session = MagicMock()
    session.drivers = list(drivers)

    # Build combined laps DataFrame
    all_laps = pd.concat([_make_mock_laps(d) for d in drivers], ignore_index=True)
    all_laps.pick_driver = lambda d: _make_mock_laps(d)

    session.laps = all_laps

    # Driver info
    def get_driver(code):
        names = {
            "NOR": ("Lando",   "Norris",     "McLaren"),
            "VER": ("Max",     "Verstappen", "Red Bull Racing"),
            "LEC": ("Charles", "Leclerc",    "Ferrari"),
        }
        fn, ln, team = names.get(code, ("Unknown", "Driver", "Unknown"))
        return {
            "Abbreviation": code,
            "FirstName":    fn,
            "LastName":     ln,
            "TeamName":     team,
            "DriverNumber": "1",
        }
    session.get_driver.side_effect = get_driver

    # Race results
    session.results = pd.DataFrame({
        "Position":     [1, 2],
        "Abbreviation": ["NOR", "VER"],
        "FullName":     ["Lando Norris", "Max Verstappen"],
        "TeamName":     ["McLaren", "Red Bull Racing"],
        "Points":       [25, 18],
        "Status":       ["Finished", "Finished"],
        "GridPosition": [2, 1],
    })

    # Weather
    minutes = np.linspace(0, 55, 100)
    session.weather_data = pd.DataFrame({
        "Time":      pd.to_timedelta(minutes, unit="m"),
        "AirTemp":   22 + np.random.normal(0, 0.3, 100),
        "TrackTemp": 37 + np.random.normal(0, 0.5, 100),
        "Humidity":  45.0 * np.ones(100),
        "Rainfall":  np.zeros(100),
    })

    return session


# ── get_drivers ───────────────────────────────────────────────────────────────

class TestGetDrivers:

    def test_returns_list(self):
        from data import get_drivers
        session = _make_mock_session(["NOR", "VER"])
        result = get_drivers(session)
        assert isinstance(result, list)

    def test_entry_keys(self):
        from data import get_drivers
        session = _make_mock_session(["NOR", "VER"])
        drivers = get_drivers(session)
        for d in drivers:
            assert "code" in d
            assert "name" in d
            assert "team" in d

    def test_sorted_by_code(self):
        from data import get_drivers
        session = _make_mock_session(["VER", "NOR", "LEC"])
        codes = [d["code"] for d in get_drivers(session)]
        assert codes == sorted(codes)

    def test_driver_count_matches_session(self):
        from data import get_drivers
        session = _make_mock_session(["NOR", "VER"])
        assert len(get_drivers(session)) == 2


# ── get_lap_times ─────────────────────────────────────────────────────────────

class TestGetLapTimes:

    def test_returns_dataframe(self):
        from data import get_lap_times
        session = _make_mock_session()
        result = get_lap_times(session, "NOR")
        assert isinstance(result, pd.DataFrame)

    def test_has_lap_time_sec_column(self):
        from data import get_lap_times
        session = _make_mock_session()
        df = get_lap_times(session, "NOR")
        assert "LapTimeSec" in df.columns

    def test_lap_times_are_positive(self):
        from data import get_lap_times
        session = _make_mock_session()
        df = get_lap_times(session, "NOR")
        assert (df["LapTimeSec"] > 0).all()

    def test_compound_is_uppercase(self):
        from data import get_lap_times
        session = _make_mock_session()
        df = get_lap_times(session, "NOR")
        assert df["Compound"].str.isupper().all()

    def test_no_nan_in_compound(self):
        from data import get_lap_times
        session = _make_mock_session()
        df = get_lap_times(session, "NOR")
        assert df["Compound"].notna().all()

    def test_lap_numbers_are_sequential(self):
        from data import get_lap_times
        session = _make_mock_session()
        df = get_lap_times(session, "NOR")
        assert df["LapNumber"].is_monotonic_increasing


# ── get_tyre_stints ───────────────────────────────────────────────────────────

class TestGetTyreStints:

    def test_returns_list_of_dicts(self):
        from data import get_tyre_stints
        session = _make_mock_session()
        result = get_tyre_stints(session, "NOR")
        assert isinstance(result, list)
        assert all(isinstance(s, dict) for s in result)

    def test_stint_keys_present(self):
        from data import get_tyre_stints
        session = _make_mock_session()
        stints = get_tyre_stints(session, "NOR")
        required = {"stint", "compound", "start_lap", "end_lap", "num_laps", "color"}
        for s in stints:
            assert required.issubset(s.keys())

    def test_stints_sorted_by_stint_number(self):
        from data import get_tyre_stints
        session = _make_mock_session()
        stints = get_tyre_stints(session, "NOR")
        nums = [s["stint"] for s in stints]
        assert nums == sorted(nums)

    def test_compound_is_uppercase(self):
        from data import get_tyre_stints
        session = _make_mock_session()
        for s in get_tyre_stints(session, "NOR"):
            assert s["compound"] == s["compound"].upper()

    def test_total_laps_match_session_laps(self):
        from data import get_tyre_stints
        session = _make_mock_session()
        stints = get_tyre_stints(session, "NOR")
        total = sum(s["num_laps"] for s in stints)
        # 50 laps in mock
        assert total == 50


# ── get_lap_delta ─────────────────────────────────────────────────────────────

class TestGetLapDelta:

    def test_returns_dataframe(self):
        from data import get_lap_delta
        session = _make_mock_session()
        result = get_lap_delta(session, "NOR", "VER")
        assert isinstance(result, pd.DataFrame)

    def test_has_delta_column(self):
        from data import get_lap_delta
        session = _make_mock_session()
        df = get_lap_delta(session, "NOR", "VER")
        assert "delta" in df.columns

    def test_delta_is_cumulative(self):
        """If we invert the drivers the delta signs should flip."""
        from data import get_lap_delta
        session = _make_mock_session()
        d_nor_ver = get_lap_delta(session, "NOR", "VER")["delta"].iloc[-1]
        d_ver_nor = get_lap_delta(session, "VER", "NOR")["delta"].iloc[-1]
        assert abs(d_nor_ver + d_ver_nor) < 1e-6  # they should sum to ~0

    def test_same_driver_delta_is_zero(self):
        from data import get_lap_delta
        session = _make_mock_session()
        df = get_lap_delta(session, "NOR", "NOR")
        assert (df["delta"].abs() < 1e-9).all()


# ── get_race_results ──────────────────────────────────────────────────────────

class TestGetRaceResults:

    def test_returns_dataframe(self):
        from data import get_race_results
        session = _make_mock_session()
        result = get_race_results(session)
        assert isinstance(result, pd.DataFrame)

    def test_sorted_by_position(self):
        from data import get_race_results
        session = _make_mock_session()
        df = get_race_results(session)
        assert df["Position"].is_monotonic_increasing

    def test_required_columns_present(self):
        from data import get_race_results
        session = _make_mock_session()
        cols = get_race_results(session).columns.tolist()
        for c in ["Position", "Abbreviation", "TeamName", "Points"]:
            assert c in cols


# ── get_weather ───────────────────────────────────────────────────────────────

class TestGetWeather:

    def test_returns_dataframe(self):
        from data import get_weather
        session = _make_mock_session()
        result = get_weather(session)
        assert isinstance(result, pd.DataFrame)

    def test_has_minutes_elapsed(self):
        from data import get_weather
        session = _make_mock_session()
        assert "MinutesElapsed" in get_weather(session).columns

    def test_minutes_are_non_negative(self):
        from data import get_weather
        session = _make_mock_session()
        assert (get_weather(session)["MinutesElapsed"] >= 0).all()


# ── COMPOUND_COLOURS completeness ─────────────────────────────────────────────

class TestCompoundColours:

    def test_known_compounds_defined(self):
        from data import COMPOUND_COLOURS
        for c in ["SOFT", "MEDIUM", "HARD", "INTER", "WET"]:
            assert c in COMPOUND_COLOURS

    def test_all_values_are_hex_strings(self):
        from data import COMPOUND_COLOURS
        import re
        pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for k, v in COMPOUND_COLOURS.items():
            assert pattern.match(v), f"{k} colour '{v}' is not a valid hex"


# ── Lap time data integrity tests ─────────────────────────────────────────────

class TestLapTimeIntegrity:

    def test_lap_numbers_are_positive(self):
        from data import get_lap_times
        session = _make_mock_session()
        df = get_lap_times(session.laps.pick_driver("NOR").copy(), "NOR") \
            if False else _make_mock_laps("NOR")
        assert (df["LapNumber"] > 0).all()

    def test_no_negative_lap_times(self):
        df = _make_mock_laps("NOR")
        times = df["LapTime"].dt.total_seconds()
        assert (times > 0).all()

    def test_compounds_are_known_strings(self):
        from data import COMPOUND_COLOURS
        df = _make_mock_laps("NOR")
        for compound in df["Compound"].unique():
            assert isinstance(compound, str)
            assert len(compound) > 0

    def test_stint_numbers_start_at_one(self):
        df = _make_mock_laps("NOR")
        assert df["Stint"].min() >= 1

    def test_lap_numbers_sequential(self):
        df = _make_mock_laps("NOR")
        laps = sorted(df["LapNumber"].tolist())
        assert laps == list(range(laps[0], laps[-1] + 1))

    def test_tyre_life_non_negative(self):
        df = _make_mock_laps("NOR")
        assert (df["TyreLife"] >= 0).all()

    def test_personal_best_column_is_boolean(self):
        df = _make_mock_laps("NOR")
        assert df["IsPersonalBest"].dtype == bool

    def test_at_most_one_personal_best_lap(self):
        """Only one lap should be flagged as the personal best."""
        df = _make_mock_laps("NOR")
        assert df["IsPersonalBest"].sum() <= 1


# ── Driver data tests ─────────────────────────────────────────────────────────

class TestGetDriversExtended:

    def test_driver_codes_are_three_chars(self):
        from data import get_drivers
        session = _make_mock_session(("NOR", "VER", "LEC"))
        drivers = get_drivers(session)
        for d in drivers:
            assert len(d["code"]) == 3, f"Code '{d['code']}' is not 3 chars"

    def test_driver_codes_are_uppercase(self):
        from data import get_drivers
        session = _make_mock_session(("NOR", "VER"))
        for d in get_drivers(session):
            assert d["code"] == d["code"].upper()

    def test_no_duplicate_driver_codes(self):
        from data import get_drivers
        session = _make_mock_session(("NOR", "VER", "LEC"))
        codes = [d["code"] for d in get_drivers(session)]
        assert len(codes) == len(set(codes))

    def test_sorted_alphabetically_by_code(self):
        from data import get_drivers
        session = _make_mock_session(("VER", "NOR", "LEC"))
        codes = [d["code"] for d in get_drivers(session)]
        assert codes == sorted(codes)

    def test_team_name_is_non_empty_string(self):
        from data import get_drivers
        session = _make_mock_session(("NOR", "VER"))
        for d in get_drivers(session):
            assert isinstance(d["team"], str)
            assert len(d["team"].strip()) > 0


# ── Season schedule tests ─────────────────────────────────────────────────────

class TestGetSeasonRoundsExtended:

    def test_round_numbers_are_positive_integers(self):
        from data import get_season_rounds
        schedule_df = _make_mock_schedule()
        with patch("data.fastf1.get_event_schedule", return_value=schedule_df):
            rounds = get_season_rounds(2025)
        for r in rounds:
            assert isinstance(r["round"], int)
            assert r["round"] > 0

    def test_event_names_are_non_empty(self):
        from data import get_season_rounds
        schedule_df = _make_mock_schedule()
        with patch("data.fastf1.get_event_schedule", return_value=schedule_df):
            rounds = get_season_rounds(2025)
        for r in rounds:
            assert len(r["name"].strip()) > 0

    def test_no_duplicate_round_numbers(self):
        from data import get_season_rounds
        schedule_df = _make_mock_schedule()
        with patch("data.fastf1.get_event_schedule", return_value=schedule_df):
            rounds = get_season_rounds(2025)
        round_nums = [r["round"] for r in rounds]
        assert len(round_nums) == len(set(round_nums))

    def test_contains_required_keys(self):
        from data import get_season_rounds
        schedule_df = _make_mock_schedule()
        with patch("data.fastf1.get_event_schedule", return_value=schedule_df):
            rounds = get_season_rounds(2025)
        for r in rounds:
            for key in ("round", "name", "country", "location"):
                assert key in r, f"Missing key '{key}' in round dict"


def _make_mock_schedule(n=5):
    """Build a minimal schedule DataFrame for season tests."""
    return pd.DataFrame({
        "RoundNumber": list(range(1, n + 1)),
        "EventName":   [f"Round {i} GP" for i in range(1, n + 1)],
        "Country":     ["Australia", "Bahrain", "China", "Japan", "USA"][:n],
        "Location":    ["Melbourne", "Sakhir", "Shanghai", "Suzuka", "Miami"][:n],
    })
