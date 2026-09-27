from pydantic import BaseModel


class EquipeCreate(BaseModel):
    nome: str
    sala_id: int


class EquipeUpdate(BaseModel):
    nome: str | None = None
    sala_id: int | None = None


class EquipeMembroCreate(BaseModel):
    professor_id: int
