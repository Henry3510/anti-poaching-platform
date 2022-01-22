from enum import Enum
from typing import Generic, TypeVar

from api.lib import APIModel

ResultT = TypeVar("ResultT")


class ConservationStatus(str, Enum):
    EX = "EX"  # Extinct
    EW = "EW"  # Extinct in the wild
    CR = "CR"  # Critically endangered
    EN = "EN"  # Endangered
    VU = "VU"  # Vulnerable
    NT = "NT"  # Near threatened
    CD = "CD"  # Conservation Dependent
    LC = "LC"  # Least concern
    DD = "DD"  # Data deficient
    NE = "NE"  # Not evaluated


class ProtectionClass(str, Enum):
    I = "I"
    II = "II"


class ResponseStatus(str, Enum):
    Success = "success"
    Pending = "pending"
    Error = "error"


class Species(APIModel):
    """
    Defines a species catagorized by the taxonomy ranks
    """

    species: str
    genus: str
    family: str
    order: str
    class_: str
    protection_class: ProtectionClass | None = None
    conservation_status: ConservationStatus | None = None
    __slots__ = "__weakref__"


class Judgment(APIModel):
    """
    The judgment document
    """

    title: str
    species: list[Species]


class ActionResult(APIModel):
    """
    The result of the current action
    """

    status: ResponseStatus
    message: str | None


class QueryActionResult(ActionResult, Generic[ResultT]):
    result: ResultT
