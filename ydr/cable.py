from bpy.types import (
    Object,
    Mesh,
)
from enum import Enum
from typing import Optional
import numpy as np
from ..sollumz_properties import SollumType

CABLE_SHADER_NAME = "cable.sps"

class CableAttr(str, Enum):
    RADIUS = ".cable.radius"
    DIFFUSE_FACTOR = ".cable.diffuse_factor"
    UM_SCALE = ".cable.um_scale"
    PHASE_OFFSET = ".cable.phase_offset"

    @property
    def type(self):
        match self:
            case CableAttr.PHASE_OFFSET:
                return "FLOAT2"
            case _:
                return "FLOAT"

    @property
    def domain(self):
        return "POINT"

    @property
    def default_value(self) -> object:
        match self:
            case CableAttr.RADIUS:
                return 0.02
            case CableAttr.DIFFUSE_FACTOR:
                return 1.0
            case CableAttr.UM_SCALE:
                return 1.0
            case CableAttr.PHASE_OFFSET:
                return (0.0, 0.0)
            case _:
                assert False, f"Default value not set for cable attribute '{self}'"

    @property
    def label(self) -> str:
        match self:
            case CableAttr.RADIUS:
                return "Radius"
            case CableAttr.DIFFUSE_FACTOR:
                return "Diffuse Factor"
            case CableAttr.UM_SCALE:
                return "Micromovements Scale"
            case CableAttr.PHASE_OFFSET:
                return "Phase Offset"
            case _:
                assert False, f"Label not set for cable attribute '{self}'"

    @property
    def description(self) -> str:
        match self:
            case CableAttr.RADIUS:
                return "Determines the size of the cable"
            case CableAttr.DIFFUSE_FACTOR:
                return "Interpolation factor for the cable diffuse color: 0 = shader_cableDiffuse, 1 = shader_cableDiffuse2"
            case CableAttr.UM_SCALE:
                return "Determines how much the cable moves: 0 = no micromovements"
            case CableAttr.PHASE_OFFSET:
                return ""
            case _:
                assert False, f"Label not set for cloth attribute '{self}'"


def mesh_add_cable_attribute(mesh: Mesh, attr: CableAttr):
    mesh.attributes.new(attr, attr.type, attr.domain)


def mesh_has_cable_attribute(mesh: Mesh, attr: CableAttr) -> bool:
    return attr in mesh.attributes

# def mesh_set_cloth_attribute_value(mesh, attr: ClothAttr, index: int, value: object):
#     mesh.attributes[attr].data[index].value = value


def mesh_get_cable_attribute_values(mesh: Mesh, attr: CableAttr) -> np.ndarray:
    num = 0
    match attr.domain:
        case "POINT":
            num = len(mesh.vertices)
        case _:
            assert False, f"Domain '{attr.domain}' not handled"


    values = np.array([attr.default_value] * num)
    mesh_attr = mesh.attributes.get(attr, None)
    if mesh_attr is not None:
        field = "vector" if attr.type == "FLOAT2" else "value" 
        mesh_attr.data.foreach_get(field, values.ravel())

    return values


def is_cable_mesh_object(mesh_obj: Optional[Object]) -> bool:
    """Gets whether the object has a valid cable mesh."""
    if mesh_obj is None:
        return False

    if mesh_obj.sollum_type != SollumType.DRAWABLE_MODEL or mesh_obj.type != "MESH":
        return False

    return is_cable_mesh(mesh_obj.data)


def is_cable_mesh(mesh: Optional[Mesh]) -> bool:
    """Gets whether the mesh is valid cable mesh."""
    if mesh is None:
        return False

    return (
        len(mesh.polygons) == 0 and
        len(mesh.vertices) > 0 and
        len(mesh.edges) > 0 and
        len(mesh.materials) == 1 and
        mesh.materials[0].shader_properties.filename == CABLE_SHADER_NAME
    )
