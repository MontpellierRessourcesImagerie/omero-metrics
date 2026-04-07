import logging

import dash
import dash_mantine_components as dmc
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc, html
from django_plotly_dash import DjangoDash
from plotly.subplots import make_subplots

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics.styles import MANTINE_THEME, PLOTLY_LAYOUT, THEME
from omero_metrics.tools import load
from omero_metrics.tools.serializers import deserialize

logger = logging.getLogger(__name__)
dashboard_name = "omero_image_psf_beads"

omero_image_psf_beads = DjangoDash(name=dashboard_name, serve_locally=True)

omero_image_psf_beads.layout = dmc.MantineProvider(
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
                                                            "Bead Distribution Map",
                                                            size="lg",
                                                            fw=500,
                                                            c=THEME["primary"],
                                                        ),
                                                        dmc.Tooltip(
                                                            label="Click on a bead in the image to view its MIP",
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
                                                    id="psf_image_graph",
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
                                                            id="channel_selector_psf_image",
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
                                                        dmc.SegmentedControl(
                                                            id="beads_info_segmented",
                                                            value="beads_info",
                                                            data=[
                                                                {
                                                                    "value": "beads_info",
                                                                    "label": "Show Beads",
                                                                },
                                                                {
                                                                    "value": "None",
                                                                    "label": "Hide Beads",
                                                                },
                                                            ],
                                                            fullWidth=True,
                                                            color=THEME["primary"],
                                                            # w='auto'
                                                        ),
                                                        dmc.Stack(
                                                            [
                                                                dmc.Checkbox(
                                                                    id="contour_checkbox_psf_image",
                                                                    label="Enable Contour View",
                                                                    checked=False,
                                                                    color=THEME[
                                                                        "primary"
                                                                    ],
                                                                ),
                                                                dmc.Checkbox(
                                                                    id="roi_checkbox_psf_image",
                                                                    label="Show ROI Boundaries",
                                                                    checked=True,
                                                                    color=THEME[
                                                                        "primary"
                                                                    ],
                                                                ),
                                                            ],
                                                            gap="xs",
                                                        ),
                                                        dmc.Divider(
                                                            label="Color Settings",
                                                            labelPosition="center",
                                                            mt="md",
                                                        ),
                                                        dmc.Select(
                                                            id="color_selector_psf_image",
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
                                                            id="color_switch_psf_image",
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
                        dmc.Paper(
                            id="paper_mip",
                            shadow="sm",
                            p="md",
                            radius="md",
                            children=[
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            id="title_mip",
                                            children="Maximum Intensity Projection",
                                            size="lg",
                                            fw=500,
                                            c=THEME["primary"],
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                                # TODO: change here the beads MIP
                                dcc.Graph(
                                    id="mip_image",
                                    figure={},
                                    style={"height": "800px"},
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


@omero_image_psf_beads.expanded_callback(
    dash.dependencies.Output("psf_image_graph", "figure"),
    [
        dash.dependencies.Input("channel_selector_psf_image", "value"),
        dash.dependencies.Input("color_selector_psf_image", "value"),
        dash.dependencies.Input("color_switch_psf_image", "checked"),
        dash.dependencies.Input("contour_checkbox_psf_image", "checked"),
        dash.dependencies.Input("roi_checkbox_psf_image", "checked"),
        dash.dependencies.Input("beads_info_segmented", "value"),
    ],
)
def update_image(channel_index, color, invert, contour, roi, beads_info, **kwargs):
    try:
        context = deserialize(kwargs["session_state"]["context"])
        mm_dataset = context["mm_dataset"]
        mm_image = context["mm_image"]
        image_id = mm_image.data_reference.omero_object_id
        channel_index = int(channel_index)
        # TODO: we have to decide, at the scheme level, on weather we set the min_distance in pixels or in FWHM
        min_distance_px = int(
            mm_dataset.input_parameters.min_lateral_distance_factor * 2
        )
        half_min_distance_px = min_distance_px // 2
        bead_properties_df = load.load_table_mm_metrics(
            mm_dataset.output["bead_properties"]
        )
        beads_location_df = bead_properties_df.loc[
            (bead_properties_df["image_id"] == image_id)
            & (bead_properties_df["channel_nr"] == channel_index),
            :,
        ].copy()

        scatter, roi_rect = beads_scatter_plot(
            beads_location_df, half_min_distance_px
        )

        if invert:
            color = f"{color}_r"
        mip_z = context["mip_z"][..., channel_index]

        fig = px.imshow(
            mip_z,
            zmin=mip_z.min(),
            zmax=mip_z.max(),
            color_continuous_scale=color,
        )

        fig.add_trace(scatter)

        if roi:
            fig.update_layout(shapes=roi_rect)
        else:
            fig.update_layout(shapes=None)

        if contour:
            fig.plotly_restyle({"type": "contour"}, 0)
            fig.update_yaxes(autorange="reversed")

        if beads_info == "beads_info":
            fig.update_traces(visible=True, selector=dict(name="Beads Locations"))
        else:
            fig.update_traces(visible=False, selector=dict(name="Beads Locations"))

        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            xaxis1=dict(showgrid=False, zeroline=False, visible=False),
            yaxis1=dict(showgrid=False, zeroline=False, visible=False),
        )

        return fig

    except Exception as e:
        logger.error(f"Error updating image: {e}", exc_info=True)
        return px.imshow([[0]], title="Error loading image")


@omero_image_psf_beads.expanded_callback(
    dash.dependencies.Output("channel_selector_psf_image", "data"),
    dash.dependencies.Output("channel_selector_psf_image", "value"),
    [dash.dependencies.Input("blank-input", "children")],
)
def update_channels_psf_image(_, **kwargs):
    context = deserialize(kwargs["session_state"]["context"])
    channel_series = context["mm_image"].channel_series
    return [
        {"label": c.name, "value": str(i)}
        for i, c in enumerate(channel_series.channels)
    ], "0"


@omero_image_psf_beads.expanded_callback(
    dash.dependencies.Output("mip_image", "figure"),
    dash.dependencies.Output("title_mip", "children"),
    [
        dash.dependencies.Input("psf_image_graph", "clickData"),
        dash.dependencies.Input("channel_selector_psf_image", "value"),
        dash.dependencies.Input("color_selector_psf_image", "value"),
        dash.dependencies.Input("color_switch_psf_image", "checked"),
    ],
    prevent_initial_call=True,
)
def callback_mip(points, channel_index, color, invert, **kwargs):
    point = points["points"][0]  # FIXME: point is None at initial call
    if point["curveNumber"] != 1:
        return dash.no_update

    context = deserialize(kwargs["session_state"]["context"])
    bead_index = point["pointNumber"]
    mm_image = context["mm_image"]
    image_id = mm_image.data_reference.omero_object_id
    channel_index = int(channel_index)
    beads_properties_df = context["beads_properties"]
    bead_df = beads_properties_df.loc[
        (beads_properties_df["image_id"] == image_id)
        & (beads_properties_df["channel_nr"] == channel_index)
        & (beads_properties_df["bead_id"] == bead_index),
        :,
    ]
    beads_array = context["beads_array"]

    bead_array = beads_array[bead_index, :, :, :, channel_index]

    # Crop Z to central 50% to reduce whitespace (issue #23)
    nz = bead_array.shape[0]
    z_start = nz // 4
    z_end = 3 * nz // 4
    bead_array_cropped = bead_array[z_start:z_end, :, :]

    mips = {
        "x": np.flipud(np.transpose(np.max(bead_array_cropped, axis=2))),
        "y": np.max(bead_array_cropped, axis=1),
        "z": np.flipud(np.max(bead_array, axis=0)),
    }
    mips = {a: np.sqrt(mip) for a, mip in mips.items()}

    mm_dataset = context["mm_dataset"]
    profiles = get_bead_profiles(
        bead_index=bead_index,
        channel_index=channel_index,
        image_id=image_id,
        mm_dataset=mm_dataset,
    )
    voxel_size = {
        "x": mm_image.voxel_size_x_micron,
        "y": mm_image.voxel_size_y_micron,
        "z": mm_image.voxel_size_z_micron,
    }
    if all(list(voxel_size.values())):
        fwhms = {
            "x": bead_df["fwhm_micron_x"].values[0],
            "y": bead_df["fwhm_micron_y"].values[0],
            "z": bead_df["fwhm_micron_z"].values[0],
        }
    else:
        fwhms = {
            "x": bead_df["fwhm_pixel_x"].values[0],
            "y": bead_df["fwhm_pixel_y"].values[0],
            "z": bead_df["fwhm_pixel_z"].values[0],
        }
    r_sq = {
        "x": bead_df["fit_gaussian_r2_x"].values[0],
        "y": bead_df["fit_gaussian_r2_y"].values[0],
        "z": bead_df["fit_gaussian_r2_z"].values[0],
    }

    fig_mip_go = fig_bead(
        mips=mips,
        color=color,
        invert=invert,
        profiles=profiles,
        fwhms=fwhms,
        r_sq=r_sq,
        voxel_size=voxel_size,
    )
    channel_name = mm_image.channel_series.channels[
        channel_index
    ].name  # TODO: rename channel_names to channels

    title = f"Channel {channel_name}: Bead number {bead_index}"
    return (
        fig_mip_go,
        title,
    )


def fig_bead(
    mips,
    color,
    invert,
    profiles,
    fwhms,
    r_sq,
    voxel_size={"x": None, "y": None, "z": None},
):
    axis_lengths = {
        "x": mips["z"].shape[1],
        "y": mips["z"].shape[0],
        "z": mips["x"].shape[1],
    }
    if all(list(voxel_size.values())):
        voxel_size_ratio = voxel_size["z"] / voxel_size["x"]
        physical_unit = "µm"
    else:
        voxel_size_ratio = 1
        physical_unit = "px"
    if invert:
        color = f"{color}_r"

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
        horizontal_spacing=0.02,
        vertical_spacing=0.02,
    )

    # Add MIP image
    for proj_axis, h_axis, v_axis, row, col, rotate in zip(
        ("x", "y", "z"),
        ("z", "x", "x"),
        ("y", "z", "y"),
        (2, 1, 2),
        (3, 2, 2),
        (False, True, False),
    ):
        fig.add_trace(
            go.Heatmap(z=mips[proj_axis], colorscale=color, showscale=False),
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
                    int(np.quantile(range(profiles[axis]["fitted"].shape[0]), 0.48))
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
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        autosize=True,
        height=700,
        margin=dict(l=10, r=10, t=10, b=10),
    )

    return fig


def get_bead_profiles(bead_index, channel_index, image_id, mm_dataset):
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
                f"{image_id}_{channel_index}_{bead_index}_{axis}_raw",
                f"{image_id}_{channel_index}_{bead_index}_{axis}_fitted_gaussian",
            ],
        ].rename(
            columns={
                f"{image_id}_{channel_index}_{bead_index}_{axis}_raw": "raw",
                f"{image_id}_{channel_index}_{bead_index}_{axis}_fitted_gaussian": "fitted",
            }
        )
        for axis, df in profiles.items()
    }
    # We flip the values of the profiles in the y-axis
    profiles["y"] = profiles["y"].iloc[::-1].reset_index(drop=True)

    return profiles


def beads_scatter_plot(df, half_min_distance_px):
    df["color"] = np.where(df["considered_valid"] == "True", "green", "red")

    beads_location_plot = go.Scatter(
        y=df["center_y"],
        x=df["center_x"],
        mode="markers",
        name="Beads Locations",
        marker=dict(
            size=0.001,
            opacity=0.01,
            color=df["color"],
        ),
        text=df["channel_nr"],
        customdata=np.stack(
            (
                df["bead_id"],
                df["considered_valid"],
                df["considered_self_proximity"],
                df["considered_lateral_edge"],
                df["considered_intensity_outlier"],
                df["considered_axial_edge"],
            ),
            axis=-1,
        ),
        # TODO: We have to make this more robust (f-sting?)
        hovertemplate=(
            "<b>Bead Number:</b>  %{customdata[0]} <br>"
            "<b>Channel Number:</b>  %{text} <br>"
            "<b>Considered valid:</b>  %{customdata[1]}<br>"
            "<b>Considered self proximity:</b>  %{customdata[2]}<br>"
            "<b>Considered lateral edge:</b>  %{customdata[3]}<br>"
            "<b>Considered intensity outlier:</b>  %{customdata[4]}<br>"
            "<b>Considered Axial Edge:</b> %{customdata[5]} <br><extra></extra>"
        ),
    )

    bead_frames = [
        dict(
            type="rect",
            x0=row.center_x - half_min_distance_px,
            y0=row.center_y - half_min_distance_px,
            x1=row.center_x + half_min_distance_px,
            y1=row.center_y + half_min_distance_px,
            xref="x",
            yref="y",
            line=dict(
                color=row["color"],
                width=3,
            ),
        )
        for _, row in df.iterrows()
    ]

    return beads_location_plot, bead_frames
