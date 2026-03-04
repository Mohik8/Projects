"""
test_cache.py — Unit tests for the LRU cache on load_session()

Verifies:
- Identical arguments return the cached (same) object
- Different arguments bypass the cache
- maxsize=8 evicts the LRU entry when full
- cache_clear() resets hit/miss counters
- Cache keys are built from (year, round_number, session_type)
"""
import pytest
from unittest.mock import MagicMock, patch, call


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_fake_session(label="session"):
    s = MagicMock()
    s.label = label
    return s


# ── Cache hit / miss behaviour ────────────────────────────────────────────────

class TestLruCacheBehaviour:

    def setup_method(self):
        """Clear the LRU cache before every test to prevent state leakage."""
        from data import load_session
        load_session.cache_clear()

    def test_same_args_returns_same_object(self):
        """Warm hit: (2025, 1, 'R') twice must return THE SAME Python object."""
        fake = _make_fake_session("australia-2025")
        with patch("data.fastf1.get_session", return_value=fake) as mock_get, \
             patch.object(fake, "load"):
            from data import load_session
            result1 = load_session(2025, 1, "R")
            result2 = load_session(2025, 1, "R")
            assert result1 is result2
            # FastF1 should only have been called ONCE
            assert mock_get.call_count == 1

    def test_different_round_is_cache_miss(self):
        """(2025, 1, 'R') and (2025, 2, 'R') are distinct cache keys."""
        fake1 = _make_fake_session("r1")
        fake2 = _make_fake_session("r2")
        sessions = [fake1, fake2]

        with patch("data.fastf1.get_session", side_effect=lambda y, r, s: sessions.pop(0)) as mock_get:
            for s in sessions:
                s.load = MagicMock()
            from data import load_session
            r1 = load_session(2025, 1, "R")
            r2 = load_session(2025, 2, "R")
            assert r1 is not r2
            assert mock_get.call_count == 2

    def test_different_year_is_cache_miss(self):
        fake24 = _make_fake_session("2024")
        fake25 = _make_fake_session("2025")

        with patch("data.fastf1.get_session", side_effect=[fake24, fake25]):
            fake24.load = MagicMock()
            fake25.load = MagicMock()
            from data import load_session
            a = load_session(2024, 1, "R")
            b = load_session(2025, 1, "R")
            assert a is not b

    def test_different_session_type_is_cache_miss(self):
        fake_r = _make_fake_session("race")
        fake_q = _make_fake_session("quali")

        with patch("data.fastf1.get_session", side_effect=[fake_r, fake_q]):
            fake_r.load = MagicMock()
            fake_q.load = MagicMock()
            from data import load_session
            a = load_session(2025, 1, "R")
            b = load_session(2025, 1, "Q")
            assert a is not b

    def test_cache_info_hit_count_increments(self):
        fake = _make_fake_session()
        with patch("data.fastf1.get_session", return_value=fake), \
             patch.object(fake, "load"):
            from data import load_session
            load_session(2025, 1, "R")  # miss
            load_session(2025, 1, "R")  # hit
            load_session(2025, 1, "R")  # hit
            info = load_session.cache_info()
            assert info.hits == 2
            assert info.misses == 1

    def test_cache_clear_resets_stats(self):
        fake = _make_fake_session()
        with patch("data.fastf1.get_session", return_value=fake), \
             patch.object(fake, "load"):
            from data import load_session
            load_session(2025, 1, "R")
            load_session(2025, 1, "R")
            load_session.cache_clear()
            info = load_session.cache_info()
            assert info.hits == 0
            assert info.misses == 0
            assert info.currsize == 0


# ── maxsize=8 eviction ────────────────────────────────────────────────────────

class TestCacheEviction:

    def setup_method(self):
        from data import load_session
        load_session.cache_clear()

    def test_maxsize_is_8(self):
        from data import load_session
        assert load_session.cache_info().maxsize == 8

    def test_evicts_lru_after_maxsize_reached(self):
        """
        Fill 8 slots, then request a 9th. The first entry (round 1) should be
        evicted (LRU). Requesting round 1 again should trigger a new miss.
        """
        sessions = {r: _make_fake_session(f"r{r}") for r in range(1, 11)}

        def fake_get(year, rnd, stype):
            s = sessions[rnd]
            s.load = MagicMock()
            return s

        with patch("data.fastf1.get_session", side_effect=fake_get):
            from data import load_session

            # Fill cache with rounds 1-8
            for rnd in range(1, 9):
                load_session(2025, rnd, "R")

            assert load_session.cache_info().currsize == 8

            # Round 9 evicts the LRU (round 1)
            load_session(2025, 9, "R")
            assert load_session.cache_info().currsize == 8

            # Requesting round 1 again should be a fresh miss
            misses_before = load_session.cache_info().misses
            load_session(2025, 1, "R")
            assert load_session.cache_info().misses == misses_before + 1

    def test_currsize_never_exceeds_maxsize(self):
        sessions_list = [_make_fake_session(f"s{i}") for i in range(20)]
        for s in sessions_list:
            s.load = MagicMock()
        it = iter(sessions_list)

        with patch("data.fastf1.get_session", side_effect=lambda y, r, s: next(it)):
            from data import load_session
            for rnd in range(1, 16):
                load_session(2025, rnd, "R")
            assert load_session.cache_info().currsize <= 8


# ── Session loading integrity ─────────────────────────────────────────────────

class TestSessionLoadCall:

    def setup_method(self):
        from data import load_session
        load_session.cache_clear()

    def test_session_loaded_with_all_data_flags(self):
        """load() must be called with telemetry=True, laps=True, weather=True."""
        fake = _make_fake_session()
        fake.load = MagicMock()

        with patch("data.fastf1.get_session", return_value=fake):
            from data import load_session
            load_session(2025, 1, "R")
            fake.load.assert_called_once_with(
                telemetry=True, laps=True, weather=True
            )

    def test_session_not_reloaded_on_cache_hit(self):
        """load() should only be called once even with multiple lookups."""
        fake = _make_fake_session()
        fake.load = MagicMock()

        with patch("data.fastf1.get_session", return_value=fake):
            from data import load_session
            for _ in range(5):
                load_session(2025, 1, "R")
            fake.load.assert_called_once()


# ── Cache thread-safety / isolation ──────────────────────────────────────────

class TestCacheIsolation:

    def setup_method(self):
        from data import load_session
        load_session.cache_clear()

    def test_qualifying_and_race_cached_independently(self):
        """Q and R for the same event must each get their own cache slot."""
        fake_r = _make_fake_session("race")
        fake_q = _make_fake_session("qual")
        fake_r.load = MagicMock()
        fake_q.load = MagicMock()
        call_map = {"R": fake_r, "Q": fake_q}

        with patch("data.fastf1.get_session", side_effect=lambda y, r, s: call_map[s]):
            from data import load_session
            load_session(2025, 1, "R")
            load_session(2025, 1, "Q")

        assert load_session.cache_info().currsize == 2
        assert load_session.cache_info().misses  == 2

    def test_practice_sessions_each_get_slot(self):
        """FP1, FP2, FP3 must produce 3 distinct cache entries."""
        for stype in ("FP1", "FP2", "FP3"):
            fake = _make_fake_session(stype)
            fake.load = MagicMock()
            with patch("data.fastf1.get_session", return_value=fake):
                from data import load_session
                load_session(2025, 1, stype)

        assert load_session.cache_info().currsize == 3

    def test_cache_warm_hit_does_not_call_load(self):
        """Once cached, load() must never be called again for that key."""
        fake = _make_fake_session()
        fake.load = MagicMock()

        with patch("data.fastf1.get_session", return_value=fake):
            from data import load_session
            load_session(2025, 5, "R")  # cold
            load_session(2025, 5, "R")  # warm
            load_session(2025, 5, "R")  # warm

        assert fake.load.call_count == 1

    def test_clear_then_reload_counts_as_miss(self):
        """After cache_clear(), the same key must produce a new miss."""
        fake = _make_fake_session()
        fake.load = MagicMock()

        with patch("data.fastf1.get_session", return_value=fake):
            from data import load_session
            load_session(2025, 1, "R")
            load_session.cache_clear()
            load_session(2025, 1, "R")

        assert load_session.cache_info().misses == 1  # fresh miss after clear


# ── Parameter boundary tests ──────────────────────────────────────────────────

class TestCacheParameterBoundaries:

    def setup_method(self):
        from data import load_session
        load_session.cache_clear()

    def test_round_zero_and_negative_are_distinct_keys(self):
        """Unusual round values should still cache independently."""
        fake0 = _make_fake_session("r0")
        fakem = _make_fake_session("rm")
        fake0.load = MagicMock()
        fakem.load = MagicMock()
        responses = {0: fake0, -1: fakem}

        with patch("data.fastf1.get_session", side_effect=lambda y, r, s: responses[r]):
            from data import load_session
            load_session(2025, 0,  "R")
            load_session(2025, -1, "R")

        assert load_session.cache_info().currsize == 2

    def test_year_boundary_2018_and_2026(self):
        """Earliest and latest supported years cache correctly."""
        fake18 = _make_fake_session("2018")
        fake26 = _make_fake_session("2026")
        fake18.load = MagicMock()
        fake26.load = MagicMock()
        call_map = {2018: fake18, 2026: fake26}

        with patch("data.fastf1.get_session", side_effect=lambda y, r, s: call_map[y]):
            from data import load_session
            r18 = load_session(2018, 1, "R")
            r26 = load_session(2026, 1, "R")

        assert r18 is not r26
        assert load_session.cache_info().misses == 2
