import dash_mantine_components as dmc
from dash_iconify import DashIconify
from django_plotly_dash import DjangoDash

from omero_metrics.styles import MANTINE_THEME, THEME

dashboard_name = "top_iu_microscope"
dash_app_microscope = DjangoDash(
    name=dashboard_name,
    serve_locally=True,
)


def _info_card(icon, label, description):
    return dmc.Paper(
        p="lg",
        radius="md",
        withBorder=True,
        style={"borderColor": THEME["border_light"]},
        children=[
            dmc.Stack(
                [
                    dmc.ThemeIcon(
                        DashIconify(icon=icon, width=22),
                        size=40,
                        radius="md",
                        color="green",
                        variant="light",
                    ),
                    dmc.Text(label, fw=600, size="sm", c=THEME["text"]["primary"]),
                    dmc.Text(description, size="xs", c=THEME["text"]["muted"]),
                ],
                gap="xs",
            ),
        ],
    )


dash_app_microscope.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        dmc.Container(
            [
                dmc.Stack(
                    [
                        # Hero section
                        dmc.Paper(
                            p="xl",
                            radius="md",
                            withBorder=True,
                            style={
                                "borderColor": THEME["border_light"],
                                "borderLeft": f"4px solid {THEME['primary']}",
                            },
                            children=[
                                dmc.Group(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Title(
                                                            "OMERO Metrics",
                                                            order=2,
                                                        ),
                                                        dmc.Badge(
                                                            "QC Dashboard",
                                                            color="green",
                                                            variant="light",
                                                            size="md",
                                                        ),
                                                    ],
                                                    gap="sm",
                                                ),
                                                dmc.Text(
                                                    "Microscopy quality control and performance tracking",
                                                    c=THEME["text"]["secondary"],
                                                    size="md",
                                                ),
                                            ],
                                            gap="xs",
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                            ],
                        ),
                        # Feature cards
                        dmc.SimpleGrid(
                            cols=3,
                            spacing="md",
                            children=[
                                _info_card(
                                    "tabler:microscope",
                                    "PSF Beads Analysis",
                                    "Measure resolution via point spread function bead imaging",
                                ),
                                _info_card(
                                    "tabler:brightness-half",
                                    "Field Illumination",
                                    "Assess illumination uniformity across the field of view",
                                ),
                                _info_card(
                                    "tabler:chart-line",
                                    "Trend Monitoring",
                                    "Track instrument performance over time across datasets",
                                ),
                            ],
                        ),
                        # Getting started
                        dmc.Alert(
                            "Select a project, dataset, or image from the left panel to begin.",
                            title="Getting Started",
                            color="green",
                            variant="light",
                            radius="md",
                            icon=DashIconify(icon="tabler:arrow-left", width=20),
                        ),
                    ],
                    gap="md",
                ),
            ],
            size="lg",
            p="lg",
            style={"backgroundColor": THEME["background"]},
        ),
    ],
)
