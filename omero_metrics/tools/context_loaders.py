from dataclasses import asdict
from datetime import datetime

import numpy as np
import pandas as pd

from omero_metrics.tools import load
from omero_metrics.tools.data_type import KKM_MAPPINGS
from omero_metrics.tools.serializers import serialize


def concatenate_images(images: list):
    list_images = []
    list_channels = []
    for mm_image in images:
        image = mm_image.array_data
        result = [image[:, :, :, :, i] for i in range(image.shape[4])]
        channels = [c.name for c in mm_image.channel_series.channels]
        list_images.extend(result)
        list_channels.extend(channels)
    return list_images, list_channels


def _precompute_intensity_profiles(mm_dataset, image_index=None):
    """Pre-compute intensity profile DataFrames from mm_dataset output.

    If image_index is given, return the single image's DataFrame.
    Otherwise, return the concatenated DataFrame for all images.
    """
    ip = mm_dataset.output["intensity_profiles"]
    if image_index is not None and isinstance(ip, list):
        return load.load_table_mm_metrics(ip[image_index])
    return load.load_table_mm_metrics(ip)


def _precompute_key_measurements(mm_dataset):
    """Pre-compute key measurements DataFrame from mm_dataset output."""
    return load.get_km_mm_metrics_dataset(mm_dataset)


def _extract_dataset_meta(mm_dataset):
    """Extract lightweight metadata from mm_dataset for delete/download."""
    return {
        "dataset_id": int(mm_dataset.data_reference.omero_object_id),
        "dataset_name": mm_dataset.name,
        "dataset_class": mm_dataset.class_name,
    }


## Image context loaders
def FieldIlluminationDataset_input_data_Image(im):
    im.mm_image = load.load_image(im.omero_image, load_array=True)
    mm_dataset = im.dataset_manager.mm_dataset
    image_id = im.mm_image.data_reference.omero_object_id

    # Pre-compute ROIs (expensive, but static — no need to redo per callback)
    rois = load.get_rois_mm_dataset(mm_dataset)
    image_rois = rois.get(
        image_id, {"roi": {"Line": [], "Rectangle": [], "Point": []}}
    )

    # Pre-compute intensity profiles for this image
    image_ip = _precompute_intensity_profiles(mm_dataset, image_index=im.image_index)

    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "rois_lines": image_rois["roi"]["Line"],
        "rois_rectangles": image_rois["roi"]["Rectangle"],
        "rois_points": image_rois["roi"]["Point"],
        "intensity_profiles": image_ip,
    }
    im.context = serialize(context)


def PSFBeadsDataset_input_data_Image(im):
    im.mm_image = load.load_image(im.omero_image, load_array=True)
    mm_dataset = im.dataset_manager.mm_dataset
    bead_properties = load.load_table_mm_metrics(
        mm_dataset.output["bead_properties"]
    )
    image_bead_properties = bead_properties.loc[
        bead_properties["image_id"] == im.omero_image.getId()
    ]
    # TODO: This is a hack. We just reproduce what microscope-metrics does to extract the min-distance
    min_distance_px = int(
        mm_dataset.input_parameters.min_lateral_distance_factor * 2
    )
    half_min_distance_px = min_distance_px // 2
    beads_array = np.zeros(
        (
            image_bead_properties.bead_id.max() + 1,
            im.mm_image.shape_z,
            min_distance_px + 1,
            min_distance_px + 1,
            im.mm_image.shape_c,
        )
    )
    for _, row in image_bead_properties.iterrows():
        y_left = int(row.center_y) - half_min_distance_px
        y_right = int(row.center_y) + half_min_distance_px + 1
        x_left = int(row.center_x) - half_min_distance_px
        x_right = int(row.center_x) + half_min_distance_px + 1
        bead_array = im.mm_image.array_data[
            0,  # time 0
            :,  # z-dimension
            max(0, y_left) : min(
                im.mm_image.array_data.shape[2], y_right
            ),  # y-dimension
            max(0, x_left) : min(
                im.mm_image.array_data.shape[3], x_right
            ),  # x-dimension
            :,  # channel
        ]
        if bead_array.shape == beads_array[row.bead_id].shape:
            beads_array[row.bead_id] = bead_array
        else:
            y_padding = (
                abs(y_left) if y_left < 0 else 0,
                (
                    abs(y_right - im.mm_image.array_data.shape[2])
                    if y_right > im.mm_image.array_data.shape[2]
                    else 0
                ),
            )
            x_padding = (
                abs(x_left) if x_left < 0 else 0,
                (
                    abs(x_right - im.mm_image.array_data.shape[3])
                    if x_right > im.mm_image.array_data.shape[3]
                    else 0
                ),
            )
            beads_array[row.bead_id] = np.pad(
                bead_array, ((0, 0), y_padding, x_padding, (0, 0))
            )

    mip_z = np.max(im.mm_image.array_data[0, ...], axis=0)
    im.mm_image.array_data = None

    # Pre-compute bead profiles for each axis
    bead_profiles = {}
    for axis in ("x", "y", "z"):
        try:
            table = mm_dataset.output[f"bead_profiles_{axis}"]
            if table:
                bead_profiles[axis] = load.load_table_mm_metrics(table)
        except (KeyError, AttributeError):
            pass

    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mm_dataset": mm_dataset,
        "mip_z": mip_z,
        "beads_properties": image_bead_properties,
        "beads_array": beads_array,
        "bead_profiles": bead_profiles,
    }
    im.context = serialize(context)


def PSFBeadsDataset_output_AveragePSF(im):
    im.mm_image = load.load_image(im.omero_image, load_array=True)

    mips = {
        "x": np.flipud(
            np.transpose(np.max(im.mm_image.array_data[0, ...], axis=2), (1, 0, 2))
        ),
        "y": np.max(im.mm_image.array_data[0, ...], axis=1),
        "z": np.flipud(np.max(im.mm_image.array_data[0, ...], axis=0)),
    }
    mips = {a: np.sqrt(mip) for a, mip in mips.items()}

    im.mm_image.array_data = None
    mm_dataset = im.dataset_manager.mm_dataset

    # Pre-compute key measurements and average bead profiles
    key_measurements_df = _precompute_key_measurements(mm_dataset)

    avg_bead_profiles = {}
    for axis in ("x", "y", "z"):
        try:
            table = mm_dataset.output[f"bead_profiles_{axis}"]
            if table:
                avg_bead_profiles[axis] = load.load_table_mm_metrics(table)
        except (KeyError, AttributeError):
            pass

    context = {
        "image_index": im.image_index,
        "mm_image": im.mm_image,
        "mips": mips,
        "kkm": im.dataset_manager.kkm,
        "key_measurements_df": key_measurements_df,
        "avg_bead_profiles": avg_bead_profiles,
        "voxel_size": {
            "x": im.mm_image.voxel_size_x_micron,
            "y": im.mm_image.voxel_size_y_micron,
            "z": im.mm_image.voxel_size_z_micron,
        },
    }
    im.context = serialize(context)


## Dataset context loaders
def FieldIlluminationDataset(dm):
    dm.load_data(load_images=True, force_reload=True)
    list_images, list_channels = concatenate_images(
        dm.mm_dataset.input_data.field_illumination_images
    )

    # Pre-compute tables once (avoid re-computing in every callback)
    key_measurements_df = _precompute_key_measurements(dm.mm_dataset)
    intensity_profiles = _precompute_intensity_profiles(dm.mm_dataset)

    context = {
        **_extract_dataset_meta(dm.mm_dataset),
        "mm_dataset": dm.mm_dataset,
        "image_data": list_images,
        "channel_names": list_channels,
        "kkm": dm.kkm,
        "key_measurements_df": key_measurements_df,
        "intensity_profiles": intensity_profiles,
    }
    dm.context = serialize(context)


def PSFBeadsDataset(dm):
    dm.load_data(load_images=False, force_reload=True)

    # Pre-compute key measurements once
    key_measurements_df = _precompute_key_measurements(dm.mm_dataset)

    context = {
        **_extract_dataset_meta(dm.mm_dataset),
        "mm_dataset": dm.mm_dataset,
        "kkm": dm.kkm,
        "key_measurements_df": key_measurements_df,
    }
    dm.context = serialize(context)


def EmptyMetricsDatasetCollection(pm):
    pm.load_data()
    pm.load_input_config()
    pm.load_thresholds()
    context = {
        "project_id": int(pm.omero_project.getId()),
        "unprocessed_datasets": list(pm.unprocessed_datasets),
        "input_parameters": pm.input_parameters,
        "sample": pm.sample,
        "thresholds": pm.thresholds,
    }
    pm.context = serialize(context)


def HarmonizedMetricsDatasetCollection(pm):
    pm.load_data()
    pm.load_input_config()
    pm.load_thresholds()
    dates = []
    min_date = None
    max_date = None
    channels = set()
    kkm_list = KKM_MAPPINGS.get(pm.mm_dataset_collection.dataset_class)
    collection_key_measurements_by_kkm = {kkm: [] for kkm in kkm_list}
    collection_key_measurements_by_dataset_id = {}
    for dataset in pm.mm_dataset_collection.dataset_collection:
        if not dataset.processed:
            raise ValueError(f"Dataset {dataset.name} is not processed")
        if dataset.output is None:
            continue
        key_measurements_by_kkm = {
            kkm: [
                {
                    "date": dataset.acquisition_datetime.split("T")[0],
                    "dataset_id": int(dataset.data_reference.omero_object_id),
                    **{
                        km.channel_name: km[kkm]
                        for km in dataset.output.key_measurements
                    },
                }
            ]
            for kkm in kkm_list
        }
        [
            collection_key_measurements_by_kkm[kkm].extend(
                key_measurements_by_kkm[kkm]
            )
            for kkm in kkm_list
        ]
        collection_key_measurements_by_dataset_id[
            int(dataset.data_reference.omero_object_id)
        ] = {
            "caption": f"{dataset.name} acquired on {dataset.acquisition_datetime}",
            "head": [kkm.replace("_", " ").title() for kkm in kkm_list],
            "body": [
                [km[kkm] for kkm in kkm_list]
                for km in dataset.output.key_measurements
            ],
        }
        channels = channels | {
            km.channel_name for km in dataset.output.key_measurements
        }
        dates.append(dataset.acquisition_datetime)
        min_date = (
            min(min_date, dataset.acquisition_datetime)
            if min_date
            else dataset.acquisition_datetime
        )
        max_date = (
            max(max_date, dataset.acquisition_datetime)
            if max_date
            else dataset.acquisition_datetime
        )
    context = {
        "project_id": int(pm.omero_project.getId()),
        "project_name": pm.omero_project.getName(),
        "key_measurements_by_kkm": collection_key_measurements_by_kkm,
        "key_measurements_by_dataset_id": collection_key_measurements_by_dataset_id,
        "channels": list(channels),
        "dates": dates,
        "min_date": min_date,
        "max_date": max_date,
        "unprocessed_datasets": list(pm.unprocessed_datasets),
        "input_parameters": pm.input_parameters,
        "sample": pm.sample,
        "thresholds": pm.thresholds,
        "kkm": kkm_list,
        "mm_dataset_collection": pm.mm_dataset_collection,
    }
    pm.context = serialize(context)
