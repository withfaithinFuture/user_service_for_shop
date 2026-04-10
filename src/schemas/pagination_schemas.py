from pydantic import BaseModel, ConfigDict


class PaginationSchema(BaseModel):
    page: int
    limit: int
    totalItems: int
    totalPages: int

    model_config = ConfigDict(from_attributes=True)
