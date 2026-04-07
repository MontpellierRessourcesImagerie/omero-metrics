# This script is used to geenrate a structure, as defined by the server_structure.yaml file in the same directory
# on the OMERO server. This structure is used to test the omero-metrics package.

import logging
import mimetypes
import os
import random
import time
from datetime import datetime

import numpy as np
import yaml
from microscopemetrics.analyses import (
    field_illumination,
    numpy_to_mm_image,
    psf_beads,
)
from microscopemetrics.strategies.field_illumination import (
    _gen_field_illumination_image,
)
from microscopemetrics.strategies.psf_beads import _gen_psf_beads_image
from microscopemetrics_schema import datamodel as mm_schema
from omero.cli import CLI
from omero.gateway import BlitzGateway
from omero.plugins.group import GroupControl
from omero.plugins.obj import ObjControl
from omero.plugins.sessions import SessionsControl
from omero.plugins.user import UserControl

from omero_metrics.tools import dump

logger = logging.getLogger(__name__)

BIT_DEPTH_TO_DTYPE = {
    8: np.uint8,
    16: np.uint16,
    32: np.float32,
}

DATASET_TO_ANALYSIS = {
    "FieldIlluminationDataset": field_illumination.analyse_field_illumination,
    "PSFBeadsDataset": psf_beads.analyse_psf_beads,
}


def generate_monthly_dates(start_date, nr_dates, month_frequency=1):
    dates = []
    current_date = start_date
    for _ in range(nr_dates):
        month = current_date.month - 1 + 1
        year = current_date.year + month // 12
        month = month % 12 + month_frequency
        day = min(
            current_date.day,
            [
                31,
                (
                    29
                    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
                    else 28
                ),
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        date1 = datetime(year, month, day)
        dates.append(date1.strftime("%Y-%m-%d"))
        current_date = date1
    return dates


def field_illumination_generator(args, microscope_name):
    datasets = []
    dates = generate_monthly_dates(
        args["start_date"], args["nr_datasets"], args["month_frequency"]
    )

    for dataset_id in range(args["nr_datasets"]):
        print(f"Generating dataset {dataset_id} for {args['name_dataset']}")
        datasets.append(
            mm_schema.FieldIlluminationDataset(
                name=f"{args['name_dataset']}_{dates[dataset_id]}",
                description=args["description_dataset"],
                acquisition_datetime=dates[dataset_id],
                microscope=mm_schema.Microscope(name=microscope_name),
                input_parameters=mm_schema.FieldIlluminationInputParameters(),
                input_data=mm_schema.FieldIlluminationInputData(
                    field_illumination_images=[
                        numpy_to_mm_image(
                            array=_gen_field_illumination_image(
                                y_shape=random.randint(
                                    args["y_image_shape"]["min"],
                                    args["y_image_shape"]["max"],
                                ),
                                x_shape=random.randint(
                                    args["x_image_shape"]["min"],
                                    args["x_image_shape"]["max"],
                                ),
                                c_shape=len(channel_names),
                                y_center_rel_offset=[
                                    random.uniform(
                                        args["center_y_relative"]["min"],
                                        args["center_y_relative"]["max"],
                                    )
                                    for _ in range(len(channel_names))
                                ],
                                x_center_rel_offset=[
                                    random.uniform(
                                        args["center_x_relative"]["min"],
                                        args["center_x_relative"]["max"],
                                    )
                                    for _ in range(len(channel_names))
                                ],
                                dispersion=[
                                    random.uniform(
                                        args["dispersion"]["min"],
                                        args["dispersion"]["max"],
                                    )
                                    for _ in range(len(channel_names))
                                ],
                                target_min_intensity=[
                                    random.uniform(
                                        args["target_min_intensity"]["min"],
                                        args["target_min_intensity"]["max"],
                                    )
                                    for _ in range(len(channel_names))
                                ],
                                target_max_intensity=[
                                    random.uniform(
                                        args["target_max_intensity"]["min"],
                                        args["target_max_intensity"]["max"],
                                    )
                                    for _ in range(len(channel_names))
                                ],
                                do_noise=True,
                                signal=[
                                    random.randint(
                                        args["signal"]["min"],
                                        args["signal"]["max"],
                                    )
                                    for _ in range(len(channel_names))
                                ],
                                dtype=BIT_DEPTH_TO_DTYPE[args["bit_depth"]],
                            ),
                            name=f"{args['name_dataset']}_{'_'.join(channel_names)}_{dates[dataset_id]}",
                            description=f"An image taken on the {microscope_name} microscope on the {dates[dataset_id]} for QC",
                            channel_names=args["channel_names"][image_id],
                            acquisition_datetime=datetime.strptime(
                                dates[dataset_id], "%Y-%m-%d"
                            ),
                        )
                        for image_id, channel_names in enumerate(
                            args["channel_names"]
                        )
                    ]
                ),
            )
        )

    return datasets


def psf_beads_generator(args, microscope_name):
    datasets = []
    dates = generate_monthly_dates(
        args["start_date"], args["nr_datasets"], args["month_frequency"]
    )

    for dataset_id in range(args["nr_datasets"]):
        print(f"Generating dataset {dataset_id} for {args['name_dataset']}")
        datasets.append(
            mm_schema.PSFBeadsDataset(
                name=f"{args['name_dataset']}_{dates[dataset_id]}",
                description=args["description_dataset"],
                acquisition_datetime=dates[dataset_id],
                microscope=mm_schema.Microscope(name=microscope_name),
                input_parameters=mm_schema.PSFBeadsInputParameters(),
                input_data=mm_schema.PSFBeadsInputData(
                    psf_beads_images=[
                        numpy_to_mm_image(
                            array=_gen_psf_beads_image(
                                z_image_shape=random.randint(
                                    args["z_image_shape"]["min"],
                                    args["z_image_shape"]["max"],
                                ),
                                y_image_shape=random.randint(
                                    args["y_image_shape"]["min"],
                                    args["y_image_shape"]["max"],
                                ),
                                x_image_shape=random.randint(
                                    args["x_image_shape"]["min"],
                                    args["x_image_shape"]["max"],
                                ),
                                c_image_shape=len(channel_names),
                                nr_valid_beads=random.randint(
                                    args["nr_valid_beads"]["min"],
                                    args["nr_valid_beads"]["max"],
                                ),
                                nr_edge_beads=random.randint(
                                    args["nr_edge_beads"]["min"],
                                    args["nr_edge_beads"]["max"],
                                ),
                                nr_out_of_focus_beads=random.randint(
                                    args["nr_out_of_focus_beads"]["min"],
                                    args["nr_out_of_focus_beads"]["max"],
                                ),
                                nr_clustering_beads=random.randint(
                                    args["nr_clustering_beads"]["min"],
                                    args["nr_clustering_beads"]["max"],
                                ),
                                min_distance_z_px=args["min_distance_z"],
                                min_distance_y_px=args["min_distance_y"],
                                min_distance_x_px=args["min_distance_x"],
                                sigma_z=random.uniform(
                                    args["sigma_z"]["min"],
                                    args["sigma_z"]["max"],
                                ),
                                sigma_y=random.uniform(
                                    args["sigma_y"]["min"],
                                    args["sigma_y"]["max"],
                                ),
                                sigma_x=random.uniform(
                                    args["sigma_x"]["min"],
                                    args["sigma_x"]["max"],
                                ),
                                background=random.uniform(
                                    args["background"]["min"],
                                    args["background"]["max"],
                                ),
                                signal=random.uniform(
                                    args["signal"]["min"],
                                    args["signal"]["max"],
                                ),
                                do_noise=True,
                                dtype=BIT_DEPTH_TO_DTYPE[args["bit_depth"]],
                            )[0],
                            name=f"{args['name_dataset']}_{dates[dataset_id]}",
                            description=f"An image taken on the {microscope_name} microscope on the {dates[dataset_id]} for QC",
                            channel_names=args["channel_names"][image_id],
                            acquisition_datetime=datetime.strptime(
                                dates[dataset_id], "%Y-%m-%d"
                            ),
                        )
                        for image_id, channel_names in enumerate(
                            args["channel_names"]
                        )
                    ]
                ),
            )
        )

    return datasets


GENERATOR_MAPPER = {
    "FieldIlluminationDataset": field_illumination_generator,
    "PSFBeadsDataset": psf_beads_generator,
}


def _attach_config(conn, project, file_path):
    """Attach a config YAML file to a project with the correct schema namespace."""
    mimetype, _ = mimetypes.guess_type(file_path)
    # Read the config to get the InputParameters type name, then use the
    # canonical class_class_curie from the schema instead of constructing
    # the namespace from the file path (which is fragile).
    with open(file_path) as f:
        config = yaml.safe_load(f)
    input_params_type = config["input_parameters"]["type"]
    input_params_cls = getattr(mm_schema, input_params_type)
    file_ann = conn.createFileAnnfromLocalFile(
        file_path,
        mimetype=mimetype,
        desc="Configuration file",
        ns=input_params_cls.class_class_curie,
    )
    project.linkAnnotation(file_ann)


def generate_users_groups(conn, users: dict, groups: dict):
    session_uuid = conn.getSession().getUuid().val
    host = conn.host
    port = conn.port
    cli = CLI()
    cli.register("sessions", SessionsControl, "test")
    cli.register("user", UserControl, "test")
    cli.register("group", GroupControl, "test")
    cli.register("obj", ObjControl, "test")

    for group in groups.values():
        cli.invoke(
            [
                "group",
                "add",
                "--type",
                "read-only",
                "-k",
                session_uuid,
                "-s",
                host,
                "-p",
                str(port),
                group["name"],
            ]
        )
        group_id = conn.c.sf.getAdminService().lookupGroup(group["name"]).id.val

        cli.invoke(
            [
                "obj",
                "update",
                f"ExperimenterGroup:{group_id}",
                f"description={group['description']}",
                "-k",
                session_uuid,
                "-s",
                host,
                "-p",
                str(port),
            ]
        )

    for user_name, user in users.items():
        cli.invoke(
            [
                "user",
                "add",
                "-P",
                user["password"],
                "-k",
                session_uuid,
                "-s",
                host,
                "-p",
                str(port),
                user_name,
                user["first_name"],
                user["last_name"],
                "--group-name",
                user["default_group"],
            ]
        )

    for group in groups.values():
        for owner in group["owners"]:
            cli.invoke(
                [
                    "group",
                    "adduser",
                    "--user-name",
                    owner,
                    "--name",
                    group["name"],
                    "--as-owner",
                    "-k",
                    session_uuid,
                    "-s",
                    host,
                    "-p",
                    str(port),
                ]
            )

        for member in group["members"]:
            cli.invoke(
                [
                    "group",
                    "adduser",
                    "--user-name",
                    member,
                    "--name",
                    group["name"],
                    "-k",
                    session_uuid,
                    "-s",
                    host,
                    "-p",
                    str(port),
                ]
            )


def annotate_microscopes(conn, microscopes: dict):
    for microscope in microscopes.values():
        try:
            microscope = mm_schema.Microscope(
                name=microscope["name"],
                description=microscope["description"],
                microscope_type=microscope["type"],
                manufacturer=microscope["manufacturer"],
                model=microscope["model"],
                serial_number=microscope["serial_number"],
            )
            omero_group = conn.getObject(
                "ExperimenterGroup", attributes={"name": microscope["name"]}
            )

            dump.dump_microscope(conn, microscope, omero_group)
        except KeyError:
            logger.info(f"Could not annotate microscope {microscope['name']}")
            continue


if __name__ == "__main__":
    with open("server_structure.yaml", "r") as f:
        server_structure = yaml.load(f, Loader=yaml.SafeLoader)

    # host = input("OMERO host: ")
    # port = int(input("OMERO port: ") or 4064)
    # username = input("OMERO username: ")
    # password = input("OMERO password: ")
    conn = BlitzGateway("root", "omero", host="localhost", port=6064, secure=True)

    try:
        # conn = BlitzGateway(username, password, host=host, port=port, secure=True)
        conn.connect()
        conn.keepAlive()

        generate_users_groups(
            conn, server_structure["users"], server_structure["microscopes"]
        )

        # annotate_microscopes(conn, server_structure["microscopes"])

        for microscope_name, microscope_projects in server_structure[
            "projects"
        ].items():
            for project in microscope_projects.values():
                mm_project = mm_schema.HarmonizedMetricsDatasetCollection(
                    name=project["name_project"],
                    description=project["description_project"],
                    dataset_collection=GENERATOR_MAPPER[project["dataset_class"]](
                        project, microscope_name
                    ),
                    dataset_class=project["dataset_class"],
                )
                time.sleep(60)

                if not conn.keepAlive():
                    conn.connect()
                temp_conn = conn.suConn(
                    project["owner"], microscope_name, ttl=300000
                )

                # We first have to dump the input images so they are annotated with the omero references
                omero_project = dump.dump_project(
                    temp_conn,
                    mm_project,
                    dump_input_images=True,  # We anyway want to dump test input images
                    dump_analysis=False,
                    dump_as_project_file_annotation=False,
                    dump_as_dataset_file_annotation=False,
                )
                dir_attachments = os.path.join(
                    os.path.dirname(__file__),
                    "config_files",
                    project["attachments_dir"],
                )
                attachment_files = [
                    os.path.join(dir_path, f)
                    for (dir_path, dir_names, filenames) in os.walk(dir_attachments)
                    for f in filenames
                ]
                for file_path in attachment_files:
                    _attach_config(temp_conn, omero_project, file_path)

                if project["process"]:
                    for dataset in mm_project.dataset_collection:
                        DATASET_TO_ANALYSIS[project["dataset_class"]](dataset)

                    omero_project = dump.dump_project(
                        temp_conn,
                        mm_project,
                        dump_input_images=False,  # We anyway want to dump test input images
                        dump_analysis=True,
                        dump_as_project_file_annotation=True,
                        dump_as_dataset_file_annotation=True,
                    )
                temp_conn.close()

    finally:
        conn.close()
        temp_conn.close()
