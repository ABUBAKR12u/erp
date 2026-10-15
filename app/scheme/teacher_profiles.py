from pydantic import BaseModel, ConfigDict


class TeacherProfilesBase(BaseModel):
    bio: str | None = None
    specialization: str | None = None
    experience_years: int | None = None
    max_groups: int | None = None


class TeacherProfilesAdd(TeacherProfilesBase):
    pass


class TeacherProfilesUpdate(TeacherProfilesBase):
    pass


class TeacherProfilesResponse(BaseModel):
    employee_id: int
    bio: str | None = None
    specialization: str | None = None
    experience_years: int | None = None
    max_groups: int | None = None