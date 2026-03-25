import datetime
import logging

from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema
from omero.gateway import (
    BlitzGateway,
    DatasetWrapper,
    ImageWrapper,
    ProjectWrapper,
)

from omero_metrics.tools import context_loaders, delete, dump, load, update
from omero_metrics.tools.data_type import (
    KKM_MAPPINGS,
    TEMPLATE_MAPPINGS_DATASET,
    TEMPLATE_MAPPINGS_IMAGE,
)

logger = logging.getLogger(__name__)


DATASET_CONTEXT_LOADERS = {
    "FieldIlluminationDataset": context_loaders.FieldIlluminationDataset,
    "PSFBeadsDataset": context_loaders.PSFBeadsDataset,
}

IMAGE_CONTEXT_LOADERS = {
    "FieldIlluminationDataset": {
        "input_data": context_loaders.FieldIlluminationDataset_input_data_Image,
    },
    "PSFBeadsDataset": {
        "input_data": context_loaders.PSFBeadsDataset_input_data_Image,
        "output": context_loaders.PSFBeadsDataset_output_AveragePSF,
    },
}


def warning_message(msg):
    dash_context = {"message": msg}
    app_name = "WarningApp"
    return dash_context, app_name


class ImageManager:
    """This class is a unit of work that processes
    data from an image (omero-metrics).
    """

    def __init__(self, conn: BlitzGateway, omero_image: ImageWrapper):
        self._conn = conn
        if isinstance(omero_image, ImageWrapper):
            self.omero_image = omero_image
        else:
            raise ValueError("the object must be an ImageWrapper")
        self.omero_image = omero_image
        self.omero_dataset = None
        self.dataset_manager = None
        self.image_exist = None
        self.image_location = None
        self.image_index = None
        self.context = {}
        self.mm_image = None
        self.image_exist = None
        self.image_index = None
        self.image_location = None
        self.app_name = None

    def load_context(self):
        self.load_data()
        if self.dataset_manager.is_processed():
            if (
                self.dataset_manager.mm_dataset.__class__.__name__
                in TEMPLATE_MAPPINGS_DATASET
            ):
                # TODO: move the image_exists call to the load_data method
                (
                    self.image_exist,
                    self.image_location,
                    self.image_index,
                ) = load.image_exist(
                    self.omero_image.getId(), self.dataset_manager.mm_dataset
                )
                if self.image_exist:
                    self.app_name = TEMPLATE_MAPPINGS_IMAGE.get(
                        self.dataset_manager.mm_dataset.__class__.__name__
                    )[self.image_location]
                    IMAGE_CONTEXT_LOADERS[
                        self.dataset_manager.mm_dataset.__class__.__name__
                    ][self.image_location](self)
                else:
                    message = "Image does not exist in the dataset yaml file. Unable to visualize"
                    logger.warning(message)
                    self.context, self.app_name = warning_message(message)
            else:
                message = "Unknown analysis type. Unable to visualize"
                logger.warning(message)
                self.context, self.app_name = warning_message(message)
        else:
            message = "Dataset has not been processed. Unable to visualize"
            logger.warning(message)
            self.context, self.app_name = warning_message(message)

    def load_data(self, force_reload: bool = False):
        if force_reload or self.dataset_manager is None:
            self.omero_dataset = self.omero_image.getParent()
            self.dataset_manager = DatasetManager(self._conn, self.omero_dataset)
        if force_reload or self.mm_image is None:
            self.dataset_manager.load_data(
                load_images=False, force_reload=force_reload
            )
            if self.dataset_manager.is_processed():
                self.dataset_manager.remove_unsupported_data()


class DatasetManager:
    """
    This class is a unit of work that processes
    data from a dataset or a dataset_collection (omero-metrics)
    It contains the data (microscope-metrics_schema
    datasets and dataset_collections) and the necessary methods
    to interact with OMERO and load and dump data.
    """

    def __init__(
        self,
        conn: BlitzGateway,
        omero_dataset: DatasetWrapper,
    ):
        self._conn = conn
        if isinstance(omero_dataset, DatasetWrapper):
            self.omero_dataset = omero_dataset
        else:
            raise ValueError("dataset must be a DatasetWrapper")
        self.omero_project = self.omero_dataset.getParent()
        self.input_parameters = None
        self.mm_dataset = None
        self.analysis_config = None
        self.analysis_config_id = None
        self.analysis_func = None
        self.app_name = None
        self.context = {}
        self.microscope = mm_schema.Microscope()
        self.kkm = None
        self.attached_images = [
            {"value": f"{i.getId()}", "label": f"{i.getName()}"}
            for i in omero_dataset.listChildren()
            if i.OMERO_CLASS == "Image"
        ]

    def is_processed(self):
        return self.mm_dataset.processed if self.mm_dataset else False

    def is_validated(self):
        return self.mm_dataset.validated if self.mm_dataset else False

    def remove_unsupported_data(self):
        dump._remove_unsupported_types(self.mm_dataset.input_data)
        dump._remove_unsupported_types(self.mm_dataset.input_parameters)
        dump._remove_unsupported_types(self.mm_dataset.output)

    def load_context(self):
        self.load_data(load_images=False)
        if self.is_processed():
            if self.mm_dataset.__class__.__name__ in TEMPLATE_MAPPINGS_DATASET:
                self.app_name = TEMPLATE_MAPPINGS_DATASET.get(
                    self.mm_dataset.__class__.__name__
                )
                DATASET_CONTEXT_LOADERS[self.mm_dataset.__class__.__name__](self)

            else:
                message = "Unknown analysis type. Unable to visualize"
                logger.warning(message)
                self.context, self.app_name = warning_message(message)

        else:
            if self.omero_project and len(self.attached_images) > 0:
                self.input_parameters = load.load_input_config_file(
                    self.omero_project
                )
                if self.input_parameters:
                    self.app_name = "omero_dataset_form"
                    self.context = {
                        "list_images": self.attached_images,
                        "input_parameters": self.input_parameters,
                        "dataset_id": self.omero_dataset.getId(),
                    }

                else:
                    message = "No, config file detected. Click on the project parent to load the config file."
                    logger.warning(message)
                    self.context, self.app_name = warning_message(message)

            else:
                message = "The dataset is not under a project or does not contain images. Unable to visualize"
                logger.warning(message)
                self.context, self.app_name = warning_message(message)

    def load_data(self, load_images: bool, force_reload: bool = False):
        if force_reload or self.mm_dataset is None:
            self.mm_dataset = load.load_dataset(self.omero_dataset, load_images)
            if self.mm_dataset is not None:
                self.kkm = KKM_MAPPINGS.get(self.mm_dataset.__class__.__name__)
        else:
            raise NotImplementedError(
                "partial loading of data from OMERO is not yet implemented"
            )

    def load_analysis_config(self, force_reload=True):
        if not force_reload and self.analysis_config and self.analysis_config_id:
            return
        else:
            (
                self.analysis_config_id,
                self.analysis_config,
            ) = load.load_analysis_config(self.omero_project)

    # TODO; This function can be probably deleted as nobody is calling it
    def dump_analysis_config(self):
        if not self.analysis_config:
            logger.error("No configuration to save.")
            return

        update.update_map_annotation(
            conn=self._conn,
            new_map_annotation=self.analysis_config,
            target_map_annotation=self.analysis_config_id,
            replace=True,
            new_description=f"config saved on {datetime.datetime.now()}",
        )
        logger.info(f"Saved configuration on mapAnn id:{self.analysis_config_id}")

    def _update_dataset_input_config(self, config):
        for key, val in config.items():
            setattr(self.mm_dataset.input_parameters, key, val)

    def dump_data(self):
        # TODO: review this function
        for mm_ds in self.mm_dataset:
            if not mm_ds.processed:
                logger.error("Dataset not processed. Unable to dump data")
            dump.dump_dataset(
                conn=self._conn,
                dataset=mm_ds,
                target_project=self.omero_project,
            )

    def process_data(self, force_reprocess=False):
        if not force_reprocess and self.is_processed():
            if self.is_validated():
                logger.warning(
                    "Dataset has been processed and validated. "
                    "Force reprocess to process again"
                )
            else:
                logger.warning(
                    "Dataset has been processed but not validated. "
                    "Force reprocess to process again"
                )
            return False
        items_to_remove = []
        config = {
            k: v for k, v in self.analysis_config.items() if k not in items_to_remove
        }

        self._update_dataset_input_config(config)
        self.analysis_func(self.mm_dataset)

        return True

    def delete_processed_data(self):
        """This function deletes the output of the dataset"""
        logger.debug(
            f"Deleting processed data for dataset {self.omero_dataset.getId()}"
        )
        if not self.is_processed():
            logger.warning("Data has not been processed. Nothing to delete")
            return
        try:
            delete.delete_mm_obj_omero_refs(self._conn, self.mm_dataset.output)
            delete.delete_dataset_file_ann(self._conn, self.omero_dataset)
        except Exception as e:
            logger.error(f"Error deleting processed data: {e}")
            self.mm_dataset.validated = False
            raise e
        else:
            logger.info("Processed data deleted.")

    def validate_data(self):
        if not self.is_processed():
            logger.error("Data has not been processed. It cannot be validated")
        if self.mm_dataset.validated:
            logger.warning("Data was already validated. Keeping unchanged.")

        self.mm_dataset.validated = True
        logger.info("Validating dataset.")

    def invalidate_data(self):
        if not self.mm_dataset.validated:
            logger.warning("Data is already not validated. Keeping unchanged.")
        self.mm_dataset.validated = False
        logger.info("Invalidating dataset.")


class ProjectManager:
    """
    This class is a unit of work that processes
    data from a project (omero-metrics)
    It contains the data and the necessary methods
    to interact with OMERO and load and dump data.
    """

    def __init__(self, conn: BlitzGateway, omero_project: ProjectWrapper):
        self._conn = conn
        self.omero_project = omero_project
        self.mm_dataset_collection = None
        self.unprocessed_datasets = set()
        self.input_parameters = None
        self.sample = None
        self.thresholds = None
        self.app_name = None
        self.context = {}

    def load_data(self, force_reload=False):
        if self.mm_dataset_collection is not None and not force_reload:
            return
        datasets_types = set()
        datasets = []
        for dataset in self.omero_project.listChildren():
            dm = DatasetManager(self._conn, dataset)
            dm.load_data(load_images=False, force_reload=force_reload)
            if dm.mm_dataset is not None:
                datasets.append(dm.mm_dataset)
                datasets_types.add(dm.mm_dataset.__class__.__name__)
            else:
                self.unprocessed_datasets.add(int(dataset.getId()))
        if len(datasets_types) == 1:
            self.mm_dataset_collection = (
                mm_schema.HarmonizedMetricsDatasetCollection(
                    name=self.omero_project.getName(),
                    description=self.omero_project.getDescription(),
                    dataset_class=datasets_types.pop(),
                    dataset_collection=datasets,
                )
            )
        elif len(datasets_types) > 1:
            self.mm_dataset_collection = mm_schema.MetricsDatasetCollection(
                name=self.omero_project.getName(),
                description=self.omero_project.getDescription(),
                dataset_collection=datasets,
            )
        else:
            self.mm_dataset_collection = None

    def is_harmonized(self):
        return isinstance(
            self.mm_dataset_collection, mm_schema.HarmonizedMetricsDatasetCollection
        )

    def load_context(self):
        self.load_data()
        if self.mm_dataset_collection is None:
            # Empty project or non-analyzed we cannot know if it is harmonized or not
            context_loaders.EmptyMetricsDatasetCollection(self)
        elif self.is_harmonized():
            if self.mm_dataset_collection.dataset_class in TEMPLATE_MAPPINGS_DATASET:
                context_loaders.HarmonizedMetricsDatasetCollection(self)
            else:
                raise ValueError("Unknown analysis type. Unable to visualize")
        else:
            raise ValueError(
                "OMERO-metrics does not support multiple analysis types in the same project."
            )

    def save_settings(self):
        pass

    def delete_data(self):
        pass

    def delete_processed_data(self):
        for dataset in self.mm_dataset_collection.dataset_collection:
            if dataset.processed:
                logger.debug(f"Deleting processed data for dataset {dataset.name}")
                try:
                    delete.delete_mm_obj_omero_refs(self._conn, dataset.output)
                    delete.delete_dataset_file_ann(
                        self._conn,
                        self._conn.getObject(
                            "Dataset", dataset.data_reference.omero_object_id
                        ),
                    )
                except Exception as e:
                    logger.error(f"Error deleting processed data: {e}")
                    dataset.validated = False
                    raise e
                else:
                    logger.info("Processed data deleted.")

    def load_input_config(self):
        if self.input_parameters is None:
            config = load.load_input_config_file(self.omero_project)
            if config is not None:
                self.input_parameters = config.get("input_parameters")
                self.sample = config.get("sample")

    def load_thresholds(self):
        if self.thresholds is None:
            self.thresholds = load.load_thresholds_file(self.omero_project)


class MicroscopeManager:
    """
    This class is a unit of work that processes
    data from a microscope (omero-metrics)
    It contains the data and the necessary methods
    to interact with OMERO and load and dump data.
    """

    def __init__(self, conn: BlitzGateway, microscope_id: int):
        self._conn = conn
        self.microscope_id = microscope_id
        self.microscope = conn.getObject("Microscope", microscope_id)
        self.data = None
        self.context = None

    def visualize_data(self):
        pass

    def save_settings(self):
        pass

    def delete_data(self):
        pass
