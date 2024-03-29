import datetime
from enum import Enum
from typing import Any, TypeVar

from fastapi import Depends

from api.lib import APIModel, has_query_params

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


class SourceCategory(str, Enum):
    Buy = "收购"
    Hunt = "猎捕"
    Sell = "出售"
    Transport = "运输"


# Schema definitions for /analytics/species
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


class SpeciesShort(APIModel):
    """
    Species information without taxonomy ranks higher than species
    """

    name: str
    protection_class: ProtectionClass | None = None
    conservation_status: ConservationStatus | None = None


class SpeciesBulkPatchResult(APIModel):
    """
    The taxons inserted or updated
    """

    species: list[str] = []
    genus: list[str] = []
    family: list[str] = []
    order: list[str] = []
    class_: list[str] = []


class SpeciesFilter(APIModel):
    """
    All the constraints need to be satisfied at the same time except fields
    that are unspecified
    """

    species: list[str] | None
    genus: list[str] | None
    family: list[str] | None
    order: list[str] | None
    class_: list[str] | None
    protection_class: list[ProtectionClass] | None
    conservation_status: list[ConservationStatus] | None


# Schema definitions for /analytics/defendant
class Defendant(APIModel):
    """
    Basic information of a defendant
    """

    id: int
    name: str
    gender: str | None
    birth: datetime.date | None
    education_level: str | None


class DefendantFilter(APIModel):
    name: list[str] | None
    gender: list[str] | None
    birth_before: datetime.date | None
    birth_after: datetime.date | None
    education_level: list[str] | None


class DefendantPost(APIModel):
    name: str
    gender: str | None
    birth: datetime.date | None
    education_level: str | None


# Schema definitions for /analytics/source
class SourcePost(APIModel):
    category: SourceCategory
    defendant_id: int | None
    occasion: str | None
    seller: str | None
    buyer: str | None
    method: str | None
    destination: str | None
    usage: str | None


class Source(SourcePost):
    judgment_id: int


class SourceFilter(APIModel):
    judgment_id: int | None
    defendant_id: int | None
    category: list[SourceCategory] | None
    occasion: list[str] | None
    seller: list[str] | None
    buyer: list[str] | None
    method: list[str] | None
    destination: list[str] | None
    usage: list[str] | None


# Schema definitions for /analytics/judgment
class Judgment(APIModel):
    """
    The judgment document
    """

    id: int
    title: str
    content: str | None
    species: list[SpeciesShort]
    defendants: list[Defendant]
    sources: list[Source]


class JudgmentFilter(APIModel):
    judgment_id: int | None
    title: str | None
    location: str | None
    date_before: datetime.datetime | None
    date_after: datetime.datetime | None
    defendant_filter: DefendantFilter = Depends(has_query_params(DefendantFilter))
    species_filter: SpeciesFilter = Depends(has_query_params(SpeciesFilter))
    source_filter: SourceFilter = Depends(has_query_params(SourceFilter))

    @staticmethod
    def no_depends(**kwargs: Any) -> "JudgmentFilter":
        return JudgmentFilter(
            defendant_filter=DefendantFilter(),
            species_filter=SpeciesFilter(),
            source_filter=SourceFilter(),
            **kwargs,
        )


class JudgmentPost(APIModel):
    title: str
    case_number: str | None
    location: str | None
    release_date: datetime.date | None
    content: str | None
    sentence: str | None
    species_names: list[str] = []
