import logging
import traceback
from datetime import datetime

import omero
from django.shortcuts import render
from microscopemetrics import AnalysisError, SaturationError
from microscopemetrics_schema import datamodel as mm_schema
from omero.gateway import FileAnnotationWrapper
from omeroweb.webclient.decorators import login_required

from omero_metrics.tools import (
    data_managers,
    data_type,
    delete,
    dump,
    load,
    omero_tools,
)
from omero_metrics.tools.data_type import TEMPLATE_MAPPINGS_DATASET
from omero_metrics.tools.serializers import serialize

logger = logging.getLogger(__name__)


TEMPLATE_DASH_NAME = "omero_metrics/dash_template_center_ui/dash_template.html"


@login_required()
def index(request, conn=None, **kwargs):
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
    }
    return render(request, "omero_metrics/top_link_template/index.html", context)


@login_required(setGroupContext=True)
def center_viewer_image(request, image_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())
    try:
        image_wrapper = conn.getObject("Image", image_id)
        if image_wrapper is None:
            raise ValueError(
                f"Image {image_id} not found. "
                "Check that you are in the correct group."
            )
        im = data_managers.ImageManager(conn, image_wrapper)
        im.load_context()
        dash_context["context"] = im.context
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": im.app_name},
        )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


@login_required(setGroupContext=True)
def center_viewer_project(request, project_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())
    try:
        project_wrapper = conn.getObject("Project", project_id)
        pm = data_managers.ProjectManager(conn, project_wrapper)
        pm.load_context()
        if pm.input_parameters is None:
            # No analyzed datasets or input parameters so we need to trigger
            # the configuration form
            dash_context["context"] = {"project_id": project_id}
            request.session["django_plotly_dash"] = dash_context
            return render(
                request,
                template_name=TEMPLATE_DASH_NAME,
                context={"app_name": "omero_project_config_form"},
            )
        if pm.mm_dataset_collection:  # There is at least one analyzed dataset
            if pm.is_harmonized():
                dash_context["context"] = pm.context
                request.session["django_plotly_dash"] = dash_context
                return render(
                    request,
                    template_name=TEMPLATE_DASH_NAME,
                    context={"app_name": "omero_project_dash"},
                )
            else:
                dash_context["context"] = {
                    "message": "OMERO-metrics does not support non-harmonized projects."
                }
                request.session["django_plotly_dash"] = dash_context
                return render(
                    request,
                    template_name=TEMPLATE_DASH_NAME,
                    context={"app_name": "WarningApp"},
                )
        else:  # No analyzed datasets but input parameters configured
            dash_context["context"] = pm.context
            request.session["django_plotly_dash"] = dash_context
            return render(
                request,
                template_name=TEMPLATE_DASH_NAME,
                context={"app_name": "omero_project_dash"},
            )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


@login_required(setGroupContext=True)
def center_viewer_group(request, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", dict())

    try:
        if request.session.get("active_group"):
            active_group = request.session["active_group"]
        else:
            active_group = conn.getEventContext().groupId
        file_ann, map_ann = load.get_annotations_tables(conn, active_group)
        dash_context = request.session.get("django_plotly_dash", dict())
        group = conn.getObject("ExperimenterGroup", active_group)
        group_name = group.getName()
        group_description = group.getDescription()
        context = {
            "group_id": active_group,
            "group_name": group_name,
            "group_description": group_description,
            "file_ann": file_ann.to_json(date_format="iso"),
            "map_ann": map_ann.to_json(date_format="iso"),
        }
        dash_context["context"] = context
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "omero_group_dash"},
        )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


@login_required(setGroupContext=True)
def center_viewer_dataset(request, dataset_id, conn=None, **kwargs):
    dash_context = request.session.get("django_plotly_dash", {})
    try:
        dataset_wrapper = conn.getObject("Dataset", dataset_id)
        dm = data_managers.DatasetManager(conn, dataset_wrapper)
        dm.load_context()
        dash_context["context"] = dm.context
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": dm.app_name},
        )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


@login_required(setGroupContext=True)
def microscope_view(request, conn=None, **kwargs):
    """This is to display the microscope dashboard
    for the top link ui"""
    return render(
        request,
        template_name="omero_metrics/top_link_template/microscope.html",
        context={"app_name": "top_iu_microscope"},
    )


@login_required(setGroupContext=True)
def center_view_projects(request, conn=None, **kwargs):
    """This is to display the project dashboard
    for the top link ui"""
    id_list = request.GET.get("projectIds", None)
    id_list = request.GET.get("Project", id_list)
    dash_context = request.session.get("django_plotly_dash", {})
    if not id_list:
        # Not really sure when this could happen
        dash_context["context"] = {"message": "No project ids provided."}
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "WarningApp"},
        )
    try:
        project_ids = [int(i) for i in id_list.split(",")]
        data = {}
        for project_id in project_ids:
            project_wrapper = conn.getObject("Project", project_id)
            pm = data_managers.ProjectManager(conn, project_wrapper)
            pm.load_context()
            if pm.input_parameters and pm.is_harmonized():
                dash_context["context"][f"{project_id}"] = pm.context

        if not dash_context["context"]:
            dash_context["context"] = {
                "message": "OMERO-metrics did not detect any analyzed projects in the selection."
            }
            request.session["django_plotly_dash"] = dash_context
            return render(
                request,
                template_name=TEMPLATE_DASH_NAME,
                context={"app_name": "WarningApp"},
            )

        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "omero_multiple_projects"},
        )
    except Exception as e:
        dash_context["context"] = {
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        request.session["django_plotly_dash"] = dash_context
        return render(
            request,
            template_name=TEMPLATE_DASH_NAME,
            context={"app_name": "ErrorApp"},
        )


# These views are called from the dash app, and they return a message and a color to display in the app.


@login_required(setGroupContext=True)
def save_config(request, conn=None, **kwargs):
    """Save the configuration file"""
    try:
        project_id = kwargs["project_id"]
        mm_input_parameters = kwargs["input_parameters"]
        mm_sample = kwargs["sample"]
        project_wrapper = conn.getObject("Project", project_id)
        setup = load.load_input_config_file(project_wrapper)
        try:
            if setup:
                to_delete = []
                for ann in project_wrapper.listAnnotations():
                    if isinstance(ann, FileAnnotationWrapper):
                        ns = ann.getFile().getName()
                        if ns.startswith("study_config"):
                            to_delete.append(ann.getId())
                conn.deleteObjects(
                    graph_spec="Annotation",
                    obj_ids=to_delete,
                    deleteAnns=True,
                    deleteChildren=True,
                    wait=True,
                )
            dump.dump_config_input_parameters(
                conn, mm_input_parameters, mm_sample, project_wrapper
            )
            return (
                "success",
                "Configuration saved successfully. Select the project to see the changes.",
            )
        except omero.SecurityViolation:
            return (
                "authorisation_error",
                "You don't have the necessary permissions to save the configuration.",
            )
        except Exception as e:
            return "unidentified_error", str(e)
    except Exception as e:
        return "unidentified_error", str(e)


@login_required(setGroupContext=True)
def run_analysis_view(request, conn=None, **kwargs):
    """Run the analysis"""
    try:
        dataset_wrapper = conn.getObject("Dataset", kwargs["dataset_id"])
        project_wrapper = dataset_wrapper.getParent()
        list_images = kwargs["list_images"]
        comment = kwargs["comment"]
        list_mm_images = [
            load.load_image(conn.getObject("Image", int(i))) for i in list_images
        ]
        mm_sample = kwargs["mm_sample"]
        mm_input_parameters = kwargs["mm_input_parameters"]
        input_data = getattr(
            mm_schema, data_type.DATA_TYPE[mm_input_parameters.class_name][1]
        )
        input_data = input_data(
            **{
                data_type.DATA_TYPE[mm_input_parameters.class_name][
                    2
                ]: list_mm_images
            }
        )
        mm_microscope = mm_schema.Microscope(
            name=project_wrapper.getDetails().getGroup().getName()
        )
        mm_experimenter = mm_schema.Experimenter(
            # TODO: we must get the ORCID from somewhere here
            orcid="0000-0002-1825-0097",
            name=conn.getUser().getName(),
        )
        mm_dataset = getattr(
            mm_schema, data_type.DATA_TYPE[mm_input_parameters.class_name][0]
        )
        mm_dataset = mm_dataset(
            name=dataset_wrapper.getName(),
            description=dataset_wrapper.getDescription(),
            data_reference=omero_tools.get_ref_from_object(dataset_wrapper),
            input_parameters=mm_input_parameters,
            microscope=mm_microscope,
            sample=mm_sample,
            input_data=input_data,
            acquisition_datetime=dataset_wrapper.getDate().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            experimenter=mm_experimenter,
        )
        try:
            # Run the analysis
            data_type.DATA_TYPE[mm_input_parameters.class_name][3](mm_dataset)
        except AnalysisError or SaturationError as e:
            logger.error(f"{e}")
            return "analysis_error", str(e), e.suggestion
        except Exception as e:
            logger.error(f"Error running the analysis: {e}")
            return (
                "unidentified_error",
                "Error during analysis run:\n"
                f"{e}\n"
                "Please, contact support with the following traceback:",
                traceback.format_exc(),
            )
        if mm_dataset.processed:
            try:
                if comment:
                    mm_comment = mm_schema.Comment(
                        datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        text=comment,
                        comment_type="PROCESSING",
                    )
                    mm_dataset["output"]["comment"] = mm_comment
                dump.dump_dataset(
                    conn=conn,
                    dataset=mm_dataset,
                    target_project=project_wrapper,
                    dump_as_project_file_annotation=True,
                    dump_as_dataset_file_annotation=True,
                    dump_input_images=False,
                    dump_analysis=True,
                )

                logger.info(f"Analysis completed successfully")
                return (
                    "success",
                    "Analysis completed successfully.",
                    mm_dataset.description,
                )
            except Exception as e:
                logger.error(f"Error saving the analysis: {e}")
                return (
                    "unidentified_error",
                    "Error while saving the analysis.\n"
                    f"{e}\n"
                    "Please, contact support with the following traceback:",
                    traceback.format_exc(),
                )
        else:
            logger.error("Analysis run but dataset.processed is False.")
            return (
                "unidentified_error",
                "Analysis run but something prevented it to be tagged as processed.\n"
                "Please, contact support with the following traceback:",
                traceback.format_exc(),
            )
    except Exception as e:
        logger.error(f"Error during run_analysis_view execution: {e}")
        return (
            "unidentified_error",
            "run_analysis_view could not proceed.\n"
            f"{e}\n"
            "Please, contact support with the following traceback:",
            traceback.format_exc(),
        )


@login_required(setGroupContext=True)
def delete_all(request, conn=None, **kwargs):
    """Delete all the files"""
    try:
        group_id = kwargs["group_id"]
        for project in conn.getObjects("Project", opts={"group": group_id}):
            pm = data_managers.ProjectManager(conn, project)
            pm.load_data()
            pm.delete_processed_data()
        return delete.delete_all_annotations(conn, group_id)
    except Exception as e:
        return "unidentified_error", str(e)


@login_required(setGroupContext=True)
def delete_dataset(request, conn=None, **kwargs):
    """Delete the dataset outputs"""
    dataset_id = kwargs["dataset_id"]
    logger.info(f"Deleting dataset {dataset_id}")
    dataset_wrapper = conn.getObject("Dataset", dataset_id)
    dm = data_managers.DatasetManager(conn, dataset_wrapper)
    dm.load_data(load_images=False)
    try:
        dm.delete_processed_data()
        return "success", "Output deleted successfully."
    except Exception as e:
        return "unidentified_error", str(e)


@login_required(setGroupContext=True)
def delete_project(request, conn=None, **kwargs):
    """Delete the project outputs"""
    project_id = kwargs["project_id"]
    logger.info(f"Deleting dataset {project_id}")
    project_wrapper = conn.getObject("Project", project_id)
    pm = data_managers.ProjectManager(conn, project_wrapper)
    pm.load_data()
    try:
        pm.delete_processed_data()
        return "success", "Output deleted successfully."
    except Exception as e:
        return "unidentified_error", str(e)


@login_required(setGroupContext=True)
def save_threshold(request, conn=None, **kwargs):
    """Save the threshold"""
    try:
        project_id = kwargs["project_id"]
        threshold = kwargs["threshold"]
        project_wrapper = conn.getObject("Project", project_id)
        threshold_exist = load.load_thresholds_file(project_wrapper)
        if threshold:
            if threshold_exist:
                to_delete = []
                for ann in project_wrapper.listAnnotations():
                    if isinstance(ann, FileAnnotationWrapper):
                        ns = ann.getFile().getName()
                        if ns.startswith("threshold"):
                            to_delete.append(ann.getId())
                conn.deleteObjects(
                    graph_spec="Annotation",
                    obj_ids=to_delete,
                    deleteAnns=True,
                    deleteChildren=True,
                    wait=True,
                )
            dump.dump_threshold(conn, project_wrapper, threshold)
            return (
                "success",
                "Threshold saved successfully. Select the project to see the changes.",
            )
        else:
            return (
                "unidentified_error",
                "Failed to save threshold Configuration file doesn't exist.",
            )
    except Exception as e:
        if isinstance(e, omero.SecurityViolation):
            return (
                "authorisation_error",
                "You don't have the necessary permissions to save the threshold.",
            )
        elif isinstance(e, omero.CmdError):
            return (
                "unidentified_error",
                "You don't have the necessary permissions to save the threshold.",
            )
        else:
            return (
                "unidentified_error",
                "Something happened. Couldn't save thresholds.",
            )


@login_required(setGroupContext=True)
def imageJ(request, conn=None, **kwargs):
    """Run ImageJ"""
    return render(
        request,
        template_name="omero_metrics/top_link_template/imagej_template.html",
        context={"app_name": "imageJ"},
    )
