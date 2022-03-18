from fastapi import APIRouter, Depends
from pydantic import parse_obj_as
from sqlalchemy.orm.session import Session

from api.crud.defendant import insert_defendant, query_defendant
from api.dependencies import get_db
from api.lib import has_query_params
from api.lib.schemas import ActionResult
from api.lib.schemas import Defendant as DefendantSchema
from api.lib.schemas import (
    DefendantFilter,
    DefendantPost,
    QueryActionResult,
    ResponseStatus,
)

router = APIRouter(prefix="/analytics/defendant")


@router.get("", response_model=QueryActionResult[list[DefendantSchema]])
def get_defendant(
    defendant_filter: DefendantFilter = Depends(has_query_params(DefendantFilter)),
    db: Session = Depends(get_db),
):
    defendants = query_defendant(db, defendant_filter=defendant_filter)

    return QueryActionResult(
        status=ResponseStatus.Success,
        result=parse_obj_as(list[DefendantSchema], defendants),
    )


@router.post("", response_model=ActionResult)
def post_defendant(defendant: DefendantPost, db: Session = Depends(get_db)):
    defendant = insert_defendant(
        db,
        name=defendant.name,
        judgment_id=defendant.judgment_id,
        gender=defendant.gender,
        birth=defendant.birth,
        education_level=defendant.education_level,
    )
    db.add(defendant)
    db.commit()

    return ActionResult(status=ResponseStatus.Success)
