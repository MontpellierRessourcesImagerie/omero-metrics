# =============================================================================
# OMERO-Metrics Design System
# Aesthetic: "Lab Precision" — scientific clarity with warm natural tones
# =============================================================================

THEME = {
    "primary": "#1a7a32",
    "primary_light": "#e8f5e9",
    "primary_hover": "#15632a",
    "secondary": "#5c8a4d",
    "accent": "#0d9488",
    "background": "#fafbfc",
    "surface": "#ffffff",
    "surface_dim": "#f4f6f5",
    "border": "#dce4df",
    "border_light": "#e8ede9",
    "text": {
        "primary": "#1a2b1e",
        "secondary": "#5a6b5e",
        "muted": "#8a9b8e",
    },
    "error": "#c53030",
    "warning": "#d69e2e",
    "success": "#1a7a32",
}

# Channel colors — vibrant, distinguishable under microscopy conventions
COLORS_CHANNELS = ["#e53e3e", "#38a169", "#3182ce", "#d69e2e"]

# =============================================================================
# Tab styling
# =============================================================================

TAB_STYLES = {
    "tab": {
        "fontSize": "13px",
        "fontWeight": 600,
        "height": "38px",
        "borderRadius": "6px",
        "transition": "all 0.15s ease",
        "&[data-active]": {
            "backgroundColor": THEME["primary_light"],
            "color": THEME["primary"],
            "fontWeight": 700,
        },
    }
}

TAB_ITEM_STYLE = {
    "fontSize": "13px",
    "fontWeight": 600,
    "color": THEME["text"]["secondary"],
    "&[data-active]": {
        "backgroundColor": THEME["primary_light"],
        "color": THEME["primary"],
    },
}

# =============================================================================
# Input and form styling
# =============================================================================

INPUT_STYLES = {
    "rightSection": {"pointerEvents": "none"},
    "item": {"fontSize": "13px"},
    "input": {
        "borderColor": THEME["border"],
        "borderRadius": "6px",
        "&:focus": {"borderColor": THEME["primary"]},
    },
    "label": {"marginBottom": "6px", "fontWeight": 500, "fontSize": "13px"},
}

INPUT_BASE_STYLES = {
    "wrapper": {"height": "36px"},
    "input": {
        "height": "36px",
        "minHeight": "36px",
        "lineHeight": "36px",
        "padding": "0 12px",
        "display": "flex",
        "alignItems": "center",
        "borderColor": THEME["border"],
        "borderRadius": "6px",
        "fontSize": "13px",
        "transition": "border-color 0.15s ease",
        "&:focus": {"borderColor": THEME["primary"]},
    },
    "rightSection": {
        "pointerEvents": "none",
        "height": "36px",
        "display": "flex",
        "alignItems": "center",
    },
    "leftSection": {
        "height": "36px",
        "display": "flex",
        "alignItems": "center",
    },
    "label": {
        "marginBottom": "6px",
        "fontSize": "13px",
        "fontWeight": 500,
        "color": THEME["text"]["primary"],
    },
    "item": {"fontSize": "13px"},
}

SELECT_STYLES = {
    **INPUT_BASE_STYLES,
    "dropdown": {
        "borderRadius": "8px",
        "border": f'1px solid {THEME["border"]}',
        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.08)",
    },
    "input": {
        **INPUT_BASE_STYLES["input"],
        "paddingLeft": "36px",
    },
}

DATEPICKER_STYLES = {
    **INPUT_BASE_STYLES,
    "calendar": {
        "borderRadius": "8px",
        "border": f'1px solid {THEME["border"]}',
    },
    "input": {
        **INPUT_BASE_STYLES["input"],
        "paddingLeft": "36px",
    },
}

# =============================================================================
# Table styling
# =============================================================================

TABLE_MANTINE_STYLE = {
    "width": "100%",
    "height": "auto",
    "borderRadius": "8px",
    "overflow": "hidden",
}

TABLE_STYLE = {
    "overflowX": "auto",
    "borderRadius": "8px",
    "fontFamily": "inherit",
    "borderCollapse": "collapse",
    "boxShadow": "0 1px 3px rgba(0, 0, 0, 0.06)",
    "margin": "0",
}

TABLE_CELL_STYLE = {
    "whiteSpace": "normal",
    "height": "36px",
    "minWidth": "90px",
    "width": "100px",
    "maxWidth": "140px",
    "textAlign": "left",
    "textOverflow": "ellipsis",
    "fontSize": "12px",
    "color": THEME["text"]["primary"],
    "fontWeight": "400",
    "padding": "8px 12px",
    "borderBottom": f'1px solid {THEME["border_light"]}',
}

TABLE_HEADER_STYLE = {
    "backgroundColor": THEME["primary"],
    "fontWeight": "600",
    "fontSize": "12px",
    "letterSpacing": "0.02em",
    "textTransform": "uppercase",
    "padding": "10px 12px",
    "color": "white",
    "borderBottom": "none",
}

STYLE_DATA_CONDITIONAL = [
    {
        "if": {"row_index": "odd"},
        "backgroundColor": THEME["surface"],
    },
    {
        "if": {"row_index": "even"},
        "backgroundColor": THEME["surface_dim"],
    },
]

# =============================================================================
# Layout styling
# =============================================================================

PAPER_STYLE = {
    "width": "100%",
    "maxWidth": "100%",
    "margin": "auto",
}

FIELDSET_STYLE = {
    "padding": "12px",
    "margin": "8px",
}

CARD_STYLE_ELEVATED = {
    "backgroundColor": THEME["surface"],
    "borderRadius": "10px",
    "border": f'1px solid {THEME["border_light"]}',
    "padding": "20px",
    "height": "100%",
    "boxShadow": "0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06)",
}

BUTTON_STYLE = {
    "backgroundColor": THEME["primary"],
    "color": "white",
    "fontSize": "13px",
    "fontWeight": 600,
    "height": "36px",
    "padding": "0 16px",
    "borderRadius": "6px",
}

CONTAINER_STYLE = {
    "backgroundColor": THEME["background"],
    "borderRadius": "10px",
    "padding": "16px",
}

HEADER_PAPER_STYLE = {
    "shadow": "xs",
    "p": "lg",
    "mb": "lg",
    "radius": "md",
}

CONTENT_PAPER_STYLE = {
    "shadow": "xs",
    "p": "md",
    "radius": "md",
    "h": "100%",
}

GRAPH_STYLE = {
    "height": "300px",
}

# =============================================================================
# Mantine theme configuration
# =============================================================================

MANTINE_THEME = {
    "colorScheme": "light",
    "primaryColor": "green",
    "fontFamily": "'Source Sans 3', 'Segoe UI', sans-serif",
    "headings": {
        "fontFamily": "'Source Sans 3', 'Segoe UI', sans-serif",
        "fontWeight": "700",
    },
    "components": {
        "Button": {
            "styles": {
                "root": {
                    "fontWeight": 600,
                    "borderRadius": "6px",
                    "fontSize": "13px",
                }
            }
        },
        "Select": {"styles": SELECT_STYLES},
        "DatePicker": {"styles": DATEPICKER_STYLES},
        "Input": {"styles": INPUT_STYLES},
        "Paper": {
            "defaultProps": {"withBorder": True},
            "styles": {
                "root": {
                    "borderColor": THEME["border_light"],
                    "borderRadius": "10px",
                }
            },
        },
        "Card": {"styles": {"root": {"borderRadius": "10px"}}},
        "Title": {
            "styles": {
                "root": {
                    "letterSpacing": "-0.02em",
                    "color": THEME["text"]["primary"],
                }
            }
        },
        "Alert": {"styles": {"root": {"borderRadius": "8px"}}},
        "Badge": {
            "styles": {
                "root": {
                    "fontWeight": 600,
                    "fontSize": "11px",
                    "letterSpacing": "0.02em",
                    "textTransform": "uppercase",
                }
            }
        },
        "Table": {
            "styles": {
                "thead": {"backgroundColor": THEME["surface_dim"]},
                "th": {
                    "fontSize": "12px",
                    "fontWeight": 600,
                    "color": THEME["text"]["secondary"],
                    "textTransform": "uppercase",
                    "letterSpacing": "0.03em",
                    "padding": "10px 12px",
                },
                "td": {
                    "fontSize": "13px",
                    "padding": "8px 12px",
                    "color": THEME["text"]["primary"],
                },
            }
        },
        "Tabs": {"styles": TAB_STYLES},
    },
}

# =============================================================================
# Chart / Plotly layout
# =============================================================================

PLOT_LAYOUT = {
    "margin": dict(l=40, r=40, t=40, b=40),
    "plot_bgcolor": THEME["surface"],
    "paper_bgcolor": THEME["surface"],
    "xaxis_showgrid": False,
    "yaxis_showgrid": False,
    "xaxis_zeroline": False,
    "yaxis_zeroline": False,
}

PLOTLY_LAYOUT = {
    "margin": dict(l=32, r=32, t=32, b=32),
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "font": dict(
        family="'Source Sans 3', sans-serif",
        size=12,
        color=THEME["text"]["secondary"],
    ),
    "xaxis": dict(showgrid=False, zeroline=False),
    "yaxis": dict(showgrid=False, zeroline=False),
    "coloraxis_colorbar": dict(
        thickness=12,
        len=0.65,
        title=dict(side="right", font=dict(size=11)),
        tickfont=dict(size=10),
        outlinewidth=0,
    ),
}

LINE_CHART_SERIES = [
    {"name": "Diagonal (\u2198)", "color": "violet.7"},
    {"name": "Diagonal (\u2197)", "color": "blue.7"},
    {"name": "Horizontal (\u2192)", "color": "pink.7"},
    {"name": "Vertical (\u2193)", "color": "teal.7"},
]
