BUTTON_BASE = """
    QPushButton {
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 600;
        border-radius: 0px;
        border: none;
    }
    QPushButton:pressed {
        padding-top: 9px;
        padding-bottom: 7px;
    }
"""


def _build(extra: str) -> str:
    return BUTTON_BASE + extra


def primary(bg: str = "#2563eb", hover: str = "#1d4ed8", down: str = "#1e40af") -> str:
    return _build(f"""
        QPushButton {{ background: {bg}; color: white; }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:pressed {{ background: {down}; }}
        QPushButton:disabled {{ background: #94a3b8; color: #cbd5e1; }}
    """)


def success(bg: str = "#059669", hover: str = "#047857", down: str = "#065f46") -> str:
    return _build(f"""
        QPushButton {{ background: {bg}; color: white; }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:pressed {{ background: {down}; }}
        QPushButton:disabled {{ background: #94a3b8; color: #cbd5e1; }}
    """)


def danger(bg: str = "#ef4444", hover: str = "#dc2626", down: str = "#b91c1c") -> str:
    return _build(f"""
        QPushButton {{ background: {bg}; color: white; }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:pressed {{ background: {down}; }}
        QPushButton:disabled {{ background: #94a3b8; color: #cbd5e1; }}
    """)


def ghost(bg: str = "transparent", hover: str = "#f1f5f9") -> str:
    return _build(f"""
        QPushButton {{ background: {bg}; color: #334155; border: 1px solid #e2e8f0; }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:pressed {{ background: #e2e8f0; }}
        QPushButton:disabled {{ background: #f1f5f9; color: #94a3b8; border-color: #e2e8f0; }}
    """)


def small(text_color: str = "#334155") -> str:
    return f"""
        QPushButton {{
            background: transparent;
            color: {text_color};
            font-weight: 600;
            font-size: 11px;
            border-radius: 0px;
            padding: 4px 8px;
            border: 1px solid #e2e8f0;
        }}
        QPushButton:hover {{ background: #f1f5f9; }}
        QPushButton:pressed {{ background: #e2e8f0; }}
        QPushButton:disabled {{ color: #94a3b8; }}
    """
