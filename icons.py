# -*- coding: utf-8 -*-
"""
Icônes SVG animées en CSS pur (aucune dépendance externe, aucun emoji).
Chaque fonction renvoie une chaîne HTML/SVG prête à injecter via st.markdown.
"""

_STROKE = "currentColor"


def _wrap(svg_inner: str, size: int = 26, css_class: str = "") -> str:
    return (
        f'<svg class="af-icon {css_class}" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{_STROKE}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{svg_inner}</svg>'
    )


def icon_euro(size: int = 26) -> str:
    inner = (
        '<path class="af-draw" d="M17 6.5a6 6 0 1 0 0 11" />'
        '<line class="af-pulse-line" x1="4" y1="10" x2="14" y2="10" />'
        '<line class="af-pulse-line" x1="4" y1="14" x2="13" y2="14" />'
    )
    return _wrap(inner, size, "af-spin-slow")


def icon_clock(size: int = 26) -> str:
    inner = (
        '<circle cx="12" cy="12" r="9" />'
        '<line class="af-rotate" x1="12" y1="12" x2="12" y2="7" />'
        '<line class="af-rotate-slow" x1="12" y1="12" x2="15.5" y2="13.5" />'
    )
    return _wrap(inner, size)


def icon_wrench(size: int = 26) -> str:
    inner = (
        '<path class="af-wiggle" d="M14.7 6.3a4 4 0 0 0-5.4 4.9L4 16.5V20h3.5l5.3-5.3a4 4 0 0 0 4.9-5.4l-2.8 2.8-2-2z" />'
    )
    return _wrap(inner, size)


def icon_plane(size: int = 26) -> str:
    inner = (
        '<path class="af-fly" d="M3 13l7-2 4-7 2 1-2.5 6.5L21 10l1 2-7.5 3.5L13 21l-2-1 1-5.5L5 15z" />'
    )
    return _wrap(inner, size)


def icon_check(size: int = 26) -> str:
    inner = '<path class="af-draw-check" d="M4 12.5l5 5 11-11" />'
    return _wrap(inner, size)


def icon_gauge(size: int = 26) -> str:
    inner = (
        '<path d="M4 15a8 8 0 1 1 16 0" />'
        '<line class="af-needle" x1="12" y1="15" x2="16" y2="10" />'
        '<circle cx="12" cy="15" r="1.2" fill="currentColor" stroke="none" />'
    )
    return _wrap(inner, size)


def icon_login(size: int = 40) -> str:
    inner = (
        '<path class="af-fly" d="M3 13l7-2 4-7 2 1-2.5 6.5L21 10l1 2-7.5 3.5L13 21l-2-1 1-5.5L5 15z" />'
    )
    return _wrap(inner, size, "af-login-icon")


ICON_CSS = """
<style>
.af-icon { display:inline-block; vertical-align:middle; color:#0c3577; }
.af-icon.af-login-icon { color:#ee2932; }

@keyframes af-spin-slow { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
.af-spin-slow { animation: af-spin-slow 6s linear infinite; transform-origin:center; }

@keyframes af-rotate { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
.af-rotate { animation: af-rotate 4s linear infinite; transform-origin:12px 12px; }
.af-rotate-slow { animation: af-rotate 9s linear infinite; transform-origin:12px 12px; }

@keyframes af-wiggle { 0%,100%{transform:rotate(0deg);} 50%{transform:rotate(-14deg);} }
.af-wiggle { animation: af-wiggle 2.2s ease-in-out infinite; transform-origin:12px 12px; }

@keyframes af-fly { 0%{transform:translate(0,0);} 50%{transform:translate(2px,-2px);} 100%{transform:translate(0,0);} }
.af-fly { animation: af-fly 2.4s ease-in-out infinite; }

@keyframes af-draw { to { stroke-dashoffset:0; } }
.af-draw-check { stroke-dasharray:30; stroke-dashoffset:30; animation: af-draw 1.4s ease forwards infinite alternate; }

@keyframes af-needle-move { 0%,100%{transform:rotate(0deg);} 50%{transform:rotate(18deg);} }
.af-needle { animation: af-needle-move 2.8s ease-in-out infinite; transform-origin:12px 15px; }
</style>
"""
