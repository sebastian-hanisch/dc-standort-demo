import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dcs_constants as C
from dcs_presets import SETTING_SPECS


def test_every_preset_has_all_keys():
    required = {"sites", "customers", "fixed", "seed", "per_dc", "region", "growth", "shrink"}
    for name, p in C.PRESETS.items():
        assert required.issubset(p.keys()), name


def test_preset_values_within_bounds():
    for name, p in C.PRESETS.items():
        assert C.SITES_MIN <= p["sites"] <= C.SITES_MAX, name
        assert C.CUSTOMERS_MIN <= p["customers"] <= C.CUSTOMERS_MAX, name
        assert C.FIXED_MIN <= p["fixed"] <= C.FIXED_MAX, name
        assert C.PER_DC_MIN <= p["per_dc"] <= C.PER_DC_MAX, name
        assert p["region"] in C.REGIONS, name
        assert C.GROWTH_MIN <= p["growth"] <= C.GROWTH_MAX, name
        assert C.SHRINK_MIN <= p["shrink"] <= C.SHRINK_MAX, name


def test_setting_specs_defaults_within_own_bounds():
    for key, spec in SETTING_SPECS.items():
        assert spec["lo"] <= spec["default"] <= spec["hi"], key


def test_per_dc_markers_within_slider_bounds():
    for n in C.PER_DC_MARKERS:
        assert C.PER_DC_MIN <= n <= C.PER_DC_MAX
