from pydantic import BaseModel


class DuplaCreate(BaseModel):
    nome_dupla: str
    sala_id: int
    professor_1_id: int
    professor_2_id: int | None = None


class DuplaUpdate(BaseModel):
    nome_dupla: str | None = None
    sala_id: int | None = None
    professor_1_id: int | None = None
    professor_2_id: int | None = None
