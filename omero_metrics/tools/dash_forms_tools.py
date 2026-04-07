import re
from dataclasses import fields
from typing import Union, get_args, get_origin

import dash_mantine_components as dmc
from dash_iconify import DashIconify

# TODO: Modify the schema to make this a mm_schema class
from linkml_runtime.utils.metamodelcore import XSDDateTime
from microscopemetrics_schema.datamodel.microscopemetrics_schema import ProtocolUrl

# These mappings must be ordered by priority
FIELD_TYPE_MAPPING = {
    XSDDateTime: [dmc.DateTimePicker, "carbon:calendar"],
    ProtocolUrl: [dmc.TextInput, "carbon:copy-link"],
    float: [dmc.NumberInput, "carbon:character-decimal"],
    int: [dmc.NumberInput, "carbon:character-whole-number"],
    bool: [dmc.Switch, "carbon:switch-disabled"],
    str: [dmc.TextInput, "carbon:string-text"],
}


def extract_form_data(form_content):
    return {
        i["props"]["id"].split(":")[1]: i["props"]["value"] for i in form_content
    }


def disable_all_fields_dash_form(form):
    for i, t in enumerate(form):
        form[i]["props"]["disabled"] = True
    return form


def clean_field_name(field: str):
    return field.replace("_", " ").title()


def get_field_types(field):
    data_type = {
        "field_name": field.name,
        "type": None,
        "optional": False,
        "default": field.default,
    }
    if get_origin(field.type) is Union:
        args = get_args(field.type)
        # Check if it's Optional (Union with None)
        if type(None) in args:
            data_type["optional"] = True
            args = [arg for arg in args if arg is not type(None)]

        # Select type by priority based on FIELD_TYPE_MAPPING order
        selected_type = None
        for priority_type in FIELD_TYPE_MAPPING.keys():
            if priority_type in args:
                selected_type = priority_type
                break

        data_type["type"] = selected_type
    elif field.type in FIELD_TYPE_MAPPING.keys():
        data_type["type"] = field.type

    return data_type


def get_dmc_field_input(field, mm_object, disabled=False):
    field_info = get_field_types(field)
    input_field_name = FIELD_TYPE_MAPPING[field_info["type"]][0]
    input_field = input_field_name()
    input_field.id = f"{mm_object.class_name}:{field_info['field_name']}"
    input_field.label = clean_field_name(field_info["field_name"])
    input_field.placeholder = f"Enter {clean_field_name(field_info['field_name'])}"
    input_field.value = (
        field_info["default"]
        if getattr(mm_object, field.name) is None
        else getattr(mm_object, field.name)
    )
    input_field.w = "100%"
    input_field.disabled = disabled
    input_field.required = not field_info["optional"]
    input_field.leftSection = DashIconify(
        icon=FIELD_TYPE_MAPPING[field_info["type"]][1]
    )
    input_field.mb = "sm"

    return input_field


def validate_form(state):
    return all(
        i["props"]["id"] == "submit_id"
        or not (
            i["props"]["required"]
            and (i["props"]["value"] is None or i["props"]["value"] == "")
        )
        for i in state
    )


def add_space_between_capitals(s: str) -> str:
    label = re.sub(r"(?<!^)(?=[A-Z])", " ", s)
    label = label.replace("P S F", "PSF")
    return label


def get_form(mm_object, disabled=False, form_id="form_content"):
    form_content = dmc.Fieldset(
        id=form_id,
        children=[],
        # TODO: we have to rather rely on the title of the class
        legend=add_space_between_capitals(mm_object.class_name),
        variant="filled",
        radius="md",
    )
    for field in fields(mm_object):
        form_content.children.append(
            get_dmc_field_input(field, mm_object, disabled=disabled)
        )
    return form_content
