import logging

import dash
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc, html
from django_plotly_dash import DjangoDash
from plotly.subplots import make_subplots

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics.styles import MANTINE_THEME, PLOTLY_LAYOUT, THEME
from omero_metrics.tools import load
from omero_metrics.tools.serializers import deserialize, deserialize_partial

logger = logging.getLogger(__name__)
dashboard_name = "omero_image_average_bead"

omero_image_average_bead = DjangoDash(name=dashboard_name, serve_locally=True)

omero_image_average_bead.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # Header Section
        my_components.header_component(
            "PSF Beads Analysis",
            "Advanced Microscopy Image Analysis",
            "PSF beads Analysis",
            load_buttons=False,
        ),
        # Main Content
        dmc.Container(
            [
                html.Div(id="blank-input"),
                # Main Content
                dmc.Stack(
                    [
                        dmc.Grid(
                            children=[
                                dmc.GridCol(
                                    [
                                        dmc.Paper(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Text(
                                                            "Average Bead Image",
                                                            size="lg",
                                                            fw=500,
                                                            c=THEME["primary"],
                                                        ),
                                                        dmc.Tooltip(
                                                            label="Average bead image max intensity projections and profiles",
                                                            children=[
                                                                my_components.get_icon(
                                                                    "material-symbols:info",
                                                                    color=THEME[
                                                                        "primary"
                                                                    ],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                ),
                                                dcc.Graph(
                                                    figure={},
                                                    style={"height": "400px"},
                                                    id="average_image_graph",
                                                ),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                            shadow="sm",
                                            h="100%",
                                        ),
                                    ],
                                    span=8,
                                ),
                                dmc.GridCol(
                                    [
                                        dmc.Paper(
                                            h="100%",
                                            shadow="xs",
                                            p="md",
                                            radius="md",
                                            children=[
                                                dmc.Stack(
                                                    [
                                                        dmc.Text(
                                                            "Visualization Controls",
                                                            size="lg",
                                                            fw=500,
                                                            c=THEME["primary"],
                                                        ),
                                                        dmc.Divider(
                                                            label="Channel Selection",
                                                            labelPosition="center",
                                                        ),
                                                        dmc.Select(
                                                            id="channel_selector_average_image",
                                                            label="Channel",
                                                            w="100%",
                                                            allowDeselect=False,
                                                            leftSection=my_components.get_icon(
                                                                "material-symbols:layers"
                                                            ),
                                                            rightSection=my_components.get_icon(
                                                                "radix-icons:chevron-down"
                                                            ),
                                                        ),
                                                        dmc.Divider(
                                                            label="Display Options",
                                                            labelPosition="center",
                                                            mt="md",
                                                        ),
                                                        dmc.Stack(
                                                            [],
                                                            gap="xs",
                                                        ),
                                                        dmc.Divider(
                                                            label="Color Settings",
                                                            labelPosition="center",
                                                            mt="md",
                                                        ),
                                                        dmc.Select(
                                                            id="color_selector_average_image",
                                                            label="Color Scheme",
                                                            allowDeselect=False,
                                                            data=[
                                                                {
                                                                    "value": "Hot",
                                                                    "label": "Hot",
                                                                },
                                                                {
                                                                    "value": "Blackbody",
                                                                    "label": "Blackbody",
                                                                },
                                                                {
                                                                    "value": "Viridis",
                                                                    "label": "Viridis",
                                                                },
                                                                {
                                                                    "value": "Inferno",
                                                                    "label": "Inferno",
                                                                },
                                                            ],
                                                            value="Blackbody",
                                                            leftSection=my_components.get_icon(
                                                                "material-symbols:palette"
                                                            ),
                                                            rightSection=my_components.get_icon(
                                                                "radix-icons:chevron-down"
                                                            ),
                                                        ),
                                                        dmc.Switch(
                                                            id="color_switch_average_image",
                                                            label="Invert Colors",
                                                            checked=False,
                                                            size="md",
                                                            color=THEME["primary"],
                                                        ),
                                                    ],
                                                    gap="sm",
                                                ),
                                            ],
                                        ),
                                    ],
                                    span=4,
                                ),
                            ],
                        ),
                    ],
                    gap="md",
                ),
            ],
            size="xl",
            p="md",
            style={"backgroundColor": THEME["surface"]},
        ),
    ],
)


@omero_image_average_bead.expanded_callback(
    dash.dependencies.Output("average_image_graph", "figure"),
    [
        dash.dependencies.Input("channel_selector_average_image", "value"),
        dash.dependencies.Input("color_selector_average_image", "value"),
        dash.dependencies.Input("color_switch_average_image", "checked"),
    ],
)
def update_image(channel_index, color, invert, **kwargs):
    try:
        if channel_index is None:
            raise dash.exceptions.PreventUpdate

        raw_context = kwargs["session_state"]["context"]
        ctx = deserialize_partial(
            raw_context,
            "mm_image",
            "mips",
            "key_measurements_df",
            "avg_bead_profiles",
        )
        voxel_size = raw_context["voxel_size"]
        kkm = raw_context["kkm"]
        channel_index = int(channel_index)

        if invert:
            color = f"{color}_r"
        mip = {
            "z": ctx["mips"]["z"][..., channel_index],
            "y": ctx["mips"]["y"][..., channel_index],
            "x": ctx["mips"]["x"][..., channel_index],
        }

        # Extract average profiles: columns are {img}_{ch}_{bead}_{axis}_{type}
        # Average raw profiles across all beads for the selected channel
        profiles = {}
        for axis in ("x", "y", "z"):
            df = ctx["avg_bead_profiles"].get(axis)
            if df is not None and not df.empty:
                raw_cols = [
                    c
                    for c in df.columns
                    if c.endswith(f"_{axis}_raw") and f"_{channel_index}_" in c
                ]
                fitted_cols = [
                    c
                    for c in df.columns
                    if c.endswith(f"_{axis}_fitted_gaussian")
                    and f"_{channel_index}_" in c
                ]

                profile_df = pd.DataFrame()
                if raw_cols:
                    profile_df["raw"] = df[raw_cols].mean(axis=1)
                if fitted_cols:
                    profile_df["fitted"] = df[fitted_cols].mean(axis=1)
                profiles[axis] = profile_df
            else:

                profiles[axis] = pd.DataFrame({"raw": [0], "fitted": [0]})
        # We flip the values of the profiles in the y-axis
        profiles["y"] = profiles["y"].iloc[::-1].reset_index(drop=True)

        table_km = ctx["key_measurements_df"]

        if all(list(voxel_size.values())):
            fwhms = {
                "x": table_km.iloc[channel_index]["average_bead_fwhm_micron_x"],
                "y": table_km.iloc[channel_index]["average_bead_fwhm_micron_y"],
                "z": table_km.iloc[channel_index]["average_bead_fwhm_micron_z"],
            }
        else:
            fwhms = {
                "x": table_km.iloc[channel_index]["average_bead_fwhm_pixel_x"],
                "y": table_km.iloc[channel_index]["average_bead_fwhm_pixel_y"],
                "z": table_km.iloc[channel_index]["average_bead_fwhm_pixel_z"],
            }
        r_sq = {
            "x": table_km.iloc[channel_index]["average_bead_fit_gaussian_r2_x"],
            "y": table_km.iloc[channel_index]["average_bead_fit_gaussian_r2_y"],
            "z": table_km.iloc[channel_index]["average_bead_fit_gaussian_r2_z"],
        }

        axis_lengths = {
            "x": mip["z"].shape[1],
            "y": mip["z"].shape[0],
            "z": mip["x"].shape[1],
        }

        if all(list(voxel_size.values())):
            voxel_size_ratio = voxel_size["z"] / voxel_size["x"]
            physical_unit = "µm"
        else:
            voxel_size_ratio = 1
            physical_unit = "px"

        fig = make_subplots(
            rows=3,
            cols=3,
            column_widths=[
                axis_lengths["x"] * 1.2,
                axis_lengths["x"],
                axis_lengths["z"] * voxel_size_ratio,
            ],
            row_heights=[
                axis_lengths["z"] * voxel_size_ratio,
                axis_lengths["y"],
                axis_lengths["x"] * 1.2,
            ],
            shared_xaxes=True,
            shared_yaxes=True,
            specs=[
                [None, {"type": "heatmap"}, None],
                [{"type": "xy"}, {"type": "heatmap"}, {"type": "heatmap"}],
                [None, {"type": "xy"}, {"type": "xy"}],
            ],
            horizontal_spacing=0.05,
            vertical_spacing=0.05,
        )
        # Add MIP images
        for proj_axis, h_axis, v_axis, row, col, rotate in zip(
            ("x", "y", "z"),
            ("z", "x", "x"),
            ("y", "z", "y"),
            (2, 1, 2),
            (3, 2, 2),
            (False, True, False),
        ):
            fig.add_trace(
                go.Heatmap(z=mip[proj_axis], colorscale=color, showscale=False),
                row=row,
                col=col,
            )
            fig.update_xaxes(
                range=[0, axis_lengths[h_axis]],
                constrain="domain",
                scaleanchor="y2",
                scaleratio=voxel_size_ratio if h_axis == "z" else 1,
                row=row,
                col=col,
            )
            fig.update_yaxes(
                range=[0, axis_lengths[v_axis]],
                constrain="domain",
                scaleanchor="y2",
                scaleratio=voxel_size_ratio if v_axis == "z" else 1,
                row=row,
                col=col,
            )
        # Add profiles
        for axis, row, col, rotate in zip(
            ("x", "y", "z"), (3, 2, 3), (2, 1, 3), (False, True, False)
        ):
            # We want to find the quartiles of the x, y and z axes to plot some pretty tick marks
            quartiles = np.quantile(
                range(axis_lengths[axis]), [0.0, 0.25, 0.5, 0.75, 1.0]
            )

            # We normalize the quartiles to place the 0 in the center of the axis, and we stringify it
            if all(list(voxel_size.values())):
                quartiles_norm = [
                    f"{q:.2f}" for q in (quartiles - quartiles[2]) * voxel_size[axis]
                ]
            else:
                quartiles_norm = quartiles - quartiles[2]

            if rotate:
                plot_x_axis = "y"
                plot_y_axis = "x"
            else:
                plot_x_axis = "x"
                plot_y_axis = "y"

            # Add traces
            fig.add_trace(
                go.Scatter(
                    name=f"{axis.upper()} raw profile",
                    mode="lines",
                    line=dict(color="red"),
                    **{plot_y_axis: profiles[axis]["raw"]},
                ),
                row=row,
                col=col,
            )
            fig.add_trace(
                go.Scatter(
                    name=f"{axis.upper()} fitted profile",
                    mode="lines",
                    line=dict(color="blue", dash="dot"),
                    **{plot_y_axis: profiles[axis]["fitted"]},
                ),
                row=row,
                col=col,
            )
            if rotate:
                fig.add_vline(
                    x=0.5,
                    line_color="gray",
                    line_dash="dash",
                    annotation_text=f"FWHM<br><b>{fwhms[axis]:.3f}{physical_unit}<b>",
                    annotation_align="right",
                    annotation_position="bottom right",
                    row=row,
                    col=col,
                )
                fig.update_xaxes(
                    range=[-0.25, 1.25], constrain="domain", row=row, col=col
                )
                fig.update_yaxes(
                    title_text=f"{axis.upper()}-axis ({physical_unit})",
                    constrain="domain",
                    scaleanchor="y2",
                    scaleratio=voxel_size_ratio if axis == "z" else 1,
                    title_font_size=18,
                    ticktext=quartiles_norm,
                    tickvals=quartiles,
                    row=row,
                    col=col,
                )
            else:
                fig.add_hline(
                    y=0.5,
                    line_color="gray",
                    line_dash="dash",
                    annotation_text=f"FWHM<br><b>{fwhms[axis]:.3f}{physical_unit}<b>",
                    annotation_align="right",
                    annotation_position="top right",
                    row=row,
                    col=col,
                )
                fig.update_xaxes(
                    title_text=f"{axis.upper()}-axis ({physical_unit})",
                    constrain="domain",
                    scaleanchor="y2",
                    scaleratio=voxel_size_ratio if axis == "z" else 1,
                    title_font_size=18,
                    ticktext=quartiles_norm,
                    tickvals=quartiles,
                    row=row,
                    col=col,
                )
                fig.update_yaxes(
                    range=[-0.25, 1.25], constrain="domain", row=row, col=col
                )
            fig.add_annotation(
                text=f"R^2<br><b>{r_sq[axis]:.3f}<b>",
                align="right" if rotate else "left",
                xanchor="left" if rotate else "right",
                ax=20 if rotate else -40,
                ay=-40 if rotate else -20,
                row=row,
                col=col,
                **{
                    plot_x_axis: int(
                        np.quantile(range(profiles[axis]["fitted"].shape[0]), 0.48)
                    ),
                    plot_y_axis: profiles[axis]["fitted"][
                        int(
                            np.quantile(
                                range(profiles[axis]["fitted"].shape[0]), 0.48
                            )
                        )
                    ],
                },
            )

        # Force identical physical domains (prevents doubled Z)
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_layout(
            grid=dict(
                rows=3,
                columns=3,
                pattern="independent",
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.05,
                xanchor="center",
                x=0.5,
            ),
            autosize=True,
            height=750,
            margin=dict(l=40, r=10, t=10, b=60),
        )

        return fig

    except dash.exceptions.PreventUpdate:
        raise
    except Exception as e:
        logger.error(f"Error updating image: {e}", exc_info=True)
        return px.imshow([[0]], title=f"Error: {str(e)}")


@omero_image_average_bead.expanded_callback(
    dash.dependencies.Output("channel_selector_average_image", "data"),
    dash.dependencies.Output("channel_selector_average_image", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_channels_average_image(_, **kwargs):
    ctx = deserialize_partial(kwargs["session_state"]["context"], "mm_image")
    channel_series = ctx["mm_image"].channel_series
    return [
        {"label": c.name, "value": str(i)}
        for i, c in enumerate(channel_series.channels)
    ], "0"


def get_average_bead_profiles(channel_index, mm_dataset):
    profiles = {
        axis: load.load_table_mm_metrics(mm_dataset.output[f"bead_profiles_{axis}"])
        for axis in ("x", "y", "z")
    }
    # TODO: we have chosen to show the gaussian fit but once the airy fit is fixed, we should add the option to
    #  choose between gaussian and airy
    profiles = {
        axis: df.loc[
            :,
            [
                f"{channel_index}_{axis}_raw",
                f"{channel_index}_{axis}_fitted_gaussian",
            ],
        ].rename(
            columns={
                f"{channel_index}_{axis}_raw": "raw",
                f"{channel_index}_{axis}_fitted_gaussian": "fitted",
            }
        )
        for axis, df in profiles.items()
    }
    # We flip the values of the profiles in the y-axis
    profiles["y"] = profiles["y"].iloc[::-1].reset_index(drop=True)

    return profiles
