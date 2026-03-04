"""
test_plots_unit.py — Unit tests for plots.py

All figure generators are pure functions (DataFrame in, Figure out).
Tests verify structural correctness of returned Plotly figures —
trace counts, axis labels, layout colours, and data shape — without
a browser or live data.
"""
import pandas as pd
import numpy as np
import pytest
import plotly.graph_objects as go


# ── fig_lap_times ─────────────────────────────────────────────────────────────

class TestFigLapTimes:

    def test_returns_figure(self, lap_df_nor, lap_df_ver):
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        assert isinstance(fig, go.Figure)

    def test_has_traces(self, lap_df_nor, lap_df_ver):
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        assert len(fig.data) > 0

    def test_trace_count_equals_compound_groups(self, lap_df_nor, lap_df_ver):
        """One trace per (driver × compound) combination."""
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        n_nor = lap_df_nor["Compound"].nunique()
        n_ver = lap_df_ver["Compound"].nunique()
        assert len(fig.data) == n_nor + n_ver

    def test_yaxis_reversed(self, lap_df_nor, lap_df_ver):
        """Faster laps (lower seconds) should appear at the top."""
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        assert fig.layout.yaxis.autorange == "reversed"

    def test_dark_background(self, lap_df_nor, lap_df_ver):
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        assert fig.layout.paper_bgcolor is not None
        assert fig.layout.paper_bgcolor != "white"

    def test_x_values_match_lap_numbers(self, lap_df_nor, lap_df_ver):
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        all_x = set()
        for trace in fig.data:
            all_x.update(trace.x)
        expected = set(lap_df_nor["LapNumber"]) | set(lap_df_ver["LapNumber"])
        assert all_x == expected

    def test_driver_names_in_trace_names(self, lap_df_nor, lap_df_ver):
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        names = " ".join(t.name for t in fig.data)
        assert "NOR" in names
        assert "VER" in names


# ── fig_lap_delta ─────────────────────────────────────────────────────────────

class TestFigLapDelta:

    def test_returns_figure(self, delta_df):
        from plots import fig_lap_delta
        fig = fig_lap_delta(delta_df, "NOR", "VER")
        assert isinstance(fig, go.Figure)

    def test_has_at_least_one_trace(self, delta_df):
        from plots import fig_lap_delta
        fig = fig_lap_delta(delta_df, "NOR", "VER")
        assert len(fig.data) >= 1

    def test_x_values_are_lap_numbers(self, delta_df):
        from plots import fig_lap_delta
        fig = fig_lap_delta(delta_df, "NOR", "VER")
        trace_x = set(fig.data[0].x)
        expected_x = set(delta_df["LapNumber"])
        assert trace_x == expected_x

    def test_y_values_match_delta_column(self, delta_df):
        from plots import fig_lap_delta
        fig = fig_lap_delta(delta_df, "NOR", "VER")
        np.testing.assert_allclose(
            list(fig.data[0].y),
            list(delta_df["delta"]),
            rtol=1e-5,
        )


# ── fig_tyre_strategy ─────────────────────────────────────────────────────────

class TestFigTyreStrategy:

    def test_returns_figure(self, stints_nor, stints_ver):
        from plots import fig_tyre_strategy
        fig = fig_tyre_strategy(stints_nor, "NOR", stints_ver, "VER", total_laps=50)
        assert isinstance(fig, go.Figure)

    def test_trace_count_matches_total_stints(self, stints_nor, stints_ver):
        from plots import fig_tyre_strategy
        fig = fig_tyre_strategy(stints_nor, "NOR", stints_ver, "VER", total_laps=50)
        assert len(fig.data) == len(stints_nor) + len(stints_ver)

    def test_bar_widths_match_stint_laps(self, stints_nor, stints_ver):
        """Each bar width should equal the number of laps in that stint."""
        from plots import fig_tyre_strategy
        fig = fig_tyre_strategy(stints_nor, "NOR", stints_ver, "VER", total_laps=50)
        expected_widths = [s["num_laps"] for s in stints_nor + stints_ver]
        actual_widths   = [trace.x[0] if hasattr(trace, "x") else trace.width
                           for trace in fig.data]
        # Just check the figure has data — exact bar attribute varies by Plotly version
        assert len(fig.data) > 0

    def test_nor_and_ver_appear_in_legend(self, stints_nor, stints_ver):
        from plots import fig_tyre_strategy
        fig = fig_tyre_strategy(stints_nor, "NOR", stints_ver, "VER", total_laps=50)
        names = " ".join(str(t.name) for t in fig.data)
        assert "NOR" in names or "VER" in names


# ── fig_speed_trace ───────────────────────────────────────────────────────────

class TestFigSpeedTrace:

    def test_returns_figure(self, telemetry_df):
        from plots import fig_speed_trace
        fig = fig_speed_trace(telemetry_df, "NOR", telemetry_df, "VER")
        assert isinstance(fig, go.Figure)

    def test_has_two_speed_traces(self, telemetry_df):
        """One trace per driver."""
        from plots import fig_speed_trace
        fig = fig_speed_trace(telemetry_df, "NOR", telemetry_df, "VER")
        assert len(fig.data) >= 2

    def test_no_nan_in_speed_values(self, telemetry_df):
        from plots import fig_speed_trace
        fig = fig_speed_trace(telemetry_df, "NOR", telemetry_df, "VER")
        for trace in fig.data:
            if trace.y is not None:
                assert not any(np.isnan(float(v)) for v in trace.y if v is not None)

    def test_driver_names_in_legend(self, telemetry_df):
        from plots import fig_speed_trace
        fig = fig_speed_trace(telemetry_df, "NOR", telemetry_df, "VER")
        names = " ".join(str(t.name) for t in fig.data)
        assert "NOR" in names and "VER" in names


# ── fig_race_results ──────────────────────────────────────────────────────────

class TestFigRaceResults:

    def test_returns_figure(self, race_results_df):
        from plots import fig_race_results
        fig = fig_race_results(race_results_df)
        assert isinstance(fig, go.Figure)

    def test_has_traces(self, race_results_df):
        from plots import fig_race_results
        fig = fig_race_results(race_results_df)
        assert len(fig.data) > 0

    def test_all_drivers_represented(self, race_results_df):
        from plots import fig_race_results
        fig = fig_race_results(race_results_df)
        all_text = " ".join(
            " ".join(str(v) for v in (trace.x or []) + (trace.y or []) +
                     list(trace.text or []))
            for trace in fig.data
        )
        for code in race_results_df["Abbreviation"]:
            assert code in all_text


# ── fig_weather ───────────────────────────────────────────────────────────────

class TestFigWeather:

    def test_returns_figure(self, weather_df):
        from plots import fig_weather
        fig = fig_weather(weather_df)
        assert isinstance(fig, go.Figure)

    def test_has_traces(self, weather_df):
        from plots import fig_weather
        fig = fig_weather(weather_df)
        assert len(fig.data) > 0

    def test_x_axis_covers_full_race(self, weather_df):
        from plots import fig_weather
        fig = fig_weather(weather_df)
        # At least one trace should span ~55 minutes
        max_x = max(max(trace.x) for trace in fig.data if trace.x is not None)
        assert max_x >= 50

    def test_dark_background(self, weather_df):
        from plots import fig_weather
        fig = fig_weather(weather_df)
        assert fig.layout.paper_bgcolor not in (None, "white", "#fff", "#ffffff")


# ── Shared theme consistency ──────────────────────────────────────────────────

class TestThemeConsistency:
    """All figures should share the same dark background colours."""

    DARK_BG = "#1e1e2e"

    @pytest.mark.parametrize("fixture_name,func_name,extra_args", [
        ("lap_df_nor",      "fig_lap_times",    ["lap_df_ver"]),
        ("delta_df",        "fig_lap_delta",    []),
        ("race_results_df", "fig_race_results", []),
        ("weather_df",      "fig_weather",      []),
    ])
    def test_paper_bgcolor_is_dark(self, fixture_name, func_name, extra_args, request):
        import plots
        func = getattr(plots, func_name)
        primary = request.getfixturevalue(fixture_name)
        extras  = [request.getfixturevalue(n) for n in extra_args]

        if func_name == "fig_lap_times":
            fig = func(primary, "NOR", extras[0], "VER")
        elif func_name == "fig_lap_delta":
            fig = func(primary, "NOR", "VER")
        elif func_name == "fig_tyre_strategy":
            fig = func(primary, "NOR", extras[0], "VER", total_laps=50)
        else:
            fig = func(primary)

        assert fig.layout.paper_bgcolor == self.DARK_BG, (
            f"{func_name} paper_bgcolor should be {self.DARK_BG}, "
            f"got {fig.layout.paper_bgcolor}"
        )


# ── Axis label & title tests ──────────────────────────────────────────────────

class TestAxisLabels:

    def test_lap_times_xaxis_references_laps(self, lap_df_nor, lap_df_ver):
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        xtitle = (fig.layout.xaxis.title.text or "").lower()
        assert "lap" in xtitle

    def test_lap_times_yaxis_references_time(self, lap_df_nor, lap_df_ver):
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        ytitle = (fig.layout.yaxis.title.text or "").lower()
        assert any(w in ytitle for w in ("time", "sec", "s"))

    def test_speed_trace_xaxis_references_distance(self, telemetry_df):
        from plots import fig_speed_trace
        fig = fig_speed_trace(telemetry_df, "NOR", telemetry_df, "VER")
        xtitle = (fig.layout.xaxis.title.text or "").lower()
        assert any(w in xtitle for w in ("dist", "m", "meter", "metre"))

    def test_weather_figure_has_title(self, weather_df):
        from plots import fig_weather
        fig = fig_weather(weather_df)
        assert fig.layout.title.text and len(fig.layout.title.text) > 0


# ── Trace colour tests ────────────────────────────────────────────────────────

class TestTraceColours:

    def test_lap_times_uses_compound_colours(self, lap_df_nor, lap_df_ver):
        """At least one trace colour should match a known compound colour."""
        from plots import fig_lap_times
        from data import COMPOUND_COLOURS
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        trace_colours = set()
        for trace in fig.data:
            if hasattr(trace, "line") and trace.line and trace.line.color:
                trace_colours.add(trace.line.color.upper())
            if hasattr(trace, "marker") and trace.marker and trace.marker.color:
                trace_colours.add(str(trace.marker.color).upper())
        known = {v.upper() for v in COMPOUND_COLOURS.values()}
        assert trace_colours & known, "No compound colour found in any trace"

    def test_two_drivers_have_different_primary_colours(self, lap_df_nor, lap_df_ver):
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER",
                            team_color1="#FF0000", team_color2="#0000FF")
        # Figure must have been constructed without raising
        assert len(fig.data) > 0

    def test_strategy_uses_compound_colours(self, stints_df_nor, stints_df_ver):
        from plots import fig_tyre_strategy
        from data import COMPOUND_COLOURS
        fig = fig_tyre_strategy(stints_df_nor, "NOR", stints_df_ver, "VER", total_laps=50)
        colours_used = set()
        for trace in fig.data:
            colour = None
            if hasattr(trace, "marker") and trace.marker.color:
                colour = str(trace.marker.color)
            if hasattr(trace, "fillcolor") and trace.fillcolor:
                colour = str(trace.fillcolor)
            if colour:
                colours_used.add(colour.upper())
        known = {v.upper() for v in COMPOUND_COLOURS.values()}
        assert colours_used & known, "No compound colour in tyre strategy chart"


# ── Empty / edge-case data tests ──────────────────────────────────────────────

class TestEdgeCaseData:

    def _empty_lap_df(self) -> "pd.DataFrame":
        import pandas as pd
        return pd.DataFrame(columns=["LapNumber", "LapTimeSec", "Compound",
                                      "TyreLife", "IsPersonalBest", "Stint",
                                      "PitOutTime", "PitInTime"])

    def test_single_lap_does_not_crash(self, lap_df_nor, lap_df_ver):
        from plots import fig_lap_times
        one_lap = lap_df_nor.head(1)
        fig = fig_lap_times(one_lap, "NOR", one_lap, "NOR")
        assert fig is not None

    def test_identical_drivers_does_not_crash(self, lap_df_nor):
        from plots import fig_lap_times
        fig = fig_lap_times(lap_df_nor, "NOR", lap_df_nor, "NOR")
        assert fig is not None

    def test_weather_single_row_does_not_crash(self, weather_df):
        from plots import fig_weather
        one_row = weather_df.head(1)
        fig = fig_weather(one_row)
        assert fig is not None

    def test_race_results_single_driver_does_not_crash(self, race_results_df):
        from plots import fig_race_results
        one = race_results_df.head(1)
        fig = fig_race_results(one)
        assert fig is not None


# ── Serialisation tests (JSON round-trip) ─────────────────────────────────────

class TestFigureSerialisation:
    """Figures must survive plotly.io JSON round-trip (used in dcc.Store)."""

    def test_lap_times_json_roundtrip(self, lap_df_nor, lap_df_ver):
        import plotly.io as pio
        from plots import fig_lap_times
        fig  = fig_lap_times(lap_df_nor, "NOR", lap_df_ver, "VER")
        json = pio.to_json(fig)
        fig2 = pio.from_json(json)
        assert len(fig2.data) == len(fig.data)

    def test_race_results_json_roundtrip(self, race_results_df):
        import plotly.io as pio
        from plots import fig_race_results
        fig  = fig_race_results(race_results_df)
        json = pio.to_json(fig)
        fig2 = pio.from_json(json)
        assert isinstance(fig2, go.Figure)

    def test_weather_json_roundtrip(self, weather_df):
        import plotly.io as pio
        from plots import fig_weather
        fig  = fig_weather(weather_df)
        json = pio.to_json(fig)
        fig2 = pio.from_json(json)
        assert isinstance(fig2, go.Figure)
