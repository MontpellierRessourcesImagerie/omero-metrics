import dash
import dash_mantine_components as dmc
from dash import html
from django_plotly_dash import DjangoDash

import omero_metrics.dash_apps.dash_utils.omero_metrics_components as my_components
from omero_metrics.styles import CARD_STYLE_ELEVATED

# Initialize the Dash app
dashboard_name = "omero_multiple_projects"
omero_multiple_projects = DjangoDash(
    dashboard_name,
    serve_locally=True,
)

omero_multiple_projects.layout = dmc.MantineProvider(
    [
        my_components.header_component(
            title="Omero Metrics Projects",
            description="This is a view for multiple projects",
            tag="Feedback",
            load_buttons=False,
        ),
        dmc.Container(
            children=[
                html.Div(id="input_void"),
                html.Div(id="chart_lines"),
            ]
        ),
    ]
)


@omero_multiple_projects.expanded_callback(
    dash.dependencies.Output("chart_lines", "children"),
    [dash.dependencies.Input("input_void", "value")],
)
def kkm_tables_projects(*args, **kwargs):
    if kwargs["session_state"]["context"]:
        data = kwargs["session_state"]["context"]
        print(data)
        print(kwargs["session_state"]["context"])
        div_data = []
        for project_id in data:
            if data[project_id]:
                title, line = my_components.get_title_line_chart(
                    project_id, data[project_id]
                )
                div_data.append(dmc.Stack([dmc.Title(title), line]))
            else:
                div_data.append(
                    dmc.Stack(
                        [
                            dmc.Text(f"Project ID: {project_id}"),
                            dmc.Text(
                                children=f"No data available for project ID: {project_id}, please analyse it first.",
                                c="dimmed",
                                fw="bold",
                            ),
                        ]
                    )
                )
        return dmc.Paper(
            style={**CARD_STYLE_ELEVATED, "marginTop": "12px"}, children=div_data
        )
    else:
        return [
            dmc.Text(
                children="No data available. Please analyse at least one project",
                c="dimmed",
                fw="bold",
            )
        ]
