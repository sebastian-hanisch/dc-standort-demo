"""SETTING_SPECS-Permalink-Muster, Presets und Zufalls-Seed-Button (nach dem in `linehaul-demo` etablierten Muster).
Jede Zahl in den Hilfetexten ist in tests/test_claims.py belegt (aus dem echten Code neu berechnet)."""

import random

import streamlit as st

import dcs_constants as C

SETTING_SPECS = {
    "sites_slider": {"url": "s", "caster": int, "default": C.DEFAULT_SITES, "lo": C.SITES_MIN, "hi": C.SITES_MAX},
    "customers_slider": {"url": "c", "caster": int, "default": C.DEFAULT_CUSTOMERS, "lo": C.CUSTOMERS_MIN, "hi": C.CUSTOMERS_MAX},
    "fixed_slider": {"url": "f", "caster": int, "default": C.DEFAULT_FIXED, "lo": C.FIXED_MIN, "hi": C.FIXED_MAX},
    "seed_input": {"url": "seed", "caster": int, "default": C.DEFAULT_SEED, "lo": 0, "hi": C.SEED_MAX},
    "per_dc_slider": {"url": "pd", "caster": int, "default": C.DEFAULT_PER_DC, "lo": C.PER_DC_MIN, "hi": C.PER_DC_MAX},
    "growth_slider": {"url": "g", "caster": float, "default": C.DEFAULT_GROWTH, "lo": C.GROWTH_MIN, "hi": C.GROWTH_MAX},
    "shrink_slider": {"url": "sh", "caster": float, "default": C.DEFAULT_SHRINK, "lo": C.SHRINK_MIN, "hi": C.SHRINK_MAX},
}


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec["lo"], spec["hi"]


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec["default"]
    if "region_select" not in st.session_state:
        st.session_state["region_select"] = C.DEFAULT_REGION


def load_permalink_settings():
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec["url"] in qp:
            try:
                value = spec["caster"](qp[spec["url"]])
                value = max(spec["lo"], min(spec["hi"], value))
                st.session_state[state_key] = value
            except (ValueError, TypeError):
                pass
    if "reg" in qp and qp["reg"] in C.REGIONS:
        st.session_state["region_select"] = qp["reg"]
    st.session_state["permalink_loaded"] = True


def sync_query_params(sites, customers, fixed, seed, per_dc, region, growth, shrink):
    try:
        st.query_params["s"] = str(int(sites))
        st.query_params["c"] = str(int(customers))
        st.query_params["f"] = str(int(fixed))
        st.query_params["seed"] = str(int(seed))
        st.query_params["pd"] = str(int(per_dc))
        st.query_params["reg"] = str(region)
        st.query_params["g"] = str(growth)
        st.query_params["sh"] = str(shrink)
    except Exception:
        pass


def apply_preset(name):
    p = C.PRESETS[name]
    st.session_state["sites_slider"] = p["sites"]
    st.session_state["customers_slider"] = p["customers"]
    st.session_state["fixed_slider"] = p["fixed"]
    st.session_state["seed_input"] = p["seed"]
    st.session_state["per_dc_slider"] = p["per_dc"]
    st.session_state["region_select"] = p["region"]
    st.session_state["growth_slider"] = p["growth"]
    st.session_state["shrink_slider"] = p["shrink"]


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
