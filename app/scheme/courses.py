from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class CourseBase(BaseModel):
    name:            str
    description:     Optional[str] = None
    duration_months: Optional[int] = None
    lessons_count:   Optional[int] = None
    price:           Decimal = Decimal("0")
    min_age:         Optional[int] = None

class CourseAdd(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass


class CourseResponse(BaseModel):
    id:              int
    name:            str
    description:     Optional[str]
    duration_months: Optional[int]
    lessons_count:   Optional[int]
    price:           Decimal
    min_age:         Optional[int]
    is_active:       bool
    created_at:      datetime