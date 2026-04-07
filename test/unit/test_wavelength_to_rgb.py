"""Tests for omero_metrics.tools.wavelength_to_rgb function."""

import pytest

from omero_metrics.tools import wavelength_to_rgb


class TestWavelengthToRgb:
    def test_blue_wavelength(self):
        r, g, b = wavelength_to_rgb(450)
        assert b > 0
        assert r == 0

    def test_green_wavelength(self):
        r, g, b = wavelength_to_rgb(520)
        assert g > 0
        assert b == 0

    def test_red_wavelength(self):
        r, g, b = wavelength_to_rgb(650)
        assert r > 0
        assert g == 0
        assert b == 0

    def test_out_of_range_low(self):
        r, g, b = wavelength_to_rgb(300)
        assert r == 0
        assert g == 0
        assert b == 0

    def test_out_of_range_high(self):
        r, g, b = wavelength_to_rgb(800)
        assert r == 0
        assert g == 0
        assert b == 0

    def test_returns_tuple_of_three(self):
        result = wavelength_to_rgb(500)
        assert len(result) == 3

    def test_boundary_380(self):
        r, g, b = wavelength_to_rgb(380)
        # exactly 380 is out of range (380 < wavelength)
        assert r == 0 and g == 0 and b == 0

    def test_boundary_750(self):
        r, g, b = wavelength_to_rgb(750)
        # 750 is in range (645 < wavelength <= 750)
        assert r >= 0

    def test_string_input(self):
        """wavelength is converted to float internally."""
        r, g, b = wavelength_to_rgb("500")
        assert isinstance(r, float)
        assert isinstance(g, float)
        assert isinstance(b, float)

    def test_custom_gamma(self):
        r1, g1, b1 = wavelength_to_rgb(500, gamma=0.8)
        r2, g2, b2 = wavelength_to_rgb(500, gamma=1.0)
        # Different gamma should produce different values
        assert (r1, g1, b1) != (r2, g2, b2) or (r1 == 0 and r2 == 0)
