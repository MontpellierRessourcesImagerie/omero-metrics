"""Tests for omero_metrics.tools.data_type module."""

import pytest

pytest.importorskip("omero", reason="omero package not available locally")

from omero_metrics.tools.data_type import (
    DATA_TYPE,
    DATASET_IMAGES,
    DATASET_TYPES,
    INPUT_IMAGES_MAPPING,
    KKM_MAPPINGS,
    TEMPLATE_MAPPINGS_DATASET,
    TEMPLATE_MAPPINGS_IMAGE,
)


class TestDatasetTypes:
    def test_supported_types(self):
        assert "FieldIlluminationDataset" in DATASET_TYPES
        assert "PSFBeadsDataset" in DATASET_TYPES

    def test_all_types_have_input_mapping(self):
        for ds_type in DATASET_TYPES:
            assert (
                ds_type in INPUT_IMAGES_MAPPING
            ), f"{ds_type} missing from INPUT_IMAGES_MAPPING"

    def test_all_types_have_image_mapping(self):
        for ds_type in DATASET_TYPES:
            assert (
                ds_type in DATASET_IMAGES
            ), f"{ds_type} missing from DATASET_IMAGES"

    def test_all_types_have_kkm_mapping(self):
        for ds_type in DATASET_TYPES:
            assert ds_type in KKM_MAPPINGS, f"{ds_type} missing from KKM_MAPPINGS"

    def test_all_types_have_template_mapping(self):
        for ds_type in DATASET_TYPES:
            assert (
                ds_type in TEMPLATE_MAPPINGS_DATASET
            ), f"{ds_type} missing from TEMPLATE_MAPPINGS_DATASET"
            assert (
                ds_type in TEMPLATE_MAPPINGS_IMAGE
            ), f"{ds_type} missing from TEMPLATE_MAPPINGS_IMAGE"


class TestInputImagesMapping:
    def test_field_illumination(self):
        assert (
            INPUT_IMAGES_MAPPING["FieldIlluminationDataset"]
            == "field_illumination_images"
        )

    def test_psf_beads(self):
        assert INPUT_IMAGES_MAPPING["PSFBeadsDataset"] == "psf_beads_images"


class TestDatasetImages:
    def test_field_illumination_structure(self):
        fi = DATASET_IMAGES["FieldIlluminationDataset"]
        assert "input_data" in fi
        assert "output" in fi
        assert isinstance(fi["input_data"], list)

    def test_psf_beads_has_output_images(self):
        psf = DATASET_IMAGES["PSFBeadsDataset"]
        assert "average_bead" in psf["output"]


class TestDataType:
    def test_field_illumination_config(self):
        fi = DATA_TYPE["FieldIlluminationInputParameters"]
        assert fi[0] == "FieldIlluminationDataset"
        assert fi[1] == "FieldIlluminationInputData"
        assert fi[2] == "field_illumination_images"
        assert callable(fi[3])

    def test_psf_beads_config(self):
        psf = DATA_TYPE["PSFBeadsInputParameters"]
        assert psf[0] == "PSFBeadsDataset"
        assert psf[1] == "PSFBeadsInputData"
        assert psf[2] == "psf_beads_images"
        assert callable(psf[3])

    def test_all_data_types_have_four_elements(self):
        for key, value in DATA_TYPE.items():
            assert len(value) == 4, f"{key} should have 4 elements"
            assert isinstance(value[0], str)
            assert isinstance(value[1], str)
            assert isinstance(value[2], str)
            assert callable(value[3])


class TestKkmMappings:
    def test_field_illumination_kkm(self):
        kkm = KKM_MAPPINGS["FieldIlluminationDataset"]
        assert "max_intensity" in kkm
        assert "center_region_intensity_fraction" in kkm

    def test_psf_beads_kkm(self):
        kkm = KKM_MAPPINGS["PSFBeadsDataset"]
        assert "considered_valid_count" in kkm
        assert "fwhm_micron_x_mean" in kkm
        assert "fwhm_micron_y_mean" in kkm
        assert "fwhm_micron_z_mean" in kkm

    def test_kkm_values_are_strings(self):
        for ds_type, kkm_list in KKM_MAPPINGS.items():
            for item in kkm_list:
                assert isinstance(
                    item, str
                ), f"KKM item '{item}' in {ds_type} should be a string"


class TestTemplateMappings:
    def test_dataset_templates_are_strings(self):
        for ds_type, template in TEMPLATE_MAPPINGS_DATASET.items():
            assert isinstance(template, str)

    def test_image_templates_have_input_data(self):
        for ds_type, mapping in TEMPLATE_MAPPINGS_IMAGE.items():
            assert (
                "input_data" in mapping
            ), f"{ds_type} missing 'input_data' in image template mapping"
