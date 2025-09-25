"""Reusable UI helpers for section count badges and inline explainer triggers."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def context_key(*parts) -> str:
    """Generate a deterministic key for session_state tracking."""
    safe_parts = [str(part).strip().lower().replace(" ", "_") for part in parts if part is not None]
    return "why_open__" + "__".join(safe_parts)


def render_header_with_badge(
    title: str,
    df: pd.DataFrame | None,
    ctx_key: str,
    inline_help: bool = True,
) -> None:
    """Render a header with a count badge and optional 'why?' trigger."""

    count = 0 if df is None else int(len(df))
    col_title, col_badge, col_help = st.columns([1, 0.14, 0.12])

    with col_title:
        st.subheader(title)

    with col_badge:
        st.markdown(
            (
                "<div style='display:inline-block;padding:2px 10px;border-radius:12px;"
                "background:#2b2f36;color:#f5f7fa;font-size:0.85rem;'>"
                f"{count}</div>"
            ),
            unsafe_allow_html=True,
        )

    if inline_help:
        with col_help:
            if st.button("why?", key=f"{ctx_key}__btn", help="Explain these results"):
                st.session_state[ctx_key] = True


def is_why_open(ctx_key: str) -> bool:
    """Return whether the contextual explainer should render expanded."""
    return bool(st.session_state.get(ctx_key, False))


__all__ = ["context_key", "render_header_with_badge", "is_why_open"]
